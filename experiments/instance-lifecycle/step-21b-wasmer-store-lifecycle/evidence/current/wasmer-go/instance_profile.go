//go:build startup_profile

package wasmer

// #include <wasmer.h>
import "C"

import (
	"runtime"
	"time"
)

// InstanceProfile is diagnostic timing, available only with startup_profile.
// Boundaries include wrapper work and cgo overhead, not only Rust CPU time.
type InstanceProfile struct {
	ImportVector, NativeCall, Exports time.Duration
}

// NewInstanceProfiled mirrors NewInstance without changing its ownership rules.
// Keep aligned with instance.go when updating the binding.
func NewInstanceProfiled(module *Module, imports *ImportObject) (*Instance, InstanceProfile, error) {
	var p InstanceProfile
	var traps *C.wasm_trap_t
	begin := time.Now()
	externs, err := imports.intoInner(module)
	p.ImportVector = time.Since(begin)
	if err != nil {
		return nil, p, err
	}
	var instance *C.wasm_instance_t
	begin = time.Now()
	err2 := maybeNewErrorFromWasmer(func() bool {
		instance = C.wasm_instance_new(module.store.Inner(), module.inner(), externs, &traps)
		return traps == nil && instance == nil
	})
	p.NativeCall = time.Since(begin)
	if err2 != nil {
		return nil, p, err2
	}
	if traps != nil {
		return nil, p, newErrorFromTrap(traps)
	}
	begin = time.Now()
	self := &Instance{_inner: instance, Exports: newExports(instance, module), imports: imports}
	runtime.SetFinalizer(self, func(self *Instance) { self.Close() })
	p.Exports = time.Since(begin)
	return self, p, nil
}
