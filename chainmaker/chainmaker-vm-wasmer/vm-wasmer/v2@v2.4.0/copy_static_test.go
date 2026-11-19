package wasmer

import (
	"bytes"
	pb "chainmaker.org/chainmaker/pb-go/v2/common"
	wasm "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestCopyStaticCandidate(t *testing.T) {
	b, e := wasm.Wat2Wasm(`(module (memory (export "memory") 1) (data (i32.const 16) "hello"))`)
	if e != nil {
		t.Fatal(e)
	}
	c := &pb.Contract{Name: "copy", Version: "1"}
	p, e := prepareStaticMemory(b, c, "test")
	if e != nil {
		t.Fatal(e)
	}
	s := wasm.NewStore(wasm.NewEngine())
	m, e := wasm.NewModule(s, p.NoData, nil)
	if e != nil {
		t.Fatal(e)
	}
	p.Module = m
	i, e := wasm.NewInstance(m, wasm.NewImportObject())
	if e != nil {
		t.Fatal(e)
	}
	if e = p.restore(m, i, b, c, "test"); e != nil {
		t.Fatal(e)
	}
	mem, e := i.Exports.GetMemory("memory")
	if e != nil {
		t.Fatal(e)
	}
	if !bytes.Equal(mem.Data()[16:21], []byte("hello")) {
		t.Fatal("copy mismatch")
	}
	if p.restore(m, i, b, c, "wrong") == nil {
		t.Fatal("config mismatch accepted")
	}
	i.Close()
	m.Close()
	s.Close()
}

func TestCopyArenaCandidateBusiness(t *testing.T) {
	dir := os.Getenv("CVW_INTEGRATION_GUEST_DIR")
	if dir == "" {
		t.Skip("set CVW_INTEGRATION_GUEST_DIR to frozen compute guest pair")
	}
	params := prepareFunc("compute", "bigNumCal")
	fillingBaseParams(params)
	var reference []byte
	for _, variant := range []struct{ name, file, copy string }{{"plain", "plain-new.wasm", "0"}, {"copy", "plain-new.wasm", "1"}, {"arena", "arena-new.wasm", "0"}, {"both", "arena-new.wasm", "1"}} {
		t.Run(variant.name, func(t *testing.T) {
			t.Setenv("CM_CVW_COPY", variant.copy)
			code, c, log := prepareContract(filepath.Join(dir, variant.file), t)
			pool, err := newVmPool(&c, code, log)
			if err != nil {
				t.Fatal(err)
			}
			defer pool.close()
			runtime := RuntimeInstance{pool: pool, log: log, chainId: ChainId}
			ctx := prepareTxSimContext(ChainId, BlockVersion, "compute", "bigNumCal", params, SnapshotMock{})
			ctx.GetTx().Payload.TxId = "copy-arena-fixed-transaction"
			result, _, _, _, _, _ := runtime.InvokeTime(&c, "bigNumCal", code, params, ctx, 0)
			if result.Code != 0 || !strings.Contains(string(result.Result), "success") {
				t.Fatalf("business failure %+v", result)
			}
			data, err := json.Marshal([]interface{}{result, ctx.GetTxRWSet(true)})
			if err != nil {
				t.Fatal(err)
			}
			t.Logf("Gas=%d result=%s", result.GasUsed, result.Result)
			if reference == nil {
				reference = data
			} else if !bytes.Equal(reference, data) {
				t.Fatalf("Gas/result/RWSet/events mismatch: %s vs %s", reference, data)
			}
		})
	}
}
