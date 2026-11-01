/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package slru

type level int

const (
	// L3 the lowest level for warm cache.
	L3 level = iota
	// L2 for hot cache.
	L2
	// L1 for hotter cache.
	L1
	// L0 for hottest cache.
	L0
)

// CanUp returns whether the level can be moved up.
func (l level) CanUp() bool {
	return l != L0
}

// CanDown returns whether the level can be moved down.
func (l level) CanDown() bool {
	return l != L3
}

// UpLevel returns the level that can be moved up.
func (l level) UpLevel() level {
	if l == L0 {
		return L0
	}
	return l + 1
}

// DownLevel returns the level that can be moved down.
func (l level) DownLevel() level {
	if l == L3 {
		return L3
	}
	return l - 1
}

// L0 returns whether the level is L0.
func (l level) L0() bool {
	return l == L0
}

// L3 returns whether the level is L3.
func (l level) L3() bool {
	return l == L3
}

// String returns the string representation of the level.
func (l level) String() string {
	switch l {
	case L3:
		return "L3"
	case L2:
		return "L2"
	case L1:
		return "L1"
	case L0:
		return "L0"
	default:
		return "unknown"
	}
}
