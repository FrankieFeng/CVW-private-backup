/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"context"
	"sync"
	"sync/atomic"
	"time"

	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/net"
)

type (
	//ListenBlockHandler interface used to know the support information of the upper layer logic for the block.
	//Indicates whether this node can synchronize the block to the requesting node.
	ListenBlockHandler func(nodeID string, blockHeight uint64) BlockSupportResult
)

var (
	defaultListenBlockHandler = func(string, uint64) BlockSupportResult {
		return BlockSupportResult{
			BlockNum: -1,
			Workload: 0,
		}
	}
	handshakeTimeout = 5 * time.Second
)

// Listener a listener for accepting new connections which can be used to sync block
// Note: the listener only actually handles the connection request
// when "listener.Accept" function is called for the first time
type Listener struct {
	accepted int32
	lsner    net.Listener
	handler  ListenBlockHandler
	connCh   chan *ServerConn
	err      error
	logger   protocol.Logger
}

// NewListener create a listener with the underlay listener specified by parameter lsner
func NewListener(lsner net.Listener, lh ListenBlockHandler, logger protocol.Logger) *Listener {
	if lh == nil {
		lh = defaultListenBlockHandler
	}
	return &Listener{
		connCh:  make(chan *ServerConn, 128),
		lsner:   lsner,
		handler: lh,
		logger:  logger,
	}
}

// NewMsgBusListener create a listener with the underlay message bus listener and a block handler
// if lh is not specified, defaultListenBlockHandler will be used.
func NewMsgBusListener(transport net.Transport, lh ListenBlockHandler, logger protocol.Logger) *Listener {
	return NewListener(net.NewMessageBusListener(transport), lh, logger)
}

// Listen for connections
func (l *Listener) Listen() error {
	if atomic.CompareAndSwapInt32(&l.accepted, 0, 1) {
		go l.accept()
	}
	return nil
}

// Accept fetch a established connection
// the listener will start work if called for the first time.
func (l *Listener) Accept() (*ServerConn, error) {
	conn, ok := <-l.connCh
	if !ok {
		return nil, l.err
	}
	return conn, nil
}

// accept get a logical connection from the underlying network,
// then initiate a negotiation for synchronizing block.
// Successfully negotiated connections will be queued
// It will exit until all connections being negotiated finish processing when the underlying listener exits.
func (l *Listener) accept() {
	wg := sync.WaitGroup{}
	for {
		conn, err := l.lsner.Accept()
		if err != nil {
			wg.Wait()
			close(l.connCh)
			l.err = err
			return
		}
		// l.logger.Infof("accept connection from %s\n", conn.RemoteAddr().String())
		wg.Add(1)
		go func(conn net.Conn) {
			defer func() {
				wg.Done()
			}()
			fconn := newFrameConn(conn)
			serverConn := hsServer(fconn, func(height uint64) BlockSupportResult {
				return l.handler(conn.RemoteAddr().String(), height)
			})
			ctx, cancel := context.WithTimeout(context.Background(), handshakeTimeout)
			defer cancel()
			if _, err := serverConn.Handshake(ctx); err != nil {
				l.logger.Infof("handshake to client[%s] err %s\n", conn.RemoteAddr().String(), err)
				fconn.Close()
				return
			}
			l.put(NewServerConn(fconn, l.logger))
		}(conn)
	}
}

func (l *Listener) put(conn *ServerConn) {
	l.connCh <- conn
}

// Close close the listener
func (l *Listener) Close() error {
	return l.lsner.Close()
}
