package readiness39e
import("context";"testing";"time")
func TestIncompleteCallbacksCannotPass(t *testing.T){
 enabled=true;for _,s:=range []string{"chain_start_enter","registry_returned","provider_returned","sync_started","chain_started","core_start_return","consensus_start_return"}{Mark(s)};CoreReady(true);Waiting()
 Notify(7);Taken(7);if Snapshot().Ready{t.Fatal("active callback incorrectly ready")}
 ctx,c:=context.WithTimeout(context.Background(),time.Millisecond);defer c();if AwaitHeight(ctx,7)==nil{t.Fatal("incomplete callback bypassed")}
 Waiting();if e:=AwaitHeight(context.Background(),7);e!=nil{t.Fatal(e)}
 Mark("stopping");if e:=AwaitHeight(context.Background(),7);e==nil{t.Fatal("stopping passed")}
}
