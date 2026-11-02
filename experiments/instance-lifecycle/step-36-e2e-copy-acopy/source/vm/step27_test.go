package wasmer

import (
	"encoding/json"
	"fmt"
	"os"
	"runtime"
	
	"strconv"
	
	"testing"
)

func TestStep27Serial(t *testing.T) {
	if !e22Enabled || !e27Enabled {
		t.Fatal("explicit flags required")
	}
	defer dOwner(t)()
	n, e := strconv.Atoi(os.Getenv("E22_PAIRS"))
	if e != nil || n < 1 || n > 2 {
		t.Fatal("1..2 paired slots only")
	}
	var variants map[string]e25Artifact
	data, e := os.ReadFile(os.Getenv("E25_VARIANTS"))
	if e != nil || json.Unmarshal(data, &variants) != nil {
		t.Fatal("missing variants")
	}
	family := os.Getenv("E27_FAMILY")
	groups := []string{os.Getenv("E25_LEFT"), os.Getenv("E25_RIGHT")}
	roles := []string{"A0", "A1"}
	raw := map[string][]byte{}
	ar := map[string]e25Artifact{}
	f := s21cPrepare(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
	defer f.close()
	m := f.instances
	c, _ := f.snapshot.store.GetContractByName("compute")
	for i, r := range roles {
		a, ok := variants[family+"-"+groups[i]]
		if !ok {
			t.Fatal("unsupported family/group")
		}
		b, e := os.ReadFile(a.Path)
		if e != nil {
			t.Fatal(e)
		}
		raw[r] = b
		ar[r] = a
	}
	shared := groups[0] == "R0" && groups[1] == "R1"
	order := []string{"A0", "A1"}
	if os.Getenv("E24_MODULE_FIRST") == "A1" {
		order = []string{"A1", "A0"}
	}
	if shared {
		if ar["A0"].SHA != ar["A1"].SHA || ar["A0"].Copy || ar["A1"].Copy {
			t.Fatal("R0/R1 must share original module")
		}
		if e = m.e25Prepare(c, raw["A0"], "A0", ar["A0"]); e != nil {
			t.Fatal(e)
		}
	} else {
		for _, r := range order {
			if e = m.e25Prepare(c, raw[r], r, ar[r]); e != nil {
				t.Fatal(e)
			}
		}
	}
	m.e22.validate = os.Getenv("E22_PHASE") == "preflight"
	start := e22Clone(f.snapshot.ledger)
	var initialHash string
	setup := order
	if shared {
		setup = []string{"A0"}
	}
	for _, r := range setup {
		m.e22.variant = r
		e27Group = ar[r].Group
		e27Role = r
		e27Pair = -1
		m.policy = "R1"
		if shared {
			m.policy = "R0"
		}
		f.snapshot.store.code["compute"] = raw[r]
		f.snapshot.ledger = e22Clone(start)
		res := f.run("setup-compute-"+r, "compute", "init_contract", "step27-init-compute", map[string]string{})
		if res.Result.Code != 0 || res.Status != 0 {
			t.Fatal("init failed")
		}
		h := f.snapshot.hash()
		if initialHash != "" && h != initialHash {
			t.Fatal("init ledger mismatch")
		}
		initialHash = h
	}
	initial := e22Clone(f.snapshot.ledger)
	if os.Getenv("E27_WARM") == "1" {
		if !shared || os.Getenv("E27_DIAG") != "1" {
			t.Fatal("warm only explicit separate shared-Store diagnostic")
		}
		e27Group = "R0"
		e27Role = "A0"
		e27Pair = -2
		m.e22.variant = "A0"
		m.policy = "R0"
		f.snapshot.ledger = e22Clone(initial)
		res := f.run("diagnostic-warm-R0", "compute", "normalCal", "step27-normalCal-fixed", map[string]string{})
		if res.Result.Code != 0 {
			t.Fatal("warm failed")
		}
	}
	for i := 0; i < n; i++ {
		first, _ := strconv.Atoi(os.Getenv("E25_FIRST"))
		callOrder := []string{"A0", "A1"}
		if (i+first)%2 != 0 {
			callOrder = []string{"A1", "A0"}
		}
		results := map[string]*s21cReceipt{}
		for _, r := range callOrder {
			group := ar[r].Group
			e27Group = group
			e27Role = r
			e27Pair = i
			m.policy = "R1"
			if group == "R0" {
				m.policy = "R0"
			}
			m.e22.variant = r
			if shared {
				m.e22.variant = "A0"
			}
			f.snapshot.store.code["compute"] = raw[r]
			f.snapshot.ledger = e22Clone(initial)
			before := e27Host()
			res := f.run(fmt.Sprintf("pair-%03d-%s", i, r), "compute", "normalCal", "step27-normalCal-fixed", map[string]string{})
			after := e27Host()
			results[r] = res
			if res.Result.Code != 0 || res.Status != 0 || string(res.Result.Result) != "success normalCal: 666" {
				t.Fatalf("normal failed %+v", res.Result)
			}
			dEvent("boundary", map[string]interface{}{"group": group, "role": r, "pair": i, "family": family, "host_before": before, "host_after": after, "shared_R0_R1_store_module": shared})
		}
		e22Assert(t, results["A0"], results["A1"])
	}
	e22Emit("correctness", map[string]interface{}{"pairs": n, "family": family, "shared_R0_R1_store_module": shared, "R0_runtime_state_preserved": true, "fresh_R1_C1_C2_only": true, "table_identity": "not_tested", "guest_gc": "not_observed"})
	runtime.KeepAlive(initial)
}
