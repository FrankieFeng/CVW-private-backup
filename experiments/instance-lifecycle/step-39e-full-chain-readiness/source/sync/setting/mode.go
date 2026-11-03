/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package setting

import (
	"fmt"
)

// SyncModeType must be [1...15], 0 is reserved.
// In the constructed uint64 mode data, bits 60-63 store the mode type.
const (
	// ModeTypeSharding indicates block data will be split into multiple pieces for transmission.
	SyncModeTypeSharding uint16 = iota + 1
)

type (
	// SyncMode is the interface for sync mode.
	SyncMode interface {
		Type() uint16             // Type is the type of sync mode.
		ToModeData() SyncModeData //[63...60]mode_type|[59...0]mode_spec
		ParseFrom(v SyncModeData) // ParseFrom parses the mode data from SyncModeData.
		Spec() interface{}        // Spec returns the spec of the sync mode.
	}

	// ShardingMode is sync mode for block data sharding
	ShardingMode struct {
		spec ShardingModeSpec
	}

	// ShardingModeSpec is the spec of sharding mode.
	ShardingModeSpec struct {
		Nodes      int // Nodes is the number of nodes to be sharded.
		Index      int // Index is the index of the node means .
		Redundancy int // Redundancy is the redundancy of the sharding.
	}
	// SyncModeData is a uint64 value constructed by SyncMode.ToSettingV().
	SyncModeData uint64
)

// Type returns the type of sync mode.
func (s SyncModeData) Type() uint16 {
	return uint16(s >> 60)
}

// ToSettingV converts SyncModeData to uint64.
func (s SyncModeData) ToSettingV() uint64 {
	return uint64(s)
}

// ToMode converts SyncModeData to SyncMode.
func (s SyncModeData) ToMode() SyncMode {
	var m SyncMode
	switch s.Type() {
	case SyncModeTypeSharding:
		m = newEmptyShardingMode()
	default:
		panic(fmt.Sprintf("invalid sync mode type: %d", s.Type()))
	}
	m.ParseFrom(s)
	return m
}

// NewShardingMode creates a new sharding mode.
func NewShardingMode(nodes, index, redundancy int) *ShardingMode {
	return &ShardingMode{
		spec: ShardingModeSpec{
			Nodes:      nodes,
			Index:      index,
			Redundancy: redundancy,
		},
	}
}

// newEmptyShardingMode creates a new empty sharding mode.
func newEmptyShardingMode() *ShardingMode {
	return &ShardingMode{}
}

// Type returns the type of sync mode.
func (s *ShardingMode) Type() uint16 {
	return SyncModeTypeSharding
}

// ToModeData converts spec of ShardingMode to SyncModeData.
func (s *ShardingMode) ToModeData() SyncModeData {
	var v uint64
	v |= uint64(s.spec.Nodes) << 16
	v |= uint64(s.spec.Index) & 0xff
	v |= uint64(s.spec.Redundancy) << 32
	v |= uint64(SyncModeTypeSharding) << 60
	return SyncModeData(v)
}

// ParseFrom parses the mode data from uint64.
// The uint64 value is constructed by SyncMode.ToSettingV().
func (s *ShardingMode) ParseFrom(v SyncModeData) {
	s.spec.Nodes = int(v>>16) & 0xff
	s.spec.Index = int(v) & 0xff
	s.spec.Redundancy = int(v>>32) & 0x0fffffff
}

// Spec returns the spec of the sync mode.
// The spec is a struct that contains the number of nodes, index and redundancy.
func (s *ShardingMode) Spec() interface{} {
	return s.spec
}
