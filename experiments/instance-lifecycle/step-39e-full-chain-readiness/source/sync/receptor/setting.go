/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import (
	ps "chainmaker.org/chainmaker/sync/v2/setting"
)

type pushSetting struct {
	totalNum   int
	rankedNo   int // begin from 0
	withRWSet  bool
	windowSize int
}

// toSettings convert pushSetting to []ps.Setting
func (s *pushSetting) toSettings() []ps.Setting {
	var (
		setts     []ps.Setting = make([]ps.Setting, 0, 3)
		withRWSet uint64
	)
	if s.withRWSet {
		withRWSet = 1
	}
	setts = append(setts, ps.Setting{
		ID:  ps.IdSyncSettingInitWindow,
		Val: uint64(s.windowSize),
	})
	if s.totalNum > 0 {
		mod := ps.NewShardingMode(s.totalNum, s.rankedNo, 0)
		setts = append(setts, ps.Setting{
			ID:  ps.IDSyncMode,
			Val: mod.ToModeData().ToSettingV(),
		})
	}
	if withRWSet > 0 {
		setts = append(setts, ps.Setting{
			ID:  ps.IDSyncWithRWSet,
			Val: withRWSet,
		})
	}
	return setts
}
