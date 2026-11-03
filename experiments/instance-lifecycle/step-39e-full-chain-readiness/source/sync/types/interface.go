/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package types

import (
	"chainmaker.org/chainmaker/pb-go/v2/store"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
)

// Event 事件接口
type Event interface {
	// EventType the type of event
	EventType() EventType
	// EventNode the node of event
	EventNode() *syncPb.NodeInform
}

// Watcher 监听器，用于处理节点事件
type Watcher interface {
	// Stop 停止监听
	Stop()
	// ResultChan 事件通道
	ResultChan() <-chan Event
}

// Connection 被clientConn和ServerConn实现
type Connection interface {
	// NodeID 连接对端的节点ID
	NodeID() string
	// Close 关闭连接
	Close() error
}

// NodeInformer 节点信息告知器
type NodeInformer interface {
	// Watch 返回一个新的监听器
	Watch() Watcher
	// List 返回维护的节点信息列表
	List() []Node
}

// Node 节点信息接口
type Node interface {
	//Info 返回节点高度信息
	Info() *syncPb.NodeInform
	//LastDetectedAliveTime 返回最近一次检测到存活的时间点
	LastDetectedAliveTime() int64
}

// BlockReveal revealing Block Data and behavior
type BlockReveal interface {
	// GetBlockWithRWSet returns the block with RWSet
	GetBlockWithRWSet() *store.BlockWithRWSet
	// ReportVerifyResult report verification results of the block
	ReportVerifyResult(success bool)
}

// Receptor 接收器
type Receptor interface {
	// WatchBlock 持续监听新块
	WatchBlock() (BlockReveal, bool)
	// PullBlock 拉取指定高度的区块
	PullBlock(height uint64, withRWSet bool) (BlockReveal, error)
	// Pause 暂停区块同步
	Pause() error
	// Resume 恢复区块同步
	Resume() error
	// Start 启动接收器
	Start() error
	// Stop 关闭接收器
	Stop() error

	// HeightHasBeenSynced returns the height that the receptor has synced to.
	HeightHasBeenSynced() uint64

	// BlocksInQueue returns the number of blocks in the queue waiting to be processed.
	BlocksInQueue() int

	// ShowConfig returns the config of the receptor in json format.
	ShowConfigJSON() string
}

// Provider 数据提供者
type Provider interface {
	// Start 启动数据提供服务
	Start() error
	// Stop 关闭服务
	Stop() error
}

// Slicer 分片切割器
type Slicer interface {
	Merger
	// SliceBlockFragment 将区块切割分片
	SliceBlockFragment(sliceNum, index int, blockWithRWSet *store.BlockWithRWSet) ([]byte, error)
}

// Merger 区块合并器
type Merger interface {
	// MergeBlockFragment 将收集的分片合并重组成区块
	MergeBlockFragment(dataList [][]byte) (*store.BlockWithRWSet, error)
	// MergeBlockFragmentWithBuffer merges a block fragment with a buffer
	// used to temporarily store merged data.
	MergeBlockFragmentWithBuffer(buf *Buffer, fragments [][]byte) (*store.BlockWithRWSet, error)
}
