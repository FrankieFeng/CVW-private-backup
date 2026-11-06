package wasmer

import (
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"context"
	"crypto/sha256"
	"errors"
	"fmt"
	"syscall"
	"time"
)

// Struct fields avoid the old ambiguous name + "_" + version concatenation.
// Chain/config are fixed by this manager and compiler, not mutable environment flags.
type storeCacheKey struct {
	name, version string
	hash          [32]byte
}
type storeModule struct {
	scope  *w.ManagedScope
	store  *w.Store
	module *w.Module
	active int
}

func currentThreadID() int { return syscall.Gettid() }
func (m *InstancesManager) prepare(c *commonPb.Contract, raw []byte) (rec *storeModule, err error) {
	w.ManagedAssert()
	if e := w.ManagedFailure(); e != nil {
		return nil, fmt.Errorf("native owner cleanup failed: %w", e)
	}
	key := storeCacheKey{c.Name, c.Version, sha256.Sum256(raw)}
	if rec = m.caches[key]; rec != nil {
		return rec, nil
	}
	scope := w.ManagedOpen("module-" + c.Name)
	ok := false
	defer func() {
		if !ok {
			err = errors.Join(err, scope.Close())
		} else {
			scope.Suspend()
		}
	}()
	store, module, e := compileStoreModule(c, raw, m.log)
	if e != nil {
		return nil, e
	}
	// Cache metadata in the cache scope, never in the first request scope.
	module.Imports()
	module.Exports()
	rec = &storeModule{scope: scope, store: store, module: module}
	m.caches[key] = rec
	ok = true
	return rec, nil
}
func (r *RuntimeInstance) invokeFresh(c *commonPb.Contract, method string, raw []byte, params map[string][]byte, tx protocol.TxSimContext, gasUsed uint64) (result *commonPb.ContractResult, order protocol.ExecOrderTxType, callSeconds float64) {
	result = &commonPb.ContractResult{Code: 1}
	order = protocol.ExecOrderTxTypeNormal
	if r.instancesManager == nil && r.pool != nil && r.pool.freshManager != nil {
		ri, e := r.pool.freshManager.NewRuntimeInstance(nil, "", "", "", c, raw, r.log)
		if e != nil {
			result.Message = e.Error()
			return
		}
		return ri.(*RuntimeInstance).invokeFresh(c, method, raw, params, tx, gasUsed)
	}
	if r.instancesManager == nil {
		result.Message = "runtime requires NewInstancesManager.NewRuntimeInstance"
		return
	}
	if c == nil || c.Name != r.contract.Name || c.Version != r.contract.Version || sha256.Sum256(raw) != sha256.Sum256(r.raw) {
		result.Message = "runtime contract/bytecode mismatch"
		return
	}
	m := r.instancesManager
	o, e := m.nativeOwner()
	if e != nil {
		result.Message = e.Error()
		return
	}
	e = o.Do(context.Background(), func() error {
		if m.isStopped() {
			return ErrOwnerClosed
		}
		return r.executeFresh(c, method, raw, params, tx, gasUsed, result, &order, &callSeconds)
	})
	if e != nil {
		result.Code = 1
		result.Message = e.Error()
	}
	return
}
func (r *RuntimeInstance) executeFresh(c *commonPb.Contract, method string, raw []byte, params map[string][]byte, tx protocol.TxSimContext, gasUsed uint64, result *commonPb.ContractResult, order *protocol.ExecOrderTxType, callSeconds *float64) (err error) {
	w.ManagedAssert()
	defer func() {
		if p := recover(); p != nil {
			err = fmt.Errorf("fresh execution panic: %v", p)
		}
	}()
	rec, e := r.instancesManager.prepare(c, raw)
	if e != nil {
		return e
	}
	rec.active++
	defer func() { rec.active-- }()
	restore := rec.scope.Activate()
	defer restore()
	scope := w.ManagedOpen("fresh-" + c.Name)
	var inst *w.Instance
	started := false
	defer func() {
		// Even a panic in guest deallocate must not skip native resource destruction.
		defer func() { err = errors.Join(err, scope.Close()) }()
		if started {
			err = errors.Join(err, CallDeallocate(inst))
		}
	}()
	store := w.NewStore(rec.store.Engine)
	if store == nil {
		return errors.New("Store allocation failed")
	}
	// All request imports, host callbacks and WASI are created in this target Store.
	var wasi *w.WasiEnvironment
	imports := w.NewImportObject()
	if hasWasi(rec.module) {
		wasi, e = w.NewWasiStateBuilder(c.Name).Finalize(store.Inner())
		if e != nil {
			return e
		}
		imports, e = wasi.GenerateImportObject(store, rec.module)
		if e != nil {
			return e
		}
	}
	host := &CMEnvironment{}
	imports, e = GetVmBridgeManager().GetImports(store, host, imports)
	if e != nil {
		return e
	}
	inst, e = w.NewInstanceInStore(rec.module, imports, store)
	if e != nil {
		return e
	}
	if hasWasi(rec.module) {
		if e = wasi.Initialize(store, inst); e != nil {
			return e
		}
		start, e := inst.Exports.GetWasiStartRawFunction()
		if e != nil {
			return e
		}
		_, e = start.Call()
		start.Close()
		if e != nil && e.Error() != "WASI exited with code: ExitCode::0" {
			return e
		}
	}
	started = true
	host.instance = inst
	host.memory, e = inst.Exports.GetMemory("memory")
	if e != nil {
		return e
	}
	available := uint64(0)
	if gasUsed < runtimeGasLimit {
		available = runtimeGasLimit - gasUsed
	}
	if e = setGasByExport(inst, available); e != nil {
		return e
	}
	sc := NewSimContext(method, r.log, r.chainId)
	defer sc.removeCtxPointer()
	sc.Contract = c
	sc.TxSimContext = tx
	sc.ContractResult = result
	sc.parameters = params
	sc.Instance = inst
	sc.SpecialTxType = protocol.ExecOrderTxTypeNormal
	result.Code = 0
	begin := time.Now()
	callErr := sc.CallMethod(inst)
	*callSeconds = time.Since(begin).Seconds()
	*order = sc.SpecialTxType
	remaining, e := getGasByExport(inst)
	if e != nil {
		return e
	}
	result.GasUsed = runtimeGasLimit - remaining
	if remaining == 0 || remaining == ^uint64(0) {
		callErr = errors.New("out of gas")
	}
	if callErr != nil {
		return callErr
	}
	result.ContractEvent = sc.ContractEvent
	// An init/upgrade failure has no reusable instance to invalidate; Module is immutable.
	return nil
}
func hasWasi(module *w.Module) bool {
	for _, imp := range module.Imports() {
		if imp.Module() == "wasi_snapshot_preview1" || imp.Module() == "wasi_unstable" {
			return true
		}
	}
	return false
}
