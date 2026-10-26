package wasmer

// Experiment-only detection. No waiting, execution lock, or changed InvokeTime boundary.
import (
	"encoding/json"
	"fmt"
	"os"
	"runtime"
	"sync/atomic"
	"time"
)

var step21aGuardEnabled = os.Getenv("CM_STEP21A_STORE_GUARD") == "1"
var step21aPoolCapacity = func() bool {
	switch os.Getenv("CM_STEP21A_POOL") {
	case "capacity":
		return true
	case "original":
		return false
	default:
		panic("CM_STEP21A_POOL must be original or capacity")
	}
}()

func (p *vmPool) step21aEnter(op int32) {
	if !step21aGuardEnabled {
		return
	}
	if atomic.CompareAndSwapInt32(&p.step21aNativeOwner, 0, op) {
		return
	}
	owner := atomic.LoadInt32(&p.step21aNativeOwner)
	row, _ := json.Marshal(map[string]interface{}{"event": "store_region_overlap_prevented", "requested": op, "owner": owner, "pool_capacity_fix": step21aPoolCapacity, "queue_len": len(p.instances), "unix_ns": time.Now().UnixNano(), "scope": "coarse create/execute/close regions; no claim a native data race occurred"})
	fmt.Fprintf(os.Stderr, "STEP21A_GUARD %s\n", row)
	stacks := make([]byte, 2*1024*1024)
	n := runtime.Stack(stacks, true)
	os.Stderr.Write(stacks[:n])
	os.Exit(86) // before the denied region touches native state; no deferred cleanup race
}
func (p *vmPool) step21aLeave(op int32) {
	if !step21aGuardEnabled {
		return
	}
	if !atomic.CompareAndSwapInt32(&p.step21aNativeOwner, op, 0) {
		panic("Step21A native region ownership mismatch")
	}
}
