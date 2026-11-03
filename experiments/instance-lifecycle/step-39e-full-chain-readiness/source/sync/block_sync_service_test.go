/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package sync

import (
	"fmt"
	"testing"
	"time"

	"chainmaker.org/chainmaker/localconf/v2"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func TestNewSyncServer(t *testing.T) {
	var (
		localInfo = nodeInfo{
			ID:     "localNode",
			Height: 5,
			Config: localconf.SyncConfig{
				BlockPoolSize:                8,
				WaitPeriodSecondsAfterLatest: 1,
			},
		}
		nodeRules = []*syncPb.NodeRule{
			{
				NodeId:       "remoteNode1",
				LatestRuleId: 3,
				Rules: []*syncPb.Rule{
					{
						Id:          3,
						BeginHeight: 5,
						Content:     `O=="org1"`,
					},
				},
			},
			{
				NodeId:       "remoteNode2",
				LatestRuleId: 3,
				Rules: []*syncPb.Rule{
					{
						Id:          3,
						BeginHeight: 10,
						Content:     `O=="org1"`,
					},
				},
			},
			{
				NodeId:       "remoteNode3",
				LatestRuleId: 3,
				Rules: []*syncPb.Rule{
					{
						Id:          3,
						BeginHeight: 15,
						Content:     `O=="org2"`,
					},
				},
			},
		}
		nodeInfos = []nodeInfo{
			{
				ID:     "remoteNode1",
				Height: 5,
				Rules:  nodeRules,
				Config: localconf.SyncConfig{
					BlockPoolSize: 8,
				},
			},
			{
				ID:     "remoteNode2",
				Height: 15,
				Rules:  nodeRules,
				Config: localconf.SyncConfig{
					BlockPoolSize: 8,
				},
			},
			{
				ID:     "remoteNode3",
				Height: 20,
				Rules:  nodeRules,
				Config: localconf.SyncConfig{
					BlockPoolSize: 8,
				},
			},
		}
	)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	cluster := initCluster(ctrl, localInfo, nodeInfos...)
	defer func() {
		go cluster.Release() //四节点模拟关闭时间略长会导致测试超时
	}()
	cluster.Run()
	for _, info := range nodeInfos {
		go func(info nodeInfo) {
			node := cluster.RemoteNode(info.ID)
			count := info.Height
			ticker := time.NewTicker(10 * time.Millisecond)
			defer ticker.Stop()
			for {
				<-ticker.C
				node.AddNewBlock()
				fmt.Printf("add a new block to [%s], height [%d]\n", node.nodeInfo.ID, node.height)
				count--
				if count <= 0 {
					return
				}
			}
		}(info)
	}

	time.Sleep(10 * time.Second)
	state, err := cluster.LocalNode().Server().GetState(true)
	require.NoError(t, err)
	t.Logf("state@@@@: %v", state)
	cluster.LocalNode().Server().Stop()
}

func TestBlockSyncService_IdealHeight(t *testing.T) {
	var (
		localInfo = nodeInfo{
			ID:     "localNode",
			Height: 0,
			Config: localconf.SyncConfig{
				BlockPoolSize:                8,
				WaitPeriodSecondsAfterLatest: 1,
			},
		}
		nodeRules = []*syncPb.NodeRule{}
		nodeInfos = []nodeInfo{
			{
				ID:     "remoteNode1",
				Height: 50,
				Rules:  nodeRules,
				Config: localconf.SyncConfig{
					BlockPoolSize: 8,
				},
			},
			{
				ID:     "remoteNode2",
				Height: 10,
				Rules:  nodeRules,
				Config: localconf.SyncConfig{
					BlockPoolSize: 8,
				},
			},
			{
				ID:     "remoteNode3",
				Height: 200,
				Rules:  nodeRules,
				Config: localconf.SyncConfig{
					BlockPoolSize: 8,
				},
			},
		}
	)
	closeC := make(chan struct{})
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	cluster := initCluster(ctrl, localInfo, nodeInfos...)
	defer func() {
		go cluster.Release()
	}()
	go func() {
		for _, info := range nodeInfos {
			go func(info nodeInfo) {
				node := cluster.RemoteNode(info.ID)
				count := 10
				ticker := time.NewTicker(1 * time.Millisecond)
				defer ticker.Stop()
				for {
					select {
					case <-ticker.C:
						node.AddNewBlock()
						fmt.Printf("add a new block to [%s], height [%d]\n", node.nodeInfo.ID, node.height)
						count--
						if count <= 0 {
							time.Sleep(2 * time.Second)
							count = 10
						}
					case <-closeC:
						return
					}
				}
			}(info)
		}
	}()
	cluster.Run()
	<-cluster.LocalNode().Server().ListenSyncToIdealHeight()
	fmt.Printf("receive a new ideal height [%d]\n", cluster.LocalNode().Server().height)
	<-cluster.LocalNode().Server().ListenSyncToIdealHeight()
	fmt.Printf("receive a new ideal height [%d]\n", cluster.LocalNode().Server().height)
	cluster.LocalNode().Server().StopBlockSync()
	time.Sleep(3 * time.Second)
	cluster.LocalNode().Server().StartBlockSync()
	<-cluster.LocalNode().Server().ListenSyncToIdealHeight()
	fmt.Printf("receive a new ideal height [%d] for resume\n", cluster.LocalNode().Server().height)
	close(closeC)
}
