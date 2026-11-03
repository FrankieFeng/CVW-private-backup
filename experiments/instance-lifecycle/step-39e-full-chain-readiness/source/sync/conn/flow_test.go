/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"testing"
	"time"
)

func Test_pushFlowWithHeight(t *testing.T) {
	flow := newPushFlowWithHeight(0)
	flow.add(10)
	closeC := make(chan struct{})
	go func() {
		h := uint64(0)
		for {
			select {
			case <-closeC:
				if h != 15 && h != 16 {
					t.Errorf("h = %d, want 15 or 16", h)
					t.Fail()
				}
				return
			default:
				h++
				flow.take(h)
				t.Logf("take %d", h)

			}
		}
	}()
	time.Sleep(time.Second)
	flow.add(1)
	time.Sleep(time.Second)
	flow.reset(5, 10)
	time.Sleep(time.Second)
	close(closeC)
	flow.add(1)
	time.Sleep(time.Second)
}
