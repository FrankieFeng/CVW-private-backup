package wasmer

import (
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"os"
)

type a24Layout struct {
	SHA              string `json:"wasm_sha"`
	Encoder          uint64 `json:"encoder_cache"`
	Fields           uint64 `json:"field_cache"`
	PointerType      uint64 `json:"target_pointer_type"`
	StructType       uint64 `json:"target_struct_type"`
	Itab             uint64 `json:"reflect_type_interface_itab"`
	EncoderValueType uint64 `json:"encoder_func_value_type"`
	Elements         map[string]struct {
		Index int    `json:"function_index"`
		Name  string `json:"name"`
	} `json:"table_element_map"`
}

var a24LayoutConfig = func() a24Layout {
	var x a24Layout
	if os.Getenv("A24_LAYOUT") == "" {
		return x
	}
	b, e := os.ReadFile(os.Getenv("A24_LAYOUT"))
	if e != nil {
		panic(e)
	}
	if json.Unmarshal(b, &x) != nil {
		panic("invalid verified cache layout")
	}
	return x
}()

func a24ReservedMode() bool { x := os.Getenv("A24_MODE"); return x == "S0" || x == "J" || x == "U" }
func a24Range(d []byte, p, n uint64) []byte {
	if p > uint64(len(d)) || n > uint64(len(d))-p {
		panic(fmt.Sprintf("cache pointer out of bounds: %d/%d/%d", p, n, len(d)))
	}
	return d[p : p+n]
}
func a24U64(d []byte, p uint64) uint64 { return binary.LittleEndian.Uint64(a24Range(d, p, 8)) }
func a24ReadMap(d []byte, base uint64, encoder bool) map[string]interface{} {
	cfg := a24LayoutConfig
	inited := binary.LittleEndian.Uint32(a24Range(d, base, 4))
	root := a24U64(d, base+16)
	if inited > 1 {
		panic("invalid map init flag")
	}
	entries := []map[string]interface{}{}
	seen := map[uint64]bool{}
	keys := map[uint64]bool{}
	var walk func(uint64)
	walk = func(p uint64) {
		if p == 0 {
			return
		}
		if len(seen) > 2048 || seen[p] {
			panic("cache node cycle/budget")
		}
		seen[p] = true
		tag := a24Range(d, p, 1)[0]
		if tag == 0 {
			a24Range(d, p, 24+16*8)
			for j := uint64(0); j < 16; j++ {
				walk(a24U64(d, p+24+8*j))
			}
			return
		}
		if tag != 1 {
			panic("invalid cache node tag")
		}
		a24Range(d, p, 48)
		keyItab, key := a24U64(d, p+16), a24U64(d, p+24)
		if keyItab != cfg.Itab || key == 0 || keys[key] {
			panic("cache key layout/uniqueness mismatch")
		}
		keys[key] = true
		a24Range(d, key, 48)
		typ, value := a24U64(d, p+32), a24U64(d, p+40)
		if encoder && typ != cfg.EncoderValueType {
			panic("unexpected encoder value type")
		}
		row := map[string]interface{}{"node": p, "key_itab": keyItab, "key_type": key, "value_type": typ, "value_data": value}
		if encoder && value != 0 {
			word := a24U64(d, value)
			row["function_word"] = word
			if symbol, ok := cfg.Elements[fmt.Sprint(word>>16)]; ok && word&65535 == 0 {
				row["static_pc_symbol"] = symbol.Name
				row["static_function_index"] = symbol.Index
			}
		}
		entries = append(entries, row)
		if len(entries) > 512 {
			panic("cache entry budget")
		}
		walk(a24U64(d, p+8))
	}
	if inited == 0 {
		if root != 0 {
			panic("cache init incomplete at checkpoint")
		}
	} else {
		if root == 0 {
			panic("initialized cache has no root")
		}
		walk(root)
	}
	return map[string]interface{}{"base": base, "initialized": inited, "root": root, "node_count": len(seen), "entries": entries, "target_pointer_present": keys[cfg.PointerType], "target_struct_present": keys[cfg.StructType]}
}
func a24Snapshot(inst *w.Instance, label string, call *a23Call) {
	if !eTraceEnabled || os.Getenv("A24_CACHE_READ") != "1" {
		return
	}
	w.ManagedAssert()
	if eSlots["erc721"].SHA != a24LayoutConfig.SHA {
		panic("cache layout WASM mismatch")
	}
	mem, e := inst.Exports.GetMemory("memory")
	if e != nil {
		panic(e)
	}
	d := mem.Data()
	record := map[string]interface{}{"event": "json_cache", "checkpoint": label, "mode": os.Getenv("A24_MODE"), "encoder": a24ReadMap(d, a24LayoutConfig.Encoder, true), "fields": a24ReadMap(d, a24LayoutConfig.Fields, false), "memory_bytes": len(d), "wasm_sha": a24LayoutConfig.SHA}
	if call != nil {
		record["call_id"] = call.CallID
		record["contract"] = call.Contract
		record["method"] = call.Method
		record["tx_id"] = call.TxID
		record["instance_id"] = call.InstanceID
		record["instance_uses_before"] = call.UsesBefore
	}
	eEmit(record)
}
func a24CacheBoundary(sc *SimContext, phase, host, when string) {
	if !eTraceEnabled || sc.Contract.Name != "erc721" {
		return
	}
	if phase == "business" || (host == "DeleteState" && when == "after") || (host == "log_message" && when == "before") {
		a24Snapshot(sc.Instance, phase+"/"+host+"/"+when, a23Calls[sc])
	}
}
