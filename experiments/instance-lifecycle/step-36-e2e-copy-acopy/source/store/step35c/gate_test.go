package step35c
import("context";"testing")
func TestGateDrain(t *testing.T){var g Gate;end,e:=g.Begin();if e!=nil{t.Fatal(e)};ctx,c:=context.WithCancel(context.Background());c();if g.Drain(ctx)==nil{t.Fatal("uncompleted operation allowed drain")};if _,e=g.Begin();e==nil{t.Fatal("new admission after stop")};end();end();if g.Count()!=0{t.Fatal("counter")};if e=g.Drain(context.Background());e!=nil{t.Fatal(e)};if e=g.Drain(context.Background());e!=nil{t.Fatal(e)}}
func TestGateWaitsExisting(t *testing.T){var g Gate;end,_:=g.Begin();done:=make(chan error,1);go func(){done<-g.Drain(context.Background())}();end();if e:=<-done;e!=nil{t.Fatal(e)}}
