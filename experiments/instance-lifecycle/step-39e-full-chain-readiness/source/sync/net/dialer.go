/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package net

import (
	"context"

	"chainmaker.org/chainmaker/sync/v2/types"
)

// Dialer interface.
type Dialer interface {
	//	Dial request to establish a connection.
	Dial(ctx context.Context, addr string) (Conn, error)
}

type messageBusDialer struct {
	dispatcher *connMessageDispatcher
}

// NewMessageBusDialer creates a new message bus dialer
func NewMessageBusDialer(transport Transport) Dialer {
	d := &messageBusDialer{
		dispatcher: newConnMessageDispatcher(transport, types.MTConn),
	}
	d.dispatcher.tag = "dialer dispatch"
	d.dispatcher.DispatchInterceptor(d.filterInterceptor)
	return d
}

// filterInterceptor only accept messages from servers, reject from clients
func (d *messageBusDialer) filterInterceptor(msg *messageBusNetMessage, handler NetMsgHandler) {
	if msg.FromType() == asClient { //客户端连接只接受从服务端发过来的消息
		return
	}
	handler(msg)
}

// Dial get a logic message bus connection
func (d *messageBusDialer) Dial(ctx context.Context, addr string) (Conn, error) {
	conn, err := newMessageBusConnAsClient(increaseSN(), addr, d.dispatcher)
	if err != nil {
		return nil, err
	}
	toCtx, cancel := context.WithTimeout(ctx, dialMaxWait)
	defer cancel()
	if err := conn.dial(toCtx); err != nil {
		conn.Close()
		return nil, err
	}
	return conn, nil
}
