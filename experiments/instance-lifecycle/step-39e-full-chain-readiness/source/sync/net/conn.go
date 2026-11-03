/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

// Package net provides network connection, communication and management capabilities.
package net

import (
	"context"
	"io"
	"net"
	"os"
	"sync/atomic"
	"time"
)

const (
	//defaultConnDataCache the max amount of unread data in a connection cache
	defaultConnDataCache = 256
)

const (
	//asClient client connection identifier
	asClient uint8 = 1
	//asClient server connection identifier
	asServer uint8 = 2
)

// Conn under connection implementation
type Conn interface {
	// net.Conn
	Read(p []byte) (n int, err error)
	Write(p []byte) (n int, err error)
	Close() error
	LocalAddr() net.Addr
	RemoteAddr() net.Addr
	SetReadDeadline(t time.Time) error
}

type messageBusConn struct {
	dispatcher *connMessageDispatcher
	//id uint64 mark number for the connection, is a part of the connection ID
	id uint64
	//as represents a connection type, such as asClient or asServer.
	//Used to prevent dispatcher from distributing data incorrectly.
	as          uint8
	localNodeID string
	//remoteNodeID identifies which remote node this is connected to
	remoteNodeID string
	//dataCh cache the message data received
	dataCh chan []byte
	//data currently being read
	data []byte
	//rtimer the timer for read deadline
	rtimer *time.Timer
	//rd the read deadline
	rd     int64
	toStop chan byte
	//rStopCh indicates that the read end is closed
	rStopCh chan struct{}
	//wStopCh indicates that the write end is closed
	wStopCh   chan struct{}
	closeCh   chan struct{}
	dialAck   chan struct{}
	heartBeat chan byte
	//indicates that the connection has been established
	established bool
	pingID      uint32
}

func newMessageBusConnAsClient(id uint64, nodeID string, dispatcher *connMessageDispatcher) (*messageBusConn, error) {
	return newMessageBusConn(id, nodeID, asClient, dispatcher, defaultConnDataCache)
}

func newMessageBusConnAsServer(id uint64, nodeID string, dispatcher *connMessageDispatcher) (*messageBusConn, error) {
	return newMessageBusConn(id, nodeID, asServer, dispatcher, defaultConnDataCache)
}

func newMessageBusConn(id uint64, remote string, as uint8,
	dispatcher *connMessageDispatcher, cacheLen int) (*messageBusConn, error) {
	conn := &messageBusConn{
		id:           id,
		as:           as,
		dispatcher:   dispatcher,
		localNodeID:  MsgBusLocalNodeID,
		remoteNodeID: remote,
		dataCh:       make(chan []byte, defaultConnDataCache),
		toStop:       make(chan byte, 2),
		rStopCh:      make(chan struct{}),
		wStopCh:      make(chan struct{}),
		closeCh:      make(chan struct{}),
		dialAck:      make(chan struct{}),
		heartBeat:    make(chan byte, 1),
	}
	err := dispatcher.Register(conn)
	if err != nil {
		return nil, err
	}
	conn.rtimer = time.NewTimer(time.Hour)
	conn.rtimer.Stop()
	go conn.listenStopSignal()
	return conn, nil
}

// listenStopSignal listen the stop signal.
// The received byte is 'r' means to close the read end, 'w' to close the write end
func (c *messageBusConn) listenStopSignal() {
	rc, wc := false, false
	for !rc || !wc {
		m := <-c.toStop
		if m == 'r' {
			if !rc {
				rc = true
				close(c.rStopCh)
			}
		} else {
			if !wc {
				wc = true
				close(c.wStopCh)
			}
		}
	}
	close(c.closeCh)
}

// keepAlive implements the keep-alive mechanism of the connection.
// It is used to detect whether the connection is alive by sending ping messages.
// If the number of pings exceeds the threshold, the connection is considered to be disconnected.
func (c *messageBusConn) keepAlive() {
	ticker := time.NewTicker(heartBeatInterval)
	defer ticker.Stop()

	// The number of consecutive pings without receiving pong messages
	ping := 0
	pingID := uint32(0)
	for {
		select {
		case <-ticker.C:
			// If the number of pings exceeds the threshold, the connection is considered to be disconnected
			if ping >= heartBeatMissCount {
				c.shutdownSignal()
				continue
			}
			pingID = atomic.AddUint32(&c.pingID, 1)
			// Send ping messages
			_, _ = c.write(typePing, []byte{byte(pingID)})
			// Increment the number of pings
			ping++
		case pongID := <-c.heartBeat:
			// Reset the number of pings if pong messages are received
			if pongID == byte(pingID) {
				ping = 0
			}
		case <-c.closeCh:
			// Stop the keep-alive mechanism if the connection is closed
			return
		}
	}
}

// put Put data received from the network into the read channel.
// If close data received signal to trigger off the read end.
// Discard the data if the read end is off.
func (c *messageBusConn) put(typ uint8, data []byte) {
	// fmt.Printf("put type = %d for node %s\n", typ, c.remoteNodeID)

	switch typ {
	case typeData:
		select {
		case <-c.rStopCh:
			return
		default:
		}

		select {
		case c.dataCh <- data:
		case <-c.rStopCh:
		}
	case typeDial:
		if c.as == asServer {
			c.established = true
			_, _ = c.write(typeDialAck, nil)
		}
	case typeDialAck:
		if c.as == asClient {
			select {
			case c.dialAck <- struct{}{}:
			default:
			}
		}
	case typeClose:
		select {
		case c.toStop <- 'r':
		default:
		}
	case typeReset:
		c.shutdownSignal()
	case typePing:
		_, _ = c.write(typePong, data[:1])
	case typePong:
		select {
		case c.heartBeat <- data[0]:
		default:
		}
	}
}

// Read read data from message bus conn.
// Since the data in messageBusConn is data block, we need to concatenate the data blocks to form a data stream.
// It will block until the read deadline expires if deadline is set.
func (c *messageBusConn) Read(out []byte) (int, error) {
	if len(out) == 0 {
		return 0, nil
	}
	td := atomic.LoadInt64(&c.rd)
	//td < 0 means the set deadline expired.
	//td = 0 means no deadline was set.
	//td > 0 means the set deadline not expired.
	if td < 0 {
		return 0, os.ErrDeadlineExceeded
	} else if td > 0 {
		select {
		case <-c.rtimer.C:
			td := atomic.LoadInt64(&c.rd)
			atomic.CompareAndSwapInt64(&c.rd, td, -1)
			return 0, os.ErrDeadlineExceeded
		default:
		}
	}

	readN := 0
	for {
		//read if there is data to read. otherwise, return if data has been read,
		// or wait until data arrives or timeout or close
		if len(c.data) == 0 {
			select {
			case data, ok := <-c.dataCh:
				if !ok {
					if readN == 0 {
						return 0, io.EOF
					}
					return readN, nil
				}
				c.data = data
			default:
				if readN > 0 {
					return readN, nil
				} else {
					select {
					case <-c.rtimer.C:
						td := atomic.LoadInt64(&c.rd)
						atomic.CompareAndSwapInt64(&c.rd, td, -1)
						return 0, os.ErrDeadlineExceeded
					case data, ok := <-c.dataCh:
						if !ok {
							return 0, io.EOF
						}
						c.data = data
					case <-c.rStopCh:
						return 0, io.EOF
					}
				}
			}

		}
		n := copy(out[readN:], c.data)
		c.data = c.data[n:]
		readN += n
		if readN == len(out) {
			return readN, nil
		}
	}
}

// Write send the data to the network.
// In order to identify the connection who sends the data,
// append the connection id number to the front of the data.
func (c *messageBusConn) Write(p []byte) (int, error) {
	if len(p) == 0 {
		return 0, nil
	}
	return c.write(typeData, p)
}

func (c *messageBusConn) write(typ uint8, p []byte) (int, error) {
	select {
	case <-c.wStopCh:
		return 0, ErrConnClosed
	default:
	}
	l := len(p)

	err := c.dispatcher.WriteTo(c.RemoteAddr().String(), packData(c.id, c.as, typ, p))
	if err != nil {
		return 0, err
	}
	return l, nil
}

// dial the remote node to establish the connection.
func (c *messageBusConn) dial(ctx context.Context) error {
	// If the connection is established, return immediately.
	if c.established {
		return nil
	}

	// Send the dial request to the remote node.
	if _, err := c.write(typeDial, nil); err != nil {
		return err
	}

	// Wait until the dial request is acknowledged by the remote node,
	// or the context is canceled.
	select {
	case <-c.dialAck:
		// If the dial request is acknowledged, mark the connection as established,
		// and start the keep-alive goroutine.
		c.established = true
		go c.keepAlive()
		return nil
	case <-ctx.Done():
		// If the context is canceled, return the context error.
		return ctx.Err()
	}
}

// packData package the data to be sent. the format is as follows:
// The high four bits of the first byte identify the data source type and
// the low four bits store the number 'N' of bytes occupied by the connection id.
// The second byte to the 'N+1' byte store the connection id.
// Other spaces store raw data.
// [as:idlen][id...][typ][data...]
func packData(id uint64, as uint8, typ uint8, data []byte) []byte {
	var (
		idBytesLen = 8
	)
	for ; idBytesLen > 0; idBytesLen-- {
		shift := (idBytesLen - 1) << 3
		if uint8(id>>shift)&255 != 0 {
			break
		}
	}
	capNeed := 2 + idBytesLen + len(data)
	buf := data
	if cap(buf) < capNeed {
		buf = make([]byte, capNeed)
	}

	buf = append(buf[:idBytesLen+2], data...)
	buf[0] = byte(as<<4) | byte(idBytesLen)
	buf[idBytesLen+1] = typ
	for i := 1; i <= idBytesLen; i++ {
		shift := (idBytesLen - i) << 3
		buf[i] = byte(id >> shift)
	}
	return buf
}

// extractData parse the correct value according to the format 'packData' packaged
func extractData(in []byte) (id uint64, as uint8, typ uint8, data []byte) {
	idBytesLen := int(in[0] & 15)
	as = uint8(in[0] >> 4)
	id = bytesToUint64(in[1 : idBytesLen+1])
	typ = in[idBytesLen+1]
	data = in[idBytesLen+2:]
	return
}

func packSystemData(id uint64, as uint8, typ uint8) []byte {
	return packData(id, as, typ, nil)
}

// func packageApplicationData(id uint64, as uint8, data []byte) []byte {
// 	return packData(id, as, typeData, data)
// }

// func (c *messageBusConn) switchDispatcher(dispatcher *connMessageDispatcher) error {
// 	if err := dispatcher.Register(c); err != nil {
// 		return err
// 	}
// 	old := c.dispatcher
// 	c.dispatcher = dispatcher
// 	old.Unregister(c.ID())
// 	return nil
// }

// LocalAddr returns the local network address, if known.
func (c *messageBusConn) LocalAddr() net.Addr {
	return messageBusNetAddr(c.localNodeID)
}

// RemoteAddr returns the remote network address, if known.
func (c *messageBusConn) RemoteAddr() net.Addr {
	return messageBusNetAddr(c.remoteNodeID)
}

// ID connection unique identifier consists of node id(c.nodeID) and mark number(c.id)
func (c *messageBusConn) ID() string {
	return genConnID(c.remoteNodeID, c.id)
}

// Close unregister itself from the dispatcher and close the read end and write end.
func (c *messageBusConn) Close() error {
	if c.dispatcher.Unregister(c.ID()) {
		// _, _ = c.Write(closedBytes)
		_, _ = c.write(typeClose, nil)
		c.shutdownSignal()
		return nil
	}
	return ErrCloseRepeat
}

// shutdownSignal sends stop signals to both the read and write ends of the connection.
func (c *messageBusConn) shutdownSignal() {
	// Attempt to send 'r' to stop the read end
	select {
	case c.toStop <- 'r':
	default:
		// Do nothing if the channel is already full
	}
	// Attempt to send 'w' to stop the write end
	select {
	case c.toStop <- 'w':
	default:
		// Do nothing if the channel is already full
	}
}

// SetReadDeadline sets the deadline for future Read calls and any currently-blocked Read call.
// A zero value for t means Read will not time out.
func (c *messageBusConn) SetReadDeadline(t time.Time) error {
	if t.IsZero() {
		c.rtimer.Stop()
		//Clears timeout signals that may have fired before
		select {
		case <-c.rtimer.C:
		default:
		}
		atomic.StoreInt64(&c.rd, 0)
		return nil
	}
	d := time.Until(t) //t.Sub(time.Now())
	atomic.StoreInt64(&c.rd, int64(d))
	c.rtimer.Reset(d)
	select {
	case <-c.rtimer.C:
	default:
	}
	return nil
}

type messageBusNetAddr string

func (a messageBusNetAddr) Network() string {
	return "msgbus"
}

func (a messageBusNetAddr) String() string {
	return string(a)
}
