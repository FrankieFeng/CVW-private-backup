/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// package queue
package queue

import (
	"testing"
)

func push(pq *PriorityQueue, priority int64) {
	di := &Item{
		Value:    priority,
		Priority: priority,
	}
	pq.Push(di)
}

func TestPriorityQueue_Push(t *testing.T) {
	pq := NewPriorityQueue(0)
	push(pq, 10)
	push(pq, 2)
	push(pq, 4)
	push(pq, 3)
	push(pq, 300)
	push(pq, 100)
	push(pq, 200)
	for {
		if pq.Len() == 0 {
			return
		}
		item := pq.Front()
		t.Logf("front value:%d, priority: %d\n", item.Value, item.Priority)
		item = pq.Pop()
		if item == nil {
			return
		}
		t.Logf("value:%d, priority: %d\n", item.Value, item.Priority)
	}
}

func TestReversePriorityQueue_Push(t *testing.T) {
	pq := NewReversePriorityQueue(8)
	push(pq, 10)
	push(pq, 2)
	push(pq, 4)
	push(pq, 3)
	push(pq, 300)
	push(pq, 100)
	push(pq, 200)
	for {
		if pq.Len() == 0 {
			return
		}
		item := pq.Front()
		t.Logf("front value:%d, priority: %d\n", item.Value, item.Priority)
		item = pq.Pop()
		if item == nil {
			return
		}
		t.Logf("value:%d, priority: %d\n", item.Value, item.Priority)
	}
}
