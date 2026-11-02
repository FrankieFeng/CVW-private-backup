package wasmer
// Existing diagnostic support moved unchanged out of _test so non-test builds are valid.
import("encoding/json";"fmt";"os";"runtime";"runtime/metrics";"syscall")
var e27Enabled = os.Getenv("E27_ENABLED") == "1"
var e27Group, e27Role string
var e27Pair int

func e27Host() map[string]interface{} {
	samples := []metrics.Sample{{Name: "/gc/cycles/total:gc-cycles"}, {Name: "/memory/classes/heap/objects:bytes"}, {Name: "/gc/pauses:seconds"}}
	metrics.Read(samples)
	v := map[string]interface{}{"host_gc_cycles": samples[0].Value.Uint64(), "host_heap_objects_bytes": samples[1].Value.Uint64()}
	h := samples[2].Value.Float64Histogram()
	v["host_gc_pause_counts"] = append([]uint64(nil), h.Counts...)
	// Buckets include infinities; emit finite strings, retaining exact interval definitions.
	buckets := make([]string, len(h.Buckets))
	for i, b := range h.Buckets {
		buckets[i] = fmt.Sprint(b)
	}
	v["host_gc_pause_buckets_seconds"] = buckets
	return v
}

type e27Probe struct {
	active bool
	usage  syscall.Rusage
	mem    runtime.MemStats
}

func e27ProbeBegin() e27Probe {
	p := e27Probe{active: e27Enabled && os.Getenv("E27_DIAG") == "1"}
	if p.active {
		runtime.ReadMemStats(&p.mem)
		syscall.Getrusage(syscall.RUSAGE_THREAD, &p.usage)
	}
	return p
}
func e27ProbeEnd(p e27Probe, wall int64) {
	if !p.active {
		return
	}
	var u syscall.Rusage
	syscall.Getrusage(syscall.RUSAGE_THREAD, &u)
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	e27StandaloneEmit("export_diagnostic", map[string]interface{}{"group": e27Group, "role": e27Role, "pair": e27Pair, "export_wall_ns": wall, "owner_cpu_ns": u.Utime.Nano() + u.Stime.Nano() - p.usage.Utime.Nano() - p.usage.Stime.Nano(), "host_gc_count": m.NumGC - p.mem.NumGC, "host_gc_pause_ns": m.PauseTotalNs - p.mem.PauseTotalNs, "owner_tid": syscall.Gettid(), "guest_gc": "not_observed", "scope": "outer diagnostic envelope; MemStats outside original B5 window"})
}

func e27StandaloneEmit(event string,data interface{}) {b,e:=json.Marshal(map[string]interface{}{"event":event,"data":data});if e!=nil{panic(e)};fmt.Printf("STEP22 %s\n",b)}
