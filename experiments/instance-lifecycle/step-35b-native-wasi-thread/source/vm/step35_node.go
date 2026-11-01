package wasmer

// Explicitly opted-in bounded real-node adapter. No old pool/grow/async-close path.
import (
	"chainmaker.org/chainmaker/logger/v2"
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"runtime"
	"sync/atomic"
	"time"
)

type nodeFreshCache struct {
	scope  *w.ManagedScope
	store  *w.Store
	module *w.Module
	plan   *staticMemoryPlan
	source string
}
type nodeFreshManager struct {
	control35a    *control35a
	owner         *SafeFreshOwner
	caches        map[string]*nodeFreshCache
	order         []string
	cacheScope    *w.ManagedScope
	chain, config string
	copy          bool
	next          uint64
	cacheObjects  int
	inflight      atomic.Int64
}
type nodeFreshRuntime struct {
	m        *nodeFreshManager
	contract common.Contract
	raw      []byte
}

func nodeSHA(b []byte) string { h := sha256.Sum256(b); return hex.EncodeToString(h[:]) }
func nodeEvent(event string, fields map[string]interface{}) {
	if fields == nil {
		fields = map[string]interface{}{}
	}
	fields["event"] = event
	fields["wall_ns"] = time.Now().UnixNano()
	var mem runtime.MemStats
	runtime.ReadMemStats(&mem)
	fields["go_heap"] = mem.HeapAlloc
	fields["go_heap_sys"] = mem.HeapSys
	fields["go_num_gc"] = mem.NumGC
	fields["go_heap_released"] = mem.HeapReleased
	if int64(syscallTID()) == nodeOwnerTID.Load() {
		fields["stores_created"] = w.ManagedStoresCreated
		fields["stores_closed"] = w.ManagedStoresClosed
		fields["instances_created"] = w.ManagedInstancesCreated
		fields["instances_closed"] = w.ManagedInstancesClosed
		fields["managed_pending"] = w.ManagedCount()
	}
	b, _ := json.Marshal(fields)
	fmt.Printf("STEP35 %s\n", b)
}

var nodeOwnerTID atomic.Int64

func newNodeFreshManager(chain string) (*nodeFreshManager, error) {
	if os.Getenv("CM_REUSE_EXPERIMENT") != "R1" {
		return nil, errors.New("safe Fresh node requires R1; no executed Instance reuse")
	}
	cfg := os.Getenv("CM_SAFE_FRESH_CONFIG")
	if cfg == "" {
		return nil, errors.New("missing immutable native/compiler/Gas/config identity")
	}
	m := &nodeFreshManager{chain: chain, config: cfg, copy: os.Getenv("CM_STATIC_MEMORY_COPY") == "1", caches: map[string]*nodeFreshCache{}}
	o, e := NewSafeFreshOwner(32, func() error { defer nodeOwnerTID.Store(0); return m.clear() })
	if e != nil {
		return nil, e
	}
	m.owner = o
	return m, nil
}
func (m *nodeFreshManager) runtime(c *common.Contract, raw []byte) (protocol.RuntimeInstance, error) {
	if c == nil || c.Name == "" || c.Version == "" || len(raw) == 0 {
		return nil, errors.New("invalid contract/bytecode")
	}
	return &nodeFreshRuntime{m: m, contract: *c, raw: append([]byte(nil), raw...)}, nil
}
func (m *nodeFreshManager) clear() error {
	w.ManagedAssert()
	if m.inflight.Load() != 0 {
		return errors.New("cleanup while invoking")
	}
	var errs []error
	for i := len(m.order) - 1; i >= 0; i-- {
		if e := m.caches[m.order[i]].scope.Close(); e != nil {
			errs = append(errs, e)
		}
	}
	m.caches = map[string]*nodeFreshCache{}
	m.order = nil
	m.cacheObjects = 0
	if m.cacheScope != nil {
		if e := m.cacheScope.Close(); e != nil {
			errs = append(errs, e)
		}
		m.cacheScope = nil
	}
	nodeEvent("cache_closed", nil)
	return errors.Join(errs...)
}
func (m *nodeFreshManager) reset() error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	return m.owner.Reset(ctx, m.clear)
}
func (m *nodeFreshManager) prepare(c *common.Contract, raw []byte) (rec *nodeFreshCache, err error) {
	w.ManagedAssert()
	if m.cacheScope == nil {
		m.cacheScope = w.ManagedOpen("node-cache-root")
		m.cacheScope.Suspend()
	}
	restore := m.cacheScope.Activate()
	defer restore()
	key := m.chain + "/" + c.Name + "/" + c.Version + "/" + nodeSHA(raw) + "/" + m.config + fmt.Sprint("/copy=", m.copy)
	if rec = m.caches[key]; rec != nil {
		nodeEvent("module_hit", map[string]interface{}{"contract": c.Name, "key": key})
		return rec, nil
	}
	if len(m.caches) >= 8 {
		return nil, errors.New("bounded module cache full")
	}
	begin := time.Now()
	baseObjects := w.ManagedCount()
	scope := w.ManagedOpen("cache-" + key)
	ok := false
	defer func() {
		if !ok {
			scope.Close()
		} else {
			scope.Suspend()
		}
	}()
	code := raw
	var plan *staticMemoryPlan
	if m.copy {
		plan, err = prepareStaticMemory(raw, c, m.config)
		if err != nil {
			nodeEvent("copy_fallback", map[string]interface{}{"contract": c.Name, "reason": err.Error()})
			plan = nil
			err = nil
		} else {
			code = plan.NoData
		}
	}
	store, module, e := dCompile(c, code, logger.GetLogger("step35"))
	if e != nil {
		return nil, e
	}
	module.Imports()
	module.Exports()
	if plan != nil {
		plan.Module = module
	}
	rec = &nodeFreshCache{scope: scope, store: store, module: module, plan: plan, source: nodeSHA(raw)}
	m.caches[key] = rec
	m.order = append(m.order, key)
	m.cacheObjects += w.ManagedCount() - baseObjects
	ok = true
	nodeEvent("module_prepared", map[string]interface{}{"contract": c.Name, "key": key, "source_sha": rec.source, "prepare_ns": time.Since(begin).Nanoseconds(), "copy": plan != nil})
	return rec, nil
}
func (r *nodeFreshRuntime) Invoke(c *common.Contract, method string, raw []byte, params map[string][]byte, tx protocol.TxSimContext, gasUsed uint64) (result *common.ContractResult, order protocol.ExecOrderTxType) {
	result = &common.ContractResult{Code: 1}
	order = protocol.ExecOrderTxTypeNormal
	if c == nil || c.Name != r.contract.Name || c.Version != r.contract.Version || nodeSHA(raw) != nodeSHA(r.raw) {
		result.Message = "runtime contract/hash mismatch"
		return
	}
	// No request deadline returns while tx context is still being accessed: cancellation is admission-only.
	e := r.m.owner.Do(context.Background(), func() error {
		nodeOwnerTID.Store(int64(syscallTID()))
		return r.invoke(c, method, raw, params, tx, gasUsed, result, &order)
	})
	if e != nil {
		result.Code = 1
		result.Message = e.Error()
	}
	return
}
func (r *nodeFreshRuntime) invoke(c *common.Contract, method string, raw []byte, params map[string][]byte, tx protocol.TxSimContext, gasUsed uint64, result *common.ContractResult, order *protocol.ExecOrderTxType) (err error) {
	m := r.m
	w.ManagedAssert()
	m.inflight.Add(1)
	defer m.inflight.Add(-1)
	begin := time.Now()
	m.next++
	id := m.next
	fields := map[string]interface{}{"tx_id": tx.GetTx().Payload.TxId, "contract": c.Name, "method": method, "depth": tx.GetDepth(), "instance_id": id}
	nodeEvent("invoke_begin", fields)
	defer func() {
		if p := recover(); p != nil {
			err = fmt.Errorf("safe invoke panic: %v", p)
		}
		if err != nil {
			result.Code = 1
			result.Message = err.Error()
		}
		fields["invoke_ns"] = time.Since(begin).Nanoseconds()
		fields["gas"] = result.GasUsed
		fields["code"] = result.Code
		fields["error"] = fmt.Sprint(err)
		nodeEvent("invoke_end", fields)
	}()
	rec, e := m.prepare(c, raw)
	if e != nil {
		return e
	}
	restore := rec.scope.Activate()
	defer restore()
	before := w.ManagedCount() - m.cacheObjects
	scope := w.ManagedOpen("fresh-" + c.Name)
	var inst *w.Instance
	started := false
	defer func() {
		cb := time.Now()
		if started {
			if e := CallDeallocate(inst); e != nil {
				err = fmt.Errorf("deallocate: %v; execution: %v", e, err)
			}
		}
		if e := scope.Close(); e != nil {
			err = fmt.Errorf("cleanup: %v; execution: %v", e, err)
		}
		if w.ManagedCount()-m.cacheObjects != before {
			err = fmt.Errorf("escaped instance resources: %d -> %d", before, w.ManagedCount()-m.cacheObjects)
		}
		fields["close_ns"] = time.Since(cb).Nanoseconds()
	}()
	store := w.NewStore(rec.store.Engine)
	envWasi, e := w.NewWasiStateBuilder("step35").Finalize(store.Inner())
	if e != nil {
		return e
	}
	imports, e := envWasi.GenerateImportObject(store, rec.module)
	if e != nil {
		return e
	}
	host := CMEnvironment{}
	imports, e = GetVmBridgeManager().GetImports(store, &host, imports)
	if e != nil {
		return e
	}
	ni := time.Now()
	inst, e = w.NewInstanceInStore(rec.module, imports, store)
	fields["newinstance_ns"] = time.Since(ni).Nanoseconds()
	if e != nil {
		return e
	}
	fields["store_id"] = fmt.Sprintf("%p", store.Inner())
	fields["compile_store_id"] = fmt.Sprintf("%p", rec.store.Inner())
	if rec.plan != nil {
		cb := time.Now()
		if e = rec.plan.restore(rec.module, inst, raw, c, m.config); e != nil {
			return e
		}
		fields["copy_ns"] = time.Since(cb).Nanoseconds()
	}
	fields["s1_ns"] = time.Since(begin).Nanoseconds()
	if e = envWasi.Initialize(store, inst); e != nil {
		return e
	}
	start, e := inst.Exports.GetWasiStartRawFunction()
	if e != nil {
		return e
	}
	sb := time.Now()
	_, e = start.Call()
	fields["start_ns"] = time.Since(sb).Nanoseconds()
	if e != nil && e.Error() != "WASI exited with code: ExitCode::0" {
		return e
	}
	start.Close()
	started = true
	fields["s2_ns"] = time.Since(begin).Nanoseconds()
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
	sc := NewSimContext(method, logger.GetLogger("step35"), m.chain)
	defer sc.removeCtxPointer()
	sc.Contract = c
	sc.TxSimContext = tx
	sc.ContractResult = result
	sc.parameters = params
	sc.Instance = inst
	sc.SpecialTxType = protocol.ExecOrderTxTypeNormal
	result.Code = 0
	cb := time.Now()
	callErr := sc.CallMethod(inst)
	fields["callmethod_ns"] = time.Since(cb).Nanoseconds()
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
		result.Code = 1
		result.Message = callErr.Error()
	} else {
		result.ContractEvent = sc.ContractEvent
	}
	return nil
}
