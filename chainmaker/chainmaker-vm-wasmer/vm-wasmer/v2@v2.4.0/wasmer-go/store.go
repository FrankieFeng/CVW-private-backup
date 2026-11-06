package wasmer

// #include <wasmer.h>
import "C"

// Store represents all global state that can be manipulated by
// WebAssembly programs. It consists of the runtime representation of
// all instances of functions, tables, memories, and globals that have
// been allocated during the life time of the abstract machine.
//
// The Store holds the Engine (that is — amongst many things — used to
// compile the Wasm bytes into a valid module artifact).
//
// # See also
//
// Specification: https://webassembly.github.io/spec/core/exec/runtime.html#store
type Store struct {
	_inner *C.wasm_store_t
	Engine *Engine
}

// NewStore instantiates a new Store with an Engine.
//
//	engine := NewEngine()
//	store := NewStore(engine)
func NewStore(engine *Engine) *Store {
	ManagedAssert()
	self := &Store{
		_inner: C.wasm_store_new(engine.inner()),
		Engine: engine,
	}

	if self._inner == nil {
		return nil
	}
	ManagedStoresCreated++
	managedSetFinalizer(self, func(self *Store) {
		self.Close()
	})

	return self
}

func (self *Store) inner() *C.wasm_store_t {
	return self.Inner()
}

func (self *Store) Inner() *C.wasm_store_t {
	ManagedAssert()
	if self._inner == nil {
		panic("closed Store")
	}
	return self._inner
}

// Close the store forcingly
//
// A managed scope owns the Store. Close may release it early on the owner thread.
func (self *Store) Close() {
	if !managedSetFinalizer(self, nil) {
		return
	}
	C.wasm_store_delete(self._inner)
	self._inner = nil
	ManagedStoresClosed++
}
