package wasmer
import("context";"testing";"time";"unsafe")
func TestStep38Clock(t *testing.T){ctx,c:=context.WithTimeout(context.Background(),10*time.Second);defer c();o,e:=NewSafeFreshOwner(2,nil);if e!=nil{t.Fatal(e)};defer func(){if e:=o.Stop(ctx);e!=nil{t.Error(e)}}();if e=o.Do(ctx,func()error{e38Drain();for i:=0;i<1000;i++{m:=e38Begin(0,"empty_observer_window",0);e38End(m)};e38Emit(map[string]interface{}{"event":"observer_calibration","independent_processes":1,"iterations":1000,"mark_struct_bytes":unsafe.Sizeof(e38Mark{}),"costs":e38Drain()});return nil});e!=nil{t.Fatal(e)}}
