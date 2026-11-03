/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"context"
	"io"
	"testing"
	"time"

	sp "chainmaker.org/chainmaker/sync/v2/setting"
	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func Test_pushSettingFrame(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ctxe, cancele := context.WithCancel(context.Background())
	defer cancele()
	doDial, serverChan := initTwoNodesConnEnv(ctxe, ctrl)
	go func() {
		for {
			fconn, ok := <-serverChan
			if !ok {
				return
			}
			go func() {
				defer fconn.Close()
				var version uint64
				frame, err := fconn.Read()
				if err != nil {
					t.Errorf("server read frame error: %v", err)
					return
				}
				t.Logf("server read frame: %+v\n", frame)
				pf := frame.(dataPushFrame)
				t.Logf("server read dataPushFrame: %+v\n", pf)
				require.True(t, pf.isInit())
				settings := pf.Payload().(*pushSettingInitMessage)
				require.Equal(t, settings.SettingNum(), 2)
				settings.ForEach(func(st syncSetting) {
					switch st.ID {
					case idSyncSettingVersion:
						version = st.Val
						require.Equal(t, st.Val, uint64(1001))
					case sp.IDSyncWithRWSet:
						require.Equal(t, st.Val, uint64(1))
					}
				})

				if err := fconn.Write(pushSettingAckWriter(uint32(version))); err != nil {
					t.Errorf("write frame error: %v", err)
					return
				}
			}()
		}
	}()

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	fconn, err := doDial(ctx)
	if err != nil {
		t.Errorf("dialer error: %v", err)
		return
	}
	defer fconn.Close()
	if err = fconn.Write(pushSettingInitWriter([]syncSetting{
		{
			ID:  idSyncSettingVersion,
			Val: uint64(1001),
		},
		{
			ID:  sp.IDSyncWithRWSet,
			Val: 1,
		},
	})); err != nil {
		t.Errorf("client write frame error: %v", err)
		return
	}
	frame, err := fconn.Read()
	if err != nil {
		t.Errorf("client read frame error: %v", err)
		return
	}
	// t.Logf("client read frame: %+v\n", frame)
	pf := frame.(dataPushFrame)
	t.Logf("client read dataPushFrame: %+v\n", pf)
	require.True(t, pf.isSettingAck())
	settings := pf.Payload().(*pushSettingAckMessage)
	t.Logf("client read dataPushFrame: %+v\n", settings)
	require.Equal(t, settings.SettingNum(), 1)
	settings.ForEach(func(st syncSetting) {
		require.Equal(t, st.ID, idSyncSettingVersion)
		require.Equal(t, st.Val, uint64(1001))
	})
	time.Sleep(time.Second)
}

func Test_pushWindowsUpdate(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ctxe, cancele := context.WithCancel(context.Background())
	defer cancele()
	doDial, serverChan := initTwoNodesConnEnv(ctxe, ctrl)
	go func() {
		for {
			fconn, ok := <-serverChan
			if !ok {
				return
			}
			go func() {
				defer fconn.Close()
				for {
					frame, err := fconn.Read()
					if err != nil {
						if err != io.EOF {
							t.Errorf("server read frame error: %v", err)
						}
						return
					}
					t.Logf("server read frame: %+v\n", frame)
					pf := frame.(pushWindowUpdateFrame)
					t.Logf("server read pushWindowUpdateFrame: %+v\n", pf)
					if pf.isReset() {
						offset, size := pf.window()
						require.Equal(t, offset, uint64(100))
						require.Equal(t, size, uint16(10))
					} else {
						offset, size := pf.window()
						require.Equal(t, offset, uint64(0))
						require.Equal(t, size, uint16(4))
					}
				}
			}()
		}
	}()

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	fconn, err := doDial(ctx)
	if err != nil {
		t.Errorf("dialer error: %v", err)
		return
	}
	defer fconn.Close()
	if err := fconn.Write(syncPushWindowUpdateWriter(100, 10)); err != nil {
		t.Errorf("client write frame error: %v", err)
		return
	}
	if err := fconn.Write(syncPushWindowUpdateWriter(0, 4)); err != nil {
		t.Errorf("client write frame error: %v", err)
		return
	}
	time.Sleep(time.Second)
}
