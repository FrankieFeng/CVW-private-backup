/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"sync"

	"chainmaker.org/chainmaker/sync/v2/internal/queue"
)

// waiter interface
type waiter interface {
	//id get the unique ID of the waiter
	id() string
	//deadline nanosecond timestamp in local time
	deadline() int64
	//notify the waiter of the result, could be a real result or a timeout error.
	notify(interface{})
}

// waiterQueue is a priority queue of waiter,priority based on deadline time of the waiter.
type waiterQueue struct {
	sync.Mutex
	waitEleMap map[string]*queue.Item
	queue      *queue.PriorityQueue
}

func newWaiterQueue() *waiterQueue {
	return &waiterQueue{
		waitEleMap: make(map[string]*queue.Item),
		queue:      queue.NewReversePriorityQueue(8),
	}
}

// Push the waiter into the queue and sort.
// Return true indicates that the waiter already exists.
func (q *waiterQueue) Push(w waiter) bool {
	q.Lock()
	defer q.Unlock()
	id := w.id()
	if _, exist := q.waitEleMap[id]; exist {
		return true
	}
	item := &queue.Item{
		Value:    w,
		Priority: w.deadline(),
	}
	q.waitEleMap[id] = item
	q.queue.Push(item)
	return false
}

// Front get the first waiter in the queue.
func (q *waiterQueue) Front() waiter {
	q.Lock()
	defer q.Unlock()
	ele := q.queue.Front()
	if ele == nil {
		return nil
	}
	return ele.Value.(waiter)
}

// Get a waiter with id, returns nil if waiter doesn't exist.
func (q *waiterQueue) Get(id string) waiter {
	q.Lock()
	e, ok := q.waitEleMap[id]
	q.Unlock()
	if !ok || e == nil {
		return nil
	}
	return e.Value.(waiter)
}

// Pop get the first waiter and remove it from the queue.
func (q *waiterQueue) Pop() waiter {
	q.Lock()
	defer q.Unlock()
	e := q.queue.Pop()
	if e == nil {
		return nil
	}
	w, _ := e.Value.(waiter)
	delete(q.waitEleMap, w.id())
	return w
}

// Remove the waiter with id from the queue.
func (q *waiterQueue) Remove(id string) waiter {
	q.Lock()
	defer q.Unlock()
	e, exist := q.waitEleMap[id]
	if !exist {
		return nil
	}
	delete(q.waitEleMap, id)
	q.queue.Remove(e)
	return e.Value.(waiter)
}

// Len get the length of the queue.
func (q *waiterQueue) Len() int {
	return q.queue.Len()
}
