/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import (
	"encoding/json"

	"chainmaker.org/chainmaker/localconf/v2"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/net"
	"chainmaker.org/chainmaker/sync/v2/types"
)

const (
	defaultBlockCacheSize      = 16
	defaultBlockChannelMaxSize = 16
)

// Config configuration for receptor creation.
type Config struct {
	//Informer the node information manager.
	Informer types.NodeInformer
	//LedgerCache local ledger.
	LedgerCache protocol.LedgerCache
	//Transport the net message.
	Transport net.Transport
	//WithRWSet whether to enable quick sync
	WithRWSet bool
	//ExposeConf exposed configurable configuration items
	ExposeConf *localconf.SyncConfig
	//Logger records logger information.
	Logger protocol.Logger
	//FragmentMerger used to merge block data fragments
	FragmentMerger types.Merger

	pushWindowSize   int
	blockChannelSize int
}

func (r *Config) complete() {
	blockPoolSize := int(r.ExposeConf.BlockPoolSize)
	if blockPoolSize == 0 {
		blockPoolSize = defaultBlockCacheSize
	}
	r.blockChannelSize = blockPoolSize / 2
	if r.blockChannelSize > defaultBlockChannelMaxSize {
		r.blockChannelSize = defaultBlockChannelMaxSize
	}
	r.pushWindowSize = blockPoolSize - r.blockChannelSize
}

// String returns the JSON representation of the Config in a human-readable format.
func (r *Config) String() string {
	// Create a configShow instance for pretty-printing the configuration
	show := configShow{
		WithRWSet:                    r.WithRWSet,
		BlockPoolSize:                r.ExposeConf.BlockPoolSize,
		ConnTimeoutScale:             r.ExposeConf.ConnTimeoutScale,
		PreferNodes:                  r.ExposeConf.FromNodes,
		IdealHeightDistance:          r.ExposeConf.IdealHeightDistance,
		WaitPeriodSecondsAfterLatest: r.ExposeConf.WaitPeriodSecondsAfterLatest,
		MaxNodesSelectedCount:        r.ExposeConf.MaxNodesSelectedCount,
	}
	// Convert the configShow instance to a JSON string and return it
	return show.String()
}

type configShow struct {
	WithRWSet                    bool     `json:"with_rWSet"`
	BlockPoolSize                uint32   `json:"block_pool_size"`
	ConnTimeoutScale             uint64   `json:"conn_timeout_scale"`
	PreferNodes                  []string `json:"prefer_nodes"`
	IdealHeightDistance          uint64   `json:"ideal_height_distance"`
	WaitPeriodSecondsAfterLatest uint32   `json:"wait_period_seconds_after_latest"`
	MaxNodesSelectedCount        int      `json:"max_nodes_selected_count"`
}

func (cs *configShow) String() string {
	bz, _ := json.Marshal(cs)
	return string(bz)
}
