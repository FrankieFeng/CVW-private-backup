/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// Package queue provides queue implementation such as Priority queue、delay queue.
package queue

import "container/heap"

// Item is the element in the Priority queue
type Item struct {
	//Value is the real value saved by the user
	Value interface{}
	//Priority the larger the value, the higher the Priority.
	Priority int64
	//index the position index of the element in the queue.
	index int
}

type sortedQueue interface {
	heap.Interface
	Front() interface{}
}

// PriorityQueue a Priority queue.
type PriorityQueue struct {
	sq sortedQueue
}

// NewPriorityQueue create a priority queue with priorities arranged from large to small.
func NewPriorityQueue(preAlloc int) *PriorityQueue {
	return &PriorityQueue{
		sq: newReverseSortQueue(preAlloc),
	}
}

// NewReversePriorityQueue create a reverse priority queue, with priorities arranged from small to large
func NewReversePriorityQueue(preAlloc int) *PriorityQueue {
	q := sortQueue(make([]*Item, 0, preAlloc))
	return &PriorityQueue{
		sq: &q,
	}
}

// Len get the length of the queue.
func (pq *PriorityQueue) Len() int { return pq.sq.Len() }

// Push item to the Priority queue
func (pq *PriorityQueue) Push(item *Item) {
	heap.Push(pq.sq, item)
}

// Pop get the first item and remove it from the Priority queue
func (pq *PriorityQueue) Pop() *Item {
	item := heap.Pop(pq.sq)
	if item == nil {
		return nil
	}
	return item.(*Item)
}

// Front get the first item in the Priority queue, but don't remove it.
func (pq *PriorityQueue) Front() *Item {
	item := pq.sq.Front()
	if item == nil {
		return nil
	}
	return item.(*Item)
}

// Remove removes and returns the element at index i from the PriorityQueue.
func (pq *PriorityQueue) Remove(item *Item) {
	heap.Remove(pq.sq, item.index)
}

// sortQueue arrange from small to large
type sortQueue []*Item

// Len get the length of the queue.
func (sq sortQueue) Len() int { return len(sq) }

// Less arrange from small to large
func (sq sortQueue) Less(i, j int) bool {
	return (sq)[i].Priority < (sq)[j].Priority
}

// Swap implements sort.Interface to swap items by Priority
func (sq sortQueue) Swap(i, j int) {
	sq[i], sq[j] = sq[j], sq[i]
	sq[i].index = i
	sq[j].index = j
}

// Push x to the Priority queue
func (sq *sortQueue) Push(x interface{}) {
	n := len(*sq)
	item, _ := x.(*Item)
	item.index = n
	*sq = append(*sq, item)
}

// Pop get the first item and remove it from the Priority queue
func (sq *sortQueue) Pop() interface{} {
	old := *sq
	n := len(old)
	item := old[n-1]
	item.index = -1
	*sq = old[0 : n-1]
	return item
}

// Front get the first item in the Priority queue, but don't remove it.
func (sq sortQueue) Front() interface{} {
	if len(sq) == 0 {
		return nil
	}
	return sq[0]
}

// reverseSortQueue arrange from large to small
type reverseSortQueue struct {
	sortQueue
}

func newReverseSortQueue(preAlloc int) *reverseSortQueue {
	return &reverseSortQueue{
		sortQueue: sortQueue(make([]*Item, 0, preAlloc)),
	}
}

// Less arrange from large to small
func (rsq *reverseSortQueue) Less(i, j int) bool {
	return (rsq.sortQueue)[i].Priority > (rsq.sortQueue)[j].Priority
}
