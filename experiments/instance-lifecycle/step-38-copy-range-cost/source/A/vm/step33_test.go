package wasmer

import (
 "encoding/json"
 "fmt"
 "os"
 "strings"
 "testing"
 "time"
)
type s33Step struct { Method string `json:"method"`; Params map[string]string `json:"params"` }
type s33Case struct { Case string `json:"case"`; Contract string `json:"contract"`; Method string `json:"method"`; Params map[string]string `json:"params"`; Setup []s33Step `json:"setup"`; Expected string `json:"expected"`; Kind string `json:"kind"` }
func s33Check(t *testing.T,f *s21cFixture,c s33Case,r *s21cReceipt) {
 t.Helper();if r.Status!=0 || r.Result.Code!=0 {t.Fatalf("real business failed method=%s result=%+v",c.Method,r.Result)}
 result:=string(r.Result.Result)
 if c.Expected!="" && result!=c.Expected {t.Fatalf("unexpected real result got=%q want=%q",result,c.Expected)}
 if len(r.Calls)!=1 || r.Calls[0].Method!=c.Method || r.Calls[0].Code!=0 {t.Fatal("expected real standalone guest execution")}
 switch c.Kind {
 case "io": if len(r.RWSet.TxWrites)!=100 {t.Fatal("ioHeavy default100 writes not executed")}; for _,w:=range r.RWSet.TxWrites {if len(w.Value)!=256 {t.Fatal("io payload size changed")}}
 case "identity_add": if f.state("identity","identity",c.Params["address"])!="1" {t.Fatal("identity whitelist state missing")}
 case "identity_remove": if f.state("identity","identity",c.Params["address"])!="" {t.Fatal("whitelist deletion failed")}
 case "identity_admin": var a []string;if json.Unmarshal([]byte(f.state("identity","identity","adminAddress")),&a)!=nil || len(a)!=1 || a[0]!=c.Params["address"] {t.Fatal("admin ledger failed")}
 case "identity_address": var a []string;if json.Unmarshal([]byte(f.state("identity","identity","adminAddress")),&a)!=nil || len(a)!=1 || result!=a[0] {t.Fatal("independent derived sender address mismatch")}
 case "itinerary_save": if f.state("itinerary",c.Params["phone"],"")!=c.Params["itinerary"] {t.Fatal("itinerary write mismatch")}; var a map[string]interface{};if json.Unmarshal(r.Result.Result,&a)!=nil || a["code"]!=float64(200) {t.Fatal("itinerary result JSON")}
 case "itinerary_history": var a map[string]interface{};if json.Unmarshal(r.Result.Result,&a)!=nil || a["code"]!=float64(200) || !strings.Contains(result,"CN-Shanghai-Shanghai") {t.Fatal("real history rows not returned")};if len(f.snapshot.store.history)==0 {t.Fatal("history derived from real RWSet absent")}
 case "raffle_register": if f.state("raffle","peoples","")!=c.Params["peoples"] {t.Fatal("raffle register ledger")}
 case "raffle_draw": var ps struct { Peoples []struct{ Num int; Name string } `json:"peoples"` };if json.Unmarshal([]byte(f.state("raffle","peoples","")),&ps)!=nil || len(ps.Peoples)!=2 {t.Fatal("actual winner removal not committed")}
 case "fact_save": if f.state("fact","fact_bytes",c.Params["file_hash"])=="" {t.Fatal("fact save write")}
 case "fact_find": var a map[string]interface{};if json.Unmarshal(r.Result.Result,&a)!=nil || a["fileHash"]!=c.Params["file_hash"] {t.Fatal("fact find real ledger result")}
 case "erc_unapproved": if result!="" {t.Fatal("new minted token is not approved")}
 case "erc_approve": if f.state("erc721","tokenApprove",c.Params["tokenId"])!=c.Params["to"] {t.Fatal("approval write absent")}
 case "erc_transfer": if f.state("erc721","tokenIds",c.Params["tokenId"])!=c.Params["to"] {t.Fatal("owner transfer not committed")}
 case "erc_tokens": if !strings.Contains(result,"1") {t.Fatal("minted token absent")}
 case "erc_latest": if !strings.Contains(result,"tokenLatestTxInfo is ") || !strings.Contains(result,"8acfaca5") {t.Fatal("latest transaction real state missing")}
 case "erc_mint2_partial": if f.state("erc721","tokenIds",c.Params["tokenId"])!="" {t.Fatal("mint2 prototype unexpectedly wrote owner")};if !strings.Contains(result,"mint success") {t.Fatal("mint2 result")}
 }
}
func TestStep33Serial(t *testing.T) {
 if !e22Enabled || !e27Enabled {t.Fatal("explicit lifecycle flags required")};defer dOwner(t)()
 var variants map[string]e25Artifact;b,e:=os.ReadFile(os.Getenv("E25_VARIANTS"));if e!=nil || json.Unmarshal(b,&variants)!=nil {t.Fatal("variants")}
 var c s33Case;b,e=os.ReadFile(os.Getenv("E33_CASE_FILE"));if e!=nil || json.Unmarshal(b,&c)!=nil {t.Fatal("case manifest")}
 order:=strings.Split(os.Getenv("E33_ORDER"),",");if len(order)!=4 {t.Fatal("four group order required")}
 groups:=strings.Split(os.Getenv("E33_SINGLE"),",");if len(groups)<1 || len(groups)>2 {t.Fatal("bounded process groups")};if len(c.Setup)>2 {t.Fatal("existing at most4 Fresh per Store boundary")};if len(c.Setup)>1 && len(groups)>1 {t.Fatal("setup Store budget requires single group process")}
 f:=s21cPrepare(t,os.Getenv("D_MANIFEST"),os.Getenv("D_OUTPUT"));defer f.close();m:=f.instances;m.policy="R1";empty:=e22Clone(f.snapshot.ledger);receipts:=map[string]*s21cReceipt{};initialHash:=""
 for _,g:=range groups {
  f.snapshot.ledger=e22Clone(empty);f.snapshot.store.history=nil;m.e22.variant=g;e27Group=g;e27Role=g;e27Pair=-1
  a,ok:=variants[c.Contract+"-"+g];if !ok {t.Fatal("contract/group artifact missing")};raw,err:=os.ReadFile(a.Path);if err!=nil {t.Fatal(err)};contract,_:=f.snapshot.store.GetContractByName(c.Contract)
  if err=m.e25Prepare(contract,raw,g,a);err!=nil {t.Fatal(err)};f.snapshot.store.code[c.Contract]=raw
  if os.Getenv("E33_ALIGNMENT")=="1" {
   m.e22.invokeBegin=time.Now();bundle,err:=m.makeE22(contract,raw);if err!=nil {t.Fatal(err)};restore:=bundle.scope.Activate();fn,err:=bundle.instance.Exports.GetRawFunction("Step18Read");if err!=nil {t.Fatal(err)};values:=[]interface{}{}
   for _,i:=range []int32{4,5,6} {v,err:=fn.Call(i);if err!=nil {t.Fatal(err)};values=append(values,v)};fn.Close();restore();e22Emit("alignment",map[string]interface{}{"contract":c.Contract,"values":values});if fmt.Sprint(values[0])!="4194304" || fmt.Sprint(values[1])!="0" || fmt.Sprint(values[2])!="4194304" {t.Fatal("first arena alignment failed")};if err=m.closeE22(bundle);err!=nil {t.Fatal(err)};continue
  }
  args:=map[string]string{};if c.Contract=="erc721" {args=map[string]string{"name":"huanletoken","symbol":"hlt","tokenURI":"https://chainmaker.org.cn"}}
  r:=f.run("setup-"+c.Contract+"-"+g,c.Contract,"init_contract","step33-init-"+c.Contract,args);if r.Result.Code!=0 || r.Status!=0 {t.Fatalf("actual init failed %+v",r.Result)}
  for i,prep:=range c.Setup {r=f.run(fmt.Sprintf("setup-business-%d-%s",i,g),c.Contract,prep.Method,fmt.Sprintf("step33-setup-%s-%d",c.Contract,i),prep.Params);if r.Result.Code!=0 || r.Status!=0 {t.Fatalf("real prerequisite failed %s %+v",prep.Method,r.Result)}}
  h:=f.snapshot.hash();if initialHash!="" && initialHash!=h {t.Fatal("initial ledger differs")};initialHash=h;m.e22.validate=os.Getenv("E22_PHASE")=="preflight";e27Pair=0;before:=e27Host()
  r=f.run("target-"+g,c.Contract,c.Method,"step33-"+c.Case+"-fixed",c.Params);s33Check(t,f,c,r);receipts[g]=r
  dEvent("boundary",map[string]interface{}{"group":g,"position":strings.Index(os.Getenv("E33_ORDER"),g),"host_before":before,"host_after":e27Host(),"gas":r.Result.GasUsed,"before_hash":r.BeforeHash,"after_hash":r.AfterHash})
 }
 for i:=1;i<len(groups);i++ {e22Assert(t,receipts[groups[0]],receipts[groups[i]])}
 e22Emit("correctness",map[string]interface{}{"case":c.Case,"groups":groups,"real_business":true,"fresh_instances_only":true,"table_function_identity":"not_tested"})
}
