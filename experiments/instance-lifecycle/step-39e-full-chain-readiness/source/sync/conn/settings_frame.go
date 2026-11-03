package conn

import (
	"fmt"

	sp "chainmaker.org/chainmaker/sync/v2/setting"
)

const (
	//typePushSetting init or update the push stream setting.
	// typePushSetting frameType = 2
	//typePushWindowUpdate update window size message.
	typePushWindowUpdate frameType = 8

	// flagPushSettingInit   frameFlag = 21
	// flagPushSettingUpdate frameFlag = 22
	// flagPushSettingAck    frameFlag = 23

	stItemSize = 10
)

type (
	syncSetting = sp.Setting

	settings []syncSetting

	// pushSettingFrame struct {
	// 	syncFrame
	// }

	pushSettingInitMessage = settings

	pushSettingUpdateMessage = settings

	pushSettingAckMessage = settings

	pushWindowUpdateFrame struct {
		syncFrame
	}
	// pushWindowUpdateMessage uint16

	pushWindowUpdateMessage struct {
		size   uint16
		height uint64
	}
)

// pushSettingInitWriter write data push frame with init setting message
func pushSettingInitWriter(ss settings) frameWriter {
	return newPushFrameWriter(flagPushSettingInit, &ss)
}

// pushSettingUpdateWriter write data push frame with update setting message
func pushSettingUpdateWriter(ss pushSettingUpdateMessage) frameWriter {
	return newPushFrameWriter(flagPushSettingUpdate, &ss)
}

// pushSettingAckWriter write data push frame with ack setting message
func pushSettingAckWriter(version uint32) frameWriter {
	return newPushFrameWriter(flagAck, &pushSettingAckMessage{
		{
			ID:  idSyncSettingVersion,
			Val: uint64(version),
		},
	})
}

func newPushWindowUpdateFrame(fh frameHeader, p framePayload) frame {
	return pushWindowUpdateFrame{
		newSyncFrame(fh, p),
	}
}

// syncPushWindowUpdateWriter write data push frame with window update message.
// h is greater than 0 means to reset the window
func syncPushWindowUpdateWriter(h uint64, w uint16) frameWriter {
	return newPushWindowUpdateFrame(frameHeader{
		Type: typePushWindowUpdate,
		Flag: flagNone,
	}, &pushWindowUpdateMessage{
		size:   w,
		height: h,
	})
}

func (ss *settings) marshalTo(fr *framer) error {
	for _, setting := range *ss {
		fr.writeUint16(uint16(setting.ID))
		fr.writeUint64(setting.Val)
	}
	return nil
}

func (ss *settings) unmarshal(payload []byte) error {
	l := len(payload)
	if l%stItemSize != 0 {
		return fmt.Errorf("bad settings")
	}
	stn := l / stItemSize
	sts := make([]syncSetting, stn)

	parser := frameString(payload)
	for i := 0; i < int(stn); i++ {
		sts[i] = syncSetting{
			ID:  sp.ID(parser.readUint16()),
			Val: parser.readUint64(),
		}
	}
	*ss = sts
	return nil
}

// marshalTo If the height is greater than 0, it means it is a reset operation,
// and the high bit of the window size is set to 1
func (f *pushWindowUpdateMessage) marshalTo(fr *framer) error {
	if f.height > 0 {
		fr.writeUint16(uint16(f.size | 0x80))
		fr.writeUint64(f.height)
	} else {
		fr.writeUint16(uint16(f.size))
	}
	return nil
}

func (f *pushWindowUpdateMessage) unmarshal(payload []byte) error {
	s := frameString(payload)
	f.size = s.readUint16()
	if f.size&0x80 > 0 {
		f.size = f.size & 0x7f
		f.height = s.readUint64()
	}
	return nil
}

func (f *pushWindowUpdateFrame) isReset() bool {
	msg, _ := f.Payload().(*pushWindowUpdateMessage)
	return msg.height > 0
}

func (f *pushWindowUpdateFrame) window() (uint64, uint16) {
	msg, _ := f.Payload().(*pushWindowUpdateMessage)
	return msg.height, msg.size
}

func (ss settings) SettingNum() int {
	return len(ss)
}

func (ss settings) ForEach(fn func(syncSetting)) {
	for _, st := range ss {
		fn(st)
	}
}

func parsePushWindowUpdateFrame(fh frameHeader, payload []byte) (frame, error) {
	m := new(pushWindowUpdateMessage)
	if err := m.unmarshal(payload); err != nil {
		return nil, err
	}
	return newPushWindowUpdateFrame(fh, m), nil
}
