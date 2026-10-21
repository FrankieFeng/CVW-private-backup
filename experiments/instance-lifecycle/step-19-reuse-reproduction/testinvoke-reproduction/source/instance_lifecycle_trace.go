package wasmer

import (
	wasmergo "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"encoding/json"
	"fmt"
	"os"
	"sync"
	"time"
)

var reuseExperimentEnabled = func() bool {
	policy := os.Getenv("CM_REUSE_EXPERIMENT")
	if policy != "R0" && policy != "R1" {
		panic("CM_REUSE_EXPERIMENT must explicitly be R0 or R1")
	}
	return policy == "R0"
}()
var reuseOutputMu sync.Mutex

func lifecycleError(err error) string {
	if err != nil {
		return err.Error()
	}
	return ""
}
func (p *vmPool) reuseObserve(event, id string, elapsed int64) {
	row := map[string]interface{}{"event": event, "instance_id": id, "contract": p.contractKey(), "unix_ns": time.Now().UnixNano(), "elapsed_ns": elapsed, "queue_len": len(p.instances)}
	reuseOutputMu.Lock()
	defer reuseOutputMu.Unlock()
	b, _ := json.Marshal(row)
	fmt.Printf("REUSE_EVENT %s\n", b)
}
func (p *vmPool) traceLifecycle(stage, id string, inst *wasmergo.Instance, event, errText string) {
	p.reuseObserve(event, id, 0)
}
func (sc *SimContext) traceBusiness(event string, inst *wasmergo.Instance, err error) {
	if sc.lifecyclePool != nil {
		sc.lifecyclePool.traceLifecycle("business", sc.lifecycleID, inst, event, lifecycleError(err))
	}
}
