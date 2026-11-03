package conn

import "fmt"

type frameBuffer struct {
	wbuf []byte
}

// writeByte append one byte to the end of the buffer.
func (b *frameBuffer) writeByte(v byte) { b.wbuf = append(b.wbuf, v) }

// writeBytev append multiple bytes to the end of the buffer.
func (b *frameBuffer) writeBytev(v []byte) { b.wbuf = append(b.wbuf, v...) }

func (b *frameBuffer) writeBytes(v ...byte) { b.wbuf = append(b.wbuf, v...) }

// writeUint16 append uint16 to the end of the buffer in big endian
func (b *frameBuffer) writeUint8(v uint8) { b.wbuf = append(b.wbuf, v) }

// writeUint16 append uint16 to the end of the buffer in big endian
func (b *frameBuffer) writeUint16(v uint16) { b.writeBytes(byte(v>>8), byte(v)) }

// writeUint32 append uint32 to the end of the buffer in big endian
func (b *frameBuffer) writeUint32(v uint32) {
	b.writeBytes(byte(v>>24), byte(v>>16), byte(v>>8), byte(v))
}

// writeUint32 append uint64 to the end of the buffer in big endian
func (b *frameBuffer) writeUint64(v uint64) {
	b.writeUint32(uint32(v >> 32))
	b.writeUint32(uint32(v))
}

func (b *frameBuffer) bytes() []byte { return b.wbuf }

func (b *frameBuffer) reset() { b.wbuf = b.wbuf[:0] }

type frameString []byte

func (p *frameString) readByte() byte {
	if b := p.readN(1); b != nil {
		return b[0]
	}
	return 0
}

func (p *frameString) readN(n int) []byte {
	if len(*p) < n || n < 0 {
		panic(fmt.Sprintf("internal error: read too much: read %d bytes from %d bytes", n, len(*p)))
		// return nil
	}
	v := (*p)[:n]
	*p = (*p)[n:]
	return v
}

func (p *frameString) readUint8() uint8 {
	if b := p.readN(1); b != nil {
		return b[0]
	}
	return 0
}

func (p *frameString) readUint16() uint16 {
	if b := p.readN(2); b != nil {
		return uint16(b[0])<<8 | uint16(b[1])
	}
	return 0
}

func (p *frameString) readUint32() uint32 {
	if b := p.readN(4); b != nil {
		return uint32(b[0])<<24 | uint32(b[1])<<16 | uint32(b[2])<<8 | uint32(b[3])
	}
	return 0
}

func (p *frameString) readUint64() uint64 {
	return uint64(p.readUint32())<<32 | uint64(p.readUint32())
}

func (p *frameString) readBytes() []byte {
	return p.readN(len(*p))
}

func (p *frameString) len() int {
	return len(*p)
}
