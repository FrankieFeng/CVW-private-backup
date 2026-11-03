/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package test

import (
	"fmt"
	"sync"

	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2/mock"
	"github.com/golang/mock/gomock"
)

type mockBlockChainStore struct {
	*mock.MockBlockchainStore
	mu        sync.Mutex
	blocks    map[uint64]*storePb.BlockWithRWSet
	lastBlock *commonPb.Block
	objects   map[string][]byte
}

// WriteObject mock
func (b *mockBlockChainStore) WriteObject(contractName string, key []byte, value []byte) error {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.objects[string(key)] = value
	return nil
}

func newMockBlockChainStore(ctrl *gomock.Controller) *mockBlockChainStore {
	mockStore := mock.NewMockBlockchainStore(ctrl)
	store := &mockBlockChainStore{
		MockBlockchainStore: mockStore,
		blocks:              make(map[uint64]*storePb.BlockWithRWSet),
		objects:             make(map[string][]byte),
	}

	mockStore.EXPECT().PutBlock(gomock.Any(), gomock.Any()).DoAndReturn(
		func(blk *commonPb.Block, txRWSets []*commonPb.TxRWSet) error {
			store.blocks[blk.Header.BlockHeight] = &storePb.BlockWithRWSet{
				Block:    blk,
				TxRWSets: txRWSets,
			}
			store.lastBlock = blk
			return nil
		}).AnyTimes()
	mockStore.EXPECT().GetBlock(gomock.Any()).DoAndReturn(func(height uint64) (*commonPb.Block, error) {
		if blk, exist := store.blocks[height]; exist {
			return blk.Block, nil
		}
		return nil, fmt.Errorf("block not find")
	}).AnyTimes()
	mockStore.EXPECT().GetBlockWithRWSets(gomock.Any()).DoAndReturn(func(height uint64) (*storePb.BlockWithRWSet, error) {
		if blk, exist := store.blocks[height]; exist {
			return blk, nil
		}
		return nil, fmt.Errorf("block not find")
	}).AnyTimes()
	mockStore.EXPECT().GetLastBlock().DoAndReturn(func() (*commonPb.Block, error) {
		if store.lastBlock != nil {
			return store.lastBlock, nil
		}
		return nil, fmt.Errorf("block not find")
	}).AnyTimes()
	mockStore.EXPECT().GetArchivedPivot().AnyTimes()
	mockStore.EXPECT().ReadObject(gomock.Any(), gomock.Any()).DoAndReturn(
		func(contractName string, key []byte) ([]byte, error) {
			store.mu.Lock()
			defer store.mu.Unlock()
			data := store.objects[string(key)]
			if data == nil {
				return nil, nil
			}
			return data, nil
			//return proto.Marshal(data.(*syncPb.NodeRule))
		}).AnyTimes()
	return store
}
