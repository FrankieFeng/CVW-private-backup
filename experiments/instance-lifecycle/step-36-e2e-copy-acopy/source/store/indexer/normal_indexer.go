/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package indexer

import (
	"time"

	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/store/v2/serialization"
)

var _ NormalizeBlockFileIndexer = (*NormalBlockFileIndexer)(nil)

// NormalBlockFileIndexer is a normal indexer can been inherited by other indexers implemention.
// Accepts the normalizer to normalize the block data,
// and then constructs the character sequence to writes into file and record the index info.
type NormalBlockFileIndexer struct {
	IndexerFile
	blockNormalizer serialization.BlockNormalizer
	assembler       normalizedBlockAssembler
	logger          protocol.Logger
}

var defaultOpts = NormalizeIndexerOptions{
	bCodec: nopBytesCodec{},
}

// NewNormalBlockFileIndexer create a NormalBlockFileIndexer instance use indexerFile and normalizer.
// bCodec is used to encode and decode bytes which will been written into files,
// such as encrypt and decrypt bytes.
func NewNormalBlockFileIndexer(file IndexerFile, normalizer serialization.BlockNormalizer,
	logger protocol.Logger, opts ...NormalizeIndexerOption) *NormalBlockFileIndexer {
	opt := defaultOpts
	for _, o := range opts {
		o(&opt)
	}
	return &NormalBlockFileIndexer{
		IndexerFile:     file,
		blockNormalizer: normalizer,
		assembler:       newNormalAssembler(opt.bCodec),
		logger:          logger,
	}
}

// WriteBlock serializes block and write the bytes serialized into binlog, and return the block index info.
//  1. Serialize each part of the block data.
//  2. Assemble the serialized data fragments which may be encrypted into a complete sequence,
//     and record the position information of the subsequence in the complete sequence.
//  2. Write the complete sequence in to file and record the index info of the sequence in file.
func (b *NormalBlockFileIndexer) WriteBlock(blockWithRWSet *storePb.BlockWithRWSet) (
	*serialization.BlockNormalized, *serialization.BlockIndex, error) {
	t := time.Now()
	normal, bytes, location, err := b.indexFor(blockWithRWSet)
	if err != nil {
		b.logger.Infof("add block %d to indexer, serialize block error: %v",
			blockWithRWSet.Block.Header.BlockHeight, err)
		return nil, nil, err
	}
	serializationDt := time.Since(t)
	location.Index, err = b.IndexerFile.WriteAndLocate(blockWithRWSet.Block.Header.BlockHeight, bytes)
	if err != nil {
		b.logger.Infof("add block %d to indexer, write file error: %v",
			blockWithRWSet.Block.Header.BlockHeight, err)
		return nil, nil, err
	}
	writeDt := time.Since(t)
	b.logger.Infof("add block [%d] to indexer, (tx: %d, bytes: %d), time used: serialize %v, write file %v",
		blockWithRWSet.Block.Header.BlockHeight, len(blockWithRWSet.Block.GetTxs()), len(bytes),
		serializationDt.Milliseconds(), (writeDt - serializationDt).Milliseconds())
	return normal, location, nil
}

// ReadBlock reads a block by height, return the block and index info.
//  1. Read the complete sequence in the file by height.
//  2. Disassembly the complete sequence to each serial part in the normalized data.
//  3. Deserialize the serialized parts of the normalized data into structures.
//  4. Return the block and index info.
func (b *NormalBlockFileIndexer) ReadBlock(height uint64,
	opts ...ReadOption) (*storePb.BlockWithRWSet, *storePb.StoreInfo, error) {
	var opt ReadOptions
	for _, o := range opts {
		o(&opt)
	}
	data, location, err := b.ReadAndLocate(height, &opt)
	if err != nil {
		return nil, nil, err
	}

	var block *storePb.BlockWithRWSet
	if block, err = b.recoveryBlockFromBytes(data); err != nil {
		return nil, nil, err
	}
	return block, location, nil
}

// IndexBlockMetaAt get bytes from binglogger by index information and decode it to Block Meta.
func (b *NormalBlockFileIndexer) IndexBlockMetaAt(fiIndex *storePb.StoreInfo) (*storePb.SerializedBlock, error) {
	sb := &storePb.SerializedBlock{}
	if err := b.indexObjAt(fiIndex, sb); err != nil {
		return nil, err
	}
	return sb, nil
}

// IndexBlockAt get bytes from binglogger by index information and decode it to BlockWithRWSet.
func (b *NormalBlockFileIndexer) IndexBlockAt(fiIndex *storePb.StoreInfo) (*storePb.BlockWithRWSet, error) {
	data, err := b.IndexerFile.ReadAt(fiIndex)
	if err != nil {
		return nil, err
	}
	return b.recoveryBlockFromBytes(data)
}

// recoveryBlockFromBytes 1. disassembly the complete sequence into each serial part in the normalized data
// 2. deserialize the serialized parts of the normalized data into structures.
func (b *NormalBlockFileIndexer) recoveryBlockFromBytes(bytes []byte) (*storePb.BlockWithRWSet, error) {
	sn, err := b.assembler.Disassembly(bytes)
	if err != nil {
		return nil, err
	}
	normal, err := b.blockNormalizer.NormalizeFromSerialization(sn)
	if err != nil {
		return nil, err
	}
	return normal.ToBlockWithRWSet(), nil
}

// IndexTxAt get bytes from binglogger by index information and decode it to Transaction.
func (b *NormalBlockFileIndexer) IndexTxAt(fiIndex *storePb.StoreInfo) (*commonPb.Transaction, error) {
	obj := &commonPb.Transaction{}
	if err := b.indexObjAt(fiIndex, obj); err != nil {
		return nil, err
	}
	return obj, nil
}

// IndexRWSetAt get bytes from binglogger by index information and decode it to TxRWSet.
func (b *NormalBlockFileIndexer) IndexRWSetAt(fiIndex *storePb.StoreInfo) (*commonPb.TxRWSet, error) {
	obj := &commonPb.TxRWSet{}
	if err := b.indexObjAt(fiIndex, obj); err != nil {
		return nil, err
	}
	return obj, nil
}

// indexObjAt read bytes sequence which is a part of the complete sequence from binglogger by index information.
// Restore data to original bytes and deserialize it intto struct.
func (b *NormalBlockFileIndexer) indexObjAt(fiIndex *storePb.StoreInfo, obj interface{}) error {
	data, err := b.IndexerFile.ReadAt(fiIndex)
	if err != nil {
		return err
	}
	data, err = b.assembler.Deplate(data)
	if err != nil {
		return err
	}
	return b.blockNormalizer.Serializer().Decode(data, obj)
}

// IndexForBlock get bytes from binglogger by block information and decode it to BlockWithRWSet
func (b *NormalBlockFileIndexer) IndexForBlock(block *storePb.BlockWithRWSet) ([]byte,
	*serialization.BlockWithSerializedInfo, error) {
	normal, bytes, index, err := b.indexFor(block)
	if err != nil {
		return nil, nil, err
	}
	return bytes, &serialization.BlockWithSerializedInfo{
		BlockNormalized: *normal,
		BlockIndex:      *index,
	}, nil
}

// Assembly each subsequence in the normalized serialization data into a complete sequence
func (b *NormalBlockFileIndexer) Assembly(sn *serialization.SerializationNormalized) (
	[]byte, *serialization.BlockIndex, error) {
	return b.assembler.Assembly(sn)
}

// Disassembly the sequence into subsequences according to the assembly order.
func (b *NormalBlockFileIndexer) Disassembly(data []byte) (*serialization.SerializationNormalized, error) {
	return b.assembler.Disassembly(data)
}

func (b *NormalBlockFileIndexer) indexFor(blockWithRWSet *storePb.BlockWithRWSet) (
	*serialization.BlockNormalized, []byte, *serialization.BlockIndex, error) {
	// First, normalize the block data into a storage agreed structure.
	normal, err := b.blockNormalizer.NormalizeBlock(blockWithRWSet)
	if err != nil {
		return nil, nil, nil, err
	}
	// assembly each subsequence in the normalized serialization data into a complete sequence,
	// and record the location information of each data fragment.
	// The data fragments will be encrypted and decrypted if encryption is configured.
	bytes, location, err := b.Assembly(&normal.SerializationNormalized)
	if err != nil {
		return nil, nil, nil, err
	}
	return normal, bytes, location, nil
}

// BlockNormalizer get the normalizer for block.
func (b *NormalBlockFileIndexer) BlockNormalizer() serialization.BlockNormalizer {
	return b.blockNormalizer
}

// Codec get sink codec.
func (b *NormalBlockFileIndexer) Codec() serialization.Serializer {
	return newIndexerCodec(b)
}

// NormalizeIndexerOptions options for NormalizeIndexer
type NormalizeIndexerOptions struct {
	bCodec BytesCodec
}

// NormalizeIndexerOption option set functionfor NormalizeIndexer
type NormalizeIndexerOption func(*NormalizeIndexerOptions)

// WithBytesCodes set BytesCodec to options
func WithBytesCodes(c BytesCodec) NormalizeIndexerOption {
	return func(nbfio *NormalizeIndexerOptions) {
		nbfio.bCodec = c
	}
}
