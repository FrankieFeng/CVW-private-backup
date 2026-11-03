/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package provider

import (
	"fmt"
	"sync"
	"testing"
	"time"

	"chainmaker.org/chainmaker/pb-go/v2/config"

	"chainmaker.org/chainmaker/pb-go/v2/store"

	"chainmaker.org/chainmaker/pb-go/v2/common"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/protocol/v2/mock"
	"chainmaker.org/chainmaker/protocol/v2/test"
	"chainmaker.org/chainmaker/sync/v2/conn"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/rule/manager"
	"chainmaker.org/chainmaker/sync/v2/setting"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/gogo/protobuf/proto"
	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

var (
	testLocker     sync.RWMutex
	testLastBlock  = make(map[string]*common.Block)
	testBlockStore = make(map[string]map[uint64]*common.Block)
	nodeRules      = make(map[string]*syncPb.NodeRule)
	sender1        = "node1"
	sender2        = "node2"
	sender3        = "node3"
	receiveNodeId  = "node5"
	receiveNodeId2 = "node6"
	fragmentLocker sync.RWMutex
	fragments      = make(map[uint64]map[int]*syncPb.SliceData)
	notifier       *HandlerNotifier
)

func TestBlockHandler(t *testing.T) {
	t.Log("====== Start test block handler ======")
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	initData()

	notifier = NewHandlerNotifier(newMockLedgerCache(ctrl, sender1), &test.GoLogger{})
	// 节点1负责推送测试
	testOneSender(t, ctrl)
	// 节点1和节点2，负责共同推送测试
	testTwoSenders(t, ctrl)
	// 节点1 、节点2、节点3 共同推送测试
	testThreeSenders(t, ctrl)
	// 本地块高不够，等待新区块生成测试
	testWaitNewBlock(t, ctrl)
}

func testOneSender(t *testing.T, ctrl *gomock.Controller) {
	mode := setting.NewShardingMode(1, 1, 0)
	handler1 := newMockHandler(ctrl, sender1)
	// 节点1 推送
	request1 := &types.BlockSyncRequest{
		Height:    0,
		Num:       3,
		WithRWSet: false,
		ModeData:  mode.ToModeData(),
	}
	writer := newMockWriter(request1, 0, newMockLogger(ctrl))
	fmt.Println("11111")
	handler1.ServeBlock(writer, request1)
	fmt.Println("22222")
	time.Sleep(time.Second)
	stopHeight := request1.Height + uint64(request1.Num) - 1
	fmt.Println("33333")
	receiverCurrentBlock := testBlockStore[receiveNodeId][stopHeight]
	fmt.Println("44444")
	require.Equal(t, testBlockStore[sender1][stopHeight], receiverCurrentBlock)
}

func testTwoSenders(t *testing.T, ctrl *gomock.Controller) {
	handler1 := newMockHandler(ctrl, sender1)
	handler2 := newMockHandler(ctrl, sender2)
	height := uint64(3)
	num := 3
	nodesTotal := 2
	mode := setting.NewShardingMode(nodesTotal, 0, 0)
	// 节点1 和节点2 共同推送
	request1 := &types.BlockSyncRequest{
		Height:    height,
		Num:       num,
		WithRWSet: false,
		ModeData:  mode.ToModeData(),
	}
	writer1 := newMockWriter(request1, 0, newMockLogger(ctrl))
	go handler1.ServeBlock(writer1, request1)
	mode = setting.NewShardingMode(nodesTotal, 1, 0)
	request2 := &types.BlockSyncRequest{
		Height:    height,
		Num:       num,
		WithRWSet: false,
		ModeData:  mode.ToModeData(),
	}
	writer2 := newMockWriter(request1, 1, newMockLogger(ctrl))
	go handler2.ServeBlock(writer2, request2)

	time.Sleep(time.Second)
	stopHeight := request1.Height + uint64(request1.Num) - 1
	receiverCurrentBlock := testBlockStore[receiveNodeId][stopHeight]
	fmt.Println(receiverCurrentBlock.Header.BlockHeight, stopHeight)
	fmt.Println("testBlockStore[sender1][stopHeight]", testBlockStore[sender1][stopHeight])
	require.Equal(t, testBlockStore[sender1][stopHeight], receiverCurrentBlock)
}

func testThreeSenders(t *testing.T, ctrl *gomock.Controller) {
	handler1 := newMockHandler(ctrl, sender1)
	handler2 := newMockHandler(ctrl, sender2)
	handler3 := newMockHandler(ctrl, sender3)

	height := uint64(6)
	num := 3
	nodesTotal := 3
	mode := setting.NewShardingMode(nodesTotal, 0, 0)
	// 节点1 和节点2 共同推送
	request1 := &types.BlockSyncRequest{
		Height:    height,
		Num:       num,
		WithRWSet: false,
		ModeData:  mode.ToModeData(),
	}
	writer1 := newMockWriter(request1, 0, newMockLogger(ctrl))
	go handler1.ServeBlock(writer1, request1)
	mode = setting.NewShardingMode(nodesTotal, 1, 0)
	request2 := &types.BlockSyncRequest{
		Height:    height,
		Num:       num,
		WithRWSet: false,
		ModeData:  mode.ToModeData(),
	}
	writer2 := newMockWriter(request1, 1, newMockLogger(ctrl))
	go handler2.ServeBlock(writer2, request2)
	mode = setting.NewShardingMode(nodesTotal, 2, 0)
	request3 := &types.BlockSyncRequest{
		Height:    height,
		Num:       num,
		WithRWSet: false,
		ModeData:  mode.ToModeData(),
	}
	writer3 := newMockWriter(request1, 2, newMockLogger(ctrl))
	go handler3.ServeBlock(writer3, request3)

	time.Sleep(time.Second)
	stopHeight := request1.Height + uint64(request1.Num) - 1
	receiverCurrentBlock := testBlockStore[receiveNodeId][stopHeight]
	require.Equal(t, testBlockStore[sender1][stopHeight], receiverCurrentBlock)
}

func testWaitNewBlock(t *testing.T, ctrl *gomock.Controller) {
	handler1 := newMockHandler(ctrl, sender1)
	handler2 := newMockHandler(ctrl, sender2)
	handler3 := newMockHandler(ctrl, sender3)

	height := uint64(9)
	num := 0
	nodesTotal := 3
	// 节点1 和节点2 共同推送
	mode := setting.NewShardingMode(nodesTotal, 0, 0)
	request1 := &types.BlockSyncRequest{
		Height:    height,
		Num:       num,
		WithRWSet: false,
		ModeData:  mode.ToModeData(),
	}

	writer1 := newMockWriter(request1, 0, newMockLogger(ctrl))
	go handler1.ServeBlock(writer1, request1)
	mode = setting.NewShardingMode(nodesTotal, 1, 0)
	request2 := &types.BlockSyncRequest{
		Height:    height,
		Num:       num,
		WithRWSet: false,
		ModeData:  mode.ToModeData(),
	}
	writer2 := newMockWriter(request1, 1, newMockLogger(ctrl))
	go handler2.ServeBlock(writer2, request2)
	mode = setting.NewShardingMode(nodesTotal, 2, 0)
	request3 := &types.BlockSyncRequest{
		Height:    height,
		Num:       num,
		WithRWSet: false,
		ModeData:  mode.ToModeData(),
	}
	writer3 := newMockWriter(request1, 2, newMockLogger(ctrl))
	go handler3.ServeBlock(writer3, request3)

	time.Sleep(time.Second * 2)
	newHeight := uint64(11)
	newHeightBlock := mockNewBlock(newHeight)
	mockNewBlockCommitted(newHeight)

	notifier.mu.RLock()
	for _, handler := range notifier.handlers {
		handler.notifier.Notify(newHeightBlock)
	}
	notifier.mu.RUnlock()

	time.Sleep(time.Second)
	receiverCurrentBlock := testBlockStore[receiveNodeId][newHeight]
	require.Equal(t, testBlockStore[sender1][newHeight], receiverCurrentBlock)

	newHeight = uint64(12)
	newHeightBlock = mockNewBlock(newHeight)
	mockNewBlockCommitted(newHeight)

	notifier.mu.RLock()
	for _, handler := range notifier.handlers {
		handler.notifier.Notify(newHeightBlock)
	}
	notifier.mu.RUnlock()

	time.Sleep(time.Second)
	receiverCurrentBlock = testBlockStore[receiveNodeId][newHeight]
	require.Equal(t, testBlockStore[sender1][newHeight], receiverCurrentBlock)

	newHeight = uint64(13)
	newHeightBlock = mockNewBlock(newHeight)
	mockNewBlockCommitted(newHeight)

	notifier.mu.RLock()
	for _, handler := range notifier.handlers {
		handler.notifier.Notify(newHeightBlock)
	}
	notifier.mu.RUnlock()

	time.Sleep(time.Second)
	receiverCurrentBlock = testBlockStore[receiveNodeId][newHeight]
	require.Equal(t, testBlockStore[sender1][newHeight], receiverCurrentBlock)

}

func newMockWriter(request *types.BlockSyncRequest, index int, logger protocol.Logger) conn.BlockWriter {
	return &mockBlockWriter{request: request, index: index, logger: logger}
}

type mockBlockWriter struct {
	request *types.BlockSyncRequest
	index   int
	logger  protocol.Logger
}

func (m *mockBlockWriter) Write(fragment types.DataFragment) error {
	slicer := types.NewBlockSlicer(m.logger)
	fragmentLocker.Lock()
	defer fragmentLocker.Unlock()
	fmt.Println(fragment)
	sliceData := &syncPb.SliceData{}
	if fragments[fragment.Height] == nil {
		fragments[fragment.Height] = make(map[int]*syncPb.SliceData)
	}
	_ = proto.Unmarshal(fragment.Data, sliceData)
	fragments[fragment.Height][m.index] = sliceData

	if m.request.ModeData.Type() != setting.SyncModeTypeSharding {
		return fmt.Errorf("unsupported mode type: %d", m.request.ModeData.Type())
	}
	ms := m.request.ModeData.ToMode().Spec()
	spec := ms.(setting.ShardingModeSpec)

	// 判断收集的分片是否足够
	if len(fragments[fragment.Height]) == int(spec.Nodes) {
		var completeFragment [][]byte
		blockWithRWSet := &store.BlockWithRWSet{}

		if int(spec.Nodes) == 1 {
			_ = proto.Unmarshal(fragments[fragment.Height][0].Data, blockWithRWSet)
		} else {
			for i := 0; i < int(spec.Nodes); i++ {
				completeFragment = append(completeFragment, fragments[fragment.Height][i].Data)
			}
			blockWithRWSet, _ = slicer.MergeBlockFragment(completeFragment)
			fmt.Println("blockWithRWSet", blockWithRWSet, len(completeFragment))
		}
		testBlockStore[receiveNodeId][fragment.Height] = blockWithRWSet.Block
		fmt.Println("testBlockStore[receiveNodeId]:", blockWithRWSet.Block)
	}
	return nil
}

func (m *mockBlockWriter) NodeID() string {
	return receiveNodeId
}

func (m *mockBlockWriter) Terminate(errors.ErrCode) {

}

func initData() {
	// 将node1的区块mock到高度10
	for i := 0; i < 11; i++ {
		block := mockNewBlock(uint64(i))
		if i == 0 {
			testBlockStore[sender1] = make(map[uint64]*common.Block)
			testBlockStore[sender2] = make(map[uint64]*common.Block)
			testBlockStore[sender3] = make(map[uint64]*common.Block)
			testBlockStore[receiveNodeId] = make(map[uint64]*common.Block)
		}
		testBlockStore[sender1][uint64(i)] = block
		testBlockStore[sender2][uint64(i)] = block
		testBlockStore[sender3][uint64(i)] = block
		testLastBlock[sender1] = block
		testLastBlock[sender2] = block
		testLastBlock[sender3] = block
	}
}

func mockNewBlock(height uint64) *common.Block {
	return &common.Block{
		Header: &common.BlockHeader{
			BlockHeight: height,
			BlockHash:   mockHash(height),
			BlockType:   common.BlockType_NORMAL_BLOCK,
		},
	}
}

func mockNewBlockCommitted(height uint64) {
	block := mockNewBlock(height)
	testLocker.Lock()
	testBlockStore[sender1][height] = block
	testBlockStore[sender2][height] = block
	testBlockStore[sender3][height] = block
	testLastBlock[sender1] = block
	testLastBlock[sender2] = block
	testLastBlock[sender3] = block
	testLocker.Unlock()
}

func mockHash(height uint64) []byte {
	return []byte(fmt.Sprintf("hash%d", height))
}

func newMockHandler(ctrl *gomock.Controller, nodeId string) conn.BlockHandler {
	storage := newMockStorage(ctrl, nodeId)
	ledgerCache := newMockLedgerCache(ctrl, nodeId)
	logger := newMockLogger(ctrl)
	chainConf := newMockChainConfig(ctrl)
	rm := manager.NewRuleManager(nodeId, storage, logger)
	_ = rm.Start()

	return newBlockSender(nodeId, notifier, storage, rm, ledgerCache, chainConf, logger)
}

func newMockStorage(ctrl *gomock.Controller, nodeId string) protocol.BlockchainStore {
	storage := mock.NewMockBlockchainStore(ctrl)
	storage.EXPECT().GetArchivedPivot().DoAndReturn(func() uint64 {
		return 5
	}).AnyTimes()
	storage.EXPECT().GetLastBlock().DoAndReturn(func() (*common.Block, error) {
		return testLastBlock[nodeId], nil
	}).AnyTimes()
	storage.EXPECT().GetBlock(gomock.Any()).DoAndReturn(func(height uint64) (*common.Block, error) {
		return testBlockStore[nodeId][height], nil
	}).AnyTimes()
	storage.EXPECT().GetBlockWithRWSets(gomock.Any()).DoAndReturn(func(height uint64) (*store.BlockWithRWSet, error) {
		return &store.BlockWithRWSet{
			Block:          testBlockStore[nodeId][height],
			TxRWSets:       []*common.TxRWSet{},
			ContractEvents: []*common.ContractEvent{},
		}, nil
	}).AnyTimes()
	storage.EXPECT().ReadObject(gomock.Any(), gomock.Any()).DoAndReturn(func(contractName string, key []byte) ([]byte, error) {
		r := nodeRules[string(key)]
		fmt.Println("******", string(key), " ", r)
		if r != nil {
			return proto.Marshal(r)
		}
		return nil, nil
	}).AnyTimes()

	return storage
}

func newMockChainConfig(ctrl *gomock.Controller) protocol.ChainConf {
	mockChainConf := mock.NewMockChainConf(ctrl)
	mockChainConf.EXPECT().ChainConfig().DoAndReturn(func() *config.ChainConfig {
		return &config.ChainConfig{
			Version: "v2.3.2",
		}
	}).AnyTimes()

	return mockChainConf
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

func newMockLedgerCache(ctrl *gomock.Controller, nodeId string) protocol.LedgerCache {
	ledgerCache := mock.NewMockLedgerCache(ctrl)
	ledgerCache.EXPECT().GetLastCommittedBlock().AnyTimes().DoAndReturn(func() *common.Block {
		lastBlock := testLastBlock[nodeId]
		fmt.Println(nodeId)
		fmt.Println(testBlockStore)
		return testBlockStore[nodeId][lastBlock.Header.BlockHeight]
	})
	ledgerCache.EXPECT().SetLastCommittedBlock(gomock.Any()).AnyTimes().DoAndReturn(func(block *common.Block) {
		testLastBlock[nodeId] = block
		testBlockStore[nodeId][block.Header.BlockHeight] = block
	})
	ledgerCache.EXPECT().CurrentHeight().AnyTimes().DoAndReturn(func() (uint64, error) {
		fmt.Println("[", nodeId, "] ledger cache CurrentHeight: ", testLastBlock[nodeId].Header.BlockHeight)
		return testLastBlock[nodeId].Header.BlockHeight, nil
	})
	return ledgerCache
}
