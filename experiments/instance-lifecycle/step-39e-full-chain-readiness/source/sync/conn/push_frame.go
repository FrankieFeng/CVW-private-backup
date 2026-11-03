package conn

import (
	"fmt"
)

const (
	//typeDataPush push message
	typeDataPush frameType = 4

	//data push protocol
	flagPushSettingInit frameFlag = 1 << (iota + 1)
	flagPushSettingUpdate
	flagPushEnd
	flagPushReset
)

type (
	dataPushFrame struct {
		syncFrame
	}

	dataPushMessage struct {
		version uint32
		height  uint64
		d       []byte
	}

	dataPushEndMessage struct {
		code uint32
	}

	dataPushResetMessage struct{}
)

func newPushFrame(h frameHeader, p framePayload) frame {
	return dataPushFrame{
		newSyncFrame(h, p),
	}
}

func newPushFrameWriter(flag frameFlag, p framePayload) frameWriter {
	return newPushFrame(frameHeader{
		Type: typeDataPush,
		Flag: flag,
	}, p)
}

// syncDataPushWriter write data push frame
func syncDataPushWriter(m *dataPushMessage) frameWriter {
	return newPushFrameWriter(flagNone, m)
}

// syncDataPushEndWriter write data push end frame
func syncDataPushEndWriter(code uint32) frameWriter {
	return newPushFrameWriter(flagPushEnd, &dataPushEndMessage{
		code: code,
	})
}

// syncDataPushResetWriter write data push reset frame
func syncDataPushResetWriter() frameWriter {
	return newPushFrameWriter(flagPushReset, dataPushResetMessage{})
}

func (m *dataPushMessage) marshalTo(fr *framer) error {
	fr.writeUint64(m.height)
	fr.writeUint32(m.version)
	fr.writeBytev(m.d)
	return nil
}

func (m *dataPushMessage) unmarshal(p []byte) error {
	parser := frameString(p)
	m.height = parser.readUint64()
	m.version = parser.readUint32()
	m.d = parser.readBytes()
	return nil
}

func (m *dataPushEndMessage) marshalTo(fr *framer) error {
	fr.writeUint32(uint32(m.code))
	return nil
}

func (m *dataPushEndMessage) unmarshal(p []byte) error {
	parser := frameString(p)
	m.code = parser.readUint32()
	return nil
}

func (m dataPushResetMessage) marshalTo(_ *framer) error {
	return nil
}

func (m dataPushResetMessage) unmarshal(_ []byte) error {
	return nil
}

func parseDataPushFrame(fh frameHeader, payload []byte) (frame, error) {
	var m framePayload
	switch fh.Flag {
	case flagNone:
		m = new(dataPushMessage)
	case flagPushSettingInit:
		m = new(pushSettingInitMessage)
	case flagPushSettingUpdate:
		m = new(pushSettingUpdateMessage)
	case flagAck:
		m = new(pushSettingAckMessage)
	case flagPushEnd:
		m = new(dataPushEndMessage)
	case flagPushReset:
		m = dataPushResetMessage{}
	default:
		return nil, fmt.Errorf("invalid handshake message flag: %d", fh.Flag)
	}
	if err := m.unmarshal(payload); err != nil {
		return nil, err
	}
	return newPushFrame(fh, m), nil
}

func (sf dataPushFrame) isInit() bool       { return sf.Flag.Has(flagPushSettingInit) }
func (sf dataPushFrame) isUpdate() bool     { return sf.Flag.Has(flagPushSettingUpdate) }
func (sf dataPushFrame) isSettingAck() bool { return sf.Flag.Has(flagAck) }
func (sf dataPushFrame) isData() bool       { return sf.Flag.Has(flagNone) }
func (sf dataPushFrame) isEnd() bool        { return sf.Flag.Has(flagPushEnd) }
func (sf dataPushFrame) isReset() bool      { return sf.Flag.Has(flagPushReset) }

func (sf dataPushFrame) PushData() *dataPushMessage {
	return sf.Payload().(*dataPushMessage)
}

func (sf dataPushFrame) PushEndInfo() *dataPushEndMessage {
	return sf.Payload().(*dataPushEndMessage)
}
