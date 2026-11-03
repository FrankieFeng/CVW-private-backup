/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */
package conn

import (
	"bytes"
	"context"
	"io"
	"math/rand"
	"testing"
	"time"

	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func Test_dataPullFrame(t *testing.T) {
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
					frameData, err := fconn.Read()
					if err != nil {
						t.Logf("server read frame error: %v", err)
						if err != io.EOF {
							t.Fail()
						}
						return
					}
					// t.Logf("server read frame: %+v\n", frame)
					pf := frameData.(dataPullFrame)
					t.Logf("server read dataPullFrame: %+v\n", pf)
					require.True(t, !pf.isAck())
					t.Logf("server read dataPul request: %+v\n", pf.pullRequest())
					if err := fconn.Write(syncDataPullAckWriter(&dataPullAckMessage{
						id:    pf.pullRequest().id,
						datas: [][]byte{[]byte("hello world")},
					})); err != nil {
						t.Logf("server write frame error: %v", err)
						t.Fail()
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
		t.Logf("dialer error: %v", err)
		t.Fail()
		return
	}
	defer fconn.Close()
	if err = fconn.Write(syncDataPullWriter(&dataPullMessage{
		id:     1,
		height: 1,
	})); err != nil {
		t.Fail()
		t.Logf("write frame error: %v", err)
		return
	}
	frameData, err := fconn.Read()
	if err != nil {
		t.Logf("client read frame error: %v", err)
		t.Fail()
		return
	}
	pf := frameData.(dataPullFrame)
	t.Logf("client read dataPullFrame: %+v\n", pf)
	require.True(t, pf.isAck())
	t.Logf("client read dataPullFrame: %+v\n", pf.pullData())
}

type pipeFrameConn struct {
	r  io.Reader
	w  io.Writer
	fr *framer
}

func newPipeFrameConn(r io.Reader, w io.Writer) *pipeFrameConn {
	return &pipeFrameConn{
		r: r,
		w: w,
		fr: &framer{
			frameBuffer: frameBuffer{
				make([]byte, frameHeaderMaxLen),
			},
			r: r,
			w: w,
		},
	}
}

func (p *pipeFrameConn) Write(fw frameWriter) error {
	return fw.writeFrame(p.fr)
}

func (p *pipeFrameConn) Read() (frame, error) {
	return p.fr.readFrame()
}

func Test_Pull(t *testing.T) {
	cr, cw := io.Pipe()
	sr, sw := io.Pipe()
	client := newPipeFrameConn(sr, cw)
	server := newPipeFrameConn(cr, sw)

	var data []byte

	go func() {
		for {
			frame, err := server.Read()
			if err != nil {
				t.Logf("server read frame error: %v", err)
				return
			}

			switch pf := frame.(type) {
			case dataPullFrame:
				if pf.isAck() {
					t.Errorf("server read dataPullFrame ack: %+v\n", frame)
				}
				req := pf.pullRequest()
				data = RandomBytes()
				server.Write(syncDataPullAckWriter(&dataPullAckMessage{
					id:    req.id,
					datas: [][]byte{data},
				}))
			default:
				t.Logf("server read frame: %+v\n", frame)
			}
		}

	}()

	for i := 0; i < 1000; i++ {
		id := uint16(16)
		client.Write(syncDataPullWriter(&dataPullMessage{
			id:     id,
			height: 1,
		}))
		frame, err := client.Read()
		if err != nil {
			t.Logf("server read frame error: %v", err)
			return
		}
		switch pf := frame.(type) {
		case dataPullFrame:
			if !pf.isAck() {
				t.Errorf("client read dataPullFrame not ack: %+v\n", frame)
				continue
			}
			resp := pf.pullData()
			if resp.id != id {
				t.Errorf("client read dataPullFrame id not match: %+v\n", frame)
			}
			t.Logf("client read data: %d\n", len(resp.datas[0]))
			if !bytes.Equal(resp.datas[0], data) {
				t.Errorf("client read dataPullFrame data not match: %+v\n", frame)
			}
		default:
			t.Logf("client read frame: %+v\n", frame)
		}
	}

	cr.Close()
	sw.Close()
	sr.Close()
	cw.Close()
}

const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

// 初始化随机种子（仅需一次）
func init() {
	rand.Seed(time.Now().UnixNano())
}

// 生成随机字符串
func RandomBytes() []byte {
	l := len(charset)
	// #nosec G404
	length := rand.Intn(1 << 23)
	b := make([]byte, length)
	for i := range b {
		// #nosec G404
		b[i] = charset[i%l] //charset[rand.Intn(len(charset))]
	}
	return b
}
