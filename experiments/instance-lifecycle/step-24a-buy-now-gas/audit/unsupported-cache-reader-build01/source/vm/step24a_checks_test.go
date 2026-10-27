package wasmer

import (
	"chainmaker.org/chainmaker/logger/v2"
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"testing"
	"time"
)

func (m *dManager) a24Prepare(c *common.Contract, raw []byte) error {
	begin := time.Now()
	scope := w.ManagedOpen("original-module-" + c.Name)
	store, module, e := dCompile(c, raw, logger.GetLogger("step24a"))
	if e != nil {
		scope.Close()
		return e
	}
	module.Imports()
	module.Exports()
	sha := staticSHA(raw)
	key := staticSHA([]byte(c.Name + "\x00" + c.Version + "\x00" + sha + "\x00" + os.Getenv("E22_CONFIG_SHA")))
	plan := &staticMemoryPlan{SourceSHA: sha, ConfigID: os.Getenv("E22_CONFIG_SHA"), Key: key}
	m.e22.cache[c.Name+"A0"] = &e22Cache{scope: scope, store: store, module: module, plan: plan, key: key + "/A0", variant: "A0"}
	m.e22.order = append(m.e22.order, c.Name+"A0")
	scope.Suspend()
	eEmit(map[string]interface{}{"event": "original_module_prepared", "contract": c.Name, "wasm_sha": sha, "prepare_ns": time.Since(begin).Nanoseconds(), "cache_key": key, "store_id": fmt.Sprintf("%p", store.Inner()), "module_id": fmt.Sprintf("%p", module), "copy_enabled": false})
	return nil
}
func TestStep24AGas(t *testing.T) {
	mode := os.Getenv("A24_MODE")
	if mode != "R0" && mode != "R1" && !a24ReservedMode() {
		t.Fatal("unregistered mode")
	}
	defer dOwner(t)()
	f := s21cPrepare(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
	defer f.close()
	m := f.instances
	for _, n := range []string{"identity", "erc721", "exchange"} {
		c, _ := f.snapshot.store.GetContractByName(n)
		code, _ := f.snapshot.store.GetContractBytecode(n)
		if e := m.a24Prepare(c, code); e != nil {
			t.Fatal(e)
		}
	}
	m.e22.variant = "A0"
	m.e22.validate = false
	for _, n := range []string{"identity", "erc721", "exchange"} {
		args := map[string]string{}
		if n == "erc721" {
			args = map[string]string{"name": "huanletoken", "symbol": "hlt", "tokenURI": "https://chainmaker.org.cn"}
		}
		a23LedgerBefore = f.snapshot.hash()
		r := f.run("init-"+n, n, "init_contract", "step21c-init-"+n, args)
		if r.Result.Code != 0 {
			t.Fatal("init failed")
		}
	}
	initial := e22Clone(f.snapshot.ledger)
	var in struct {
		Tx     string            `json:"root_tx_id"`
		Input  map[string]string `json:"root_input"`
		Before string            `json:"expected_initial_hash"`
		After  string            `json:"expected_final_hash"`
	}
	b, e := os.ReadFile(os.Getenv("E23_INPUTS"))
	if e != nil || json.Unmarshal(b, &in) != nil {
		t.Fatal("missing fixed inputs")
	}
	if f.snapshot.hash() != in.Before {
		t.Fatal("initial ledger mismatch")
	}
	if a24ReservedMode() {
		m.policy = "R0"
		if mode == "S0" {
			c, _ := f.snapshot.store.GetContractByName("erc721")
			candidate, err := m.makeBundle(c, f.snapshot.store.code["erc721"])
			if err != nil {
				t.Fatal(err)
			}
			m.cache["erc721"] = candidate
		} else {
			method := "testgasJSONMarshal"
			if mode == "U" {
				method = "testgasJSONUnmarshal"
			}
			a23LedgerBefore = f.snapshot.hash()
			warm := f.run("diagnostic-warm", "erc721", method, "step24a-warm-"+mode, map[string]string{})
			if warm.Result.Code != 0 || warm.Status != common.TxStatusCode_SUCCESS {
				t.Fatal("real warm export failed")
			}
			eEmit(map[string]interface{}{"event": "warm_record", "mode": mode, "gas": warm.Result.GasUsed, "method": method, "ledger_restore_only": true, "runtime_state_preserved": true})
		}
		candidate := m.cache["erc721"]
		restore := candidate.scope.Activate()
		a24Snapshot(candidate.instance, "reserved-before-root", &a23Call{CallID: -1, Contract: "erc721", Method: "reserved", TxID: in.Tx, InstanceID: candidate.id, UsesBefore: candidate.used})
		restore()
		f.snapshot.ledger = e22Clone(initial)
		m.policy = "R1"
	}
	a23LedgerBefore = f.snapshot.hash()
	if a23LedgerBefore != in.Before {
		t.Fatal("diagnostic ledger not equivalent")
	}
	r := f.run("target", "exchange", "buyNow", in.Tx, in.Input)
	if r.Result.Code != 0 || r.Status != common.TxStatusCode_SUCCESS || string(r.Result.Result) != "buyNow success" || r.BeforeHash != in.Before || r.AfterHash != in.After {
		t.Fatalf("real target failed %+v", r.Result)
	}
	expected := []string{"exchange/buyNow", "identity/addWriteList", "identity/isApprovedUser", "identity/isApprovedUser", "erc721/mint", "erc721/setApprovalForAll2", "erc721/transferFrom"}
	calls := append([]s21cCall(nil), r.Calls...)
	sort.Slice(calls, func(i, j int) bool { return calls[i].ID < calls[j].ID })
	if len(calls) != 7 {
		t.Fatal("wrong call graph")
	}
	for i, c := range calls {
		if c.ID != i || c.Contract+"/"+c.Method != expected[i] || c.Code != 0 || i > 0 && c.Depth != 1 {
			t.Fatal("actual callee failed")
		}
	}
	if len(a23Stack) != 0 || len(a23Calls) != 0 {
		t.Fatal("active observer stack")
	}
	dEvent("boundary", map[string]interface{}{"mode": mode, "gas": r.Result.GasUsed})
	eEmit(map[string]interface{}{"event": "root_checked", "mode": mode, "gas": r.Result.GasUsed, "before": r.BeforeHash, "after": r.AfterHash, "real_children": 6, "copy_enabled": false, "table_function_identity": "not_tested", "exception_paths": "not_tested"})
}
