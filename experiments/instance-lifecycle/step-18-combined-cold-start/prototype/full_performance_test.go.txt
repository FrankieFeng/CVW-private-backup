//go:build step16

package wasmer

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"runtime"
	"runtime/debug"
	"strconv"
	"testing"

	logger2 "chainmaker.org/chainmaker/logger/v2"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	wasm "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
)

func step18Pool(t *testing.T, s s15Spec, contract string, enabled bool) *vmPool {
	key := "original"
	if enabled {
		key = "nodata"
	}
	os.Setenv("CM_STATIC_MEMORY_COPY", map[bool]string{false: "0", true: "1"}[enabled])
	os.Setenv("CM_FRESH_INVOKE", "1")
	os.Setenv("CM_STEP16_SERIALIZED_MODULE", step16Artifact(s, key))
	b, e := os.ReadFile(s.Paths["original"])
	s15Must(t, e)
	p, e := newVmPool(&commonPb.Contract{Name: contract, Version: "1.0.0", RuntimeType: commonPb.RuntimeType_WASMER}, b, logger2.GetLogger("step18"))
	s15Must(t, e)
	if enabled && p.staticPlan == nil {
		t.Fatalf("unexpected fallback: %s", p.staticFallback)
	}
	t.Cleanup(func() { p.module.Close(); p.store.Close() })
	return p
}

func TestStep18Pilot(t *testing.T) {
	// Initialize the same protocol limits as the node/step-16 fixture.
	os.Setenv("S15_CONTRACT", os.Getenv("S18_CONTRACT")+"-a0p0-"+os.Getenv("S18_MODE"))
	_ = step16Spec(t)
	b, e := os.ReadFile(os.Getenv("S15_MANIFEST"))
	s15Must(t, e)
	var specs []s15Spec
	s15Must(t, json.Unmarshal(b, &specs))
	contract, mode := os.Getenv("S18_CONTRACT"), os.Getenv("S18_MODE")
	n, e := strconv.Atoi(os.Getenv("S16_N"))
	s15Must(t, e)
	seed, e := strconv.ParseInt(os.Getenv("S16_SEED"), 10, 64)
	s15Must(t, e)
	out, e := os.OpenFile(os.Getenv("S16_OUT"), os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
	s15Must(t, e)
	defer out.Close()
	emit := func(v interface{}) { s15Must(t, json.NewEncoder(out).Encode(v)) }
	groups := 4
	full := os.Getenv("S18_FULL") == "1"
	if full {
		groups = 8
	}
	pools := make([]*vmPool, groups)
	selected := make([]s15Spec, groups)
	for j := 0; j < groups/2; j++ {
		a, pv := j, 0
		if full {
			a, pv = j/2, j%2
		}
		label := fmt.Sprintf("%s-a%dp%d-%s", contract, a, pv, mode)
		var s s15Spec
		for _, v := range specs {
			if v.Label == label {
				s = v
			}
		}
		if s.Label == "" {
			t.Fatal("missing build", label)
		}
		for c := 0; c < 2; c++ {
			k := j*2 + c
			p := step18Pool(t, s, contract, c == 1)
			pools[k] = p
			selected[k] = s
			if c == 1 {
				emit(map[string]interface{}{"kind": "module", "contract": contract, "A": a, "P": pv, "C": c, "mode": mode, "template_ns": p.staticPlan.PrecomputeNS, "template_bytes": len(p.staticPlan.Image), "range_metadata_bytes": len(p.staticPlan.Ranges) * 16, "template_sha256": fmt.Sprintf("%x", sha256.Sum256(p.staticPlan.Image)), "source_sha256": p.staticPlan.SourceSHA, "config_id": p.staticPlan.ConfigID})
			}
		}
	}
	rng := rand.New(rand.NewSource(seed))
	seen := map[string]bool{}
	runtime.GC()
	oldGC := debug.SetGCPercent(-1)
	defer debug.SetGCPercent(oldGC)
	for i := -5; i < n; i++ {
		if i >= 0 && i%20 == 0 {
			runtime.GC()
		}
		for pos, k := range rng.Perm(groups) {
			p, s := pools[k], selected[k]
			aFactor, pv := k/2, 0
			if full {
				aFactor, pv = k/4, (k/2)%2
			}
			s.Label = contract
			// Probe reads happen at S2, outside the plain performance run. They affect
			// probe S3/Invoke and are explicitly excluded from performance conclusions.
			var diagnostic map[string]interface{}
			if mode == "probe" {
				p.profileObserver = func(stage string, inst *wasm.Instance) {
					if stage != "S2" {
						return
					}
					fn, e := inst.Exports.GetRawFunction("Step18Read")
					s15Must(t, e)
					defer fn.Close()
					read := func(idx int32) int64 { v, e := fn.Call(idx); s15Must(t, e); return v.(int64) }
					begin, end, moduleEnd := read(0), read(1), read(3)
					reserveBloc, skipped, alignment := read(4), read(5), read(6)
					if aFactor == 1 && (reserveBloc != 4<<20 || skipped != 0 || alignment != 4<<20) {
						t.Fatalf("A first reserve missed: bloc=%d skip=%d align=%d", reserveBloc, skipped, alignment)
					}
					// Calibrate the host/guest monotonic clocks. Minimum RTT bounds uncertainty.
					best := int64(1 << 62)
					offset := int64(0)
					for j := 0; j < 7; j++ {
						h0 := step18MonoNow()
						g := read(2)
						h1 := step18MonoNow()
						if h1-h0 < best {
							best = h1 - h0
							offset = (h0+h1)/2 - g
						}
					}
					diagnostic = map[string]interface{}{"package_begin_host_mono_ns": begin + offset, "b1_ns": end - begin, "clock_uncertainty_ns": best / 2, "runtime_module_end": moduleEnd, "first_reserve_bloc": reserveBloc, "first_alignment_skip_bytes": skipped, "heap_alignment_bytes": alignment}
				}
			}
			row := step16Invoke(t, s, p)
			profile := p.lastCreated.initProfile
			id := row["instance_id"].(string)
			if seen[id] {
				t.Fatal("Instance reused")
			}
			seen[id] = true
			row["contract"] = contract
			row["A"] = aFactor
			row["P"] = pv
			row["C"] = k % 2
			row["mode"] = mode
			row["sample"] = i
			row["position"] = pos
			row["start_ns"] = profile.StartNS
			row["native_init_and_setgas_gas"] = uint64(10000000000000000000) - profile.NativeBeforeBusiness
			if mode == "probe" {
				for key, v := range diagnostic {
					row[key] = v
				}
				row["a_ns"] = diagnostic["package_begin_host_mono_ns"].(int64) - profile.StartMonoNS
				row["probe_observer_affects_s3_invoke"] = true
			}
			if i >= 0 {
				emit(row)
			}
		}
	}
}

func TestStep18Checks(t *testing.T) {
	contract := os.Getenv("S18_CONTRACT")
	os.Setenv("S15_CONTRACT", contract+"-a0p0-plain")
	_ = step16Spec(t)
	b, e := os.ReadFile(os.Getenv("S15_MANIFEST"))
	s15Must(t, e)
	var specs []s15Spec
	s15Must(t, json.Unmarshal(b, &specs))
	out, e := os.OpenFile(os.Getenv("S16_OUT"), os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
	s15Must(t, e)
	defer out.Close()
	enc := json.NewEncoder(out)
	pv := 0
	if os.Getenv("S18_P") == "1" {
		pv = 1
	}
	for a := 0; a < 2; a++ {
		label := fmt.Sprintf("%s-a%dp%d-plain", contract, a, pv)
		var s s15Spec
		for _, v := range specs {
			if v.Label == label {
				s = v
			}
		}
		for c := 0; c < 2; c++ {
			s.Label = label
			p := step18Pool(t, s, contract, c == 1)
			s.Label = contract
			s1Checks, s1Mismatch := 0, 0
			p.profileObserver = func(stage string, inst *wasm.Instance) {
				if stage == "S1" {
					m, e := inst.Exports.GetMemory("memory")
					s15Must(t, e)
					s1Checks++
					if fmt.Sprintf("%x", sha256.Sum256(m.Data())) != s.ImageSHA {
						s1Mismatch++
					}
				}
			}
			templateBefore := ""
			if c == 1 {
				templateBefore = fmt.Sprintf("%x", sha256.Sum256(p.staticPlan.Image))
			}
			success := step16Invoke(t, s, p)
			// Missing export exercises host dispatch failure, not a guest error branch.
			bad := s
			bad.Method = "__step18_missing_method__"
			bad.Expected = ""
			exception := step16Invoke(t, bad, p)
			var guestError map[string]interface{}
			if contract == "erc721" || contract == "fact" {
				negative := s
				negative.Expected = ""
				negative.Params = map[string]string{}
				for k, v := range s.Params {
					negative.Params[k] = v
				}
				if contract == "erc721" {
					negative.Params["tokenId"] = "not-a-number"
				} else {
					negative.Params["time"] = "not-a-number"
				}
				guestError = step16Invoke(t, negative, p)
			}
			peerA, e := p.NewInstance()
			s15Must(t, e)
			peerB, e := p.NewInstance()
			s15Must(t, e)
			ma, e := peerA.wasmInstance.Exports.GetMemory("memory")
			s15Must(t, e)
			mb, e := peerB.wasmInstance.Exports.GetMemory("memory")
			s15Must(t, e)
			before := sha256.Sum256(mb.Data())
			ma.Data()[0] ^= 255
			independent := before == sha256.Sum256(mb.Data())
			ma.Data()[0] ^= 255
			p.CloseInstance(peerA)
			p.CloseInstance(peerB)
			templateSame := true
			if c == 1 {
				templateSame = templateBefore == fmt.Sprintf("%x", sha256.Sum256(p.staticPlan.Image))
			}
			s15Must(t, enc.Encode(map[string]interface{}{"kind": "checks", "contract": contract, "A": a, "P": pv, "C": c, "s1_checks": s1Checks, "s1_mismatches": s1Mismatch, "fresh_memory_isolation": independent, "template_immutable": templateSame, "success": success, "exception": exception, "guest_error": guestError, "exception_scope": "host missing export; guest invalid numeric input for ERC721/fact only; no general traps/OOG", "cross_contract": "not_tested", "table_function_identity": "not_tested"}))
		}
	}
}
