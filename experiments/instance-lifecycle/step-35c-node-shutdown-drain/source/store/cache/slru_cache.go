/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package cache

import (
	"sync"

	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/store/v2/cache/slru"
)

const (
	log      = 2
	log4Mask = 1<<2 - 1
)

var _ Cache = (*SLRUCache)(nil)

// SLRUConfig config for slru cache.
type SLRUConfig struct {
	Memory   int64 `mapstructure:"memory"`   //Maximum memory usage in MB
	Capacity int   `mapstructure:"capacity"` //Maximum number of cache entries
	//function to calculate the memory size consumed by value.
	Cost func(interface{}) int64 `mapstructure:"-"`
}

// SLRUCache the cache with slru.
type SLRUCache struct {
	mutex  sync.Mutex
	config *SLRUConfig
	slru   *slru.S4LRU
	logger protocol.Logger
}

// NewSlruCache new slru cache.
// Make Capacity divisible by 4 and calculate the number of bytes of memory.
func NewSlruCache(c *SLRUConfig, logger protocol.Logger) *SLRUCache {
	return &SLRUCache{
		config: c,
		slru:   newS4LRU(c),
		logger: logger,
	}
}

func newS4LRU(c *SLRUConfig) *slru.S4LRU {
	var (
		capacity = c.Capacity
		memory   = c.Memory << 20
	)

	if capacity&log4Mask != 0 {
		capacity = c.Capacity >> log << log
	}
	c.Cost = func(i interface{}) int64 {
		return int64(len(i.([]byte)))
	}
	return slru.NewS4LRU(slru.S4LRUConfig{Capacity: capacity, Memory: memory, Cost: c.Cost})
}

// Set add kv to slru. If the key already exists, it will be updated.
func (c *SLRUCache) Set(key string, value []byte) error {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	c.addOrUpdate(key, value)
	return nil
}

func (c *SLRUCache) addOrUpdate(key string, value interface{}) bool {
	if c.slru.Has(key) {
		return c.slru.UpdateIfHas(key, value)
	}
	return c.slru.Set(key, value)
}

// Get gets value by key
// Reading will cause data to migrate between different levels, so concurrent reading is not possible.
func (c *SLRUCache) Get(key string) ([]byte, error) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	if v, ok := c.slru.Get(key); ok {
		return v.([]byte), nil
	}
	return nil, nil
}

// Delete delete value by key
func (c *SLRUCache) Delete(key string) error {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	c.slru.Remove(key)
	return nil
}

// Reset recreate a new slru.
func (c *SLRUCache) Reset() error {
	c.slru = newS4LRU(c.config)
	return nil
}

// Close no op.
func (c *SLRUCache) Close() error {
	return nil
}
