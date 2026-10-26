package wasmer

import (
	"chainmaker.org/chainmaker/logger/v2"
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"testing"
)

func eLedgerClone(x map[string]map[string][]byte) map[string]map[string][]byte {
	b, e := json.Marshal(x)
	if e != nil {
		panic(e)
	}
	var y map[string]map[string][]byte
	if e = json.Unmarshal(b, &y); e != nil {
		panic(e)
	}
	return y
}
func eSuccess(t *testing.T, r *s21cReceipt) {
	t.Helper()
	if r.Result.Code != 0 || r.Status != common.TxStatusCode_SUCCESS {
		t.Fatalf("actual business failed: %+v", r.Result)
	}
}
func eInputs(t *testing.T, name string) map[string]string {
	b, e := os.ReadFile(os.Getenv("E_INPUTS"))
	if e != nil {
		t.Fatal(e)
	}
	var all map[string]map[string]string
	if e = json.Unmarshal(b, &all); e != nil {
		t.Fatal(e)
	}
	return all[name]
}
func TestStep21EGas(t *testing.T) {
	defer dOwner(t)()
	n := dN(t)
	name := os.Getenv("D_METHOD")
	if name == "buyNow" {
		if n != 1 {
			t.Fatal("one root budget")
		}
		s21cPreparedScenario(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
		return
	}
	if name != "fact" && name != "erc721" {
		t.Fatal("unregistered case")
	}
	f := s21cPrepare(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
	defer f.close()
	args := map[string]string{}
	if name == "erc721" {
		args = map[string]string{"name": "huanletoken", "symbol": "hlt", "tokenURI": "https://chainmaker.org.cn"}
	}
	eSuccess(t, f.run("init-"+name, name, "init_contract", "step21e-init-"+name, args))
	initial := eLedgerClone(f.snapshot.ledger)
	input := eInputs(t, name)
	method := "mint"
	if name == "fact" {
		method = "saveAndFindByFileHash"
	}
	expectedAfter := ""
	expectedResult := ""
	for i := 0; i < n; i++ {
		f.snapshot.ledger = eLedgerClone(initial)
		r := f.run(fmt.Sprintf("equal-%03d", i), name, method, "step21e-equal-000", input)
		eSuccess(t, r)
		if i == 0 {
			expectedAfter = r.AfterHash
			expectedResult = string(r.Result.Result)
		} else if r.AfterHash != expectedAfter || string(r.Result.Result) != expectedResult {
			t.Fatal("equivalent-state business changed")
		}
		b, _ := json.Marshal(input)
		h := sha256.Sum256(b)
		eEmit(map[string]interface{}{"event": "equivalent_state", "index": i, "policy": f.instances.policy, "contract": name, "input_sha256": hex.EncodeToString(h[:]), "before_hash": r.BeforeHash, "after_hash": r.AfterHash, "gas": r.Result.GasUsed})
	}
}
func TestStep21ENormal(t *testing.T) {
	defer dOwner(t)()
	n := dN(t)
	order := os.Getenv("E_ORDER")
	if order != "ABBAAB" && order != "BAABBA" {
		t.Fatal("pre-registered order required")
	}
	if n == 1 {
		if order == "ABBAAB" {
			order = "AB"
		} else {
			order = "BA"
		}
	}
	f := s21cPrepare(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
	defer f.close()
	m := f.instances
	c, _ := f.snapshot.store.GetContractByName("compute")
	code := f.snapshot.store.code["compute"]
	r0, e := m.makeBundle(c, code)
	if e != nil {
		t.Fatal(e)
	}
	m.cache["compute"] = r0
	m.prepared = map[string][]*dBundle{"compute": {}}
	for i := 0; i < n; i++ {
		b, err := m.makeBundle(c, code)
		if err != nil {
			t.Fatal(err)
		}
		m.prepared["compute"] = append(m.prepared["compute"], b)
	}
	m.policy = "R0"
	r := f.run("warmup-r0", "compute", "normalCal", "step21e-normal-warm", map[string]string{})
	eSuccess(t, r)
	eEmit(map[string]interface{}{"event": "normal_measure_start", "order": order, "fresh_count": n, "prebuilt_only": true, "warmup_r0": 1, "guest_gc": "not_observed"})
	for i, mode := range order {
		m.policy = "R0"
		if mode == 'B' {
			m.policy = "R1"
		}
		r = f.run(fmt.Sprintf("measure-%02d-%s", i, m.policy), "compute", "normalCal", "step21e-normal-measure", map[string]string{})
		eSuccess(t, r)
		if r.Result.GasUsed != 100000072 || string(r.Result.Result) != "success normalCal: 666" {
			t.Fatal("normal work/gas mismatch")
		}
	}
	if len(m.prepared["compute"]) != 0 {
		t.Fatal("unconsumed fresh queue")
	}
}

// Capability check only: trusted self-produced serialized code, no optimization benchmark.
func TestStep21EModule(t *testing.T) {
	defer dOwner(t)()
	scope := w.ManagedOpen("trusted-module-capability")
	defer func() {
		if e := scope.Close(); e != nil {
			t.Error(e)
		}
	}()
	c := &common.Contract{Name: "module-capability", Version: "1"}
	store, module, e := dCompile(c, []byte(`(module (func (export "answer") (result i32) i32.const 42))`), logger.GetLogger("step21e-module"))
	if e != nil {
		t.Fatal(e)
	}
	call := func(mod *w.Module) {
		inst, err := w.NewInstance(mod, w.NewImportObject())
		if err != nil {
			t.Fatal(err)
		}
		fn, err := inst.Exports.GetRawFunction("answer")
		if err != nil {
			t.Fatal(err)
		}
		result, err := fn.Call()
		if err != nil || result != int32(42) {
			t.Fatalf("actual answer mismatch %v %v", result, err)
		}
		fn.Close()
	}
	call(module)
	call(module)
	blob, e := module.Serialize()
	if e != nil || len(blob) == 0 {
		t.Fatalf("serialize %v", e)
	}
	target := w.NewStore(store.Engine)
	if target.Inner() == store.Inner() {
		t.Fatal("target Store is not distinct")
	}
	decoded, e := w.DeserializeModule(target, blob)
	if e != nil {
		t.Fatal(e)
	}
	call(decoded)
	eEmit(map[string]interface{}{"event": "module_capability", "same_module_serial_instances": 2, "deserialized_target_store_instance": 1, "actual_result": 42, "serialized_bytes": len(blob), "distinct_store": true, "trusted_self_generated_artifact": true, "not_a_performance_benchmark": true})
}
