package main
import (
 "bufio"
 "encoding/json"
 "fmt"
 "os"
 "sort"
 "sync"
 "time"
 "crypto/sha256"
 "golang.org/x/sys/unix"
 sdk "chainmaker.org/chainmaker/sdk-go/v2"
 sdkutils "chainmaker.org/chainmaker/sdk-go/v2/utils"
 pb "chainmaker.org/chainmaker/pb-go/v2/common"
)
type Job struct {Mode,Op,Contract,Method,Tag,Path string; Params map[string]string}
var clients map[string]*sdk.ChainClient
func run(j Job) map[string]interface{} {
 cc:=clients[j.Mode]; row:=map[string]interface{}{"mode":j.Mode,"op":j.Op,"contract":j.Contract,"method":j.Method,"tag":j.Tag}; kv:=[]*pb.KeyValuePair{}; keys:=[]string{};for k:=range j.Params{keys=append(keys,k)};sort.Strings(keys);for _,k:=range keys{kv=append(kv,&pb.KeyValuePair{Key:k,Value:[]byte(j.Params[k])})}
 var ts unix.Timespec;unix.ClockGettime(unix.CLOCK_MONOTONIC,&ts);row["client_begin_mono_ns"]=ts.Nano();
 begin:=time.Now();var resp *pb.TxResponse;var err error
 if j.Op=="deploy" {
  var payload *pb.Payload
  payload,err=cc.CreateContractCreatePayload(j.Contract,"1.0.0",j.Path,pb.RuntimeType_WASMER,kv)
  if err==nil { var e *pb.EndorsementEntry; base:=os.Getenv("STEP17_ADMIN");e,err=sdkutils.MakeEndorserWithPath(base+".sign.key",base+".sign.crt",payload);if err==nil{resp,err=cc.SendContractManageRequest(payload,[]*pb.EndorsementEntry{e},60,true)} }
 } else if j.Op=="query" {resp,err=cc.QueryContract(j.Contract,j.Method,kv,60)} else {resp,err=cc.InvokeContract(j.Contract,j.Method,fmt.Sprintf("1919%x",sha256.Sum256([]byte(fmt.Sprintf("%s:%s:%d",j.Tag,j.Mode,time.Now().UnixNano()))))[:64],kv,60,true)}
 row["elapsed_ns"]=time.Since(begin).Nanoseconds();unix.ClockGettime(unix.CLOCK_MONOTONIC,&ts);row["client_end_mono_ns"]=ts.Nano();if err!=nil{row["error"]=err.Error()};row["response"]=resp;return row
}
func main(){
 clients=map[string]*sdk.ChainClient{};for _,mode:=range []string{"baseline","optimized"}{cc,err:=sdk.NewChainClient(sdk.WithConfPath(os.Getenv("STEP17_ROOT")+"/network/"+mode+"/sdk.yml"));if err!=nil{panic(err)};clients[mode]=cc;defer cc.Stop()}
 scanner:=bufio.NewScanner(os.Stdin);scanner.Buffer(make([]byte,4096),20*1024*1024)
 for scanner.Scan(){var jobs []Job;if err:=json.Unmarshal(scanner.Bytes(),&jobs);err!=nil{panic(err)};rows:=make([]map[string]interface{},len(jobs));var wg sync.WaitGroup;for i,j:=range jobs{wg.Add(1);go func(i int,j Job){defer wg.Done();rows[i]=run(j)}(i,j)};wg.Wait();b,_:=json.Marshal(rows);fmt.Printf("RESULT %s\n",b)}
 if scanner.Err()!=nil{panic(scanner.Err())}
}
