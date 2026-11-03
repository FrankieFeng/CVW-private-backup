/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// Package test provides utilities for testing Chainmaker components.
package test

import (
	"fmt"
	"time"

	"chainmaker.org/chainmaker/common/v2/msgbus"
	"chainmaker.org/chainmaker/protocol/v2"
)

// MessageDelay is the delay time for deliver messages.
var MessageDelay = 2 * time.Millisecond //time.Duration(0)

// MockNode indicates a mock node.
type MockNode struct {
	mbs    msgbus.MessageBus
	nodeID string
	logger protocol.Logger
	// timer    *time.Timer
	receiveC chan interface{}
	closeC   chan struct{}
}

// MockFullNode owns all dependent module instances
type MockFullNode struct {
	*MockNode
	Logger    protocol.Logger
	Store     *mockBlockChainStore
	Ledger    protocol.LedgerCache
	Verifier  protocol.BlockVerifier
	Committer protocol.BlockCommitter
	ChainCfg  protocol.ChainConf
}

// MessageBus get the messagebus.
func (n *MockNode) MessageBus() msgbus.MessageBus {
	return n.mbs
}

// NodeID get nodeid.
func (n *MockNode) NodeID() string {
	return n.nodeID
}

// receive receive a message from the node.
//
// receive receives a message from the node. It will wait for the messageDelay duration
// before publishing the message to the message bus.
func (n *MockNode) receive(payload interface{}) {
	// wait for the messageDelay duration
	// if messageDelay > 0 {
	// 	<-n.timer.C
	// }
	select {
	case n.receiveC <- payload:
	default:
		fmt.Println("message bus is full, drop message")
		return
	}
	// publish the message to the message bus
	// n.mbs.Publish(msgbus.RecvSyncBlockMsg, payload)

	// reset the timer
	// if messageDelay > 0 {
	// 	n.timer.Reset(messageDelay)
	// }
}

func (n *MockNode) consume() {
	var delayTimer *time.Ticker
	if MessageDelay > 0 {
		delayTimer = time.NewTicker(MessageDelay)
		defer delayTimer.Stop()
	}
	for {
		if delayTimer != nil {
			select {
			case <-n.closeC:
				return
			case <-delayTimer.C:
			}
		}
		select {
		case payload, ok := <-n.receiveC:
			if !ok {
				return
			}
			n.mbs.Publish(msgbus.RecvSyncBlockMsg, payload)
		case <-n.closeC:
			return
		}
	}
}

// destroy destroys the mock node.
func (n *MockNode) destroy() {
	// if n.timer != nil {
	// 	n.timer.Stop()
	// }
	n.mbs.Close()
	close(n.closeC)
}
