package wasmer

import (
	protocol "chainmaker.org/chainmaker/protocol/v2"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"runtime"
	"strconv"
	"strings"
	"testing"
	"time"
)

func step34Business(t *testing.T) {
	if !e22Enabled || !e27Enabled {
		t.Fatal("explicit flags required")
	}

	var variants map[string]e25Artifact
	data, e := os.ReadFile(os.Getenv("E25_VARIANTS"))
	if e != nil || json.Unmarshal(data, &variants) != nil {
		t.Fatal("manifest")
	}
	name := os.Getenv("E22_CONTRACT")
	method := os.Getenv("E22_METHOD")
	groups := strings.Split(os.Getenv("E32_ORDER"), ",")
	if len(groups) != 4 {
		t.Fatal("quadruple order required")
	}
	if g := os.Getenv("E32_SINGLE"); g != "" {
		groups = strings.Split(g, ",")
		if len(groups) > 2 || (name == "exchange" && len(groups) > 1) {
			t.Fatal("process target-call budget")
		}
	}
	f := s21cPrepare(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
	defer f.close()
	m := f.instances
	m.policy = "R1"
	names := []string{name}
	if name == "exchange" {
		names = []string{"identity", "erc721", "exchange"}
		if os.Getenv("E32_ALIGNMENT") == "1" {
			names = []string{"identity", "exchange"}
		}
	}
	raws := map[string]map[string][]byte{}
	for _, g := range groups {
		raws[g] = map[string][]byte{}
		for _, cname := range names {
			a, ok := variants[cname+"-"+g]
			if !ok {
				t.Fatal("variant missing")
			}
			b, err := os.ReadFile(a.Path)
			if err != nil {
				t.Fatal(err)
			}
			raws[g][cname] = b
			c, _ := f.snapshot.store.GetContractByName(cname)
			if err = m.e25Prepare(c, b, g, a); err != nil {
				t.Fatal(err)
			}
		}
	}
	if os.Getenv("E32_ALIGNMENT") == "1" {
		m.e22.variant = groups[0]
		for _, cname := range names {
			c, _ := f.snapshot.store.GetContractByName(cname)
			m.e22.invokeBegin = time.Now()
			b, err := m.makeE22(c, raws[groups[0]][cname])
			if err != nil {
				t.Fatal(err)
			}
			restore := b.scope.Activate()
			fn, err := b.instance.Exports.GetRawFunction("Step18Read")
			if err != nil {
				t.Fatal(err)
			}
			values := []interface{}{}
			for _, idx := range []int32{4, 5, 6} {
				v, err := fn.Call(idx)
				if err != nil {
					t.Fatal(err)
				}
				values = append(values, v)
			}
			fn.Close()
			restore()
			e22Emit("alignment", map[string]interface{}{"contract": cname, "group": groups[0], "first_reserve_bloc": values[0], "alignment_distance": values[1], "alignment": values[2]})
			if fmt.Sprint(values[0]) != "4194304" || fmt.Sprint(values[1]) != "0" || fmt.Sprint(values[2]) != "4194304" {
				t.Fatal("A alignment not proven")
			}
			if err = m.closeE22(b); err != nil {
				t.Fatal(err)
			}
		}
		return
	}
	empty := e22Clone(f.snapshot.ledger)
	var initial map[string]map[string][]byte
	initialHash := ""
	for _, g := range groups {
		m.e22.variant = g
		e27Group = g
		e27Role = g
		e27Pair = -1
		f.snapshot.ledger = e22Clone(empty)
		for _, cname := range names {
			f.snapshot.store.code[cname] = raws[g][cname]
			args := map[string]string{}
			if cname == "erc721" {
				args = map[string]string{"name": "huanletoken", "symbol": "hlt", "tokenURI": "https://chainmaker.org.cn"}
			}
			r := f.run("setup-"+cname+"-"+g, cname, "init_contract", "step32-init-"+cname, args)
			if r.Result.Code != 0 || r.Status != 0 {
				t.Fatalf("init failed %+v", r.Result)
			}
		}
		h := f.snapshot.hash()
		if initialHash != "" && initialHash != h {
			t.Fatal("initial state mismatch")
		}
		initialHash = h
		initial = e22Clone(f.snapshot.ledger)
	}
	params := map[string]string{}
	switch name {
	case "fact":
		params = map[string]string{"file_hash": "005521f27d745a04999c6d09f559764f9c44376a", "file_name": "aoteman.jpg", "time": "1792827547"}
	case "erc721":
		params = map[string]string{"to": "8acfaca5eeec9f6f7c23c4ffac969b86f27799b0", "tokenId": "1", "metadata": "http://chainmaker.org.cn/"}
	case "exchange":
		params = map[string]string{"from": "8acfaca5eeec9f6f7c23c4ffac969b86f27799b0", "to": "818fac1ac51525aeedf619a9a339b95854930159", "tokenId": "1", "metadata": "http://chainmaker.org.cn/"}
	}
	receipts := map[string]*s21cReceipt{}
	block, _ := strconv.Atoi(os.Getenv("E32_BLOCK"))
	m.e22.validate = os.Getenv("E22_PHASE") == "preflight"
	for pos, g := range groups {
		m.e22.variant = g
		e27Group = g
		e27Role = g
		e27Pair = block
		for _, cname := range names {
			f.snapshot.store.code[cname] = raws[g][cname]
		}
		f.snapshot.ledger = e22Clone(initial)
		exception := os.Getenv("E32_EXCEPTION")
		if exception=="missing" {method="step34_missing_method"}
 if exception == "empty" {
			params = map[string]string{}
		}
		if exception == "duplicate" {
			f.snapshot.ledger["erc721"][string(protocol.GetKeyStr("tokenIds", "1"))] = []byte(params["from"])
		}
		before := e27Host()
		s34Armed = true
		r := f.run("target-"+g, name, method, "step32-"+os.Getenv("E32_CASE")+"-fixed", params)
		s34Armed = false
		if os.Getenv("E34_FAULT") != "" {
			if r.Result.Code == 0 || r.BeforeHash != r.AfterHash {
				t.Fatal("fault rollback failed")
			}
			s34Emit("fault_rollback", map[string]interface{}{"stage": os.Getenv("E34_FAULT"), "gas": r.Result.GasUsed, "ledger_unchanged": true})
			recovery := f.run("recovery-"+g, name, method, "step32-"+os.Getenv("E32_CASE")+"-fixed", params)
			if recovery.Result.Code != 0 || recovery.Status != 0 {
				t.Fatal("recovery after injected failure failed")
			}
			e22Expected(t, f, name, params, recovery)
			continue
		}
		receipts[g] = r
		if exception != "" {
			if r.Result.Code == 0 || r.BeforeHash != r.AfterHash {
				t.Fatal("expected failure rollback not observed")
			}
			e22Emit("exception", map[string]interface{}{"kind": exception, "group": g, "calls": len(r.Calls), "gas": r.Result.GasUsed, "unchanged_ledger": r.BeforeHash == r.AfterHash})
		} else {
			if r.Result.Code != 0 || r.Status != 0 {
				t.Fatalf("business failed %+v", r.Result)
			}
			if method == "hashCal" {
				h := sha256.Sum256([]byte("ChainMaker Performance Test"))
				if string(r.Result.Result) != "success hashCal "+hex.EncodeToString(h[:]) {
					t.Fatalf("hash mismatch %s", r.Result.Result)
				}
			} else if method == "normalCal" {
				if string(r.Result.Result) != "success normalCal: 666" {
					t.Fatal("normal result")
				}
			} else {
				e22Expected(t, f, name, params, r)
			}
		}
		dEvent("boundary", map[string]interface{}{"group": g, "pair": block, "position": pos, "host_before": before, "host_after": e27Host(), "gas": r.Result.GasUsed, "before_hash": r.BeforeHash, "after_hash": r.AfterHash})
	}
	for i := 1; i < len(groups); i++ {
		e22Assert(t, receipts[groups[0]], receipts[groups[i]])
	}
	e22Emit("correctness", map[string]interface{}{"groups": groups, "block": block, "s1_checked": m.e22.validate, "fresh_instances_only": true, "table_function_identity": "not_tested", "exception": os.Getenv("E32_EXCEPTION")})
}

func TestStep34Serial(t *testing.T) {
	o, e := NewSafeFreshOwner(1, nil)
	if e != nil {
		t.Fatal(e)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 35*time.Second)
	defer cancel()
	e = o.Do(ctx, func() error { step34Business(t); runtime.GC(); return nil })
	if e != nil {
		t.Error(e)
	}
	if e = o.Stop(ctx); e != nil {
		t.Error(e)
	}
	if w.ManagedStoresCreated != w.ManagedStoresClosed || w.ManagedInstancesCreated != w.ManagedInstancesClosed {
		t.Fatal("native lifecycle allocation imbalance")
	}
}
