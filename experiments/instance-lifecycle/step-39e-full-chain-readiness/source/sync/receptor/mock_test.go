/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import (
	"fmt"
	"math"
	"sync"
	"time"

	"chainmaker.org/chainmaker/logger/v2"
	"chainmaker.org/chainmaker/sync/v2/internal/rand"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/setting"

	"chainmaker.org/chainmaker/common/v2/msgbus"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/pb-go/v2/store"
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/protocol/v2/mock"
	"chainmaker.org/chainmaker/sync/v2/conn"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/internal/test"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/gogo/protobuf/proto"
	"github.com/golang/mock/gomock"
)

var (
// remoteNode = "remote-node"
// localNode  = "local-node"
// errStr = "implement me"
)

type mockNode struct {
	syncPb.NodeInform
}

func (mock *mockNode) Info() *syncPb.NodeInform {
	return &mock.NodeInform
}

func (mock *mockNode) LastDetectedAliveTime() int64 {
	return time.Now().Unix()
}

type mockNodeInformer struct {
	nodes    []syncPb.NodeInform
	mu       sync.Mutex
	watchers map[chan types.Event]struct{}
}

func (ni *mockNodeInformer) List() []types.Node {
	nodes := make([]types.Node, 0, len(ni.nodes))
	for _, node := range ni.nodes {
		nodes = append(nodes, &mockNode{node})
	}
	return nodes
}

func (ni *mockNodeInformer) Watch() types.Watcher {
	ch := make(chan types.Event, 16)
	ni.mu.Lock()
	defer ni.mu.Unlock()
	ni.watchers[ch] = struct{}{}
	return &watcher{
		ch:       ch,
		informer: ni,
	}
}

// func (ni *mockNodeInformer) delWatcher(ch chan types.Event) {
// 	ni.mu.Lock()
// 	defer ni.mu.Unlock()
// 	delete(ni.watchers, ch)
// }

// func (ni *mockNodeInformer) trigger() {
// 	ticker := time.NewTicker(10 * time.Millisecond)
// 	for {
// 		<-ticker.C
// 		ni.triggerOnce()
// 		ni.mu.Unlock()
// 	}
// }

// #nosec G404
func (ni *mockNodeInformer) triggerOnce() {
	idx := rand.Intn(len(ni.nodes))
	ni.nodes[idx].Height++
	e := &mockEvent{
		t: types.EventUpdateNode,
		inform: syncPb.NodeInform{
			Id:            ni.nodes[idx].Id,
			Height:        ni.nodes[idx].Height,
			ArchiveHeight: ni.nodes[idx].ArchiveHeight,
		},
	}
	ni.mu.Lock()
	for ch := range ni.watchers {
		select {
		case ch <- e:
		default:
		}
	}
	ni.mu.Unlock()
}

type watcher struct {
	ch       chan types.Event
	informer *mockNodeInformer
}

func (w *watcher) Stop() {
	close(w.ch)
}

func (w *watcher) ResultChan() <-chan types.Event {
	return w.ch
}

type mockEvent struct {
	t      types.EventType
	inform syncPb.NodeInform
}

func (e *mockEvent) EventType() types.EventType {
	return e.t
}
func (e *mockEvent) EventNode() *syncPb.NodeInform {
	return &e.inform
}

func newMockInformer(nodes ...syncPb.NodeInform) *mockNodeInformer {
	informer := &mockNodeInformer{
		nodes:    nodes,
		watchers: make(map[chan types.Event]struct{}),
	}
	// go informer.trigger()
	return informer
}

func newMockLedgerCache(ctrl *gomock.Controller, blk *commonPb.Block) protocol.LedgerCache {
	mockLedger := mock.NewMockLedgerCache(ctrl)
	lastCommitBlk := blk
	mockLedger.EXPECT().GetLastCommittedBlock().DoAndReturn(func() *commonPb.Block {
		return lastCommitBlk
	}).AnyTimes()
	mockLedger.EXPECT().CurrentHeight().DoAndReturn(func() (uint64, error) {
		return lastCommitBlk.Header.BlockHeight, nil
	}).AnyTimes()
	mockLedger.EXPECT().SetLastCommittedBlock(gomock.Any()).DoAndReturn(func(blk *commonPb.Block) {
		lastCommitBlk = blk
	}).AnyTimes()
	return mockLedger
}

// func newMockVerifier(ctrl *gomock.Controller) protocol.BlockVerifier {
// 	mockVerify := mock.NewMockBlockVerifier(ctrl)
// 	mockVerify.EXPECT().VerifyBlock(gomock.Any(), gomock.Any()).AnyTimes()
// 	mockVerify.EXPECT().VerifyBlockWithRwSets(gomock.Any(), gomock.Any(), gomock.Any()).AnyTimes()
// 	return mockVerify
// }

// func newMockCommitter(ctrl *gomock.Controller, mockLedger protocol.LedgerCache) protocol.BlockCommitter {
// 	mockCommit := mock.NewMockBlockCommitter(ctrl)
// 	mockCommit.EXPECT().AddBlock(gomock.Any()).DoAndReturn(func(blk *commonPb.Block) error {
// 		mockLedger.SetLastCommittedBlock(blk)
// 		return nil
// 	}).AnyTimes()
// 	return mockCommit
// }

// func newMockBlockChainStore(ctrl *gomock.Controller) protocol.BlockchainStore {
// 	mockStore := mock.NewMockBlockchainStore(ctrl)
// 	blocks := make(map[uint64]*commonPb.Block)
// 	mockStore.EXPECT().PutBlock(gomock.Any(), gomock.Any()).DoAndReturn(
// 		func(blk *commonPb.Block, txRWSets []*commonPb.TxRWSet) error {
// 			blocks[blk.Header.BlockHeight] = blk
// 			return nil
// 		}).AnyTimes()
// 	mockStore.EXPECT().GetBlock(gomock.Any()).DoAndReturn(func(height uint64) (*commonPb.Block, error) {
// 		if blk, exist := blocks[height]; exist {
// 			return blk, nil
// 		}
// 		return nil, fmt.Errorf("block not find")
// 	}).AnyTimes()
// 	mockStore.EXPECT().GetArchivedPivot().AnyTimes()
// 	return mockStore
// }

//------------------------------new mock-----------------

func initCluster(ctrl *gomock.Controller, logger protocol.Logger, local string, remotes ...string) (msgbus.MessageBus, func() error) {
	ns := test.NewWorkNS(ctrl)
	localNode := ns.NewMockNode(local, logger)
	servers := make([]*mockServer, 0, len(remotes))
	for _, rid := range remotes {
		remoteNode := ns.NewMockNode(rid, logger)
		server := newMockServer(remoteNode, nodeInfo{}, logger)
		server.Listen()
		servers = append(servers, server)
	}
	closeFunc := func() error {
		for _, server := range servers {
			server.Close()
		}
		ns.Release()
		return nil
	}
	return localNode.MessageBus(), closeFunc
}

type serverCluster struct {
	ns      *test.WorkNS
	local   *test.MockNode
	remotes map[string]*mockServer
}

func (s *serverCluster) LocalNode() *test.MockNode {
	return s.local
}

func (s *serverCluster) Remove(nodeID string) {
	// if server, exist := s.remotes[nodeID]; exist {
	// 	server.Close()
	// 	delete(s.remotes, nodeID)
	// }
	s.ns.RemoveSoft(nodeID)
}

func (s *serverCluster) Close() {
	for _, server := range s.remotes {
		server.Close()
	}
	s.ns.Release()
}

type nodeInfo struct {
	ID             string
	Height         uint64
	ruleMeetHeight uint64
}

func initCluster2(ctrl *gomock.Controller, local string, remotes ...nodeInfo) *serverCluster {
	ns := test.NewWorkNS(ctrl)
	cLogger := logger.GetLoggerByChain(logger.MODULE_SYNC, local)
	localNode := ns.NewMockNode(local, cLogger)
	servers := make(map[string]*mockServer, len(remotes))
	for _, info := range remotes {
		cLogger = logger.GetLoggerByChain(logger.MODULE_SYNC, info.ID)
		remoteNode := ns.NewMockNode(info.ID, cLogger)
		server := newMockServer(remoteNode, info, cLogger)
		server.Listen()
		servers[info.ID] = server
	}

	return &serverCluster{
		ns:      ns,
		local:   localNode,
		remotes: servers,
	}

	// closeFunc := func() error {
	// 	for _, server := range servers {
	// 		server.Close()
	// 	}
	// 	ns.Release()
	// 	return nil
	// }
	// return localNode.MessageBus(), closeFunc
}

type handlerFunc func(conn.BlockWriter, *types.BlockSyncRequest)

func (h handlerFunc) ServeBlock(w conn.BlockWriter, r *types.BlockSyncRequest) {
	h(w, r)
}

func generateBlock(height uint64) *store.BlockWithRWSet {
	return &store.BlockWithRWSet{
		Block: &commonPb.Block{
			Header: &commonPb.BlockHeader{
				BlockHeight: height,
			},
			AdditionalData: &commonPb.AdditionalData{
				ExtraData: map[string][]byte{
					"aaa": []byte("hello world"),
					"bbb": []byte("hello world"),
					"ccc": []byte("hello world"),
					"ddd": []byte("hello world"),
				},
			},
		},
	}
}

func mockHandler(w conn.BlockWriter, r *types.BlockSyncRequest) {
	fmt.Printf("Mock Handler: %+v\n", *r)

	if r.ModeData.Type() != setting.SyncModeTypeSharding {
		fmt.Printf("unsupported mode type: %d", r.ModeData.Type())
		return
	}
	ms := r.ModeData.ToMode().Spec()
	spec := ms.(setting.ShardingModeSpec)

	endHeight := r.Height + uint64(r.Num)
	if r.Num == 0 {
		endHeight = math.MaxUint64
	}
	for h := r.Height; h < endHeight; h++ {
		block := generateBlock(h)
		bz, err := proto.Marshal(block)
		if err != nil {
			fmt.Println("marsh block err: ", err)
			h--
			continue
		}
		minSize := len(bz) / spec.Nodes
		from := minSize * (spec.Index - 1)
		to := minSize * int(spec.Index)
		if spec.Index == spec.Nodes {
			to = len(bz)
		}
		err = w.Write(types.DataFragment{
			Height: h,
			Data:   bz[from:to],
		})
		if err != nil {
			fmt.Println("server block error: ", err)
			return
		}
	}

	if flusher, ok := w.(conn.BlockFlusher); ok {
		flusher.Flush()
	}
}

type mockServer struct {
	listener       *conn.Listener
	handler        handlerFunc
	height         uint64
	node           *test.MockNode
	slicer         types.Slicer
	ruleMeetHeight uint64
}

func newMockServer(node *test.MockNode, info nodeInfo, logger protocol.Logger) *mockServer {
	tp := net.NewBlockSyncTransport(node.MessageBus())
	s := &mockServer{
		node:           node,
		slicer:         types.NewBlockSlicer(logger),
		height:         info.Height,
		ruleMeetHeight: info.ruleMeetHeight,
	}
	s.listener = conn.NewMsgBusListener(tp, s.listenHandle, logger)
	return s
}

func (s *mockServer) ServeBlock(w conn.BlockWriter, r *types.BlockSyncRequest) {
	fmt.Println("ServeBlock: ", s.node.NodeID(), s.height, r.Height, r.Num)
	_, orpull := w.(conn.BlockFlusher)
	if r.ModeData.Type() != setting.SyncModeTypeSharding {
		fmt.Printf("unsupported mode type: %d", r.ModeData.Type())
		return
	}
	ms := r.ModeData.ToMode().Spec()
	spec := ms.(setting.ShardingModeSpec)
	fmt.Printf("Mock Handler ModeData spec: %+v for pull: %v\n", ms, orpull)

	endHeight := r.Height + uint64(r.Num)
	if r.Num == 0 {
		endHeight = math.MaxUint64
	}
	gid := 0
	defer func() {
		if flusher, ok := w.(conn.BlockFlusher); ok {
			flusher.Flush()
		}
	}()
	for h := r.Height; h < endHeight; h++ {
		fmt.Printf("Mock Handler Height: %d for pull : %v\n", h, orpull)
		if s.ruleMeetHeight > 0 && h > s.ruleMeetHeight {
			w.Terminate(errors.ErrCodeRuleNotMeet)
			return
		}
		if s.height > 0 && h > s.height {
			time.Sleep(time.Second)
			h--
			continue
		}
		block := generateBlock(h)

		bz, err := s.slicer.SliceBlockFragment(int(spec.Nodes), int(spec.Index), block)
		if err != nil {
			fmt.Println("SliceBlockFragment err: ", err)
			h--
			continue
		}
		sliceData := &syncPb.SliceData{
			Version: uint32(types.Version),
			RuleId:  uint64(gid),
			Data:    bz,
		}
		sliceDataBz, err := proto.Marshal(sliceData)
		if err != nil {
			fmt.Println("marsh SliceData err: ", err)
			h--
			continue
		}
		err = w.Write(types.DataFragment{
			Height: h,
			Data:   sliceDataBz,
		})
		if err != nil {
			fmt.Printf("[%s] server block error: %v\n", s.node.NodeID(), err)
			return
		}
	}

}

func (s *mockServer) Listen() {
	if s.handler == nil {
		s.handler = mockHandler
	}
	conns := make([]*conn.ServerConn, 0, 10)
	_ = s.listener.Listen()
	go func() {
		fmt.Printf("[%s] mock server listening\n", s.node.NodeID())
		for {
			sc, err := s.listener.Accept()
			if err != nil {
				fmt.Println("Accept", err)
				for _, conn := range conns {
					conn.Close()
				}
				return
			}
			conns = append(conns, sc)
			fmt.Printf("[%s] Accept connect from [%s]\n", s.node.NodeID(), sc.NodeID())
			go func() {
				_ = sc.Serve(s)
			}()
		}
	}()
}

func (s *mockServer) listenHandle(nodeID string, height uint64) conn.BlockSupportResult {
	ret := conn.BlockSupportResult{
		BlockNum: -1,
	}
	if s.ruleMeetHeight > 0 && height > s.ruleMeetHeight {
		ret.BlockNum = 0
	}
	return ret
}

func (s *mockServer) Close() {
	s.listener.Close()
}
