/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package types

import (
	"chainmaker.org/chainmaker/common/v2/msgbus"
	"chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
)

// NewMessageBusSubscriber new subscriber
// 接收本地新块落块消息，并通知给Provider
func NewMessageBusSubscriber(notifyFuncList []func(block *common.Block),
	logger protocol.Logger) msgbus.Subscriber {
	return &messageBusSubscriber{
		notifyFuncList: notifyFuncList,
		logger:         logger,
	}
}

// messageBusSubscriber implementation of the message bus subscriber interface.
// notifyFuncList is the list of notify function
// onmessage will notify to the functions one by one
type messageBusSubscriber struct {
	notifyFuncList []func(block *common.Block)
	logger         protocol.Logger
}

// OnMessage implement the function OnMessage of the transport subscriber.
// Topic msgbus.BlockInfo 是blockCommitter在提交区块的时候，触发的通知
func (s *messageBusSubscriber) OnMessage(message *msgbus.Message) {
	switch message.Topic {
	case msgbus.BlockInfo:
		s.logger.Infof("[msgBus] on message new block")
		if blockInfo, ok := message.Payload.(*common.BlockInfo); ok {
			s.logger.Infof("[msgBus] on message new block, height [%d]", blockInfo.Block.Header.BlockHeight)
			// 通知provider新落块
			for _, notifyFunc := range s.notifyFuncList {
				notifyFunc(blockInfo.Block)
			}
		}
	}
}

// OnQuit implement the function OnQuit of the transport subscriber.
func (s *messageBusSubscriber) OnQuit() {

}
