/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"context"
	"fmt"
	"math"
	"testing"
	"time"

	"chainmaker.org/chainmaker/logger/v2"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/internal/test"
	un "chainmaker.org/chainmaker/sync/v2/net"
	sp "chainmaker.org/chainmaker/sync/v2/setting"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

var (
	cLogger protocol.Logger
)

const (
	remoteNodeID = "remoteNode"
)

type contextUse struct {
	ctx    context.Context
	cancel context.CancelFunc
}

func (c *contextUse) Context() context.Context {
	return c.ctx
}

func (c *contextUse) Cancel() {
	c.cancel()
}

func init() {
	cLogger = logger.GetLoggerByChain(logger.MODULE_SYNC, "chain1")
}

type handlerFunc func(BlockWriter, *types.BlockSyncRequest)

func (h handlerFunc) ServeBlock(w BlockWriter, r *types.BlockSyncRequest) {
	h(w, r)
}

func mockHandler(w BlockWriter, r *types.BlockSyncRequest) {
	fmt.Printf("Mock Handler: %+v\n", *r)
	// w.Terminate(errors.ErrCodeBuildData)
	endHeight := r.Height + uint64(r.Num)
	if r.Num == 0 {
		endHeight = math.MaxUint64
	}
	for h := r.Height; h < endHeight; h++ {
		err := w.Write(types.DataFragment{
			Height: h,
			Data:   []byte(fmt.Sprintf("hello world@@@ %d", uint64(h))),
		})
		if err != nil {
			fmt.Println("server block error: ", err)
			return
		}
	}

	if flusher, ok := w.(BlockFlusher); ok {
		flusher.Flush()
	}
}

func mockHandlerError(w BlockWriter, r *types.BlockSyncRequest) {
	fmt.Printf("Mock Handler: %+v\n", *r)
	w.Terminate(errors.ErrCodeRuleNotMeet)
	if flusher, ok := w.(BlockFlusher); ok {
		flusher.Flush()
	}
}

func pull(cc *ClientConn, req types.BlockSyncRequest) ([]types.DataFragment, error) {
	ctx := pullCtx()
	defer ctx.cancel()
	return cc.PullBlock(ctx.Context(), req)
}

func Test_serverLister(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ns := test.NewWorkNS(ctrl)
	localNode := ns.NewMockNode("localhost", cLogger)
	remoteNode := ns.NewMockNode(remoteNodeID, cLogger)
	defer ns.Release()

	lsn := NewMsgBusListener(un.NewBlockSyncTransport(remoteNode.MessageBus()), nil, cLogger)
	_ = lsn.Listen()
	go func() {
		for {
			sc, err := lsn.Accept()
			if err != nil {
				t.Log("accept error", err)
				return
			}
			t.Log("server")
			go func() {
				_ = sc.Serve(handlerFunc(mockHandler))
			}()
		}
	}()
	time.Sleep(time.Second)

	dialer := NewMsgBusSyncDialer(un.NewBlockSyncTransport(localNode.MessageBus()), cLogger)
	cc, err := dialer.Dial(WithHeightContext(context.Background(), 1), remoteNodeID)
	if err != nil {
		t.Fatalf("dialer error: %v", err)
		return
	}

	time.Sleep(100 * time.Millisecond)
	mode := sp.NewShardingMode(1, 1, 0)
	datas, err := pull(cc, types.BlockSyncRequest{
		Height:   1,
		Num:      1,
		ModeData: mode.ToModeData(),
	})
	if err != nil {
		cc.Close()
		t.Fatalf("pull data error: %v", err)
		return
	}
	for _, data := range datas {
		t.Log("got data", data.Height, string(data.Data))
	}
	cc.Close()

	time.Sleep(2 * time.Second)
	cc, err = dialer.Dial(WithHeightContext(context.Background(), 1), remoteNodeID)
	if err != nil {
		t.Fatalf("dialer error: %v", err)
		return
	}
	defer cc.Close()
	time.Sleep(100 * time.Millisecond)

	datas, err = pull(cc, types.BlockSyncRequest{
		Height:   2,
		Num:      1,
		ModeData: mode.ToModeData(),
	})
	if err != nil {
		t.Fatalf("pull data error: %v", err)
		return
	}
	for _, data := range datas {
		t.Log("got data", data.Height, string(data.Data))
	}
}

func openPushCtx() *contextUse {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	return &contextUse{ctx: ctx, cancel: cancel}
}

func pullCtx() *contextUse {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	return &contextUse{ctx: ctx, cancel: cancel}
}

func openPush(cc *ClientConn, fromHeight uint64, kvs ...sp.Setting) (*PushStream, error) {
	ctx := openPushCtx()
	defer ctx.cancel()
	return cc.OpenPush(ctx.Context(), fromHeight, kvs...)
}
func updatePush(ps *PushStream, fromHeight uint64, kvs ...sp.Setting) error {
	ctx := openPushCtx()
	defer ctx.cancel()
	return ps.UpdateSetting(ctx.Context(), fromHeight, kvs...)
}

func Test_serverPush(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	remoteNodeName := remoteNodeID
	// pushWindowSize = 16

	ns := test.NewWorkNS(ctrl)
	localNode := ns.NewMockNode("localhost", cLogger)
	remoteNode := ns.NewMockNode(remoteNodeID, cLogger)
	defer ns.Release()

	lsn := NewMsgBusListener(un.NewBlockSyncTransport(remoteNode.MessageBus()), nil, cLogger)
	_ = lsn.Listen()
	go func() {
		for {
			sc, err := lsn.Accept()
			if err != nil {
				t.Log("accept error", err)
				return
			}
			t.Log("server")
			go func() {
				_ = sc.Serve(handlerFunc(mockHandler))
			}()
		}
	}()
	time.Sleep(time.Second)

	dialer := NewMsgBusSyncDialer(un.NewBlockSyncTransport(localNode.MessageBus()), cLogger)
	cc, err := dialer.Dial(WithHeightContext(context.Background(), 1), remoteNodeName)
	require.Nil(t, err)

	// cc.Close()
	// defer cc.Close()
	time.Sleep(100 * time.Millisecond)
	mode := sp.NewShardingMode(1, 1, 0)

	ps, err := openPush(cc, 1, sp.Setting{
		ID:  sp.IDSyncMode,
		Val: mode.ToModeData().ToSettingV(),
	})
	if err != nil {
		t.Log("OpenPush  error", err)
		require.Nil(t, err)
		return
	}
	fmt.Println("version1:", cc.settingVersion)
	time.Sleep(100 * time.Millisecond)
	err = updatePush(ps, 5, sp.Setting{
		ID:  sp.IDSyncMode,
		Val: mode.ToModeData().ToSettingV(),
	})
	if err != nil {
		t.Log("UpdateSetting  error", err)
		require.Nil(t, err)
		return
	}
	time.Sleep(1000 * time.Millisecond)
	fmt.Println("version2:", cc.settingVersion)
	for i := 0; i < 10; i++ {
		time.Sleep(10 * time.Millisecond)
		d, ok := ps.Fetch()
		if !ok {
			t.Log("Not read:", d.Height)
			continue
		}
		t.Log("read:", d.Height, string(d.Data))
	}

	ps.Close()
	time.Sleep(10 * time.Millisecond)
	_, err = openPush(cc, 1, sp.Setting{
		ID:  sp.IDSyncMode,
		Val: mode.ToModeData().ToSettingV(),
	})
	if err != nil {
		t.Log("OpenPush  error", err)
		require.Nil(t, err)
		return
	}

	cc.Close()

	cc, err = dialer.Dial(WithHeightContext(context.Background(), 1), remoteNodeID)
	require.Nil(t, err)

	// cc.Close()
	// defer cc.Close()
	time.Sleep(100 * time.Millisecond)
	_, err = openPush(cc, 1, sp.Setting{
		ID:  sp.IDSyncMode,
		Val: mode.ToModeData().ToSettingV(),
	})
	if err != nil {
		t.Log("OpenPush  error", err)
		require.Nil(t, err)
		return
	}
}

func Test_serverPushError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	remoteNodeName := remoteNodeID
	// pushWindowSize = 16
	ns := test.NewWorkNS(ctrl)
	localNode := ns.NewMockNode("localhost", cLogger)
	remoteNode := ns.NewMockNode(remoteNodeID, cLogger)
	defer ns.Release()

	lsn := NewMsgBusListener(un.NewBlockSyncTransport(remoteNode.MessageBus()), nil, cLogger)
	_ = lsn.Listen()
	go func() {
		for {
			sc, err := lsn.Accept()
			if err != nil {
				t.Log("accept error", err)
				return
			}
			t.Log("server")
			go func() {

				_ = sc.Serve(handlerFunc(func(bw BlockWriter, bsr *types.BlockSyncRequest) {
					time.Sleep(100 * time.Millisecond)
					mockHandlerError(bw, bsr)
				}))
			}()
		}
	}()
	time.Sleep(time.Second)

	dialer := NewMsgBusSyncDialer(un.NewBlockSyncTransport(localNode.MessageBus()), cLogger)
	cc, err := dialer.Dial(WithHeightContext(context.Background(), 1), remoteNodeName)
	require.Nil(t, err)

	time.Sleep(100 * time.Millisecond)
	mode := sp.NewShardingMode(1, 1, 0)
	ps, err := openPush(cc, 1, sp.Setting{
		ID:  sp.IDSyncMode,
		Val: mode.ToModeData().ToSettingV(),
	})
	if err != nil {
		t.Log("OpenPush  error", err)
		require.Nil(t, err)
		return
	}
	fmt.Println("version1:", cc.settingVersion)
	time.Sleep(100 * time.Millisecond)
	cr := <-ps.ListenClose()
	t.Logf("terminated error: %+v", cr)
	if cr.Code.Terminate() {
		cc.Close()
	}
}
func ping(cc *ClientConn) error {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Millisecond)
	defer cancel()
	return cc.Ping(ctx)
}

func TestClientConn_Ping(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	remoteNodeName := remoteNodeID
	// pushWindowSize = 16

	ns := test.NewWorkNS(ctrl)
	localNode := ns.NewMockNode("localhost", cLogger)
	remoteNode := ns.NewMockNode(remoteNodeID, cLogger)
	defer ns.Release()

	lsn := NewMsgBusListener(un.NewBlockSyncTransport(remoteNode.MessageBus()), nil, cLogger)
	_ = lsn.Listen()
	go func() {
		for {
			sc, err := lsn.Accept()
			if err != nil {
				t.Log("accept error", err)
				return
			}
			t.Log("server")
			go func() {
				_ = sc.Serve(handlerFunc(mockHandler))
			}()
		}
	}()
	time.Sleep(time.Second)

	dialer := NewMsgBusSyncDialer(un.NewBlockSyncTransport(localNode.MessageBus()), cLogger)
	cc, err := dialer.Dial(WithHeightContext(context.Background(), 1), remoteNodeName)
	require.Nil(t, err)
	time.Sleep(10 * time.Millisecond)
	for i := 0; i < 2; i++ {
		err = ping(cc)
		require.Nil(t, err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Millisecond)
	defer cancel()
	err = cc.Ping(ctx)
	require.Nil(t, err)
}

func TestClientConn_PullBlock(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	ns := test.NewWorkNS(ctrl)
	localNode := ns.NewMockNode("localhost", cLogger)
	remoteNode := ns.NewMockNode(remoteNodeID, cLogger)
	defer ns.Release()

	lsn := NewMsgBusListener(un.NewBlockSyncTransport(remoteNode.MessageBus()), nil, cLogger)
	_ = lsn.Listen()
	go func() {
		for {
			sc, err := lsn.Accept()
			if err != nil {
				t.Log("accept error", err)
				return
			}
			t.Log("server")
			go func() {
				_ = sc.Serve(handlerFunc(mockHandler))
			}()
		}
	}()
	time.Sleep(time.Second)

	dialer := NewMsgBusSyncDialer(un.NewBlockSyncTransport(localNode.MessageBus()), cLogger)
	cc, err := dialer.Dial(WithHeightContext(context.Background(), 1), remoteNodeID)
	if err != nil {
		t.Log("dialer error", err)
		t.Fail()
		return
	}

	time.Sleep(100 * time.Millisecond)
	mode := sp.NewShardingMode(1, 1, 0)
	datas, err := pull(cc, types.BlockSyncRequest{
		Height:    1,
		Num:       1,
		WithRWSet: true,
		ModeData:  mode.ToModeData(),
	})
	if err != nil {
		cc.Close()
		t.Log("pull data error", err)
		return
	}
	for _, data := range datas {
		t.Log("got data", data.Height, string(data.Data))
	}
	cc.Close()

	time.Sleep(2 * time.Second)
	cc, err = dialer.Dial(WithHeightContext(context.Background(), 1), remoteNodeID)
	if err != nil {
		t.Log("dialer error", err)
		return
	}
	defer cc.Close()
	time.Sleep(100 * time.Millisecond)

	datas, err = pull(cc, types.BlockSyncRequest{
		Height:   2,
		Num:      1,
		ModeData: mode.ToModeData(),
	})
	if err != nil {
		t.Log("pull data error", err)
		return
	}
	for _, data := range datas {
		t.Log("got data", data.Height, string(data.Data))
	}
}

func TestClientConn_PullBlockError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ns := test.NewWorkNS(ctrl)
	localNode := ns.NewMockNode("localhost", cLogger)
	remoteNode := ns.NewMockNode(remoteNodeID, cLogger)
	defer ns.Release()

	lsn := NewMsgBusListener(un.NewBlockSyncTransport(remoteNode.MessageBus()), nil, cLogger)
	lsn.Listen()
	go func() {
		for {
			sc, err := lsn.Accept()
			if err != nil {
				t.Log("accept error", err)
				return
			}
			t.Log("server")
			go sc.Serve(handlerFunc(mockHandlerError))
		}
	}()
	time.Sleep(time.Second)

	dialer := NewMsgBusSyncDialer(un.NewBlockSyncTransport(localNode.MessageBus()), cLogger)
	cc, err := dialer.Dial(WithHeightContext(context.Background(), 1), remoteNodeID)
	if err != nil {
		t.Log("dialer error", err)
		t.Fail()
		return
	}

	time.Sleep(100 * time.Millisecond)
	mode := sp.NewShardingMode(1, 1, 0)
	_, err = pull(cc, types.BlockSyncRequest{
		Height:    1,
		Num:       1,
		WithRWSet: true,
		ModeData:  mode.ToModeData(),
	})
	require.NotNil(t, err)
	cc.Close()
	t.Log("pull data error:", err)
}
