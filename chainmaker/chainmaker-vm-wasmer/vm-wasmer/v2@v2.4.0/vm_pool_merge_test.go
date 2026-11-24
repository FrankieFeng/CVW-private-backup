/*
Copyright (C) BABEC. All rights reserved.
Copyright (C) THL A29 Limited, a Tencent company.

SPDX-License-Identifier: Apache-2.0
*/

package wasmer

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	wasmergo "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
)

func newMergeRegressionPool(t *testing.T) *vmPool {
	t.Helper()
	t.Setenv(envProcessIsolation, "0")
	t.Setenv("CM_CVW_COPY", "0")
	_, contract, log := prepareContract("./testdata/compute-go.wasm", t)
	wasm, err := wasmergo.Wat2Wasm(`(module
		(import "wasi_snapshot_preview1" "args_sizes_get" (func $args (param i32 i32) (result i32)))
		(memory (export "memory") 1)
		(func (export "probe") (result i32)
			i32.const 0 i32.const 4 call $args))`)
	require.NoError(t, err)
	pool, err := newVmPool(&contract, wasm, log)
	require.NoError(t, err)
	t.Cleanup(func() {
		pool.close()
		select {
		case <-pool.closed:
		case <-time.After(5 * time.Second):
			t.Error("pool did not close")
		}
	})
	return pool
}

func TestMergeRepairWASIPrivateStores(t *testing.T) {
	pool := newMergeRegressionPool(t)
	first, err := pool.NewInstance()
	require.NoError(t, err)
	defer pool.CloseInstance(first)
	second, err := pool.NewInstance()
	require.NoError(t, err)
	defer pool.CloseInstance(second)

	require.True(t, first.store.Inner() != second.store.Inner())
	require.True(t, pool.store.Inner() != first.store.Inner())
	require.True(t, pool.store.Inner() != second.store.Inner())
	for _, instance := range []*wrappedInstance{first, second} {
		probe, err := instance.wasmInstance.Exports.GetFunction("probe")
		require.NoError(t, err)
		result, err := probe()
		require.NoError(t, err)
		require.Equal(t, int32(0), result)
	}
	firstMemory, err := first.wasmInstance.Exports.GetMemory("memory")
	require.NoError(t, err)
	secondMemory, err := second.wasmInstance.Exports.GetMemory("memory")
	require.NoError(t, err)
	firstMemory.Data()[16] = 42
	require.Zero(t, secondMemory.Data()[16])
}

func TestMergeRepairEngineLifecycle(t *testing.T) {
	pool := newMergeRegressionPool(t)
	require.NotNil(t, pool.engine)
	require.Same(t, pool.store.Engine, pool.engine)
	pool.close()
	pool.close()
	select {
	case <-pool.closed:
	case <-time.After(5 * time.Second):
		t.Fatal("pool did not close")
	}
	require.Nil(t, pool.engine)
	require.Nil(t, pool.store.Inner())
}
