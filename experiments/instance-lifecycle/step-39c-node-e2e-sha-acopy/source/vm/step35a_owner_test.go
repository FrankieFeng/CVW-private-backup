package wasmer

import (
	"context"
	"errors"
	"runtime"
	"testing"
	"time"
)

func TestStep35AResetStop(t *testing.T) {
	o, e := NewSafeFreshOwner(4, nil)
	if e != nil {
		t.Fatal(e)
	}
	entered, release := make(chan struct{}), make(chan struct{})
	job := make(chan error, 1)
	go func() { job <- o.Do(context.Background(), func() error { close(entered); <-release; return nil }) }()
	<-entered
	reset := make(chan error, 1)
	go func() { reset <- o.Reset(context.Background(), func() error { return nil }) }()
	deadline := time.Now().Add(time.Second)
	for {
		o.mu.Lock()
		active := o.resetting
		o.mu.Unlock()
		if active {
			break
		}
		if time.Now().After(deadline) {
			close(release)
			t.Fatal("Reset did not begin")
		}
		runtime.Gosched()
	}
	if e = o.Do(context.Background(), func() error { return nil }); !errors.Is(e, ErrOwnerClosed) {
		t.Fatal("new job admitted during Reset", e)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Millisecond)
	defer cancel()
	e = o.Stop(ctx)
	if !errors.Is(e, context.DeadlineExceeded) {
		close(release)
		t.Fatal("Stop should wait Reset, not return early", e)
	}
	close(release)
	if e = <-job; e != nil {
		t.Fatal(e)
	}
	if e = <-reset; e != nil {
		t.Fatal(e)
	}
	if e = o.Stop(context.Background()); e != nil {
		t.Fatal(e)
	}
	if e = o.Stop(context.Background()); e != nil {
		t.Fatal(e)
	}
}
func TestStep35AStopThenReset(t *testing.T) {
	o, e := NewSafeFreshOwner(2, nil)
	if e != nil {
		t.Fatal(e)
	}
	entered, release := make(chan struct{}), make(chan struct{})
	job := make(chan error, 1)
	go func() { job <- o.Do(context.Background(), func() error { close(entered); <-release; return nil }) }()
	<-entered
	stopped := make(chan error, 1)
	go func() { stopped <- o.Stop(context.Background()) }()
	deadline := time.Now().Add(time.Second)
	for {
		o.mu.Lock()
		closing := o.closing
		o.mu.Unlock()
		if closing {
			break
		}
		if time.Now().After(deadline) {
			close(release)
			t.Fatal("Stop did not close admission")
		}
		runtime.Gosched()
	}
	if e = o.Reset(context.Background(), func() error { return nil }); !errors.Is(e, ErrOwnerClosed) {
		close(release)
		t.Fatal("Reset admitted after Stop", e)
	}
	close(release)
	if e = <-job; e != nil {
		t.Fatal(e)
	}
	if e = <-stopped; e != nil {
		t.Fatal(e)
	}
}
