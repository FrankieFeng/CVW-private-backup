//go:build step16
package wasmer
import("testing";"time")
func TestStep17FreshResetAudit(t *testing.T) {
 p:=&vmPool{freshOnDemand:true,resetC:make(chan struct{})}
 done:=make(chan struct{});go func(){p.reset();close(done)}()
 select{case <-done:t.Fatal("audit assumption changed: reset unexpectedly has a receiver");case <-time.After(20*time.Millisecond):}
 // Drain test-created signal to avoid leaving the reproduction goroutine behind.
 <-p.resetC;<-done
 t.Log("CONFIRMED LIMITATION: fresh-on-demand reset blocks without refreshingLoop; do not use live ResetAVmPool in this experiment")
}
