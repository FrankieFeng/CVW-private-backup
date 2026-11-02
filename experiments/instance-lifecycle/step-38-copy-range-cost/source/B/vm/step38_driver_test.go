package wasmer
import("testing";"os";"encoding/json";"crypto/sha256";"encoding/hex";"fmt";"runtime";"strings";common "chainmaker.org/chainmaker/pb-go/v2/common";vm "chainmaker.org/chainmaker/vm/v2")
type e38Case struct{Case,Contract,Method,Expected string;Params map[string]string;Setup []struct{Method string;Params map[string]string}}
func TestStep38VM(t *testing.T){
 var cfg e38Case;b,e:=os.ReadFile(os.Getenv("E38_CASE_FILE"));if e!=nil||json.Unmarshal(b,&cfg)!=nil{t.Fatal("case")}
 f:=s21cPrepare(t,os.Getenv("D_MANIFEST"),os.Getenv("D_OUTPUT"));m:=NewInstancesManager(ChainId);if m.safeErr!=nil||m.safe==nil{t.Fatalf("safe owner: %v",m.safeErr)};f.manager.(*vm.VmManagerImpl).InstanceManagers[common.RuntimeType_WASMER]=m
 defer func(){if e:=m.StopVM();e!=nil{t.Error(e)}}()
 names:=[]string{cfg.Contract};if cfg.Contract=="exchange"{names=[]string{"identity","erc721","exchange"}}
 for _,c:=range names{args:=map[string]string{};if c=="erc721"{args=map[string]string{"name":"huanletoken","symbol":"hlt","tokenURI":"https://chainmaker.org.cn"}};r:=f.run("init-"+c,c,"init_contract","e38-init-"+c,args);if r.Result.Code!=0||r.Status!=0{t.Fatalf("init: %+v",r.Result)}}
 for i,s:=range cfg.Setup{r:=f.run(fmt.Sprint("setup-",i),cfg.Contract,s.Method,fmt.Sprint("e38-setup-",i),s.Params);if r.Result.Code!=0||r.Status!=0{t.Fatalf("setup: %+v",r.Result)}}
 initial:=e22Clone(f.snapshot.ledger);beforeHash:=f.snapshot.hash();e38Drain()
 run:=func(phase string,i int){f.snapshot.ledger=e22Clone(initial);token:=sha256.Sum256([]byte(cfg.Case+"|"+os.Getenv("E38_BATCH")+"|"+phase+fmt.Sprint(i)));tx:=hex.EncodeToString(token[:]);var a,b runtime.MemStats;runtime.ReadMemStats(&a);r:=f.run(fmt.Sprintf("%s-%d",phase,i),cfg.Contract,cfg.Method,tx,cfg.Params);runtime.ReadMemStats(&b);if r.Status!=0||r.Result.Code!=0{t.Fatalf("business %s: %+v",phase,r.Result)};if cfg.Expected!=""&&!strings.HasPrefix(string(r.Result.Result),cfg.Expected){t.Fatalf("result %s",string(r.Result.Result))};if r.BeforeHash!=beforeHash{t.Fatal("initial ledger mismatch")};e38Emit(map[string]interface{}{"event":"target","phase":phase,"slot":i,"tx_id":tx,"case":cfg.Case,"strategy":os.Getenv("E38_STRATEGY"),"result":r.Result,"rwset":r.RWSet,"before_hash":r.BeforeHash,"after_hash":r.AfterHash,"runcontract_ns":r.RunContractWallNS,"host_envelope_allocs":b.Mallocs-a.Mallocs,"host_envelope_alloc_bytes":b.TotalAlloc-a.TotalAlloc,"host_heap":b.HeapAlloc,"host_gc":b.NumGC,"costs":e38Drain()})}
 for i:=0;i<2;i++{run("warmup",i)}
 for i:=0;i<2;i++{run("formal",i)}
}
