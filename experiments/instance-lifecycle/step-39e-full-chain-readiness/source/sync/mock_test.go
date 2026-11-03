/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package sync

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"math/rand"
	"time"

	"chainmaker.org/chainmaker/pb-go/v2/common"

	"chainmaker.org/chainmaker/common/v2/msgbus"
	"chainmaker.org/chainmaker/localconf/v2"
	acPb "chainmaker.org/chainmaker/pb-go/v2/accesscontrol"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/sync/v2/internal/test"
	rulemgr "chainmaker.org/chainmaker/sync/v2/rule/manager"
	"github.com/gogo/protobuf/proto"
	"github.com/golang/mock/gomock"
)

type mockCluster struct {
	ns      *test.WorkNS
	local   *mockNode
	remotes map[string]*mockNode
}

func (c *mockCluster) LocalNode() *mockNode {
	return c.local
}

func (c *mockCluster) RemoteNode(nodeId string) *mockNode {
	return c.remotes[nodeId]
}

func (c *mockCluster) Run() {
	for _, server := range c.remotes {
		server.Run()
		fmt.Printf("start remote node [%s]\n", server.NodeID())
	}
	c.local.Run()
	fmt.Printf("start local node [%s]\n", c.local.NodeID())
}

func (c *mockCluster) Release() {
	for _, node := range c.remotes {
		node.Stop()
	}
	c.local.Stop()
	c.ns.Release()
}

type nodeInfo struct {
	ID     string
	Height uint64
	Rules  []*syncPb.NodeRule
	Config localconf.SyncConfig
}

func initCluster(ctrl *gomock.Controller, local nodeInfo, remotes ...nodeInfo) *mockCluster {
	ns := test.NewWorkNS(ctrl)
	localNode := newMockNode(local, ns.NewMockFullNode(local.ID))
	rs := make(map[string]*mockNode, len(remotes))
	for _, rp := range remotes {
		node := newMockNode(rp, ns.NewMockFullNode(rp.ID))
		rs[rp.ID] = node
	}
	cluster := &mockCluster{
		ns:      ns,
		local:   localNode,
		remotes: rs,
	}
	return cluster
}

type mockNode struct {
	*test.MockFullNode
	nodeInfo nodeInfo
	height   uint64
	server   *BlockSyncService
}

func (s *mockNode) AddNewBlock() {
	s.height++
	s.addBlock(s.height)
}

func (s *mockNode) addBlock(h uint64) {
	block, rwSets := mockNewCommonBlock(h)
	_ = s.Store.PutBlock(block, rwSets)
	s.Ledger.SetLastCommittedBlock(block)
	s.MessageBus().Publish(msgbus.BlockInfo, &common.BlockInfo{
		Block: block,
	})
}

func (s *mockNode) Server() *BlockSyncService {
	return s.server
}

func (s *mockNode) Run() {
	if len(s.nodeInfo.Rules) > 0 {
		for _, rule := range s.nodeInfo.Rules {
			bz, _ := proto.Marshal(rule)
			key := string(rulemgr.GetRuleKey(rule.NodeId))
			_ = s.Store.WriteObject("", []byte(key), bz)
		}
	}
	s.addBlock(0)

	server, err := NewSyncServer(s.nodeInfo.ID, &s.nodeInfo.Config,
		s.ChainCfg, s.Store, s.Ledger, s.Logger, s.MessageBus(), s.Verifier, s.Committer)
	if err != nil {
		panic(err)
	}
	s.server = server
	err = s.server.Start()
	if err != nil {
		panic(err)
	}
}

func (s *mockNode) Stop() {
	if s.server != nil {
		s.server.Stop()
	}
}

func newMockNode(info nodeInfo, node *test.MockFullNode) *mockNode {
	return &mockNode{
		nodeInfo:     info,
		MockFullNode: node,
	}
}

func mockNewCommonBlock(height uint64) (*commonPb.Block, []*commonPb.TxRWSet) {
	return createBlockAndRWSets("chain1", height, 1)
}

func createBlock(chainId string, height uint64, txNum int) *commonPb.Block {
	block := &commonPb.Block{
		Header: &commonPb.BlockHeader{
			ChainId:      chainId,
			BlockHeight:  height,
			BlockVersion: 3000000,
			Proposer: &acPb.Member{
				OrgId:      "org1",
				MemberInfo: []byte("User1"),
			},
		},
		Txs: []*commonPb.Transaction{},
	}
	for i := 0; i < txNum; i++ {
		tx := &commonPb.Transaction{
			Payload: &commonPb.Payload{
				ChainId: chainId,
				TxType:  commonPb.TxType_INVOKE_CONTRACT,
				TxId:    generateTxId(chainId, height, i),
			},
			Sender: &commonPb.EndorsementEntry{
				Signer: &acPb.Member{
					OrgId:      "org1",
					MemberInfo: []byte("User1"),
				},
				Signature: []byte("signature1"),
			},
			Result: &commonPb.Result{
				Code: commonPb.TxStatusCode_SUCCESS,
				ContractResult: &commonPb.ContractResult{
					Result: []byte("ok"),
				},
			},
		}
		block.Txs = append(block.Txs, tx)
	}
	block.Header.BlockHash = generateBlockHash(chainId, height)
	block.Txs[0].Payload.TxId = generateTxId(chainId, height, 0)
	block.Dag = &commonPb.DAG{
		Vertexes: []*commonPb.DAG_Neighbor{{
			Neighbors: []uint32{0, 1, 2},
		}},
	}

	return block
}

func createBlockAndRWSets(chainId string, height uint64, txNum int) (*commonPb.Block, []*commonPb.TxRWSet) {
	block := createBlock(chainId, height, txNum)
	var txRWSets []*commonPb.TxRWSet

	for i := 0; i < txNum; i++ {
		key := fmt.Sprintf("key_%d", i)
		value := RandomString(10 << 20)
		txRWset := &commonPb.TxRWSet{
			TxId: block.Txs[i].Payload.TxId,
			TxWrites: []*commonPb.TxWrite{
				{
					Key:          []byte(key),
					Value:        []byte(value),
					ContractName: "testContract",
				},
			},
		}
		txRWSets = append(txRWSets, txRWset)
	}

	return block, txRWSets
}

func generateBlockHash(chainId string, height uint64) []byte {
	blockHash := sha256.Sum256([]byte(fmt.Sprintf("%s-%d", chainId, height)))
	return blockHash[:]
}

func generateTxId(chainId string, height uint64, index int) string {
	txIdBytes := sha256.Sum256([]byte(fmt.Sprintf("%s-%d-%d", chainId, height, index)))
	return hex.EncodeToString(txIdBytes[:])
}

const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

// 初始化随机种子（仅需一次）
func init() {
	rand.Seed(time.Now().UnixNano())
}

// 生成随机字符串
func RandomString(length int) string {
	b := make([]byte, length)
	for i := range b {
		// #nosec G404
		b[i] = charset[rand.Intn(len(charset))]
	}
	return string(b)
}
