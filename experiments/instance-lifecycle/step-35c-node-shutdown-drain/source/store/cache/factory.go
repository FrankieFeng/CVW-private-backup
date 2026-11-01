/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package cache

import (
	"fmt"
	"time"

	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/store/v2/conf"
	"github.com/allegro/bigcache/v3"
	"github.com/mitchellh/mapstructure"
)

const (
	// CacheProviderSLRU cache with slur algorithm.
	CacheProviderSLRU = "slru"
	// CacheProviderBC bigcache
	CacheProviderBC = "bigcache"
)

// NewCache construct Cache
func NewCache(cacheConf *conf.CacheConfig, logger protocol.Logger) (Cache, error) {
	return (&Factory{logger}).CreateCache(cacheConf)
}

// Factory cache factory
type Factory struct {
	logger protocol.Logger
}

// CreateCache construct Cache by cacheConf.
// According to cacheConf.Provider, create different Cache.
func (f *Factory) CreateCache(cacheConf *conf.CacheConfig) (Cache, error) {
	if cacheConf == nil {
		return newBigCache(cacheConf)
	}
	switch cacheConf.Provider {
	case CacheProviderSLRU:
		config := &SLRUConfig{}
		err := mapstructure.Decode(cacheConf.Spec, config)
		if err != nil {
			return nil, err
		}
		return NewSlruCache(config, f.logger), nil
	case CacheProviderBC:
		return newBigCache(cacheConf)
	case "": // Compatibility
		f.logger.Warn("cache provider not specified, using bigcache by default")
		return newBigCache(cacheConf)
	}
	return nil, fmt.Errorf("unknown cache provider: %s", cacheConf.Provider)
}

func newBigCache(cacheConfig *conf.CacheConfig) (Cache, error) {
	bigCacheDefaultConfig := bigcache.Config{
		// number of shards (must be a power of 2)
		Shards: 1024,
		// time after which entry can be evicted
		LifeWindow: 10 * time.Minute,
		// rps * lifeWindow, used only in initial memory allocation
		CleanWindow: 10 * time.Second,
		// max entry size in bytes, used only in initial memory allocation
		MaxEntrySize: 500,
		// prints information about additional memory allocation
		Verbose: true,
		// cache will not allocate more memory than this limit, value in MB
		// if value is reached then the oldest entries can be overridden for the new ones
		// 0 value means no size limit
		HardMaxCacheSize: 128,
		// callback fired when the oldest entry is removed because of its
		// expiration time or no space left for the new entry. Default value is nil which
		// means no callback and it prevents from unwrapping the oldest entry.
		OnRemove: nil,
	}
	// 配置文件不为空，使用给定配置
	if cacheConfig != nil {
		bigCacheDefaultConfig.LifeWindow = cacheConfig.LifeWindow
		bigCacheDefaultConfig.CleanWindow = cacheConfig.CleanWindow
		bigCacheDefaultConfig.MaxEntrySize = cacheConfig.MaxEntrySize
		bigCacheDefaultConfig.HardMaxCacheSize = cacheConfig.HardMaxCacheSize
	}
	return bigcache.NewBigCache(bigCacheDefaultConfig)
}
