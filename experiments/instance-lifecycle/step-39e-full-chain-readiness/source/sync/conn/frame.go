/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"bytes"
	"errors"
	"fmt"
	"io"
)

const (
	frameHeaderMaxLen = 6
	dataMaxLenLog     = 30
	dataMaxLen        = 1 << dataMaxLenLog
)

var (
	//ErrDataTooLarge occurs when the size of the data waiting to be sent is large than 2^32.
	ErrDataTooLarge = errors.New("data too large")
	//ErrShortWrite occurs when the size of the data has been written is less than the size of the raw data.
	ErrShortWrite = io.ErrShortWrite
	//ErrProtocolIncompatible occurs when the protocol version is less than the peer protocol version.
	ErrProtocolIncompatible = errors.New("protocol is incompatible")
)

type (
	frameType uint8

	frameFlag uint8

	frameWriter interface {
		writeFrame(*framer) error
	}

	frame interface {
		Header() frameHeader
		Payload() interface{}
		frameWriter
	}

	framePayload interface {
		marshalTo(*framer) error
		unmarshal([]byte) error
	}

	frameHeader struct {
		Length uint32
		Type   frameType
		Flag   frameFlag
	}

	syncFrame struct {
		frameHeader
		payload framePayload
	}
)

const (
	flagNone frameFlag = 1 << iota
	//sync flag ack
	flagAck
)

// Has the frameFlag 'f' contain the syncFlag 'v' or not.
func (f frameFlag) Has(v frameFlag) bool {
	return (f & v) == v
}

// framer write frame to the w and  read frame from r.
type framer struct {
	r    io.Reader
	rbuf bytes.Buffer
	//wbuf stitching a complete frame of data.
	//frame structure is that
	//proto version(1byte) | data length(4bytes) | proto type(1byte) | proto flag(1byte) | data content(n bytes)
	// wbuf []byte
	frameBuffer
	w io.Writer
	//headerBuffer the header of the frame buffer.
	// headerBuffer [frameHeaderLen]byte
}

func (f *framer) reset(r io.Reader, w io.Writer) {
	f.r = r
	f.w = w
	f.rbuf.Reset()
}

func (f *framer) startWrite(p frameType, flag frameFlag) {
	f.frameBuffer.reset()
	f.writeBytes(0, 0, 0, 0, byte(p), byte(flag))
}

func (f *framer) endWrite() error {
	wbuf := f.bytes()
	length := len(wbuf) - frameHeaderMaxLen
	if length >= dataMaxLen {
		return ErrDataTooLarge
	}
	n, b := lenToBytesLE(length)

	_ = append(wbuf[:0],
		byte(b[3]),
		byte(b[2]),
		byte(b[1]),
		byte(b[0]))

	wbuf = wbuf[4-n:]
	// fmt.Printf("write frame header [%+v]\n", frameHeader{
	// 	Length: uint32(length),
	// 	Type:   frameType(wbuf[n]),
	// 	Flag:  frameFlag(wbuf[n+1]),
	// })

	n, err := f.w.Write(wbuf)
	if err == nil && n != len(wbuf) {
		err = ErrShortWrite
	}
	return err
}

// readFrame read the header of a frame from r reader,
// then read the content of the frame according to the length information in the frame header.
// Parse data into different frames according to different protocol types.
func (f *framer) readFrame() (frame, error) {
	h, err := f.readHeader()
	if err != nil {
		if err == ErrProtocolIncompatible {
			_, _ = f.readData(int(h.Length))
		}
		return nil, err
	}
	d, err := f.readData(int(h.Length))
	// fmt.Printf("read frame header [%+v], buf cap: %d\n", h, f.rbuf.Cap())
	if err != nil {
		return nil, err
	}

	defer func() {
		if r := recover(); r != nil {
			fmt.Printf("frame header: %v, body: %v\n", h, d)
			panic(r)
		}
	}()

	return getSyncFrameParser(h.Type)(h, d)
}

// readHeader read the header of a frame from r reader,
// then determine whether the protocol version supports processing, if not, return a error.
func (f *framer) readHeader() (frameHeader, error) {
	if err := f.needBytes(1); err != nil {
		return frameHeader{}, err
	}
	headerLen := 3 + int(f.rbuf.Bytes()[0]>>6)
	if err := f.needBytes(headerLen); err != nil {
		return frameHeader{}, err
	}
	header := f.rbuf.Next(headerLen)
	n, dataLen := bytesBEToLen(header)
	hb := header[n:]
	return frameHeader{
		Length: uint32(dataLen),
		Type:   frameType(hb[0]),
		Flag:   frameFlag(hb[1]),
	}, nil
}

func (f *framer) needBytes(n int) error {
	for f.rbuf.Len() < n {
		if err := f.readFromUntil(n); err != nil {
			return err
		}
	}
	return nil
}

func (f *framer) readFromUntil(n int) error {
	if f.rbuf.Len() >= n {
		return nil
	}
	needs := n - f.rbuf.Len()
	f.rbuf.Grow(needs + bytes.MinRead)
	_, err := f.rbuf.ReadFrom(&atLeastReader{f.r, int64(needs)})
	if err == io.ErrUnexpectedEOF {
		err = io.EOF
	}
	return err
}

func (f *framer) readData(l int) ([]byte, error) {
	if l == 0 {
		return nil, nil
	}
	if err := f.needBytes(l); err != nil {
		return nil, err
	}
	d := make([]byte, l)
	copy(d, f.rbuf.Next(l))
	return d, nil
}

// little endian
func lenToBytesLE(l int) (n int, ret [4]byte) {
	if l == 0 {
		n = 1
	}
	for l > 0 {
		ret[n] = byte(l)
		n++
		l >>= 8
	}
	if ret[n-1]&0xc0 == 0 {
		ret[n-1] |= byte((n - 1) << 6)
	} else {
		ret[n] = byte(n << 6)
		n++
	}
	return
}

// big endian
func bytesBEToLen(p []byte) (n int, l int) {
	extra := int(p[0] >> 6)
	l = int(p[0] & 0x3f)
	for i := 1; i <= extra; i++ {
		l = l<<8 | int(p[i])
	}

	return 1 + extra, l
}

type frameParser func(fh frameHeader, payload []byte) (frame, error)

func protoErrorPanic(fh frameHeader, _ []byte) (frame, error) {
	fmt.Printf("frame header is [%+v]\n", fh)
	return nil, errSyncProtoWrong
}

var syncFrameParsers = map[frameType]frameParser{
	typeHandshake: parseHandshakeFrame,
	// typePushSetting: parsePushSettingFrame,
	typeDataPull: parseDataPullFrame,
	typeDataPush: parseDataPushFrame,
	// syncProtoReset:            parseResetFrame,
	typeFinish:           parseFinishFrame,
	typePing:             parsePingFrame,
	typePushWindowUpdate: parsePushWindowUpdateFrame,
}

// func registerFrameParser(pt frameType, fn frameParser) error {
// 	if _, ok := syncFrameParsers[pt]; ok {
// 		panic(fmt.Errorf("protocol type %d already registered", pt))
// 	}
// 	syncFrameParsers[pt] = fn
// 	return nil
// }

func getSyncFrameParser(pt frameType) frameParser {
	fn, ok := syncFrameParsers[pt]
	if !ok {
		return protoErrorPanic
	}
	return fn
}

func (f frameHeader) Header() frameHeader {
	return f
}

func newSyncFrame(h frameHeader, p framePayload) syncFrame {
	return syncFrame{
		frameHeader: h,
		payload:     p,
	}
}

func (f syncFrame) writeFrame(fr *framer) error {
	fr.startWrite(f.Type, f.Flag)
	if err := f.payload.marshalTo(fr); err != nil {
		return err
	}
	return fr.endWrite()
}

// Payload returns the payload of the frame.
func (f syncFrame) Payload() interface{} {
	return f.payload
}

type atLeastReader struct {
	r io.Reader
	n int64
}

// Read reads data from r into p until the total number of bytes read is at least n.
func (r *atLeastReader) Read(p []byte) (int, error) {
	if r.n <= 0 {
		return 0, io.EOF
	}
	n, err := r.r.Read(p)
	r.n -= int64(n)
	// If EOF is reached but not enough data has been read, return an error.
	// This is to ensure that framer.buffer's Read can break out of the loop.
	if err == io.EOF && r.n > 0 {
		return n, io.ErrUnexpectedEOF
	}
	// Avoid framer.buffer allocating memory again next time it reads
	if r.n <= 0 && err == nil {
		return n, io.EOF
	}
	return n, err
}
