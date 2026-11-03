/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

/*
Package consistent provides a consistent hook implementation for the consistent engine.
It includes the SyncHook struct which implements the consistent_service.ConsistentHook interface.
The SyncHook struct provides methods for getting request and response additional information.
*/
package consistent

import (
	"chainmaker.org/chainmaker/consensus-utils/v2/consistent_service"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/gogo/protobuf/proto"
)

// NewSyncHook 实例化一致性引擎ConsistentHook接口
func NewSyncHook(nodeID string, sendEvent func(event types.Event),
	ledgerCache protocol.LedgerCache, storage protocol.BlockchainStore, logger protocol.Logger) *SyncHook {
	return &SyncHook{
		nodeID:      nodeID,
		sendEvent:   sendEvent,
		ledgerCache: ledgerCache,
		storage:     storage,
		logger:      logger,
	}
}

// SyncHook 实现一致性引擎ConsistentHook接口
type SyncHook struct {
	nodeID      string
	sendEvent   func(event types.Event)
	ledgerCache protocol.LedgerCache
	storage     protocol.BlockchainStore
	logger      protocol.Logger
}

// GetRequestAdditional 广播自身的节点信息
func (h *SyncHook) GetRequestAdditional(node consistent_service.Node) []byte {
	return h.getNodeInfoBytes()
}

// GetResponseAdditional 收到心跳后回复信息
func (h *SyncHook) GetResponseAdditional(node consistent_service.Node, msg []byte) []byte {
	return h.getNodeInfoBytes()
}

// getNodeInfoBytes 获取当前节点信息
func (h *SyncHook) getNodeInfoBytes() []byte {
	currentHeight, err := h.ledgerCache.CurrentHeight()
	if err != nil {
		h.logger.Errorf("[consistent] get current height from ledger cache failed,err: %v", err)
		return nil
	}
	archiveHeight := h.storage.GetArchivedPivot()

	bz, err := proto.Marshal(&syncPb.NodeInform{
		Id:            h.nodeID,
		Height:        currentHeight,
		ArchiveHeight: archiveHeight,
	})
	if err != nil {
		h.logger.Errorf("[consistent] pb marshal failed,err: %v", err)
		return nil
	}
	return bz
}

// Update 接收到心跳后
// 1. 更新节点状态
// 2. 同时发送节点更新事件
func (h *SyncHook) Update(node consistent_service.Node, msg []byte) {
	nodeInfo := &syncPb.NodeInform{}
	err := proto.Unmarshal(msg, nodeInfo)
	if err != nil {
		h.logger.Errorf("[consistent] pb unmarshal failed,err: %v", err)
		return
	}
	h.logger.Infof("[consistent] update node info, id: %s, height: %d, archiveHeight: %d",
		nodeInfo.Id, nodeInfo.Height, nodeInfo.ArchiveHeight)
	// 更新节点信息
	syncNode, _ := node.(*SyncNode)
	syncNode.UpdateHeight(nodeInfo.Height, nodeInfo.ArchiveHeight)

	event := &types.NodeEvent{
		Type: types.EventUpdateNode,
		SyncNode: &syncPb.NodeInform{
			Id:            syncNode.Id,
			Height:        syncNode.Height,
			ArchiveHeight: syncNode.ArchiveHeight,
		},
	}
	h.sendEvent(event)
}

// Notify 通知节点上下线
func (h *SyncHook) Notify(state consistent_service.State, node consistent_service.Node) {
	syncNode, _ := node.(*SyncNode)
	switch state {
	case consistent_service.Online:
		// 发送事件通知节点上线
		event := &types.NodeEvent{
			Type: types.EventAddNode,
			SyncNode: &syncPb.NodeInform{
				Id:            syncNode.Id,
				Height:        syncNode.Height,
				ArchiveHeight: syncNode.ArchiveHeight,
			},
		}
		h.sendEvent(event)
	case consistent_service.Offline:
		// 发送事件通知节点下线
		event := &types.NodeEvent{
			Type: types.EventDelNode,
			SyncNode: &syncPb.NodeInform{
				Id:            syncNode.Id,
				Height:        syncNode.Height,
				ArchiveHeight: syncNode.ArchiveHeight,
			},
		}
		h.logger.Infof("[consistent] remove node by consistent offline, id = %s", event.SyncNode.Id)
		h.sendEvent(event)
	}
}
