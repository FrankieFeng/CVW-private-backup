/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import (
	"testing"
	"time"

	"chainmaker.org/chainmaker/common/v2/msgbus"
	"chainmaker.org/chainmaker/localconf/v2"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func createBlockReceptor(ctrl *gomock.Controller, mbs msgbus.MessageBus, nodes ...nodeInfo) *receptor {
	transport := net.NewBlockSyncTransport(mbs)
	ledger := newMockLedgerCache(ctrl, &commonPb.Block{
		Header: &commonPb.BlockHeader{
			BlockHeight: 0,
		},
	})
	var nodeInforms []syncPb.NodeInform
	for _, node := range nodes {
		node := syncPb.NodeInform{
			Id:     node.ID,
			Height: node.Height,
		}
		nodeInforms = append(nodeInforms, node)
	}

	return NewBlockReceptor(&Config{
		Informer:    newMockInformer(nodeInforms...),
		Transport:   transport,
		LedgerCache: ledger,
		ExposeConf: &localconf.SyncConfig{
			BlockPoolSize: 8,
		},
		Logger:         cLogger,
		FragmentMerger: types.NewBlockSlicer(cLogger),
	}).(*receptor)
}

func Test_receptor_WatchBlock(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	var (
		nodeInfos = []nodeInfo{
			{
				ID:             "remoteNode1",
				Height:         5,
				ruleMeetHeight: 2,
			},
			{
				ID:     "remoteNode2",
				Height: 150,
			},
			{
				ID:     "remoteNode3",
				Height: 200,
			},
		}
	)

	cluster := initCluster2(ctrl, "localNode", nodeInfos...)
	defer cluster.Close()
	receptor := createBlockReceptor(ctrl, cluster.LocalNode().MessageBus(), nodeInfos...)
	err := receptor.Start()
	require.NoError(t, err)
	sgNode := receptor.streamList.Front()
	require.Equal(t, len(nodeInfos), sgNode.sg.len())
	time.Sleep(2 * time.Second)

	num := 15
	for {
		block, ok := receptor.WatchBlock()
		if !ok {
			break
		}
		t.Logf("block: %+v", block)
		num--
		if num == 0 {
			break
		}
	}
	// panic("AAAAAAAAAAA")
	sgNode = receptor.streamList.Front()
	require.Equal(t, 2, sgNode.sg.len())
	err = receptor.Stop()
	require.NoError(t, err)

}

func Test_receptor_Pause_Resume(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	var (
		nodeInfos = []nodeInfo{
			{
				ID:     "remoteNode1",
				Height: 20,
			},
			{
				ID:     "remoteNode2",
				Height: 20,
			},
			{
				ID:     "remoteNode3",
				Height: 20,
			},
		}
	)

	cluster := initCluster2(ctrl, "localNode", nodeInfos...)
	defer cluster.Close()
	receptor := createBlockReceptor(ctrl, cluster.LocalNode().MessageBus(), nodeInfos...)
	err := receptor.Start()
	require.NoError(t, err)
	time.Sleep(1 * time.Second)
	err = receptor.Pause()
	require.Nil(t, err)
	time.Sleep(2 * time.Second)
	err = receptor.Resume()
	require.Nil(t, err)

	sgNode := receptor.streamList.Front()
	require.Equal(t, 3, sgNode.sg.len())
	time.Sleep(time.Second)
	num := 3
	for {
		block, ok := receptor.WatchBlock()
		if !ok {
			break
		}
		t.Logf("block: %+v", block)
		receptor.ledgerCache.SetLastCommittedBlock(block.GetBlockWithRWSet().Block)
		num--
		if num == 0 {
			break
		}
	}
	err = receptor.Pause()
	require.NoError(t, err)
	err = receptor.Resume()
	require.NoError(t, err)

	time.Sleep(time.Second)
	num = 17
	for {
		block, ok := receptor.WatchBlock()
		if !ok {
			break
		}
		t.Logf("block: %+v", block)
		receptor.ledgerCache.SetLastCommittedBlock(block.GetBlockWithRWSet().Block)
		num--
		if num == 0 {
			break
		}
	}
	informer := receptor.informer.(*nodeInformer).NodeInformer.(*mockNodeInformer)
	informer.triggerOnce()
	informer.triggerOnce()
	informer.triggerOnce()
	time.Sleep(time.Second)

}

func Test_receptor_PullBlock(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	var (
		nodeInfos = []nodeInfo{
			{
				ID:     "remoteNode1",
				Height: 5,
			},
			{
				ID:     "remoteNode2",
				Height: 15,
			},
			{
				ID:     "remoteNode3",
				Height: 20,
			},
		}
	)

	cluster := initCluster2(ctrl, "localNode", nodeInfos...)
	defer cluster.Close()
	receptor := createBlockReceptor(ctrl, cluster.LocalNode().MessageBus(), nodeInfos...)
	err := receptor.Start()
	require.NoError(t, err)
	defer func() {
		err = receptor.Stop()
		require.Nil(t, err)
	}()
	block, err := receptor.PullBlock(1, false)
	require.Nil(t, err)
	t.Log("block", block)
}
