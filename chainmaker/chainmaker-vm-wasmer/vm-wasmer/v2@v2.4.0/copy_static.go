package wasmer

import (
	"bytes"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	wasm "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"fmt"
	"sort"
)

type staticRange struct{ Begin, End int }
type staticMemoryPlan struct {
	ConfigID string
	Image    []byte
	Ranges   []staticRange
	Module   *wasm.Module
	NoData   []byte
}

type staticReader struct {
	b []byte
	p int
}

func (r *staticReader) byte() byte {
	if r.p >= len(r.b) {
		panic("truncated binary")
	}
	v := r.b[r.p]
	r.p++
	return v
}
func (r *staticReader) u() int {
	v, s := uint64(0), uint(0)
	for i := 0; i < 5; i++ {
		b := r.byte()
		v |= uint64(b&127) << s
		if b < 128 {
			if v > 1<<32-1 {
				panic("ULEB32 overflow")
			}
			return int(v)
		}
		s += 7
	}
	panic("ULEB32 overflow")
}
func (r *staticReader) signed() int {
	v, s := int64(0), uint(0)
	for i := 0; i < 5; i++ {
		b := r.byte()
		v |= int64(b&127) << s
		s += 7
		if b < 128 {
			if b&64 != 0 {
				v |= -(1 << s)
			}
			if v < 0 || v > 1<<31-1 {
				panic("negative/overflow offset")
			}
			return int(v)
		}
	}
	panic("SLEB32 overflow")
}
func (r *staticReader) take(n int) []byte {
	if n < 0 || r.p+n > len(r.b) {
		panic("truncated section")
	}
	v := r.b[r.p : r.p+n]
	r.p += n
	return v
}
func (r *staticReader) name() string { return string(r.take(r.u())) }

func prepareStaticMemory(source []byte, c *commonPb.Contract, config string) (plan *staticMemoryPlan, err error) {
	defer func() {
		if v := recover(); v != nil {
			plan = nil
			err = fmt.Errorf("unsupported static template: %v", v)
		}
	}()
	if len(source) < 8 || !bytes.Equal(source[:8], []byte{0, 97, 115, 109, 1, 0, 0, 0}) {
		return nil, fmt.Errorf("not wasm v1")
	}
	plan = &staticMemoryPlan{ConfigID: config}
	r := staticReader{b: source, p: 8}
	out := append([]byte{}, source[:8]...)
	var data []byte
	memories := 0
	memoryExport := false
	for r.p < len(source) {
		start := r.p
		k := r.byte()
		payload := r.take(r.u())
		q := staticReader{b: payload}
		switch k {
		case 2:
			n := q.u()
			for i := 0; i < n; i++ {
				q.name()
				q.name()
				if q.byte() != 0 {
					panic("non-function import (memory/global/table/tag)")
				}
				q.u()
			}
		case 5:
			if q.u() != 1 {
				panic("requires one local memory")
			}
			flags := q.u()
			if flags != 0 && flags != 1 {
				panic("shared/memory64 memory")
			}
			pages := q.u()
			if pages > 512 {
				panic("initial memory exceeds limit")
			}
			if flags == 1 {
				q.u()
			}
			memories++
			plan.Image = make([]byte, pages*65536)
		case 7:
			n := q.u()
			for i := 0; i < n; i++ {
				name := q.name()
				kind, index := q.byte(), q.u()
				if name == "memory" && kind == 2 && index == 0 {
					memoryExport = true
				}
			}
		case 8:
			panic("automatic start executes before host copy")
		case 9:
			// Only active MVP funcref element segments with constant offsets.
			n := q.u()
			for i := 0; i < n; i++ {
				if q.u() != 0 {
					panic("complex/passive element segment")
				}
				if q.byte() != 0x41 {
					panic("complex table offset")
				}
				q.signed()
				if q.byte() != 0x0b {
					panic("complex table offset expr")
				}
				count := q.u()
				for j := 0; j < count; j++ {
					q.u()
				}
			}
		case 11:
			data = payload
		case 12:
			panic("DataCount/data-index semantics")
		}
		if k != 11 {
			out = append(out, source[start:r.p]...)
		}
	}
	if memories != 1 || !memoryExport {
		return nil, fmt.Errorf("requires exported single local memory")
	}
	if data != nil {
		q := staticReader{b: data}
		count := q.u()
		for i := 0; i < count; i++ {
			flags := q.u()
			if flags == 2 {
				if q.u() != 0 {
					panic("nonzero memory index")
				}
			} else if flags != 0 {
				panic("passive/unsupported data")
			}
			if q.byte() != 0x41 {
				panic("complex data offset")
			}
			a := q.signed()
			if q.byte() != 0x0b {
				panic("complex data expression")
			}
			payload := q.take(q.u())
			b := a + len(payload)
			if len(payload) == 0 || b > len(plan.Image) {
				panic("zero-length/out-of-bounds segment")
			}
			copy(plan.Image[a:b], payload)
			plan.Ranges = append(plan.Ranges, staticRange{a, b})
		}
		if q.p != len(data) {
			panic("trailing data")
		}
	}
	sort.Slice(plan.Ranges, func(i, j int) bool { return plan.Ranges[i].Begin < plan.Ranges[j].Begin })
	union := make([]staticRange, 0, len(plan.Ranges))
	for _, r := range plan.Ranges {
		n := len(union)
		if n > 0 && r.Begin <= union[n-1].End {
			if r.End > union[n-1].End {
				union[n-1].End = r.End
			}
		} else {
			union = append(union, r)
		}
	}
	nonzero := make([]staticRange, 0, len(union))
	for _, r := range union {
		for _, b := range plan.Image[r.Begin:r.End] {
			if b != 0 {
				nonzero = append(nonzero, r)
				break
			}
		}
	}
	plan.Ranges = nonzero
	plan.NoData = out
	return plan, nil
}
func (p *staticMemoryPlan) restore(module *wasm.Module, instance *wasm.Instance, source []byte, contract *commonPb.Contract, config string) error {
	if p.Module != module || p.ConfigID != config {
		return fmt.Errorf("static template module/config mismatch")
	}
	// Key is bound at pool construction; recomputing SHA over the original WASM per
	// instance would defeat amortization. Source bytes are private immutable copies.
	memory, e := instance.Exports.GetMemory("memory")
	if e != nil {
		return e
	}
	dst := memory.Data()
	if len(dst) != len(p.Image) {
		return fmt.Errorf("static template memory length mismatch")
	}
	for _, r := range p.Ranges {
		copy(dst[r.Begin:r.End], p.Image[r.Begin:r.End])
	}
	return nil
}
