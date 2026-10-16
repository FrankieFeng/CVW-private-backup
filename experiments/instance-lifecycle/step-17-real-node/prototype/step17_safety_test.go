//go:build step16
package wasmer
import (
 "bytes"
 "fmt"
 "sync"
 "testing"
 commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
 wasm "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
)
func TestStep17SharedTemplateConcurrent(t *testing.T) {
 b:=step16Wat(t,`(module (memory (export "memory") 1) (data (i32.const 8) "hello"))`)
 c:=&commonPb.Contract{Name:"concurrent",Version:"1"};p,e:=prepareStaticMemory(b,c,"test");s15Must(t,e)
 before:=append([]byte(nil),p.Image...);errs:=make(chan error,4);var wg sync.WaitGroup
 // Each native worker owns its Store, matching the runtime's mutability contract.
 // Immutable Image/Ranges are genuinely shared by all four workers.
 for k:=0;k<4;k++ {wg.Add(1);go func(){defer wg.Done();store:=wasm.NewStore(wasm.NewEngine());defer store.Close();module,e:=wasm.NewModule(store,p.NoData,nil);if e!=nil{errs<-e;return};defer module.Close();q:=*p;q.Module=module
  for n:=0;n<30;n++ {a,e:=wasm.NewInstance(module,wasm.NewImportObject());if e!=nil{errs<-e;return};peer,e:=wasm.NewInstance(module,wasm.NewImportObject());if e!=nil{errs<-e;return}
   if e=q.restore(module,a,b,c,"test");e!=nil{errs<-e;return};if e=q.restore(module,peer,b,c,"test");e!=nil{errs<-e;return}
   ma,_:=a.Exports.GetMemory("memory");mb,_:=peer.Exports.GetMemory("memory");ma.Data()[8]='X';if string(mb.Data()[8:13])!="hello"{errs<-fmt.Errorf("cross-instance leak");return};a.Close();peer.Close()
  }
 }()};wg.Wait();close(errs);for e:=range errs{t.Error(e)};if !bytes.Equal(before,p.Image){t.Fatal("shared template was mutated")}
}
