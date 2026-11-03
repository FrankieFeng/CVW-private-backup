/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 */

package consistent

import (
	"fmt"
	"testing"

	"chainmaker.org/chainmaker/consensus-utils/v2/consistent_service"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"

	"github.com/gogo/protobuf/proto"
	"github.com/test-go/testify/require"

	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/protocol/v2/mock"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/golang/mock/gomock"
)

var eventC chan types.Event

func TestHook(t *testing.T) {
	syncHook := initHookData(t, 10)
	syncNode1 := NewSyncNode("node1")

	bz, _ := proto.Marshal(&syncPb.NodeInform{
		Id:            "node1",
		Height:        10,
		ArchiveHeight: 0,
	})

	require.Equal(t, bz, syncHook.GetRequestAdditional(syncNode1))
	require.Equal(t, bz, syncHook.GetResponseAdditional(syncNode1, nil))
}

func TestHookUpdate(t *testing.T) {
	syncHook := initHookData(t, 10)

	syncNode1 := NewSyncNode("node1")
	syncHook.Update(syncNode1, nil)
	event, ok := <-eventC
	require.True(t, ok)
	require.Equal(t, event.EventType(), types.EventType(types.EventUpdateNode))
	require.Equal(t, event.EventNode(), &syncPb.NodeInform{
		Id:            syncNode1.ID(),
		Height:        syncNode1.Height,
		ArchiveHeight: syncNode1.ArchiveHeight,
	})
}

func TestHookNotify(t *testing.T) {
	syncHook := initHookData(t, 10)

	data := initStateData()
	for _, item := range data {
		syncHook.Notify(item.state, item.node)
		event, ok := <-eventC
		require.True(t, ok)
		require.Equal(t, item.result.Type, event.EventType())
		require.Equal(t, item.result.SyncNode, event.EventNode())
	}
}

type stateData struct {
	state  consistent_service.State
	node   consistent_service.Node
	result *types.NodeEvent
}

func initStateData() []stateData {
	syncNode1 := NewSyncNode("node1")
	syncNode1.Height = 100
	return []stateData{
		{
			state: consistent_service.Online,
			node:  syncNode1,
			result: &types.NodeEvent{
				Type: types.EventAddNode,
				SyncNode: &syncPb.NodeInform{
					Id:            syncNode1.Id,
					Height:        syncNode1.Height,
					ArchiveHeight: syncNode1.ArchiveHeight,
				},
			},
		},
		{
			state: consistent_service.Offline,
			node:  syncNode1,
			result: &types.NodeEvent{
				Type: types.EventDelNode,
				SyncNode: &syncPb.NodeInform{
					Id:            syncNode1.Id,
					Height:        syncNode1.Height,
					ArchiveHeight: syncNode1.ArchiveHeight,
				},
			},
		},
	}
}

func initHookData(t *testing.T, height uint64) *SyncHook {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	logger := newMockLogger(ctrl)
	ledgerCache := newMockLedgerCache(ctrl, height)
	storage := newMockStorage(ctrl)

	eventC = make(chan types.Event, 3)

	return NewSyncHook("node1", func(event types.Event) {
		eventC <- event
	}, ledgerCache, storage, logger)
}

func newMockStorage(ctrl *gomock.Controller) protocol.BlockchainStore {
	storage := mock.NewMockBlockchainStore(ctrl)
	storage.EXPECT().GetArchivedPivot().DoAndReturn(func() uint64 {
		return 0
	}).AnyTimes()
	return storage
}

func newMockLogger(ctrl *gomock.Controller) protocol.Logger {
	mockLogger := mock.NewMockLogger(ctrl)
	mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		fmt.Println(fmt.Sprintf(format, args))
	}).AnyTimes()
	mockLogger.EXPECT().Infof(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		fmt.Println(fmt.Sprintf(format, args))
	}).AnyTimes()
	mockLogger.EXPECT().Debugf(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		//fmt.Println(fmt.Sprintf(format, args))
	}).AnyTimes()
	mockLogger.EXPECT().Warnf(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		fmt.Println(fmt.Sprintf(format, args))
	}).AnyTimes()
	return mockLogger
}

func newMockLedgerCache(ctrl *gomock.Controller, height uint64) protocol.LedgerCache {
	ledgerCache := mock.NewMockLedgerCache(ctrl)
	ledgerCache.EXPECT().CurrentHeight().AnyTimes().DoAndReturn(func() (uint64, error) {
		return height, nil
	})
	return ledgerCache
}
