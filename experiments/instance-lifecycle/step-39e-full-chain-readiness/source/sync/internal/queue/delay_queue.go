/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package queue

import (
	"context"
	"sync"
	"sync/atomic"
	"time"
)

// DelayItem is an interface that represents an item in the delay queue.
type DelayItem interface {
	// Delay gets the delay time which is relative to the current time, for example 10s, 1m, etc.
	Delay() time.Duration
}

// DelayQueue is a priority queue that can be used to delay the execution of tasks
// based on their deadlines. It uses a min-heap to store the items, and the item with
// the earliest deadline will be at the top of the queue.
// The queue is thread-safe, so it can be used in a concurrent environment.
type DelayQueue struct {
	mu       sync.Mutex
	pq       *PriorityQueue
	timer    *time.Timer
	sleeping uint32
	wakeUpC  chan struct{}
}

// NewDelayQueue creates a new DelayQueue instance.
func NewDelayQueue() *DelayQueue {
	dq := &DelayQueue{
		pq:      NewReversePriorityQueue(8),
		wakeUpC: make(chan struct{}, 1),
	}
	dq.timer = time.NewTimer(time.Hour)
	dq.timer.Stop()
	return dq
}

// Push adds an item to the queue. The item will be added to the queue based on its
// deadline. The item with the earliest deadline will be at the top of the queue.
// If the queue is empty, the item will be added to the top of the queue.
// If the queue is not empty, the item will be added to the appropriate position
// based on its deadline.
func (dq *DelayQueue) Push(item DelayItem) {
	dq.mu.Lock()
	defer dq.mu.Unlock()
	di := &Item{
		Value:    item,
		Priority: time.Now().Add(item.Delay()).UnixNano(),
	}
	dq.pq.Push(di)
	if dq.pq.Front() == di {
		if atomic.CompareAndSwapUint32(&dq.sleeping, 1, 0) {
			dq.wakeUpC <- struct{}{}
		}
	}
}

// Take removes the item with the earliest deadline from the queue and returns it.
// If the queue is empty, it will block until an item is available.
// If the context is done, it will return nil and false.
// The item will be removed from the queue and will not be available for any other
// operations.
func (dq *DelayQueue) Take(ctx context.Context) (DelayItem, bool) {
	for {
		dq.mu.Lock()
		if dq.pq.Len() > 0 {
			item := dq.pq.Front()
			delta := item.Priority - time.Now().UnixNano()
			if delta <= 0 {
				dq.pq.Pop()
				dq.mu.Unlock()
				return item.Value.(DelayItem), true
			}
			dq.timer.Reset(time.Duration(delta))
		}
		atomic.StoreUint32(&dq.sleeping, 1)
		dq.mu.Unlock()

		select {
		case <-ctx.Done():
			dq.timer.Stop()
			return nil, false
		case <-dq.wakeUpC:
			dq.timer.Stop()
		case <-dq.timer.C:
			if atomic.SwapUint32(&dq.sleeping, 0) == 0 {
				<-dq.wakeUpC
			}
		}
	}
}
