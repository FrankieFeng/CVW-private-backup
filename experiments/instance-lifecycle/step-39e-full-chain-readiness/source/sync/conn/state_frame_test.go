/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */
package conn

import (
	"context"
	"io"
	"sync"
	"testing"
	"time"

	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func Test_pingFrame(t *testing.T) {
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
							t.Logf("read frame error: %v", err)
						}
						return
					}
					// t.Logf("server read frame: %+v\n", frame)
					pf := frame.(pingFrame)
					t.Logf("server read frame: %+v\n", pf)
					if err := fconn.Write(syncPingAckWriter(pf.Key())); err != nil {
						t.Errorf("server write frame error: %v", err)
						return
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
	if err = fconn.Write(syncPingAckWriter(pingBytes{0x01})); err != nil {
		t.Errorf("write frame error: %v", err)
		return
	}
	frame, err := fconn.Read()
	if err != nil {
		t.Errorf("client read frame error: %v", err)
		return
	}
	pf := frame.(pingFrame)
	t.Logf("client read frame: %+v\n", pf)
	require.True(t, pf.IsAck())
	require.Equal(t, []byte{0x01}, pf.Key())
}

func Test_finishFrame(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ctxe, cancele := context.WithCancel(context.Background())
	defer cancele()
	doDial, serverChan := initTwoNodesConnEnv(ctxe, ctrl)
	group := sync.WaitGroup{}
	defer group.Wait()
	go func() {
		for {
			fconn, ok := <-serverChan
			if !ok {
				return
			}
			group.Add(1)
			go func() {
				defer group.Done()
				defer fconn.Close()
				for {
					frame, err := fconn.Read()
					if err != nil {
						t.Logf("read frame error: %v", err)
						return
					}
					// t.Logf("server read frame: %+v\n", frame)
					pf := frame.(finishFrame)
					t.Logf("server read finishFrame: %+v\n", pf)
					if err := fconn.Write(syncFinishWriter()); err != nil {
						t.Logf("server write frame error: %v", err)
						return
					}
					t.Log("server write finishFrame")
				}
			}()
		}
	}()

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	fconn, err := doDial(ctx)
	if err != nil {
		t.Logf("dialer error: %v", err)
		return
	}
	defer fconn.Close()
	if err = fconn.Write(syncFinishWriter()); err != nil {
		t.Errorf("write frame error: %v", err)
		return
	}
	t.Logf("client write finishFrame")
	frame, err := fconn.Read()
	if err != nil {
		t.Errorf("client read frame error: %v", err)
		return
	}
	pf := frame.(finishFrame)
	t.Logf("client read finishFrame: %+v\n", pf)

}
