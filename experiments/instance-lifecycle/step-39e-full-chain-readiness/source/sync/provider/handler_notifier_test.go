/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package provider

import (
	"fmt"
	"sync"
	"testing"

	"chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2/test"

	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func TestHandlerNotifier(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	initData()
	notifier = NewHandlerNotifier(newMockLedgerCache(ctrl, sender1), &test.GoLogger{})
	emptyHandlers := make(map[string]*BlockSender)
	require.Equal(t, emptyHandlers, notifier.handlers)

	wg := sync.WaitGroup{}
	wg2 := sync.WaitGroup{}
	wg.Add(3)
	wg2.Add(3)
	// 模拟协程1，等待块11
	go func() {
		h1 := newMockHandler(ctrl, "node1").(*BlockSender)
		notifier.Register(h1)
		wg.Done()
		height := h1.notifier.WaitingForNewBlock(h1, 11)
		require.Equal(t, uint64(11), height)
		wg2.Done()
		notifier.mu.RLock()
		fmt.Println(" n.Handlers()", notifier.handlers)
		notifier.mu.RUnlock()
	}()

	// 模拟协程2，等待块11
	go func() {
		h2 := newMockHandler(ctrl, "node2").(*BlockSender)
		notifier.Register(h2)
		wg.Done()
		height := h2.notifier.WaitingForNewBlock(h2, 11)
		require.Equal(t, uint64(11), height)
		wg2.Done()
		notifier.mu.RLock()
		fmt.Println(" n.Handlers()", notifier.handlers)
		notifier.mu.RUnlock()
	}()

	// 模拟协程3，等待块11
	go func() {
		h3 := newMockHandler(ctrl, "node3").(*BlockSender)
		notifier.Register(h3)
		wg.Done()
		height := h3.notifier.WaitingForNewBlock(h3, 11)
		require.Equal(t, uint64(11), height)
		wg2.Done()
		notifier.mu.RLock()
		fmt.Println(" n.Handlers()", notifier.handlers)
		notifier.mu.RUnlock()
	}()

	// 通知等待的协程，块11已经落块
	wg.Wait()
	notifier.Notify(&common.Block{Header: &common.BlockHeader{BlockHeight: 11}})
	wg2.Wait()
	notifier.mu.RLock()
	require.Equal(t, emptyHandlers, notifier.handlers)
	notifier.mu.RUnlock()

}

type Student struct {
	Age int
}

func TestRemove(t *testing.T) {
	count := 1
	skip := 1
	rwSetList := make([]*Student, 0, count)
	for i := 0; i < count; i++ {
		rwSetList = append(rwSetList, &Student{Age: i})
	}
	for i := 0; i < count; i++ {
		if i%skip == 0 {
			rwSetList[i] = nil
		}
	}
	fillIdx := -1
	for i, rwSet := range rwSetList {
		if rwSet == nil {
			if fillIdx < 0 {
				fillIdx = i
			}
			continue
		}
		if fillIdx >= 0 {
			rwSetList[fillIdx] = rwSet
			// fillIdx = i
			fillIdx++
		}
	}
	if fillIdx >= 0 {
		t.Log("AAAAAA")
		rwSetList = rwSetList[:fillIdx]
	}
	for _, rwSet := range rwSetList {
		t.Logf("rwSetList: %+v", rwSet)
	}

}
