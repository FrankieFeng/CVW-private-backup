/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package net

import (
	"bytes"
	"fmt"
	"sync"

	"chainmaker.org/chainmaker/common/v2/msgbus"
	netPb "chainmaker.org/chainmaker/pb-go/v2/net"
	"chainmaker.org/chainmaker/sync/v2/types"
)

var (
	defaultMQSize = 10240
)

// Message represents a single message received or sent
type Message struct {
	Type    types.MsgType // unique identifier
	From    string        // where the message is from
	To      string        // where the message will be sent to
	Payload []byte        // the message body
}

// Handler network message handler.
// The kind of message to be processed is identified by MessageType().
type Handler interface {
	OnMessage(Message)
	OnQuit()
	MessageType() types.MsgType
}

// Transport used to send and receive network messages.
// Distribute the received message to the handler according to the types.MsgType.
type Transport interface {
	Register(Handler)
	Unregister(Handler)
	Send(Message) error
	Close()
}

// blockSyncTransport responsible for receiving from the message bus and dispatching message
// to the corresponding handler, and writing message to message bus
type blockSyncTransport struct {
	msgbus msgbus.MessageBus
	//subscriber used to subscribe message from message bus
	subscriber *messageBusBlockSyncSub
	//rwlock protect conns map
	rwlock      sync.RWMutex
	msgHandlers map[types.MsgType][]*handlerWithMQ //Handler
	//quit indicates whether to quit work
	quit bool
}

// NewBlockSyncTransport new a new blockSyncTransport instance and register itself to the message bus.
func NewBlockSyncTransport(mbs msgbus.MessageBus) Transport {
	d := &blockSyncTransport{
		msgbus:      mbs,
		msgHandlers: make(map[types.MsgType][]*handlerWithMQ),
	}
	d.subscriber = &messageBusBlockSyncSub{d}
	mbs.Register(msgbus.RecvSyncBlockMsg, d.subscriber)
	return d
}

// Register registers a net handler to the transport so that messages can be distributed to it.
// ignore if the transport is already quitted or the handler is already registered.
func (d *blockSyncTransport) Register(h Handler) {
	d.rwlock.Lock()
	defer d.rwlock.Unlock()
	if d.quit {
		return
	}
	for _, s := range d.msgHandlers[h.MessageType()] {
		if s.Handler == h {
			return
		}
	}
	d.msgHandlers[h.MessageType()] = append(d.msgHandlers[h.MessageType()], newHandlerWithMQ(d, h))
}

// Unregister unregister a net handler from the transport.
func (d *blockSyncTransport) Unregister(h Handler) {
	d.rwlock.Lock()
	defer d.rwlock.Unlock()
	d.unregisterLocked(h)
}

func (d *blockSyncTransport) unregisterLocked(h Handler) {
	handlers := d.msgHandlers[h.MessageType()]
	for i, s := range handlers {
		if s.Handler == h {
			d.msgHandlers[h.MessageType()] = append(handlers[:i], handlers[i+1:]...)
			s.close()
			break
		}
	}
	if len(d.msgHandlers[h.MessageType()]) == 0 {
		delete(d.msgHandlers, h.MessageType())
	}
}

// dispatch parse the id of the message and distribute to the corresponding handlers.
func (d *blockSyncTransport) dispatchSyncBlocMsg(msg *netPb.NetMsg) {
	typ, payload := deserialize(msg.Payload)
	msg.Payload = payload
	d.dispatch(typ, msg)
}

func (d *blockSyncTransport) dispatch(typ types.MsgType, msg *netPb.NetMsg) {
	d.rwlock.RLock()
	hs := d.msgHandlers[typ]
	d.rwlock.RUnlock()
	m := Message{
		Type:    typ,
		From:    msg.To,
		Payload: msg.Payload,
	}
	for _, s := range hs {
		s.OnMessage(m)
	}
}

// Send send the message to message bus.
// Fill the message id to the front of the payload.
func (d *blockSyncTransport) Send(m Message) error {
	d.msgbus.Publish(msgbus.SendSyncBlockMsg, &netPb.NetMsg{
		Payload: m.serialize(),
		Type:    netPb.NetMsg_SYNC_BLOCK_MSG,
		To:      m.To,
	})
	return nil
}

// Close unregister from the message bus.
func (d *blockSyncTransport) Close() {
	d.rwlock.Lock()
	if d.quit {
		d.rwlock.Unlock()
		return
	}
	d.quit = true
	handlers := make([]*handlerWithMQ, 0, 6) // 6 is the type count.
	for _, hs := range d.msgHandlers {
		handlers = append(handlers, hs...)
		for _, h := range hs {
			d.unregisterLocked(h.Handler)
		}
	}
	d.rwlock.Unlock()
	for _, h := range handlers {
		h.OnQuit()
	}
	d.msgbus.UnRegister(msgbus.RecvSyncBlockMsg, d.subscriber)
}

// messageBusBlockSyncSub implementation of the message bus subscriber interface
// for block synchronization network message.
type messageBusBlockSyncSub struct {
	*blockSyncTransport
}

// OnMessage implement the function OnMessage of the message bus subscriber.
func (s *messageBusBlockSyncSub) OnMessage(message *msgbus.Message) {
	switch message.Topic {
	case msgbus.RecvSyncBlockMsg:
		if msg, ok := message.Payload.(*netPb.NetMsg); ok {
			s.dispatchSyncBlocMsg(msg)
		}
	}
}

// OnQuit implement the function OnQuit of the message bus subscriber.
func (s *messageBusBlockSyncSub) OnQuit() {
	s.Close()
}

// Fill the message id to the front of the payload.
func (m *Message) serialize() []byte {
	return serialize(m.Payload, m.Type)
}

func serialize(payload []byte, typ types.MsgType) []byte {
	if typ == types.MTCompatible {
		return payload
	}
	buf := make([]byte, len(payload)+3)
	d := append(buf[:3], payload...)
	copy(d[:2], magicB[:])
	d[2] = byte(typ)
	return d
}

func deserialize(in []byte) (types.MsgType, []byte) {
	if !bytes.Equal(in[:2], magicB[:]) {
		return types.MTCompatible, in
	}
	typ := types.MsgType(in[2])
	return typ, in[3:]
}

type handlerWithMQ struct {
	Handler
	transport    Transport
	messageQueue chan Message
	closeCh      chan struct{}
}

func newHandlerWithMQ(t Transport, hdr Handler) *handlerWithMQ {
	h := &handlerWithMQ{
		Handler:      hdr,
		transport:    t,
		messageQueue: make(chan Message, defaultMQSize),
		closeCh:      make(chan struct{}),
	}
	go h.consume()
	return h
}

func (h *handlerWithMQ) consume() {
	for {
		select {
		case msg, ok := <-h.messageQueue:
			if !ok {
				return
			}
			h.Handler.OnMessage(msg)
		case <-h.closeCh:
			return
		}
	}
}

func (h *handlerWithMQ) close() {
	close(h.closeCh)
}

// OnQuit implement the function OnQuit of the Handler interface.
// func (h *handlerWithMQ) OnQuit() {
// 	h.Handler.OnQuit()
// 	h.transport.Unregister(h.Handler)
// }

// OnMessage implement the function OnMessage of the Handler interface.
func (h *handlerWithMQ) OnMessage(m Message) {
	select {
	case h.messageQueue <- m:
	default:
		fmt.Printf("[sync] messageQueue[%d] is full: %d, message drop: [%s]to[%s]\n",
			m.Type, len(h.messageQueue), m.From, m.To)
	}
}
