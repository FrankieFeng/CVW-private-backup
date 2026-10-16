package wasmer

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"runtime"
	"sync"
	"time"

	wasmergo "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
)

// Diagnostic only: enable with CM_INSTANCE_LIFECYCLE_TRACE=1.
// Call while the caller owns the instance; never inspect it after enqueue/Close.
var lifecycleOutputMu sync.Mutex
var lifecycleSequence uint64

func lifecycleError(err error) string {
	if err != nil {
		return err.Error()
	}
	return ""
}

func (p *vmPool) traceLifecycle(stage, id string, inst *wasmergo.Instance, event, errText string) {
	if os.Getenv("CM_INSTANCE_LIFECYCLE_TRACE") != "1" {
		return
	}
	row := map[string]interface{}{"stage": stage, "event": event, "instance_id": id, "module_id": fmt.Sprintf("%p", p.module), "store_id": fmt.Sprintf("%p", p.store), "contract": p.contractKey(), "timestamp": time.Now().Format(time.RFC3339Nano), "error": errText}
	if inst != nil {
		row["wasm_instance_ptr"] = fmt.Sprintf("%p", inst)
		memory, err := inst.Exports.GetMemory("memory")
		if err != nil {
			row["memory_error"] = err.Error()
		} else {
			data := memory.Data()
			row["bytes"] = len(data)
			row["pages"] = uint64(memory.Size())
			row["sha256"] = fmt.Sprintf("%x", sha256.Sum256(data))
			if len(data) > 0 {
				row["memory_ptr"] = fmt.Sprintf("%p", &data[0])
			}
			runtime.KeepAlive(inst)
		}
	}
	lifecycleOutputMu.Lock()
	defer lifecycleOutputMu.Unlock()
	lifecycleSequence++
	row["seq"] = lifecycleSequence
	b, _ := json.Marshal(row)
	fmt.Printf("LIFECYCLE %s\n", b)
}

func (sc *SimContext) traceBusiness(event string, inst *wasmergo.Instance, err error) {
	if sc.lifecyclePool != nil {
		sc.lifecyclePool.traceLifecycle("business", sc.lifecycleID, inst, event, lifecycleError(err))
	}
}
