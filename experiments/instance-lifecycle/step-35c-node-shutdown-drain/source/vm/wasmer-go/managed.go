package wasmer

// Experimental deterministic finalizer ownership. Never install a Go native finalizer.
import (
	"fmt"
	"reflect"
	"syscall"
)

type managedEntry struct {
	object, fn interface{}
	live       bool
}
type ManagedScope struct {
	entries []*managedEntry
	closed  bool
	parent  *ManagedScope
	label   string
}

var managedOwner int
var managedCurrent *ManagedScope
var managedEntries = map[interface{}]*managedEntry{}

func ManagedBeginOwner() {
	if managedOwner != 0 {
		panic("owner already exists")
	}
	managedOwner = syscall.Gettid()
}
func ManagedAssert() {
	if managedOwner == 0 || syscall.Gettid() != managedOwner {
		panic("native owner thread violation")
	}
}
func ManagedOpen(label string) *ManagedScope {
	ManagedAssert()
	s := &ManagedScope{parent: managedCurrent, label: label}
	managedCurrent = s
	return s
}
func (s *ManagedScope) Activate() func() {
	ManagedAssert()
	old := managedCurrent
	if s.closed {
		panic("closed scope")
	}
	managedCurrent = s
	return func() { managedCurrent = old }
}
func managedSetFinalizer(obj, fn interface{}) bool {
	ManagedAssert()
	if fn == nil {
		if e := managedEntries[obj]; e != nil {
			e.live = false
			delete(managedEntries, obj)
			return true
		}
		return false
	}
	if managedCurrent == nil || managedCurrent.closed {
		panic("native allocation outside managed scope")
	}
	if len(managedEntries) >= 8192 || len(managedCurrent.entries) >= 8192 {
		panic("bounded native registry full")
	}
	if _, ok := managedEntries[obj]; ok {
		panic("duplicate finalizer registration")
	}
	e := &managedEntry{object: obj, fn: fn, live: true}
	managedCurrent.entries = append(managedCurrent.entries, e)
	managedEntries[obj] = e
	return true
}
func (s *ManagedScope) Close() (err error) {
	ManagedAssert()
	if managedCallDepth[s] != 0 {
		return fmt.Errorf("close while native call active")
	}
	if s.closed {
		return nil
	}
	old := managedCurrent
	managedCurrent = s
	defer func() {
		s.closed = true
		managedCurrent = old
		if old == s {
			managedCurrent = s.parent
		}
	}()
	for i := len(s.entries) - 1; i >= 0; i-- {
		e := s.entries[i]
		if !e.live {
			continue
		}
		func() {
			defer func() {
				if r := recover(); r != nil {
					err = fmt.Errorf("scope %s cleanup panic: %v", s.label, r)
				}
			}()
			reflect.ValueOf(e.fn).Call([]reflect.Value{reflect.ValueOf(e.object)})
		}()
		e.live = false
		delete(managedEntries, e.object)
	}
	s.entries = nil
	return err
}
func ManagedCount() int { ManagedAssert(); return len(managedEntries) }
func ManagedEndOwner() {
	ManagedAssert()
	if len(managedEntries) != 0 {
		panic("native cleanup registry not empty")
	}
	managedCurrent = nil
	managedOwner = 0
}
func (s *ManagedScope) Suspend() {
	ManagedAssert()
	if managedCurrent != s {
		panic("scope nesting")
	}
	managedCurrent = s.parent
}

// Same-thread C callback reentry is limited to existing exported Gas getters/setters.
// General same-Store recursive execution and deletion while active are rejected.
var managedCallDepth = map[*ManagedScope]int{}

func managedEnterFunction(f *Function) func() {
	ManagedAssert()
	managedBorrowAlive(f._ownedBy)
	s := f._managedScope
	if s == nil || s.closed {
		panic("native call outside live scope")
	}
	depth := managedCallDepth[s]
	if depth > 0 && (depth >= 2 || (f._managedName != "GetGas" && f._managedName != "SetGas")) {
		panic("unreviewed same-Store function reentry: " + f._managedName)
	}
	managedCallDepth[s] = depth + 1
	return func() {
		managedCallDepth[s]--
		if managedCallDepth[s] == 0 {
			delete(managedCallDepth, s)
		}
	}
}

var ManagedStoresCreated, ManagedStoresClosed, ManagedInstancesCreated, ManagedInstancesClosed uint64

func managedBorrowAlive(owner interface{}) {
	ManagedAssert()
	switch x := owner.(type) {
	case *Exports:
		if managedEntries[x] == nil || (x._store != nil && x._store._inner == nil) {
			panic("closed exports/Store")
		}
	case *Store:
		if x._inner == nil {
			panic("closed Store")
		}
	case *Module:
		if x._inner == nil {
			panic("closed Module")
		}
	}
}
