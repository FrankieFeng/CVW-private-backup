/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package conn

const (
	// ProtocolVersion11 means protocol version 1.1
	// If the protocol is updated or the protocol data changes,
	// please pay attention to adjust the version number.
	ProtocolVersion11 uint16 = 0x0101
)

var supportVersions = []uint16{
	ProtocolVersion11,
}

type (
	// CompressionAlgType compression algorithm type.
	CompressionAlgType uint16
	// CompressionAlg compression algorithm.
	CompressionAlg interface {
		Name() string
		Compress([]byte) ([]byte, error)
		Decompress([]byte) ([]byte, error)
	}
)

const (
	// CompressionNone means no compression
	CompressionNone CompressionAlgType = iota
)

const (
	// DataFormatNone means no special data format specified.
	DataFormatNone uint16 = iota
)

var (
	defaultCompressionAlgTypes = []CompressionAlgType{}
	defaultDataFormats         = []uint16{}

	// compressionAlgMap = map[CompressionAlgType]CompressionAlg{}
)

// NodeDetectFunc determine whether to synchronize blocks from the peer node based on the result.
type NodeDetectFunc func(BlockSupportResult) error

type handshakeConfig struct {
	FromHeight          uint64
	Versions            []uint16
	CompressionAlgTypes []CompressionAlgType
	DataFormats         []uint16
	NodeDetect          NodeDetectFunc
}
