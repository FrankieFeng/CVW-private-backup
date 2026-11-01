/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package bloom

import (
	"fmt"
	"os"
	"testing"
	"time"

	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"github.com/test-go/testify/require"
)

var (
	txCount = 100
	wsCount = 2
)

func genTestBlock(h uint64) *storePb.BlockWithRWSet {
	return &storePb.BlockWithRWSet{
		Block:    &commonPb.Block{Header: &commonPb.BlockHeader{BlockHeight: h}},
		TxRWSets: genTestRWSets(h),
	}
}

func genTestRWSets(h uint64) []*commonPb.TxRWSet {
	sets := make([]*commonPb.TxRWSet, 0)
	for i := 0; i < txCount; i++ {
		set := &commonPb.TxRWSet{
			TxWrites: []*commonPb.TxWrite{},
		}
		for j := 0; j < wsCount; j++ {
			set.TxWrites = append(set.TxWrites, &commonPb.TxWrite{Key: []byte(fmt.Sprintf("test_%d_%d_%d", h, i, j))})
		}
		sets = append(sets, set)
	}

	return sets
}

func TestBlockBloom(t *testing.T) {
	filter, err := NewBlockBloomFilter(1000000, 0.01,
		WithDumpCycle(0), WithDumpAsync())
	if err != nil {
		t.Error(err)
		t.Fail()
	}
	defer func() {
		os.Remove("./bloom.dump")
	}()
	for i := 0; i < 10; i++ {
		filter.AddBlock(genTestBlock(uint64(i + 1)))
	}
	t.Log(filter.Dump())
	time.Sleep(time.Second * 2)
	filter.filter.Close()
	filter2, err := NewBlockBloomFilter(1000000, 0.01,
		WithDumpCycle(2), WithDumpAsync())
	if err != nil {
		t.Error(err)
		t.Fail()
	}
	for i := 0; i < 10; i++ {
		for j := 0; j < txCount; j++ {
			for k := 0; k < wsCount; k++ {
				key := []byte(fmt.Sprintf("test_%d_%d_%d", i+1, j, k))
				require.True(t, filter2.has(key))
			}
		}
	}
}

type mockBlockLoader struct {
	height uint64
}

func (m *mockBlockLoader) Height() uint64 {
	return m.height
}

func (m *mockBlockLoader) GetBlockWithRWSets(height uint64) (*storePb.BlockWithRWSet, error) {
	return genTestBlock(height), nil
}

func newMockBlockLoader(h uint64) BlockLoader {
	return &mockBlockLoader{
		height: h,
	}
}

func TestBloomRestore(t *testing.T) {
	h := uint64(1000)
	filter, err := NewBlockBloomFilter(1000000, 0.01, WithDumpCycle(0),
		WithBlockLoader(newMockBlockLoader(h)))
	defer func() {
		os.Remove("./bloom.dump")
	}()
	require.NoError(t, err)
	require.Equal(t, h, filter.height)
}
