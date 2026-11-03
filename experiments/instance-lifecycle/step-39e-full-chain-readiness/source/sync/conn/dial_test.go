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
	"chainmaker.org/chainmaker/sync/v2/net"
	"github.com/golang/mock/gomock"
)

func TestWithHeightContext(t *testing.T) {
	ctx := context.Background()

	height := extractHeightFromCtx(ctx)
	t.Logf("%d\n", height)
	enable := extractEnableCompressionFromCtx(ctx)
	t.Logf("%v\n", enable)
}

func TestSyncDialer_Dial(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ns := test.NewWorkNS(ctrl)
	localNode := ns.NewMockNode("localhost", cLogger)
	remoteNode := ns.NewMockNode(remoteNodeID, cLogger)
	defer ns.Release()

	lsn := NewMsgBusListener(net.NewBlockSyncTransport(remoteNode.MessageBus()), nil, cLogger)
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

	dialer := NewMsgBusSyncDialer(net.NewBlockSyncTransport(localNode.MessageBus()), cLogger)

	type args struct {
		ctx  context.Context
		addr string
	}
	tests := []struct {
		name    string
		fields  *SyncDialer
		args    args
		want    *ClientConn
		wantErr bool
	}{
		// TODO: Add test cases.
		{
			name:   "test",
			fields: dialer,
			args: args{
				addr: remoteNodeID,
				ctx:  WithHeightContext(context.Background(), 1),
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			d := tt.fields
			got, err := d.Dial(tt.args.ctx, tt.args.addr)
			if (err != nil) != tt.wantErr {
				t.Errorf("SyncDialer.Dial() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			t.Logf("SyncDialer.Dial() got = %v", got)
			// if !reflect.DeepEqual(got, tt.want) {
			// 	t.Errorf("SyncDialer.Dial() = %v, want %v", got, tt.want)
			// }
		})
	}
}
