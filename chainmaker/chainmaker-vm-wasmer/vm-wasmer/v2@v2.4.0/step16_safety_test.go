//go:build step16

package wasmer

import (
	"bytes"
	logger2 "chainmaker.org/chainmaker/logger/v2"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	wasm "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"encoding/json"
	"os"
	"runtime"
	"testing"
)

func step16Wat(t *testing.T, wat string) []byte { b, e := wasm.Wat2Wasm(wat); s15Must(t, e); return b }
func TestStep16SafetyAndTableSynthetic(t *testing.T) {
	b := step16Wat(t, `(module (type $t (func (result i32))) (memory (export "memory") 1) (global $g (export "g") (mut i32) (i32.const 7))
 (func $a (type $t) i32.const 11) (func $b (type $t) i32.const 22) (table (export "table") 2 funcref) (elem (i32.const 0) $a $b)
 (func (export "peek") (param i32) (result i32) local.get 0 call_indirect (type $t))
 (func (export "clear") i32.const 0 ref.null func table.set 0) (data (i32.const 8) "hello"))`)
	c := &commonPb.Contract{Name: "safety", Version: "1"}
	plan, e := prepareStaticMemory(b, c, "test")
	s15Must(t, e)
	if !bytes.Equal(plan.Image[8:13], []byte("hello")) {
		t.Fatal("template bytes")
	}
	other, e := prepareStaticMemory(b, &commonPb.Contract{Name: "safety", Version: "2"}, "test")
	s15Must(t, e)
	if plan.Key == other.Key {
		t.Fatal("version key alias")
	}
	other, e = prepareStaticMemory(b, c, "different-config")
	s15Must(t, e)
	if plan.Key == other.Key {
		t.Fatal("configuration key alias")
	}
	changed := bytes.Replace(b, []byte("hello"), []byte("jello"), 1)
	sourcePlan, e := prepareStaticMemory(changed, c, "test")
	s15Must(t, e)
	if sourcePlan.Key == plan.Key {
		t.Fatal("source hash key alias")
	}
	store := wasm.NewStore(wasm.NewEngine())
	defer store.Close()
	original, e := wasm.NewModule(store, b, nil)
	s15Must(t, e)
	defer original.Close()
	optimized, e := wasm.NewModule(store, plan.NoData, nil)
	s15Must(t, e)
	defer optimized.Close()
	plan.Module = optimized
	makeInstance := func(module *wasm.Module, copyData bool) *wasm.Instance {
		i, e := wasm.NewInstance(module, wasm.NewImportObject())
		s15Must(t, e)
		if copyData {
			s15Must(t, plan.restore(module, i, b, c, "test"))
		}
		return i
	}
	base := makeInstance(original, false)
	defer base.Close()
	a := makeInstance(optimized, true)
	defer a.Close()
	peer := makeInstance(optimized, true)
	defer peer.Close()
	peek := func(i *wasm.Instance, n int32) (interface{}, error) {
		f, e := i.Exports.GetRawFunction("peek")
		s15Must(t, e)
		defer f.Close()
		return f.Call(n)
	}
	for _, i := range []*wasm.Instance{base, a, peer} {
		v, e := peek(i, 0)
		s15Must(t, e)
		if v.(int32) != 11 {
			t.Fatal(v)
		}
		v, e = peek(i, 1)
		s15Must(t, e)
		if v.(int32) != 22 {
			t.Fatal(v)
		}
	}
	f, e := a.Exports.GetRawFunction("clear")
	s15Must(t, e)
	_, e = f.Call()
	s15Must(t, e)
	f.Close()
	if _, e = peek(a, 0); e == nil {
		t.Fatal("cleared element should trap")
	}
	v, e := peek(peer, 0)
	s15Must(t, e)
	if v.(int32) != 11 {
		t.Fatal("table write leaked to peer")
	}
	ma, e := a.Exports.GetMemory("memory")
	s15Must(t, e)
	mb, e := peer.Exports.GetMemory("memory")
	s15Must(t, e)
	ma.Data()[8] = 'X'
	if string(mb.Data()[8:13]) != "hello" || string(plan.Image[8:13]) != "hello" {
		t.Fatal("writable memory/template alias")
	}
	if e = plan.restore(original, base, b, c, "test"); e == nil {
		t.Fatal("foreign module accepted")
	}
	if e = plan.restore(optimized, peer, b, &commonPb.Contract{Name: "other", Version: "1"}, "test"); e == nil {
		t.Fatal("foreign contract key accepted")
	}
	t.Log("PASS: synthetic complete element values and table mutation isolation; memory/template isolation; module/config/version key guards")
}
func TestStep16UnsupportedAndFallback(t *testing.T) {
	cases := map[string]string{
		"auto-start":    `(module (memory (export "memory") 1) (func $s) (start $s))`,
		"passive":       `(module (memory (export "memory") 1) (data "x"))`,
		"import-memory": `(module (import "env" "memory" (memory 1)) (export "memory" (memory 0)))`,
		"global-offset": `(module (import "env" "g" (global i32)) (memory (export "memory") 1) (data (global.get 0) "x"))`,
		"data-count":    `(module (memory (export "memory") 1) (data "x") (func i32.const 0 i32.const 0 i32.const 1 memory.init 0))`,
	}
	for name, wat := range cases {
		t.Run(name, func(t *testing.T) {
			b := step16Wat(t, wat)
			if _, e := prepareStaticMemory(b, &commonPb.Contract{Name: "fallback", Version: "1"}, "test"); e == nil {
				t.Fatal("unsupported module accepted")
			}
		})
	}
	// Actual constructor fallback: automatic start must see the original active data.
	t.Setenv("CM_STEP16_SERIALIZED_MODULE", "")
	t.Setenv("CM_STATIC_MEMORY_COPY", "1")
	t.Setenv("CM_FRESH_INVOKE", "1")
	b := step16Wat(t, `(module (import "wasi_snapshot_preview1" "fd_close" (func (param i32) (result i32))) (memory (export "memory") 1) (global $g (export "g") (mut i32) (i32.const 7)) (data (i32.const 8) "z") (func $s i32.const 8 i32.load8_u global.set $g) (start $s))`)
	p, e := newVmPool(&commonPb.Contract{Name: "fallback", Version: "1"}, b, logger2.GetLogger("step16_safety"))
	s15Must(t, e)
	defer p.store.Close()
	defer p.module.Close()
	if p.staticPlan != nil || p.staticFallback == "" {
		t.Fatal("did not fall back")
	}
	i, e := p.NewInstance()
	s15Must(t, e)
	defer i.wasmInstance.Close()
	g, e := i.wasmInstance.Exports.GetGlobal("g")
	s15Must(t, e)
	v, e := g.Get()
	s15Must(t, e)
	if v.(int32) != 122 {
		t.Fatal("fallback automatic start/data semantics broken")
	}
}
func TestStep16TemplateCost(t *testing.T) {
	s := step16Spec(t)
	b, e := os.ReadFile(s.Paths["original"])
	s15Must(t, e)
	_, config := step16TestConfig()
	out, e := os.OpenFile(os.Getenv("S16_OUT"), os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
	s15Must(t, e)
	defer out.Close()
	enc := json.NewEncoder(out)
	contract := &commonPb.Contract{Name: s.Label, Version: "1.0.0"}
	for i := 0; i < 30; i++ {
		plan, e := prepareStaticMemory(b, contract, config)
		s15Must(t, e)
		s15Must(t, enc.Encode(map[string]interface{}{"kind": "template_sample", "label": s.Label, "sample": i, "precompute_ns": plan.PrecomputeNS, "image_bytes": len(plan.Image), "ranges_capacity_bytes": cap(plan.Ranges) * 16, "temporary_nodata_wasm_bytes": len(plan.NoData)}))
	}
	runtime.GC()
	var before, after runtime.MemStats
	runtime.ReadMemStats(&before)
	retained, e := prepareStaticMemory(b, contract, config)
	s15Must(t, e)
	retained.NoData = nil
	runtime.GC()
	runtime.ReadMemStats(&after)
	s15Must(t, enc.Encode(map[string]interface{}{"kind": "template_memory", "label": s.Label, "logical_retained_bytes": cap(retained.Image) + cap(retained.Ranges)*16, "go_heap_delta_bytes": int64(after.HeapAlloc) - int64(before.HeapAlloc), "excludes": "native module memory and original WASM already retained by baseline"}))
	runtime.KeepAlive(retained)
}
