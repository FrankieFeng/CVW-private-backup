package wasmer

/*
#include <stdlib.h>
#include <wasmer.h>
#include <malloc.h>
#include <stdint.h>
// Read-only debug layout, pinned to dcdfa716... ELF: wasm_store_delete @0x2ce610 reads *(store), then decrements *(rc).
static size_t step35a_rc_before_delete(void *store) { return **(size_t **)store; }
*/
import "C"
import "unsafe"

var ManagedStoreLastStrong, ManagedStoreSharedStrong uint64
var ManagedStoreStrongHistogram = map[uint64]uint64{}

func diagnostic35aStoreDelete(store *C.wasm_store_t) {
	ManagedAssert()
	n := uint64(C.step35a_rc_before_delete(unsafe.Pointer(store)))
	ManagedStoreStrongHistogram[n]++
	if n == 1 {
		ManagedStoreLastStrong++
	} else {
		ManagedStoreSharedStrong++
	}
}

var ManagedWasiCreated, ManagedWasiClosed, ManagedImportContainersCreated, ManagedImportContainersClosed uint64

func Diagnostic35aNative() map[string]interface{} {
	ManagedAssert()
	m := C.mallinfo2()
	histogram := map[uint64]uint64{}
	for k, v := range ManagedStoreStrongHistogram {
		histogram[k] = v
	}
	hostFunctionStore.RLock()
	host := len(hostFunctionStore.functions)
	hostFunctionStore.RUnlock()
	return map[string]interface{}{"store_last_strong_delete": ManagedStoreLastStrong, "store_shared_strong_delete": ManagedStoreSharedStrong, "store_strong_before_histogram": histogram, "glibc_arena_bytes": uint64(m.arena), "glibc_inuse_bytes": uint64(m.uordblks), "glibc_free_bytes": uint64(m.fordblks), "glibc_mmap_bytes": uint64(m.hblkhd), "host_function_registrations": host, "wasi_created": ManagedWasiCreated, "wasi_closed": ManagedWasiClosed, "import_containers_created": ManagedImportContainersCreated, "import_containers_closed": ManagedImportContainersClosed}
}
