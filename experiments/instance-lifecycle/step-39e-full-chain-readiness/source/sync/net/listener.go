/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package net

import (
	"fmt"
	"sync/atomic"

	"chainmaker.org/chainmaker/sync/v2/types"
)

// Listener interface.
type Listener interface {
	Listen() error
	Accept() (Conn, error)
	Close() error
}

type messageBusListener struct {
	dispatcher *connMessageDispatcher
	connCh     chan Conn
	closed     int32
	done       chan struct{}
}

// NewMessageBusListener creates a new message bus listener instance
func NewMessageBusListener(transport Transport) Listener {
	dispatcher := newConnMessageDispatcher(transport, types.MTConn)
	dispatcher.tag = "listener dispatch"
	listener := &messageBusListener{
		dispatcher: dispatcher,
		connCh:     make(chan Conn, 128),
		done:       make(chan struct{}, 1),
	}
	listener.do()
	return listener
}

func (l *messageBusListener) do() {
	l.dispatcher.DispatchInterceptor(l.acceptInterceptor)
	l.dispatcher.DispatchInterceptor(l.filterInterceptor)
}

// filterInterceptor only accept messages from clients, reject from servers
func (l *messageBusListener) filterInterceptor(msg *messageBusNetMessage, handler NetMsgHandler) {
	if msg.FromType() == asServer { //服务端连接只接受从客户端发过来的消息
		return
	}
	handler(msg)
}

// acceptInterceptor intercept to process the ping message and return.
// Others messages will be released to the handler.
func (l *messageBusListener) acceptInterceptor(msg *messageBusNetMessage, handler NetMsgHandler) {
	if msg.Type() == typeDial {
		nodeID, id := resolveConnID(msg.From())
		conn, err := newMessageBusConnAsServer(id, nodeID, l.dispatcher)
		if err != nil {
			return
		}
		conn.put(msg.Type(), msg.Payload())
		select {
		case l.connCh <- conn:
		default:
			fmt.Printf("[sync] listener connCh is full, close conn: %s\n", nodeID)
			conn.Close()
		}
		return
	}
	handler(msg)
}

// Listen for connections
func (l *messageBusListener) Listen() error {
	return nil
}

// Accept fetch a prepared connection from the connCh.
// It will be blocked until a ready connection arrives.
// Return error if the messageBusListener has been closed.
func (l *messageBusListener) Accept() (Conn, error) {
	select {
	case <-l.done:
		return nil, ErrListenerClosed
	case conn := <-l.connCh:
		return conn, nil
	}
}

// Close close the dispatcher and the connection channel.
// Return error if the messageBusListener has been closed.
func (l *messageBusListener) Close() error {
	if atomic.CompareAndSwapInt32(&l.closed, 0, 1) {
		l.dispatcher.Close()
		close(l.done)
		return nil
	}
	return ErrListenerClosed
}
