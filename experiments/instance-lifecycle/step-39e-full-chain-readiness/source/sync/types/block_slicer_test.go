/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package types

import (
	"fmt"
	"testing"

	"github.com/golang/mock/gomock"

	"github.com/test-go/testify/require"

	"chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/protocol/v2/mock"
)

func TestBlockSlicer(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	s := NewBlockSlicer(newMockLogger(ctrl)).(*blockSlicer)
	block := mockBlockWithRWSet()

	// 测试参数异常
	_, err := s.SliceBlockFragment(0, 0, block)
	require.EqualError(t, ErrInvalidSliceNum, err.Error())

	_, err = s.SliceBlockFragment(1, -1, block)
	require.EqualError(t, ErrInvalidSliceIndex, err.Error())

	_, err = s.SliceBlockFragment(1, 1, block)
	require.EqualError(t, ErrInvalidSliceIndex, err.Error())

	_, err = s.SliceBlockFragment(2, 1, nil)
	require.EqualError(t, ErrInvalidBlock, err.Error())

	// 测试只分1片
	s0, err := s.SliceBlockFragment(1, 0, block)
	require.Nil(t, err)
	block0, err := s.MergeBlockFragment([][]byte{s0})
	require.Nil(t, err)
	require.Equal(t, block, block0)

	// 测试分多片
	var slist [][]byte
	s1, err := s.SliceBlockFragment(3, 0, block)
	require.Nil(t, err)
	slist = append(slist, s1)

	block = mockBlockWithRWSet()
	s2, err := s.SliceBlockFragment(3, 1, block)
	require.Nil(t, err)
	slist = append(slist, s2)

	block = mockBlockWithRWSet()
	s3, err := s.SliceBlockFragment(3, 2, block)
	require.Nil(t, err)
	slist = append(slist, s3)

	blockNew, err := s.MergeBlockFragment(slist)
	require.Nil(t, err)

	fmt.Println(blockNew)
	require.Equal(t, block, blockNew)
}

func mockBlockWithRWSet() *store.BlockWithRWSet {
	return &store.BlockWithRWSet{
		Block: &common.Block{
			Header: &common.BlockHeader{
				BlockHeight: 100,
			},
			AdditionalData: &common.AdditionalData{
				ExtraData: map[string][]byte{
					"key": []byte("haha"),
				},
			},
		},
		TxRWSets:       nil,
		ContractEvents: nil,
	}

}

func newMockLogger(ctrl *gomock.Controller) protocol.Logger {
	mockLogger := mock.NewMockLogger(ctrl)
	mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		fmt.Println(fmt.Sprintf(format, args...))
	}).AnyTimes()
	mockLogger.EXPECT().Infof(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		fmt.Println(fmt.Sprintf(format, args...))
	}).AnyTimes()
	mockLogger.EXPECT().Debugf(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		//fmt.Println(fmt.Sprintf(format, args))
	}).AnyTimes()
	mockLogger.EXPECT().Warnf(gomock.Any(), gomock.Any()).Do(func(format string, args ...interface{}) {
		fmt.Println(fmt.Sprintf(format, args...))
	}).AnyTimes()
	return mockLogger
}
