/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// Package slru is a LRU with 4 segments.
package slru

import (
	"container/list"
)

// S4LRU is a LRU with 4 segments to avoid cache pollution.
// 4 segments are like four levels(L3, L2, L1, L0) of cache, representing warm, hot, hotter and hottest.
type S4LRU struct {
	data   map[string]*list.Element
	layers fourLayers
	cost   func(interface{}) int64
}

// S4LRUConfig is the config for S4LRU.
type S4LRUConfig struct {
	// The max entries in S4LRU.
	Capacity int
	// The memory limit in S4LRU, 0 means no limit.
	Memory int64
	// The cost function which returns the memory size of the value.
	Cost func(interface{}) int64
}

// NewS4LRU creates a new S4LRU.
func NewS4LRU(config S4LRUConfig) *S4LRU {
	if config.Cost == nil {
		config.Cost = func(_ interface{}) int64 {
			return 0
		}
	}
	return &S4LRU{
		data:   make(map[string]*list.Element),
		layers: newFourLayers(config.Memory, config.Capacity),
		cost:   config.Cost,
	}
}

// Set adds a kv into the S4LRU. Return true if successfully added.
// Note: Non-concurrency safety
func (u *S4LRU) Set(key string, value interface{}) bool {
	evicted, ele := u.layers.Add(u.newCacheItem(key, value))
	u.tidy(evicted, []*list.Element{ele})
	return ele != nil
}

// Get a value from the S4LRU.
// If the value is in the S4LRU, the value will be moved to the hotter layer to make hot.
// If the value is not in the S4LRU, return false.
// Note: Non-concurrency safety
func (u *S4LRU) Get(key string) (interface{}, bool) {
	v, ok := u.data[key]
	if !ok {
		return nil, false
	}
	value := v.Value.(*cacheItem).value
	u.tidy(u.layers.MakeHot(v))
	return value, true
}

func (u *S4LRU) newCacheItem(key string, value interface{}) *cacheItem {
	return &cacheItem{kv: kv{key, value}, attr: attr{cost: u.cost(value)}}
}

// Remove removes an item from the S4LRU, returning the item and a boolean indicating if it was found.
// Note: Non-concurrency safety
func (u *S4LRU) Remove(key string) (interface{}, bool) {
	item, ok := u.data[key]
	if !ok {
		return nil, false
	}
	evicted := u.layers.Remove(item)
	u.tidy([]*cacheItem{evicted}, nil)
	return evicted.value, true
}

// UpdateIfHas just updates the value in the S4LRU,no affecting the hotspot location of data.
// Note: Non-concurrency safety
func (u *S4LRU) UpdateIfHas(key string, value interface{}) bool {
	ele, ok := u.data[key]
	if !ok {
		return false
	}
	ele.Value.(*cacheItem).value = value
	u.layers.Update(ele, attr{cost: u.cost(value)})
	return true
}

// Has returns true if the key is in the S4LRU, no affect the hot of the data.
func (u *S4LRU) Has(key string) bool {
	_, exist := u.data[key]
	return exist
}

// tidy removes the evicted items from the S4LRU and adds the cached items to the S4LRU.
func (u *S4LRU) tidy(evicted []*cacheItem, cached []*list.Element) {
	for _, item := range evicted {
		delete(u.data, item.key)
	}
	for _, ele := range cached {
		if ele == nil {
			continue
		}
		item, _ := ele.Value.(*cacheItem)
		u.data[item.key] = ele
	}
}

// Stats gets the stats of the S4LRU.
func (u *S4LRU) Stats() [4]Stat {
	return u.layers.stats()
}
