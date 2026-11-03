package receptor

import (
	"time"

	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/sync/v2/types"
)

var (
	longSilenceTime                      = 10 * time.Second
	eventTypeLongSilence types.EventType = 1000
)

type nodeInformer struct {
	types.NodeInformer
}

func newNodeInformer(iInformer types.NodeInformer) types.NodeInformer {
	return &nodeInformer{
		NodeInformer: iInformer,
	}
}

func (i *nodeInformer) Watch() types.Watcher {
	iWatcher := i.NodeInformer.Watch()
	return newNodeInfoWatcher(iWatcher)
}

type nodeInfoWatcher struct {
	iWatcher types.Watcher
	events   chan types.Event
}

func newNodeInfoWatcher(w types.Watcher) *nodeInfoWatcher {
	watcher := &nodeInfoWatcher{
		iWatcher: w,
		events:   make(chan types.Event, 64),
	}
	go watcher.relayEvent()
	return watcher
}

func (w *nodeInfoWatcher) Stop() {
	w.iWatcher.Stop()
}

func (w *nodeInfoWatcher) relayEvent() {
	ticker := time.NewTicker(longSilenceTime)
	defer ticker.Stop()
	iEvents := w.iWatcher.ResultChan()
	longSilence := true
	for {
		select {
		case <-ticker.C:
			if longSilence {
				w.events <- longSilenceEvent{}
			}
			longSilence = true
		case event, ok := <-iEvents:
			if !ok {
				close(w.events)
				return
			}
			w.events <- event
			longSilence = false
		}
	}
}

func (w *nodeInfoWatcher) ResultChan() <-chan types.Event {
	return w.events
}

type longSilenceEvent struct {
}

func (e longSilenceEvent) EventType() types.EventType {
	return eventTypeLongSilence
}

func (e longSilenceEvent) EventNode() *syncPb.NodeInform {
	return nil
}
