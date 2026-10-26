package wasmer

import (
	"chainmaker.org/chainmaker/logger/v2"
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"runtime"
	"sort"
	"strconv"
	"testing"
	"time"
)

var e22Enabled = os.Getenv("E22_ENABLED") == "1"

type e22Profile struct {
	CallError string `json:"call_error_observed"`

	Contract      string `json:"contract"`
	Variant       string `json:"variant"`
	Method        string `json:"method"`
	TxID          string `json:"tx_id"`
	ID            int    `json:"instance_id"`
	Depth         int    `json:"depth"`
	NewInstanceNS int64  `json:"newinstance_ns"`
	CopyNS        int64  `json:"copy_ns"`
	CopyBytes     int    `json:"copy_bytes"`
	CopyRanges    int    `json:"copy_ranges"`
	WASIPrepNS    int64  `json:"wasi_imports_ns"`
	S1NS          int64  `json:"to_s1_ns"`
	S2NS          int64  `json:"to_s2_ns"`
	S3NS          int64  `json:"to_s3_ns"`
	StartNS       int64  `json:"start_ns"`
	InitializeNS  int64  `json:"wasi_initialize_ns"`
	CallMethodNS  int64  `json:"callmethod_ns"`
	CloseNS       int64  `json:"close_ns"`
	InvokeNS      int64  `json:"invoke_ns"`
	S1Hash        string `json:"s1_hash,omitempty"`
	Gas           uint64 `json:"gas"`
	Code          uint32 `json:"code"`
	BeforeObjects int    `json:"managed_before"`
	AfterObjects  int    `json:"managed_after"`
}
type e22Cache struct {
	scope   *w.ManagedScope
	store   *w.Store
	module  *w.Module
	plan    *staticMemoryPlan
	key     string
	variant string
}
type e22State struct {
	cache       map[string]*e22Cache
	plans       map[string]*staticMemoryPlan
	order       []string
	variant     string
	invokeBegin time.Time
	validate    bool
	rows        []e22Profile
}

func newE22State() *e22State {
	return &e22State{cache: map[string]*e22Cache{}, plans: map[string]*staticMemoryPlan{}, variant: "A0"}
}
func e22Emit(event string, data interface{}) {
	b, e := json.Marshal(map[string]interface{}{"event": event, "data": data})
	if e != nil {
		panic(e)
	}
	fmt.Printf("STEP22 %s\n", b)
}
func e22Hash(b []byte) string { h := sha256.Sum256(b); return hex.EncodeToString(h[:]) }
func (m *dManager) e22Prepare(c *common.Contract, raw []byte) error {
	w.ManagedAssert()
	begin := time.Now()
	cfg := os.Getenv("E22_CONFIG_SHA")
	if cfg == "" {
		return fmt.Errorf("missing immutable configuration identity")
	}
	p, e := prepareStaticMemory(raw, c, cfg)
	if e != nil {
		return e
	}
	imageSHA := e22Hash(p.Image)
	nodataSHA := e22Hash(p.NoData)
	m.e22.plans[c.Name] = p
	e22Emit("template", map[string]interface{}{"contract": c.Name, "source_sha": p.SourceSHA, "nodata_sha": nodataSHA, "image_sha": imageSHA, "key": p.Key, "image_bytes": len(p.Image), "ranges": len(p.Ranges), "prepare_ns": time.Since(begin).Nanoseconds()})
	for _, v := range []string{"A0", "A1"} {
		scope := w.ManagedOpen("module-" + c.Name + v)
		start := time.Now()
		code := raw
		if v == "A1" {
			code = p.NoData
		}
		store, module, err := dCompile(c, code, logger.GetLogger("step22-prepare"))
		if err != nil {
			scope.Close()
			return err
		}
		// Pin module's lazy owning metadata in module scope, not the first Instance scope.
		module.Imports()
		module.Exports()
		key := p.Key + "/" + v
		rec := &e22Cache{scope: scope, store: store, module: module, plan: p, key: key, variant: v}
		m.e22.cache[c.Name+v] = rec
		m.e22.order = append(m.e22.order, c.Name+v)
		if v == "A1" {
			p.Module = module
		}
		scope.Suspend()
		e22Emit("module", map[string]interface{}{"contract": c.Name, "variant": v, "module_prepare_ns": time.Since(start).Nanoseconds(), "cache_key": key, "module_wasm_sha": e22Hash(code), "managed": w.ManagedCount()})
	}
	e22Emit("preparation_total", map[string]interface{}{"contract": c.Name, "prepare_total_ns": time.Since(begin).Nanoseconds()})
	return nil
}
func (m *dManager) makeE22(c *common.Contract, raw []byte) (b *dBundle, err error) {
	w.ManagedAssert()
	rec := m.e22.cache[c.Name+m.e22.variant]
	if rec == nil {
		return nil, fmt.Errorf("module not prepared; no per-call compilation allowed")
	}
	restore := rec.scope.Activate()
	defer restore()
	before := w.ManagedCount()
	scope := w.ManagedOpen("instance-" + c.Name + rec.variant)
	m.next++
	b = &dBundle{scope: scope, contract: c.Name, id: m.next, profile: &e22Profile{Contract: c.Name, Variant: rec.variant, ID: m.next, BeforeObjects: before}}
	p := b.profile
	begin := m.e22.invokeBegin
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("create panic: %v", r)
		}
		if err != nil {
			scope.Close()
		} else {
			scope.Suspend()
		}
	}()
	wasiBegin := time.Now()
	envWasi, e := w.NewWasiStateBuilder("step22").Finalize(rec.store.Inner())
	if e != nil {
		return b, e
	}
	imports, e := envWasi.GenerateImportObject(rec.store, rec.module)
	if e != nil {
		return b, e
	}
	host := CMEnvironment{}
	imports, e = GetVmBridgeManager().GetImports(rec.store, &host, imports)
	if e != nil {
		return b, e
	}
	p.WASIPrepNS = time.Since(wasiBegin).Nanoseconds()
	ni := time.Now()
	inst, e := w.NewInstance(rec.module, imports)
	p.NewInstanceNS = time.Since(ni).Nanoseconds()
	if e != nil {
		return b, e
	}
	b.instance = inst
	if rec.variant == "A1" {
		cb := time.Now()
		e = rec.plan.restore(rec.module, inst, raw, c, rec.plan.ConfigID)
		p.CopyNS = time.Since(cb).Nanoseconds()
		if e != nil {
			return b, e
		}
		for _, r := range rec.plan.Ranges {
			p.CopyBytes += r.End - r.Begin
		}
		p.CopyRanges = len(rec.plan.Ranges)
	}
	p.S1NS = time.Since(begin).Nanoseconds()
	if m.e22.validate {
		mem, e := inst.Exports.GetMemory("memory")
		if e != nil {
			return b, e
		}
		p.S1Hash = e22Hash(mem.Data())
		if p.S1Hash != e22Hash(rec.plan.Image) {
			return b, fmt.Errorf("S1 differs from static template")
		}
	}
	ib := time.Now()
	if e = envWasi.Initialize(rec.store, inst); e != nil {
		return b, e
	}
	p.InitializeNS = time.Since(ib).Nanoseconds()
	start, e := inst.Exports.GetWasiStartRawFunction()
	if e != nil {
		return b, e
	}
	sb := time.Now()
	_, e = start.Call()
	p.StartNS = time.Since(sb).Nanoseconds()
	if e != nil && e.Error() != "WASI exited with code: ExitCode::0" {
		return b, e
	}
	start.Close()
	p.S2NS = time.Since(begin).Nanoseconds()
	host.instance = inst
	host.memory, e = inst.Exports.GetMemory("memory")
	if e != nil {
		return b, e
	}
	m.created++
	return b, nil
}
func (m *dManager) closeE22(b *dBundle) (err error) {
	if b == nil || b.closed {
		return nil
	}
	w.ManagedAssert()
	restore := b.scope.Activate()
	defer restore()
	begin := time.Now()
	beforeClose := w.ManagedCount()
	ownedLive := b.scope.ManagedLiveCount()
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("deallocate panic: %v", r)
		}
		if e := b.scope.Close(); e != nil {
			err = fmt.Errorf("scope cleanup: %v; %w", err, e)
		}
		b.closed = true
		b.instance = nil
		m.closed++
		b.profile.CloseNS = time.Since(begin).Nanoseconds()
		b.profile.AfterObjects = w.ManagedCount()
		if b.profile.AfterObjects != beforeClose-ownedLive {
			err = fmt.Errorf("scope ownership cleanup mismatch: before=%d own=%d after=%d", beforeClose, ownedLive, b.profile.AfterObjects)
		}
		if m.policy == "R1" && b.profile.AfterObjects != b.profile.BeforeObjects {
			err = fmt.Errorf("per-instance metadata escaped scope: %d -> %d", b.profile.BeforeObjects, b.profile.AfterObjects)
		}
	}()
	return CallDeallocate(b.instance)
}
func (s *e22State) closeCaches() error {
	w.ManagedAssert()
	begin := time.Now()
	for i := len(s.order) - 1; i >= 0; i-- {
		if e := s.cache[s.order[i]].scope.Close(); e != nil {
			return e
		}
	}
	s.cache = map[string]*e22Cache{}
	e22Emit("cache_closed", map[string]interface{}{"close_ns": time.Since(begin).Nanoseconds(), "managed_remaining": w.ManagedCount()})
	return nil
}
func e22Clone(in map[string]map[string][]byte) map[string]map[string][]byte {
	b, _ := json.Marshal(in)
	var out map[string]map[string][]byte
	json.Unmarshal(b, &out)
	return out
}
func e22Expected(t *testing.T, f *s21cFixture, name string, p map[string]string, r *s21cReceipt) {
	t.Helper()
	switch name {
	case "compute":
		if string(r.Result.Result) != "success bigNumCal: 607723520" {
			t.Fatal("wrong bigNum result")
		}
	case "fact":
		var result map[string]interface{}
		if json.Unmarshal(r.Result.Result, &result) != nil || result["fileHash"] != p["file_hash"] || result["fileName"] != p["file_name"] || fmt.Sprint(result["time"]) != "1.792827547e+09" && fmt.Sprint(result["time"]) != "1792827547" {
			t.Fatalf("wrong fact JSON: %s", r.Result.Result)
		}
		if f.state("fact", "fact_bytes", p["file_hash"]) == "" {
			t.Fatal("fact write missing")
		}
	case "erc721":
		if string(r.Result.Result) != "mint success" || f.state("erc721", "tokenIds", p["tokenId"]) != p["to"] {
			t.Fatal("mint result/owner mismatch")
		}
	case "exchange":
		if string(r.Result.Result) != "buyNow success" || f.state("erc721", "tokenIds", p["tokenId"]) != p["to"] || len(r.Calls) != 7 {
			t.Fatal("full real buyNow/owner/call graph failed")
		}
		for _, c := range r.Calls {
			if c.Code != 0 || c.Depth > 1 {
				t.Fatal("callee failed or unexpected depth")
			}
		}
	default:
		t.Fatal("unregistered expected business")
	}
}
func e22Assert(t *testing.T, a, b *s21cReceipt) {
	t.Helper()
	if a.Result.Code != b.Result.Code || a.Status != b.Status || a.Result.GasUsed != b.Result.GasUsed || string(a.Result.Result) != string(b.Result.Result) || a.AfterHash != b.AfterHash {
		t.Fatalf("A0/A1 return/Gas/state differs: %+v vs %+v", a.Result, b.Result)
	}
	aw, _ := json.Marshal(a.RWSet)
	bw, _ := json.Marshal(b.RWSet)
	ae, _ := json.Marshal(a.Result.ContractEvent)
	be, _ := json.Marshal(b.Result.ContractEvent)
	if string(aw) != string(bw) || string(ae) != string(be) {
		t.Fatal("A0/A1 RWSet/events differ")
	}
}
func TestStep22Serial(t *testing.T) {
	if !e22Enabled {
		t.Fatal("explicit E22_ENABLED required")
	}
	defer dOwner(t)()
	n, e := strconv.Atoi(os.Getenv("E22_PAIRS"))
	if e != nil || n < 1 || n > 3 {
		t.Fatal("registered budget 1..3 pairs")
	}
	name := os.Getenv("E22_CONTRACT")
	method := os.Getenv("E22_METHOD")
	phase := os.Getenv("E22_PHASE")
	f := s21cPrepare(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
	defer f.close()
	m := f.instances
	names := []string{}
	for name := range f.snapshot.store.contracts {
		names = append(names, name)
	}
	sort.Strings(names)
	for _, name := range names {
		c, _ := f.snapshot.store.GetContractByName(name)
		code, _ := f.snapshot.store.GetContractBytecode(name)
		if e = m.e22Prepare(c, code); e != nil {
			t.Fatal(e)
		}
	}
	// Actual initialization is outside timed samples. Both variants start from identical cloned ledger.
	single := os.Getenv("E22_SINGLE_VARIANT")
	if single != "" && (name != "exchange" || n != 1 || single != "A0" && single != "A1") {
		t.Fatal("unregistered single-process split budget")
	}
	m.e22.variant = "A0"
	if single != "" {
		m.e22.variant = single
	}
	for _, name := range names {
		args := map[string]string{}
		if name == "erc721" {
			args = map[string]string{"name": "huanletoken", "symbol": "hlt", "tokenURI": "https://chainmaker.org.cn"}
		}
		r := f.run("setup-"+name, name, "init_contract", "step22-init-"+name, args)
		if r.Result.Code != 0 {
			t.Fatalf("actual init failed: %+v", r.Result)
		}
	}
	initial := e22Clone(f.snapshot.ledger)
	m.e22.validate = phase == "preflight"
	for i := 0; i < n; i++ {
		params := map[string]string{}
		if name == "fact" {
			params = map[string]string{"file_hash": "005521f27d745a04999c6d09f559764f9c44376a", "file_name": "aoteman.jpg", "time": "1792827547"}
		}
		if name == "erc721" {
			params = map[string]string{"to": "8acfaca5eeec9f6f7c23c4ffac969b86f27799b0", "tokenId": fmt.Sprint(i + 1), "metadata": "http://chainmaker.org.cn/"}
		}
		if name == "exchange" {
			params = map[string]string{"from": "8acfaca5eeec9f6f7c23c4ffac969b86f27799b0", "to": "818fac1ac51525aeedf619a9a339b95854930159", "tokenId": fmt.Sprint(i + 1), "metadata": "http://chainmaker.org.cn/"}
		}
		order := []string{"A0", "A1"}
		seed, _ := strconv.ParseInt(os.Getenv("E22_SEED"), 10, 64)
		if rand.New(rand.NewSource(seed+int64(i))).Intn(2) == 1 {
			order = []string{"A1", "A0"}
		}
		if single != "" {
			order = []string{single}
		}
		receipts := map[string]*s21cReceipt{}
		for _, v := range order {
			m.e22.variant = v
			f.snapshot.ledger = e22Clone(initial)
			r := f.run(fmt.Sprintf("pair-%03d-%s", i, v), name, method, fmt.Sprintf("step22-%s-%03d", name, i), params)
			receipts[v] = r
			e22Expected(t, f, name, params, r)
			if r.Result.Code != 0 {
				t.Fatalf("business failed %+v", r.Result)
			}
			dEvent("boundary", map[string]interface{}{"contract": name, "variant": v, "pair": i})
		}
		if single == "" {
			e22Assert(t, receipts["A0"], receipts["A1"])
		} else {
			e22Emit("split_receipt", map[string]interface{}{"variant": single, "receipt_label": fmt.Sprintf("pair-%03d-%s", i, single), "note": "must compare against matching other-process variant; no pair pass claimed here"})
		}
	}
	e22Emit("correctness", map[string]interface{}{"observed_pair_slots": n, "single_variant": single, "phase": phase, "S1_memory_checked": m.e22.validate, "table_function_identity": "not_tested", "fresh_instances_only": true})
	runtime.KeepAlive(initial)
}

// Native scalar lifecycle probe: repeated fresh instances from one cached Module, no WASI.
func TestStep22ModuleLifecycle(t *testing.T) {
	defer dOwner(t)()
	scope := w.ManagedOpen("persistent-probe")
	store := w.NewStore(w.NewEngine())
	mod, e := w.NewModule(store, []byte(`(module (memory (export "memory") 1) (func (export "answer") (result i32) i32.const 42))`), nil)
	if e != nil {
		t.Fatal(e)
	}
	mod.Imports()
	mod.Exports()
	base := w.ManagedCount()
	scope.Suspend()
	for i := 0; i < 3; i++ {
		restore := scope.Activate()
		s := w.ManagedOpen("fresh-probe")
		inst, e := w.NewInstance(mod, w.NewImportObject())
		if e != nil {
			t.Fatal(e)
		}
		mem, e := inst.Exports.GetMemory("memory")
		if e != nil {
			t.Fatal(e)
		}
		if mem.Data()[0] != 0 {
			t.Fatal("fresh memory not zero")
		}
		mem.Data()[0] = byte(i + 1)
		fn, e := inst.Exports.GetRawFunction("answer")
		if e != nil {
			t.Fatal(e)
		}
		v, e := fn.Call()
		if e != nil || v.(int32) != 42 {
			t.Fatal("scalar result mismatch")
		}
		fn.Close()
		if e = s.Close(); e != nil {
			t.Fatal(e)
		}
		restore()
		if w.ManagedCount() != base {
			t.Fatal("cached module metadata lost/leaked")
		}
	}
	if e = scope.Close(); e != nil {
		t.Fatal(e)
	}
	e22Emit("lifecycle_probe", map[string]interface{}{"fresh_count": 3, "result": 42, "zero_new_memory": true, "managed_after": w.ManagedCount()})
}
