/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package provider

import (
	rule "chainmaker.org/chainmaker/common/v2/syncrule"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/sync/v2/conn"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/rule/manager"
)

type listenHandler struct {
	ruleManager *manager.RuleManager
}

func newListenHandler(rManager *manager.RuleManager) *listenHandler {
	return &listenHandler{
		ruleManager: rManager,
	}
}

// HandleListen handles incoming listen requests from other nodes
// It checks the rules set by the node and returns the block number and workload
func (l *listenHandler) HandleListen(nodeID string, height uint64) conn.BlockSupportResult {
	// check if the nodeID and height meet the rules
	ok := l.checkRules(nodeID, height)
	if ok {
		// if the rules are met, set the blockNum to -1
		return conn.BlockSupportResult{
			BlockNum: -1,
			Workload: 0,
			Code:     errors.ErrCodeNon,
		}
	}
	return conn.BlockSupportResult{
		BlockNum: 0,
		Workload: 0,
		Code:     errors.ErrCodeRuleNotMeet,
	}
}

func (l *listenHandler) checkRules(nodeID string, height uint64) bool {
	// 检查过滤规则是否满足
	// 获取请求节点在此高度的规则,
	requestNodeRule := l.ruleManager.GetNodeRule(nodeID, height)
	ownRule := l.ruleManager.OwnRule(height)

	// 判断自身规则是否包含请求节点规则
	// 1. 如果本地节点未设置规则，则检查通过
	if !hasRule(ownRule) {
		return true
	}
	// 2. 如果本地节点有规则，请求节点未设置规则，则检查不通过
	if !hasRule(requestNodeRule) {
		return false
	}
	// 3. 当本地节点有规则，请求节点也有规则，则判断包含关系
	return rule.CompareRules(ownRule.Content, requestNodeRule.Content)
}

func hasRule(rule *syncPb.Rule) bool {
	return rule != nil && len(rule.Content) > 0
}
