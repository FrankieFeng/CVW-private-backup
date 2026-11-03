/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package manager

import (
	"fmt"
	"testing"
	"time"

	"github.com/gogo/protobuf/proto"

	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"

	"chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/protocol/v2/mock"
	"github.com/golang/mock/gomock"

	ruleL "chainmaker.org/chainmaker/common/v2/syncrule"
	"github.com/test-go/testify/require"
)

var (
	testLastBlock  *common.Block
	testBlockStore = make(map[uint64]*common.Block)
	nodeRules      = make(map[string]*syncPb.NodeRule)
)

func TestRuleManager(t *testing.T) {
	t.Log("====== Start test rule manager ======")
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	nodeId := "node1"
	storage := newMockStorage(ctrl)
	logger := newMockLogger(ctrl)

	initData()

	defaultR := defaultRule()

	// 初始化rule manager
	rm := NewRuleManager(nodeId, storage, logger)
	require.Nil(t, rm.Start())
	require.Equal(t, defaultR, rm.ownRule)

	newRule := customRule(2, `O == "org2"`)
	nodeRules[string(GetRuleKey("node1"))] = newRule
	nodeRules[string(GetRuleKey("node2"))] = node2Rule()
	rm.NotifyNewBlock(getConfigBlock())
	time.Sleep(time.Second)
	require.Equal(t, newRule.Rules[1].Content, rm.OwnRulePerm(11))

	rule := rm.GetNodeRule("node2", 0)
	require.NotNil(t, rule)
	require.Equal(t, node2Rule().Rules[0], rule)
	fmt.Println("rule", rule)

	ts, err := rm.GetRulePermTs("node2", rule)
	require.Nil(t, err)
	ts2, err := ruleL.ParseRule(`O == "org1"`)
	require.Nil(t, err)
	require.Equal(t, ts2, ts)

	rm.ownRule = newRule
	require.Equal(t, uint64(201), rm.GetNextRuleFromHeight("node2", 80))
	require.Equal(t, uint64(0), rm.GetCurrentRuleFromHeight("node2", 80))
}

func initData() {
	block := getRuleBlock(10)
	testLastBlock = block
	testBlockStore[10] = block

	ruleKey := string(GetRuleKey("node1"))
	nodeRules[ruleKey] = defaultRule()
}

func getRuleBlock(height uint64) *common.Block {
	return &common.Block{
		Header: &common.BlockHeader{
			BlockVersion: 0,
			BlockType:    0,
			BlockHeight:  height,
		},
	}
}

func getConfigBlock() *common.Block {
	return &common.Block{
		Header: &common.BlockHeader{
			BlockHeight: 11,
		},
		Txs: []*common.Transaction{
			{
				Payload: &common.Payload{
					Method:       ruleMethod,
					ContractName: syncContract,
					Parameters: []*common.KeyValuePair{
						{
							Key:   ParamNodeID,
							Value: []byte("node1"),
						},
						{
							Key:   ParamNodeID,
							Value: []byte("node2"),
						},
					},
				},
			},
		},
	}
}

func newMockStorage(ctrl *gomock.Controller) protocol.BlockchainStore {
	storage := mock.NewMockBlockchainStore(ctrl)
	storage.EXPECT().GetArchivedPivot().DoAndReturn(func() uint64 {
		return 5
	}).AnyTimes()
	storage.EXPECT().GetLastBlock().DoAndReturn(func() (*common.Block, error) {
		return testLastBlock, nil
	}).AnyTimes()
	storage.EXPECT().ReadObject(gomock.Any(), gomock.Any()).DoAndReturn(func(contractName string, key []byte) ([]byte, error) {
		r := nodeRules[string(key)]
		fmt.Println("******", string(key), " ", r)
		return proto.Marshal(r)
	}).AnyTimes()

	return storage
}

func defaultRule() *syncPb.NodeRule {
	return &syncPb.NodeRule{
		NodeId:       "node1",
		LatestRuleId: 1,
		Rules: []*syncPb.Rule{
			{
				Id:          1,
				BeginHeight: 0,
				EndHeight:   0,
				Content:     `O == "org1"`,
			},
		},
	}
}

func node2Rule() *syncPb.NodeRule {
	return &syncPb.NodeRule{
		NodeId:       "node2",
		LatestRuleId: 1,
		Rules: []*syncPb.Rule{
			{
				Id:          1,
				BeginHeight: 0,
				EndHeight:   100,
				Content:     `O == "org1"`,
			},
			{
				Id:          2,
				BeginHeight: 101,
				EndHeight:   200,
				Content:     `O == "org2"`,
			},
			{
				Id:          3,
				BeginHeight: 201,
				EndHeight:   300,
				Content:     `O == "org3"`,
			},
		},
	}
}

func customRule(id uint32, perm string) *syncPb.NodeRule {
	return &syncPb.NodeRule{
		NodeId:       "node1",
		LatestRuleId: id,
		Rules: []*syncPb.Rule{
			{
				Id:          1,
				BeginHeight: 0,
				EndHeight:   10,
				Content:     `O == "org1"`,
			},
			{
				Id:          id,
				BeginHeight: 11,
				EndHeight:   20,
				Content:     perm,
			},
		},
	}
}

func newMockLogger(ctrl *gomock.Controller) protocol.Logger {
	mockLogger := mock.NewMockLogger(ctrl)
	mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		fmt.Println(fmt.Sprintf(format, args))
	}).AnyTimes()
	mockLogger.EXPECT().Infof(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		fmt.Println(fmt.Sprintf(format, args))
	}).AnyTimes()
	mockLogger.EXPECT().Debugf(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		//fmt.Println(fmt.Sprintf(format, args))
	}).AnyTimes()
	mockLogger.EXPECT().Warnf(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		fmt.Println(fmt.Sprintf(format, args))
	}).AnyTimes()
	return mockLogger
}
