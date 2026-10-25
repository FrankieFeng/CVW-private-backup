package wasmer

import (
	"fmt"
	"testing"
)

// Real guest functional diagnostic, not the default empty-pool continuous-load benchmark.
// Inventory=1 before first call and maintenance drain after EACH call are disclosed changes.
func TestStep21AIsolatedGuest(t *testing.T) {
	if !step21aGuardEnabled || !step21Enabled {
		t.Fatal("safety observations required")
	}
	name, method, n := *invokeContractName, *invokeContractMethod, *invokeTestTime
	wasm, contract, logger := prepareContract(prepareFile(name, *invokeContractType), t)
	p, err := newVmPool(&contract, wasm, logger)
	if err != nil {
		t.Fatal(err)
	}
	defer step21ClosePool(t, p)
	// Worker has no requests. Precreate one in the calling thread before any Invoke.
	p.grow(1)
	fmt.Println("STEP21A_DIAGNOSTIC inventory1_and_drain_between_calls_not_primary_benchmark")
	rt := RuntimeInstance{pool: p, log: logger, chainId: ChainId}
	inputs := step21LoadInputs(t, n)
	for i := 0; i < n; i++ {
		params := step21InputMap(inputs[i])
		fillingBaseParams(params)
		tx := prepareTxSimContext(ChainId, BlockVersion, name, method, params, SnapshotMock{})
		r, _, begin, end, total, call := rt.InvokeTime(&contract, method, wasm, params, tx, 0)
		step21Sample(i, method, params, r, begin, end, total, call)
		if r.Code != 0 {
			t.Fatalf("guest failed: %s", r.Message)
		}
		step21Quiesce(t, p)
	}
}
