package store
import("testing";"runtime";"chainmaker.org/chainmaker/store/v2/conf";"chainmaker.org/chainmaker/store/v2/utils/wait";"chainmaker.org/chainmaker/protocol/v2/test")
func TestStep35CCloseNil(t *testing.T){var b *BlockStoreImpl;if e:=b.Close();e!=nil{t.Fatal(e)}}
func TestStep35CCloseDrain(t *testing.T){b:=&BlockStoreImpl{stopCh:make(chan struct{}),waitG:new(wait.Group),storeConfig:&conf.StorageConfig{},logger:test.NewTestLogger(t)};end,_:=b.drain35c.Begin();done:=make(chan error,1);go func(){done<-b.Close()}();for{f,e:=b.drain35c.Begin();if e!=nil{break};f();runtime.Gosched()};select{case<-done:t.Fatal("closed DB while accepted writer active");default:};end();if e:=<-done;e!=nil{t.Fatal(e)};if e:=b.Close();e!=nil{t.Fatal(e)}}
