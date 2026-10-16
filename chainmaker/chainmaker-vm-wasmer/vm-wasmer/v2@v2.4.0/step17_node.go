// Experiment-only node observations. Never enabled in a production checkout.
package wasmer

import (
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	"encoding/json"
	"fmt"
	"os"
	"sync"
	"sync/atomic"
	"time"
)

var step17OutMu sync.Mutex
var step17Hits, step17Misses uint64

func step17Emit(row map[string]interface{}) {
	if os.Getenv("CM_STEP17_OBSERVE") != "1" {
		return
	}
	b, err := json.Marshal(row)
	if err != nil {
		panic(err)
	}
	step17OutMu.Lock()
	defer step17OutMu.Unlock()
	fmt.Printf("STEP17 %s\n", b)
}
func step17Cache(p *vmPool, hit bool) {
	if hit {
		atomic.AddUint64(&step17Hits, 1)
	} else {
		atomic.AddUint64(&step17Misses, 1)
	}
}
func step17Pool(p *vmPool) {
	row := map[string]interface{}{"kind": "pool", "contract": p.contractId.Name, "version": p.contractId.Version, "source_sha": staticSHA(p.byteCode), "config_id": p.staticConfig, "fallback": p.staticFallback, "fresh": p.freshOnDemand, "template_bytes": 0, "range_count": 0, "copy_bytes": 0, "precompute_ns": 0}
	if q := p.staticPlan; q != nil {
		n := 0
		for _, r := range q.Ranges {
			n += r.End - r.Begin
		}
		row["template_bytes"] = len(q.Image)
		row["range_count"] = len(q.Ranges)
		row["copy_bytes"] = n
		row["precompute_ns"] = q.PrecomputeNS
		row["template_sha"] = staticSHA(q.Image)
		row["key"] = q.Key
	}
	step17Emit(row)
}
func step17Invoke(p *vmPool, w *wrappedInstance, c *commonPb.Contract, method string, tx protocol.TxSimContext, result *commonPb.ContractResult, begin time.Time) {
	if w == nil {
		return
	}
	q := w.initProfile
	row := map[string]interface{}{"kind": "invoke", "tx_id": tx.GetTx().Payload.TxId, "depth": tx.GetDepth(), "contract": c.Name, "method": method, "instance_id": w.id, "optimized": p.staticPlan != nil, "s1_ns": q.S1NS, "s2_ns": q.S2NS, "s3_ns": q.S3NS, "copy_ns": q.CopyNS, "invoke_ns": time.Since(begin).Nanoseconds(), "cache_hits": atomic.LoadUint64(&step17Hits), "cache_misses": atomic.LoadUint64(&step17Misses)}
	if result != nil {
		row["code"] = result.Code
		row["gas"] = result.GasUsed
		row["result_sha"] = staticSHA(result.Result)
	}
	step17Emit(row)
}
