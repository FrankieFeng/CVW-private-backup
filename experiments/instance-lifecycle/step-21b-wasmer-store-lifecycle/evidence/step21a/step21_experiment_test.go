package wasmer

import (
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"testing"
	"time"
)

var step21InputFile = flag.String("step21_inputs", "", "frozen per-call business parameters; no workload changes")

func step21LoadInputs(t *testing.T, n int) []map[string]string {
	if *step21InputFile == "" {
		return nil
	}
	b, err := os.ReadFile(*step21InputFile)
	if err != nil {
		t.Fatal(err)
	}
	var rows []map[string]string
	if err = json.Unmarshal(b, &rows); err != nil {
		t.Fatal(err)
	}
	if len(rows) < n {
		t.Fatal("not enough frozen input rows")
	}
	return rows
}

func step21InputMap(row map[string]string) map[string][]byte {
	r := make(map[string][]byte, len(row))
	for k, v := range row {
		r[k] = []byte(v)
	}
	return r
}

func step21Sample(i int, method string, params map[string][]byte, r *commonPb.ContractResult, begin, end int64, total, call float64) {
	b, _ := json.Marshal(params)
	step21Emit(map[string]interface{}{
		"event": "sample", "index": i, "method": method, "begin_ns": begin, "end_ns": end,
		"invoke_s": total, "callmethod_s": call, "code": r.Code, "gas": r.GasUsed,
		"result": r.Result, "message": r.Message, "input_sha256": fmt.Sprintf("%x", sha256.Sum256(b)),
	})
}

// Drain only after all measured InvokeTime calls. No added wait between calls.
func step21Quiesce(t *testing.T, p *vmPool) {
	if !step21Enabled {
		return
	}
	done := make(chan struct{})
	go func() { p.step21Tasks.Wait(); close(done) }()
	select {
	case <-done:
	case <-time.After(5 * time.Second):
		t.Fatal("step21 maintenance drain timeout")
	}
	ack := make(chan struct{})
	select {
	case p.step21Barrier <- ack:
	case <-time.After(5 * time.Second):
		t.Fatal("step21 worker barrier timeout")
	}
	select {
	case <-ack:
	case <-time.After(5 * time.Second):
		t.Fatal("step21 worker acknowledgement timeout")
	}
	step21Emit(map[string]interface{}{"event": "drained", "queue_len": len(p.instances)})
}

func step21ClosePool(t *testing.T, p *vmPool) {
	if !step21Enabled {
		p.close()
		return
	}
	step21Quiesce(t, p)
	p.close()
	select {
	case <-p.step21Done:
		step21Emit(map[string]interface{}{"event": "closed", "worker_exited": true})
	case <-time.After(5 * time.Second):
		t.Error("step21 pool shutdown timeout")
	}
}
