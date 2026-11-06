/*
Copyright (C) BABEC. All rights reserved.
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
SPDX-License-Identifier: Apache-2.0
*/
package wasmer

import (
	"chainmaker.org/chainmaker/logger/v2"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	"context"
	"errors"
	"sync"
)

// InstancesManager caches compiled Modules, never executed Instances or WASI envs.
// Native cache access and request resources are confined to owner.
type InstancesManager struct {
	chainId  string
	log      *logger.CMLogger
	m        sync.Mutex
	owner    *SafeFreshOwner
	stopped  bool
	stopDone chan struct{}
	stopErr  error
	caches   map[storeCacheKey]*storeModule
}

func NewInstancesManager(chainId string) *InstancesManager {
	return &InstancesManager{chainId: chainId, log: logger.GetLoggerByChain(logger.MODULE_VM, chainId), caches: make(map[storeCacheKey]*storeModule)}
}
func (m *InstancesManager) nativeOwner() (*SafeFreshOwner, error) {
	m.m.Lock()
	defer m.m.Unlock()
	if m.stopped {
		return nil, ErrOwnerClosed
	}
	if m.owner == nil {
		o, e := acquireFreshOwner()
		if e != nil {
			return nil, e
		}
		m.owner = o
	}
	return m.owner, nil
}
func (m *InstancesManager) NewRuntimeInstance(_ protocol.TxSimContext, _, _, _ string, c *commonPb.Contract, raw []byte, _ protocol.Logger) (protocol.RuntimeInstance, error) {
	if c == nil || c.Name == "" || c.Version == "" || len(raw) == 0 {
		return nil, errors.New("invalid contract/bytecode")
	}
	o, e := m.nativeOwner()
	if e != nil {
		return nil, e
	}
	// Compile before returning, preserving bytecode validation at runtime creation.
	// Copy input because the caller may reuse its buffer after this method returns.
	code := append([]byte(nil), raw...)
	contract := *c
	e = o.Do(context.Background(), func() error {
		if m.isStopped() {
			return ErrOwnerClosed
		}
		_, e := m.prepare(&contract, code)
		return e
	})
	if e != nil {
		return nil, e
	}
	return &RuntimeInstance{log: m.log, chainId: m.chainId, instancesManager: m, contract: contract, raw: code}, nil
}
func (m *InstancesManager) isStopped() bool { m.m.Lock(); defer m.m.Unlock(); return m.stopped }
func (m *InstancesManager) clearContract(c *commonPb.Contract) error {
	var errs []error
	for k, r := range m.caches {
		if c == nil || (k.name == c.Name && k.version == c.Version) {
			if e := r.scope.Close(); e != nil {
				errs = append(errs, e)
			}
			delete(m.caches, k)
		}
	}
	return errors.Join(errs...)
}
func (m *InstancesManager) invalidate(c *commonPb.Contract) error {
	o, e := m.nativeOwner()
	if e != nil {
		return e
	}
	return o.Do(context.Background(), func() error {
		if m.isStopped() {
			return ErrOwnerClosed
		}
		// A callback must never invalidate a Module while its parent is executing.
		for k, r := range m.caches {
			if (c == nil || (k.name == c.Name && k.version == c.Version)) && r.active != 0 {
				return errors.New("cache invalidation from active contract callback rejected")
			}
		}
		return m.clearContract(c)
	})
}
func (m *InstancesManager) CloseRuntimeInstance(name, version string) error {
	return m.invalidate(&commonPb.Contract{Name: name, Version: version})
}
func (m *InstancesManager) CloseAVmPool(c *commonPb.Contract) {
	if e := m.invalidate(c); e != nil {
		m.log.Errorf("close module cache: %v", e)
	}
}
func (m *InstancesManager) CloseAllVmPool() {
	if e := m.invalidate(nil); e != nil {
		m.log.Errorf("close module caches: %v", e)
	}
}
func (m *InstancesManager) ResetAVmPool(c *commonPb.Contract) { m.CloseAVmPool(c) }
func (m *InstancesManager) ResetAllPool()                     { m.CloseAllVmPool() }
func (m *InstancesManager) StartVM() error                    { _, e := m.nativeOwner(); return e }
func (m *InstancesManager) StopVM() error {
	m.m.Lock()
	o := m.owner
	if o != nil && o.tid.Load() == int64(currentThreadID()) {
		m.m.Unlock()
		return errors.New("StopVM from active native callback rejected")
	}
	if m.stopped {
		done := m.stopDone
		m.m.Unlock()
		<-done
		return m.stopErr
	}
	m.stopped = true
	m.stopDone = make(chan struct{})
	done := m.stopDone
	m.m.Unlock()
	var e error
	if o != nil {
		// FIFO owner admission drains all earlier native calls; late jobs check stopped.
		e = o.Do(context.Background(), func() error { return m.clearContract(nil) })
		e = errors.Join(e, releaseFreshOwner(o))
	}
	m.stopErr = e
	close(done)
	return e
}
func (m *InstancesManager) BeforeSchedule(string, uint64) {}
func (m *InstancesManager) AfterSchedule(string, uint64)  {}

// Retained for old in-package pool probes. Native handles cannot be leased to
// arbitrary goroutines; use NewRuntimeInstance instead.
func (m *InstancesManager) getVmPool(_ *commonPb.Contract, _ []byte) (*vmPool, error) {
	return nil, errors.New("legacy Instance pool disabled; use NewRuntimeInstance")
}
