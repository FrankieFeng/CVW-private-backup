/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package indexer

import (
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/store/v2/binlog"
	"chainmaker.org/chainmaker/store/v2/serialization"
)

// Assembler is used to merge scattered data into a complete sequence and separate it into subsequences.
type Assembler interface {
	// Assembly the serialized parts in SerializationNormalized into complete block data
	// in its own way and generating index information of each part in the complete data.
	Assembly(*serialization.SerializationNormalized) ([]byte, *serialization.BlockIndex, error)
	// Disassembly unpacks a complete character sequence into the serialized parts of the normalized data,
	// It does not deserialize the serialized parts of the normalized data into structures.
	// Therefore, the object pointers in BlockNormalized are nil.
	Disassembly([]byte) (*serialization.SerializationNormalized, error)
}

// IndexerFile is used to store and read index info.
type IndexerFile interface {
	// WriteAndLocate write data to file and return the index info.
	// The param height which is the height of block, it is used to index the data in file.
	WriteAndLocate(height uint64, data []byte) (*storePb.StoreInfo, error)
	// ReadAndLocate read data by height from file and return the index info.
	ReadAndLocate(height uint64, opt *ReadOptions) ([]byte, *storePb.StoreInfo, error)
	// ReadAt read data from file by index info.
	ReadAt(fiIndex *storePb.StoreInfo) ([]byte, error)
}

// NormalizeBlockAssembler undertakes the task of normalize block data and serializing it into bytes.
type NormalizeBlockAssembler interface {
	// BlockNormalizer get the normalizer.
	BlockNormalizer() serialization.BlockNormalizer
	Assembler
}

// BlockFile is used to store and read block data.
type BlockFile interface {
	// WriteBlock normalize the block and write the bytes serialized into log file, record the index info.
	WriteBlock(*storePb.BlockWithRWSet) (*serialization.BlockNormalized, *serialization.BlockIndex, error)
	//ReadBlock reads a block by height, return the block and index info.
	ReadBlock(height uint64, opts ...ReadOption) (*storePb.BlockWithRWSet, *storePb.StoreInfo, error)
}

// BlockFileIndexer undertakes the task of indexing block data and interpret them.
type BlockFileIndexer interface {
	// IndexBlockMetaAt indexes data at the given position and interpret to the block meta .
	IndexBlockMetaAt(fiIndex *storePb.StoreInfo) (*storePb.SerializedBlock, error)
	// IndexBlockAt indexes data at the given position and interpret to the block .
	IndexBlockAt(fiIndex *storePb.StoreInfo) (*storePb.BlockWithRWSet, error)
	// IndexTxAt indexes data at the given position and interpret to the Transaction .
	IndexTxAt(fiIndex *storePb.StoreInfo) (*commonPb.Transaction, error)
	// IndexRWSetAt indexes data at the given position and interpret to the TxRWSet .
	IndexRWSetAt(fiIndex *storePb.StoreInfo) (*commonPb.TxRWSet, error)
}

// NormalizeBlockFileIndexer undertakes the task of normalize block data and serializing it into files.
// So, it know how to index the serialized data and interpret them.
type NormalizeBlockFileIndexer interface {
	NormalizeBlockAssembler
	BlockFile
	BlockFileIndexer
}

// BinLoggerIndexer Inherited from binlog.BinLogger and NormalizeBlockFileIndexer
// It know how to store block into binlogger and cnstructs objects from binlogger.
type BinLoggerIndexer interface {
	binlog.BinLogger
	NormalizeBlockFileIndexer
}

// BlockWalIndexer used to adapt the data index of WAL
type BlockWalIndexer interface {
	NormalizeBlockAssembler
	BlockFile
}

// BytesCodec provides bytes encoding and decoding functions. such as encrypt and decrypt bytes.
type BytesCodec interface {
	// Encode bytes to a new bytes
	Encode([]byte) ([]byte, error)
	// Decode bytes to original bytes
	Decode([]byte) ([]byte, error)
}

// normalizedBlockAssembler
// 1. Assemble each part of the serialized data in the normalized block data into a complete sequence.
// 2. Disassembly a complete sequence into each serial part in the normalized data
type normalizedBlockAssembler interface {
	Assembler
	// Plate to mask the original appearance of the data by plating it with something.
	// Used in the assembly process to plate all data fragments.
	Plate([]byte) ([]byte, error)
	// Deplate to deplate the data frament in order to restore its original appearance.
	// Used in the disassembly process to deplate all data fragments.
	Deplate([]byte) ([]byte, error)
}
