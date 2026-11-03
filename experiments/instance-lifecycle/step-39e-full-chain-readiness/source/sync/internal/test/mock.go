/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package test

import (
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/pb-go/v2/config"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/protocol/v2/mock"
	"github.com/golang/mock/gomock"
)

func newMockVerifier(ctrl *gomock.Controller) protocol.BlockVerifier {
	mockVerify := mock.NewMockBlockVerifier(ctrl)
	mockVerify.EXPECT().VerifyBlock(gomock.Any(), gomock.Any()).AnyTimes()
	mockVerify.EXPECT().VerifyBlockSync(gomock.Any(), gomock.Any()).Return(nil, nil).AnyTimes()
	mockVerify.EXPECT().VerifyBlockWithRwSets(gomock.Any(), gomock.Any(), gomock.Any()).Return(nil).AnyTimes()
	return mockVerify
}

func newMockCommitter(ctrl *gomock.Controller, mockLedger protocol.LedgerCache) protocol.BlockCommitter {
	mockCommit := mock.NewMockBlockCommitter(ctrl)
	mockCommit.EXPECT().AddBlock(gomock.Any()).DoAndReturn(func(blk *commonPb.Block) error {
		mockLedger.SetLastCommittedBlock(blk)
		return nil
	}).AnyTimes()
	return mockCommit
}

func newMockChainConfig(ctrl *gomock.Controller) protocol.ChainConf {
	cfg := mock.NewMockChainConf(ctrl)
	cfg.EXPECT().ChainConfig().DoAndReturn(func() *config.ChainConfig {
		return &config.ChainConfig{
			Version: "v2.3.2",
		}
	}).AnyTimes()
	return cfg
}

type mockLedgerCache struct {
	*mock.MockLedgerCache
	lastCommitBlk *commonPb.Block
}

func newMockLedgerCache(ctrl *gomock.Controller) protocol.LedgerCache {
	mockLedger := mock.NewMockLedgerCache(ctrl)
	leger := &mockLedgerCache{
		MockLedgerCache: mockLedger,
		lastCommitBlk: &commonPb.Block{
			Header: &commonPb.BlockHeader{
				BlockHeight: 0,
			},
		},
	}
	mockLedger.EXPECT().GetLastCommittedBlock().DoAndReturn(func() *commonPb.Block {
		return leger.lastCommitBlk
	}).AnyTimes()
	mockLedger.EXPECT().CurrentHeight().DoAndReturn(func() (uint64, error) {
		return leger.lastCommitBlk.Header.BlockHeight, nil
	}).AnyTimes()
	mockLedger.EXPECT().SetLastCommittedBlock(gomock.Any()).DoAndReturn(func(blk *commonPb.Block) {
		leger.lastCommitBlk = blk
	}).AnyTimes()
	return leger
}
