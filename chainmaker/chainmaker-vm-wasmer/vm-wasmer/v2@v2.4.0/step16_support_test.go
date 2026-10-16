//go:build step16

// Loaded into the VM test package with Go's -overlay; no production file is edited.
package wasmer

import (
	protocol "chainmaker.org/chainmaker/protocol/v2"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"testing"
	"time"

	logger2 "chainmaker.org/chainmaker/logger/v2"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	wasm "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
)

type s15Spec struct {
	Label, Status    string
	Method, Expected string
	Params           map[string]string
	BusinessScope    string `json:"business_scope"`
	Real             bool
	Paths            map[string]string
	Ranges           [][2]int
	Globals, Tables  int
	ImageSHA         string `json:"image_sha256"`
}
type s15Prepared struct {
	spec   s15Spec
	module *wasm.Module
	store  *wasm.Store
	pool   *vmPool
	image  []byte
}
type s15Fresh struct {
	instance *wasm.Instance
	memory   *wasm.Memory
	env      *CMEnvironment
	begin    time.Time
	row      map[string]interface{}
	bind     func()
	close    func()
}

func s15Must(t *testing.T, e error) {
	t.Helper()
	if e != nil {
		t.Fatal(e)
	}
}
func s15Prepare(t *testing.T, s s15Spec, key string) *s15Prepared {
	config := wasm.NewConfig()
	config.MaxPagesLimit(512)
	if s.Real {
		config = s15GasConfig()
	}
	store := wasm.NewStore(wasm.NewEngineWithConfig(config))
	b, e := os.ReadFile(s.Paths[key])
	s15Must(t, e)
	logger := logger2.GetLogger("step15")
	s15Must(t, wasm.ValidateModule(store, b))
	var module *wasm.Module
	if dir := os.Getenv("S15_ARTIFACTS"); s.Real && dir != "" {
		serialized, err := os.ReadFile(filepath.Join(dir, s.Label, key+".module"))
		s15Must(t, err)
		module, e = wasm.DeserializeModule(store, serialized)
	} else {
		module, e = wasm.NewModule(store, b, logger)
	}
	s15Must(t, e)
	t.Cleanup(func() { module.Close(); store.Close() })
	image, e := os.ReadFile(s.Paths["image"])
	s15Must(t, e)
	p := &s15Prepared{spec: s, module: module, store: store, image: image}
	p.pool = &vmPool{store: store, module: module, log: logger, contractId: &commonPb.Contract{Name: s.Label, Version: "1.0.0", RuntimeType: commonPb.RuntimeType_WASMER}}
	return p
}
func s15Create(t *testing.T, p *s15Prepared, method string) *s15Fresh {
	f := &s15Fresh{env: &CMEnvironment{}, row: map[string]interface{}{}}
	f.begin = time.Now()
	imports := wasm.NewImportObject()
	release := func() {}
	f.bind = func() {}
	if p.spec.Real {
		wasi, e := p.pool.acquireWasiEnv()
		s15Must(t, e)
		imports, e = wasi.GenerateImportObject(p.store, p.module)
		s15Must(t, e)
		imports, e = GetVmBridgeManager().GetImports(p.store, f.env, imports)
		s15Must(t, e)
		release = func() { p.pool.releaseWasiEnv(wasi) }
		f.bind = func() { s15Must(t, wasi.Initialize(p.store, f.instance)) }
	}
	start := time.Now()
	i, e := wasm.NewInstance(p.module, imports)
	f.row["new_instance_ns"] = time.Since(start).Nanoseconds()
	s15Must(t, e)
	f.instance = i
	start = time.Now()
	memory, e := i.Exports.GetMemory("memory")
	s15Must(t, e)
	f.memory = memory
	copyNS := int64(0)
	if method != "baseline" {
		copyStart := time.Now()
		dst := memory.Data() // one view per instance: two C API calls, no intermediate copy
		if len(dst) != len(p.image) {
			t.Fatal("memory length mismatch")
		}
		if method == "A_full" {
			copy(dst, p.image)
		} else {
			for _, r := range p.spec.Ranges {
				copy(dst[r[0]:r[1]], p.image[r[0]:r[1]])
			}
		}
		copyNS = time.Since(copyStart).Nanoseconds()
	}
	f.row["memory_access_and_copy_ns"] = time.Since(start).Nanoseconds()
	f.row["memory_copy_ns"] = copyNS
	f.row["total_s1_ns"] = time.Since(f.begin).Nanoseconds()
	f.close = func() { i.Close(); release(); runtime.KeepAlive(imports) }
	return f
}
func s15Start(t *testing.T, f *s15Fresh) {
	f.bind()
	start, e := f.instance.Exports.GetWasiStartRawFunction()
	s15Must(t, e)
	if start == nil {
		t.Fatal("missing _start")
	}
	begin := time.Now()
	_, e = start.Call()
	f.row["start_ns"] = time.Since(begin).Nanoseconds()
	if e != nil && e.Error() != "WASI exited with code: ExitCode::0" {
		t.Fatal(e)
	}
	f.row["total_s2_ns"] = time.Since(f.begin).Nanoseconds()
	start.Close()
	f.env.instance = f.instance
	f.env.memory = f.memory
}

// Cross-contract responses are deterministic mocks: callees are NOT executed.
type s15CrossContext struct {
	protocol.TxSimContext
	last  []byte
	calls []string
}

func (c *s15CrossContext) GetContractByName(name string) (*commonPb.Contract, error) {
	return &commonPb.Contract{Name: name, Version: "1.0.0", RuntimeType: commonPb.RuntimeType_WASMER}, nil
}
func (c *s15CrossContext) GetCurrentResult() []byte { return c.last }
func (c *s15CrossContext) CallContract(caller, contract *commonPb.Contract, method string, bytecode []byte, params map[string][]byte, gas uint64, ref commonPb.TxType) (*commonPb.ContractResult, protocol.ExecOrderTxType, commonPb.TxStatusCode) {
	answers := map[string]string{"identity/addWriteList": "add write list success", "identity/isApprovedUser": "true", "erc721/mint": "mint success", "erc721/setApprovalForAll2": "setApprovalForAll2 success", "erc721/transferFrom": "transfer success"}
	key := contract.Name + "/" + method
	answer, ok := answers[key]
	c.calls = append(c.calls, key)
	if !ok {
		return &commonPb.ContractResult{Code: 1, Message: "unexpected mock call"}, protocol.ExecOrderTxTypeNormal, commonPb.TxStatusCode_CONTRACT_FAIL
	}
	c.last = []byte(answer)
	return &commonPb.ContractResult{Result: c.last}, protocol.ExecOrderTxTypeNormal, commonPb.TxStatusCode_SUCCESS
}
func s15Business(t *testing.T, p *s15Prepared, f *s15Fresh) map[string]interface{} {
	params := map[string][]byte{}
	for k, v := range p.spec.Params {
		params[k] = []byte(v)
	}
	fillingBaseParams(params)
	tx := prepareTxSimContext(ChainId, BlockVersion, p.spec.Label, p.spec.Method, params, SnapshotMock{})
	tx.GetTx().Payload.TxId = "STEP15_FIXED_TX"
	cross := &s15CrossContext{TxSimContext: tx}
	if p.spec.Label == "exchange" {
		tx = cross
	}
	result := &commonPb.ContractResult{}
	sc := NewSimContext(p.spec.Method, p.pool.log, ChainId)
	sc.removeCtxPointer()
	sc.CtxPtr = 10000001
	GetVmBridgeManager().put(sc.CtxPtr, sc)
	defer sc.removeCtxPointer()
	sc.Contract = p.pool.contractId
	sc.TxSimContext = tx
	sc.ContractResult = result
	sc.parameters = params
	sc.Instance = f.instance
	s15Must(t, setGasByExport(f.instance, runtimeGasLimit))
	before := f.instance.GetGasRemaining()
	callerr := sc.CallMethod(f.instance)
	after := f.instance.GetGasRemaining()
	gas, e := getGasByExport(f.instance)
	s15Must(t, e)
	writes := tx.GetTxRWSet(true).TxWrites
	sort.Slice(writes, func(i, j int) bool {
		if writes[i].ContractName != writes[j].ContractName {
			return writes[i].ContractName < writes[j].ContractName
		}
		return string(writes[i].Key) < string(writes[j].Key)
	})
	w, e := json.Marshal(writes)
	s15Must(t, e)
	events, e := json.Marshal(sc.ContractEvent)
	s15Must(t, e)
	errtext := ""
	if callerr != nil {
		errtext = callerr.Error()
	}
	expected := p.spec.Expected == "" || string(result.Result) == p.spec.Expected
	if p.spec.Label == "itinerary" {
		var answer map[string]interface{}
		if json.Unmarshal(result.Result, &answer) == nil {
			data, ok := answer["data"].(map[string]interface{})
			expected = ok && answer["code"] == float64(200) && data["ip"] == "127.0.0.1" && data["city"] == "Shanghai"
		} else {
			expected = false
		}
	}
	return map[string]interface{}{"result_code": result.Code, "result": string(result.Result), "message": result.Message, "call_error": errtext, "expected_output": expected,
		"registry_gas_used": runtimeGasLimit - gas, "native_business_gas_used": before - after, "parameter_bytes": sc.B5Profile.ParameterSize,
		"writes_sha256": fmt.Sprintf("%x", sha256.Sum256(w)), "writes": string(w), "events": string(events), "cross_calls": cross.calls}
}
func s15State(t *testing.T, p *s15Prepared, f *s15Fresh) map[string]interface{} {
	values := map[string]interface{}{}
	for i := 0; i < p.spec.Globals; i++ {
		g, e := f.instance.Exports.GetGlobal(fmt.Sprintf("__s14_g%d", i))
		s15Must(t, e)
		v, e := g.Get()
		s15Must(t, e)
		values[fmt.Sprintf("g%d", i)] = v
	}
	for i := 0; i < p.spec.Tables; i++ {
		table, e := f.instance.Exports.GetTable(fmt.Sprintf("__s14_t%d", i))
		s15Must(t, e)
		values[fmt.Sprintf("t%d_size", i)] = uint64(table.Size())
	}
	return values
}
func s15Hash(f *s15Fresh) string { return fmt.Sprintf("%x", sha256.Sum256(f.memory.Data())) }

func s15SpecFromEnv(t *testing.T) s15Spec {
	b, e := os.ReadFile(os.Getenv("S15_MANIFEST"))
	s15Must(t, e)
	var specs []s15Spec
	s15Must(t, json.Unmarshal(b, &specs))
	for _, s := range specs {
		if s.Label == os.Getenv("S15_CONTRACT") {
			return s
		}
	}
	t.Fatal("contract not found")
	return s15Spec{}
}
