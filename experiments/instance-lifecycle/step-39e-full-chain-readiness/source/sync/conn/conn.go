/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"net"
	"sync"
	"time"

	inet "chainmaker.org/chainmaker/sync/v2/net"
)

var (
	frameBufferSize = 1 << 6 // the read and write frame buffer size for the connection

	framerPool = &sync.Pool{
		New: func() interface{} {
			fr := &framer{
				frameBuffer: frameBuffer{
					make([]byte, frameHeaderMaxLen),
				},
			}
			// fmt.Printf("new framer: %p\n", fr)
			return fr
		},
	}
)

// FrameConn a connection that can handle framed data.
type FrameConn interface {
	Write(frameWriter) error
	Read() (frame, error)
	Close() error
	LocalAddr() net.Addr
	RemoteAddr() net.Addr
	SetReadDeadline(t time.Time) error
}

type frameConn struct {
	conn inet.Conn
	fr   *framer
}

func newFrameConn(conn inet.Conn) *frameConn {
	fr, _ := framerPool.Get().(*framer)
	fr.reset(conn, conn)
	// fmt.Printf("get framer: %p for conn: %s\n", fr, conn.RemoteAddr())
	return &frameConn{
		conn: conn,
		fr:   fr,
	}
}

// Write writes a frame.
func (c *frameConn) Write(fw frameWriter) error {
	return fw.writeFrame(c.fr)
}

// Read reads a frame.
func (c *frameConn) Read() (frame, error) {
	return c.fr.readFrame()
}

// Close closes the connection and releases the framer.
func (c *frameConn) Close() error {
	if c.fr == nil {
		return nil
	}
	err := c.conn.Close()
	framerPool.Put(c.fr)
	c.fr = nil
	return err
}

// LocalAddr returns the local network address.
func (c *frameConn) LocalAddr() net.Addr {
	return c.conn.LocalAddr()
}

// RemoteAddr returns the remote network address.
func (c *frameConn) RemoteAddr() net.Addr {
	return c.conn.RemoteAddr()
}

// SetReadDeadline sets the deadline for future Read calls.
func (c *frameConn) SetReadDeadline(t time.Time) error {
	return c.conn.SetReadDeadline(t)
}

type readFrameResult struct {
	frame frame
	err   error
}
