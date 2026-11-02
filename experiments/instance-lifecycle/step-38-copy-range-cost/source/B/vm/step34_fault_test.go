package wasmer

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
)

var s34Armed bool
var s34StoresCreated int

func s34Emit(e string, d interface{}) {
	b, _ := json.Marshal(map[string]interface{}{"event": e, "data": d})
	fmt.Printf("STEP34 %s\n", b)
}
func s34Fault(stage string, after bool) error {
	if s34Armed && os.Getenv("E34_FAULT") == "cancel-"+stage {
		return context.Canceled
	}
	if s34Armed && os.Getenv("E34_FAULT") == stage {
		return fmt.Errorf("injected Go fault %s after_cleanup_or_guest=%v; not native failure", stage, after)
	}
	return nil
}
