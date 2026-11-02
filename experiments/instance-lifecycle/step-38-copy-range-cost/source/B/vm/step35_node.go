package wasmer

// Explicitly opted-in bounded real-node adapter. No old pool/grow/async-close path.
import (
 "bytes"
	"chainmaker.org/chainmaker/logger/v2"
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	trace35c "chainmaker.org/chainmaker/store/v2/step35c"
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
 e38ID uint64
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
	trace35c.Event("vm_"+event, fields)
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
	id:=e38NewID();mark:=e38Begin(id,"runtime_bytecode_clone",len(raw));private:=append([]byte(nil),raw...);e38End(mark)
 return &nodeFreshRuntime{m:m,contract:*c,raw:private,e38ID:id},nil
}
func (m *nodeFreshManager) clear() error {
	trace35c.Hold("reset_cleanup")
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
	hashMark:=e38Begin(e38Current,"prepare_SHA",len(raw))
key := m.chain + "/" + c.Name + "/" + c.Version + "/" + nodeSHA(raw) + "/" + m.config + fmt.Sprint("/copy=", m.copy)
 e38End(hashMark)
	lookupMark:=e38Begin(e38Current,"module_cache_map_lookup",0);rec=m.caches[key];e38End(lookupMark)
 if rec != nil {
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
 strategy := "C0"
if e := e38Coalesce(plan,strategy); e != nil { return nil,e }
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
	mark:=e38Begin(r.e38ID,"invoke_two_SHA",len(raw)+len(r.raw));bad:=c == nil || c.Name != r.contract.Name || c.Version != r.contract.Version || nodeSHA(raw) != nodeSHA(r.raw);e38End(mark)
 if bad {
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
 oldID:=e38Current;e38Current=r.e38ID;defer func(){e38Current=oldID}()
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
	cost_module_prepare_inclusive:=e38Begin(r.e38ID,"module_prepare_inclusive",0)
 rec, e := m.prepare(c, raw)
 e38End(cost_module_prepare_inclusive)
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
		cm:=e38Begin(r.e38ID,"native_scope_close",0);closeErr:=scope.Close();e38End(cm)
 if e := closeErr; e != nil {
			err = fmt.Errorf("cleanup: %v; execution: %v", e, err)
		}
		if w.ManagedCount()-m.cacheObjects != before {
			err = fmt.Errorf("escaped instance resources: %d -> %d", before, w.ManagedCount()-m.cacheObjects)
		}
		fields["close_ns"] = time.Since(cb).Nanoseconds()
	}()
	cost_new_store:=e38Begin(r.e38ID,"new_store",0)
 store := w.NewStore(rec.store.Engine)
 e38End(cost_new_store)
	bm:=e38Begin(r.e38ID,"wasi_builder",0);builder:=w.NewWasiStateBuilder("step35");e38End(bm)
 fm:=e38Begin(r.e38ID,"wasi_finalize",0);envWasi,e:=builder.Finalize(store.Inner());e38End(fm)
	if e != nil {
		return e
	}
	cost_wasi_generate_imports:=e38Begin(r.e38ID,"wasi_generate_imports",0)
 imports, e := envWasi.GenerateImportObject(store, rec.module)
 e38End(cost_wasi_generate_imports)
	if e != nil {
		return e
	}
	host := CMEnvironment{}
	cost_cm_get_imports:=e38Begin(r.e38ID,"cm_get_imports",0)
 imports, e = GetVmBridgeManager().GetImports(store, &host, imports)
 e38End(cost_cm_get_imports)
	if e != nil {
		return e
	}
	ni := time.Now()
	cost_newinstance_inclusive:=e38Begin(r.e38ID,"newinstance_inclusive",0)
 inst, e = w.NewInstanceInStore(rec.module, imports, store)
 e38End(cost_newinstance_inclusive)
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
	if rec.plan != nil { fields["range_count"]=len(rec.plan.Ranges);fields["copy_bytes"]=rec.plan.e38CopyBytes }
 if os.Getenv("E38_VERIFY_MEMORY")=="1" { image:=[]byte(nil);if rec.plan!=nil { image=rec.plan.Image } else { checkPlan,err:=prepareStaticMemory(raw,c,m.config);if err!=nil{return err};image=checkPlan.Image };checkMem,err:=inst.Exports.GetMemory("memory");if err!=nil{return err};if !bytes.Equal(checkMem.Data(),image){return errors.New("initial full Memory mismatch")};fields["initial_memory_match"]=true }
 fields["s1_ns"] = time.Since(begin).Nanoseconds()
	wim:=e38Begin(r.e38ID,"wasi_initialize",0);e=envWasi.Initialize(store,inst);e38End(wim)
 if e != nil {
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
