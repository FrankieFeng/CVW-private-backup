/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package types

import syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"

// 事件类型
// EventAddNode 添加节点
// EventUpdateNode 删除节点
// EventDelNode 更新节点
const (
	EventAddNode = iota + 1
	EventUpdateNode
	EventDelNode
)

// EventType 事件类型
type EventType int

// NodeEvent 节点事件
// Type 事件类型
// SyncNode 节点信息
type NodeEvent struct {
	Type     EventType
	SyncNode *syncPb.NodeInform
}

// EventType 事件类型
func (e *NodeEvent) EventType() EventType {
	return e.Type
}

// EventNode 事件节点
func (e *NodeEvent) EventNode() *syncPb.NodeInform {
	return e.SyncNode
}
