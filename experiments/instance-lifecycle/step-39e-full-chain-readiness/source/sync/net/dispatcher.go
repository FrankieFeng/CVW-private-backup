/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package net

import (
	"fmt"
	"net"
	"sync"

	"chainmaker.org/chainmaker/sync/v2/types"
)

type (
	//NetMsgHandler handle incoming netpb.NetMsg
	NetMsgHandler func(msg *messageBusNetMessage)
	//NetMsgInterceptor intercept and process netpb.NetMsg
	//Whether the processing flow is passed down to the handler depends on the interceptor
	NetMsgInterceptor func(msg *messageBusNetMessage, handler NetMsgHandler)
	//ErrNetMsgHandler handle unconsumed messages
	ErrNetMsgHandler func(msg *messageBusNetMessage, err error)
)

// messageBusNetMessage encapsulate the original network message structure for special processing
// For example, some external data such as connection id
type messageBusNetMessage struct {
	// msg     *netpb.NetMsg
	from    string
	connID  uint64
	connAs  uint8
	typ     uint8
	payload []byte
}

func newMessageBusNetMessage(msg Message) *messageBusNetMessage {
	id, as, typ, payload := extractData(msg.Payload)
	nm := &messageBusNetMessage{
		from:    msg.From,
		connID:  id,
		connAs:  as,
		typ:     typ,
		payload: payload,
	}
	return nm
}

// Payload raw real and clean data
func (m *messageBusNetMessage) Payload() []byte {
	return m.payload
}

// From source of network messages
func (m *messageBusNetMessage) From() string {
	return genConnID(m.from, m.connID)
}

// FromType source type of network messages,such as client or server
func (m *messageBusNetMessage) FromType() uint8 {
	return m.connAs
}

// Type type of network messages
func (m *messageBusNetMessage) Type() uint8 {
	return m.typ
}

// connInDispatcher interface for connection in dispatcher.
type connInDispatcher interface {
	put(typ uint8, data []byte)
	ID() string
	RemoteAddr() net.Addr
	Close() error
}

// connMessageDispatcher responsible for receiving from the message bus and dispatching message
// to the corresponding connection, and writing data from connection to message bus
type connMessageDispatcher struct {
	transport Transport
	//subscriber used to subscribe message from message bus
	subscriber *connMessageDispatcherSub
	//handler used to handle received message
	//default just to distribute the message to the corresponding connection
	handler NetMsgHandler
	//errHandler messages that are not consumed will be processed by the handler with cause error
	errHandler ErrNetMsgHandler
	//rwLocker protect conns map
	rwLocker sync.RWMutex
	conns    map[string]connInDispatcher
	//quit indicates whether to quit work
	quit    bool
	tag     string
	msgType types.MsgType
}

func newConnMessageDispatcher(transport Transport, mt types.MsgType) *connMessageDispatcher {
	d := &connMessageDispatcher{
		transport: transport,
		conns:     make(map[string]connInDispatcher),
		msgType:   mt,
	}
	d.subscriber = &connMessageDispatcherSub{d}
	d.handler = d.dispatch
	d.errHandler = d.mismatchHandle
	transport.Register(d.subscriber)
	return d
}

func (d *connMessageDispatcher) MessageType() types.MsgType {
	return d.msgType //types.MT_Conn
}

// Register register a connection to the dispatcher so that messages can be distributed to it.
// Return error if the dispatcher is already quitted or the connection is already registered.
func (d *connMessageDispatcher) Register(conn connInDispatcher) error {
	d.rwLocker.Lock()
	defer d.rwLocker.Unlock()
	if d.quit {
		return fmt.Errorf("msgbus has quit")
	}
	if _, exist := d.conns[conn.ID()]; exist {
		return fmt.Errorf("connection [%s] already registered", conn.RemoteAddr().String())
	}
	d.conns[conn.ID()] = conn
	return nil
}

// Unregister unregister a connection from the dispatcher.
// Return true if the id connection exists, false otherwise.
func (d *connMessageDispatcher) Unregister(id string) bool {
	d.rwLocker.Lock()
	defer d.rwLocker.Unlock()
	_, exist := d.conns[id]
	if exist {
		delete(d.conns, id)
	}
	return exist
}

// WriteTo send the data to a node the parameter "to" specifies.
func (d *connMessageDispatcher) WriteTo(to string, data []byte) error {
	return d.transport.Send(Message{
		Type:    d.MessageType(),
		To:      to,
		Payload: data,
	})
}

// DispatchInterceptor set a interceptor for the dispatcher.
// The interceptor processed messages in preference to default dispatch handler.
// The interceptor is setted later and will be execed first.
func (d *connMessageDispatcher) DispatchInterceptor(interceptor NetMsgInterceptor) {
	handler := d.handler
	d.handler = func(msg *messageBusNetMessage) {
		interceptor(msg, handler)
	}
}

//	func (d *connMessageDispatcher) SetErrorHandler(handler ErrNetMsgHanler) {
//		d.errHandler = handler
//	}
//
// mismatchHandle used to handle the message without receivers
func (d *connMessageDispatcher) mismatchHandle(msg *messageBusNetMessage, _ error) {
	if msg.Type() == typeReset || msg.Type() == typeClose {
		return
	}
	// if len(msg.Payload()) == len(closedBytes) && bytes.Equal(msg.Payload(), closedBytes) {
	// 	return
	// }
	_ = d.WriteTo(msg.from, packSystemData(msg.connID, msg.connAs, typeReset))
}

// dispatch parse the source of the message and distribute to the corresponding connection.
func (d *connMessageDispatcher) dispatch(msg *messageBusNetMessage) {
	d.rwLocker.RLock()
	conn := d.conns[msg.From()]
	d.rwLocker.RUnlock()
	if conn == nil && d.errHandler != nil {
		d.errHandler(msg, nil)
		return
	}
	if conn != nil {
		conn.put(msg.Type(), msg.Payload())
	}
}

// Close unregister from the message bus and close all connections
func (d *connMessageDispatcher) Close() {
	d.rwLocker.Lock()
	if d.quit {
		d.rwLocker.Unlock()
		return
	}
	d.quit = true
	// avoid map race access
	conns := make([]connInDispatcher, 0, len(d.conns))
	for _, conn := range d.conns {
		conns = append(conns, conn)
	}
	d.rwLocker.Unlock()
	for _, conn := range conns {
		conn.Close()
	}
	d.transport.Unregister(d.subscriber)
}

// connMessageDispatcherSub implementation of the message bus subscriber interface.
type connMessageDispatcherSub struct {
	*connMessageDispatcher
}

// OnMessage implement the function OnMessage of the message bus subscriber.
func (s *connMessageDispatcherSub) OnMessage(message Message) {
	// if message.Type != s.MessageType() {
	// 	return
	// }
	s.handler(newMessageBusNetMessage(message))
}

// OnQuit implement the function OnQuit of the message bus subscriber.
func (s *connMessageDispatcherSub) OnQuit() {
	s.Close()
}
