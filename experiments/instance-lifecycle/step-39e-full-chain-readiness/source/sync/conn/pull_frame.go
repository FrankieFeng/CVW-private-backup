package conn

const (
	//typeDataPull pull data message.
	typeDataPull frameType = 3
)

type (
	dataPullFrame struct {
		syncFrame
	}

	dataPullMessage struct {
		// request id
		id uint16
		// block height for request
		height uint64
		// block count for request
		num uint32
		// whether request with rwset
		withRWSet bool
		// pull mode how to process the block data.
		mode uint64
	}

	dataPullAckMessage struct {
		// request id
		id uint16
		// set the error code if failed
		errCode uint32
		// block data
		datas [][]byte
	}
)

// newDataPullFrame create data pull frame
func newDataPullFrame(fh frameHeader, p framePayload) frame {
	return dataPullFrame{
		newSyncFrame(fh, p),
	}
}

// newDataPullFrameWriter create data pull frame for frame writing
func newDataPullFrameWriter(flag frameFlag, p framePayload) frame {
	return newDataPullFrame(frameHeader{
		Type: typeDataPull,
		Flag: flag,
	}, p)
}

// syncDataPullWriter create data pull frame with data pull message for frame writing.
func syncDataPullWriter(m *dataPullMessage) frameWriter {
	return newDataPullFrameWriter(flagNone, m)
}

// syncDataPullAckWriter create data pull frame with data pull ack message for frame writing.
func syncDataPullAckWriter(m *dataPullAckMessage) frameWriter {
	return newDataPullFrameWriter(flagAck, m)
}

func (m *dataPullMessage) marshalTo(fr *framer) error {
	var rwSet byte
	if m.withRWSet {
		rwSet = 1
	}
	fr.writeUint16(m.id)
	fr.writeUint64(m.height)
	fr.writeUint32(m.num)
	fr.writeByte(rwSet)
	fr.writeUint64(m.mode)
	return nil
}

func (m *dataPullMessage) unmarshal(payload []byte) error {
	p := frameString(payload)
	return m.unmarshalP(&p)
}

func (m *dataPullMessage) unmarshalP(p *frameString) error {
	m.id = p.readUint16()
	m.height = p.readUint64()
	m.num = p.readUint32()
	m.withRWSet = p.readByte() == 1
	m.mode = p.readUint64()
	return nil
}

func (m *dataPullAckMessage) marshalTo(fr *framer) error {
	// if err := m.dataPullMessage.marshalTo(fr); err != nil {
	// 	return err
	// }
	fr.writeUint16(m.id)
	fr.writeUint32(m.errCode)
	for _, bz := range m.datas {
		fr.writeUint32(uint32(len(bz)))
		fr.writeBytev(bz)
	}
	return nil
}

func (m *dataPullAckMessage) unmarshal(payload []byte) error {
	p := frameString(payload)
	m.id = p.readUint16()
	// if err := m.dataPullMessage.unmarshalP(&p); err != nil {
	// 	return err
	// }
	m.errCode = p.readUint32()
	for p.len() > 0 {
		l := p.readUint32()
		m.datas = append(m.datas, p.readN(int(l)))
	}
	return nil
}

func (f dataPullFrame) pullData() *dataPullAckMessage {
	return f.Payload().(*dataPullAckMessage)
}

func (f dataPullFrame) isAck() bool { return f.Flag.Has(flagAck) }

func (f dataPullFrame) pullRequest() *dataPullMessage {
	return f.Payload().(*dataPullMessage)
}

// parseDataPullFrame parse data pull frame.
func parseDataPullFrame(fh frameHeader, payload []byte) (frame, error) {
	var m framePayload
	switch fh.Flag {
	case flagNone:
		m = new(dataPullMessage)
	case flagAck:
		m = new(dataPullAckMessage)
	}
	if err := m.unmarshal(payload); err != nil {
		return nil, err
	}
	return newDataPullFrame(fh, m), nil
}
