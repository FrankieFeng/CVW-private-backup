package receptor

import (
	"fmt"
	"testing"
	"time"

	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
)

func Test_nodeInformer_Watch(t *testing.T) {
	mockInformer := newMockInformer(syncPb.NodeInform{
		Id: "node1",
	}, syncPb.NodeInform{
		Id: "node2",
	})
	longSilenceTime = 500 * time.Millisecond
	informer := newNodeInformer(mockInformer)

	watcher := informer.Watch()

	go func() {
		for i := 0; i < 10; i++ {
			mockInformer.triggerOnce()
		}
		time.Sleep(2 * time.Second)
		watcher.Stop()
	}()
	for e := range watcher.ResultChan() {
		fmt.Printf("event.type: %+v\n", e.EventType())
	}
}
