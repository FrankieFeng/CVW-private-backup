package wasmer

import (
	"chainmaker.org/chainmaker/logger/v2"
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"encoding/json"
	"fmt"
	"os"
	"runtime"
	"strconv"
	"testing"
	"time"
)

type e25Artifact struct {
	Path  string `json:"path"`
	SHA   string `json:"sha"`
	Copy  bool   `json:"copy"`
	Group string `json:"group"`
}

func (m *dManager) e25Prepare(c *common.Contract, raw []byte, role string, a e25Artifact) error {
	w.ManagedAssert()
	begin := time.Now()
	cfg := os.Getenv("E22_CONFIG_SHA")
	if cfg == "" || e22Hash(raw) != a.SHA {
		return fmt.Errorf("missing configuration or source hash mismatch")
	}
	p := m.e22.plans[a.SHA]
	if p == nil {
		var e error
		p, e = prepareStaticMemory(raw, c, cfg)
		if e != nil {
			return e
		}
		m.e22.plans[a.SHA] = p
		e22Emit("template", map[string]interface{}{"contract": c.Name, "group": a.Group, "source_sha": p.SourceSHA, "nodata_sha": e22Hash(p.NoData), "image_sha": e22Hash(p.Image), "key": p.Key, "image_bytes": len(p.Image), "ranges": len(p.Ranges), "prepare_ns": time.Since(begin).Nanoseconds()})
	}
	scope := w.ManagedOpen("module-" + c.Name + role)
	start := time.Now()
	code := raw
	if a.Copy {
		code = p.NoData
	}
	store, module, e := dCompile(c, code, logger.GetLogger("step25-prepare"))
	if e != nil {
		scope.Close()
		return e
	}
	module.Imports()
	module.Exports()
	rec := &e22Cache{scope: scope, store: store, module: module, plan: p, key: p.Key + "/" + a.Group, variant: role, doCopy: a.Copy}
	m.e22.cache[c.Name+role] = rec
	m.e22.order = append(m.e22.order, c.Name+role)
	if a.Copy {
		p.Module = module
	}
	scope.Suspend()
	e22Emit("module", map[string]interface{}{"contract": c.Name, "group": a.Group, "variant": role, "copy_enabled": a.Copy, "module_prepare_ns": time.Since(start).Nanoseconds(), "cache_key": rec.key, "module_wasm_sha": e22Hash(code), "source_sha": p.SourceSHA})
	return nil
}
func TestStep25Serial(t *testing.T) {
	if !e22Enabled {
		t.Fatal("explicit enabled required")
	}
	defer dOwner(t)()
	n, e := strconv.Atoi(os.Getenv("E22_PAIRS"))
	if e != nil || n < 1 || n > 2 {
		t.Fatal("one or two paired slots only")
	}
	var artifacts map[string]e25Artifact
	b, e := os.ReadFile(os.Getenv("E25_VARIANTS"))
	if e != nil || json.Unmarshal(b, &artifacts) != nil {
		t.Fatal("missing artifact manifest")
	}
	name := os.Getenv("E22_CONTRACT")
	method := os.Getenv("E22_METHOD")
	groups := []string{os.Getenv("E25_LEFT"), os.Getenv("E25_RIGHT")}
	roles := []string{"A0", "A1"}
	raw := map[string][]byte{}
	selected := map[string]e25Artifact{}
	f := s21cPrepare(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
	defer f.close()
	m := f.instances
	c, _ := f.snapshot.store.GetContractByName(name)
	for i, role := range roles {
		a, ok := artifacts[name+"-"+groups[i]]
		if !ok {
			t.Fatal("missing explicit variant")
		}
		if os.Getenv("E25_COPY_CHECK") == "1" && i == 0 {
			a.Copy = false
		}
		code, e := os.ReadFile(a.Path)
		if e != nil {
			t.Fatal(e)
		}
		selected[role] = a
		raw[role] = code
	}
	prepareOrder := []string{"A0", "A1"}
	if os.Getenv("E24_MODULE_FIRST") == "A1" {
		prepareOrder = []string{"A1", "A0"}
	}
	for _, role := range prepareOrder {
		if e = m.e25Prepare(c, raw[role], role, selected[role]); e != nil {
			t.Fatal(e)
		}
	}
	start := e22Clone(f.snapshot.ledger)
	var initialHash string
	for _, role := range prepareOrder {
		m.e22.variant = role
		f.snapshot.store.code[name] = raw[role]
		f.snapshot.ledger = e22Clone(start)
		args := map[string]string{}
		if name == "erc721" {
			args = map[string]string{"name": "huanletoken", "symbol": "hlt", "tokenURI": "https://chainmaker.org.cn"}
		}
		r := f.run("setup-"+name+"-"+role, name, "init_contract", "step25-init-"+name, args)
		if r.Result.Code != 0 || r.Status != 0 {
			t.Fatalf("actual init failed %+v", r.Result)
		}
		h := f.snapshot.hash()
		if initialHash != "" && h != initialHash {
			t.Fatal("initial ledger differs")
		}
		initialHash = h
	}
	initial := e22Clone(f.snapshot.ledger)
	m.e22.validate = os.Getenv("E22_PHASE") == "preflight"
	for i := 0; i < n; i++ {
		order := []string{"A0", "A1"}
		first, _ := strconv.Atoi(os.Getenv("E25_FIRST"))
		if (i+first)%2 == 1 {
			order = []string{"A1", "A0"}
		}
		receipts := map[string]*s21cReceipt{}
		params := map[string]string{}
		if name == "fact" {
			params = map[string]string{"file_hash": "005521f27d745a04999c6d09f559764f9c44376a", "file_name": "aoteman.jpg", "time": "1792827547"}
		}
		if name == "erc721" {
			params = map[string]string{"to": "8acfaca5eeec9f6f7c23c4ffac969b86f27799b0", "tokenId": "1", "metadata": "http://chainmaker.org.cn/"}
		}
		for _, role := range order {
			m.e22.variant = role
			f.snapshot.store.code[name] = raw[role]
			f.snapshot.ledger = e22Clone(initial)
			r := f.run(fmt.Sprintf("pair-%03d-%s", i, role), name, method, "step25-"+name+"-"+method+"-fixed", params)
			receipts[role] = r
			if name == "compute" && method == "normalCal" {
				if string(r.Result.Result) != "success normalCal: 666" {
					t.Fatal("normal result differs")
				}
			} else {
				e22Expected(t, f, name, params, r)
			}
			if r.Result.Code != 0 || r.Status != 0 {
				t.Fatalf("business failed %+v", r.Result)
			}
			var heap runtime.MemStats
			runtime.ReadMemStats(&heap)
			dEvent("boundary", map[string]interface{}{"contract": name, "method": method, "variant": role, "group": selected[role].Group, "pair": i, "go_heap_alloc": heap.HeapAlloc, "go_heap_sys": heap.HeapSys, "go_heap_inuse": heap.HeapInuse, "gas": r.Result.GasUsed})
		}
		// Deliberately strict across builds in this screening. Any Gas/state mismatch stops expansion.
		e22Assert(t, receipts["A0"], receipts["A1"])
	}
	e22Emit("correctness", map[string]interface{}{"pair_slots": n, "fresh_instances_only": true, "phase": os.Getenv("E22_PHASE"), "s1_checked": m.e22.validate, "table_function_identity": "not_tested", "exception_paths": "not_tested"})
	runtime.KeepAlive(initial)
}
