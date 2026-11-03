/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package types

import (
	"chainmaker.org/chainmaker/sync/v2/setting"
)

// BlockSyncRequest 区块同步请求体
type BlockSyncRequest struct {
	// Height 起始同步高度
	Height uint64
	// Num 同步块数
	Num int
	// WithRWSet 是否带读写集
	WithRWSet bool
	// ModeData 同步模式数据
	ModeData setting.SyncModeData
}

// DataFragment 数据帧
type DataFragment struct {
	// Height 区块高度信息
	Height uint64
	// Data 数据信息
	Data []byte
}
