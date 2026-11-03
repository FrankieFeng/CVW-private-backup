/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

// Package manager provides functionality for managing rules.
package manager

import (
	"fmt"
 rd39e "experiment.local/readiness39e"
	"strings"
	"sync"

	rule "chainmaker.org/chainmaker/common/v2/syncrule"
	"chainmaker.org/chainmaker/pb-go/v2/common"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/pb-go/v2/syscontract"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/gogo/protobuf/proto"
)

var (
	// syncContract 系统合约名称
	syncContract = syscontract.SystemContract_SYNC_RULE.String()
	// ruleMethod 规则方法名称
	ruleMethod = syscontract.SyncRuleFunction_ADD.String()

	consensusAddNodeParamKey = "node_ids"

	emptyRule = &syncPb.NodeRule{}
)

const (
	// ParamNodeID 用来匹配规则修改交易中node_id字段参数
	// 需要和vm-native/syncmgr.ParamNodeID保持一致
	ParamNodeID = "node_id"
	// GetRuleKey 函数使用此值生成key，需要和vm-native/syncmgr.ruleKeyPrefix保持一致
	ruleKeyPrefix = "sync_rule"
)

// GetRuleKey 用于生成nodeID对应的rule key，通过key从存储中读取对应的rule.
// 需要和vm-native/syncmgr.GetRuleKey函数保持一致
func GetRuleKey(nodeID string) []byte {
	return []byte(fmt.Sprintf("%s#%s", ruleKeyPrefix, nodeID))
}

// NewRuleManager for provider
func NewRuleManager(nodeId string, store protocol.BlockchainStore, logger protocol.Logger) *RuleManager {
	return &RuleManager{
		upRuleTo: 0,
		ownRule: &syncPb.NodeRule{
			NodeId: nodeId,
		},
		nodeRules: make(map[string]*syncPb.NodeRule),
		newBlockC: make(chan *common.Block, types.DefaultChanCap),
		store:     store,
		logger:    logger,
	}
}

// RuleManager 规则管理器
type RuleManager struct {
	mu sync.RWMutex
	// 管理器更新规则到的块⾼
	upRuleTo uint64
	// ownRule 自身的规则
	ownRule *syncPb.NodeRule
	// nodeRules 其他节点的规则
	nodeRules map[string]*syncPb.NodeRule
	// newBlockC 新落块的通知通道
	newBlockC chan *common.Block
	// TxSpecification缓存，在同一个ruleId下TS是相同的
	tsCache map[string]ridTsCache
	store   protocol.BlockchainStore
	logger  protocol.Logger
}

// Start 启动规则管理器
// 1. 设置自身当前区块高度
// 2. 缓存自身规则
// 3. 初始化ts缓存map
func (m *RuleManager) Start() error {
	lastBlock, err := m.store.GetLastBlock()
	if err != nil {
		return err
	}
	m.upRuleTo = lastBlock.Header.BlockHeight

	if ownRule, err := m.getRuleFromStore(m.ownRule.NodeId); err == nil {
		m.ownRule = ownRule
	}

	m.tsCache = make(map[string]ridTsCache)

	go m.watchNewBlock()
	return nil
}

// Stop 关闭
func (m *RuleManager) Stop() error {
	return nil
}

// NotifyNewBlock 新块落块通知
func (m *RuleManager) NotifyNewBlock(block *common.Block) {
	if block!=nil&&block.Header!=nil{rd39e.Notify(block.Header.BlockHeight)}else{rd39e.Notify(0)}
 m.newBlockC <- block
}

// watchNewBlock 监听新的区块被提交
func (m *RuleManager) watchNewBlock() {
	defer rd39e.Mark("rule_consumer_exit")
 for {
  rd39e.Waiting()
  block,ok:=<-m.newBlockC
  if !ok{return}
  h:=uint64(0);if block!=nil&&block.Header!=nil{h=block.Header.BlockHeight};rd39e.Taken(h)
		// 判断只有一条交易
		if block == nil || len(block.Txs) != 1 || block.Txs[0] == nil || block.Txs[0].Payload == nil {
			continue
		}
		m.logger.Infof("receive a new block, height [%v]", block.Header.BlockHeight)

		// 如果高不大于已更新的最新块高，忽略
		if block.Header.BlockHeight <= m.upRuleTo {
			continue
		}

		switch block.Txs[0].Payload.ContractName {
		case syncContract:
			// 如果是正在同步的节点，更新规则
			parameters := block.Txs[0].Payload.Parameters
			m.logger.Infof("receive a new block with rule op, parameters [%v]", parameters)
			for _, kvs := range parameters {
				if kvs.Key == ParamNodeID {
					m.updateRule(string(kvs.Value))
					m.upRuleTo = block.Header.BlockHeight
				}
			}
		case syscontract.SystemContract_CHAIN_CONFIG.String():
			method := block.Txs[0].Payload.Method
			if method == syscontract.ChainConfigFunction_NODE_ID_ADD.String() ||
				method == syscontract.ChainConfigFunction_NODE_ORG_ADD.String() {
				// 如果是正在同步的节点，更新规则
				parameters := block.Txs[0].Payload.Parameters
				m.logger.Infof("receive a new block with consensus node added, parameters [%v]", parameters)
				for _, kvs := range parameters {
					if kvs.Key == consensusAddNodeParamKey {
						for _, nodeId := range strings.Split(string(kvs.Value), ",") {
							m.updateRule(nodeId)
						}
						m.upRuleTo = block.Header.BlockHeight
					}
				}
			}
		}
	}
}

// updateRule 更新节点规则
// 1. 从存储中读取规则
// 2. 如果是自身节点，更新ownRule
// 3. 如果是其他节点，更新nodeRules
// 4. 规则更新后，清除tsCache
func (m *RuleManager) updateRule(nodeId string) {
	if nodeId == m.ownRule.NodeId {
		newNodeRule, err := m.getRuleFromStore(nodeId)
		m.logger.Infof("update own rule: %v", newNodeRule)
		if err != nil {
			m.logger.Errorf("get rule from store failed, err: %v", err)
			return
		}
		m.mu.Lock()
		m.ownRule = newNodeRule
		delete(m.tsCache, nodeId)
		m.mu.Unlock()
		return
	}

	m.mu.Lock()
	defer m.mu.Unlock()
	if _, ok := m.nodeRules[nodeId]; ok {
		delete(m.nodeRules, nodeId)
		delete(m.tsCache, nodeId)
	}
}

// getRuleFromStore 从存储中获取节点规则
func (m *RuleManager) getRuleFromStore(nodeId string) (*syncPb.NodeRule, error) {
	key := GetRuleKey(nodeId)
	bytes, err := m.store.ReadObject(syncContract, key)
	if err != nil {
		return nil, err
	}
	r := &syncPb.NodeRule{}
	if err = proto.Unmarshal(bytes, r); err != nil {
		return nil, err
	}
	return r, nil
}

// OwnRule 自身节点NodeRule
func (m *RuleManager) OwnRule(height uint64) *syncPb.Rule {
	if len(m.ownRule.Rules) == 0 {
		return nil
	}
	return getRule(m.ownRule, height)
}

// OwnRulePerm 获取自身当前规则perm
func (m *RuleManager) OwnRulePerm(height uint64) string {
	if r := getRule(m.ownRule, height); r != nil {
		return r.Content
	}
	return ""
}

// OwnNextRuleAtHeight own next rule whose BeginHeight is greater than height.
func (m *RuleManager) OwnNextRuleAtHeight(height uint64) *syncPb.Rule {
	return getNextRule(m.ownRule, height)
}

// GetNodeRule 获取节点规则
// 1. 判读列表中是否存在，存在直接返回
// 2. 如果不存在，则从db中读取，缓存后返回
func (m *RuleManager) GetNodeRule(nodeId string, height uint64) *syncPb.Rule {
	m.mu.RLock()
	defer m.mu.RUnlock()
	nRule := m.getNodeRuleUnlock(nodeId)
	return getRule(nRule, height)
}

func getRule(nr *syncPb.NodeRule, height uint64) *syncPb.Rule {
	if nr == nil {
		return nil
	}
	for i := len(nr.Rules) - 1; i >= 0; i-- {
		r := nr.Rules[i]
		if height >= r.BeginHeight && (r.EndHeight == 0 || height <= r.EndHeight) {
			return r
		}
	}
	return nil
}

func getNextRule(nr *syncPb.NodeRule, height uint64) *syncPb.Rule {
	if nr == nil {
		return nil
	}
	for i := len(nr.Rules) - 1; i >= 0; i-- {
		if nr.Rules[i].BeginHeight > height {
			return nr.Rules[i]
		}
	}
	return nil
}

// GetNodeRuleById 通过ruleId获取节点规则
func (m *RuleManager) GetNodeRuleById(nodeId string, ruleId uint32) *syncPb.Rule {
	m.mu.RLock()
	defer m.mu.RUnlock()
	if nRule := m.getNodeRuleUnlock(nodeId); nRule != nil {
		for _, r := range nRule.Rules {
			if r.GetId() == ruleId {
				return r
			}
		}
	}
	return nil
}

// func (m *RuleManager) getNodeRule(nodeId string) *syncPb.NodeRule {
// 	m.mu.RLock()
// 	defer m.mu.RUnlock()
// 	return m.getNodeRuleUnlock(nodeId)
// }

func (m *RuleManager) getNodeRuleUnlock(nodeId string) *syncPb.NodeRule {
	nRule := m.nodeRules[nodeId]
	if nRule == nil {
		newNodeRule, err := m.getRuleFromStore(nodeId)
		if err != nil {
			m.logger.Errorf("[rule] get node[%s] rule from store error: %v", nodeId, err)
			return nil
		}
		m.logger.Infof("[rule] update [%s] rule : %v", nodeId, newNodeRule)
		if newNodeRule == nil {
			newNodeRule = emptyRule
		}
		nRule = newNodeRule
		m.nodeRules[nodeId] = newNodeRule
	}
	return nRule
}

// GetRulePermTs 获取规则解析TxSpecification
func (m *RuleManager) GetRulePermTs(nodeId string, r *syncPb.Rule) (rule.TxSpecification, error) {
	// 从缓存中读取，如果存在直接返回, created表示节点ID对应的规则缓存是否已经存在
	// exsist表示rule.id对应的规则是否存在于缓存中
	tx, exsist, created := func() (rule.TxSpecification, bool, bool) {
		m.mu.RLock()
		defer m.mu.RUnlock()
		ridTs, exist := m.tsCache[nodeId]
		if !exist {
			return nil, false, false
		} else if ts, ok := ridTs[r.Id]; ok {
			return ts, true, true
		}
		return nil, false, true
	}()
	if exsist {
		return tx, nil
	}
	m.mu.Lock()
	defer m.mu.Unlock()
	if !created {
		m.tsCache[nodeId] = make(ridTsCache)
	}
	// 缓存不存在，解析规则后，存储缓存并返回
	ts, err := rule.ParseRule(r.Content)
	if err != nil {
		return nil, err
	}
	m.tsCache[nodeId][r.Id] = ts
	return ts, err
}

// ridTsCache rid => TxSpecification
type ridTsCache map[uint32]rule.TxSpecification

// GetCurrentRuleId 获取当前规则ruleId
func (m *RuleManager) GetCurrentRuleId(nodeId string, currentHeight uint64) uint32 {
	currentRule := m.getCurrentRule(nodeId, currentHeight)
	if currentRule == nil {
		return 0
	}
	return currentRule.GetId()
}

// getCurrentRule 获取当前规则ruleId
func (m *RuleManager) getCurrentRule(nodeId string, currentHeight uint64) *syncPb.Rule {
	m.mu.RLock()
	defer m.mu.RUnlock()
	nRule := m.getNodeRuleUnlock(nodeId)
	return getRule(nRule, currentHeight)
}

// GetNodeNextRuleAtHeight get next rule whose BeiginHeight is greater than currentHeight for nodeid.
func (m *RuleManager) GetNodeNextRuleAtHeight(nodeId string, currentHeight uint64) *syncPb.Rule {
	m.mu.RLock()
	defer m.mu.RUnlock()
	if nRule := m.getNodeRuleUnlock(nodeId); nRule != nil {
		return getNextRule(nRule, currentHeight)
	}

	return nil
}

// GetNextRuleFromHeight 计算下一个规则生效高度
func (m *RuleManager) GetNextRuleFromHeight(nodeId string, currentHeight uint64) uint64 {
	// 获取当前高度的规则ID
	// currentRuleId := m.GetCurrentRuleId(nodeId, currentHeight)
	m.mu.RLock()
	defer m.mu.RUnlock()
	if nRule := m.getNodeRuleUnlock(nodeId); nRule != nil {
		if rule := getNextRule(nRule, currentHeight); rule != nil {
			return rule.BeginHeight
		}
	}
	return 0
}

// GetCurrentRuleFromHeight 获取当前规则的起始块高
func (m *RuleManager) GetCurrentRuleFromHeight(nodeId string, currentHeight uint64) uint64 {
	// 获取当前高度的规则
	currentRule := m.getCurrentRule(nodeId, currentHeight)
	if currentRule != nil {
		return currentRule.BeginHeight
	}
	return 0
}
