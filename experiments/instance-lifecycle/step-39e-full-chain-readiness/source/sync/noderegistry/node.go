/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package noderegistry

import (
	"sync"
	"time"

	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/sync/v2/types"
)

type (
	nodeWithStatus struct {
		syncPb.NodeInform
		status int
		liveAt int64
	}

	// nodeSets is a collection of nodes.
	// all nodes are stored in this collection even if they are offline.
	nodeSets struct {
		mu      sync.RWMutex
		nodes   map[string]*nodeWithStatus
		livings int
	}
)

func newNodeWithStatus(node *syncPb.NodeInform) *nodeWithStatus {
	n := &nodeWithStatus{
		NodeInform: *node,
		status:     1,
	}
	n.updateLiveTime()
	return n
}

// Info get node information
func (n *nodeWithStatus) Info() *syncPb.NodeInform {
	return &n.NodeInform
}

// LastDetectedAliveTime get the last time the node was detected active,(seconds)
func (n *nodeWithStatus) LastDetectedAliveTime() int64 {
	return n.liveAt / 1e3
}

// isLiving returns true if the node is online
func (n *nodeWithStatus) isLiving() bool {
	return n.status == 1
}

// makeOffline set the status of the node 0 means offline
func (n *nodeWithStatus) makeOffline() {
	n.status = 0
}

// makeOnline set the status of the node 1 means online
func (n *nodeWithStatus) makeOnline() {
	n.status = 1
	n.updateLiveTime()
}

// updateLiveTime update the last time the node was detected active
func (n *nodeWithStatus) updateLiveTime() {
	n.liveAt = nodeTime()
}

// updateInfo update node information
func (n *nodeWithStatus) updateInfo(info *syncPb.NodeInform) {
	n.NodeInform = *info
	n.updateLiveTime()
}

func newNodeSets() *nodeSets {
	return &nodeSets{
		nodes:   make(map[string]*nodeWithStatus),
		livings: 0,
	}
}

// add adds a node to the nodeSets.
// If the node is already exist, if it is online, return false means no update
// if the node is offline, update the node and return true means update
// If the node is new, add it to the nodeSets and return true
func (s *nodeSets) add(node *syncPb.NodeInform) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	nd, exist := s.nodes[node.GetId()]
	if exist {
		if !nd.isLiving() {
			nd.NodeInform = *node
			nd.makeOnline()
			s.livings++
			return true
		}
		return false
	}
	nd = newNodeWithStatus(node)
	s.nodes[node.GetId()] = nd
	s.livings++
	return true
}

// update updates the status of the node if it is living and status has changed.
func (s *nodeSets) update(node *syncPb.NodeInform) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	nd, exist := s.nodes[node.GetId()]
	if !exist {
		return false
	}
	// no changes, no update, return false
	if !nd.isLiving() {
		return false
	}
	if nd.NodeInform == *node {
		nd.updateLiveTime()
		return false
	}
	nd.updateInfo(node)
	return true
}

// remove makes the node offline if the node exists.
func (s *nodeSets) remove(id string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	nd, exist := s.nodes[id]
	if !exist {
		return false
	}
	if !nd.isLiving() {
		return false
	}
	nd.makeOffline()
	s.livings--
	return true
}

// func (s *nodeSets) get(id string) *nodeWithStatus {
// 	s.mu.RLock()
// 	defer s.mu.RUnlock()
// 	return s.nodes[id]
// }

func (s *nodeSets) doFor(id string, do func(*nodeWithStatus)) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	nd, exist := s.nodes[id]
	if !exist {
		return
	}
	do(nd)
}

// listNodes get all nodes
func (s *nodeSets) listNodes() []types.Node {
	s.mu.RLock()
	defer s.mu.RUnlock()
	nodes := make([]types.Node, 0, len(s.nodes))
	for _, node := range s.nodes {
		nodes = append(nodes, node)
	}
	return nodes
}

// listLivingNodes get all living nodes
func (s *nodeSets) listLivingNodes() []types.Node {
	s.mu.RLock()
	defer s.mu.RUnlock()
	if s.livings == 0 {
		return nil
	}
	nodes := make([]types.Node, 0, s.livings)
	for _, node := range s.nodes {
		if node.isLiving() {
			nodes = append(nodes, node)
		}
	}
	return nodes
}

// isLiving returns true if the node exist and is online
func (s *nodeSets) isLiving(id string) bool {
	s.mu.RLock()
	defer s.mu.RUnlock()
	nd, exist := s.nodes[id]
	if !exist {
		return false
	}
	return nd.isLiving()
}

// forEach iterate over all nodes in the nodeSets.
func (s *nodeSets) forEach(fn func(*nodeWithStatus) bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	for _, nd := range s.nodes {
		if fn(nd) {
			return
		}
	}
}

func nodeTime() int64 {
	return time.Now().UnixNano() / 1e6
}
