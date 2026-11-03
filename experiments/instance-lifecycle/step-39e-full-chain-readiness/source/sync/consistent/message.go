/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package consistent

import (
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/types"
)

// NewSyncMessage 实例化一致性引擎消息
func NewSyncMessage(transport net.Transport, logger protocol.Logger) *SyncMessage {
	tcm := &SyncMessage{
		transport: transport,
		subscriber: &consistentSubscriber{
			messageChan: make(chan []byte, types.DefaultChanCap),
			logger:      logger,
		},
		logger: logger,
	}
	return tcm
}

// SyncMessage 用于一致性引擎的消息
type SyncMessage struct {
	transport  net.Transport
	subscriber *consistentSubscriber
	logger     protocol.Logger
}

// Send 发送消息到指定节点
// 通过Publish方案发送到指定节点
func (m *SyncMessage) Send(to string, payload []byte) {
	err := m.transport.Send(net.Message{
		Type:    types.MTConsistent,
		To:      to,
		Payload: payload,
	})
	if err != nil {
		m.logger.Warnf("[consistent] send to %s failed, err=%v", to, err)
	}
}

// Receive 从消息通道接收消息
func (m *SyncMessage) Receive() []byte {
	bz, ok := <-m.subscriber.messageChan
	if !ok {
		return nil
	}
	return bz
}

// Start syncMessage
func (m *SyncMessage) Start() error {
	m.transport.Register(m.subscriber)
	return nil
}

// Stop syncMessage
func (m *SyncMessage) Stop() error {
	m.transport.Unregister(m.subscriber)
	close(m.subscriber.messageChan)
	return nil
}
