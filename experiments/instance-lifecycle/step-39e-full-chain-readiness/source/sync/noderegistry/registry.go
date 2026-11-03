/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// Package noderegistry discover and detect nodes and registry them.
package noderegistry

import (
	"context"
	"sync"
	"time"

	"chainmaker.org/chainmaker/consensus-utils/v2/consistent_service"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/consistent"
	"chainmaker.org/chainmaker/sync/v2/internal/controller"
	"chainmaker.org/chainmaker/sync/v2/internal/queue"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/types"
)

const (
	nodeDiscoverTicker = 2 * time.Minute
	// DefaultIdealHeightDistance 默认理想高度差
	DefaultIdealHeightDistance = 1
)

var (
	removeDelay = time.Minute
)

type (
	// Registry discover nodes and maintain node status information.
	Registry struct {
		mu                  sync.RWMutex
		nodeID              string
		idealHeightDistance uint64                         // 理想高度差距
		nodes               *nodeSets                      //map[string]*nodeWithStatus
		watcherList         map[uint32]*types.EventWatcher // 事件列表
		consistentEngine    *consistent_service.StatusConsistentEngine
		ledgerCache         protocol.LedgerCache
		discoverInterval    time.Duration
		discoverer          *nodeDiscoverer
		//wg used to manage sub go routines.
		wg     *controller.GoRoutineGroup
		fireC  chan struct{}
		closeC chan struct{}
		logger protocol.Logger
		dq     *delayQueue
	}
)

// NewRegistry create a node registry.
func NewRegistry(nodeID string,
	idealHeightDistance uint64,
	discoverInterval time.Duration,
	transport net.Transport,
	ledgerCache protocol.LedgerCache,
	storage protocol.BlockchainStore,
	logger protocol.Logger) *Registry {
	// 如果没有配置理想高度差，则使用默认差
	if idealHeightDistance == 0 {
		idealHeightDistance = DefaultIdealHeightDistance
	}
	if discoverInterval <= 0 {
		discoverInterval = nodeDiscoverTicker
	}

	manager := &Registry{
		nodeID:              nodeID,
		idealHeightDistance: idealHeightDistance,
		nodes:               newNodeSets(),
		watcherList:         make(map[uint32]*types.EventWatcher),
		ledgerCache:         ledgerCache,
		discoverInterval:    discoverInterval,
		wg:                  controller.NewGoRoutineGroup(),
		fireC:               make(chan struct{}, 1),
		closeC:              make(chan struct{}),
		logger:              logger,
		dq:                  newDelayQueue(),
	}
	manager.discoverer = newNodeDiscoverer(nodeID, transport, ledgerCache, storage, manager, logger)

	// 实例化一致性引擎
	localNode := consistent.NewSyncNode(nodeID)
	message := consistent.NewSyncMessage(transport, logger)
	hook := consistent.NewSyncHook(nodeID, manager.handleEvent, ledgerCache, storage, logger)
	manager.consistentEngine = consistent_service.NewConsistentService(
		nil, localNode, logger, nil, message, hook, consistent_service.ModeV2)

	return manager
}

// Start 启动节点管理器
// 1. 启动一致性引擎
// 2. 启动心跳监听
// 3. 启动心跳广播器
func (r *Registry) Start() error {
	// 启动一致性引擎
	if err := r.consistentEngine.Start(context.Background()); err != nil {
		r.logger.Errorf("start consistent engine error, %v", err)
		return err
	}
	r.discoverer.discover(triggerFunc(func() <-chan struct{} {
		return r.fireC
	}))
	r.doFire("start")
	r.wg.Run(r.tickFire)
	r.wg.Run(r.clearDeadNodeFromConsistentEngine)
	// 等待两个广播周期，待收集一定数量的节点信息
	time.Sleep(2 * time.Second)
	return nil
}

// Stop 关闭节点管理器
// 1. 停止心跳广播, 并按照顺序关闭关闭channel
// 2. 关闭transport
// 3. 关闭heartBeatChan通道
// 4. 关闭eventChan通道和updateNodeChan通道
func (r *Registry) Stop() error {
	close(r.closeC)
	if err := r.consistentEngine.Stop(context.Background()); err != nil {
		r.logger.Errorf("stop consistent engine error, %v", err)
	}
	r.dq.Close()
	r.wg.Wait()
	close(r.fireC)
	return nil
}

// doFire send a node discovery signal. reason is used to log where fire is triggered.
func (r *Registry) doFire(reason string) {
	r.logger.Debugf("trigger discover once for: %s", reason)
	select {
	case r.fireC <- struct{}{}:
	default:
	}
}

// tickFire 每隔一段时间触发一次节点发现
func (r *Registry) tickFire() {
	ticker := time.NewTicker(r.discoverInterval)
	defer ticker.Stop()
	for {
		select {
		case <-r.closeC:
			return
		case <-ticker.C:
			r.doFire("ticker")
		}
	}
}

// OnNodeDiscovery handle the info of other nodes.
// If the node is already exist, discard the information.
// If the node is itself, discard the information.
// If the node is new, add it to the consistent engine and notify the event.
func (r *Registry) OnNodeDiscovery(node *syncPb.NodeInform) {
	// 如果节点已经存在，丢弃信息
	nodeID := node.GetId()
	// only nodes that do not exist or are not alive will be added.
	if r.nodes.isLiving(nodeID) {
		return
	}
	if nodeID == r.nodeID {
		r.logger.Warnf("node[%v] discover itself, it is incredible", node)
		return
	}
	r.logger.Infof("discover new node: %v", node)
	// 加入一致性引擎
	if err := r.consistentEngine.PutRemoter(nodeID, nil, consistent.NewSyncNode(nodeID)); err != nil {
		// due to delayed deletion, the node has been marked dead
		// but has not yet been deleted from the consistency engine.
		if err != consistent_service.ErrorRemoterExist {
			r.logger.Errorf("add node [%s] to consistent engine failed, nodes, err: %v", node.GetId(), err)
		}
	}

	// 触发新节点事件
	event := &types.NodeEvent{
		Type:     types.EventAddNode,
		SyncNode: node,
	}
	r.handleEvent(event)
}

// clearDeadNodeFromConsistentEngine clear the dead node from consistent engine.
// If no node is alive, trigger a node discovery.
// Delayed deletion is to prevent the addition and deletion operations from being triggered continuously
// due to the time difference between the two parties when the new node is added.
// a sends discovery message to b, b adds a to the consistent engine, then b send discovery response to a and
// b's consistency engine sends heartbeat request to a, a will not respond to b since a's consistent engine
// has not yet added b, so b thinks a is offline and deletes a from its consistent engine.
// a adds b to its consistent engine when it receives the discovery response from b, a will not receive
// heartbeat response from b since b has deleted a from its consistent engine,
// so a thinks b is offline and deletes b from its consistent engine too.
func (r *Registry) clearDeadNodeFromConsistentEngine() {
	for {
		item, ok := r.dq.Take()
		if !ok {
			return
		}
		node, _ := item.(*delayRemoveNode)
		needRm := false
		r.nodes.doFor(node.ID, func(nd *nodeWithStatus) {
			needRm = !nd.isLiving() && nd.liveAt <= node.DeadAt
		})
		if !needRm {
			continue
		}

		r.logger.Infof("clean the dead node [%s] from registry", node.ID)

		if err := r.consistentEngine.RemoveRemoter(node.ID); err != nil {
			r.logger.Warnf("remove node [%s] from consistent engine failed, err: %v", node.ID, err)
		}
		// In order to prevent the resurrection of the race gap node from causing inconsistency between
		// the consistency engine and the nodes, it will be deleted again.
		// Even if it is deleted by mistake, it will be added back.
		if r.nodes.remove(node.ID) {
			r.logger.Infof("remove node [%s] from registry's node list again", node.ID)
		}

		if len(r.nodes.listLivingNodes()) == 0 {
			r.doFire("no living nodes")
		}
	}
}

// Watch 创建事件管理器，并添加到事件列表
func (r *Registry) Watch() types.Watcher {
	eventWatcher := types.NewEventWatcher(r.stopWatch)
	r.mu.Lock()
	defer r.mu.Unlock()
	r.watcherList[eventWatcher.Id()] = eventWatcher
	return eventWatcher
}

// stopWatch 停止指定的Watcher
func (r *Registry) stopWatch(watcherId uint32) {
	r.mu.Lock()
	defer r.mu.Unlock()
	delete(r.watcherList, watcherId)
}

// ListAll get all nodes whether alive or not.
func (r *Registry) ListAll() []types.Node {
	return r.nodes.listNodes()
}

// List get all nodes who is alive.
func (r *Registry) List() []types.Node {
	return r.nodes.listLivingNodes()
}

// CheckIdealHeight 当于其他节点高度差距小于等于1的时候返回true
func (r *Registry) CheckIdealHeight() bool {
	currentHeight, err := r.ledgerCache.CurrentHeight()
	if err != nil {
		r.logger.Errorf("get current height from ledger cache failed: %s", err.Error())
		return false
	}
	reach := true
	r.nodes.forEach(func(nd *nodeWithStatus) bool {
		if nd.isLiving() {
			if currentHeight+r.idealHeightDistance < nd.Height {
				reach = false
				return true
			}
		}
		return false
	})
	return reach
}

// handleEvent 处理事件
// 事件来源1： 自身心跳广播触发的新节点事件
// 事件来源2： 一致性引擎通知的节点上下线
// 处理流程1： 更新节点管理器自身的节点维护信息
// 处理流程2: 发送事件给已注册的事件监听器（provider和receptor）
func (r *Registry) handleEvent(event types.Event) {
	switch event.EventType() {
	case types.EventAddNode:
		r.logger.Infof("add node Event, node: %v", event.EventNode())
		if !r.nodes.add(event.EventNode()) {
			return
		}
	case types.EventUpdateNode:
		if !r.nodes.update(event.EventNode()) {
			return
		}
	case types.EventDelNode:
		r.logger.Infof("remove node Event, node: %v", event.EventNode())
		if !r.nodes.remove(event.EventNode().GetId()) {
			return
		}
		r.dq.Push(&delayRemoveNode{
			ID:     event.EventNode().GetId(),
			DeadAt: nodeTime(),
		})
	}
	r.sendEvent(event)
}

// sendEvent 发送Event事件给订阅者
func (r *Registry) sendEvent(event types.Event) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	for _, eventWatcher := range r.watcherList {
		if err := eventWatcher.SendEvent(event); err != nil {
			r.logger.Errorf("send event to [%s] failed", event.EventNode().GetId())
		}
	}
}

type delayRemoveNode struct {
	ID     string
	DeadAt int64
}

// Delay get delay time
// Delay time is the time when the node is dead
// The node will be removed from the consistent engine after the delay time.
func (d *delayRemoveNode) Delay() time.Duration {
	return removeDelay
}

type delayQueue struct {
	*queue.DelayQueue
	Ctx    context.Context
	Cancel context.CancelFunc
}

func newDelayQueue() *delayQueue {
	ctx, cancel := context.WithCancel(context.Background())
	return &delayQueue{
		DelayQueue: queue.NewDelayQueue(),
		Ctx:        ctx,
		Cancel:     cancel,
	}
}

func (d *delayQueue) Take() (queue.DelayItem, bool) {
	return d.DelayQueue.Take(d.Ctx)
}

func (d *delayQueue) Close() {
	d.Cancel()
}
