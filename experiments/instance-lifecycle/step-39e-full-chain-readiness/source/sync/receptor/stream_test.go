/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import (
	"context"
	"fmt"
	"testing"
	"time"

	"chainmaker.org/chainmaker/protocol/v2/test"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func getConn(e *endpoint, height uint64, dialer dialer) (*clientConn, error) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	return e.GetConn(ctx, height, dialer)
}

func Test_streamGroup_FetchAllFragments(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	var merger types.Merger = types.NewBlockSlicer(cLogger)
	var (
		nodeIDs = []string{
			"remoteNode1",
			"remoteNode2",
			"remoteNode3",
		}
	)

	mbs, closeFunc := initCluster(ctrl, cLogger, "localNode", nodeIDs...)
	defer closeFunc()
	time.Sleep(time.Second)
	transport := newTransport(net.NewBlockSyncTransport(mbs), cLogger)
	epp := newEndpointPool(transport, test.GoLogger{})
	for _, id := range nodeIDs {
		epp.AddEndpoint(id, blockState{
			height: 1000,
		})
	}

	eps := getValidEndpointsSorted(1, epp.Select(endpointFilterFunc(func(e *endpoint) bool {
		return e.isLiving() && e.ArchiveHeight() < 1 && e.Height() >= 1
	})))
	ccs := make([]*clientConn, 0, len(eps))
	for _, e := range eps {
		conn, err := getConn(e, 1, transport)
		if err != nil {
			continue
		}
		ccs = append(ccs, conn)
	}

	// connPool := newClientConnPool(net.NewBlockSyncTransport(mbs), cLogger)
	// for _, id := range nodeIDs {
	// 	cc, err := connPool.GetClientConn(id, 1)
	// 	require.NoError(t, err)
	// 	cc.release()
	// }

	require.NotZero(t, len(ccs))
	t.Logf("no push connection cached.len %d", len(ccs))
	sg := newStreamGroup(1, streamConf{timeout: 10 * time.Second, windowInitSize: 16})
	sg.build(ccs...)
	require.Equal(t, sg.len(), len(ccs))
	time.Sleep(time.Second)
	count := 10
	buf := make([]byte, 0, 1024)
	for {
		time.Sleep(10 * time.Millisecond)
		buf = buf[:0]
		bc := sg.FetchAllFragments()
		if len(bc.miss) > 0 {
			t.Errorf("block fragments has miss %v", bc.miss)
			continue
		}
		if len(bc.reward) > 0 {
			t.Logf("reward %+v", bc.reward)
		}
		if len(bc.diss) > 0 {
			t.Logf("diss %+v", bc.diss)
		}
		block, err := merger.MergeBlockFragment(bc.fragments)
		if err != nil {
			t.Errorf("MergeBlockFragment err %v", err)
		}
		t.Logf("received block %+v", block)
		count--
		if count == 0 {
			break
		}
	}
	sg.release()
	time.Sleep(time.Second * 1)
}

func Test_streamGroup_build(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	var (
		nodeIDs = []string{
			"remoteNode1",
			"remoteNode2",
			"remoteNode3",
		}
	)

	mbs, closeFunc := initCluster(ctrl, cLogger, "localNode", nodeIDs...)
	defer closeFunc()
	time.Sleep(time.Second)

	transport := newTransport(net.NewBlockSyncTransport(mbs), cLogger)
	epp := newEndpointPool(transport, test.GoLogger{})
	for _, id := range nodeIDs {
		epp.AddEndpoint(id, blockState{
			height: 1000,
		})
	}

	eps := getValidEndpointsSorted(1, epp.Select(endpointFilterFunc(func(e *endpoint) bool {
		return e.isLiving() && e.ArchiveHeight() < 1 && e.Height() >= 1
	})))
	ccs := make([]*clientConn, 0, len(eps))
	for _, e := range eps {
		conn, err := getConn(e, 1, transport)
		if err != nil {
			continue
		}
		ccs = append(ccs, conn)
	}

	require.NotZero(t, len(ccs))
	t.Logf("no push connection cached.len %d", len(ccs))
	sg := newStreamGroup(1, streamConf{timeout: 10 * time.Second, windowInitSize: 16})
	sg.build(ccs...)
	require.Equal(t, sg.len(), len(ccs))
	sg.release()
	time.Sleep(100 * time.Millisecond)
}

func Test_streamGroup_replace(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	var (
		nodeIDs = []string{
			"remoteNode1",
			"remoteNode2",
			"remoteNode3",
		}
	)

	mbs, closeFunc := initCluster(ctrl, cLogger, "localNode", nodeIDs...)
	defer closeFunc()
	time.Sleep(time.Second)

	transport := newTransport(net.NewBlockSyncTransport(mbs), cLogger)
	epp := newEndpointPool(transport, test.GoLogger{})
	for _, id := range nodeIDs {
		epp.AddEndpoint(id, blockState{
			height: 1000,
		})
	}

	eps := getValidEndpointsSorted(1, epp.Select(endpointFilterFunc(func(e *endpoint) bool {
		return e.isLiving() && e.ArchiveHeight() < 1 && e.Height() >= 1
	})))
	ccs := make([]*clientConn, 0, len(eps))
	for _, e := range eps {
		conn, err := getConn(e, 1, transport)
		if err != nil {
			continue
		}
		ccs = append(ccs, conn)
	}

	require.NotZero(t, len(ccs))
	t.Logf("no push connection cached.len %d", len(ccs))
	sg := newStreamGroup(1, streamConf{timeout: 2 * time.Second, windowInitSize: 16})
	sg.build(ccs...)
	require.Equal(t, sg.len(), len(ccs))
	downID := ccs[0].nodeID()
	err := ccs[0].closeForError(fmt.Errorf("endpoint down"))
	require.NoError(t, err)
	has := sg.hasInvalidStream()
	require.False(t, has)
	sg.check()
	has = sg.hasInvalidStream()
	require.True(t, has)
	sts := sg.invalidStreams()
	require.Equal(t, len(sts), 1)
	time.Sleep(1000 * time.Millisecond)
	min, _ := sg.heightReceived()
	t.Logf("received height min [%d]", min)
	sg2 := sg.clone(min + 1)
	end := epp.GetEndpoint(downID)
	cc, err := getConn(end, 1, transport) //connPool.GetClientConn(downID, 1)
	require.NoError(t, err)
	cc.release()
	eps = epp.Select(endpointFilterFunc(func(e *endpoint) bool {
		return e.noPushLocked()
	}))
	ccs = make([]*clientConn, 0, len(eps))
	for _, e := range eps {
		conn, err := getConn(e, 1, transport)
		if err != nil {
			continue
		}
		ccs = append(ccs, conn)
	}
	sg2.rebuild(ccs...)
	require.Equal(t, len(nodeIDs), sg.len())
	time.Sleep(100 * time.Millisecond)
	min, _ = sg.heightReceived()
	t.Logf("received height min [%d]", min)
}

func Test_streamLinkedList(t *testing.T) {
	tests := []struct {
		name   string
		fields *streamLinkedList
	}{
		{
			name:   "test",
			fields: newStreamLinkedList(),
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := tt.fields
			sg1 := newStreamGroup(1, streamConf{timeout: 10 * time.Second, windowInitSize: 16})
			l.Push(sg1)
			front := l.Front()
			require.Equal(t, sg1, front.sg)
			sg2 := newStreamGroup(10, streamConf{timeout: 10 * time.Second, windowInitSize: 16})
			l.Push(sg2)
			next := front.Next()
			require.Equal(t, sg2, next.sg)
			back := l.Back()
			require.Equal(t, back, next)
			l.Remove(front)
			front = l.Front()
			require.Equal(t, sg2, front.sg)
			l.ClearAll()
			front = l.Front()
			require.Nil(t, front)
		})
	}
}

func TestBlock(t *testing.T) {
	blockFragment1 := sliceData{}
	if blockFragment1.miss() {
		t.Log("blockFragment.miss")
	}
	if blockFragment1.invalid() {
		t.Log("blockFragment.invalid")
	}

	blockFragment2 := sliceData{
		SliceData: invalidFragment,
	}

	if blockFragment2.miss() {
		t.Log("blockFragment2.miss")
	}
	if blockFragment2.invalid() {
		t.Log("blockFragment2.invalid")
	}
}
