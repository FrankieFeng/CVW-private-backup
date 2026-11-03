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
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/internal/test"
	"chainmaker.org/chainmaker/sync/v2/net"
	"github.com/golang/mock/gomock"
)

type mockNodeDiscoveryListener struct {
	logger protocol.Logger
}

func (l *mockNodeDiscoveryListener) OnNodeDiscovery(node *syncPb.NodeInform) {
	l.logger.Infof("receive node[%s], height;[%d], archiveHeight:[%d]\n", node.Id, node.Height, node.ArchiveHeight)
}

func createDiscoverer(node *test.MockFullNode) *nodeDiscoverer {
	return newNodeDiscoverer(node.NodeID(), net.NewBlockSyncTransport(node.MessageBus()),
		node.Ledger, node.Store, &mockNodeDiscoveryListener{
			logger: node.Logger,
		}, node.Logger)
}

func Test_nodeDiscoverer_Discover(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ns := test.NewWorkNS(ctrl)
	defer ns.Release()
	localNode := ns.NewMockFullNode("local")
	remoteNode := ns.NewMockFullNode("remote")

	localNodeDiscoverer := createDiscoverer(localNode)
	remoteNodeDiscoverer := createDiscoverer(remoteNode)

	localBlockCount, remoteBlockCount := 40, 20
	wg := sync.WaitGroup{}
	wg.Add(2)
	localNodeDiscoverer.discover(triggerFunc(func() <-chan struct{} {
		c := make(chan struct{}, 1)
		go func() {
			defer wg.Done()
			i := uint64(1)
			ticker := time.NewTicker(100 * time.Millisecond)
			defer func() {
				ticker.Stop()
				close(c)
			}()
			for {
				<-ticker.C
				block := &common.Block{
					Header: &common.BlockHeader{
						BlockHeight: i,
					},
				}
				_ = localNode.Store.PutBlock(block, nil)
				localNode.Ledger.SetLastCommittedBlock(block)

				select {
				case c <- struct{}{}:
				default:
				}
				if i == uint64(localBlockCount) {
					c <- struct{}{}
					return
				}
				i++
			}
		}()
		return c
	}))

	remoteNodeDiscoverer.discover(triggerFunc(func() <-chan struct{} {
		c := make(chan struct{}, 1)
		go func() {
			defer wg.Done()
			i := uint64(1)
			ticker := time.NewTicker(200 * time.Millisecond)
			defer func() {
				ticker.Stop()
				close(c)
			}()
			for {
				<-ticker.C
				block := &common.Block{
					Header: &common.BlockHeader{
						BlockHeight: i,
					},
				}
				_ = remoteNode.Store.PutBlock(block, nil)
				remoteNode.Ledger.SetLastCommittedBlock(block)

				select {
				case c <- struct{}{}:
				default:
				}
				if i == uint64(remoteBlockCount) {
					c <- struct{}{}
					return
				}
				i++
			}
		}()
		return c
	}))
	wg.Wait()
	time.Sleep(time.Second)
}
