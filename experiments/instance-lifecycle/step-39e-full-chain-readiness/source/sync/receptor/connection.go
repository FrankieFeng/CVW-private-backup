/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import (
	"context"
	"fmt"
	"sync"
	"time"

	"chainmaker.org/chainmaker/protocol/v2"

	"chainmaker.org/chainmaker/sync/v2/conn"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/net"
	sp "chainmaker.org/chainmaker/sync/v2/setting"
	"chainmaker.org/chainmaker/sync/v2/types"
)

type (
	connI interface {
		NodeID() string
		Ping(ctx context.Context) error
		OpenPush(ctx context.Context, fromHeight uint64, kvs ...sp.Setting) (clientStream, error)
		PullBlock(ctx context.Context, req types.BlockSyncRequest) ([]types.DataFragment, error)
		Close() error
	}

	connection struct {
		*conn.ClientConn
	}

	clientConn struct {
		ep          *endpoint
		mu          sync.Mutex
		closed      bool
		closeFor    error
		conn        connI
		ref         int32
		stream      clientStream
		idleTimeout time.Duration
		idleTimer   *time.Timer
		logger      protocol.Logger
	}
)

var connIdleTimeout = 5 * time.Minute

func (c *connection) OpenPush(ctx context.Context, fromHeight uint64, kvs ...sp.Setting) (clientStream, error) {
	return c.ClientConn.OpenPush(ctx, fromHeight, kvs...)
}

func newClientConn(c connI, ep *endpoint, logger protocol.Logger) *clientConn {
	return &clientConn{
		conn:        c,
		ref:         1,
		idleTimeout: connIdleTimeout,
		ep:          ep,
		logger:      logger,
	}
}

func (cc *clientConn) nodeID() string {
	return cc.conn.NodeID()
}

// func (cc *clientConn) isIdle() bool {
// 	cc.mu.Lock()
// 	defer cc.mu.Unlock()
// 	return !cc.closed && cc.ref == 0
// }

func (cc *clientConn) isPushing() bool {
	cc.mu.Lock()
	defer cc.mu.Unlock()
	return cc.stream != nil
}

func (cc *clientConn) isClosed() bool {
	cc.mu.Lock()
	defer cc.mu.Unlock()
	return cc.closed
}

// healthCheck checks the health of the connection.
// If the connection is closed, it will return false.
// If the ping fails, it will return false and log a warning.
func (cc *clientConn) healthCheck(ctx context.Context) bool {
	if cc.isClosed() {
		// If the connection is closed, it's not healthy.
		return false
	}
	// Ping the connection to check its health.
	if err := cc.conn.Ping(ctx); err != nil {
		if err == errors.ErrConnClosed {
			// If the connection is already closed, close it explicitly.
			_ = cc.closeForError(errors.ErrConnClosed)
		}
		// Log a warning if the ping fails.
		cc.logger.Warnf("conn[%s] ping error: %v", cc.nodeID(), err)
		return false
	}
	return true
}

func (cc *clientConn) pull(ctx context.Context, req types.BlockSyncRequest) ([]types.DataFragment, error) {
	if cc.isClosed() {
		return nil, fmt.Errorf("client has closed")
	}
	return cc.conn.PullBlock(ctx, req)
}

// retain increments the reference count of the connection.
// If the connection is closed, it will return an error.
func (cc *clientConn) retain() error {
	cc.mu.Lock()
	defer cc.mu.Unlock()
	return cc.retainLocked()
}

func (cc *clientConn) retainLocked() error {
	if cc.closed {
		return fmt.Errorf("connection lost")
	}
	cc.ref++
	// If the idle timer is running, stop it.
	if cc.idleTimer != nil {
		cc.idleTimer.Stop()
	}
	return nil
}

// release decrements the reference count of the connection.
// If the connection is closed, it will return an error.
// If the reference count is zero, it will start a timer to close the connection after the idle timeout.
func (cc *clientConn) release() error {
	cc.mu.Lock()
	defer cc.mu.Unlock()
	return cc.releaseLocked()
}

func (cc *clientConn) releaseLocked() error {
	if cc.ref == 0 {
		return fmt.Errorf("connection was released multiple times")
	}
	cc.ref--
	if cc.ref == 0 {
		// Start a timer to close the connection after the idle timeout.
		if cc.idleTimeout != 0 {
			if cc.idleTimer == nil {
				cc.idleTimer = time.AfterFunc(cc.idleTimeout, cc.closeIfIdle)
			} else {
				cc.idleTimer.Reset(cc.idleTimeout)
			}
		}
	}
	return nil
}

func (cc *clientConn) closeIfIdle() {
	cc.mu.Lock()
	if cc.ref == 0 {
		_ = cc.closeForErrorLocked(fmt.Errorf("idle"))
	}
	cc.mu.Unlock()
}

func (cc *clientConn) closeForError(err error) error {
	cc.mu.Lock()
	defer cc.mu.Unlock()
	return cc.closeForErrorLocked(err)
}

// closeForErrorUnlocked closes the connection with the given error.
// It returns an error if the connection is already closed.
func (cc *clientConn) closeForErrorLocked(err error) error {
	if cc.closed {
		return nil
	}
	cc.logger.Infof("connection [%s] closed for: %v", cc.nodeID(), err)
	cc.closed = true
	cc.closeFor = err
	// Close the push stream if it is open.
	cc.closeStreamLocked()
	// Stop the idle timer if it is running.
	if cc.idleTimer != nil {
		cc.idleTimer.Stop()
	}
	// connection already closed.
	if err == errors.ErrConnClosed {
		return nil
	}
	return cc.conn.Close()
}

// openStream opens a push stream on the connection and returns the stream.
// The block height from which to start pushing is given by the fromHeight parameter.
// The setting parameter is used to configure the push stream.
// If the stream is already open, it returns an error.
func (cc *clientConn) openStream(ctx context.Context, fromHeight uint64, set pushSetting) (*clientPushStream, error) {
	cc.mu.Lock()
	defer cc.mu.Unlock()
	if cc.stream != nil {
		return nil, fmt.Errorf("stream is already opened")
	}
	if err := cc.retainLocked(); err != nil {
		return nil, err
	}
	defer func() {
		if cc.stream == nil {
			_ = cc.releaseLocked()
		}
	}()
	setts := set.toSettings()
	if setts == nil {
		return nil, fmt.Errorf("setting wrong")
	}
	// Open the push stream on the connection.
	stream, err := cc.conn.OpenPush(ctx, fromHeight, setts...)
	if err != nil {
		return nil, err
	}
	cc.logger.Infof("connection [%s] open push stream at height[%d]", cc.nodeID(), fromHeight)
	cc.stream = stream
	// Return a clientPushStream for the newly opened stream.
	return newClientStream(cc, stream), nil
}

func (cc *clientConn) closeStream() {
	cc.mu.Lock()
	defer cc.mu.Unlock()
	cc.closeStreamLocked()
}

func (cc *clientConn) closeStreamLocked() {
	if cc.stream != nil {
		closed, _ := cc.stream.IsClosed()
		if !closed {
			cc.logger.Info("client push stream closed with connect close")
			cc.stream.Close()
		}
		cc.stream = nil
	}
}

type transport struct {
	dialer *conn.SyncDialer
	logger protocol.Logger
}

func newTransport(tp net.Transport, logger protocol.Logger) *transport {
	return &transport{
		dialer: conn.NewMsgBusSyncDialer(tp, logger),
		logger: logger,
	}
}

func (t *transport) checkDial(resp conn.BlockSupportResult) error {
	if resp.BlockNum == 0 {
		if resp.Code.Occurred() {
			return resp.Code
		}
		return fmt.Errorf("unsupported for synchronization")
	}
	return nil
}

// Dial dials to the remote node with the given address and height.
// It creates a ClientConn and wraps it into a connection.
func (t *transport) Dial(addr string, height uint64) (*connection, error) {
	// Create a context with the given height and dial function.
	ctx := conn.WithHeightContext(context.Background(), height)
	ctx = conn.WithNodeCheckFuncContext(ctx, t.checkDial)

	// Dial to the remote node.
	conn, err := t.dialer.Dial(ctx, addr)
	if err != nil {
		// If dial fails, log the error and return it.
		t.logger.Infof("dial to [%s] at height [%d] failed: %v", addr, height, err)
		return nil, err
	}
	// If dial succeeds, log the success and return a connection.
	t.logger.Infof("dial to [%s] at height [%d] ok", addr, height)
	return &connection{
		ClientConn: conn,
	}, nil
}
