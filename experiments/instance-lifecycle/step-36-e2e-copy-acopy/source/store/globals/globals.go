/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// Package globals contains global constants and variables.
package globals

const (
	// QuickWriteChannelSize is the size of the quick write channel
	QuickWriteChannelSize = 100
	// BlockCacheDefaultSize is the default size of the block cache which is used to store blocks
	// before writing to the block db. The size should be equal to QuickWriteChannelSize, but
	// the process is asynchronous, when the channel is full, a block outside the channel may be in flight.
	// So we need to add 1 to the default size.
	BlockCacheDefaultSize = QuickWriteChannelSize + 1
)
