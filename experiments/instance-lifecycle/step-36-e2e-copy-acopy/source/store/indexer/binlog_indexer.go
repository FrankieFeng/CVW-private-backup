/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package indexer

import (
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/store/v2/binlog"
	"chainmaker.org/chainmaker/store/v2/serialization"
)

var _ BinLoggerIndexer = (*binLoggerIndexer)(nil)

// binLoggerIndexer is a indexer based on binlog.
// It stands to reason that binLoggerIndexer should have full control over how block are serialized,
// but it use the NormalBlockSerializer from package serialization,
// NormalBlockSerializer ensures that the byte slice can be decoded externally by the same codec.
type binLoggerIndexer struct {
	binlog.BinLogger
	*NormalBlockFileIndexer
	logger protocol.Logger
}

// NewBinLoggerIndexer create a binLoggerIndexer instance use binlogger and normalizer.
func NewBinLoggerIndexer(binlogger binlog.BinLogger, normalizer serialization.BlockNormalizer,
	logger protocol.Logger, opts ...NormalizeIndexerOption) BinLoggerIndexer {
	return &binLoggerIndexer{
		BinLogger: binlogger,
		NormalBlockFileIndexer: NewNormalBlockFileIndexer(
			&indexerBinlog{binlogger}, normalizer, logger, opts...),
		logger: logger,
	}
}

var _ IndexerFile = (*indexerBinlog)(nil)

type indexerBinlog struct {
	binlog.BinLogger
}

// WriteAndLocate write data into binlog file and return the index info of the data.
func (b *indexerBinlog) WriteAndLocate(height uint64, data []byte) (*storePb.StoreInfo, error) {
	fileName, offset, bytesLen, err := b.BinLogger.Write(height+1, data)
	if err != nil {
		return nil, err
	}
	return &storePb.StoreInfo{
		FileName: fileName,
		Offset:   offset,
		ByteLen:  bytesLen,
	}, nil
}

// ReadAndLocate read data by lable'index' from file and return the index info.
func (b *indexerBinlog) ReadAndLocate(height uint64, opt *ReadOptions) ([]byte, *storePb.StoreInfo, error) {
	fromLatestFile := false
	if opt != nil {
		fromLatestFile = opt.FromLatestFile
	}
	data, fileName, offset, bytesLen, err := b.BinLogger.ReadLastSegSection(height+1, !fromLatestFile)
	if err != nil {
		return nil, nil, err
	}
	return data, &storePb.StoreInfo{
		FileName: fileName,
		Offset:   offset,
		ByteLen:  bytesLen,
	}, err
}

// ReadAt read data from file by index info.
func (b *indexerBinlog) ReadAt(fiIndex *storePb.StoreInfo) ([]byte, error) {
	return b.BinLogger.ReadFileSection(fiIndex, 0)
}
