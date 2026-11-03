/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

/*
Package sync provides synchronization primitives for the Chainmaker protocol.
It includes utilities for synchronizing blocks, handling block requests, and managing node connections.
*/
package sync

import (
 rd39e "experiment.local/readiness39e"
	"sync"
	"time"

	"chainmaker.org/chainmaker/localconf/v2"
	"chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/noderegistry"
	"chainmaker.org/chainmaker/sync/v2/types"

	commonErrors "chainmaker.org/chainmaker/common/v2/errors"
	"chainmaker.org/chainmaker/common/v2/msgbus"
	"chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/provider"
	"chainmaker.org/chainmaker/sync/v2/receptor"

	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
)

const (
	stopped uint32 = iota
	started
	paused
)

type verifyStatus uint8

const (
	verifyStatusOk verifyStatus = iota
	verifyStatusRepeat
	verifyStatusRetry
	verifyStatusFail
)

// BlockSyncService 同步服务
type BlockSyncService struct {
	nodeID string
	// 同步服务大锁
	locker sync.Mutex
	// 是否快速同步
	withRWSet bool
	// 当前高度
	height uint64
	// 同步状态
	syncStatus uint32
	statusCond *sync.Cond
	// 同步网络消息传输
	transport net.Transport
	// 节点仓
	nodeRegistry *noderegistry.Registry
	// 数据提供者，发送者
	provider types.Provider
	// 数据接收器
	receptor types.Receptor
	// 缓存
	ledgerCache protocol.LedgerCache
	// The module that provides blocks storage/query
	blockChainStore protocol.BlockchainStore
	// 区块验证
	verifier protocol.BlockVerifier
	// 区块提交
	committer protocol.BlockCommitter
	// 同步到理想高度
	syncToIdealHeightC chan struct{}
	// 理想高度是否已通知
	// idealHeightNotified bool
	// logger 日志
	logger protocol.Logger
}

var (
	_ protocol.SyncService = (*BlockSyncService)(nil)
)

// NewSyncServer 实例化同步服务
func NewSyncServer(
	nodeID string,
	cfg *localconf.SyncConfig,
	chainConfig protocol.ChainConf,
	storage protocol.BlockchainStore,
	ledgerCache protocol.LedgerCache,
	logger protocol.Logger,
	msgBus msgbus.MessageBus,
	verifier protocol.BlockVerifier,
	committer protocol.BlockCommitter) (*BlockSyncService, error) {

	// 实例化传输层的transport，用于provider通信和心跳通信
	transport := net.NewBlockSyncTransport(msgBus)
	withRWSet := localconf.ChainMakerConfig.NodeConfig.FastSyncConfig.Enable
	registry := noderegistry.NewRegistry(nodeID, cfg.IdealHeightDistance, 0,
		transport, ledgerCache, storage, logger)

	blockProvider := provider.NewProvideServer(nodeID, transport, registry, ledgerCache,
		storage, msgBus, chainConfig, logger)

	rc := &receptor.Config{
		Informer:       registry,
		LedgerCache:    ledgerCache,
		Transport:      transport,
		WithRWSet:      withRWSet,
		ExposeConf:     cfg,
		FragmentMerger: types.NewBlockSlicer(logger),
		Logger:         logger,
	}

	syncServer := &BlockSyncService{
		nodeID:             nodeID,
		nodeRegistry:       registry,
		withRWSet:          withRWSet,
		transport:          transport,
		provider:           blockProvider,
		receptor:           receptor.NewBlockReceptor(rc),
		ledgerCache:        ledgerCache,
		syncToIdealHeightC: make(chan struct{}, 1),
		logger:             logger,
		verifier:           verifier,
		committer:          committer,
		blockChainStore:    storage,
	}
	syncServer.statusCond = sync.NewCond(&syncServer.locker)

	return syncServer, nil
}

// Start 启动同步服务
func (s *BlockSyncService) Start() error {
	s.locker.Lock()
	defer s.locker.Unlock()
	s.logger.Infof("sync server start")

	if s.syncStatus != stopped {
		s.logger.Warnf("sync server start failed: sync status [%d] ", s.syncStatus)
		return types.ErrSyncStatusStart
	}

	// 启动节点管理器
	if err := s.nodeRegistry.Start(); err != nil {
		return err
	}
	rd39e.Mark("registry_returned")
 // 启动数据提供者
	if err := s.provider.Start(); err != nil {
		return err
	}
	rd39e.Mark("provider_returned")
 // 启动数据接收器
	if err := s.receptor.Start(); err != nil {
		return err
	}

	// 读取当前区块高度
	height, err := s.ledgerCache.CurrentHeight()
	if err != nil {
		s.logger.Errorf("[sync] get ledge cache failed, err: %v", err)
		return err
	}
	s.height = height

	// 监听block并提交
	go s.watchBlock()

	// 标记状态started
	s.syncStatus = started
 rd39e.Mark("sync_started")
	return nil
}

// Stop 停止同步服务
func (s *BlockSyncService) Stop() {
	s.locker.Lock()
	defer s.locker.Unlock()
	if s.syncStatus != started {
		s.logger.Warnf("sync server stop failed: sync status [%d] ", s.syncStatus)
		return
	}
	// 停止数据接收器
	err := s.receptor.Stop()
	s.logger.Infof("receptor stopped with error: %v", err)
	// 停止数据提供者
	err = s.provider.Stop()
	s.logger.Infof("provider stopped with error: %v", err)
	// 停止节点管理器
	err = s.nodeRegistry.Stop()
	s.logger.Infof("node manager stopped with error: %v", err)
	s.transport.Close()
	s.logger.Infof("net transport closed with error: %v", err)
	// 关闭理想高度通知channel
	close(s.syncToIdealHeightC)
	// 标记状态stopped
	s.syncStatus = stopped
}

// ListenSyncToIdealHeight 监听是否到达理想高度
func (s *BlockSyncService) ListenSyncToIdealHeight() <-chan struct{} {
	return s.syncToIdealHeightC
}

// GetState  get sync state, with_others indicates whether to obtain the height state of other nodes known.
// Return an error if failed.
func (s *BlockSyncService) GetState(withPeers bool) (*syncPb.SyncState, error) {
	height, err := s.ledgerCache.CurrentHeight()
	if err != nil {
		s.logger.Errorf("gets the current height error:%s", err.Error())
		return nil, err
	}
	archivedHeight := s.blockChainStore.GetArchivedPivot()
	state := syncPb.SyncState{
		NodeId:          s.nodeID,
		Height:          height,
		ArchivedHeight:  archivedHeight,
		BlocksHasSynced: s.receptor.HeightHasBeenSynced(),
		BlocksInCache:   int32(s.receptor.BlocksInQueue()),
		ConfigShow:      s.receptor.ShowConfigJSON(),
		Timestamp:       time.Now().Unix(),
	}
	if withPeers {
		nodeList := s.nodeRegistry.ListAll()
		state.Others = make([]*syncPb.NodeState, 0, len(nodeList))
		for _, node := range nodeList {
			info := node.Info()
			state.Others = append(state.Others, &syncPb.NodeState{
				NodeId:         info.Id,
				Height:         info.Height,
				ArchivedHeight: info.ArchiveHeight,
				ReceiveTime:    node.LastDetectedAliveTime(),
			})
		}
	}
	return &state, nil
}

// StopBlockSync 暂停区块同步
func (s *BlockSyncService) StopBlockSync() {
	s.locker.Lock()
	defer s.locker.Unlock()
	if s.syncStatus != started {
		s.logger.Warnf("pause block sync failed: sync status [%d] ", s.syncStatus)
		return
	}

	if err := s.receptor.Pause(); err != nil {
		s.logger.Errorf("[sync] pause receptor failed,err:%v", err)
	}
	s.syncStatus = paused
}

// StartBlockSync 开始区块同步
func (s *BlockSyncService) StartBlockSync() {
	s.locker.Lock()
	defer s.locker.Unlock()
	if s.syncStatus != paused {
		s.logger.Warnf("resume block sync failed: sync status [%d] ", s.syncStatus)
		return
	}
	if err := s.receptor.Resume(); err != nil {
		s.logger.Errorf("[sync] resume receptor failed,err:%v", err)
		return
	}

	// 清除通道内可能遗留的数据，且避免阻塞
	select {
	case <-s.syncToIdealHeightC:
	default:
	}
	s.syncStatus = started
	s.statusCond.Broadcast()
	// 重新放开理想高度通知
	// s.idealHeightNotified = false
}

// watchBlock 监听区块并提交
func (s *BlockSyncService) watchBlock() {
	var (
		pause = func() bool {
			var isPaused bool
			s.locker.Lock()
			defer s.locker.Unlock()
			for s.syncStatus == paused {
				isPaused = true
				s.statusCond.Wait()
				continue
			}
			return isPaused
		}
		toIdealHeightSignal = func() {
			// 1. 检查是否已同步到理想块高
			// 如果到达理想块高，则通知外层
			if s.nodeRegistry.CheckIdealHeight() {
				select {
				case s.syncToIdealHeightC <- struct{}{}:
				default:
				}
			}
		}
		block   types.BlockReveal
		watchOK bool
	)
	for {
		toIdealHeightSignal()
		if pause() {
			toIdealHeightSignal()
			currentHeight, _ := s.ledgerCache.CurrentHeight()
			// 2. 监听接收器的新区块
			for {
				block, watchOK = s.receptor.WatchBlock()
				// !ok 表示receptor已经关闭, 则退出区块监听
				if !watchOK {
					return
				}
				if block.GetBlockWithRWSet().Block.Header.BlockHeight > currentHeight {
					break
				}
			}
		} else {
			// 2. 监听接收器的新区块
			block, watchOK = s.receptor.WatchBlock()
			// !ok 表示receptor已经关闭, 则退出区块监听
			if !watchOK {
				return
			}
		}
		blockH := block.GetBlockWithRWSet().Block.Header.BlockHeight
		s.logger.Infof("watch a new block, height: %d", blockH)

		// 5. 验证并提交区块
		// 提交失败，补偿区块
		if err := s.verifyAndCommit(block.GetBlockWithRWSet()); err != nil {
			s.logger.Errorf("verify the watched block[%d] failed, err: %v", blockH, err)
			if err == types.ErrVerifyConfigBlock {
				// 如果是配置快异常，则需要补偿带读写集的区块啊
				s.pullBlock(blockH, true)
			} else {
				block.ReportVerifyResult(false)
				// 普通区块补偿，不需要带读写集
				s.pullBlock(blockH, s.withRWSet)
			}
		}
		// 6. 当前节点高度+1
		s.height = blockH
	}
}

// pullBlock 持续补偿区块直到提交成功
// 需要指定返回读写集
// 在补偿配置块的时候，需要读写集数据
// 在补偿其他块的时候，不需要读写集数据
func (s *BlockSyncService) pullBlock(height uint64, withRWSet bool) {
	for {
		block, err := s.receptor.PullBlock(height, withRWSet)
		if err != nil {
			s.logger.Errorf("pull block failed,err:%v", err)
			continue
		}
		if err = s.verifyAndCommit(block.GetBlockWithRWSet()); err != nil {
			block.ReportVerifyResult(false)
			s.logger.Errorf("verify the pulled block failed, err: %v", err)
			continue
		}
		return
	}
}

// verifyAndCommit verifies the block and commits it to the store.
// If the block is filtered, it removes the transaction hash set key from the additional data.
func (s *BlockSyncService) verifyAndCommit(blockWithRWSet *store.BlockWithRWSet) error {
	if blockWithRWSet == nil || blockWithRWSet.Block == nil {
		return types.ErrInvalidBlock
	}
	// Verify the block with its read-write sets
verify:
	vs, err := s.verifyBlock(blockWithRWSet)
	if err != nil {
		s.logger.Errorf("verify block[%d] error: %v", blockWithRWSet.Block.Header.BlockHeight, err)
		return err
	}
	if vs == verifyStatusRetry { // this block is verifying wait a moment.
		time.Sleep(2 * time.Second)
		goto verify
	}
	if vs != verifyStatusOk {
		return nil
	}

	// Check if the block is filtered
	if blockIsFiltered(blockWithRWSet) {
		// Remove the transaction hash set key from the block's additional data
		delete(blockWithRWSet.Block.AdditionalData.ExtraData, protocol.SYNC_txHash_set_key)
	}

	// Commit the block to the blockchain
	return s.commitBlock(blockWithRWSet.Block)
}

// verifyBlock verifies the block and its read-write sets if they are present.
// The block is verified using the following rules:
// 1. If the block is filtered, it is verified with the filter.
// 2. If the block has read-write sets, they are verified with the block.
// 3. If the block does not have read-write sets, it is verified without them.
func (s *BlockSyncService) verifyBlock(blockWithRWSet *store.BlockWithRWSet) (verifyStatus, error) {
	var (
		height     = blockWithRWSet.GetBlock().GetHeader().BlockHeight
		withRWSet  = len(blockWithRWSet.TxRWSets) > 0
		withFilter = blockIsFiltered(blockWithRWSet)
		errCheck   = func(err error) (verifyStatus, error) {
			switch err {
			case nil:
				return verifyStatusOk, nil
			case commonErrors.ErrBlockHadBeenCommited:
				return verifyStatusRepeat, nil
			case commonErrors.ErrConcurrentVerify:
				return verifyStatusRetry, nil
			}
			return verifyStatusFail, err
		}
	)

	if withFilter {
		s.logger.Infof("verify block [%d] with filter", height)
		return errCheck(s.verifier.VerifyBlockWithRwSets(
			blockWithRWSet.Block, blockWithRWSet.TxRWSets, protocol.SYNC_FILTER_VERIFY))
	}
	// 读写集不为空，则使用带读写集验证
	if withRWSet {
		s.logger.Infof("verify block [%d] with rwSet", height)
		return errCheck(s.verifier.VerifyBlockWithRwSets(
			blockWithRWSet.Block, blockWithRWSet.TxRWSets, protocol.SYNC_VERIFY))
	}
	// 未指定读写集验证
	// 如果是配置块，且没有读写集信息，则验证失败
	// 返回error，重新pullBlock
	s.logger.Infof("verify block [%d] without rwSet", height)
	if blockWithRWSet.Block.Header.BlockType == common.BlockType_CONFIG_BLOCK &&
		blockWithRWSet.TxRWSets == nil {
		return verifyStatusFail, types.ErrVerifyConfigBlock
	}
	return errCheck(s.verifier.VerifyBlock(blockWithRWSet.Block, protocol.SYNC_VERIFY))
}

func (s *BlockSyncService) commitBlock(block *common.Block) error {
	height := block.GetHeader().BlockHeight
	// 验证通过，提交区块
	if err := s.committer.AddBlock(block); err != nil {
		if err == commonErrors.ErrBlockHadBeenCommited {
			s.logger.Warnf("add block, the block: %d has been committed in the blockChainStore ", height)
			return nil
		}
		s.logger.Errorf("add block[%d] failed, err:%v", height, err)
		return err
	}

	s.logger.Infof("add block[%d] successfully", height)
	return nil
}

func blockIsFiltered(blockWithRWSet *store.BlockWithRWSet) bool {
	addData := blockWithRWSet.GetBlock().GetAdditionalData()
	if addData == nil {
		return false
	}
	_, exist := addData.ExtraData[protocol.SYNC_txHash_set_key]
	return exist
}
