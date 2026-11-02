/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package slru

import (
	"container/list"
)

type (
	kv struct {
		key   string
		value interface{}
	}
	cacheItem struct {
		kv
		attr
		lidx level
	}
	attr struct {
		cost int64
	}
)

type layer struct {
	l *cachedList
	// l           *list.List
	evictedList []*cacheItem
	cap         int
	memoryUsed  int64
	memoryMax   int64
}

func newLayer(memory int64, cap int) *layer {
	if memory <= 0 && cap <= 0 {
		panic("memory or cap must be greater than 0")
	}
	return &layer{
		l: newCachedList(),
		// l:         list.New(),
		cap:       cap,
		memoryMax: memory,
	}
}

// Add adds the item into the layer cache, if the layer is full,
// either in terms of memory usage or number of entries,
// some cache entries will be evicted to place this item.
// The evicted cache entries will be returned and the new entry which is put to the front of the layer.
func (l *layer) Add(in *cacheItem) ([]*cacheItem, *list.Element) {
	var (
		alloced bool
		evicted []*cacheItem
	)
	defer func() {
		// clear the evicted list for memory usage
		l.evictedList = l.evictedList[:0]
	}()
	if evicted, alloced = l.malloc(in); !alloced {
		return nil, nil
	}
	if l.full() {
		back := l.l.Back()
		bitem, _ := back.Value.(*cacheItem)
		l.mfree(bitem)
		evicted = append(evicted, bitem)
		back.Value = in
		l.l.MoveToFront(back)
		return evicted, back
	}
	return evicted, l.l.PushFront(in)
}

// Remove removes the item from the layer cache.
func (l *layer) Remove(ele *list.Element) *cacheItem {
	item, _ := ele.Value.(*cacheItem)
	l.mfree(item)
	l.l.Remove(ele)
	return item
}

// Len returns the number of items in the layer cache.
func (l *layer) Len() int {
	return l.l.Len()
}

func (l *layer) full() bool {
	return l.cap > 0 && l.Len() == l.cap
}

func (l *layer) mleft() int64 {
	return l.memoryMax - l.memoryUsed
}

func (l *layer) mfree(item *cacheItem) {
	l.memoryUsed -= item.cost
}

func (l *layer) malloc(item *cacheItem) ([]*cacheItem, bool) {
	if l.memoryMax == 0 {
		l.memoryUsed += item.cost
		return nil, true
	}
	evicteds, ok := l.makeRoom(item.cost)
	if ok {
		l.memoryUsed += item.cost
	}
	return evicteds, ok
}

// makeRoom makes room for the new item in the layer cache.
// If the item is too big which cannot be placed in the layer cache, it returns false.
func (l *layer) makeRoom(cost int64) ([]*cacheItem, bool) {
	if cost > l.memoryMax {
		return nil, false
	}
	return l.evictForRoom(cost), true
}

// evictForRoom evicts items from the layer cache to make room for the new item.
// It will traverse all elements from back to front until cache free space is greater than or equal
// to the cost of the new item.
func (l *layer) evictForRoom(cost int64) []*cacheItem {
	free := l.mleft()
	if free >= cost {
		return nil
	}
	// if the last element is enough to place the new item, do not evict, just replace the last element.
	if l.full() && l.l.Back().Value.(*cacheItem).cost+free >= cost {
		return nil
	}

	for back := l.l.Back(); back != nil; back = l.l.Back() {
		item, _ := back.Value.(*cacheItem)
		free += item.cost
		l.mfree(item)
		l.l.Remove(back)
		l.evictedList = append(l.evictedList, item)
		if free >= cost {
			break
		}
	}
	return l.evictedList
}

// MakeHot moving the item to the front of the layer cache which makes this item hottest in the layer.
func (l *layer) MakeHot(ele *list.Element) {
	l.l.MoveToFront(ele)
}

// Update updates the cost of the item in the layer cache.
func (l *layer) Update(ele *list.Element, attr attr) bool {
	item, _ := ele.Value.(*cacheItem)
	l.memoryUsed += attr.cost - item.attr.cost
	item.attr = attr
	return true
}

// fourLayers is a set of four layers cache. It know which layer the item should be placed on.
type fourLayers [4]*layer

// newFourLayers creates a set of four layers cache.
// Allocate memory and number of entries per layer according to memory limit.
// If memory limit is set, the quota ratio of each layer(l0:l1:l2:l3) is 1:2:3:4, l0 is the hottest layer.
// Otherwise, the quota ratio of each layer(l0:l1:l2:l3) is 1:1:1:1.
func newFourLayers(memory int64, cap int) fourLayers {
	const layerNum = 4
	var (
		baseMemoryPerLayer int64
		baseCapPerLayer    int
		ratios             [layerNum]int
		layers             [layerNum]*layer
	)

	if memory > 0 { // Try to fit large values ​​into the cache
		baseMemoryPerLayer = memory / 10
		baseCapPerLayer = cap / 10
		ratios = [4]int{4, 3, 2, 1}
	} else {
		baseCapPerLayer = cap / 4
		ratios = [4]int{1, 1, 1, 1}
	}

	for i := L3; ; i = i.UpLevel() {
		ratio := ratios[i]
		layers[i] = newLayer(baseMemoryPerLayer*int64(ratio), baseCapPerLayer*ratio)
		if !i.CanUp() {
			break
		}
	}
	return layers
}

// Add adds a new item into the layer L3 cache.
func (f *fourLayers) Add(in *cacheItem) ([]*cacheItem, *list.Element) {
	return f.putToLayer(in, L3)
}

// MakeHot moving the item to the front of the upper layer cache which makes this item hotter.
// If the item has been in the l0 layer, just move it to the front of L0.
// Moving to the upper layer maybe need to evict some items from the upper layer
// and we need to add the evicted items to the lower layer one by one those will cause some items
// being evicted from the lower layer and add them...repeat until the bottom layer L3.
// Returns the item that actually needs to be evicted existed in the L3 layers and those items have beem
// adjusted layer.
func (f *fourLayers) MakeHot(ele *list.Element) ([]*cacheItem, []*list.Element) {
	item, _ := ele.Value.(*cacheItem)
	// at the l0 layer, just move it to the front
	if !item.lidx.CanUp() {
		f.layer(item.lidx).MakeHot(ele)
		return nil, nil
	}
	layerLevel := item.lidx
	// move the item to a higher level cache.
	evicted, le := f.moveToLevel(ele, layerLevel.UpLevel())
	// invalid cached means the item cant been place in the upper layer due to some reasons such as
	// the size of item is larger than the cache layer. just move it to the front at the current level cache.
	if le == nil {
		f.layer(item.lidx).MakeHot(ele)
		return evicted, nil
	}

	var (
		changes     = make([]*list.Element, 1, len(evicted)+1)
		nextEvicted []*cacheItem
	)
	changes[0] = le
	if len(evicted) > 0 {
		nextEvicted = make([]*cacheItem, 0, len(evicted)/2)
	}

	// add the items those have been evicted from the upper layer to the down layer
	for ; len(evicted) > 0; layerLevel = layerLevel.DownLevel() {
		for _, item := range evicted {
			evictedItems, ele := f.putToLayer(item, layerLevel)
			if len(evictedItems) > 0 {
				nextEvicted = append(nextEvicted, evictedItems...)
			}
			if ele == nil { //never happen
				// panic("ele must not be nil")
				nextEvicted = append(nextEvicted, item)
				continue
			}
			changes = append(changes, ele)
		}

		// swapping to save allocation overhead.
		nextEvicted, evicted = evicted[:0], nextEvicted
		if !layerLevel.CanDown() {
			break
		}
	}
	return evicted, changes
}

func (f *fourLayers) layer(l level) *layer {
	return f[l]
}

// Remove removes the item from the layer cache.
func (f *fourLayers) Remove(le *list.Element) *cacheItem {
	item, _ := le.Value.(*cacheItem)
	return f.layer(item.lidx).Remove(le)
}

// Update the cost record of the item at layer cache.
func (f *fourLayers) Update(ele *list.Element, attr attr) {
	item, _ := ele.Value.(*cacheItem)
	f.layer(item.lidx).Update(ele, attr)
}

// moveToLevel moves the item from one layer to another layer.
// If moved, remove form the old layer and return the evicted items and the new element.
func (f *fourLayers) moveToLevel(ele *list.Element, l level) ([]*cacheItem, *list.Element) {
	item, _ := ele.Value.(*cacheItem)
	evicted, upEle := f.layer(l).Add(item)
	if upEle != nil {
		f.layer(item.lidx).Remove(ele)
		item.lidx = l
	}
	return evicted, upEle
}

// putToLayer puts the item not exists in any layer cache into layer cache.
func (f *fourLayers) putToLayer(item *cacheItem, l level) ([]*cacheItem, *list.Element) {
	evicted, ele := f.layer(l).Add(item)
	if ele != nil {
		item.lidx = l
	}
	return evicted, ele
}

// Stat returns the stats of the layer cache.
type Stat struct {
	Name        string // name of the layer
	Num         int    // number of items
	Memory      int64  // memory used by the layer
	Cap         int    // capacity of the layer
	MemoryLimit int64  // memory limit
}

func (f *fourLayers) stats() (s [4]Stat) {
	for i := 0; i < 4; i++ {
		layer := f.layer(level(i))
		s[i] = Stat{
			Name:        level(i).String(),
			Num:         layer.Len(),
			Memory:      layer.memoryUsed,
			Cap:         layer.cap,
			MemoryLimit: layer.memoryMax,
		}
	}
	return
}
