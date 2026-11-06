package wasmer

// #include <wasmer.h>
import "C"

import (
	"fmt"
	"unsafe"
)

// ImportObject contains all of the import data used when
// instantiating a WebAssembly module.
type ImportObject struct {
	closed  bool
	externs map[string]map[string]IntoExtern
	_inner  *C.wasm_extern_vec_t
}

// NewImportObject instantiates a new empty ImportObject.
//
//	imports := NewImportObject()
func NewImportObject() *ImportObject {
	ManagedAssert()
	ManagedImportContainersCreated++
	self := &ImportObject{externs: make(map[string]map[string]IntoExtern)}
	managedSetFinalizer(self, func(self *ImportObject) { self.Close() })
	return self
}

func (self *ImportObject) intoInner(module *Module) (*C.wasm_extern_vec_t, error) {
	cExterns := &C.wasm_extern_vec_t{}

	var externs []*C.wasm_extern_t
	var numberOfExterns uint

	for _, importType := range module.Imports() {
		namespace := importType.Module()
		name := importType.Name()
		//fmt.Println(namespace, name)
		if self.externs[namespace][name] == nil {
			return nil, fmt.Errorf("missing import %s.%s", namespace, name)
		}
		externs = append(externs, self.externs[namespace][name].IntoExtern().inner())
		numberOfExterns++

	}

	if numberOfExterns > 0 {
		C.wasm_extern_vec_new(cExterns, C.size_t(numberOfExterns), (**C.wasm_extern_t)(unsafe.Pointer(&externs[0])))
	}
	self._inner = cExterns
	return cExterns, nil
}

// ContainsNamespace returns true if the ImportObject contains the given namespace (or module name)
//
//	imports := NewImportObject()
//	_ = imports.ContainsNamespace("env") // false
func (self *ImportObject) ContainsNamespace(name string) bool {
	_, exists := self.externs[name]

	return exists
}

// Register registers a namespace (or module name) in the ImportObject.
//
// It takes two arguments: the namespace name and a map with imports names as key and externs as values.
//
// Note:️ An extern is anything implementing IntoExtern: Function, Global, Memory, Table.
//
//	 imports := NewImportObject()
//	 importObject.Register(
//	 	"env",
//	 	map[string]wasmer.IntoExtern{
//	 		"host_function": hostFunction,
//	 		"host_global": hostGlobal,
//	 	},
//	)
//
// Note:️ The namespace (or module name) may be empty:
//
//	imports := NewImportObject()
//	importObject.Register(
//		"",
//		map[string]wasmer.IntoExtern{
//	 		"host_function": hostFunction,
//			"host_global": hostGlobal,
//		},
//	)
func (self *ImportObject) Register(namespaceName string, namespace map[string]IntoExtern) {
	ManagedAssert()
	if self.closed {
		panic("closed Imports")
	}
	_, exists := self.externs[namespaceName]

	if !exists {
		self.externs[namespaceName] = namespace
	} else {
		for key, value := range namespace {
			self.externs[namespaceName][key] = value
		}
	}
}

// MODIFIED
func (self *ImportObject) Close() {
	if !managedSetFinalizer(self, nil) {
		return
	}
	self.closed = true
	ManagedImportContainersClosed++
	for _, namespace := range self.externs {
		for name, _ := range namespace {
			delete(namespace, name)
		}
	}
	if self._inner != nil {
		C.wasm_extern_vec_destroy(self._inner)
		self._inner = nil
	}
}

// Reject cross-Store imports before passing native pointers to Wasmer.
func (self *ImportObject) validateStore(store *Store) error {
	ManagedAssert()
	if self.closed {
		return fmt.Errorf("closed Imports")
	}
	for ns, items := range self.externs {
		for name, v := range items {
			if nativeStore(v) != store {
				return fmt.Errorf("import %s.%s belongs to another/unknown Store", ns, name)
			}
		}
	}
	return nil
}
func nativeStore(v interface{}) *Store {
	switch x := v.(type) {
	case *Store:
		return x
	case *Exports:
		return x._store
	case *Function:
		if x._store != nil {
			return x._store
		}
		return nativeStore(x._ownedBy)
	case *Memory:
		if x._store != nil {
			return x._store
		}
		return nativeStore(x._ownedBy)
	case *Global:
		if x._store != nil {
			return x._store
		}
		return nativeStore(x._ownedBy)
	case *Table:
		if x._store != nil {
			return x._store
		}
		return nativeStore(x._ownedBy)
	case *Extern:
		if x._store != nil {
			return x._store
		}
		return nativeStore(x._ownedBy)
	}
	return nil
}
