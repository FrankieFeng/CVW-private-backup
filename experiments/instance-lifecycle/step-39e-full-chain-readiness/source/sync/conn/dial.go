/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"context"
	"fmt"

	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/net"
)

var (
	defaultNodeDetectFn = func(resp BlockSupportResult) error {
		if resp.BlockNum == 0 {
			if resp.Code.Occurred() {
				return resp.Code
			}
			return alertNodeCantBeenUsed
		}
		return nil
	}
)

// SyncNegotiateResp sync negotiation result from remote node
// BlockNum: the number of blocks that remote nodes can give. 0: no blocks can be given. -1: all blocks until
// to the highest block. a positive value the exact amount can be given by remote node.
// Workload: the number of requesting(sync) nodes that the remote node is serving.
type SyncNegotiateResp struct {
	NodeID   string
	BlockNum int
	Workload uint32
	Code     errors.ErrCode
}

// SyncDialer the dialer used to negotiate synchronization.
// SyncDialer use the net.Dialer to establish a low-level connection,
// then communicate via a synchronous negotiated protocol.
type SyncDialer struct {
	dl     net.Dialer
	logger protocol.Logger
}

// NewMsgBusSyncDialer create a sync dialer whose underlying network uses message bus.
func NewMsgBusSyncDialer(transport net.Transport, logger protocol.Logger) *SyncDialer {
	return NewSyncDialer(net.NewMessageBusDialer(transport), logger)
}

// NewSyncDialer  create a sync dialer with the underlying net dialer.
func NewSyncDialer(dl net.Dialer, logger protocol.Logger) *SyncDialer {
	d := &SyncDialer{
		dl:     dl,
		logger: logger,
	}
	return d
}

// DialWithHeight Dial to the remote node with the current block height.
// Return a available client connection if error is nil.
// ctx can be used to control early exit from the handshake process.
// blockHeight is where the client expects to get the block from.
// addr is the node id of the remote node.
// adopt the upper logic can specify a function to judge whether the synchronous handshake is acceptable
// based on the info "SyncNegotiateResp" from remote node.
// func (d *SyncDialer) DialWithHeight(ctx context.Context,
// 	blockHeight uint64, addr string, adopt func(SyncNegotiateResp) error) (*ClientConn, error) {
// 	return d.Dial(WithHeightContext(ctx, blockHeight), addr)
// }

// Dial request to establish a connection for synchronizing block.
func (d *SyncDialer) Dial(ctx context.Context, addr string) (*ClientConn, error) {
	height := extractHeightFromCtx(ctx)
	if height == 0 {
		return nil, fmt.Errorf("height needs to be specified and must be greater than 0")
	}
	conn, err := d.dl.Dial(ctx, addr)
	if err != nil {
		return nil, err
	}

	var (
		compressionAlgTypes []CompressionAlgType
		dataFormats         []uint16
	)

	if !extractEnableCompressionFromCtx(ctx) {
		compressionAlgTypes = []CompressionAlgType{CompressionNone}
	}
	if !extractUseDataFormatFromCtx(ctx) {
		dataFormats = []uint16{DataFormatNone}
	}

	nodeDetect := extractNodeCheckFuncFromCtx(ctx)
	if nodeDetect == nil {
		nodeDetect = defaultNodeDetectFn
	}

	fconn := newFrameConn(conn)
	client := hsClient(fconn, &handshakeConfig{
		FromHeight:          height,
		CompressionAlgTypes: compressionAlgTypes,
		DataFormats:         dataFormats,
		NodeDetect:          nodeDetect,
	})

	if _, err := client.Handshake(ctx); err != nil {
		fconn.Close()
		return nil, err
	}
	return newClientConn(fconn, d.logger), nil
}

type heightCtxKey struct{}

// WithHeightContext set the height to context.
func WithHeightContext(ctx context.Context, height uint64) context.Context {
	if ctx == nil {
		ctx = context.Background()
	}
	return context.WithValue(ctx, heightCtxKey{}, height)
}

func extractHeightFromCtx(ctx context.Context) uint64 {
	h, _ := ctx.Value(heightCtxKey{}).(uint64)
	return h
}

type compressCtxKey struct{}

// WithEnableCompressionContext set the enable compression to context.
func WithEnableCompressionContext(ctx context.Context) context.Context {
	return context.WithValue(ctx, compressCtxKey{}, true)
}

func extractEnableCompressionFromCtx(ctx context.Context) bool {
	enable, _ := ctx.Value(compressCtxKey{}).(bool)
	return enable
}

type useDataFormatCtxKey struct{}

// WithEnableDataFormatContext set the enable data format to context.
func WithEnableDataFormatContext(ctx context.Context) context.Context {
	return context.WithValue(ctx, useDataFormatCtxKey{}, true)
}

func extractUseDataFormatFromCtx(ctx context.Context) bool {
	enable, _ := ctx.Value(useDataFormatCtxKey{}).(bool)
	return enable
}

type nodeCheckFuncCtxKey struct{}

// WithNodeCheckFuncContext set the node check function to context.
// The function is used to determine whether to synchronize blocks from the peer node based on the result.
func WithNodeCheckFuncContext(ctx context.Context, f NodeDetectFunc) context.Context {
	return context.WithValue(ctx, nodeCheckFuncCtxKey{}, f)
}

func extractNodeCheckFuncFromCtx(ctx context.Context) NodeDetectFunc {
	f, _ := ctx.Value(nodeCheckFuncCtxKey{}).(NodeDetectFunc)
	return f
}
