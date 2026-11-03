package wasmer

import (
	"bytes"
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"context"
	"sync"
	"testing"
)

func TestStep39Artifact(t *testing.T) {
	var g e39Registry
	var costs []e39Cost
	c := &common.Contract{Name: "same", Version: "1"}
	raw := []byte{0, 97, 115, 109, 1}
	a, e := g.acquire("chain", "config", c, raw, &costs)
	if e != nil {
		t.Fatal(e)
	}
	want := nodeSHA(raw)
	raw[0] = 99
	if a.raw[0] != 0 || a.digest != want || nodeSHA(a.raw) != a.digest {
		t.Fatal("mutable alias")
	}
	// Same label with different content must replace registry, old snapshot remains valid.
	b, e := g.acquire("chain", "config", c, raw, &costs)
	if e != nil || a == b || b.digest == a.digest || a.raw[0] != 0 {
		t.Fatal("content invalidation")
	}
	c2 := *c
	c2.Version = "2"
	v, _ := g.acquire("chain", "config", &c2, raw, &costs)
	c2.Name = "other"
	n, _ := g.acquire("chain", "config", &c2, raw, &costs)
	ch, _ := g.acquire("otherchain", "config", c, raw, &costs)
	cfg, _ := g.acquire("chain", "otherconfig", c, raw, &costs)
	if v == b || n == v || ch == b || cfg == b {
		t.Fatal("identity isolation")
	}
	var wg sync.WaitGroup
	for i := 0; i < 8; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			var local []e39Cost
			for j := 0; j < 20; j++ {
				x, err := g.acquire("chain", "config", c, raw, &local)
				if err != nil || x != b || !bytes.Equal(x.raw, raw) || nodeSHA(x.raw) != x.digest {
					t.Error("concurrent immutable read")
				}
			}
		}()
	}
	wg.Wait()
	if len(g.entries) != 5 {
		t.Fatalf("registry identities %d", len(g.entries))
	}
	e39Emit(map[string]interface{}{"event": "artifact_identity_test", "passed": true, "concurrent_readers": 8, "reads_per_reader": 20, "snapshot_hash": want, "content_change_replaced": true, "version_chain_config_contract_isolated": true})
}

// No native execution is reached on identity failure.
type e39Tx struct{ protocol.TxSimContext }

func (e39Tx) GetTx() *common.Transaction {
	return &common.Transaction{Payload: &common.Payload{TxId: "e39-reject"}}
}
func TestStep39Reject(t *testing.T) {
	c := &common.Contract{Name: "reject", Version: "1"}
	m := &nodeFreshManager{chain: "c", config: "cfg"}
	r, e := m.runtime(c, []byte{0, 97, 115, 109, 1})
	if e != nil {
		t.Fatal(e)
	}
	result, _ := r.Invoke(c, "unused", []byte{0, 97, 115, 109, 2}, nil, e39Tx{}, 0)
	if result.Code == 0 || result.Message != "runtime contract/hash mismatch" {
		t.Fatalf("mismatch accepted: %+v", result)
	}
	other := *c
	other.Version = "2"
	result, _ = r.Invoke(&other, "unused", []byte{0, 97, 115, 109, 1}, nil, e39Tx{}, 0)
	if result.Code == 0 {
		t.Fatal("version mismatch")
	}
	e39Emit(map[string]interface{}{"event": "runtime_reject_test", "passed": true, "mode": e39Mode})
}
func TestStep39ModuleIdentity(t *testing.T) {
	m, e := newNodeFreshManager("e39-identity")
	if e != nil {
		t.Fatal(e)
	}
	defer func() {
		if err := m.owner.Stop(context.Background()); err != nil {
			t.Error(err)
		}
	}()
	c := &common.Contract{Name: "upgrade", Version: "1"}
	raw1, e := w.Wat2Wasm(`(module (memory (export "memory") 1) (data (i32.const 0) "first"))`)
	if e != nil {
		t.Fatal(e)
	}
	raw2, e := w.Wat2Wasm(`(module (memory (export "memory") 1) (data (i32.const 0) "second"))`)
	if e != nil {
		t.Fatal(e)
	}
	get := func(raw []byte) *nodeFreshCache {
		rr, err := m.runtime(c, raw)
		if err != nil {
			t.Fatal(err)
		}
		var rec *nodeFreshCache
		err = m.owner.Do(context.Background(), func() error {
			nodeOwnerTID.Store(int64(syscallTID()))
			var er error
			rec, er = m.prepare(c, raw, rr.(*nodeFreshRuntime))
			return er
		})
		if err != nil {
			t.Fatal(err)
		}
		if rec.source != nodeSHA(raw) {
			t.Fatal("module digest mismatch")
		}
		return rec
	}
	a := get(raw1)
	b := get(raw2)
	again := get(raw1)
	if a == b || a != again || len(m.caches) != 2 {
		t.Fatal("module content invalidation or reuse")
	}
	if e = m.reset(); e != nil {
		t.Fatal(e)
	}
	if len(m.caches) != 0 {
		t.Fatal("reset module cache")
	}
	fresh := get(raw1)
	if fresh == a {
		t.Fatal("closed module reused")
	}
	e39Emit(map[string]interface{}{"event": "module_identity_test", "passed": true, "same_version_content_change": true, "old_content_cache_hit": true, "reset_recompiled": true})
}
