package wasmer
import("bytes";"context";"fmt";"testing";"time";common "chainmaker.org/chainmaker/pb-go/v2/common";w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go")
func TestStep38Memory(t *testing.T){
 ctx,cancel:=context.WithTimeout(context.Background(),30*time.Second);defer cancel();o,e:=NewSafeFreshOwner(4,nil);if e!=nil{t.Fatal(e)};defer func(){if e:=o.Stop(ctx);e!=nil{t.Error(e)}}()
 err:=o.Do(ctx,func()error{
  cases:=[]struct{name,wat string;bad bool}{
   {"zero",`(module (memory (export "memory") 2 4) (data (i32.const 20) "\00\00\00"))`,false},
   {"nonzero_short_long_gap",`(module (memory (export "memory") 2 4) (data (i32.const 10) "ABC") (data (i32.const 18) "XYZ") (data (i32.const 70000) "Q"))`,false},
   {"overlap_zero_override",`(module (memory (export "memory") 2 4) (data (i32.const 0) "ABCDEF") (data (i32.const 2) "\00\00") (data (i32.const 5) "XY"))`,false},
   {"adjacent",`(module (memory (export "memory") 2 4) (data (i32.const 0) "AB") (data (i32.const 2) "CD") (data (i32.const 4) "EF"))`,false},
   {"automatic_start_trap",`(module (memory (export "memory") 1 4) (func $bad unreachable) (start $bad))`,true},
   {"out_of_bounds",`(module (memory (export "memory") 1 4) (data (i32.const 65535) "AB"))`,true},
  }
  for _,tc:=range cases{scope:=w.ManagedOpen("correctness-"+tc.name);raw,e:=w.Wat2Wasm(tc.wat);if e!=nil{return e};engine:=w.NewEngine();cs:=w.NewStore(engine);mod,e:=w.NewModule(cs,raw,nil);if e!=nil{return e};mod.Imports();mod.Exports()
   baselineScope:=w.ManagedOpen("baseline");st:=w.NewStore(engine);inst,e:=w.NewInstanceInStore(mod,w.NewImportObject(),st)
   if tc.bad{if e==nil{return fmt.Errorf("OOB native did not trap")};if p,err:=prepareStaticMemory(raw,&common.Contract{Name:"test",Version:"1"},"e38");err==nil||p!=nil{return fmt.Errorf("OOB transform accepted")};baselineScope.Close();scope.Close();e38Emit(map[string]interface{}{"event":"memory_check","case":tc.name,"passed":true,"native_trap":true,"transform_rejected_fallback_required":true});continue}
   if e!=nil{return e};mem,e:=inst.Exports.GetMemory("memory");if e!=nil{return e};want:=append([]byte(nil),mem.Data()...);if !mem.Grow(1){return fmt.Errorf("baseline grow")};wantGrown:=append([]byte(nil),mem.Data()...);if e=baselineScope.Close();e!=nil{return e}
   for _,strategy:=range []string{"C0","C1","C2","C3","C4"}{p,e:=prepareStaticMemory(raw,&common.Contract{Name:"test",Version:"1"},"e38");if e!=nil{return e};if e=e38Coalesce(p,strategy);e!=nil{return e};no,e:=w.NewModule(cs,p.NoData,nil);if e!=nil{return e};no.Imports();no.Exports();p.Module=no
    req:=w.ManagedOpen("fresh-check");target:=w.NewStore(engine);a,e:=w.NewInstanceInStore(no,w.NewImportObject(),target);if e!=nil{return e};am,e:=a.Exports.GetMemory("memory");if e!=nil{return e};for _,b:=range am.Data(){if b!=0{return fmt.Errorf("NoData target not zero")}}
    c:=&common.Contract{Name:"test",Version:"1"};if e=p.restore(no,a,raw,c,"e38");e!=nil{return e};if !bytes.Equal(want,am.Data()){return fmt.Errorf("full memory mismatch %s %s",tc.name,strategy)}
    am.Data()[0]^=127;otherStore:=w.NewStore(engine);other,e:=w.NewInstanceInStore(no,w.NewImportObject(),otherStore);if e!=nil{return e};if e=p.restore(no,other,raw,c,"e38");e!=nil{return e};om,_:=other.Exports.GetMemory("memory");if !bytes.Equal(want,om.Data())||am.Data()[0]==om.Data()[0]{return fmt.Errorf("instance isolation")}
    if !om.Grow(1)||!bytes.Equal(wantGrown,om.Data()){return fmt.Errorf("growth semantics")};if e=p.restore(no,other,raw,c,"e38");e==nil{return fmt.Errorf("grew target accepted by fixed template")};am.Data()[100000]=90;if e=p.restore(no,a,raw,c,"e38");e!=nil{return e};if am.Data()[100000]!=90{return fmt.Errorf("nonfresh negative control unexpectedly reset hole")};if bytes.Equal(want,am.Data()){return fmt.Errorf("nonfresh target falsely restored")};if e=req.Close();e!=nil{return e};e38Emit(map[string]interface{}{"event":"memory_check","case":tc.name,"strategy":strategy,"passed":true,"bytes":p.e38CopyBytes,"ranges":len(p.Ranges),"full_initial_memory":true,"growth_and_isolation":true,"nonfresh_reuse_not_supported":true,"dirty_target_not_reset_proven":true})
   };if e:=scope.Close();e!=nil{return e}
  };return nil
 });if err!=nil{t.Fatal(err)}
}
