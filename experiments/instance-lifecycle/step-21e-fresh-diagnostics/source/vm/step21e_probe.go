package wasmer

import (
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"os"
	"runtime"
	"syscall"
	"time"
)

type eSlot struct {
	Slot uint64 `json:"slot"`
	SHA  string `json:"sha256"`
}

var eSlots = func() map[string]eSlot {
	p := os.Getenv("E_COUNTERS")
	if p == "" {
		return nil
	}
	b, e := os.ReadFile(p)
	if e != nil {
		panic(e)
	}
	var v map[string]eSlot
	if e = json.Unmarshal(b, &v); e != nil {
		panic(e)
	}
	return v
}()
var eTraceEnabled = os.Getenv("E_GAS_TRACE") == "1"
var eActive = map[*w.Instance]*SimContext{}
var eEpoch = time.Now()

func eEmit(v map[string]interface{}) {
	v["monotonic_ns"] = time.Since(eEpoch).Nanoseconds()
	b, e := json.Marshal(v)
	if e != nil {
		panic(e)
	}
	fmt.Printf("STEP21E %s\n", b)
}
func eRawGas(inst *w.Instance, contract string) uint64 {
	w.ManagedAssert()
	slot, ok := eSlots[contract]
	if !ok {
		panic("no verified counter slot: " + contract)
	}
	mem, e := inst.Exports.GetMemory("memory")
	if e != nil {
		panic(e)
	}
	data := mem.Data()
	if slot.Slot+8 > uint64(len(data)) {
		panic("counter slot out of bounds")
	}
	pointer := binary.LittleEndian.Uint64(data[slot.Slot : slot.Slot+8])
	if pointer == 0 || pointer+8 > uint64(len(data)) {
		panic("counter pointer out of bounds")
	}
	return binary.LittleEndian.Uint64(data[pointer : pointer+8])
}
func eGas(sc *SimContext, phase, host, when, detail string) {
	if !eTraceEnabled || sc == nil {
		return
	}
	sc.eSeq++
	remain := eRawGas(sc.Instance, sc.Contract.Name)
	eEmit(map[string]interface{}{"event": "gas", "contract": sc.Contract.Name, "method": sc.method, "tx_id": sc.TxSimContext.GetTx().Payload.TxId, "depth": sc.TxSimContext.GetDepth(), "instance_id": sc.lifecycleID, "policy": sc.ePolicy, "seq": sc.eSeq, "phase": phase, "host": host, "when": when, "detail": detail, "remaining": remain, "gas_absolute": runtimeGasLimit - remain})
}
func eVerifyGas(inst *w.Instance, contract string, expected uint64) {
	if !eTraceEnabled {
		return
	}
	actual := eRawGas(inst, contract)
	if actual != expected {
		panic(fmt.Sprintf("raw counter mismatch %d != GetGas %d", actual, expected))
	}
}

type eMeasure struct {
	time  time.Time
	usage syscall.Rusage
	gc    runtime.MemStats
}

func eBeginMeasure() eMeasure {
	var m eMeasure
	runtime.ReadMemStats(&m.gc)
	syscall.Getrusage(syscall.RUSAGE_THREAD, &m.usage)
	m.time = time.Now()
	return m
}
func eEndMeasure(m eMeasure, sc *SimContext) {
	elapsed := time.Since(m.time).Nanoseconds()
	var u syscall.Rusage
	syscall.Getrusage(syscall.RUSAGE_THREAD, &u)
	var gc runtime.MemStats
	runtime.ReadMemStats(&gc)
	cpu := (u.Utime.Nano() + u.Stime.Nano()) - (m.usage.Utime.Nano() + m.usage.Stime.Nano())
	eEmit(map[string]interface{}{"event": "export_profile", "contract": sc.Contract.Name, "method": sc.method, "policy": sc.ePolicy, "instance_id": sc.lifecycleID, "tx_id": sc.TxSimContext.GetTx().Payload.TxId, "depth": sc.TxSimContext.GetDepth(), "export_ns": elapsed, "owner_thread_cpu_ns": cpu, "host_gc_count": gc.NumGC - m.gc.NumGC, "host_gc_pause_ns": gc.PauseTotalNs - m.gc.PauseTotalNs, "host_heap_before": m.gc.HeapAlloc, "host_heap_after": gc.HeapAlloc, "guest_gc": "not_observed_no_export_or_dwarf"})
}
