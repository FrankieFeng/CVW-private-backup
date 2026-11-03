/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package consistent

import (
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/types"
)

// consistentSubscriber implementation of the message bus subscriber interface.
// messageChan 一致性引擎心跳接收通道
type consistentSubscriber struct {
	messageChan chan []byte
	logger      protocol.Logger
}

// OnMessage implement the function OnMessage of the transport subscriber.
func (t *consistentSubscriber) OnMessage(message net.Message) {
	switch message.Type {
	case types.MTConsistent:
		t.messageChan <- message.Payload
	}
}

// MessageType implement the function MessageType of the transport subscriber.
func (t *consistentSubscriber) MessageType() types.MsgType {
	return types.MTConsistent
}

// OnQuit implement the function OnQuit of the transport subscriber.
func (t *consistentSubscriber) OnQuit() {

}
