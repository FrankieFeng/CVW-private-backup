package wasmer

// Experiment-only Unix control, no network listen. All native diagnostics stay on the existing Owner.
import (
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"runtime/debug"
	"sync"
	"time"
)

type control35a struct {
	server       *http.Server
	listener     net.Listener
	mu           sync.Mutex
	lastResetErr string
	resetSeq     int
	closed       bool
}

func (c *control35a) Close() {
	c.mu.Lock()
	if c.closed {
		c.mu.Unlock()
		return
	}
	c.closed = true
	c.mu.Unlock()
	c.listener.Close()
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	if e := c.server.Shutdown(ctx); e != nil {
		c.server.Close()
		nodeEvent("control_shutdown_error", map[string]interface{}{"error": e.Error()})
	}

}
func (m *InstancesManager) tracked35aReset() error {
	begin := time.Now()
	nodeEvent("manager_reset_begin", map[string]interface{}{"entry": "InstancesManager.ResetAllPool/ResetAVmPool", "inflight": m.safe.inflight.Load()})
	err := m.safe.reset()
	nodeEvent("manager_reset_end", map[string]interface{}{"error": fmt.Sprint(err), "reset_ns": time.Since(begin).Nanoseconds(), "inflight": m.safe.inflight.Load()})
	if c := m.safe.control35a; c != nil {
		c.mu.Lock()
		c.lastResetErr = fmt.Sprint(err)
		c.resetSeq++
		c.mu.Unlock()
	}
	return err
}
func (m *InstancesManager) start35aControl() error {
	path := os.Getenv("CM_STEP35A_CONTROL")
	if path == "" {
		return nil
	}
	if !filepath.IsAbs(path) {
		return errors.New("control socket must be absolute")
	}
	if _, e := os.Lstat(path); !os.IsNotExist(e) {
		return errors.New("existing control path: preserve, do not overwrite")
	}
	ln, e := net.Listen("unix", path)
	if e != nil {
		return e
	}
	if e = os.Chmod(path, 0600); e != nil {
		ln.Close()
		return e
	}
	c := &control35a{listener: ln}
	m.safe.control35a = c
	mux := http.NewServeMux()
	mux.HandleFunc("/state", func(rw http.ResponseWriter, r *http.Request) {
		o := m.safe.owner
		o.mu.Lock()
		s := map[string]interface{}{"resetting": o.resetting, "closing": o.closing, "accepted": o.accepted, "limit": o.limit, "inflight": m.safe.inflight.Load()}
		o.mu.Unlock()
		json.NewEncoder(rw).Encode(s)
	})
	mux.HandleFunc("/reset", func(rw http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			rw.WriteHeader(405)
			return
		}
		m.ResetAllPool()
		c.mu.Lock()
		out := map[string]interface{}{"manager_entry": "ResetAllPool", "seq": c.resetSeq, "error": c.lastResetErr}
		c.mu.Unlock()
		json.NewEncoder(rw).Encode(out)
	})
	mux.HandleFunc("/snapshot", func(rw http.ResponseWriter, r *http.Request) {
		var out map[string]interface{}
		err := m.safe.owner.Do(context.Background(), func() error { out = m.safe.snapshot35a(r.URL.Query().Get("tag")); return nil })
		if err != nil {
			rw.WriteHeader(409)
			json.NewEncoder(rw).Encode(map[string]interface{}{"error": err.Error()})
			return
		}
		json.NewEncoder(rw).Encode(out)
	})
	// Forced collection/scavenging is a separately labelled diagnostic, never a service setting or admission benchmark.
	mux.HandleFunc("/gc", func(rw http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			rw.WriteHeader(405)
			return
		}
		runtime.GC()
		json.NewEncoder(rw).Encode(map[string]string{"diagnostic": "explicit Go GC only"})
	})
	mux.HandleFunc("/scavenge", func(rw http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			rw.WriteHeader(405)
			return
		}
		debug.FreeOSMemory()
		json.NewEncoder(rw).Encode(map[string]string{"diagnostic": "explicit Go GC+scavenge; not default runtime policy"})
	})
	c.server = &http.Server{Handler: mux, ReadHeaderTimeout: 2 * time.Second}
	go func() {
		e := c.server.Serve(ln)
		if e != nil && !errors.Is(e, net.ErrClosed) && !errors.Is(e, http.ErrServerClosed) {
			nodeEvent("control_error", map[string]interface{}{"error": e.Error()})
		}
	}()
	return nil
}
func (m *nodeFreshManager) snapshot35a(tag string) map[string]interface{} {
	w.ManagedAssert()
	var ms runtime.MemStats
	runtime.ReadMemStats(&ms)
	goThreadRecords, _ := runtime.ThreadCreateProfile(nil)
	tasks, _ := filepath.Glob("/proc/self/task/*")
	thread := []map[string]string{}
	for _, p := range tasks {
		b, _ := os.ReadFile(p + "/comm")
		wc, _ := os.ReadFile(p + "/wchan")
		thread = append(thread, map[string]string{"tid": filepath.Base(p), "comm": string(b), "wchan": string(wc)})
	}
	roll, _ := os.ReadFile("/proc/self/smaps_rollup")
	status, _ := os.ReadFile("/proc/self/status")
	out := map[string]interface{}{"tag": tag, "wall_ns": time.Now().UnixNano(), "go_heap": ms.HeapAlloc, "go_heap_sys": ms.HeapSys, "go_heap_idle": ms.HeapIdle, "go_heap_released": ms.HeapReleased, "go_num_gc": ms.NumGC, "go_pause_total_ns": ms.PauseTotalNs, "goroutines": runtime.NumGoroutine(), "os_threads": len(tasks), "go_thread_create_records": goThreadRecords, "thread_details": thread, "smaps_rollup": string(roll), "proc_status": string(status), "stores_created": w.ManagedStoresCreated, "stores_closed": w.ManagedStoresClosed, "instances_created": w.ManagedInstancesCreated, "instances_closed": w.ManagedInstancesClosed, "managed_pending": w.ManagedCount(), "modules_cached": len(m.caches), "inflight": m.inflight.Load(), "native_diagnostic": w.Diagnostic35aNative()}
	nodeEvent("resource_snapshot", map[string]interface{}{"tag": tag, "modules_cached": len(m.caches), "goroutines": runtime.NumGoroutine(), "os_threads": len(tasks)})
	return out
}
