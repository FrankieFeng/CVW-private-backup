/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package consistent

import (
	"chainmaker.org/chainmaker/consensus-utils/v2/consistent_service"
)

const (
	// TypeNodeState 节点状态
	TypeNodeState = int8(1)
)

// NewSyncNode create a new SyncNode with status
// id is the node identity
// status is the status data that needs to be initialized
func NewSyncNode(id string) *SyncNode {
	status := NewNodeStatus()
	statuses := make(map[int8]SyncStatus)
	statuses[status.Type()] = status
	return &SyncNode{
		Id:       id,
		statuses: statuses,
	}
}

// SyncStatus alias of consistent_service.Status.
type SyncStatus = consistent_service.Status

// SyncNode represents a sync state node
type SyncNode struct {
	Id            string
	Height        uint64
	ArchiveHeight uint64
	statuses      map[int8]SyncStatus
}

// ID get the node identity
func (n *SyncNode) ID() string {
	return n.Id
}

// Statuses get all status of the node
func (n *SyncNode) Statuses() map[int8]consistent_service.Status {
	return n.statuses
}

// UpdateHeight update height
func (n *SyncNode) UpdateHeight(height, archiveHeight uint64) {
	n.Height = height
	n.ArchiveHeight = archiveHeight
}

// StatusByType get the status of the specified type
// if not exist return nil
func (n *SyncNode) StatusByType(tpy int8) SyncStatus {
	return n.statuses[tpy]
}

// UpdateStatus update node's status
func (n *SyncNode) UpdateStatus(status consistent_service.Status) {
	tpy := status.Type()
	if s, exist := n.statuses[tpy]; exist {
		s.Update(status)
		return
	}
	n.statuses[tpy] = status
}

// NewNodeStatus new local status
func NewNodeStatus() *NodeStatus {
	return &NodeStatus{}
}

// NodeStatus node status
type NodeStatus struct {
	height uint64
}

// Type the type of node status
func (s *NodeStatus) Type() int8 {
	return TypeNodeState
}

// Data the data contained in the node status
func (s *NodeStatus) Data() interface{} {
	return s.height
}

// Update update status data
func (s *NodeStatus) Update(status consistent_service.Status) {
	if s.Type() != status.Type() {
		return
	}
	if height, ok := status.Data().(uint64); ok {
		s.height = height
	}
}
