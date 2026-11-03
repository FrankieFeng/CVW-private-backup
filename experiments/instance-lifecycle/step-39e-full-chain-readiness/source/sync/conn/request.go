/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"context"
	"fmt"

	"chainmaker.org/chainmaker/sync/v2/types"
)

type writeRequest interface {
	waiter
	getFrame() frameWriter
}

type frameSender interface {
	Send(context.Context, writeRequest) error
}

// SenderFunc is a function that implements the frameSender interface.
type SenderFunc func(context.Context, writeRequest) error

// Send sends a frame request.
// It takes a frameRequest as an argument and returns an error.
func (f SenderFunc) Send(ctx context.Context, fr writeRequest) error {
	return f(ctx, fr)
}

// newFrameRequest creates a new frameRequest.
// The context is used to manage the lifecycle of the request which waits for a response.
func newFrameRequest(key string, frame frameWriter) *frameRequest {
	return &frameRequest{
		key:   key,
		frame: frame,
	}
}

// newFrameRequestWithoutKey creates a new frameRequest without key.
// This is used for requests that do not require a response or do not need to wait for a response.
func newFrameRequestWithoutKey(frame frameWriter) *frameRequest {
	return &frameRequest{
		frame: frame,
	}
}

type frameRequest struct {
	key      string
	frame    frameWriter
	resultCh chan interface{}
}

func (fr *frameRequest) id() string {
	return fr.key
}

func (fr *frameRequest) deadline() int64 {
	return 0
}

func (fr *frameRequest) notify(resp interface{}) {
	if fr.resultCh == nil {
		return
	}
	select {
	case fr.resultCh <- resp:
	default:
	}
}

func (fr *frameRequest) getFrame() frameWriter {
	return fr.frame
}

// Request sends a frame request to the remote node and waits for the result.
// It returns the result of the request or an error if the request fails.
// The result is sent to the result channel, and the function blocks until
// the result is received or the context is canceled.
func (fr *frameRequest) Request(ctx context.Context, w frameSender) (interface{}, error) {
	fr.resultCh = make(chan interface{}, 1)
	if err := w.Send(ctx, fr); err != nil {
		return nil, err
	}
	result := <-fr.resultCh
	switch resp := result.(type) {
	case error:
		return nil, resp
	default:
		return resp, nil
	}
}

// Send sends the frame request to the remote node.
// It returns an error if the send operation fails.
// This function is used to send the request without waiting for a response.
func (fr *frameRequest) Send(ctx context.Context, w frameSender) error {
	return w.Send(ctx, fr)
}

type frameWriteRequest struct {
	req  writeRequest
	done chan error
}

type settingFrameRequest struct {
	*frameRequest
	call func()
}

// newSettingAckAwaiter create a settingAckAwaiter to wait for setting ack.
// call is to ensure that ack and some processing are executed synchronously.
func newSettingFrameRequest(version uint32, frame frameWriter, call func()) *settingFrameRequest {
	return &settingFrameRequest{
		frameRequest: newFrameRequest(fmt.Sprintf("%d", version), frame),
		call:         call,
	}
}

// notify the settingAckAwaiter of the result.
// If the result is a error, the settingAckAwaiter will be notified directly.
// If the result is nil, the settingAckAwaiter will be notified after the call.
func (sfr *settingFrameRequest) notify(in interface{}) {
	if _, ok := in.(error); ok {
		sfr.frameRequest.notify(in)
		return
	}
	if sfr.call != nil {
		sfr.call()
	}
	sfr.frameRequest.notify(in)
}

// Request send a setting frame request to the remote node and wait for the the result of the setting request.
func (sfr *settingFrameRequest) Request(ctx context.Context, w frameSender) error {
	sfr.resultCh = make(chan interface{}, 1)
	if err := w.Send(ctx, sfr); err != nil {
		return err
	}
	result := <-sfr.resultCh
	switch resp := result.(type) {
	case error:
		return resp
	default:
		return nil
	}
}

// blockSyncRequest wrap types.BlockSyncRequest to generate key and frameWriter.
type blockSyncRequest struct {
	types.BlockSyncRequest
}

// syncDataPullWriter generate the frameWriter for pull block
func (r *blockSyncRequest) syncDataPullWriter(id uint16) (string, frameWriter) {
	msg := &dataPullMessage{
		id:        id,
		height:    r.Height,
		num:       uint32(r.Num),
		withRWSet: r.WithRWSet,
		mode:      r.ModeData.ToSettingV(),
	}
	return keyOf(msg), syncDataPullWriter(msg)

}

// Key generate unique key which is used to identify the request.
func (r *blockSyncRequest) Key() string {
	return keyOf(r)
}

// keyOf generate unique key which is used to identify the request.
func keyOf(o interface{}) string {
	switch obj := o.(type) {
	case blockSyncRequest:
		return fmt.Sprintf("%d_%d_%d", obj.Height, obj.Num, obj.ModeData.ToSettingV())
	case *blockSyncRequest:
		return fmt.Sprintf("%d_%d_%d", obj.Height, obj.Num, obj.ModeData.ToSettingV())
	case dataPullAckMessage:
		return fmt.Sprintf("pull_%d", obj.id)
	case *dataPullAckMessage:
		return fmt.Sprintf("pull_%d", obj.id)
	case dataPullMessage:
		return fmt.Sprintf("pull_%d", obj.id)
	case *dataPullMessage:
		return fmt.Sprintf("pull_%d", obj.id)
	default:
		panic("please implement")
	}
}

func toInternalSyncRequest(req types.BlockSyncRequest) blockSyncRequest {
	return blockSyncRequest{
		req,
	}
}

type dataWithVersion struct {
	settingVersion uint32
	data           types.DataFragment
}

// responseWaiter wait for the response of the request.
type responseWaiter struct {
	writeRequest
	doneC chan struct{} // waiter ends the wait
}

// newResponseWaiter create a responseWaiter to wait for the response of the request.
func newResponseWaiter(req writeRequest) *responseWaiter {
	return &responseWaiter{
		writeRequest: req,
		doneC:        make(chan struct{}),
	}
}

// notify the responseWaiter of the result.
func (r *responseWaiter) notify(in interface{}) {
	close(r.doneC)
	r.writeRequest.notify(in)
}

// done return the channel used to notify whether to end the waiting
func (r *responseWaiter) done() <-chan struct{} {
	return r.doneC
}
