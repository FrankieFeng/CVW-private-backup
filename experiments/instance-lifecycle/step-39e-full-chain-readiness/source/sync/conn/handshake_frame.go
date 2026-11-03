package conn

import (
	"fmt"
	"strconv"

	"chainmaker.org/chainmaker/sync/v2/internal/errors"
)

const (
	typeHandshake frameType = 1

	flagClientHandshake frameFlag = 11
	flagServerHandshake frameFlag = 12
	flagHandshakeDone   frameFlag = 13
	flagHandshakeAlert  frameFlag = 14
)

type (
	handshakeFrame struct {
		syncFrame
	}
	// BlockSupportResult describes the node's support for the requested block.
	// BlockNum: the number of blocks that can be pushed. 0: no blocks can be pushed. -1: all blocks.
	// a positive value is the number of supported.
	// Workload: node workload used to make the requesting node evaluate
	// whether to receive blocks from this peer.
	BlockSupportResult struct {
		BlockNum int
		Workload int
		Code     errors.ErrCode
	}

	clientHandshakeMsg struct {
		// block height
		Height uint64
		// supported compression algorithms
		CompressionAlgs uint16
		// supported protocols version
		SupportProtocol []uint16
		// supported data formats
		SupportDataFormats []uint16
	}
	serverHandshakeMsg struct {
		// negotiated protocol
		Protocol uint16
		// negotiated compression algorithm
		CompressionAlg uint16
		// negotiated data format
		DataFormat uint16
		// number of blocks that can be pushed
		BlockSupportResult
	}
	handshakeDoneMsg struct{}
	// Handshake alert message contains an alert code to terminate the handshake process.
	handshakeAlertMsg struct {
		Alert [2]byte
	}

	alert uint8
)

const (
	alertUnexpectedProtocol   alert = 1
	alertUnexpectedCompressor alert = 2
	alertUnexpectedDataFormat alert = 3
	alertUnexpectedMessage    alert = 10
	alertUnsupportedSync      alert = 21
	alertNodeCantBeenUsed     alert = 22
)

var alertText = map[alert]string{
	alertUnexpectedProtocol:   "unexpected protocol",
	alertUnexpectedCompressor: "unexpected compressor",
	alertUnexpectedDataFormat: "unexpected data format",
	alertUnsupportedSync:      "unsupported block sync",
	alertNodeCantBeenUsed:     "node can't be used",
	alertUnexpectedMessage:    "unexpected message",
}

// Error returns the string representation of the alert code.
func (a alert) Error() string {
	if s, ok := alertText[a]; ok {
		return s
	}
	return "alert(" + strconv.Itoa(int(a)) + ")"
}

// newHandshakeFrame creates a new handshake frame.
func newHandshakeFrame(h frameHeader, p framePayload) frame {
	return handshakeFrame{
		syncFrame: newSyncFrame(h, p),
	}
}

// newHandshakeFrameWriter creates a new handshake frame writer.
func newHandshakeFrameWriter(flag frameFlag, p framePayload) frameWriter {
	return newHandshakeFrame(frameHeader{
		Type: typeHandshake,
		Flag: flag,
	}, p)
}

// clientHandshakeFrame creates a new client handshake frame writer with client handshake message.
func clientHandshakeFrame(msg *clientHandshakeMsg) frameWriter {
	return newHandshakeFrameWriter(flagClientHandshake, msg)
}

// serverHandshakeFrame creates a new server handshake frame writer with server handshake message.
func serverHandshakeFrame(msg *serverHandshakeMsg) frameWriter {
	return newHandshakeFrameWriter(flagServerHandshake, msg)
}

// handshakeDoneFrame creates a new handshake done frame writer.
func handshakeDoneFrame() frameWriter {
	return newHandshakeFrameWriter(flagHandshakeDone, &handshakeDoneMsg{})
}

// handshakeAlertFrame creates a new handshake alert frame writer.
func handshakeAlertFrame(msg *handshakeAlertMsg) frameWriter {
	return newHandshakeFrameWriter(flagHandshakeAlert, msg)
}

func (m *clientHandshakeMsg) marshalTo(fr *framer) error {
	fr.writeUint64(m.Height)
	fr.writeUint16(m.CompressionAlgs)
	protoLen := len(m.SupportProtocol)
	fr.writeUint8(uint8(protoLen))
	for _, proto := range m.SupportProtocol {
		fr.writeUint16(proto)
	}
	dataLen := len(m.SupportDataFormats)
	fr.writeUint8(uint8(dataLen))
	for _, data := range m.SupportDataFormats {
		fr.writeUint16(data)
	}
	return nil
}

func (m *clientHandshakeMsg) unmarshal(data []byte) error {
	s := frameString(data)
	m.Height = s.readUint64()
	m.CompressionAlgs = s.readUint16()
	protoLen := int(s.readUint8())
	if protoLen > 0 {
		m.SupportProtocol = make([]uint16, protoLen)
		for i := 0; i < protoLen; i++ {
			m.SupportProtocol[i] = s.readUint16()
		}
	}

	dataLen := int(s.readUint8())
	if dataLen > 0 {
		m.SupportDataFormats = make([]uint16, dataLen)
		for i := 0; i < dataLen; i++ {
			m.SupportDataFormats[i] = s.readUint16()
		}
	}

	return nil
}

func (m *serverHandshakeMsg) marshalTo(fr *framer) error {
	fr.writeUint16(m.Protocol)
	fr.writeUint16(m.CompressionAlg)
	fr.writeUint16(m.DataFormat)
	fr.writeUint32(uint32(m.BlockNum))
	fr.writeUint32(uint32(m.Workload))
	fr.writeUint32(uint32(m.Code))
	return nil
}

func (m *serverHandshakeMsg) unmarshal(data []byte) error {
	s := frameString(data)
	m.Protocol = s.readUint16()
	m.CompressionAlg = s.readUint16()
	m.DataFormat = s.readUint16()
	m.BlockNum = int(s.readUint32())
	m.Workload = int(s.readUint32())
	m.Code = errors.ErrCode(s.readUint32())
	return nil
}

func (m *handshakeDoneMsg) marshalTo(_ *framer) error {
	return nil
}

func (m *handshakeDoneMsg) unmarshal(_ []byte) error {
	return nil
}

func (m *handshakeAlertMsg) marshalTo(fr *framer) error {
	fr.writeBytev(m.Alert[:])
	return nil
}

func (m *handshakeAlertMsg) unmarshal(data []byte) error {
	s := frameString(data)
	m.Alert[0] = s.readByte()
	m.Alert[1] = s.readByte()
	return nil
}

func (f handshakeFrame) alert() bool {
	return f.Header().Flag.Has(flagHandshakeAlert)
}

func parseHandshakeFrame(fh frameHeader, payload []byte) (frame, error) {
	var m framePayload
	switch fh.Flag {
	case flagClientHandshake:
		m = new(clientHandshakeMsg)
	case flagServerHandshake:
		m = new(serverHandshakeMsg)
	case flagHandshakeDone:
		m = new(handshakeDoneMsg)
	case flagHandshakeAlert:
		m = new(handshakeAlertMsg)
	default:
		return nil, fmt.Errorf("invalid handshake message flag: %d", fh.Flag)
	}
	if err := m.unmarshal(payload); err != nil {
		return nil, err
	}
	return newHandshakeFrame(fh, m), nil
}
