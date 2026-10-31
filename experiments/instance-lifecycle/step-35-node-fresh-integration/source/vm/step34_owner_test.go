package wasmer

import (
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"context"
	"errors"
	"os"
	"runtime"
	"testing"
	"time"
)

func TestStep34Owner(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 12*time.Second)
	defer cancel()
	var cache *w.ManagedScope
	var store *w.Store
	var module *w.Module
	var engine *w.Engine
	closeCache := func() error {
		if cache == nil {
			return nil
		}
		e := cache.Close()
		cache = nil
		return e
	}
	o, e := NewSafeFreshOwner(24, closeCache)
	if e != nil {
		t.Fatal(e)
	}
	prepare := func() error {
		cache = w.ManagedOpen("cache")
		engine = w.NewEngine()
		store = w.NewStore(engine)
		var e error
		module, e = w.NewModule(store, []byte{0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 127, 3, 2, 1, 0, 7, 7, 1, 3, 114, 117, 110, 0, 0, 10, 6, 1, 4, 0, 65, 42, 11}, nil)
		if e != nil {
			return e
		}
		module.Imports()
		module.Exports()
		cache.Suspend()
		return nil
	}
	if e = o.Do(ctx, prepare); e != nil {
		t.Fatal(e)
	}
	native := func() error {
		s := w.ManagedOpen("request")
		defer s.Close()
		target := w.NewStore(engine)
		if target.Inner() == nil {
			return errors.New("store")
		}
		i, e := w.NewInstanceInStore(module, w.NewImportObject(), target)
		if e != nil {
			return e
		}
		fn, e := i.Exports.GetRawFunction("run")
		if e != nil {
			return e
		}
		v, e := fn.Call()
		if e != nil || v != int32(42) {
			return errors.New("result")
		}
		fn.Close()
		i.Close()
		rejected := false
		func() {
			defer func() {
				if recover() != nil {
					rejected = true
				}
			}()
			fn.Call()
		}()
		if !rejected {
			return errors.New("function accessed after Instance Close")
		}
		i.Close()
		target.Close()
		target.Close()
		runtime.GC()
		return nil
	}
	for n := 0; n < 4; n++ {
		if e = o.Do(ctx, native); e != nil {
			t.Fatal(e)
		}
	}
	// Invalid real module is a safe native error, not a synthetic successful fixture.
	if e = o.Do(ctx, func() error {
		s := w.ManagedOpen("bad-module")
		defer s.Close()
		_, err := w.NewModule(w.NewStore(engine), []byte{0, 97, 115, 109, 1, 0, 0, 0, 255, 0}, nil)
		if err == nil {
			return errors.New("invalid module accepted")
		}
		return nil
	}); e != nil {
		t.Fatal(e)
	}
 if e=o.Do(ctx,func()error{s:=w.ManagedOpen("real-trap");defer s.Close();st:=w.NewStore(engine);m,e:=w.NewModule(st,[]byte(`(module (func (export "fail") unreachable))`),nil);if e!=nil{return e};i,e:=w.NewInstanceInStore(m,w.NewImportObject(),st);if e!=nil{return e};fn,e:=i.Exports.GetRawFunction("fail");if e!=nil{return e};_,e=fn.Call();return e});e==nil{t.Fatal("native trap lost")};if _,ok:=e.(*w.TrapError);ok{t.Fatal("native frame handles escaped owner")}

	if e = o.Do(ctx, func() error {
		return o.Do(ctx, func() error {
			if o.Reset(ctx, closeCache) == nil {
				return errors.New("inline Reset accepted")
			}
			if o.Stop(ctx) == nil {
				return errors.New("inline Stop accepted")
			}
			return nil
		})
	}); e != nil {
		t.Fatal(e)
	}
	entered := make(chan struct{})
	release := make(chan struct{})
	first := make(chan error, 1)
	go func() { first <- o.Do(ctx, func() error { close(entered); <-release; return nil }) }()
	<-entered
	canceled, cc := context.WithCancel(ctx)
	cc()
	if !errors.Is(o.Do(canceled, native), context.Canceled) {
		t.Fatal("cancel before creation")
	}
	resetDone := make(chan error, 1)
	go func() { resetDone <- o.Reset(ctx, closeCache) }()
	runtime.GC()
	close(release)
	if e = <-first; e != nil {
		t.Fatal(e)
	}
	if e = <-resetDone; e != nil {
		t.Fatal(e)
	}
	if e = o.Do(ctx, prepare); e != nil {
		t.Fatal(e)
	}
	if e = o.Do(ctx, native); e != nil {
		t.Fatal(e)
	}
	// Stop cannot free cache while an admitted task is running; deadline doesn't abort native code.
	entered = make(chan struct{})
	release = make(chan struct{})
	go func() { first <- o.Do(ctx, func() error { close(entered); <-release; return nil }) }()
	<-entered
	short, cs := context.WithCancel(ctx)
	cs()
	if !errors.Is(o.Stop(short), context.Canceled) {
		t.Fatal("stop must wait")
	}
	close(release)
	if e = <-first; e != nil {
		t.Fatal(e)
	}
	if e = o.Stop(ctx); e != nil {
		t.Fatal(e)
	}
	if e = o.Stop(ctx); e != nil {
		t.Fatal(e)
	}
	if o.Do(ctx, native) == nil {
		t.Fatal("post Stop admitted")
	}
	if w.ManagedStoresCreated != w.ManagedStoresClosed || w.ManagedInstancesCreated != w.ManagedInstancesClosed {
		t.Fatal("native counts")
	}
	s34Emit("owner_protocol", map[string]interface{}{"stores_created": w.ManagedStoresCreated, "stores_closed": w.ManagedStoresClosed, "instances_created": w.ManagedInstancesCreated, "instances_closed": w.ManagedInstancesClosed, "gc_forced": true, "reset_stop": true, "repeat_close": true, "mode": os.Getenv("E34_INDEPENDENT")})
}
