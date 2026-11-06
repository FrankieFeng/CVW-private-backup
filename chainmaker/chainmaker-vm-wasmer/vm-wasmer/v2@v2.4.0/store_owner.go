package wasmer

import (
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"context"
	"errors"
	"fmt"
	"runtime"
	"sync"
	"sync/atomic"
	"syscall"
)

var ErrOwnerClosed = errors.New("native owner closed")
var ownerLease = make(chan struct{}, 1)

type ownerJob struct {
	fn    func() error
	reply chan error
}

// SafeFreshOwner confines creation, execution and destruction to one OS thread.
// Cancellation affects admission only; after admission Do waits for native cleanup.
// This prevents a caller from reusing its transaction context while WASM still runs.
type SafeFreshOwner struct {
	q       chan ownerJob
	done    chan struct{}
	mu      sync.Mutex
	pending sync.WaitGroup
	closing bool
	tid     atomic.Int64
	err     error
	cleanup func() error
}

func NewSafeFreshOwner(queueSize int, cleanup func() error) (*SafeFreshOwner, error) {
	if queueSize < 1 || queueSize > 32 {
		return nil, errors.New("owner queue size must be 1..32")
	}
	select {
	case ownerLease <- struct{}{}:
	default:
		return nil, errors.New("one native owner per process")
	}
	o := &SafeFreshOwner{q: make(chan ownerJob, queueSize), done: make(chan struct{}), cleanup: cleanup}
	ready := make(chan struct{})
	go o.loop(ready)
	<-ready
	return o, nil
}
func (o *SafeFreshOwner) loop(ready chan struct{}) {
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	w.ManagedBeginOwner()
	root := w.ManagedOpen("owner-root")
	o.tid.Store(int64(syscall.Gettid()))
	close(ready)
	defer func() {
		o.err = errors.Join(o.err, root.Close())
		nativeFailure := w.ManagedFailure()
		o.err = errors.Join(o.err, nativeFailure)
		if n := w.ManagedCount(); n != 0 {
			o.err = errors.Join(o.err, fmt.Errorf("native objects remain: %d", n))
		} else if nativeFailure == nil {
			w.ManagedEndOwner()
			<-ownerLease
		}
		o.tid.Store(0)
		close(o.done)
	}()
	for j := range o.q {
		err := func() (err error) {
			defer func() {
				if p := recover(); p != nil {
					err = fmt.Errorf("native owner panic: %v", p)
				}
			}()
			err = j.fn()
			if err != nil {
				return errors.New(err.Error())
			}
			return nil
		}()
		j.reply <- err
		o.pending.Done()
	}
}
func (o *SafeFreshOwner) Do(ctx context.Context, fn func() error) error {
	if ctx.Err() != nil {
		return ctx.Err()
	}
	if int64(syscall.Gettid()) == o.tid.Load() {
		return fn()
	} // synchronous cross-contract callback
	o.mu.Lock()
	if o.closing {
		o.mu.Unlock()
		return ErrOwnerClosed
	}
	o.pending.Add(1)
	o.mu.Unlock()
	j := ownerJob{fn: fn, reply: make(chan error, 1)}
	select {
	case o.q <- j:
		return <-j.reply
	case <-ctx.Done():
		o.pending.Done()
		return ctx.Err()
	}
}
func (o *SafeFreshOwner) Stop(ctx context.Context) error {
	if int64(syscall.Gettid()) == o.tid.Load() {
		return errors.New("Stop from active native callback rejected")
	}
	o.mu.Lock()
	first := !o.closing
	o.closing = true
	o.mu.Unlock()
	if first {
		go func() {
			o.pending.Wait()
			if o.cleanup != nil {
				j := ownerJob{fn: o.cleanup, reply: make(chan error, 1)}
				o.pending.Add(1)
				o.q <- j
				o.err = <-j.reply
				o.pending.Wait()
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

// All chain managers share the same native thread; each retains its own caches.
var freshService struct {
	sync.Mutex
	owner *SafeFreshOwner
	refs  int
}

func acquireFreshOwner() (*SafeFreshOwner, error) {
	freshService.Lock()
	defer freshService.Unlock()
	if freshService.owner == nil {
		o, e := NewSafeFreshOwner(32, nil)
		if e != nil {
			return nil, e
		}
		freshService.owner = o
	}
	freshService.refs++
	return freshService.owner, nil
}
func releaseFreshOwner(o *SafeFreshOwner) error {
	freshService.Lock()
	defer freshService.Unlock()
	if freshService.owner != o {
		return errors.New("owner reference mismatch")
	}
	freshService.refs--
	if freshService.refs != 0 {
		return nil
	}
	err := o.Stop(context.Background())
	freshService.owner = nil
	return err
}
