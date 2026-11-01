/*
Copyright (C) BABEC. All rights reserved.
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package wasmer

import (
	"context"
	"fmt"
	"os"
	"sync"
	"time"

	"chainmaker.org/chainmaker/logger/v2"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/utils/v2"
)

// InstancesManager manages vm pools for all contracts
type InstancesManager struct {
	safe    *nodeFreshManager
	safeErr error
	// chain identifier
	chainId string
	// control map operations
	m sync.RWMutex
	// contractName_contractVersion -> vm pool
	instanceMap map[string]*vmPool
	// module log
	log *logger.CMLogger
}

// NewInstancesManager return InstancesManager for every chain
func NewInstancesManager(chainId string) *InstancesManager {
	vmPoolManager := &InstancesManager{
		instanceMap: make(map[string]*vmPool),
		log:         logger.GetLoggerByChain(logger.MODULE_VM, chainId),
		chainId:     chainId,
	}
	if os.Getenv("CM_SAFE_FRESH_NODE") == "1" {
		vmPoolManager.safe, vmPoolManager.safeErr = newNodeFreshManager(chainId)
		if vmPoolManager.safeErr == nil {
			vmPoolManager.safeErr = vmPoolManager.start35aControl()
		}
	} else {
		vmPoolManager.safeErr = fmt.Errorf("managed experimental binary requires CM_SAFE_FRESH_NODE=1; rollback uses the original binary, not the legacy pool in this binary")
	}
	return vmPoolManager
}

// NewRuntimeInstance init vm pool and check byteCode correctness
func (m *InstancesManager) NewRuntimeInstance(
	txSimContext protocol.TxSimContext,
	chainId, method, codePath string,
	contract *commonPb.Contract,
	byteCode []byte,
	log protocol.Logger) (protocol.RuntimeInstance, error) {
	if m.safeErr != nil {
		return nil, m.safeErr
	}
	if m.safe != nil {
		return m.safe.runtime(contract, byteCode)
	}
	var err error
	if contract == nil || contract.Name == "" || contract.Version == "" {
		err = fmt.Errorf("contract id is nil")
		m.log.Warn(err)
		return nil, err
	}

	if len(byteCode) == 0 {
		err = fmt.Errorf("[%s_%s], byte code is nil", contract.Name, contract.Version)
		m.log.Warn(err)
		return nil, err
	}

	pool, err := m.getVmPool(contract, byteCode)
	if err != nil || pool == nil {
		return nil, err
	}

	runtime := &RuntimeInstance{
		pool:             pool,
		log:              m.log,
		chainId:          m.chainId,
		instancesManager: m,
	}

	return runtime, nil
}

// CloseRuntimeInstance comment at next version
func (m *InstancesManager) CloseRuntimeInstance(
	contractName string,
	contractVersion string) error {
	if m.safe != nil {
		return m.safe.reset()
	}
	m.log.Debugf("wasmer instance manager => close runtime instance => %v(%v)", contractName, contractVersion)
	contract := commonPb.Contract{
		Name:    contractName,
		Version: contractVersion,
	}

	m.CloseAVmPool(&contract)
	return nil
}

func (m *InstancesManager) getVmPool(contractId *commonPb.Contract, byteCode []byte) (*vmPool, error) {
	var err error
	key := contractId.Name + "_" + contractId.Version

	m.m.RLock()
	pool, ok := m.instanceMap[key]
	m.m.RUnlock()
	if !ok {
		m.m.Lock()
		defer m.m.Unlock()

		pool, ok = m.instanceMap[key]
		if !ok {
			start := utils.CurrentTimeMillisSeconds()
			m.log.Infof("[%s] init vm pool start", key)

			pool, err = newVmPool(contractId, byteCode, m.log)
			if err != nil {
				return nil, err
			}

			pool.grow(defaultMinSize)
			m.instanceMap[key] = pool
			end := utils.CurrentTimeMillisSeconds()
			m.log.Infof("[%s] init vmPool done, currentSize=%d, spend %dms", key, pool.currentSize, end-start)
		}
	}
	return pool, err
}

// CloseAVmPool close the contract vm pool
func (m *InstancesManager) CloseAVmPool(contractId *commonPb.Contract) {
	if m.safe != nil {
		if e := m.tracked35aReset(); e != nil {
			m.log.Errorf("safe reset: %v", e)
		}
		return
	}
	m.m.Lock()
	defer m.m.Unlock()

	key := contractId.Name + "_" + contractId.Version
	pool, ok := m.instanceMap[key]
	if ok {
		m.log.Infof("close pool %s", key)
		pool.close()
		delete(m.instanceMap, key)
	}
}

// CloseAllVmPool close all contract vm pool
func (m *InstancesManager) CloseAllVmPool() {
	if m.safe != nil {
		if e := m.tracked35aReset(); e != nil {
			m.log.Errorf("safe reset: %v", e)
		}
		return
	}
	m.m.Lock()
	defer m.m.Unlock()

	for key, pool := range m.instanceMap {
		m.log.Infof("close pool %s", key)
		pool.close()
	}
	m.instanceMap = make(map[string]*vmPool)
}

// ResetAVmPool reset a contract vm pool install
// FIXME: 确认函数名是否多了字符A？@taifu
func (m *InstancesManager) ResetAVmPool(contractId *commonPb.Contract) {
	if m.safe != nil {
		if e := m.tracked35aReset(); e != nil {
			m.log.Errorf("safe reset: %v", e)
		}
		return
	}
	m.m.Lock()
	defer m.m.Unlock()

	key := contractId.Name + "_" + contractId.Version
	pool, ok := m.instanceMap[key]
	if ok {
		m.log.Infof("reset pool %s", key)
		pool.reset()
	}
}

// ResetAllPool reset all contract pool instance
func (m *InstancesManager) ResetAllPool() {
	if m.safe != nil {
		if e := m.tracked35aReset(); e != nil {
			m.log.Errorf("safe reset: %v", e)
		}
		return
	}
	m.m.Lock()
	defer m.m.Unlock()

	for key, pool := range m.instanceMap {
		m.log.Infof("reset pool %s", key)
		pool.reset()
	}
}

// StartVM comment at next version
func (m *InstancesManager) StartVM() error {
	return m.safeErr
}

// StopVM comment at next version
func (m *InstancesManager) StopVM() error {
	if m.safe != nil {
		// Do not return a timeout to Blockchain.Stop while a guest may still access its TxSimContext/store.
		// The external node supervisor bounds shutdown and kills the whole process on a stuck native call.
		nodeEvent("stop_requested", map[string]interface{}{"inflight": m.safe.inflight.Load()})
		start := time.Now()
		err := m.safe.owner.Stop(context.Background())
		if m.safe.control35a != nil {
			m.safe.control35a.Close()
		}
		nodeEvent("stop_finished", map[string]interface{}{"stop_ns": time.Since(start).Nanoseconds(), "error": fmt.Sprint(err)})
		return err
	}
	return m.safeErr
}

// BeforeSchedule add request before block schedule
func (m *InstancesManager) BeforeSchedule(blockFingerprint string, blockHeight uint64) {
}

// AfterSchedule print tx log after block schedule
func (m *InstancesManager) AfterSchedule(blockFingerprint string, blockHeight uint64) {
}
