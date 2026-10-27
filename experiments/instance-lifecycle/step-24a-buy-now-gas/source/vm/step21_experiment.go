// Step21 experiment-only observations. No Store mutex or reuse policy change.
package wasmer

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
)

var step21Enabled = os.Getenv("CM_STEP21_OBSERVE") == "1"

func step21Emit(row map[string]interface{}) {
	if !step21Enabled {
		return
	}
	b, err := json.Marshal(row)
	if err != nil {
		panic(err)
	}
	fmt.Printf("STEP21 %s\n", b)
}

func (p *vmPool) step21Acquire(w *wrappedInstance, begin time.Time, wait time.Duration, blocked bool) {
	id := ""
	if w != nil {
		id = w.id
	}
	step21Emit(map[string]interface{}{
		"event": "acquire", "unix_ns": time.Now().UnixNano(), "instance_id": id,
		"getinstance_ns": time.Since(begin).Nanoseconds(), "channel_receive_ns": wait.Nanoseconds(),
		"empty_branch": blocked, "queue_after_receive": len(p.instances),
	})
}
