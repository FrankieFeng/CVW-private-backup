package step35c

import (
	"context"
	"encoding/json"
	"fmt"
	"golang.org/x/sys/unix"
	"net"
	"net/http"
	"os"
	"sync"
	"sync/atomic"
	"time"
)

var seq uint64
var once sync.Once
var mu sync.Mutex
var phase string
var release chan struct{}
var used bool
var server35c *http.Server
var listener35c net.Listener
var done35c chan struct{}
var close35c sync.Once

func Mono() int64 { var t unix.Timespec; unix.ClockGettime(unix.CLOCK_MONOTONIC, &t); return t.Nano() }
func Event(event string, x map[string]interface{}) {
	if os.Getenv("CM35C_TRACE") != "1" {
		return
	}
	if x == nil {
		x = map[string]interface{}{}
	}
	x["event"] = event
	x["mono_ns"] = Mono()
	x["wall_ns"] = time.Now().UnixNano()
	x["seq"] = atomic.AddUint64(&seq, 1)
	b, _ := json.Marshal(x)
	fmt.Printf("STEP35C %s\n", b)
}
func Start() {
	once.Do(func() {
		p := os.Getenv("CM35C_SOCKET")
		if p == "" {
			return
		}
		ln, e := net.Listen("unix", p)
		if e != nil {
			panic(e)
		}
		os.Chmod(p, 0600)
		mux := http.NewServeMux()
		mux.HandleFunc("/state", func(w http.ResponseWriter, r *http.Request) {
			mu.Lock()
			defer mu.Unlock()
			json.NewEncoder(w).Encode(map[string]interface{}{"phase": phase, "used": used})
		})
		mux.HandleFunc("/release", func(w http.ResponseWriter, r *http.Request) {
			mu.Lock()
			defer mu.Unlock()
			if release != nil {
				close(release)
				release = nil
			}
			json.NewEncoder(w).Encode(map[string]bool{"released": true})
		})
		server35c = &http.Server{Handler: mux}
		listener35c = ln
		done35c = make(chan struct{})
		go func() {
			defer close(done35c)
			e := server35c.Serve(ln)
			Event("diagnostic_server_exit", map[string]interface{}{"error": fmt.Sprint(e)})
		}()
	})
}
func Hold(p string) {
	Start()
	if os.Getenv("CM35C_HOLD") != p {
		return
	}
	mu.Lock()
	if used {
		mu.Unlock()
		return
	}
	used = true
	phase = p
	c := make(chan struct{})
	release = c
	mu.Unlock()
	Event("hold_enter", map[string]interface{}{"phase": p})
	select {
	case <-c:
	case <-time.After(12 * time.Second):
		Event("hold_timeout", nil)
		panic("step35c diagnostic hold timeout")
	}
	Event("hold_exit", map[string]interface{}{"phase": p})
}

func Stop() {
	close35c.Do(func() {
		if server35c == nil {
			return
		}
		ctx, c := context.WithTimeout(context.Background(), 2*time.Second)
		defer c()
		if e := server35c.Shutdown(ctx); e != nil {
			panic(e)
		}
		listener35c.Close()
		select {
		case <-done35c:
		case <-ctx.Done():
			panic(ctx.Err())
		}
		Event("diagnostic_stopped", nil)
	})
}
