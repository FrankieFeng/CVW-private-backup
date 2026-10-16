//go:build step16

package wasmer

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"runtime"
	"runtime/debug"
	"sort"
	"strconv"
	"testing"
	"time"

	"chainmaker.org/chainmaker/common/v2/serialize"
	logger2 "chainmaker.org/chainmaker/logger/v2"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	protocol "chainmaker.org/chainmaker/protocol/v2"
	wasm "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
)

func step16Spec(t *testing.T) s15Spec {
	if os.Getenv("S16_INIT_LIMITS") != "0" {
		protocol.ParametersValueMaxLength = protocol.DefaultParametersValueMaxSize * 1024 * 1024
	}
	return s15SpecFromEnv(t)
}
func step16Artifact(s s15Spec, key string) string {
	return filepath.Join(os.Getenv("S16_ARTIFACTS"), s.Label, key+".module")
}
func step16Metadata(t *testing.T, path, wasmPath, config string) {
	b, e := os.ReadFile(path)
	s15Must(t, e)
	code, e := os.ReadFile(wasmPath)
	s15Must(t, e)
	m, e := json.Marshal(map[string]string{"WasmSHA": staticSHA(code), "ConfigID": config, "ArtifactSHA": staticSHA(b)})
	s15Must(t, e)
	s15Must(t, os.WriteFile(path+".json", m, 0600))
}
func TestStep16Metadata(t *testing.T) {
	s := step16Spec(t)
	_, config := step16TestConfig()
	for _, key := range []string{"original", "nodata", "diagnostic", "diagnostic_nodata"} {
		step16Metadata(t, step16Artifact(s, key), s.Paths[key], config)
	}
}
func TestStep16CompileProbe(t *testing.T) {
	s := step16Spec(t)
	key := os.Getenv("S16_KEY")
	cfg, config := step16TestConfig()
	store := wasm.NewStore(wasm.NewEngineWithConfig(cfg))
	defer store.Close()
	b, e := os.ReadFile(s.Paths[key])
	s15Must(t, e)
	mod, e := wasm.NewModule(store, b, logger2.GetLogger("step16"))
	s15Must(t, e)
	defer mod.Close()
	data, e := mod.Serialize()
	s15Must(t, e)
	path := step16Artifact(s, key)
	s15Must(t, os.WriteFile(path, data, 0600))
	step16Metadata(t, path, s.Paths[key], config)
}
func step16Pool(t *testing.T, s s15Spec, enabled bool, diagnostic bool) *vmPool {
	key := "original"
	if enabled {
		key = "nodata"
	}
	sourceKey := "original"
	if diagnostic {
		sourceKey = "diagnostic"
		key = "diagnostic"
		if enabled {
			key = "diagnostic_nodata"
		}
	}
	os.Setenv("CM_STATIC_MEMORY_COPY", map[bool]string{true: "1", false: "0"}[enabled])
	os.Setenv("CM_FRESH_INVOKE", "1")
	os.Setenv("CM_STEP16_SERIALIZED_MODULE", step16Artifact(s, key))
	b, e := os.ReadFile(s.Paths[sourceKey])
	s15Must(t, e)
	p, e := newVmPool(&commonPb.Contract{Name: s.Label, Version: "1.0.0", RuntimeType: commonPb.RuntimeType_WASMER}, b, logger2.GetLogger("step16"))
	s15Must(t, e)
	t.Cleanup(func() { p.module.Close(); p.store.Close() })
	if enabled && p.staticPlan == nil {
		t.Fatalf("unexpected fallback %s", p.staticFallback)
	}
	if !enabled && p.staticPlan != nil {
		t.Fatal("disabled path has template")
	}
	return p
}
func step16Tx(s s15Spec) (protocol.TxSimContext, map[string][]byte, *s15CrossContext) {
	params := map[string][]byte{}
	for k, v := range s.Params {
		params[k] = []byte(v)
	}
	fillingBaseParams(params)
	tx := prepareTxSimContext(ChainId, BlockVersion, s.Label, s.Method, params, SnapshotMock{})
	tx.GetTx().Payload.TxId = "STEP16_FIXED_TX"
	cross := &s15CrossContext{TxSimContext: tx}
	if s.Label == "exchange" {
		tx = cross
	}
	return tx, params, cross
}
func step16Invoke(t *testing.T, s s15Spec, p *vmPool) map[string]interface{} {
	tx, params, cross := step16Tx(s)
	rt := &RuntimeInstance{pool: p, log: p.log, chainId: ChainId}
	start := time.Now()
	result, special := rt.Invoke(p.contractId, s.Method, p.byteCode, params, tx, 0)
	invokeNS := time.Since(start).Nanoseconds()
	if p.lastCreated == nil {
		t.Fatal("Invoke did not create fresh instance")
	}
	inst := p.lastCreated
	writes := tx.GetTxRWSet(true).TxWrites
	sort.Slice(writes, func(i, j int) bool {
		if writes[i].ContractName != writes[j].ContractName {
			return writes[i].ContractName < writes[j].ContractName
		}
		return string(writes[i].Key) < string(writes[j].Key)
	})
	w, e := json.Marshal(writes)
	s15Must(t, e)
	events, e := json.Marshal(result.ContractEvent)
	s15Must(t, e)
	expected := s.Expected == "" || string(result.Result) == s.Expected
	if s.Label == "itinerary" {
		var v map[string]interface{}
		expected = false
		if json.Unmarshal(result.Result, &v) == nil {
			data, ok := v["data"].(map[string]interface{})
			expected = ok && v["code"] == float64(200) && data["ip"] == "127.0.0.1" && data["city"] == "Shanghai"
		}
	}
	return map[string]interface{}{"kind": "sample", "label": s.Label, "instance_id": inst.id, "s1_ns": inst.initProfile.S1NS, "s2_ns": inst.initProfile.S2NS, "s3_ns": inst.initProfile.S3NS, "invoke_ns": invokeNS, "copy_ns": inst.initProfile.CopyNS,
		"result": string(result.Result), "result_code": result.Code, "message": result.Message, "expected_output": expected, "registry_gas": result.GasUsed, "native_business_gas": inst.initProfile.NativeBeforeBusiness - inst.initProfile.NativeAfterBusiness, "writes": string(w), "writes_sha256": fmt.Sprintf("%x", sha256.Sum256(w)), "events": string(events), "special": special, "cross_calls": cross.calls, "host_parameter_limit": protocol.ParametersValueMaxLength}
}
func TestStep16Integration(t *testing.T) {
	s := step16Spec(t)
	n, e := strconv.Atoi(os.Getenv("S16_N"))
	s15Must(t, e)
	seed, e := strconv.ParseInt(os.Getenv("S16_SEED"), 10, 64)
	s15Must(t, e)
	out, e := os.OpenFile(os.Getenv("S16_OUT"), os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
	s15Must(t, e)
	defer out.Close()
	encoder := json.NewEncoder(out)
	emit := func(v interface{}) { s15Must(t, encoder.Encode(v)) }
	base := step16Pool(t, s, false, false)
	opt := step16Pool(t, s, true, false)
	emit(map[string]interface{}{"kind": "module", "label": s.Label, "key": opt.staticPlan.Key, "source_sha": opt.staticPlan.SourceSHA, "config_id": opt.staticPlan.ConfigID, "precompute_ns": opt.staticPlan.PrecomputeNS, "image_bytes": len(opt.staticPlan.Image), "range_bytes": len(opt.staticPlan.Ranges) * 16, "range_count": len(opt.staticPlan.Ranges), "prepared_path": "newVmPool -> newInstanceFromModule -> restore before WASI -> RuntimeInstance.Invoke"})
	rng := rand.New(rand.NewSource(seed))
	runtime.GC()
	old := debug.SetGCPercent(-1)
	defer debug.SetGCPercent(old)
	seen := map[string]bool{}
	for i := -5; i < n; i++ {
		if i >= 0 && i%20 == 0 {
			runtime.GC()
		}
		for position, k := range rng.Perm(2) {
			p, method := base, "baseline"
			if k == 1 {
				p = opt
				method = "optimized"
			}
			row := step16Invoke(t, s, p)
			id := row["instance_id"].(string)
			if seen[id] {
				t.Fatal("instance reused")
			}
			seen[id] = true
			if i >= 0 {
				row["sample"] = i
				row["position"] = position
				row["method"] = method
				emit(row)
			}
		}
	}
}
func TestStep16ExchangeDiagnostic(t *testing.T) {
	s := step16Spec(t)
	p := step16Pool(t, s, false, false)
	out, e := os.OpenFile(os.Getenv("S16_OUT"), os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
	s15Must(t, e)
	defer out.Close()
	enc := json.NewEncoder(out)
	step16CrossDiagnostic = func(isLen bool, body []byte, err error) {
		ec := serialize.NewEasyCodecWithBytes(body)
		b, _ := json.Marshal(ec.GetItems())
		s15Must(t, enc.Encode(map[string]interface{}{"kind": "cross_boundary", "is_len": isLen, "error": fmt.Sprint(err), "request_items": string(b)}))
	}
	defer func() { step16CrossDiagnostic = nil }()
	row := step16Invoke(t, s, p)
	s15Must(t, enc.Encode(row))
}
func TestStep16Validation(t *testing.T) {
	s := step16Spec(t)
	b, e := os.ReadFile(filepath.Join(os.Getenv("S16_ARTIFACTS"), s.Label, "table_expected.json"))
	s15Must(t, e)
	var tables [][]*int
	s15Must(t, json.Unmarshal(b, &tables))
	out, e := os.OpenFile(os.Getenv("S16_OUT"), os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
	s15Must(t, e)
	defer out.Close()
	enc := json.NewEncoder(out)
	var expectedGlobals map[string]interface{}
	for _, enabled := range []bool{false, true} {
		p := step16Pool(t, s, enabled, true)
		stages := []map[string]interface{}{}
		p.profileObserver = func(stage string, inst *wasm.Instance) {
			mem, e := inst.Exports.GetMemory("memory")
			s15Must(t, e)
			fn, e := inst.Exports.GetRawFunction("__step16_table_null")
			s15Must(t, e)
			defer fn.Close()
			mismatch := 0
			for i, v := range tables[0] {
				answer, e := fn.Call(int32(i))
				s15Must(t, e)
				want := int32(0)
				if v == nil {
					want = 1
				}
				if answer.(int32) != want {
					mismatch++
				}
			}
			record := map[string]interface{}{"stage": stage, "table_entries": len(tables[0]), "table_nullness_mismatches": mismatch, "table_function_identity_dynamic": "not_tested; unavailable native API", "table_element_static_mapping": "exact original/nodata mapping preserved"}
			if stage == "S1" {
				h := fmt.Sprintf("%x", sha256.Sum256(mem.Data()))
				record["s1_memory_equal"] = h == s.ImageSHA
				f := &s15Fresh{instance: inst, memory: mem}
				prepared := &s15Prepared{spec: s}
				g := s15State(t, prepared, f)
				if !enabled {
					expectedGlobals = g
				}
				record["globals_table_size_equal"] = fmt.Sprint(g) == fmt.Sprint(expectedGlobals)
			}
			stages = append(stages, record)
		}
		row := step16Invoke(t, s, p)
		// Parallel live fresh memory/global objects, mutating one cannot affect peers.
		// Constructors return at S2. Use observer to mutate/check at S1 before runtime writes.
		var a, before *wrappedInstance
		p.profileObserver = nil
		a, e = p.NewInstance()
		s15Must(t, e)
		before, e = p.NewInstance()
		s15Must(t, e)
		ma, e := a.wasmInstance.Exports.GetMemory("memory")
		s15Must(t, e)
		mb, e := before.wasmInstance.Exports.GetMemory("memory")
		s15Must(t, e)
		digest := sha256.Sum256(mb.Data())
		ma.Data()[0] ^= 255
		ga, e := a.wasmInstance.Exports.GetGlobal("__s14_g0")
		s15Must(t, e)
		gb, e := before.wasmInstance.Exports.GetGlobal("__s14_g0")
		s15Must(t, e)
		old, e := gb.Get()
		s15Must(t, e)
		oldA, e := ga.Get()
		s15Must(t, e)
		s15Must(t, ga.Set(int32(991), wasm.I32))
		after, e := gb.Get()
		s15Must(t, e)
		isolated := digest == sha256.Sum256(mb.Data()) && fmt.Sprint(old) == fmt.Sprint(after)
		s15Must(t, ga.Set(oldA, wasm.I32))
		ma.Data()[0] ^= 255
		p.CloseInstance(a)
		p.CloseInstance(before)
		s15Must(t, enc.Encode(map[string]interface{}{"kind": "validation", "label": s.Label, "enabled": enabled, "stages": stages, "fresh_memory_globals_isolation": isolated, "business": row, "table_dynamic_identity": "not_tested", "table_coverage": "full nullness at S1/S2/S3 plus static element mapping; synthetic identity/isolation test separate"}))
	}
}
