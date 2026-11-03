/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package provider

import (
	"sync"

	"chainmaker.org/chainmaker/pb-go/v2/common"

	"chainmaker.org/chainmaker/common/v2/msgbus"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/conn"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/rule/manager"
	"chainmaker.org/chainmaker/sync/v2/types"
)

// NewProvideServer 创建一个数据提供者服务实例
func NewProvideServer(nodeId string, transport net.Transport,
	informer types.NodeInformer, ledgerCache protocol.LedgerCache, storage protocol.BlockchainStore,
	msgBus msgbus.MessageBus, chainConfig protocol.ChainConf, logger protocol.Logger) *ProvideServer {

	// 实例化规则管理器
	rulesManager := manager.NewRuleManager(nodeId, storage, logger)

	listenHandler := newListenHandler(rulesManager)

	// 实例化数据提供者监听器
	listener := conn.NewMsgBusListener(transport, listenHandler.HandleListen, logger)

	// 实例化HandlerNotifier
	notifier := NewHandlerNotifier(ledgerCache, logger)

	// 注册msgBus，用于本地落块消息监听和一致性引擎消息监听
	// 1. 先通知ruleManager
	// 2. 再通知handler
	notifyFuncList := []func(block *common.Block){
		rulesManager.NotifyNewBlock,
		notifier.Notify,
	}

	subscriber := types.NewMessageBusSubscriber(notifyFuncList, logger)
	msgBus.Register(msgbus.BlockInfo, subscriber)

	// 创建Provider
	return &ProvideServer{
		listener:        listener,
		serverLinker:    newServerLinker(),
		ruleManager:     rulesManager,
		eventWatcher:    informer.Watch(),
		HandlerNotifier: notifier,
		msgBus:          msgBus,
		subscriber:      subscriber,
		chainConfig:     chainConfig,
		storage:         storage,
		ledgerCache:     ledgerCache,
		logger:          logger,
	}

}

// ProvideServer 数据提供者服务
// 保持和各个数据接受者的连接
// 并将数据通过连接，发送给目标接收者
type ProvideServer struct {
	serverLinker    *serverLinker        // 连接器
	ruleManager     *manager.RuleManager // 规则管理器
	listener        *conn.Listener       // 连接监听器
	eventWatcher    types.Watcher        // 事件监听器
	HandlerNotifier *HandlerNotifier     // 新落块通知器
	msgBus          msgbus.MessageBus
	subscriber      msgbus.Subscriber
	chainConfig     protocol.ChainConf
	storage         protocol.BlockchainStore
	ledgerCache     protocol.LedgerCache
	logger          protocol.Logger
}

// Start 启动数据提供者服务
// 1. 启动连接监听blockHandler
// 2. 启动事件监听
func (p *ProvideServer) Start() error {
	p.logger.Infof("[Provider Service] start")

	// 启动规则管理器
	if err := p.ruleManager.Start(); err != nil {
		p.logger.Errorf("[Provider Service] start rule manager failed,err: %v", err)
		return err
	}

	// 监听连接
	if err := p.listen(); err != nil {
		p.logger.Errorf("[Provider Service] provider listen error,err: %v", err)
		return err
	}

	// 异步监听事件
	go p.watchEvent()

	return nil
}

// Stop 停止数据提供者服务
func (p *ProvideServer) Stop() error {
	// 关闭Listener
	if err := p.listener.Close(); err != nil {
		p.logger.Errorf("[Provider Service] close listener failed, err: %v", err)
		return err
	}
	// 关闭连接器
	if err := p.serverLinker.close(); err != nil {
		p.logger.Errorf("[Provider Service] close provider conns failed, err: %v", err)
		return err
	}
	// 关闭规则管理器
	if err := p.ruleManager.Stop(); err != nil {
		p.logger.Errorf("[Provider Service] stop rule manager failed, err: %v", err)
		return err
	}

	// 解除注册
	p.msgBus.UnRegister(msgbus.BlockInfo, p.subscriber)
	return nil
}

// watchEvent 监听Event事件
func (p *ProvideServer) watchEvent() {
	for event := range p.eventWatcher.ResultChan() {
		switch event.EventType() {
		// 监听删除事件，移除本地连接
		case types.EventDelNode:
			if conn := p.serverLinker.removeConnByID(event.EventNode().GetId()); conn != nil {
				_ = conn.Close()
			}
		}
	}
}

// listen 监听连接，并添加到连接池
func (p *ProvideServer) listen() error {
	// 启动监听
	if err := p.listener.Listen(); err != nil {
		return err
	}
	go func() {
		for {
			// 接收connection
			sc, err := p.listener.Accept()
			if err != nil {
				p.logger.Infof("[Provider Service] listener closed with : %v", err)
				return
			}
			// 启动服务
			go p.serve(sc)
		}
	}()
	return nil
}

// serve 启动服务
func (p *ProvideServer) serve(sc *conn.ServerConn) {
	defer p.serverLinker.removeConn(sc)
	// 添加新连接
	if old := p.serverLinker.addConnOrReplace(sc); old != nil {
		_ = old.Close()
		p.logger.Infof("close old conn[%s]", old.NodeID())
	}

	// 实例化数据提供者区块发送器
	blockSender := newBlockSender(sc.NodeID(), p.HandlerNotifier, p.storage,
		p.ruleManager, p.ledgerCache, p.chainConfig, p.logger)

	// 异步启动服务
	if err := sc.Serve(blockSender); err != nil {
		if err == errors.ErrConnClosed { // 连接已关闭
			p.logger.Infof("server conn[%s] serve over", sc.NodeID())
			_ = sc.Close()
			return
		}
		p.logger.Warnf("server conn[%s] serve failed, err : %v", sc.NodeID(), err)
		if err = sc.Close(); err != nil {
			p.logger.Errorf("[Provider Service] close sc failed, err : %v", err)
		}
	}
}

// newServerLinker 实例化Provider连接管理器
func newServerLinker() *serverLinker {
	return &serverLinker{
		mu:          sync.RWMutex{},
		serverConns: make(map[string]types.Connection),
	}
}

// serverLinker 数据提供者连接管理器
type serverLinker struct {
	mu          sync.RWMutex
	serverConns map[string]types.Connection // 连接列表
}

// addConn 添加连接
func (p *serverLinker) addConnOrReplace(sc types.Connection) types.Connection {
	p.mu.Lock()
	defer p.mu.Unlock()
	old := p.serverConns[sc.NodeID()]
	p.serverConns[sc.NodeID()] = sc
	return old
}

func (p *serverLinker) removeConn(sc types.Connection) types.Connection {
	p.mu.Lock()
	defer p.mu.Unlock()
	id := sc.NodeID()
	if conn, exist := p.serverConns[id]; exist {
		if conn == sc {
			delete(p.serverConns, id)
			return conn
		}
	}
	return nil
}

func (p *serverLinker) removeConnByID(nodeID string) types.Connection {
	p.mu.Lock()
	defer p.mu.Unlock()
	if sc, ok := p.serverConns[nodeID]; ok {
		// 从连接列表中删除
		delete(p.serverConns, nodeID)
		return sc
	}
	return nil
}

// close 关闭链接管理器
func (p *serverLinker) close() error {
	p.mu.Lock()
	defer p.mu.Unlock()

	// 如果连接列表为空，直接返回
	if len(p.serverConns) == 0 {
		return nil
	}

	for nodeId, sc := range p.serverConns {
		if err := sc.Close(); err != nil && err != errors.ErrConnClosed {
			return err
		}
		// 从连接列表中删除
		delete(p.serverConns, nodeId)
	}
	return nil
}
