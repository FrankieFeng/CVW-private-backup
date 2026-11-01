/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0

*/

package historykvdb

import (
	"encoding/binary"
	"fmt"
	"time"

	"chainmaker.org/chainmaker/protocol/v2"
	leveldbprovider "chainmaker.org/chainmaker/store-leveldb/v2"
	"chainmaker.org/chainmaker/store/v2/cache"
	"chainmaker.org/chainmaker/store/v2/conf"
	"chainmaker.org/chainmaker/store/v2/historydb"
	"chainmaker.org/chainmaker/store/v2/serialization"
	"chainmaker.org/chainmaker/store/v2/types"
	"chainmaker.org/chainmaker/utils/v2"
)

const (
	keyHistoryPrefix        = "k"
	accountTxHistoryPrefix  = "a"
	contractTxHistoryPrefix = "c"
	historyDBSavepointKey   = "historySavepointKey"
	splitChar               = "#"
	splitCharPlusOne        = "$"
)

// HistoryKvDB provider an implementation of `historydb.HistoryDB`
// @Description:
// This implementation provides a key-value based data model
type HistoryKvDB struct {
	dbHandle protocol.DBHandle
	cache    *cache.FIFOBlockCache
	logger   protocol.Logger
	config   *conf.HistoryDbConfig
}

// NewHistoryKvDB init historyKvDB handler
// @Description:
// @param chainId
// @param config
// @param db
// @param logger
// @return *HistoryKvDB
func NewHistoryKvDB(chainId string, config *conf.HistoryDbConfig, db protocol.DBHandle,
	logger protocol.Logger) *HistoryKvDB {
	return &HistoryKvDB{
		dbHandle: db,
		config:   config,
		cache:    cache.NewFIFOBlockCache(0, logger),
		logger:   logger,
	}
}

// InitGenesis init genesis block
// @Description:
// @receiver h
// @param genesisBlock
// @return error
func (h *HistoryKvDB) InitGenesis(genesisBlock *serialization.BlockWithSerializedInfo) error {
	err := h.CommitBlock(genesisBlock, true)
	if err != nil {
		return err
	}
	return h.CommitBlock(genesisBlock, false)
}

// CommitBlock commits the block rwsets in an atomic operation
// @Description:
// @receiver h
// @param blockInfo
// @param isCache
// @return error
func (h *HistoryKvDB) CommitBlock(blockInfo *serialization.BlockWithSerializedInfo, isCache bool) error {

	batchGen := func(blockInfo *serialization.BlockWithSerializedInfo) protocol.StoreBatcher {
		batch := types.NewUpdateBatch()
		// 1. last block height
		block := blockInfo.Block
		lastBlockNumBytes := make([]byte, 8)
		binary.BigEndian.PutUint64(lastBlockNumBytes, block.Header.BlockHeight)
		batch.Put([]byte(historyDBSavepointKey), lastBlockNumBytes)
		blockHeight := block.Header.BlockHeight
		txRWSets := blockInfo.TxRWSets
		if !h.config.DisableKeyHistory {
			for index, txRWSet := range txRWSets {
				txID := txRWSet.TxId
				for _, write := range txRWSet.TxWrites {
					key := constructKey(write.ContractName, write.Key, blockHeight, txID, uint64(index))
					batch.Put(key, []byte{0}) //write key modify history
				}
			}
		}

		if !h.config.DisableAccountHistory || !h.config.DisableContractHistory {
			for _, tx := range block.Txs {
				accountID := tx.GetSenderAccountId()
				txID := tx.Payload.TxId
				contractName := tx.Payload.ContractName
				if !h.config.DisableAccountHistory {
					batch.Put(constructAcctTxHistKey(accountID, blockHeight, txID), []byte{0})
				}
				if !h.config.DisableContractHistory {
					batch.Put(constructContractTxHistKey(contractName, blockHeight, txID), []byte{0})
				}
			}
		}
		return batch
	}

	start := time.Now()
	block := blockInfo.Block
	if isCache {
		h.logger.Debugf("[historydb]start CommitCache currtime[%d]", utils.CurrentTimeMillisSeconds())
		batch := batchGen(blockInfo)
		// h.logger.Debugf("[historydb]3 CommitCache currtime[%d]", utils.CurrentTimeMillisSeconds())
		// update cache
		h.cache.PushBlock(&cache.BlockBatch{Height: block.Header.BlockHeight, Batcher: batch})
		h.logger.Debugf("[historydb]end CommitCache currtime[%d]", utils.CurrentTimeMillisSeconds())

		h.logger.Debugf("chain[%s]: commit cache block[%d] historydb, batch[%d], time used: %d",
			block.Header.ChainId, block.Header.BlockHeight, batch.Len(),
			time.Since(start).Milliseconds())
		return nil
	}

	bt, exist := h.cache.PeekMinBlock()
	//should not happen
	if !exist || bt.Height != block.Header.BlockHeight {
		h := uint64(0)
		if bt != nil {
			h = bt.Height
		}
		panic(fmt.Sprintf("get block from cache wrong: need block[%d], but got[%d]",
			block.Header.BlockHeight, h))
	}

	batch := bt.Batcher
	batchDur := time.Since(start)
	err := h.writeBatch(block.Header.BlockHeight, batch)
	if err != nil {
		return err
	}
	h.cache.PopBlock()
	writeDur := time.Since(start)
	h.logger.Debugf("chain[%s]: commit block[%d] kv historydb, time used (batch[%d]:%d, "+
		"write:%d, total:%d)", block.Header.ChainId, block.Header.BlockHeight, batch.Len(),
		batchDur.Milliseconds(), (writeDur - batchDur).Milliseconds(), time.Since(start).Milliseconds())
	return nil
}

// GetLastSavepoint returns the last block height
// @Description:
// @receiver h
// @return uint64
// @return error
func (h *HistoryKvDB) GetLastSavepoint() (uint64, error) {
	bytes, err := h.get([]byte(historyDBSavepointKey))
	if err != nil {
		return 0, err
	} else if bytes == nil {
		return 0, nil
	}
	num := binary.BigEndian.Uint64(bytes)
	return num, nil
}

// Close is used to close database
// @Description:
// @receiver h
func (h *HistoryKvDB) Close() {
	h.logger.Info("close history kv db")
	h.dbHandle.Close()
	h.cache.Clear()
}

// writeBatch add next time
// @Description:
// @receiver h
// @param blockHeight
// @param batch
// @return error
func (h *HistoryKvDB) writeBatch(blockHeight uint64, batch protocol.StoreBatcher) error {
	//Devin: 这里如果用了协程，那么UT就不会过，因为查询主要是Prefix查询，而缓存是不支持前缀查询的。
	//TODO: 如果Cache能提供 GetByPrefix 查询就可以重新启用
	//go func() {
	//batches := batch.SplitBatch(102400)
	//wg := &sync.WaitGroup{}
	//wg.Add(len(batches))
	//for i := 0; i < len(batches); i++ {
	//	go func(index int) {
	//		defer wg.Done()
	//		if err := h.dbHandle.WriteBatch(batches[index], true); err != nil {
	//			panic(fmt.Sprintf("Error writing history db: %s", err))
	//		}
	//	}(i)
	//}
	//wg.Wait()
	isLevelDB := h.dbHandle.GetDbType() == leveldbprovider.DbType_Leveldb
	lastKey := []byte(historyDBSavepointKey)
	value, err := batch.Get(lastKey)
	if err != nil {
		return err
	}
	batch.Remove(lastKey)

	if err = h.dbHandle.WriteBatch(batch, !isLevelDB); err != nil {
		panic(fmt.Sprintf("Error writing db: %s", err))
	}

	//db committed, clean cache
	// write savePoint
	if err = h.dbHandle.Put(lastKey, value); err != nil {
		panic(fmt.Sprintf("Error writing db: %s", err))
	}

	return nil
}

// get first query cache,if not hit query db
// @Description:
// @receiver h
// @param key
// @return []byte
// @return error
func (h *HistoryKvDB) get(key []byte) ([]byte, error) {
	//get from cache
	value, exist := h.cache.Get(key)
	if exist {
		return value, nil
	}
	//get from database
	return h.dbHandle.Get(key)

}

//func (h *HistoryKvDB) has(key []byte) (bool, error) {
//	//check has from cache
//	isDelete, exist := h.cache.Has(string(key))
//	if exist {
//		return !isDelete, nil
//	}
//	return h.dbHandle.Has(key)
//}

// historyKeyIterator iterator
// @Description:
type historyKeyIterator struct {
	dbIter    protocol.Iterator
	buildFunc func(key []byte) (*historydb.BlockHeightTxId, error)
}

// Next check has value
// @Description:
// @receiver i
// @return bool
func (i *historyKeyIterator) Next() bool {
	return i.dbIter.Next()
}

// Value get current tx id
// @Description:
// @receiver i
// @return *historydb.BlockHeightTxId
// @return error
func (i *historyKeyIterator) Value() (*historydb.BlockHeightTxId, error) {
	err := i.dbIter.Error()
	if err != nil {
		return nil, err
	}
	return i.buildFunc(i.dbIter.Key())
}

// Release close the iterator
// @Description:
// @receiver i
func (i *historyKeyIterator) Release() {
	i.dbIter.Release()
}
