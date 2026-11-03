/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package net

import (
	"context"
	"fmt"
	"io"
	"testing"
	"time"

	"chainmaker.org/chainmaker/sync/v2/internal/test"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/golang/mock/gomock"
)

func listenerService(transport Transport) *messageBusListener {
	listener := NewMessageBusListener(transport)
	_ = listener.Listen()
	go func() {
		for {
			conn, err := listener.Accept()
			if err != nil {
				return
			}
			time.Sleep(1 * time.Millisecond)
			go func(conn Conn) {
				buf := make([]byte, 1024)
				for i := 0; ; i++ {
					if _, err := conn.Write([]byte(fmt.Sprintf("hello_srv_%d", i))); err != nil {
						fmt.Printf("Listener.Conn.Write() error = %v\n", err)
						return
					}
					// fmt.Println("AAAAAAAAA")
					n, err := conn.Read(buf[0:])
					// fmt.Println("BBBBBBBBBBBB")
					if err != nil {
						fmt.Printf("Listener.Conn.Read() error = %v\n", err)
						continue
					}
					fmt.Printf("Listener.Conn.read1: %s\n", string(buf[:n]))
					if i == 2 {
						_, _ = conn.Write([]byte("bey bey"))
						n, err := conn.Read(buf[0:])
						if err != nil {
							fmt.Printf("Listener.Conn.Read() error = %v\n", err)
							return
						}
						fmt.Printf("Listener.Conn.read2: %s\n", string(buf[:n]))
						conn.Close()
						return
					}
				}
			}(conn)
		}
	}()
	return listener.(*messageBusListener)
}

func Test_messageBusDialer_Conn(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ns := test.NewWorkNS(ctrl)
	defer ns.Release()
	localNode := ns.NewMockNode("localNode", nil)
	remoteNode := ns.NewMockNode("remoteNode", nil)

	remoteTransport := NewBlockSyncTransport(remoteNode.MessageBus())
	listener := listenerService(remoteTransport)
	defer remoteTransport.Close()
	defer listener.Close()
	buf := make([]byte, 1024)

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
			times := 0
		again:
			got, err := d.Dial(tt.args.ctx, tt.args.addr)
			if (err != nil) != tt.wantErr {
				t.Errorf("messageBusDialer.Dial() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			// got.SetReadDeadline(time.Now().Add(3000 * time.Millisecond))
			for i := 0; ; i++ {
				if _, err := got.Write([]byte(fmt.Sprintf("hello_cli_%d", i))); err != nil {
					fmt.Printf("messageBusDialer.Conn.Write() error = %v\n", err)
					break
				}

				n, err := got.Read(buf[0:])

				if err != nil {
					if err == io.EOF {
						fmt.Println("messageBusDialer.Conn closed")
						break
					}
					fmt.Printf("messageBusDialer.Conn.Read() error = %v\n", err)
					break
				}
				fmt.Printf("messageBusDialer.Conn.read: %s\n", string(buf[:n]))
				if i == 2 {
					_, _ = got.Write([]byte("bey bey"))
					got.Close()
				}
			}
			time.Sleep(time.Second)
			times++
			if times > 2 {
				return
			}
			goto again

		})
	}
}

type mockHandler struct {
	t Transport
}

func (h *mockHandler) OnMessage(m Message) {
	fmt.Printf("mockHandler.OnMessage() %v\n", m)
}
func (h *mockHandler) OnQuit() {
	fmt.Printf("mockHandler.OnQuit()\n")
	h.t.Unregister(h)
}
func (h *mockHandler) MessageType() types.MsgType {
	return types.MTNormal
}

func Test_Transport_Close(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ns := test.NewWorkNS(ctrl)
	defer ns.Release()
	localNode := ns.NewMockNode("localNode", nil)
	transport := NewBlockSyncTransport(localNode.MessageBus())
	transport.Register(&mockHandler{
		t: transport,
	})
	transport.Close()
}
