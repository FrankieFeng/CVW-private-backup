/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package provider

import (
	"sync"

	"chainmaker.org/chainmaker/protocol/v2"

	"chainmaker.org/chainmaker/pb-go/v2/common"
)

// NewHandlerNotifier handler通知器
func NewHandlerNotifier(ledgerCache protocol.LedgerCache, logger protocol.Logger) *HandlerNotifier {
	return &HandlerNotifier{
		handlers:   make(map[string]*BlockSender),
		lastHeight: ledgerCache.GetLastCommittedBlock().Header.BlockHeight,
		logger:     logger,
	}
}

// HandlerNotifier 通知器
// handlers 为待通知的handler列表
type HandlerNotifier struct {
	mu         sync.RWMutex
	lastHeight uint64 // 当前最新块高
	handlers   map[string]*BlockSender
	logger     protocol.Logger
}

// Handlers 待通知列表
// func (h *HandlerNotifier) Handlers() map[string]*BlockSender {
// 	h.mu.RLock()
// 	defer h.mu.RUnlock()
// 	return h.handlers
// }

// Register 注册到待通知列表
func (h *HandlerNotifier) Register(handler *BlockSender) {
	h.mu.Lock()
	defer h.mu.Unlock()
	h.handlers[handler.Remoter()] = handler
}

// UnRegister 从待通知列表中移除
func (h *HandlerNotifier) UnRegister(handler *BlockSender) {
	h.mu.Lock()
	defer h.mu.Unlock()
	delete(h.handlers, handler.Remoter())
}

// Notify 通知新区块产生
func (h *HandlerNotifier) Notify(block *common.Block) {
	h.logger.Infof("[notifier] notify new block, height [%d]", block.Header.BlockHeight)
	h.mu.RLock()
	defer h.mu.RUnlock()

	// 更新本地最新块高
	h.lastHeight = block.Header.BlockHeight

	if len(h.handlers) == 0 {
		return
	}

	// 通知所有已注册的handler
	for _, handler := range h.handlers {
		select {
		case handler.NewBlockChan() <- block.Header.BlockHeight:
		default:

		}
	}
}

// WaitingForNewBlock 等待新区块
// handler 为每一个区块处理器
// height uint64 表示自身需要落块的快高
func (h *HandlerNotifier) WaitingForNewBlock(handler *BlockSender, height uint64) uint64 {
	// 将handler注册到通知器
	h.Register(handler)

	for newHeight := range handler.newBlockChan {
		// select {
		// case newHeight, ok := <-handler.newBlockChan:
		// if !ok {
		// 	return 0
		// }
		if newHeight >= height {
			// 满足通知条件，从通知器中移除handler
			h.UnRegister(handler)
			return height
		}
		// }
	}
	return 0
}
