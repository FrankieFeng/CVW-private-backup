/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"context"
	"testing"
	"time"

	"chainmaker.org/chainmaker/sync/v2/internal/test"
	un "chainmaker.org/chainmaker/sync/v2/net"
	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func TestServerConn_Ping(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	remoteNodeName := "remoteNode"
	// pushWindowSize = 16

	ns := test.NewWorkNS(ctrl)
	localNode := ns.NewMockNode("localhost", cLogger)
	remoteNode := ns.NewMockNode(remoteNodeName, cLogger)
	defer ns.Release()

	lsn := NewMsgBusListener(un.NewBlockSyncTransport(remoteNode.MessageBus()), nil, cLogger)
	_ = lsn.Listen()
	errCh := make(chan error, 1)
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
			for {
				time.Sleep(10 * time.Millisecond)
				ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
				errCh <- sc.Ping(ctx)
				cancel()
			}
		}
	}()
	time.Sleep(time.Second)

	dialer := NewMsgBusSyncDialer(un.NewBlockSyncTransport(localNode.MessageBus()), cLogger)
	_, err := dialer.Dial(WithHeightContext(context.Background(), 1), remoteNodeName)
	require.Nil(t, err)
	err = <-errCh
	require.Nil(t, err)

}
