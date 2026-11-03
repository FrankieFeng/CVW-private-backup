/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package consistent

import (
	"fmt"
	"testing"

	"chainmaker.org/chainmaker/sync/v2/net"

	"github.com/test-go/testify/require"

	"github.com/golang/mock/gomock"
)

var (
	testNodeIds = []string{
		"node1", "node2",
	}
	testBz    = []byte("test")
	testNodeC = [2]chan []byte{}
)

func TestMessage(t *testing.T) {
	fmt.Println("====== Start test message ======")
	node1SyncMessage := initMessageData(t, 0)
	node2SyncMessage := initMessageData(t, 1)
	require.Nil(t, node1SyncMessage.Start())
	require.Nil(t, node2SyncMessage.Start())

	node1SyncMessage.Send(testNodeIds[1], testBz)
	require.Equal(t, testBz, node2SyncMessage.Receive())

	node1SyncMessage.Send(testNodeIds[1], []byte(""))
	require.Equal(t, []byte(""), node2SyncMessage.Receive())

	node2SyncMessage.Send(testNodeIds[0], testBz)
	require.Equal(t, testBz, node1SyncMessage.Receive())

	require.Nil(t, node1SyncMessage.Stop())
	require.Nil(t, node2SyncMessage.Stop())
	fmt.Println("====== Stop test message ======")
}

func initMessageData(t *testing.T, index int) *SyncMessage {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	logger := newMockLogger(ctrl)

	transport := newMockTransport(index)

	sm := NewSyncMessage(transport, logger)
	testNodeC[index] = sm.subscriber.messageChan
	return sm
}

func newMockTransport(index int) net.Transport {
	return &mockTransport{index: index}
}

type mockTransport struct {
	index int
}

func (t *mockTransport) Register(net.Handler) {
}

func (t *mockTransport) Unregister(net.Handler) {}

func (t *mockTransport) Send(msg net.Message) error {
	for index, c := range testNodeC {
		if index != t.index {
			c <- msg.Payload
		}
	}
	return nil
}

func (t *mockTransport) Close() {}
