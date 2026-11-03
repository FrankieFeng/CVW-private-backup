/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package net

import (
	"context"
	"fmt"
	"io"
	"sync"
	"testing"
	"time"

	"chainmaker.org/chainmaker/sync/v2/internal/test"
	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func Test_packData(t *testing.T) {
	type args struct {
		id   uint64
		as   uint8
		typ  uint8
		data []byte
	}
	tests := []struct {
		name string
		args args
		want []byte
	}{
		{
			name: "test",
			args: args{
				id:   501020537,
				as:   2,
				typ:  typeData,
				data: []byte{1},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := packData(tt.args.id, tt.args.as, tt.args.typ, tt.args.data)
			id, as, typ, _ := extractData(got)
			require.Equal(t, as, tt.args.as)
			require.Equal(t, id, tt.args.id)
			require.Equal(t, typ, tt.args.typ)
		})
	}
}

type mockConnNoPing struct {
	*messageBusConn
}

func newMockConnNoPing(id uint64, nodeID string, dispatcher *connMessageDispatcher) (*mockConnNoPing, error) {
	conn, err := newMessageBusConnAsServer(id, nodeID, dispatcher)
	if err != nil {
		return nil, err
	}
	dispatcher.Unregister(conn.ID())
	mConn := &mockConnNoPing{
		messageBusConn: conn,
	}
	if err := dispatcher.Register(mConn); err != nil {
		return nil, err
	}
	return mConn, nil
}

func (c *mockConnNoPing) put(typ uint8, p []byte) {
	if typ == typePing {
		fmt.Printf("ping id = %d for node %s\n", p[0], c.remoteNodeID)
		return
	}
	c.messageBusConn.put(typ, p)
}

type mockListener struct {
	*messageBusListener
}

func newMockListener(transport Transport) *mockListener {
	listener := &mockListener{
		messageBusListener: NewMessageBusListener(transport).(*messageBusListener),
	}
	listener.dispatcher.DispatchInterceptor(listener.acceptInterceptor2)
	listener.dispatcher.DispatchInterceptor(listener.filterInterceptor)
	return listener
}

func (l *mockListener) acceptInterceptor2(msg *messageBusNetMessage, handler NetMsgHandler) {
	if msg.Type() == typeDial {
		nodeID, id := resolveConnID(msg.From())
		conn, err := newMockConnNoPing(id, nodeID, l.dispatcher)
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

func Test_messageBusConn_keepAlive(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	heartBeatInterval = 1 * time.Second

	ns := test.NewWorkNS(ctrl)
	defer ns.Release()
	localNode := ns.NewMockNode("localNode", nil)
	remoteNode := ns.NewMockNode("remoteNode", nil)

	remoteTransport := NewBlockSyncTransport(remoteNode.MessageBus())
	listener := newMockListener(remoteTransport)
	wg := sync.WaitGroup{}
	wg.Add(1)
	go func() {
		wg.Done()
		for {
			conn, err := listener.Accept()
			if err != nil {
				t.Logf("accept error: %v\n", err)
				return
			}
			t.Logf("accept conn: %+v\n", conn.RemoteAddr().String())
			buf := make([]byte, 1024)
			n, err := conn.Read(buf)
			t.Logf("server read data: %s, err: %v\n", string(buf[:n]), err)
		}
	}()
	defer wg.Wait()
	defer remoteTransport.Close()
	defer listener.Close()

	type fields struct {
		dialer Dialer
	}
	type args struct {
		ctx  context.Context
		addr string
	}
	tests := []struct {
		name    string
		fields  fields
		args    args
		want    Conn
		wantErr bool
	}{
		// TODO: Add test cases.
		{
			name: "test_0",
			fields: fields{
				dialer: NewMessageBusDialer(NewBlockSyncTransport(localNode.MessageBus())),
			},
			args: args{
				ctx:  context.Background(),
				addr: "remoteNode",
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			d := tt.fields.dialer
			conn, err := d.Dial(tt.args.ctx, tt.args.addr)
			if (err != nil) != tt.wantErr {
				t.Errorf("messageBusDialer.Dial() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			buf := make([]byte, 1024)
			n, err := conn.Read(buf)
			t.Logf("client read data: %s, err: %v\n", string(buf[:n]), err)
			require.Equal(t, io.EOF, err)
		})
	}
}
