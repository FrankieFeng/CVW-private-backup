/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package types

import (
	"sync/atomic"
)

// DefaultChanCap 默认channel的缓存长度
const DefaultChanCap = 3

// increaseId 生成监听器使用的增长ID
var increaseId uint32

// NewEventWatcher 实例化一个EventWatcher
func NewEventWatcher(stopWatch func(id uint32)) *EventWatcher {
	return &EventWatcher{
		eventChan: make(chan Event, DefaultChanCap),
		stopWatch: stopWatch,
		id:        genWatcherId(),
	}
}

// EventWatcher 事件监听器，监听节点管理器对节点增删改的事件
// id 事件监听器的唯一标志
// stopWatch创建方关闭监听回调函数
type EventWatcher struct {
	id        uint32
	eventChan chan Event
	stopWatch func(id uint32)
}

// Id 获取事件ID
func (w *EventWatcher) Id() uint32 {
	return w.id
}

// Stop 关闭事件监听器
// 1. 通知使用方停止使用此监听器
// 2. 关闭事件通道
func (w *EventWatcher) Stop() {
	w.stopWatch(w.id)
	close(w.eventChan)
}

// ResultChan 获取事件结果监听channel
func (w *EventWatcher) ResultChan() <-chan Event {
	return w.eventChan
}

// SendEvent 发送节点事件
// 通过EventWatcher向channel里发送事件，接收器和分发器 接收到事件后作出相应的处理
// eventType 节点事件类型：添加节点、更新节点、删除节点
func (w *EventWatcher) SendEvent(event Event) error {
	w.eventChan <- event
	return nil
}

// genWatcherId 生成一个watcherId
func genWatcherId() uint32 {
	return atomic.AddUint32(&increaseId, 1)
}
