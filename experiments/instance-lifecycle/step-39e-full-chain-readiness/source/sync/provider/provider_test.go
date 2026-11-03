/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package provider

import (
	"sync"
	"testing"
	"time"

	"chainmaker.org/chainmaker/common/v2/msgbus"
	"chainmaker.org/chainmaker/common/v2/msgbus/mock"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

var (
	testSubs        []msgbus.Subscriber
	testNodeManager *mockNodeManager
)

func TestProvider(t *testing.T) {
	t.Log("====== Start test provider ======")
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	initData()
	msgBus := newMockMessageBus(ctrl)
	transport := net.NewBlockSyncTransport(msgBus)
	testNodeManager = newMockNodeInformer()
	ledgerCache := newMockLedgerCache(ctrl, sender1)
	storage := newMockStorage(ctrl, sender1)
	chainConf := newMockChainConfig(ctrl)
	logger := newMockLogger(ctrl)

	provider := NewProvideServer(sender1, transport, testNodeManager, ledgerCache, storage, msgBus, chainConf, logger)
	require.Nil(t, provider.Start())

	testServerLinker(t, provider)
	require.Nil(t, provider.Stop())
}

func testServerLinker(t *testing.T, provider *ProvideServer) {
	linker := provider.serverLinker

	conn1 := newMockConn(receiveNodeId)
	linker.addConnOrReplace(conn1)
	result1 := map[string]types.Connection{
		receiveNodeId: conn1,
	}
	require.Equal(t, result1, linker.serverConns)

	conn2 := newMockConn(receiveNodeId2)
	linker.addConnOrReplace(conn2)
	result2 := map[string]types.Connection{
		receiveNodeId:  conn1,
		receiveNodeId2: conn2,
	}
	require.Equal(t, result2, linker.serverConns)

	require.Equal(t, conn2, linker.removeConnByID(receiveNodeId2))
	require.Equal(t, result1, linker.serverConns)

	for _, watcher := range testNodeManager.watcherList {
		err := watcher.SendEvent(newMockDelEvent())
		require.Nil(t, err)
	}

	time.Sleep(100 * time.Millisecond)
	require.Empty(t, linker.serverConns)

	linker.addConnOrReplace(conn1)
	linker.addConnOrReplace(conn2)
	require.Nil(t, linker.close())
	require.Empty(t, linker.serverConns)

}

func newMockDelEvent() types.Event {
	return &types.NodeEvent{
		Type: types.EventDelNode,
		SyncNode: &syncPb.NodeInform{
			Id:            receiveNodeId,
			Height:        0,
			ArchiveHeight: 0,
		},
	}
}

func newMockNodeInformer() *mockNodeManager {
	return &mockNodeManager{
		watcherList: make(map[uint32]*types.EventWatcher),
	}
}

type mockNodeManager struct {
	mu          sync.Mutex
	watcherList map[uint32]*types.EventWatcher // 事件列表
}

func (m *mockNodeManager) Watch() types.Watcher {
	eventWatcher := types.NewEventWatcher(nil)
	m.mu.Lock()
	defer m.mu.Unlock()
	m.watcherList[eventWatcher.Id()] = eventWatcher
	return eventWatcher
}

func (m *mockNodeManager) List() []types.Node {
	return nil
}

func newMockConn(nodeId string) types.Connection {
	return &testConn{nodeId: nodeId}
}

type testConn struct {
	nodeId string
}

func (t *testConn) Close() error {
	return nil
}

func (t *testConn) NodeID() string {
	return t.nodeId
}

func newMockMessageBus(ctrl *gomock.Controller) msgbus.MessageBus {
	mockMsgBus := mock.NewMockMessageBus(ctrl)
	mockMsgBus.EXPECT().Register(gomock.Any(), gomock.Any()).Do(func(topic msgbus.Topic, sub msgbus.Subscriber) {}).AnyTimes()

	mockMsgBus.EXPECT().Publish(gomock.Any(), gomock.Any()).AnyTimes().Do(func(topic msgbus.Topic, payload interface{}) {
		if topic == msgbus.SendSyncBlockMsg {
			topic = msgbus.RecvSyncBlockMsg
		}
		message := &msgbus.Message{
			Topic:   topic,
			Payload: payload,
		}

		for _, sub := range testSubs {
			sub.OnMessage(message)
		}
	})
	mockMsgBus.EXPECT().UnRegister(gomock.Any(), gomock.Any()).AnyTimes()
	return mockMsgBus
}
