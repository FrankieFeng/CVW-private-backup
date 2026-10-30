package wasmer

// Experimental bounded native owner. No native handle is returned to request goroutines.
import (
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"runtime"
	"sync"
	"sync/atomic"
	"syscall"
)

var ErrOwnerClosed = errors.New("owner closed/resetting")
var ownerLease = make(chan struct{}, 1)

type ownerJob struct {
	ctx     context.Context
	fn      func() error
	reply   chan error
	control bool
}
type SafeFreshOwner struct {
	q                  chan ownerJob
	done               chan struct{}
	mu                 sync.Mutex
	wg                 sync.WaitGroup
	closing, resetting bool
	poisoned           bool
	accepted, limit    int
	tid                atomic.Int64
	err                error
	cleanup            func() error
}

func NewSafeFreshOwner(limit int, cleanup func() error) (*SafeFreshOwner, error) {
	if limit < 1 || limit > 32 {
		return nil, errors.New("bounded owner request limit 1..32")
	}
	select {
	case ownerLease <- struct{}{}:
	default:
		return nil, errors.New("one native owner per process")
	}
	o := &SafeFreshOwner{q: make(chan ownerJob, 1), done: make(chan struct{}), limit: limit, cleanup: cleanup}
	ready := make(chan struct{})
	go o.loop(ready)
	<-ready
	return o, nil
}
func (o *SafeFreshOwner) loop(ready chan struct{}) {
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	w.ManagedBeginOwner()
	root := w.ManagedOpen("step34-owner-root")
	o.tid.Store(int64(syscall.Gettid()))
	close(ready)
	defer func() {
		if r := recover(); r != nil {
			o.err = fmt.Errorf("owner panic: %v", r)
		}
		if e := root.Close(); e != nil {
			o.err = e
		}
		remaining := w.ManagedCount()
		if remaining != 0 {
			o.err = fmt.Errorf("owner objects remain: %d", remaining)
		} else {
			w.ManagedEndOwner()
		}
		data, _ := json.Marshal(map[string]interface{}{"event": "owner_closed", "managed_pending": remaining, "managed_objects": remaining, "stores_created": w.ManagedStoresCreated, "stores_closed": w.ManagedStoresClosed, "instances_created": w.ManagedInstancesCreated, "instances_closed": w.ManagedInstancesClosed})
		fmt.Printf("STEP21C %s\n", data)
		o.tid.Store(0)
		if remaining == 0 {
			<-ownerLease
		}
		close(o.done)
	}()
	for j := range o.q {
		func() {
			err := errors.New("owner job aborted")
			defer func() {
				if r := recover(); r != nil {
					err = fmt.Errorf("owner job panic: %v", r)
				}
				if err!=nil && !errors.Is(err,context.Canceled) && !errors.Is(err,context.DeadlineExceeded) {err=errors.New(err.Error())} // never return native Trap/Frame handles outside owner
 j.reply <- err
				if !j.control {
					o.wg.Done()
				}
			}()
			if j.ctx.Err() != nil {
				err = j.ctx.Err()
				return
			}
			err = j.fn()
		}()
	}
}
func (o *SafeFreshOwner) Do(ctx context.Context, fn func() error) error {
	if int64(syscall.Gettid()) == o.tid.Load() {
		if ctx.Err() != nil {
			return ctx.Err()
		}
		return fn()
	} // same-owner parent/child callback, no self-queue
	o.mu.Lock()
	if o.closing || o.resetting || o.poisoned || o.accepted >= o.limit {
		o.mu.Unlock()
		return ErrOwnerClosed
	}
	o.accepted++
	o.wg.Add(1)
	o.mu.Unlock()
	j := ownerJob{ctx: ctx, fn: fn, reply: make(chan error, 1)}
	select {
	case o.q <- j:
	case <-ctx.Done():
		o.wg.Done()
		return ctx.Err()
	case <-o.done:
		o.wg.Done()
		return ErrOwnerClosed
	}
	select {
	case e := <-j.reply:
		return e
	case <-ctx.Done():
		return ctx.Err()
	case <-o.done:
		return ErrOwnerClosed
	}
}
func (o *SafeFreshOwner) Reset(ctx context.Context, reset func() error) error {
	if int64(syscall.Gettid()) == o.tid.Load() {
		return errors.New("reset from active owner rejected")
	}
	o.mu.Lock()
	if o.closing || o.resetting || o.poisoned {
		o.mu.Unlock()
		return ErrOwnerClosed
	}
	o.resetting = true
	o.mu.Unlock()
	reply := make(chan error, 1)
	go func() {
		o.wg.Wait()
		j := ownerJob{ctx: context.Background(), fn: reset, reply: make(chan error, 1), control: true}
		var err error
		select {
		case o.q <- j:
			err = <-j.reply
		case <-o.done:
			err = ErrOwnerClosed
		}
		o.mu.Lock()
		o.resetting = false
		if err != nil {
			o.poisoned = true
		}
		o.mu.Unlock()
		reply <- err
	}()
	select {
	case e := <-reply:
		return e
	case <-ctx.Done():
		return ctx.Err()
	}
}
func (o *SafeFreshOwner) Stop(ctx context.Context) error {
	if int64(syscall.Gettid()) == o.tid.Load() {
		return errors.New("stop from active owner rejected")
	}
	o.mu.Lock()
	if o.resetting {
		o.mu.Unlock()
		return ErrOwnerClosed
	}
	first := !o.closing
	o.closing = true
	o.mu.Unlock()
	if first {
		go func() {
			o.wg.Wait()
			if o.cleanup != nil {
				j := ownerJob{ctx: context.Background(), fn: o.cleanup, reply: make(chan error, 1), control: true}
				select {
				case o.q <- j:
					select {
					case e := <-j.reply:
						if e != nil {
							o.err = e
						}
					case <-o.done:
						return
					}
				case <-o.done:
					return
				}
			}
			close(o.q)
		}()
	}
	select {
	case <-o.done:
		return o.err
	case <-ctx.Done():
		return ctx.Err()
	}
}
