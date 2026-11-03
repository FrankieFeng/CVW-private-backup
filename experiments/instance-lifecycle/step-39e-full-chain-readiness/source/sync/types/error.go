/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package types

import (
	"errors"
)

var (
	// ErrInvalidParameter 参数错误
	ErrInvalidParameter = errors.New("invalid parameter")
	// ErrItemNotExist 元素不存在
	ErrItemNotExist = errors.New("item is not exist")
	// ErrItemExist 元素已经存在
	ErrItemExist = errors.New("item is exist")
	// ErrEmptySliceData 需分片的数据为空
	ErrEmptySliceData = errors.New("empty slice data")
	// ErrInvalidNodesTotal 总的节点数不合法
	ErrInvalidNodesTotal = errors.New("invalid nodes total")
	// ErrInvalidSliceNum 总的分片数不合法
	ErrInvalidSliceNum = errors.New("invalid slice numbers")
	// ErrInvalidBlock 区块不合法
	ErrInvalidBlock = errors.New("invalid block")
	// ErrInvalidSliceIndex 当前分片索引不合法
	ErrInvalidSliceIndex = errors.New("invalid slice index")
	// ErrVerifyConfigBlock 验证配置配置块错误
	ErrVerifyConfigBlock = errors.New("config block with no rwsets")
	// ErrSliceDataList 分片数据不合法
	ErrSliceDataList = errors.New("invalid slice data list")
	// ErrChannelClosed 通道已经关闭
	ErrChannelClosed = errors.New("channel already closed")
	// ErrPermIsEmpty 规则为空
	ErrPermIsEmpty = errors.New("perm is empty")
	// ErrSyncStatusStop 同步状态已经停止
	ErrSyncStatusStop = errors.New("sync status is already stopped")
	// ErrSyncStatusStart 同步状态已经启动
	ErrSyncStatusStart = errors.New("sync status is already started")
)
