/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package queue

import (
	"context"
	"testing"
	"time"

	"github.com/test-go/testify/require"
)

type delayMockItem struct {
	idx   int
	delay time.Duration
}

func (i *delayMockItem) Delay() time.Duration {
	return i.delay
}

func TestDelayQueue_Take(t *testing.T) {
	dq := NewDelayQueue()
	ctx, cancel := context.WithCancel(context.Background())
	go func() {
		time.Sleep(time.Second)
		for i := 1; i < 10; i++ {
			dq.Push(&delayMockItem{
				idx:   i,
				delay: time.Duration(i*10) * time.Millisecond,
			})
		}
		dq.Push(&delayMockItem{
			idx:   10,
			delay: time.Duration(10) * time.Millisecond,
		})
		dq.Push(&delayMockItem{
			idx:   11,
			delay: time.Minute,
		})
		time.Sleep(2 * time.Second)
		cancel()
	}()

	idx := 0
	for {
		item, ok := dq.Take(ctx)
		if !ok {
			t.Log("over", idx)
			require.Equal(t, 9, idx)
			return
		}
		idx = item.(*delayMockItem).idx
		t.Logf("idx: %d", idx)
	}
}
