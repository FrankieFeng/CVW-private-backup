/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package serialization

import (
	"fmt"
	"reflect"
	"sync"

	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/store/v2/serialization/protobuf"
)

var _ BlockNormalizer = (*NormalBlockNormalizer)(nil)

// NormalBlockNormalizer This is a general block normalizer.
// It uses the external serializer to serialize and deserialize the organization data,
// so that different serialization methods can be met in the future.
type NormalBlockNormalizer struct {
	sinkCodec Serializer
}

// NewNormalProtobufBlockNormalizer new normalizer with protobuf as serializer.
func NewNormalProtobufBlockNormalizer() *NormalBlockNormalizer {
	return NewNormalBlockNormalizer(protobuf.NewSerializer())
}

// NewNormalBlockNormalizer constructs a NormalBlockNormalizer object using an externally provided serializer.
func NewNormalBlockNormalizer(sinkCodec Serializer) *NormalBlockNormalizer {
	return &NormalBlockNormalizer{
		sinkCodec: sinkCodec,
	}
}

// NormalizeBlock organizes blocks into a standard format for storage definition.
// 1. Split and organize block data.
// 2. Serialize the split data.
func (n *NormalBlockNormalizer) NormalizeBlock(blockWithRWSet *storePb.BlockWithRWSet) (
	*BlockNormalized, error) {
	var (
		err            error
		normalizedInfo = n.organizeBlock(blockWithRWSet)
	)

	if normalizedInfo.SerializedMeta, err =
		n.serialize(normalizedInfo.Meta); err != nil {
		return nil, fmt.Errorf("serialize meta error: %s", err)
	}
	if normalizedInfo.SerializedTxs, err =
		n.serializeBatch(toInterfaceSlice(normalizedInfo.Txs)); err != nil {
		return nil, fmt.Errorf("serialize txs error: %s", err)
	}
	if normalizedInfo.SerializedTxRWSets, err =
		n.serializeBatch(toInterfaceSlice(normalizedInfo.TxRWSets)); err != nil {
		return nil, fmt.Errorf("serialize txRWSets error: %s", err)
	}
	if normalizedInfo.SerializedContractEvents, err =
		n.serializeBatch(toInterfaceSlice(normalizedInfo.ContractEvents)); err != nil {
		return nil, fmt.Errorf("serialize contract events error: %s", err)
	}
	return normalizedInfo, nil
}

// NormalizeFromSerialization restore normalized data from serialized data
func (n *NormalBlockNormalizer) NormalizeFromSerialization(normal *SerializationNormalized) (*BlockNormalized, error) {
	meta := &storePb.SerializedBlock{}
	if err := n.deserialize(normal.SerializedMeta, meta); err != nil {
		return nil, fmt.Errorf("deserialize meta error: %s", err)
	}

	var txs []*commonPb.Transaction
	if err := n.deserializeBatch(normal.SerializedTxs, &txs); err != nil {
		return nil, fmt.Errorf("deserialize txs error: %s", err)
	}
	var txRWSets []*commonPb.TxRWSet
	if err := n.deserializeBatch(normal.SerializedTxRWSets, &txRWSets); err != nil {
		return nil, fmt.Errorf("deserialize txRWSets error: %s", err)
	}
	var ets []*commonPb.ContractEvent
	if err := n.deserializeBatch(normal.SerializedContractEvents, &ets); err != nil {
		return nil, fmt.Errorf("deserialize contract events error: %s", err)
	}
	return &BlockNormalized{
		Block: &commonPb.Block{
			Header:         meta.Header,
			Dag:            meta.Dag,
			Txs:            txs,
			AdditionalData: meta.AdditionalData,
		},
		Txs:                     txs,
		Meta:                    meta,
		TxRWSets:                txRWSets,
		ContractEvents:          ets,
		SerializationNormalized: *normal,
	}, nil
}

// Serializer get the serializer used by BlockNormalizer,
// so that users can deserialize the character data in BlockNormalized
func (n *NormalBlockNormalizer) Serializer() Serializer {
	return n.sinkCodec
}

func (n *NormalBlockNormalizer) organizeBlock(blockWithRWSet *storePb.BlockWithRWSet) *BlockNormalized {
	block := blockWithRWSet.Block
	txRWSets := blockWithRWSet.TxRWSets
	events := blockWithRWSet.ContractEvents
	info := &BlockNormalized{}
	info.Block = block
	meta := &storePb.SerializedBlock{
		Header:         block.Header,
		Dag:            block.Dag,
		TxIds:          make([]string, 0, len(block.Txs)),
		AdditionalData: block.AdditionalData,
	}

	for _, tx := range block.Txs {
		meta.TxIds = append(meta.TxIds, tx.Payload.TxId)
		info.Txs = append(info.Txs, tx)
	}

	info.TxRWSets = append(info.TxRWSets, txRWSets...)
	info.Meta = meta
	info.ContractEvents = events
	return info
}

func (s *NormalBlockNormalizer) serialize(obj interface{}) ([]byte, error) {
	return s.sinkCodec.Encode(obj)
}

func (s *NormalBlockNormalizer) deserialize(bz []byte, obj interface{}) error {
	return s.sinkCodec.Decode(bz, obj)
}

// serializeBatch serialize batch objects to bytes in parallel.
func (s *NormalBlockNormalizer) serializeBatch(
	objs []interface{}) ([][]byte, error) {
	if len(objs) == 0 {
		return nil, nil
	}

	serializedByteList := make([][]byte, len(objs))
	batchSize := 1000
	taskNum := len(objs)/batchSize + 1
	errsChan := make(chan error, taskNum)
	wg := sync.WaitGroup{}
	wg.Add(taskNum)
	for taskId := 0; taskId < taskNum; taskId++ {
		startIndex := taskId * batchSize
		endIndex := (taskId + 1) * batchSize
		if endIndex > len(objs) {
			endIndex = len(objs)
		}
		go func(start int, end int) {
			defer wg.Done()
			for offset, obj := range objs[start:end] {
				bytes, err := s.sinkCodec.Encode(obj)
				if err != nil {
					errsChan <- err
				}
				serializedByteList[start+offset] = bytes
			}
		}(startIndex, endIndex)
	}
	wg.Wait()
	if len(errsChan) > 0 {
		return nil, <-errsChan
	}

	return serializedByteList, nil
}

func (s *NormalBlockNormalizer) deserializeBatch(bytesList [][]byte, to interface{}) error {
	num := len(bytesList)
	if num == 0 {
		return nil
	}

	//*[]*object{} or *[]object
	toVP := reflect.ValueOf(to)
	if toVP.Kind() != reflectKindPointer {
		return fmt.Errorf("to must be a pointer, but: %s", toVP.Kind())
	}
	toTS := toVP.Type().Elem()
	if toTS.Kind() != reflect.Slice {
		return fmt.Errorf("to element must be a slice, but: %s", toTS.Kind())
	}
	toVSET := toTS.Elem()
	toS := reflect.MakeSlice(toTS, int(num), int(num))

	isPoint := false
	toElem := toVSET
	if toElem.Kind() == reflectKindPointer {
		isPoint = true
		toElem = toElem.Elem()
	}

	for i, bytes := range bytesList {
		elem := reflect.New(toElem)
		if err := s.sinkCodec.Decode(bytes, elem.Interface()); err != nil {
			return err
		}
		if isPoint {
			toS.Index(int(i)).Set(elem)
		} else {
			toS.Index(int(i)).Set(elem.Elem())
		}

	}
	toVP.Elem().Set(toS)

	return nil
}

// toInterfaceSlice convert slice to []interface{}
func toInterfaceSlice(in interface{}) []interface{} {
	value := reflect.ValueOf(in)
	if value.Kind() != reflect.Slice {
		return nil
	}
	count := value.Len()
	result := make([]interface{}, 0, count)
	for i := 0; i < count; i++ {
		result = append(result, value.Index(i).Interface())
	}
	return result
}

// ToBlockWithRWSet build a BlockWithRWSet from BlockNormalized.
func (n *BlockNormalized) ToBlockWithRWSet() *storePb.BlockWithRWSet {
	return &storePb.BlockWithRWSet{
		Block:          n.Block,
		TxRWSets:       n.TxRWSets,
		ContractEvents: n.ContractEvents,
	}
}
