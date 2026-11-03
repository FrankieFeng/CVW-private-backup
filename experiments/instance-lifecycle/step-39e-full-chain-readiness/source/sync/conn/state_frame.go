/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package conn

const (
	//typeFinish close the connection
	typeFinish frameType = 6
	//typePing ping message type
	typePing frameType = 7
)

type (
	pingFrame struct {
		syncFrame
	}

	finishMessage  struct{}
	pingBytes      []byte
	pingMessage    = pingBytes
	pingAckMessage = pingBytes

	finishFrame struct {
		syncFrame
	}
)

// newPingFrame create ping frame
func newPingFrame(fh frameHeader, p framePayload) frame {
	return pingFrame{
		newSyncFrame(fh, p),
	}
}

// newPingFrameWriter create ping frame for frame writing
func newPingFrameWriter(flag frameFlag, p framePayload) frameWriter {
	return newPingFrame(frameHeader{
		Type: typePing,
		Flag: flag,
	}, p)
}

// newFinishFrame create finish frame
func newFinishFrame(fh frameHeader) frame {
	return finishFrame{
		newSyncFrame(fh, finishMessage{}),
	}
}

// newFinishFrameWriter create finish frame for frame writing.
func newFinishFrameWriter() frameWriter {
	return newFinishFrame(frameHeader{
		Type: typeFinish,
		Flag: flagNone,
	})
}

// syncFinishWriter write finish frame.
func syncFinishWriter() frameWriter {
	return newFinishFrameWriter()
}

// syncPingWriter write ping frame with ping message
func syncPingWriter(m pingMessage) frameWriter {
	return newPingFrameWriter(flagNone, m)
}

// syncPingAckWriter write ping frame with ack
func syncPingAckWriter(m pingAckMessage) frameWriter {
	return newPingFrameWriter(flagAck, m)
}

func (m finishMessage) marshalTo(_ *framer) error {
	return nil
}

func (m finishMessage) unmarshal(_ []byte) error {
	return nil
}

func (m pingBytes) marshalTo(fr *framer) error {
	fr.writeBytev(m)
	return nil
}

func (m pingBytes) unmarshal(payload []byte) error {
	// *m = payload
	return nil
}

func parseFinishFrame(fh frameHeader, _ []byte) (frame, error) {
	return newFinishFrame(fh), nil
}

func (f pingFrame) IsAck() bool { return f.Flag.Has(flagAck) }
func (f pingFrame) Key() []byte { return f.Payload().(pingBytes) }

func parsePingFrame(fh frameHeader, payload []byte) (frame, error) {
	return newPingFrame(fh, pingBytes(payload)), nil
}
