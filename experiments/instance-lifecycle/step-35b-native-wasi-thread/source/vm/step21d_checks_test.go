package wasmer

import (
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"fmt"
	"os"
	"runtime"
	"strconv"
	"testing"
	"time"
)

func dN(t *testing.T) int {
	n, e := strconv.Atoi(os.Getenv("D_N"))
	if e != nil || n < 1 || n > 3 {
		t.Fatal("unreviewed invocation budget; allowed 1..3")
	}
	return n
}
func dOwner(t *testing.T) func() {
	runtime.LockOSThread()
	w.ManagedBeginOwner()
	root := w.ManagedOpen("process")
	return func() {
		if e := root.Close(); e != nil {
			t.Error(e)
		}
		if w.ManagedCount() != 0 {
			t.Error("pending native wrappers")
		}
		if os.Getenv("D_FORCE_GC") == "1" {
			runtime.GC()
		}
		runtime.GC()
		dEvent("owner_closed", map[string]interface{}{"managed_pending": w.ManagedCount()})
		w.ManagedEndOwner()
		runtime.UnlockOSThread()
	}
}
func TestStep21DOwnerFailure(t *testing.T) {
	defer dOwner(t)()
	m := newDManager("R1")
	rejected := make(chan bool, 1)
	go func() { defer func() { rejected <- recover() != nil }(); w.ManagedAssert() }()
	select {
	case ok := <-rejected:
		if !ok {
			t.Fatal("non-owner accepted")
		}
	case <-time.After(time.Second):
		t.Fatal("ownership rejection blocked")
	}
	base := w.ManagedCount()
	_, e := m.makeBundle(&common.Contract{Name: "invalid", Version: "1"}, []byte{1, 2, 3})
	if e == nil {
		t.Fatal("malformed module accepted")
	}
	if w.ManagedCount() != base {
		t.Fatal("failed create leaked wrapper registry")
	}
	dEvent("creation_failure_handled", map[string]interface{}{"error": e.Error(), "pending": w.ManagedCount()})
	b, e := m.makeBundle(&common.Contract{Name: "no-deallocator", Version: "1"}, []byte(`(module (import "wasi_snapshot_preview1" "proc_exit" (func (param i32))) (memory (export "memory") 1) (func (export "_start")))`))
	if e != nil {
		t.Fatal(e)
	}
	if e = m.closeBundle(b); e == nil {
		t.Fatal("missing guest deallocator was not reported")
	}
	if w.ManagedCount() != base {
		t.Fatal("close failure left tracked native objects")
	}
	dEvent("close_failure_handled", map[string]interface{}{"error": e.Error(), "pending": w.ManagedCount()})

	if e = m.Close(); e != nil {
		t.Fatal(e)
	}
	m.closing = true
	if _, e = m.NewRuntimeInstance(nil, "", "", "", &common.Contract{}, nil, nil); e == nil {
		t.Fatal("accepted after close")
	}
}
func TestStep21DCompute(t *testing.T) {
	defer dOwner(t)()
	n := dN(t)
	method := os.Getenv("D_METHOD")
	if method != "bigNumCal" && method != "normalCal" {
		t.Fatal("method not registered")
	}
	f := s21cPrepare(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
	defer f.close()
	expected := "success bigNumCal: 607723520"
	gas := uint64(105920)
	if method == "normalCal" {
		expected = "success normalCal: 666"
		gas = 100000072
	}
	for i := 0; i < n; i++ {
		r := f.run(fmt.Sprintf("compute-%03d", i), "compute", method, fmt.Sprintf("step21d-%03d", i), map[string]string{})
		if r.Result.Code != 0 || r.Status != common.TxStatusCode_SUCCESS || string(r.Result.Result) != expected || r.Result.GasUsed != gas {
			t.Fatalf("business/gas mismatch: %+v expected=%q gas=%d", r.Result, expected, gas)
		}
		if len(r.Calls) != 1 {
			t.Fatal("unexpected downstream call")
		}
		if os.Getenv("D_FORCE_GC") == "1" {
			runtime.GC()
		}
	}
}
func TestStep21DExchange(t *testing.T) {
	defer dOwner(t)()
	if dN(t) != 1 {
		t.Fatal("exchange resource gate limits this stage to one root")
	}
	s21cPreparedScenario(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
}
