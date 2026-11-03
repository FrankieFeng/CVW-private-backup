/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package test

import (
	"fmt"
	"strings"
	"sync"

	"chainmaker.org/chainmaker/logger/v2"
	"chainmaker.org/chainmaker/sync/v2/internal/rand"

	"chainmaker.org/chainmaker/common/v2/msgbus"
	mbusmock "chainmaker.org/chainmaker/common/v2/msgbus/mock"
	netPb "chainmaker.org/chainmaker/pb-go/v2/net"
	"chainmaker.org/chainmaker/protocol/v2"
	"github.com/golang/mock/gomock"
)

// WorkNS is a mock network namespace for isolate network.
type WorkNS struct {
	id          uint64
	nodeMapMu   sync.RWMutex
	mockNodeMap map[string]*MockNode
	ctrl        *gomock.Controller
}

// NewWorkNS creates a mock network namespace.
func NewWorkNS(ctrl *gomock.Controller) *WorkNS {
	w := &WorkNS{
		id:          rand.Uint64(),
		ctrl:        ctrl,
		mockNodeMap: make(map[string]*MockNode),
	}
	fmt.Printf("test work namespace %d created\n", w.id)
	return w
}

// NewMockNode creates a mock node and add it into cluster.
// It will return a mock node which has a message bus and a node id.
// The message bus will be used to publish and subscribe messages.
func (ns *WorkNS) NewMockNode(nodeID string, log protocol.Logger) *MockNode {
	if log == nil {
		log = logger.GetLoggerByChain(logger.MODULE_SYNC, nodeID)
	}
	return ns.newMockNode(nodeID, log)
}

// NewMockNode2 creates a mock node and add it into cluster.
func (ns *WorkNS) NewMockNode2(nodeID string) *MockNode {
	log := logger.GetLoggerByChain(logger.MODULE_SYNC, nodeID)
	return ns.newMockNode(nodeID, log)
}

func (ns *WorkNS) newMockNode(nodeID string, logger protocol.Logger) *MockNode {
	// create a new mock node
	mbs := ns.newMockMessageBus(nodeID)
	node := &MockNode{
		mbs:    mbs,
		nodeID: nodeID,
		// create a timer to simulate the delay of message sending
		// timer:  time.NewTimer(messageDelay),
		logger:   logger,
		receiveC: make(chan interface{}, 10240),
		closeC:   make(chan struct{}),
	}
	go node.consume()
	// add the mock node to the cluster
	ns.addNodeToCluster(node)
	return node
}

// NewMockFullNode creates a mock full node and add it into cluster.
func (ns *WorkNS) NewMockFullNode(nodeID string) *MockFullNode {
	cLogger := logger.GetLoggerByChain(logger.MODULE_SYNC, nodeID)
	store := newMockBlockChainStore(ns.ctrl)
	leger := newMockLedgerCache(ns.ctrl)
	verifier := newMockVerifier(ns.ctrl)
	committer := newMockCommitter(ns.ctrl, leger)
	chainCfg := newMockChainConfig(ns.ctrl)
	return &MockFullNode{
		MockNode:  ns.newMockNode(nodeID, cLogger),
		Logger:    cLogger,
		Store:     store,
		Ledger:    leger,
		Verifier:  verifier,
		Committer: committer,
		ChainCfg:  chainCfg,
	}
}

func (ns *WorkNS) addNodeToCluster(node *MockNode) bool {
	ns.nodeMapMu.Lock()
	defer ns.nodeMapMu.Unlock()
	if _, exist := ns.mockNodeMap[node.nodeID]; exist {
		return false
	}
	ns.mockNodeMap[node.nodeID] = node
	return true
}

func (ns *WorkNS) newMockMessageBus(nodeID string) msgbus.MessageBus {
	var (
		mu          sync.RWMutex
		registerMap = make(map[msgbus.Topic][]msgbus.Subscriber)
		mockMsgBus  = mbusmock.NewMockMessageBus(ns.ctrl)
	)

	mockMsgBus.EXPECT().Register(gomock.Any(), gomock.Any()).Do(func(topic msgbus.Topic, sub msgbus.Subscriber) {
		mu.Lock()
		defer mu.Unlock()
		registerMap[topic] = append(registerMap[topic], sub)
	}).AnyTimes()
	mockMsgBus.EXPECT().Publish(gomock.Any(), gomock.Any()).AnyTimes().Do(func(topic msgbus.Topic, payload interface{}) {
		mu.RLock()
		subscribers := registerMap[topic]
		mu.RUnlock()
		if netMsg, ok := payload.(*netPb.NetMsg); ok {
			if topic == msgbus.RecvSyncBlockMsg {
				bz := netMsg.Payload
				for _, sub := range subscribers {
					netMsg.Payload = bz
					sub.OnMessage(&msgbus.Message{
						Topic:   topic,
						Payload: netMsg,
					})
				}
				return
			}
			//本地使用，拷贝一份，防止使用者发送后，更改bytes导致不可预知的问题
			payloadCopied := append([]byte(nil), netMsg.Payload...)
			netMsg.Payload = payloadCopied
			netMsg.To = strings.TrimSpace(netMsg.To)
			if netMsg.To == "" {
				ns.forEachNode(func(node *MockNode) bool {
					if nodeID != node.nodeID {
						//浅拷贝，以防止更改对bytes数组的引用导致不可预知的问题
						msgCopied := *netMsg
						msgCopied.To = nodeID
						node.receive(&msgCopied)
					}
					return false
				})
				return
			}

			node, exist := ns.getNode(netMsg.To)
			if !exist {
				fmt.Printf("node[%s] not found in ns\n", netMsg.To)
				return
			}
			netMsg.To = nodeID
			node.receive(netMsg)
			return
		}
		for _, sub := range subscribers {
			go sub.OnMessage(&msgbus.Message{
				Topic:   topic,
				Payload: payload,
			})
		}

		// if !ok {
		// 	return
		// }

	}).AnyTimes()
	mockMsgBus.EXPECT().UnRegister(gomock.Any(), gomock.Any()).AnyTimes()
	mockMsgBus.EXPECT().Close().Do(func() {
		mu.Lock()
		m := registerMap
		registerMap = make(map[msgbus.Topic][]msgbus.Subscriber)
		mu.Unlock()
		for _, subs := range m {
			for _, s := range subs {
				s.OnQuit()
			}
		}

	}).AnyTimes()
	return mockMsgBus
}

func (ns *WorkNS) getNode(nodeID string) (*MockNode, bool) {
	ns.nodeMapMu.RLock()
	defer ns.nodeMapMu.RUnlock()
	node, exist := ns.mockNodeMap[nodeID]
	return node, exist
}

func (ns *WorkNS) forEachNode(fn func(node *MockNode) bool) {
	ns.nodeMapMu.RLock()
	defer ns.nodeMapMu.RUnlock()
	for _, node := range ns.mockNodeMap {
		if fn(node) {
			return
		}
	}
}

// Remove removes a node from cluster and destroy it.
func (ns *WorkNS) Remove(nodeID string) {
	ns.nodeMapMu.Lock()
	node, exist := ns.mockNodeMap[nodeID]
	delete(ns.mockNodeMap, nodeID)
	ns.nodeMapMu.Unlock()
	if exist {
		node.destroy()
	}
}

// AddNode add a node to cluster
// func (ns *WorkNS) AddNode(node *MockNode) {
// 	ns.addNodeToCluster(node)
// }

// RemoveSoft just remove the node from cluster
func (ns *WorkNS) RemoveSoft(nodeID string) {
	ns.nodeMapMu.Lock()
	delete(ns.mockNodeMap, nodeID)
	ns.nodeMapMu.Unlock()
}

// Release releases the mock network namespace.
func (ns *WorkNS) Release() {
	fmt.Printf("test work namespace %d released\n", ns.id)
	ns.nodeMapMu.RLock()
	for _, node := range ns.mockNodeMap {
		node.destroy()
	}
	ns.nodeMapMu.RUnlock()
	ns.nodeMapMu.Lock()
	defer ns.nodeMapMu.Unlock()
	ns.mockNodeMap = make(map[string]*MockNode)
}
