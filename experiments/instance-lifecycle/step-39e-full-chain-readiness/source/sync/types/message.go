/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package types

// MsgType message type for net message handler.
type MsgType uint8

const (
	// MTCompatible compatible message for reserve
	MTCompatible = iota
	// MTNormal normal message for reserve
	MTNormal
	// MTNodeInfo represent node info message
	MTNodeInfo
	// MTConn represent message for double-ended connections
	MTConn
	// MTConsistent for consistent heart beat
	MTConsistent
)
