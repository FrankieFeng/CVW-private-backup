package wasmer

import (
	"fmt"
	"time"

	"chainmaker.org/chainmaker/logger/v2"
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"os"
	"strconv"
	"strings"
	"syscall"
)

type dBundle struct {
	profile *e22Profile

	scope    *w.ManagedScope
	instance *w.Instance
	contract string
	id       int
	used     int
	closed   bool
}
type dManager struct {
	e22 *e22State

	protocol.VmInstancesManager
	policy          string
	cache           map[string]*dBundle
	active          map[string]bool
	fixture         *s21cFixture
	next            int
	inFlight        int
	closing         bool
	created, closed int
}

func newDManager(policy string) *dManager {
	if policy != "R0" && policy != "R1" {
		panic("explicit D_POLICY required")
	}
	m := &dManager{policy: policy, cache: map[string]*dBundle{}, active: map[string]bool{}}
	if e22Enabled {
		m.e22 = newE22State()
	}
	return m
}

var dEpoch = time.Now()

func dEvent(event string, fields map[string]interface{}) {
	if e22Enabled && event != "manager_closed" && event != "owner_closed" && event != "boundary" {
		return
	}
	w.ManagedAssert()
	if fields == nil {
		fields = map[string]interface{}{}
	}
	fields["event"] = event
	fields["wall_unix_ns"] = time.Now().UnixNano()
	fields["monotonic_ns"] = time.Since(dEpoch).Nanoseconds()
	fields["owner_tid"] = syscall.Gettid()
	fields["managed_objects"] = w.ManagedCount()
	data, _ := os.ReadFile("/proc/self/status")
	for _, line := range strings.Split(string(data), "\n") {
		for _, key := range []string{"VmRSS:", "Threads:"} {
			if strings.HasPrefix(line, key) {
				v, _ := strconv.Atoi(strings.Fields(line)[1])
				fields[key[:len(key)-1]] = v
			}
		}
	}
	s21cEmit(fields)
	// Same protection thresholds, checked at lifecycle boundaries as well as external polling.
	if v, ok := fields["VmRSS"].(int); ok && v > 1536*1024 {
		panic("RSS protection")
	}
	if v, ok := fields["Threads"].(int); ok && v > 220 {
		panic("thread protection")
	}
}
func (m *dManager) NewRuntimeInstance(_ protocol.TxSimContext, chain, method, path string, c *common.Contract, code []byte, _ protocol.Logger) (protocol.RuntimeInstance, error) {
	w.ManagedAssert()
	if m.closing {
		return nil, fmt.Errorf("manager closing")
	}
	if len(m.cache) >= 3 && m.cache[c.Name] == nil {
		return nil, fmt.Errorf("contract capacity")
	}
	return &dRuntime{manager: m, chain: chain}, nil
}
func (m *dManager) makeBundle(c *common.Contract, code []byte) (b *dBundle, err error) {
	if e22Enabled {
		return m.makeE22(c, code)
	}
	w.ManagedAssert()
	m.next++
	b = &dBundle{scope: w.ManagedOpen(c.Name), contract: c.Name, id: m.next}
	begin := time.Now()
	dEvent("create_begin", map[string]interface{}{"contract": c.Name, "instance_id": b.id})
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("create panic: %v", r)
		}
		if err != nil {
			if e := b.scope.Close(); e != nil {
				err = fmt.Errorf("%v; cleanup: %w", err, e)
			}
			dEvent("create_failed", map[string]interface{}{"error": err.Error()})
		} else {
			b.scope.Suspend()
		}
	}()
	log := logger.GetLogger("step21d")
	store, module, e := dCompile(c, code, log)
	if e != nil {
		return b, e
	}
	compileEnd := time.Now()
	// Module is compiled in exactly this Store, and binding NewInstance uses module.store.
	wasi, e := w.NewWasiStateBuilder("step21d").Finalize(store.Inner())
	if e != nil {
		return b, e
	}
	imports, e := wasi.GenerateImportObject(store, module)
	if e != nil {
		return b, e
	}
	env := CMEnvironment{}
	imports, e = GetVmBridgeManager().GetImports(store, &env, imports)
	if e != nil {
		return b, e
	}
	inst, e := w.NewInstance(module, imports)
	if e != nil {
		return b, e
	}
	b.instance = inst
	if e = wasi.Initialize(store, inst); e != nil {
		return b, e
	}
	start, e := inst.Exports.GetWasiStartRawFunction()
	if e != nil {
		return b, e
	}
	if _, e = start.Call(); e != nil {
		// Fixed packaged ABI reports a successful WASI proc_exit(0) as a TrapError.
		// The original pool ignores all start errors; admit only this precise zero-exit case.
		if e.Error() != "WASI exited with code: ExitCode::0" {
			return b, e
		}
		dEvent("start_exit_zero", map[string]interface{}{"instance_id": b.id, "error": e.Error()})
	}
	start.Close()
	env.instance = inst
	env.memory, e = inst.Exports.GetMemory("memory")
	if e != nil {
		return b, e
	}
	m.created++
	dEvent("create_done", map[string]interface{}{"contract": c.Name, "instance_id": b.id, "create_ns": time.Since(begin).Nanoseconds(), "compile_ns": compileEnd.Sub(begin).Nanoseconds()})
	return b, nil
}
func (m *dManager) closeBundle(b *dBundle) (err error) {
	if e22Enabled {
		return m.closeE22(b)
	}
	if b == nil || b.closed {
		return nil
	}
	w.ManagedAssert()
	restore := b.scope.Activate()
	defer restore()
	begin := time.Now()
	dEvent("close_begin", map[string]interface{}{"contract": b.contract, "instance_id": b.id})
	// Scope always executes even if guest deallocation fails. Native void deletes have no status API.
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("deallocate panic: %v", r)
		}
		if e := b.scope.Close(); e != nil {
			err = fmt.Errorf("close cleanup: %v; %w", err, e)
		}
		b.closed = true
		b.instance = nil
		m.closed++
		dEvent("close_done", map[string]interface{}{"contract": b.contract, "instance_id": b.id, "close_ns": time.Since(begin).Nanoseconds(), "error": fmt.Sprint(err)})
	}()
	if b.instance != nil {
		err = CallDeallocate(b.instance)
	}
	return err
}
func (m *dManager) Close() error {
	w.ManagedAssert()
	m.closing = true
	if m.inFlight != 0 {
		return fmt.Errorf("in-flight %d", m.inFlight)
	}
	for _, b := range m.cache {
		if e := m.closeBundle(b); e != nil {
			return e
		}
	}
	m.cache = map[string]*dBundle{}
	if m.created != m.closed {
		return fmt.Errorf("lifecycle count %d/%d", m.created, m.closed)
	}
	if e22Enabled {
		if err := m.e22.closeCaches(); err != nil {
			return err
		}
	}
	dEvent("manager_closed", map[string]interface{}{"created": m.created, "closed": m.closed, "in_flight": m.inFlight})
	return nil
}

type dRuntime struct {
	manager *dManager
	chain   string
}

func (r *dRuntime) Invoke(c *common.Contract, method string, code []byte, params map[string][]byte, ctx protocol.TxSimContext, gasUsed uint64) (result *common.ContractResult, order protocol.ExecOrderTxType) {
	m := r.manager
	w.ManagedAssert()
	begin := time.Now()
	result = &common.ContractResult{}
	order = protocol.ExecOrderTxTypeNormal
	id := m.fixture.nextID
	m.fixture.nextID++
	depth := ctx.GetDepth()
	var callNS int64
	var b *dBundle
	defer func() {
		if x := recover(); x != nil {
			result.Code = 1
			result.Message = fmt.Sprint(x)
		}
		end := time.Now()
		if e22Enabled && b != nil && b.profile != nil {
			b.profile.InvokeNS = end.Sub(begin).Nanoseconds()
			b.profile.CallMethodNS = callNS
			b.profile.Gas = result.GasUsed
			b.profile.Code = result.Code
			b.profile.Method = method
			b.profile.Depth = depth
			b.profile.TxID = ctx.GetTx().Payload.TxId
			m.e22.rows = append(m.e22.rows, *b.profile)
			e22Emit("sample", b.profile)
		}
		row := s21cCall{ID: id, Depth: depth, Contract: c.Name, Method: method, TxID: ctx.GetTx().Payload.TxId, BeginNS: begin.UnixNano(), EndNS: end.UnixNano(), InvokeSeconds: end.Sub(begin).Seconds(), CallMethodSeconds: float64(callNS) / 1e9, GasUsed: result.GasUsed, Code: result.Code, Result: string(result.Result), Message: result.Message}
		m.fixture.calls = append(m.fixture.calls, row)
		s21cEmit(map[string]interface{}{"event": "invoke_return", "call": row})
	}()
	if m.closing || m.active[c.Name] || depth > 2 || m.inFlight >= 3 {
		result.Code = 1
		result.Message = "ownership/depth/capacity rejection"
		return
	}
	m.active[c.Name] = true
	m.inFlight++
	defer func() { delete(m.active, c.Name); m.inFlight-- }()
	if e22Enabled {
		m.e22.invokeBegin = begin
	}
	acquireBegin := time.Now()
	var e error
	if m.policy == "R0" {
		b = m.cache[c.Name]
	}
	if b == nil {
		b, e = m.makeBundle(c, code)
		if e != nil {
			result.Code = 1
			result.Message = e.Error()
			return
		}
		if m.policy == "R0" {
			m.cache[c.Name] = b
		}
	}
	restore := b.scope.Activate()
	defer restore()
	dEvent("acquire", map[string]interface{}{"contract": c.Name, "instance_id": b.id, "acquire_ns": time.Since(acquireBegin).Nanoseconds(), "channel_block_ns": 0, "queue_len": 0, "in_flight": m.inFlight, "previous_uses": b.used})
	if m.policy == "R1" && b.used != 0 {
		panic("fresh instance reused")
	}
	b.used++
	if m.policy == "R1" {
		defer func() {
			if ce := m.closeBundle(b); ce != nil {
				result.Code = 1
				result.Message += " close failure: " + ce.Error()
			}
		}()
	}
	limit := runtimeGasLimit
	available := limit
	if gasUsed < limit {
		available = limit - gasUsed
	} else {
		available = 0
	}
	if e = setGasByExport(b.instance, available); e != nil {
		panic(e)
	}
	sc := NewSimContext(method, logger.GetLogger("step21d"), r.chain)
	defer sc.removeCtxPointer()
	sc.Contract = c
	sc.TxSimContext = ctx
	sc.ContractResult = result
	sc.parameters = params
	sc.Instance = b.instance
	sc.SpecialTxType = protocol.ExecOrderTxTypeNormal
	execBegin := time.Now()
	dEvent("execute_begin", map[string]interface{}{"contract": c.Name, "instance_id": b.id, "method": method})
	callBegin := time.Now()
	e = sc.CallMethod(b.instance)
	if b.profile != nil {
		b.profile.ExportCallNS = sc.B5Profile.ExportCallNs
	}
	callNS = time.Since(callBegin).Nanoseconds()
	order = sc.SpecialTxType
	remaining, gasErr := getGasByExport(b.instance)
	if gasErr != nil {
		panic(gasErr)
	}
	// Preserve original runtime semantics: the existing code overwrites CallMethod err with gas read err.
	// Capture original CallMethod error separately as evidence, never rewrite Gas rules.
	observedCallError := e
	e = gasErr
	if remaining == 0 || remaining == ^uint64(0) {
		e = fmt.Errorf("contract invoke failed, out of gas %d", runtimeGasLimit)
	}
	result.GasUsed = limit - remaining
	if e != nil {
		result.Code = 1
		result.Message = e.Error()
	} else {
		result.ContractEvent = sc.ContractEvent
	}
	dEvent("execute_done", map[string]interface{}{"contract": c.Name, "instance_id": b.id, "method": method, "execute_ns": time.Since(execBegin).Nanoseconds(), "callmethod_ns": callNS, "gas": result.GasUsed, "code": result.Code, "call_error_observed": fmt.Sprint(observedCallError)})
	if e22Enabled && b.profile != nil {
		b.profile.S3NS = time.Since(begin).Nanoseconds()
		b.profile.CallError = fmt.Sprint(observedCallError)
	}

	return
}
