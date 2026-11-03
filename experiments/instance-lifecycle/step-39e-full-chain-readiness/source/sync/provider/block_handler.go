/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// Package provider accept block synchronization requests, query, split and send block data.
package provider

import (
	"math"

	rule "chainmaker.org/chainmaker/common/v2/syncrule"
	"chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/pb-go/v2/store"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/conn"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/rule/manager"
	"chainmaker.org/chainmaker/sync/v2/setting"
	"chainmaker.org/chainmaker/sync/v2/types"
	"chainmaker.org/chainmaker/utils/v2"
	"github.com/gogo/protobuf/proto"
)

type (
	// BlockSender 区块发送者实现了blockHandler
	// notifyNewHeightChan 新区块落块通知
	BlockSender struct {
		remoter      string // 推送对端的nodeId
		newBlockChan chan uint64
		notifier     *HandlerNotifier
		ruleManager  *manager.RuleManager
		slicer       types.Slicer
		storage      protocol.BlockchainStore
		ledgerCache  protocol.LedgerCache
		chainConfig  protocol.ChainConf
		logger       protocol.Logger
	}
	blockRequest struct {
		Height    uint64
		Num       int
		WithRWSet bool
		setting.ShardingModeSpec
	}
)

// newBlockSender 实例化区块发送者
func newBlockSender(remoter string, notifier *HandlerNotifier, storage protocol.BlockchainStore,
	ruleManager *manager.RuleManager, ledgerCache protocol.LedgerCache, chainConfig protocol.ChainConf,
	logger protocol.Logger) conn.BlockHandler {
	return &BlockSender{
		remoter:      remoter,
		newBlockChan: make(chan uint64, 1),
		notifier:     notifier,
		ruleManager:  ruleManager,
		slicer:       types.NewBlockSlicer(logger),
		storage:      storage,
		chainConfig:  chainConfig,
		ledgerCache:  ledgerCache,
		logger:       logger,
	}
}

// ServeBlock handles the main logic for sending blocks.
// It starts from the specified height in the request and sends the specified number of blocks.
// The sending stops when the latest block of the current node is sent.
func (b *BlockSender) ServeBlock(blockWriter conn.BlockWriter, request *types.BlockSyncRequest) {
	b.logger.Infof("[provider] serve block request: %v from: %s", request, blockWriter.NodeID())

	if request.ModeData.Type() != setting.SyncModeTypeSharding {
		b.logger.Errorf("unsupported mode type: %d", request.ModeData.Type())
		return
	}
	spec, _ := request.ModeData.ToMode().Spec().(setting.ShardingModeSpec)
	// Handle invalid request parameters
	if spec.Nodes < 1 {
		return
	}

	// Get the last committed block from the ledger cache
	lastBlock := b.ledgerCache.GetLastCommittedBlock()

	// If the current node's latest committed block height is less than the request's starting block height, do not process
	if lastBlock.Header.BlockHeight < request.Height {
		return
	}

	// Check synchronization rules
	if !b.checkRules(blockWriter.NodeID(), request.Height) {
		// Terminate the block writer if rules are not met
		blockWriter.Terminate(errors.ErrCodeRuleNotMeet)

		// Flush any buffered data in the block writer
		if flusher, ok := blockWriter.(conn.BlockFlusher); ok {
			flusher.Flush()
		}

		b.logger.Infof("[handler] check rules failed, stop serve block")
		return
	}

	// Start pushing blocks
	b.pushBlock(blockWriter, blockRequest{
		Height:           request.Height,
		Num:              request.Num,
		WithRWSet:        request.WithRWSet,
		ShardingModeSpec: spec,
	})
}

// Remoter 推送的对端nodeId
func (b *BlockSender) Remoter() string {
	return b.remoter
}

// checkRules checks if the synchronization rules are met for the given node and height
//
//  1. If the local node has no rules set, the check passes
//  2. If the local node has rules set and the remote node has no rules set, the check fails
//  3. If the local node and remote node have rules set, the check passes if the remote node's
//     rules are a subset of the local node's rules
func (b *BlockSender) checkRules(nodeId string, height uint64) bool {
	// Get the rules for the remote node at the given height
	requestNodeRule := b.ruleManager.GetNodeRule(nodeId, height)

	// Get the rules for the local node at the given height
	ownRule := b.ruleManager.OwnRule(height)
	b.logger.Debugf("check rules: ownRule: %v, node[%s] rule: %v, at height: %d", ownRule, nodeId, requestNodeRule, height)

	// Check if the local node has rules set
	if !hasRule(ownRule) {
		return true
	}

	// Check if the remote node has rules set
	if !hasRule(requestNodeRule) {
		b.logger.Warnf("check rules failed for node [%s] at height [%d]", nodeId, height)
		return false
	}

	// Check if the remote node's rules are a subset of the local node's rules
	return rule.CompareRules(ownRule.Content, requestNodeRule.Content)
}

// pushBlock pushes blocks to the block writer until the specified height is reached or
// the setting item is invalid.
func (b *BlockSender) pushBlock(blockWriter conn.BlockWriter, request blockRequest) {
	height := request.Height
	var (
		stopHeight     uint64 = math.MaxUint64
		nodeId                = blockWriter.NodeID()
		nextRuleHeight        = b.nextRuleHeight(nodeId, height)
	)
	if request.Num != 0 {
		stopHeight = request.Height + uint64(request.Num) - 1
	}

	b.logger.Infof("[handler] start push block from height[%d], stop height[%d]", height, stopHeight)

	// Flush the data frame to ensure that the block writer is empty
	defer func() {
		if flusher, ok := blockWriter.(conn.BlockFlusher); ok {
			if err := flusher.Flush(); err != nil {
				b.logger.Warnf("block writer flush failed with [%v]", err)
			}
		}
	}()

	for {
		// 1. If the current height is greater than the stop height, exit the loop.
		if height > stopHeight {
			b.logger.Infof("[handler] sync block finished for [%v]", request)
			return
		}
		// 2. If the current height is less than or equal to the latest block height of the local node,
		//    prepare and send the data fragment.
		if height <= b.notifier.lastHeight {
			// 2.1 Get the next rule height for the remote node.
			// If the next rule height is 0, it means that there is no next rule.
			b.logger.Infof("[handler] next rule height [%d]", nextRuleHeight)
			// 2.2 If the current height is equal to the next rule height,
			//     check if the rule is included in the local node's rules.
			//     If not, terminate the block writer.
			if height == nextRuleHeight {
				// 2.2.1 If the rule is included, update the next rule height.
				if !b.checkRules(nodeId, height) {
					b.logger.Infof("[handler] check rules failed, terminate push[%d]", height)
					blockWriter.Terminate(errors.ErrCodeRuleNotMeet)
					return
				}
				nextRuleHeight = b.nextRuleHeight(nodeId, height)
				// else {
				// 	nextRuleHeight = b.ruleManager.GetNextRuleFromHeight(nodeId, height)
				// }
			} else if height > nextRuleHeight {
				// 2.3 If the current height is greater than the next rule height,
				//     it means that the rule has been changed, so update the current height
				//     and continue to send blocks.
				height = b.ruleManager.GetCurrentRuleFromHeight(nodeId, height)
				b.logger.Infof("[handler] current height larger than next rule height，"+
					"change current height to [%d]", height)
				continue
			}

			// 2.4 Prepare the data fragment.
			dataFragment, err := b.prepareDataFragment(blockWriter, height, request)
			if err != nil {
				blockWriter.Terminate(errors.ErrCodeBuildData)
				b.logger.Errorf("prepare data fragment for height[%d] failed: %s", height, err)
				return
			}
			// 2.5 Send the data fragment.
			// If an error occurs, terminate the block writer.
			b.logger.Infof("start write data fragment, height: %d", height)
			if connError := blockWriter.Write(*dataFragment); connError != nil {
				if connError == errors.ErrPushEOF {
					b.logger.Infof("push over at height: %d", height)
				} else {
					b.logger.Errorf("write block failed, err: %s", connError)
				}
				return
			}

		} else {
			// 3. If the current height is greater than the latest block height of the local node,
			//    wait for new blocks to be generated.
			//    First, clear the newBlockChan to prevent any remaining blocks from being sent.
			b.logger.Infof("[handler] waiting for new block,height [%d]", height)
			b.newBlockChan = make(chan uint64, 1)
			if h := b.notifier.WaitingForNewBlock(b, height); h == 0 {
				// If the newBlockChan is closed, exit the loop.
				return
			}

			continue
		}
		height++
	}
}

// nextRuleHeight returns the next rule height for the given node and height.
// It returns the minimum of the next rule height of the node and the next rule height of the local node.
func (b *BlockSender) nextRuleHeight(nodeId string, height uint64) uint64 {
	var (
		nRuleHeight, oRuleHeight uint64 = math.MaxUint64, math.MaxUint64
	)
	// Get the next rule height of the node.
	if rule := b.ruleManager.GetNodeNextRuleAtHeight(nodeId, height); rule != nil {
		nRuleHeight = rule.BeginHeight
	}
	// Get the next rule height of the local node.
	if rule := b.ruleManager.OwnNextRuleAtHeight(height); rule != nil {
		oRuleHeight = rule.BeginHeight
	}
	// Return the minimum of the two.
	if nRuleHeight <= oRuleHeight {
		return nRuleHeight
	}
	return oRuleHeight
}

// prePareDataFragment 准备固定高度的数据分片
// sliceBytes 是types.DataFragment中的DATA
// sliceBytes = proto.SliceData
func (b *BlockSender) prepareDataFragment(blockWriter conn.BlockWriter, height uint64,
	request blockRequest) (*types.DataFragment, error) {

	var (
		err            error
		sliceBytes     []byte
		blockWithRWSet *store.BlockWithRWSet
	)

	// 发送的分片数据，前两个字节为ruleId
	// currentRuleId := b.ruleManager.GetCurrentRuleId(blockWriter.NodeID(), height)
	rule := b.ruleManager.GetNodeRule(blockWriter.NodeID(), height)
	b.logger.Infof("[handler] start prepare data fragment, height[%d], rule id [%d]", height, rule.GetId())
	sliceData := &syncPb.SliceData{
		Version: b.chainConfig.ChainConfig().GetBlockVersion(),
		RuleId:  uint64(rule.GetId()),
		Data:    nil,
	}

	if request.Nodes < 1 {
		return nil, types.ErrInvalidNodesTotal
	}

	// 准备区块数据
	blockWithRWSet, err = b.prepareBlock(height, blockWriter.NodeID(), request.WithRWSet, rule)
	if err != nil {
		return nil, err
	}
	// 不启用分片的时候，直接拼装dataBytes
	if request.Nodes == 1 {
		sliceData.Data, err = proto.Marshal(blockWithRWSet)
		if err != nil {
			return nil, err
		}
	} else {
		// 切割分片
		// 最后一个index，负责发送additionalData
		sliceBytes, err = b.slicer.SliceBlockFragment(int(request.Nodes), int(request.Index), blockWithRWSet)
		if err != nil {
			return nil, err
		}
		sliceData.Data = sliceBytes
	}

	sliceDataBz, err := proto.Marshal(sliceData)
	if err != nil {
		return nil, err
	}

	// 构建发送数据帧
	dataFragment := &types.DataFragment{
		Height: height,
		Data:   sliceDataBz,
	}

	return dataFragment, nil
}

// prepareBlock 准备同步的区块
func (b *BlockSender) prepareBlock(height uint64,
	receptorId string, withRWSet bool, currentRule *syncPb.Rule) (*store.BlockWithRWSet, error) {
	blockWithRWSet, err := b.storage.GetBlockWithRWSets(height)
	if err != nil {
		return nil, err
	}

	// 查询节点接收端节点是否有过滤规则
	// 是普通交易区块，且有过滤规则，则进行交易过滤
	// currentRule := b.ruleManager.GetNodeRuleById(receptorId, currentRuleId)
	if isNormalBlock(blockWithRWSet.Block) && currentRule != nil {
		// blockWithRWSet.Block, err = b.filterTxs(blockWithRWSet.GetBlock(), receptorId, currentRule)
		blockWithRWSet, err = b.filterTxs(blockWithRWSet, receptorId, currentRule)
		return blockWithRWSet, err
	}

	// 没有规则
	// 是否快速同步: 是 不管，不是 则读写集置空
	if !withRWSet {
		blockWithRWSet.TxRWSets = []*common.TxRWSet{}
		blockWithRWSet.ContractEvents = []*common.ContractEvent{}
	}
	return blockWithRWSet, err
}

// appendTxHashes 计算每一笔交易的Hash，并写入 additionalData中
// 用于提交区块的时候，Core模块验证区块使用
// func (b *BlockSender) appendTxHashes(blockWithRWSet *store.BlockWithRWSet) (*store.BlockWithRWSet, error) {
// 	txHashSet := &syncPb.TxHashSet{TxHashSet: make(map[string][]byte, len(blockWithRWSet.Block.Txs))}
// 	blockVersion := int(blockWithRWSet.Block.Header.BlockVersion)
// 	// 将每一条交易，都计算Hash值，并存到b.txHashSet中
// 	for _, tx := range blockWithRWSet.Block.Txs {
// 		txHash, err := utils.CalcTxHashWithVersion(b.chainConfig.ChainConfig().Crypto.Hash, tx, blockVersion)
// 		if err != nil {
// 			return nil, err
// 		}
// 		txHashSet.TxHashSet[tx.Payload.TxId] = txHash
// 	}
// 	// 如果AdditionalData为空的时候，初始化AdditionalData
// 	if blockWithRWSet.Block.AdditionalData == nil {
// 		blockWithRWSet.Block.AdditionalData = &common.AdditionalData{
// 			ExtraData: make(map[string][]byte),
// 		}
// 	}

// 	bz, err := proto.Marshal(txHashSet)
// 	if err != nil {
// 		return nil, err
// 	}
// 	blockWithRWSet.Block.AdditionalData.ExtraData[protocol.SYNC_txHash_set_key] = bz
// 	return blockWithRWSet, nil
// }

// filterTxs filters transactions in a block based on a specified rule and receptor ID.
// It removes transactions that do not meet the filter criteria and updates the block and RWSet accordingly.
// It also generates a hash set of the filtered transactions.
func (b *BlockSender) filterTxs(blockWithRWSet *store.BlockWithRWSet,
	receptorId string, rule *syncPb.Rule) (*store.BlockWithRWSet, error) {
	block, rwSetList := blockWithRWSet.GetBlock(), blockWithRWSet.GetTxRWSets()
	b.logger.Infof("[handler] filter block [%d] txs, use rule [%s]", block.Header.BlockHeight, rule.Content)

	ts, err := b.ruleManager.GetRulePermTs(receptorId, rule)
	if err != nil {
		return blockWithRWSet, nil
	}

	txHashSet := &syncPb.TxHashSet{TxHashSet: make(map[string][]byte, len(blockWithRWSet.Block.Txs))}
	blockVersion := int(blockWithRWSet.Block.Header.BlockVersion)

	// Function to remove a transaction from the RWSetList
	removeRWSet := func(rwSetList []*common.TxRWSet, txId string) {
		for i, rwSet := range rwSetList {
			if rwSet != nil && rwSet.TxId == txId {
				rwSetList[i] = nil
				break
			}
		}
	}

	// Function to add a transaction hash to the TxHashSet
	addTxHash := func(hashSet map[string][]byte, tx *common.Transaction) error {
		txHash, err := utils.CalcTxHashWithVersion(b.chainConfig.ChainConfig().Crypto.Hash, tx, blockVersion)
		if err != nil {
			return err
		}
		hashSet[tx.Payload.TxId] = txHash
		return nil
	}

	// Iterate over the transactions in the block
	for index, tx := range block.Txs {
		// Check if the transaction meets the filter criteria
		if !ts.IsSpecifiedTx(tx) {
			// Replace the transaction with a simplified version that only contains TxId
			block.Txs[index] = &common.Transaction{
				Payload: &common.Payload{
					TxId: tx.Payload.TxId,
				},
				Sender: tx.Sender,
				Result: &common.Result{
					RwSetHash: tx.Result.RwSetHash,
				},
			}
			// Remove the transaction from the RWSetList
			removeRWSet(rwSetList, tx.Payload.TxId)
			// Add the transaction hash to the TxHashSet
			if err := addTxHash(txHashSet.TxHashSet, tx); err != nil {
				return nil, err
			}
		}
	}

	// If there are transactions in the TxHashSet, marshal it and add it to the AdditionalData of the block
	if len(txHashSet.TxHashSet) > 0 {
		bz, err := proto.Marshal(txHashSet)
		if err != nil {
			return nil, err
		}
		if blockWithRWSet.Block.AdditionalData == nil {
			blockWithRWSet.Block.AdditionalData = &common.AdditionalData{
				ExtraData: make(map[string][]byte),
			}
		}
		blockWithRWSet.Block.AdditionalData.ExtraData[protocol.SYNC_txHash_set_key] = bz
	}

	// Rearrange the RWSetList to remove any nil values
	fillIdx := -1
	for i, rwSet := range rwSetList {
		if rwSet == nil {
			if fillIdx < 0 {
				fillIdx = i
			}
			continue
		}
		if fillIdx >= 0 {
			rwSetList[fillIdx] = rwSet
			fillIdx++
		}
	}
	if fillIdx >= 0 {
		blockWithRWSet.TxRWSets = rwSetList[:fillIdx]
	}

	return blockWithRWSet, nil
}

// NewBlockChan get the channel.
func (b *BlockSender) NewBlockChan() chan uint64 {
	return b.newBlockChan
}

// Close 关闭block sender
func (b *BlockSender) Close() {

}

func isNormalBlock(block *common.Block) bool {
	return block.Header.BlockType == common.BlockType_NORMAL_BLOCK &&
		!(len(block.GetTxs()) == 1 && utils.IsManagementTx(block.Txs[0]))

}
