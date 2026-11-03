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

	"chainmaker.org/chainmaker/logger/v2"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/net"

	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

var (
	cLogger protocol.Logger
)

func init() {
	cLogger = logger.GetLoggerByChain(logger.MODULE_SYNC, "chain1")
}

func Test_clientConnPool_GetClientConn(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mbs, closeFunc := initCluster(ctrl, cLogger, "localNode", "remoteNode1")
	defer func() {
		_ = closeFunc()
	}()
	time.Sleep(time.Second)
	transport := newTransport(net.NewBlockSyncTransport(mbs), cLogger)
	type args struct {
		height uint64
	}
	tests := []struct {
		name    string
		fields  *endpoint
		args    args
		want    *clientConn
		wantErr bool
	}{
		{
			name: "test1",
			fields: newEndpoint("remoteNode1", blockState{
				height: 1000,
			}, cLogger),
			args: args{
				height: 100,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := tt.fields
			cc, err := getConn(p, 1, transport)
			if (err != nil) != tt.wantErr {
				t.Errorf("clientConnPool.GetClientConn() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			defer cc.release()
			require.NotNil(t, cc)
			ctx, cancel := context.WithTimeout(context.Background(), time.Second)
			defer cancel()
			st, err := cc.openStream(ctx, 1, pushSetting{
				totalNum: 1,
				rankedNo: 0,
			})
			require.Nil(t, err)
			count := 10
			for {
				time.Sleep(10 * time.Millisecond)
				if fragment, err := st.fetchData(); err == nil {
					fmt.Printf("fetch [%d] data: %s\n", fragment.Height, string(fragment.Data.Data))
				} else if fragment.Height > st.heightReceived() {
					fmt.Println("fetch data over: ", string(fragment.Data.Data))
					break
				}
				count--
				if count == 0 {
					break
				}
			}
		})
	}
}
