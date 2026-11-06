package wasmer

import (
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"context"
	"errors"
	"fmt"
	"os"
	"runtime"
	"strings"
	"sync"
	"testing"
	"time"
)

// These fixtures execute in the real C API and in the production manager path.
// State checks trap if a previous request's Memory, Global or Table was reused.
func repairFixture(t *testing.T, extra string) []byte {
	t.Helper()
	text := fmt.Sprintf(`(module
 (type $number (func (result i32)))
 (memory (export "memory") 1)
 (global $state (mut i32) (i32.const 7))
 (global $gas (mut i64) (i64.const 0))
 (func $one (result i32) i32.const 11)
 (func $two (result i32) i32.const 22)
 (table 2 funcref) (elem (i32.const 0) $one $two)
 (func (export "runtime_type") (result i32) i32.const %d)
 (func (export "allocate") (param i32) (result i32) i32.const 1024)
 (func (export "deallocate") (param i32))
 (func (export "SetGas") (param i64) local.get 0 global.set $gas)
 (func (export "GetGas") (result i64) global.get $gas)
 (func (export "check")
  i32.const 0 i32.load i32.eqz if else unreachable end
  global.get $state i32.const 7 i32.eq if else unreachable end
  i32.const 0 call_indirect (type $number) i32.const 11 i32.eq if else unreachable end
  i32.const 0 i32.const 42 i32.store
  i32.const 99 global.set $state
  i32.const 0 ref.func $two table.set)
 (func (export "fail") unreachable)
 %s)`, int32(commonPb.RuntimeType_WASMER), extra)
	if imports, body, found := strings.Cut(extra, "END_IMPORTS:"); found {
		text = strings.Replace(text, extra, body, 1)
		text = strings.Replace(text, "(module", "(module "+imports, 1)
	}
	if strings.Contains(extra, ";; omit-memory") {
		text = strings.Replace(text, `(memory (export "memory") 1)`, `(memory 1)`, 1)
	}
	if strings.Contains(extra, ";; bad-deallocate") {
		text = strings.Replace(text, `(func (export "deallocate") (param i32))`, `(func (export "deallocate") (param i32) unreachable)`, 1)
	}
	b, e := w.Wat2Wasm(text)
	if e != nil {
		t.Fatal(e)
	}
	return b
}
func repairRuntime(t *testing.T, m *InstancesManager, c *commonPb.Contract, b []byte) protocol.RuntimeInstance {
	t.Helper()
	r, e := m.NewRuntimeInstance(nil, "", "", "", c, b, m.log)
	if e != nil {
		t.Fatal(e)
	}
	return r
}
func repairCall(r protocol.RuntimeInstance, c *commonPb.Contract, b []byte, method string) *commonPb.ContractResult {
	result, _ := r.Invoke(c, method, b, map[string][]byte{}, nil, 0)
	return result
}
func repairStats(t *testing.T, m *InstancesManager) (objects int, stores, closed, instances, instancesClosed, wasi, wasiClosed uint64) {
	t.Helper()
	o, e := m.nativeOwner()
	if e != nil {
		t.Fatal(e)
	}
	e = o.Do(context.Background(), func() error {
		if n := w.ManagedHostFunctionCount(); n != 0 {
			return fmt.Errorf("host callbacks remain: %d", n)
		}
		objects = w.ManagedCount()
		stores = w.ManagedStoresCreated
		closed = w.ManagedStoresClosed
		instances = w.ManagedInstancesCreated
		instancesClosed = w.ManagedInstancesClosed
		wasi = w.ManagedWasiCreated
		wasiClosed = w.ManagedWasiClosed
		return nil
	})
	if e != nil {
		t.Fatal(e)
	}
	return
}
func repairStop(t *testing.T, m *InstancesManager) {
	t.Helper()
	if e := m.StopVM(); e != nil {
		t.Error(e)
	}
}

func TestStoreRepairBusinessIsolationAndCache(t *testing.T) {
	m := NewInstancesManager("repair-isolation")
	defer repairStop(t, m)
	b := repairFixture(t, "")
	c := &commonPb.Contract{Name: "a", Version: "1"}
	d := &commonPb.Contract{Name: "b", Version: "1"}
	r := repairRuntime(t, m, c, b)
	other := repairRuntime(t, m, d, b)
	base, s0, c0, i0, ic0, _, _ := repairStats(t, m)
	for n := 0; n < 40; n++ {
		target := r
		contract := c
		if n%2 == 1 {
			target = other
			contract = d
		}
		result := repairCall(target, contract, b, "check")
		if result.Code != 0 {
			t.Fatalf("fresh %d: %+v", n, result)
		}
	}
	objects, s1, c1, i1, ic1, _, _ := repairStats(t, m)
	if objects != base || s1-s0 != 40 || c1-c0 != 40 || i1-i0 != 40 || ic1-ic0 != 40 {
		t.Fatalf("resources: objects %d -> %d stores %d/%d instances %d/%d", base, objects, s1-s0, c1-c0, i1-i0, ic1-ic0)
	}
	o, _ := m.nativeOwner()
	if e := o.Do(context.Background(), func() error {
		if len(m.caches) != 2 {
			return fmt.Errorf("cache entries %d", len(m.caches))
		}
		return nil
	}); e != nil {
		t.Fatal(e)
	}
	// The timing API cannot silently select the old shared-Store path.
	ri := r.(*RuntimeInstance)
	result, _, _, _, _, _ := ri.InvokeTime(c, "check", b, map[string][]byte{}, nil, 0)
	if result.Code != 0 {
		t.Fatal(result)
	}
	runtime.GC()
	if e := m.CloseRuntimeInstance(c.Name, c.Version); e != nil {
		t.Fatal(e)
	}
	if result = repairCall(r, c, b, "check"); result.Code != 0 {
		t.Fatal(result)
	}
}

func TestStoreRepairRollbackAndTraps(t *testing.T) {
	m := NewInstancesManager("repair-errors")
	defer repairStop(t, m)
	for _, tc := range []struct{ name, extra, method string }{
		{"call-trap", "", "fail"},
		{"instance-start-trap", "(func $bad unreachable) (start $bad)", "check"},
		{"wasi-start-trap", `(import "wasi_snapshot_preview1" "proc_exit" (func $exit (param i32))) END_IMPORTS: (func (export "_start") unreachable)`, "check"},
		{"wasi-init-error", `(import "wasi_snapshot_preview1" "proc_exit" (func $exit (param i32))) END_IMPORTS: (func (export "_start")) ;; omit-memory
 `, "check"},
		{"deallocate-trap", ";; bad-deallocate\n", "check"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			b := repairFixture(t, tc.extra)
			c := &commonPb.Contract{Name: tc.name, Version: "1"}
			r := repairRuntime(t, m, c, b)
			base, s0, c0, _, _, _, _ := repairStats(t, m)
			for n := 0; n < 3; n++ {
				result := repairCall(r, c, b, tc.method)
				if result.Code == 0 {
					t.Fatalf("trap accepted: %+v", result)
				}
			}
			objects, s1, c1, _, _, _, _ := repairStats(t, m)
			if objects != base || s1-s0 != c1-c0 {
				t.Fatalf("rollback objects %d/%d stores %d/%d", base, objects, s1-s0, c1-c0)
			}
		})
	}
	c := &commonPb.Contract{Name: "invalid", Version: "1"}
	before, _, _, _, _, _, _ := repairStats(t, m)
	if _, e := m.NewRuntimeInstance(nil, "", "", "", c, []byte{0, 97, 115, 109, 1, 0, 0, 0, 255, 0}, m.log); e == nil {
		t.Fatal("invalid module accepted")
	}
	after, _, _, _, _, _, _ := repairStats(t, m)
	if after != before {
		t.Fatalf("compile failure leaked %d -> %d", before, after)
	}
}

func TestStoreRepairNativeStoreAndHostImports(t *testing.T) {
	o, e := NewSafeFreshOwner(4, nil)
	if e != nil {
		t.Fatal(e)
	}
	defer func() {
		if e := o.Stop(context.Background()); e != nil {
			t.Error(e)
		}
	}()
	e = o.Do(context.Background(), func() (err error) {
		scope := w.ManagedOpen("native-isolation")
		defer func() { err = errors.Join(err, scope.Close()) }()
		engine := w.NewEngine()
		compile := w.NewStore(engine)
		module, e := w.NewModule(compile, []byte(`(module (import "host" "value" (func $host (result i32))) (func (export "run") (result i32) call $host))`), nil)
		if e != nil {
			return e
		}
		// Different wrapper pointers alone are insufficient: execute independent hosts.
		first := w.NewStore(engine)
		second := w.NewStore(engine)
		if first.Inner() == second.Inner() || first.Inner() == compile.Inner() {
			return errors.New("Store wrappers aliased")
		}
		for _, item := range []struct {
			store *w.Store
			value int32
		}{{first, 17}, {second, 29}} {
			imports := w.NewImportObject()
			value := item.value
			fn := w.NewFunction(item.store, w.NewFunctionType(w.NewValueTypes(), w.NewValueTypes(w.I32)), func([]w.Value) ([]w.Value, error) { return []w.Value{w.NewI32(value)}, nil })
			imports.Register("host", map[string]w.IntoExtern{"value": fn})
			wrong := first
			if item.store == first {
				wrong = second
			}
			if _, e = w.NewInstanceInStore(module, imports, wrong); e == nil {
				return errors.New("cross-Store import accepted")
			}
			inst, e := w.NewInstanceInStore(module, imports, item.store)
			if e != nil {
				return e
			}
			run, e := inst.Exports.GetRawFunction("run")
			if e != nil {
				return e
			}
			v, e := run.Call()
			if e != nil || v != value {
				return fmt.Errorf("host result %v, %v", v, e)
			}
			run.Close()
			inst.Close()
			inst.Close()
			rejected := false
			func() { defer func() { rejected = recover() != nil }(); run.Call() }()
			if !rejected {
				return errors.New("function callable after Close")
			}
			item.store.Close()
			item.store.Close()
		}
		// Missing imports fail before passing a malformed array to C.
		if _, e = w.NewInstanceInStore(module, w.NewImportObject(), compile); e == nil {
			return errors.New("missing import accepted")
		}
		return nil
	})
	if e != nil {
		t.Fatal(e)
	}
}

func TestStoreRepairConcurrentStop(t *testing.T) {
	m := NewInstancesManager("repair-concurrent")
	b := repairFixture(t, "")
	c := &commonPb.Contract{Name: "concurrent", Version: "1"}
	r := repairRuntime(t, m, c, b)
	var wg sync.WaitGroup
	start := make(chan struct{})
	fail := make(chan string, 16)
	for n := 0; n < 16; n++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			<-start
			result := repairCall(r, c, b, "check")
			if result.Code != 0 && result.Message != ErrOwnerClosed.Error() {
				fail <- result.Message
			}
		}()
	}
	close(start)
	var stops sync.WaitGroup
	for n := 0; n < 3; n++ {
		stops.Add(1)
		go func() {
			defer stops.Done()
			if e := m.StopVM(); e != nil {
				fail <- e.Error()
			}
		}()
	}
	wg.Wait()
	stops.Wait()
	close(fail)
	for e := range fail {
		t.Error(e)
	}
	if result := repairCall(r, c, b, "check"); result.Code == 0 {
		t.Fatal("invoke after Stop accepted")
	}
	// Shared owner allows different chain managers to stop independently.
	a := NewInstancesManager("chain-a")
	z := NewInstancesManager("chain-z")
	ra := repairRuntime(t, a, c, b)
	rz := repairRuntime(t, z, c, b)
	if result := repairCall(ra, c, b, "check"); result.Code != 0 {
		t.Fatal(result)
	}
	repairStop(t, a)
	if result := repairCall(rz, c, b, "check"); result.Code != 0 {
		t.Fatal(result)
	}
	repairStop(t, z)
}

func TestStoreRepairOwnerDrainAndCancel(t *testing.T) {
	o, e := NewSafeFreshOwner(2, nil)
	if e != nil {
		t.Fatal(e)
	}
	entered := make(chan struct{})
	release := make(chan struct{})
	reply := make(chan error, 1)
	ctx, cancel := context.WithCancel(context.Background())
	go func() { reply <- o.Do(ctx, func() error { close(entered); <-release; return nil }) }()
	<-entered
	cancel()
	select {
	case <-reply:
		t.Fatal("admitted call returned before native cleanup")
	case <-time.After(10 * time.Millisecond):
	}
	stopped := make(chan error, 1)
	go func() { stopped <- o.Stop(context.Background()) }()
	close(release)
	if e := <-reply; e != nil {
		t.Fatal(e)
	}
	if e := <-stopped; e != nil {
		t.Fatal(e)
	}
	if e := o.Stop(context.Background()); e != nil {
		t.Fatal(e)
	}
	if e := o.Do(context.Background(), func() error { return nil }); !errors.Is(e, ErrOwnerClosed) {
		t.Fatal(e)
	}
}

func TestStoreRepairRealGoContract(t *testing.T) {
	b, e := os.ReadFile("testdata/compute-go.wasm")
	if e != nil {
		t.Fatal(e)
	}
	m := NewInstancesManager(ChainId)
	defer repairStop(t, m)
	c := &commonPb.Contract{Name: "compute-test", Version: "1", RuntimeType: commonPb.RuntimeType_WASMER}
	r := repairRuntime(t, m, c, b)
	base, _, _, _, _, w0, wc0 := repairStats(t, m)
	for n := 0; n < 2; n++ {
		params := prepareFunc("compute-test", "bigNumCal")
		fillingBaseParams(params)
		tx := prepareTxSimContext(ChainId, BlockVersion, c.Name, "bigNumCal", params, SnapshotMock{})
		result, _ := r.Invoke(c, "bigNumCal", b, params, tx, 0)
		if result.Code != 0 {
			t.Fatalf("real Go contract %d: %+v", n, result)
		}
		if string(result.Result) != "success bigNumCal: 607723520" {
			t.Fatalf("unexpected real Go result: %q", result.Result)
		}
	}
	objects, _, _, _, _, w1, wc1 := repairStats(t, m)
	if objects != base || w1-w0 != 2 || wc1-wc0 != 2 {
		t.Fatalf("Go WASI resources: objects %d/%d env %d/%d", base, objects, w1-w0, wc1-wc0)
	}
}

func TestStoreRepairActiveCloseAndNestedCallback(t *testing.T) {
	o, e := NewSafeFreshOwner(4, nil)
	if e != nil {
		t.Fatal(e)
	}
	defer func() {
		if e := o.Stop(context.Background()); e != nil {
			t.Error(e)
		}
	}()
	e = o.Do(context.Background(), func() (err error) {
		scope := w.ManagedOpen("parent")
		defer func() { err = errors.Join(err, scope.Close()) }()
		engine := w.NewEngine()
		compile := w.NewStore(engine)
		child, e := w.NewModule(compile, []byte(`(module (func (export "run") (result i32) i32.const 99))`), nil)
		if e != nil {
			return e
		}
		parent, e := w.NewModule(compile, []byte(`(module (import "host" "nested" (func $nested (result i32))) (func (export "run") (result i32) call $nested))`), nil)
		if e != nil {
			return e
		}
		store := w.NewStore(engine)
		fn := w.NewFunction(store, w.NewFunctionType(w.NewValueTypes(), w.NewValueTypes(w.I32)), func([]w.Value) ([]w.Value, error) {
			if e := scope.Close(); e == nil {
				return nil, errors.New("scope closed while active")
			}
			rejected := false
			func() { defer func() { rejected = recover() != nil }(); store.Close() }()
			if !rejected {
				return nil, errors.New("Store closed while active")
			}
			if e := o.Stop(context.Background()); e == nil {
				return nil, errors.New("Stop accepted inside callback")
			}
			var value interface{}
			err := o.Do(context.Background(), func() (err error) {
				nested := w.ManagedOpen("child")
				defer func() { err = errors.Join(err, nested.Close()) }()
				target := w.NewStore(engine)
				inst, e := w.NewInstanceInStore(child, w.NewImportObject(), target)
				if e != nil {
					return e
				}
				run, e := inst.Exports.GetRawFunction("run")
				if e != nil {
					return e
				}
				value, e = run.Call()
				return e
			})
			if err != nil {
				return nil, err
			}
			if value != int32(99) {
				return nil, fmt.Errorf("nested result %v", value)
			}
			return []w.Value{w.NewI32(99)}, nil
		})
		imports := w.NewImportObject()
		imports.Register("host", map[string]w.IntoExtern{"nested": fn})
		inst, e := w.NewInstanceInStore(parent, imports, store)
		if e != nil {
			return e
		}
		run, e := inst.Exports.GetRawFunction("run")
		if e != nil {
			return e
		}
		v, e := run.Call()
		if e != nil {
			return e
		}
		if v != int32(99) {
			return fmt.Errorf("parent result %v", v)
		}
		return nil
	})
	if e != nil {
		t.Fatal(e)
	}
	// Foreign threads cannot use owner-native objects, even during an idle period.
	rejected := false
	func() { defer func() { rejected = recover() != nil }(); w.ManagedCount() }()
	if !rejected {
		t.Fatal("foreign thread accepted")
	}
}

func TestStoreRepairCleanupError(t *testing.T) {
	cleanup := func() (err error) {
		scope := w.ManagedOpen("cleanup-trap")
		defer func() { err = errors.Join(err, scope.Close()) }()
		store := w.NewStore(w.NewEngine())
		module, e := w.NewModule(store, []byte(`(module (func (export "fail") unreachable))`), nil)
		if e != nil {
			return e
		}
		inst, e := w.NewInstanceInStore(module, w.NewImportObject(), store)
		if e != nil {
			return e
		}
		fn, e := inst.Exports.GetRawFunction("fail")
		if e != nil {
			return e
		}
		_, e = fn.Call()
		return e
	}
	o, e := NewSafeFreshOwner(2, cleanup)
	if e != nil {
		t.Fatal(e)
	}
	if e = o.Stop(context.Background()); e == nil || !strings.Contains(e.Error(), "unreachable") {
		t.Fatalf("cleanup trap lost: %v", e)
	}
	if e = o.Stop(context.Background()); e == nil {
		t.Fatal("duplicate Stop lost cleanup error")
	}
}
