// Experiment-only trace, enabled solely for step-19 transaction IDs.
package step19trace

import (
	"encoding/json"
	"fmt"
	"golang.org/x/sys/unix"
	"os"
	"strings"
)

func Emit(tx, stage string) {
	if os.Getenv("CM_STEP19_TRACE") != "1" || !strings.HasPrefix(tx, "1919") {
		return
	}
	var t unix.Timespec
	if e := unix.ClockGettime(unix.CLOCK_MONOTONIC, &t); e != nil {
		panic(e)
	}
	b, _ := json.Marshal(map[string]interface{}{"tx_id": tx, "stage": stage, "mono_ns": t.Nano()})
	fmt.Printf("STEP19 %s\n", b)
}
