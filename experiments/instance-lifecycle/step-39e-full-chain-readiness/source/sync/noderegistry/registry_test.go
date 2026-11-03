/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package noderegistry

import (
	"sync"
	"testing"
	"time"

	"chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/sync/v2/internal/test"
	"chainmaker.org/chainmaker/sync/v2/net"
	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func createRegistry(node *test.MockFullNode) *Registry {
	return NewRegistry(node.NodeID(), 1, time.Second, net.NewBlockSyncTransport(node.MessageBus()),
		node.Ledger, node.Store, node.Logger)
}

func Test_Registry(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ns := test.NewWorkNS(ctrl)
	defer ns.Release()
	localNode := ns.NewMockFullNode("local")
	remoteNode := ns.NewMockFullNode("remote")

	localNodeRegistry := createRegistry(localNode)
	remoteNodeRegistry := createRegistry(remoteNode)

	localBlockCount, remoteBlockCount := 40, 20

	wg := sync.WaitGroup{}
	wg.Add(2)

	go func() {
		err := localNodeRegistry.Start()
		require.Nil(t, err)
	}()
	go func() {
		err := remoteNodeRegistry.Start()
		require.Nil(t, err)
	}()
	go func() {
		defer wg.Done()
		i := uint64(1)
		ticker := time.NewTicker(100 * time.Millisecond)
		defer ticker.Stop()
		for {
			<-ticker.C
			block := &common.Block{
				Header: &common.BlockHeader{
					BlockHeight: i,
				},
			}
			_ = localNode.Store.PutBlock(block, nil)
			localNode.Ledger.SetLastCommittedBlock(block)
			if i == uint64(localBlockCount) {
				return
			}
			i++
		}
	}()

	go func() {
		defer wg.Done()
		i := uint64(1)
		ticker := time.NewTicker(200 * time.Millisecond)
		defer ticker.Stop()
		for {
			<-ticker.C
			block := &common.Block{
				Header: &common.BlockHeader{
					BlockHeight: i,
				},
			}
			_ = remoteNode.Store.PutBlock(block, nil)
			remoteNode.Ledger.SetLastCommittedBlock(block)

			if i == uint64(remoteBlockCount) {
				return
			}
			i++
		}
	}()

	wg.Wait()
	err := localNodeRegistry.Stop()
	require.Nil(t, err)
	err = remoteNodeRegistry.Stop()
	require.Nil(t, err)
}

func Test_ClearDeadNode(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ns := test.NewWorkNS(ctrl)
	defer ns.Release()
	localNode := ns.NewMockFullNode("local")
	remoteNode := ns.NewMockFullNode("remote")

	localNodeRegistry := createRegistry(localNode)
	remoteNodeRegistry := createRegistry(remoteNode)

	localBlockCount, remoteBlockCount := 40, 10

	removeDelay = time.Second

	wg := sync.WaitGroup{}
	wg.Add(2)

	go func() {
		defer wg.Done()
		err := localNodeRegistry.Start()
		require.Nil(t, err)

		i := uint64(1)
		ticker := time.NewTicker(100 * time.Millisecond)
		defer ticker.Stop()
		for {
			<-ticker.C
			block := &common.Block{
				Header: &common.BlockHeader{
					BlockHeight: i,
				},
			}
			_ = localNode.Store.PutBlock(block, nil)
			localNode.Ledger.SetLastCommittedBlock(block)
			if i == uint64(localBlockCount) {
				break
			}
			i++
		}
	}()
	go func() {
		defer wg.Done()
		err := remoteNodeRegistry.Start()
		require.Nil(t, err)

		i := uint64(1)
		ticker := time.NewTicker(200 * time.Millisecond)
		defer ticker.Stop()
		for {
			<-ticker.C
			block := &common.Block{
				Header: &common.BlockHeader{
					BlockHeight: i,
				},
			}
			_ = remoteNode.Store.PutBlock(block, nil)
			remoteNode.Ledger.SetLastCommittedBlock(block)

			if i == uint64(remoteBlockCount) {
				break
			}
			i++
		}

		err = remoteNodeRegistry.Stop()
		require.Nil(t, err)
		t.Logf("remote node exit")
	}()

	wg.Wait()
	t.Logf("all goroutines exit")
	time.Sleep(10 * removeDelay)
	err := localNodeRegistry.Stop()
	require.Nil(t, err)
}
