package blockchain

// Experiment-only single-chain readiness observer. No VM/native access.
import (
 "context"
 "encoding/json"
 "fmt"
 "net"
 "net/http"
 "os"
 "strconv"
 "sync"
 "sync/atomic"
 "time"
 "chainmaker.org/chainmaker/common/v2/msgbus"
 rd39e "experiment.local/readiness39e"
)
const fenceTopic39E msgbus.Topic=1000039
var server39e *http.Server
var listener39e net.Listener
var socketMu39e sync.Mutex
var markerSeq39e atomic.Uint64

type marker39e struct{Run,Chain string;ID uint64;Done chan struct{}}
type subscriber39e struct{run,chain string}
func(s *subscriber39e)OnMessage(m *msgbus.Message){x,ok:=m.Payload.(*marker39e);if !ok||x.Run!=s.run||x.Chain!=s.chain{return};rd39e.FenceAck();close(x.Done)}
func(s *subscriber39e)OnQuit(){}
type boundedFence39e interface{Diagnostic39EFence(context.Context,msgbus.Topic,interface{})error}
func(bc *Blockchain)startReadiness39E()error{
 if !rd39e.Enabled(){return nil}
 if os.Getenv("CM39E_CHAIN")!=bc.chainId{return fmt.Errorf("39E supports exactly the configured experiment chain")}
 socketMu39e.Lock();defer socketMu39e.Unlock()
 if server39e!=nil{return fmt.Errorf("39E readiness server already exists")}
 path:=os.Getenv("CM39E_SOCKET");if path==""{return fmt.Errorf("39E readiness socket missing")}
 if _,e:=os.Lstat(path);!os.IsNotExist(e){return fmt.Errorf("39E preserve existing socket")}
 bus,ok:=bc.msgBus.(boundedFence39e);if !ok{return fmt.Errorf("39E bounded same-queue fence unavailable")}
 ln,e:=net.Listen("unix",path);if e!=nil{return e};if e=os.Chmod(path,0600);e!=nil{ln.Close();return e}
 bc.msgBus.Register(fenceTopic39E,&subscriber39e{run:os.Getenv("CM39E_RUN"),chain:bc.chainId})
 mux:=http.NewServeMux()
 mux.HandleFunc("/ready",func(w http.ResponseWriter,r *http.Request){
  if r.Method!="GET"{w.WriteHeader(405);return}
  begin:=time.Now();ctx,cancel:=context.WithTimeout(r.Context(),3*time.Second);defer cancel()
  before:=rd39e.Snapshot();out:=map[string]interface{}{"passed":false,"scope":"components_and_safe_queue_only; SDK probe still required","state":before}
  defer func(){out["handler_ns"]=time.Since(begin).Nanoseconds();json.NewEncoder(w).Encode(out)}()
  if before.Closing{out["error"]="node stopping";return}
  if !before.ChainStarted||!before.RegistryReturned||!before.ProviderReturned||!before.SyncStarted||!before.ConsumerStarted||!before.CoreStarted||!before.ConsensusStarted{return}
  minHeight,err:=strconv.ParseUint(r.URL.Query().Get("min_height"),10,64);if r.URL.Query().Get("min_height")==""{minHeight=0;err=nil};if err!=nil{out["error"]=err.Error();return}
  ids:=[]uint64{}
  for i:=0;i<2;i++{
   id:=markerSeq39e.Add(1);ids=append(ids,id);m:=&marker39e{Run:before.Run,Chain:before.Chain,ID:id,Done:make(chan struct{})}
   if err=bus.Diagnostic39EFence(ctx,fenceTopic39E,m);err!=nil{out["error"]=err.Error();return}
   select{case<-m.Done:case<-ctx.Done():out["error"]=ctx.Err().Error();return}
   if err=rd39e.AwaitHeight(ctx,minHeight);err!=nil{out["error"]=err.Error();return}
  }
  after:=rd39e.Snapshot();out["state"]=after;out["fence_ids"]=ids;out["min_height"]=minHeight;out["passed"]=after.Ready&&after.LastCompletedHeight>=minHeight&&after.FenceCount>=before.FenceCount+2
  rd39e.Mark("readiness_fence_complete")
 })
 server39e=&http.Server{Handler:mux,ReadHeaderTimeout:2*time.Second};listener39e=ln
 go func(){e:=server39e.Serve(ln);if e!=nil&&e!=http.ErrServerClosed{rd39e.Mark("readiness_server_error")}}()
 return nil
}
func(bc *Blockchain)stopReadiness39E(){
 if !rd39e.Enabled(){return};socketMu39e.Lock();defer socketMu39e.Unlock();if server39e==nil{return}
 ctx,cancel:=context.WithTimeout(context.Background(),3*time.Second);defer cancel();if e:=server39e.Shutdown(ctx);e!=nil{rd39e.Mark("readiness_shutdown_timeout");server39e.Close()};listener39e.Close();rd39e.Mark("readiness_server_closed")
}
