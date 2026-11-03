/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package noderegistry

import (
	"time"

	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/vmihailenco/msgpack/v5"
)

type (
	// trigger trigger a signal to drive a node detection
	trigger interface {
		fire() <-chan struct{}
	}

	//triggerFunc convert a func to trigger
	triggerFunc func() <-chan struct{}

	// nodeDiscoveryListener node discoverer informs the listener of the node information discovered.
	nodeDiscoveryListener interface {
		OnNodeDiscovery(node *syncPb.NodeInform)
	}

	//nodeDiscoverer detects and discovers surrounding nodes that can be accessed.
	nodeDiscoverer struct {
		nodeID      string
		ledgerCache protocol.LedgerCache
		storage     protocol.BlockchainStore
		tr          net.Transport
		listener    nodeDiscoveryListener
		logger      protocol.Logger
	}
	// ndMessage the message for node discovering.
	// Type: 1:request 2:response
	ndMessage struct {
		Type      uint8
		Msg       *syncPb.NodeInform
		Timestamp int64
	}
)

const (
	ndMTRequest  uint8 = 1
	ndMTResponse uint8 = 2

	messageExpirationTime = 3 * time.Second
)

func (fn triggerFunc) fire() <-chan struct{} {
	return fn()
}

func newNodeDiscoverer(nodeID string, tr net.Transport, ledgerCache protocol.LedgerCache,
	storage protocol.BlockchainStore, listener nodeDiscoveryListener, logger protocol.Logger) *nodeDiscoverer {
	return &nodeDiscoverer{
		nodeID:      nodeID,
		ledgerCache: ledgerCache,
		storage:     storage,
		tr:          tr,
		listener:    listener,
		logger:      logger,
	}
}

// discover registers self to the network to receive node messages and
// broadcast messages to detect surrounding nodes based on the signal of the trigger.
// Terminate detection when the trigger is closed and unregister from network.
func (nd *nodeDiscoverer) discover(trigger trigger) {
	nd.tr.Register(nd)
	go func() {
		defer nd.tr.Unregister(nd)
		c := trigger.fire()
		for range c {
			nd.scan()
		}
	}()
}

// OnMessage called when a network message arrives.
func (nd *nodeDiscoverer) OnMessage(message net.Message) {
	ndMsg := &ndMessage{}
	if err := ndMsg.unmarshal(message.Payload); err != nil {
		nd.logger.Errorf("unmarshal node discover message error: %v", err)
		return
	}
	if time.Now().Unix()-ndMsg.Timestamp > int64(messageExpirationTime) {
		nd.logger.Debugf("node discover message[%v] expired", ndMsg)
		return
	}

	switch ndMsg.Type {
	case ndMTRequest:
		nd.handleRequest(message.From, ndMsg.Msg)
	case ndMTResponse:
		nd.handleResponse(message.From, ndMsg.Msg)
	default:
		nd.logger.Errorf("something unexpected happened when unmarshal message[%v] from ",
			message.Payload, message.From)
	}
}

// MessageType message type of Interest
func (nd *nodeDiscoverer) MessageType() types.MsgType {
	return types.MTNodeInfo
}

// OnQuit implement the function OnQuit of the transport subscriber.
func (nd *nodeDiscoverer) OnQuit() {
}

func (nd *nodeDiscoverer) scan() {
	nd.sendMessage("", ndMTRequest)
}

// handleResponse receives status responses from other nodes to notify listener.
func (nd *nodeDiscoverer) handleResponse(from string, info *syncPb.NodeInform) {
	// info.Id = from
	nd.logger.Debugf("receive node[%s] response height[%d] archiveHeight[%d]",
		info.Id, info.Height, info.ArchiveHeight)
	nd.listener.OnNodeDiscovery(info)
}

// handleRequest when receiving a request from other nodes, it informs itself of its current height status.
func (nd *nodeDiscoverer) handleRequest(from string, info *syncPb.NodeInform) {
	nd.sendMessage(from, ndMTResponse)
	// info.Id = from
	nd.logger.Debugf("receive node[%s] request height[%d] archiveHeight[%d]",
		info.Id, info.Height, info.ArchiveHeight)
	nd.listener.OnNodeDiscovery(info)
}

func (nd *nodeDiscoverer) sendMessage(to string, mt uint8) {
	height, err := nd.ledgerCache.CurrentHeight()
	if err != nil {
		nd.logger.Errorf("get current height from ledger cache failed: %s", err.Error())
		return
	}
	message := &ndMessage{
		Type: mt,
		Msg: &syncPb.NodeInform{
			Id:            nd.nodeID,
			Height:        height,
			ArchiveHeight: nd.storage.GetArchivedPivot(),
		},
		Timestamp: time.Now().Unix(),
	}
	nd.send(to, message)
}

func (nd *nodeDiscoverer) send(to string, msg *ndMessage) {
	payload, err := msg.marshal()
	if err != nil {
		nd.logger.Errorf("node discover message[%v] marshal err: %s", msg, err.Error())
		return
	}
	// To设置为空，表示广播
	err = nd.tr.Send(net.Message{
		Type:    types.MTNodeInfo,
		To:      to,
		Payload: payload,
	})
	if err != nil {
		nd.logger.Warnf("send discover message[%v] to [%s] failed: %s", msg, err)
	} else {
		nd.logger.Debugf("send discover message[%v] to [%s] successfully", msg, to)
	}
}

func (m *ndMessage) marshal() ([]byte, error) {
	return msgpack.Marshal(m)
}

func (m *ndMessage) unmarshal(data []byte) error {
	m.Msg = &syncPb.NodeInform{}
	return msgpack.Unmarshal(data, m)
}
