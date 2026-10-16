//go:build step16
package wasmer
import (
 "testing"
 commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
)
func TestStep17RejectStaleWasm(t *testing.T) {
 c:=&commonPb.Contract{Name:"cached",Version:"1"}
 p:=&vmPool{byteCode:[]byte("original")}
 m:=&InstancesManager{instanceMap:map[string]*vmPool{"cached_1":p}}
 if _,e:=m.getVmPool(c,[]byte("changed"));e==nil{t.Fatal("stale same-identity module accepted")}
 q,e:=m.getVmPool(c,[]byte("original"));if e!=nil||q!=p{t.Fatal("valid cache lookup rejected")}
}
