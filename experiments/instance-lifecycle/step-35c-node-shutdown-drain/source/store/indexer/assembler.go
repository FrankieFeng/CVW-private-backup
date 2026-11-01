/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package indexer

import (
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/store/v2/serialization"
	"github.com/gogo/protobuf/proto"
)

// NormalAssembler a normal assembler for assembly block data to a complete byte sequence
// which will be writted into file and generate index info for each subsequence.
type NormalAssembler struct {
	bCodec BytesCodec
}

func newNormalAssembler(bCodec BytesCodec) *NormalAssembler {
	return &NormalAssembler{
		bCodec: bCodec,
	}
}

// Assembly each subsequence in the normalized data into a complete sequence according to a certain sequence
// and record the position index of each subsequence in the sequence.
func (a *NormalAssembler) Assembly(block *serialization.SerializationNormalized) (
	[]byte, *serialization.BlockIndex, error) {
	var (
		err   error
		buf   = proto.NewBuffer(nil)
		index = &serialization.BlockIndex{}
	)
	// put metadata(header,dag,txids,additionalData) into buffer and get index
	if index.MetaIndex, err = a.serializeToBuffer(block.SerializedMeta, buf); err != nil {
		return nil, nil, err
	}
	// put each transaction into buffer and get index of each transaction.
	if index.TxsIndex, err = a.serializeBatchToBuffer(block.SerializedTxs, buf, true); err != nil {
		return nil, nil, err
	}
	//put rwset of each transaction into buffer and get index
	if index.RWSetsIndex, err = a.serializeBatchToBuffer(block.SerializedTxRWSets, buf, true); err != nil {
		return nil, nil, err
	}
	//put contract events into buffer
	if _, err = a.serializeBatchToBuffer(block.SerializedContractEvents, buf, false); err != nil {
		return nil, nil, err
	}
	return buf.Bytes(), index, nil
}

// Disassembly the sequence into subsequences according to the assembly order.
func (a *NormalAssembler) Disassembly(in []byte) (*serialization.SerializationNormalized, error) {
	var (
		buf   = proto.NewBuffer(in)
		block = &serialization.SerializationNormalized{}
		err   error
	)
	//pop metadata from buffer.
	if block.SerializedMeta, err = a.deserializeFromBuffer(buf); err != nil {
		return nil, err
	}
	//pop txs from buffer.
	if block.SerializedTxs, err = a.deserializeBatchFromBuffer(buf); err != nil {
		return nil, err
	}
	//pop rwset from buffer.
	if block.SerializedTxRWSets, err = a.deserializeBatchFromBuffer(buf); err != nil {
		return nil, err
	}
	//pop contract events from buffer.
	if block.SerializedContractEvents, err = a.deserializeBatchFromBuffer(buf); err != nil {
		return nil, err
	}
	return block, nil
}

// Plate to mask the original appearance of the data by plating it with something.
func (a *NormalAssembler) Plate(in []byte) ([]byte, error) {
	return a.bCodec.Encode(in)
}

// Deplate to deplate the data in order to restore its original appearance.
func (a *NormalAssembler) Deplate(in []byte) ([]byte, error) {
	return a.bCodec.Decode(in)
}

func (a *NormalAssembler) serializeToBuffer(in []byte, buf *proto.Buffer) (*storePb.StoreInfo, error) {
	bz, err := a.bCodec.Encode(in)
	if err != nil {
		return nil, err
	}
	index := &storePb.StoreInfo{
		Offset:  uint64(len(buf.Bytes())) + getLenLeng(uint64(len(bz))),
		ByteLen: uint64(len(bz)),
	}
	if err := buf.EncodeRawBytes(bz); err != nil {
		return nil, err
	}
	return index, nil
}

func (a *NormalAssembler) deserializeFromBuffer(buf *proto.Buffer) ([]byte, error) {
	bz, err := buf.DecodeRawBytes(false)
	if err != nil {
		return nil, err
	}
	return a.bCodec.Decode(bz)
}

func (a *NormalAssembler) serializeBatchToBuffer(
	bytesList [][]byte, buf *proto.Buffer, withIndex bool) ([]*storePb.StoreInfo, error) {
	if err := buf.EncodeVarint(uint64(len(bytesList))); err != nil {
		return nil, err
	}
	if len(bytesList) == 0 {
		return nil, nil
	}

	if withIndex {
		index := make([]*storePb.StoreInfo, len(bytesList))
		for i, bytes := range bytesList {
			bz, err := a.bCodec.Encode(bytes)
			if err != nil {
				return nil, err
			}
			index[i] = &storePb.StoreInfo{
				Offset:  uint64(len(buf.Bytes())) + getLenLeng(uint64(len(bz))),
				ByteLen: uint64(len(bz)),
			}
			if err := buf.EncodeRawBytes(bz); err != nil {
				return nil, err
			}
		}
		return index, nil
	}
	for _, bytes := range bytesList {
		bz, err := a.bCodec.Encode(bytes)
		if err != nil {
			return nil, err
		}
		if err := buf.EncodeRawBytes(bz); err != nil {
			return nil, err
		}
	}
	return nil, nil
}

func (a *NormalAssembler) deserializeBatchFromBuffer(buf *proto.Buffer) ([][]byte, error) {
	num, err := buf.DecodeVarint()
	if err != nil {
		return nil, err
	}
	if num == 0 {
		return nil, nil
	}

	bytesList := make([][]byte, 0, num)

	for i := uint64(0); i < num; i++ {
		bytes, err := buf.DecodeRawBytes(false)
		if err != nil {
			return nil, err
		}
		bz, err := a.bCodec.Decode(bytes)
		if err != nil {
			return nil, err
		}
		bytesList = append(bytesList, bz)
	}
	return bytesList, nil
}

// getLenLeng is a replica of the protobuf.EncodeVarint function.
// Protobuf writes the length first and then the data，
// so we need to know the length of the data in the proto buffer to locate the data.
func getLenLeng(x uint64) uint64 {
	n := uint64(1)
	for x >= 1<<7 {
		x >>= 7
		n++
	}
	return n
}

type nopBytesCodec struct {
}

// Decode noop
func (n nopBytesCodec) Decode(bz []byte) ([]byte, error) {
	return bz, nil
}

// Encode noop
func (n nopBytesCodec) Encode(bz []byte) ([]byte, error) {
	return bz, nil
}
