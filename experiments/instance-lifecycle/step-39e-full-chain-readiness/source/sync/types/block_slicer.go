/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

// Package types provides data types and structures for the Chainmaker protocol.
package types

import (
	"chainmaker.org/chainmaker/protocol/v2"

	"chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/pb-go/v2/store"
	"github.com/gogo/protobuf/proto"
)

// NewBlockSlicer 实例化一个分片切割器
func NewBlockSlicer(logger protocol.Logger) Slicer {
	return &blockSlicer{logger: logger}
}

// blockSlicer 分片切割器
type blockSlicer struct {
	logger protocol.Logger
	// dataBytes []byte
}

// SliceBlockFragment 分片策略，按照节点数和当前节点索引，切割数据
// nodesTotal 为总的节点数
// index 当前节点的索引，从0开始
// 最后一个分片取到结尾，保证数据完整
func (s *blockSlicer) SliceBlockFragment(sliceNum, sliceIndex int,
	blockWithRWSet *store.BlockWithRWSet) ([]byte, error) {

	// 总分片数不能小于1
	if sliceNum < 1 {
		return nil, ErrInvalidSliceNum
	}
	//  index不能超过 分片数-1
	if sliceIndex+1 > sliceNum || sliceIndex < 0 {
		s.logger.Warnf("sliceIndex: %d, sliceNum: %d", sliceIndex, sliceNum)
		return nil, ErrInvalidSliceIndex
	}
	if blockWithRWSet == nil {
		return nil, ErrInvalidBlock
	}
	s.logger.Infof("slice block height [%d], num [%d], index [%d]",
		blockWithRWSet.Block.Header.BlockHeight, sliceNum, sliceIndex)

	// 如果分片数为1，则表示不分片
	if sliceNum == 1 {
		return proto.Marshal(blockWithRWSet)
	}
	// 当前分片为最后一个分片,返回additionalData
	if sliceIndex+1 == sliceNum {
		// s.logger.Infof("slice block additional data [%v]", blockWithRWSet.Block.AdditionalData)
		if blockWithRWSet.Block.AdditionalData == nil {
			return nil, nil
		}
		return proto.Marshal(blockWithRWSet.Block.AdditionalData)
	}
	blockWithRWSet.Block.AdditionalData = nil
	dataBytes, err := proto.Marshal(blockWithRWSet)
	if err != nil {
		return nil, err
	}

	// 如果2个节点，则不需要切割
	if sliceNum == 2 {
		return dataBytes, nil
	}
	avgLen := len(dataBytes) / (sliceNum - 1)
	start := sliceIndex * avgLen
	if sliceIndex == sliceNum-2 {
		return dataBytes[start:], nil
	}
	return dataBytes[start : start+avgLen], nil
}

// MergeBlockFragment 将数据分片合并成带读写集的Block
// dataList 数据切片需要按照分片顺序
func (s *blockSlicer) MergeBlockFragment(dataList [][]byte) (*store.BlockWithRWSet, error) {
	var (
		buffer *Buffer
	)
	if len(dataList) > 1 {
		bufLen := 0
		for i := 0; i < len(dataList)-1; i++ {
			bufLen += len(dataList[i])
		}
		buffer = NewBuffer(bufLen)
	}

	return s.MergeBlockFragmentWithBuffer(buffer, dataList)
}

// MergeBlockFragmentWithBuffer the buffer are reused during merging to
// reduce the cost of frequent memory allocations
func (s *blockSlicer) MergeBlockFragmentWithBuffer(buffer *Buffer, dataList [][]byte) (*store.BlockWithRWSet, error) {
	if len(dataList) == 0 {
		return nil, ErrSliceDataList
	}
	// 只有一个分片，则直接反解 blockWithRWSet
	blockWithRWSet := &store.BlockWithRWSet{}
	if len(dataList) == 1 {
		if err := proto.Unmarshal(dataList[0], blockWithRWSet); err != nil {
			return nil, err
		}
		return blockWithRWSet, nil
	}
	// 多个分片，组装实际被分片的数据
	for i := 0; i < len(dataList)-1; i++ {
		buffer.Append(dataList[i])
	}

	// 反解 blockWithRWSet
	if err := proto.Unmarshal(buffer.Bytes(), blockWithRWSet); err != nil {
		return nil, err
	}

	// 最后一个分片，为additionalData
	additionalBytes := dataList[len(dataList)-1]
	if len(additionalBytes) == 0 {
		blockWithRWSet.Block.AdditionalData = nil
	} else {
		// 反解 additionalData
		additionalData := &common.AdditionalData{}
		if err := proto.Unmarshal(additionalBytes, additionalData); err != nil {
			return nil, err
		}
		// 拼装 additionalData
		blockWithRWSet.Block.AdditionalData = additionalData
	}

	return blockWithRWSet, nil
}
