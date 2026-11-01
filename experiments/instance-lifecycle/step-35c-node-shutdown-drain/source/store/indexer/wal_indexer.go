/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package indexer

import (
	"fmt"

	"chainmaker.org/chainmaker/common/v2/wal"
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/store/v2/serialization"
)

// WalIndexer is a indexer based on wallog.
// The indexer has own way to organize the block into bytes and knows how to index the data
// in each part of the block.
// But due to the characteristics of WAL, it is impossible to directly index sub-partial data of a block
// in wal file based on index information. Just can read the complete block by height.
type WalIndexer struct {
	*wal.Log
	BlockWalIndexer
	logger protocol.Logger
}

// NewWalIndexer create a WalIndexer instance use wal and codec.
func NewWalIndexer(logFile *wal.Log, normalizer serialization.BlockNormalizer,
	logger protocol.Logger, opts ...NormalizeIndexerOption) *WalIndexer {
	return &WalIndexer{
		Log:             logFile,
		BlockWalIndexer: NewNormalBlockFileIndexer(&indexerWal{logFile}, normalizer, logger, opts...),
		logger:          logger,
	}
}

var _ IndexerFile = (*indexerWal)(nil)

type indexerWal struct {
	*wal.Log
}

// WriteAndLocate write data into wal file but no index info generated, wal not supported
func (b *indexerWal) WriteAndLocate(height uint64, data []byte) (*storePb.StoreInfo, error) {
	return &storePb.StoreInfo{
		ByteLen: uint64(len(data)),
	}, b.Log.Write(height+1, data)
}

// WriteAndLocate write data into wal file but no index info.
func (b *indexerWal) ReadAndLocate(height uint64, _ *ReadOptions) ([]byte, *storePb.StoreInfo, error) {
	data, err := b.Log.Read(height + 1)
	return data, nil, err
}

// ReadAt not soupported by wal.
func (b *indexerWal) ReadAt(fiIndex *storePb.StoreInfo) ([]byte, error) {
	return nil, fmt.Errorf("wal not support reading by file index")
}
