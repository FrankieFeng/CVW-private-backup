/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"sync"
)

type flow struct {
	n int32
}

func (f *flow) available() int32 {
	return f.n
}

func (f *flow) take(n int32) {
	if n > f.available() {
		panic("internal error: took too much")
	}
	f.n -= n
}

// add adds n token (positive or negative) to the flow control window.
// It returns false if the sum would exceed 2^31-1.
func (f *flow) add(n int32) bool {
	sum := f.n + n
	if (sum > n) == (f.n > 0) {
		f.n = sum
		return true
	}
	return false
}

// pushFlow indicates the push stream flow control window
type pushFlow struct {
	flow
	locker *sync.Mutex
	cond   *sync.Cond
}

func newPushFlow(locker *sync.Mutex) *pushFlow {
	fl := &pushFlow{
		locker: locker,
		cond:   sync.NewCond(locker),
	}
	return fl
}

// take one from flow control window, if not enough, wait.
// func (f *pushFlow) take() {
// 	f.locker.Lock()
// 	defer f.locker.Unlock()
// 	f.takeLocked()
// }

func (f *pushFlow) takeLocked() {
	for {
		if f.flow.available() == 0 {
			// fmt.Printf("take flow wait: %d\n", f.flow.available())
			f.cond.Wait()
			continue
		}
		f.flow.take(1)
		return
	}
}

// add n token to the flow window, wake up who is waiting for enough tokens.
func (f *pushFlow) add(n int32) bool {
	f.locker.Lock()
	defer f.locker.Unlock()
	return f.addLocked(n)
}

func (f *pushFlow) addLocked(n int32) bool {
	ok := f.flow.add(n)
	if ok {
		f.cond.Broadcast()
	}
	return ok
}

func (f *pushFlow) resetLocked(n int32) {
	f.n = n
	f.cond.Broadcast()
}

type pushFlowWithHeight struct {
	*pushFlow
	locker        sync.Mutex
	heightWritten uint64
}

func newPushFlowWithHeight(h uint64) *pushFlowWithHeight {
	fl := &pushFlowWithHeight{
		heightWritten: h,
	}
	fl.pushFlow = newPushFlow(&fl.locker)
	return fl
}

// take one from flow control window, if not enough, wait.
// If the heightWritten is not h+1 means the heightWritten has been reset,
// return the token to the window and return false.
func (f *pushFlowWithHeight) take(h uint64) bool {
	f.locker.Lock()
	defer f.locker.Unlock()
	// fmt.Printf("take flow take: %d, %d\n", h, f.available())
	f.takeLocked()
	if h != f.heightWritten+1 { // someone fallBack
		f.addLocked(1)
		return false
	}
	f.heightWritten = h
	return true
}

// fallBack reset the flow control window to the height that has been written.
func (f *pushFlowWithHeight) fallBack(h uint64) {
	f.locker.Lock()
	defer f.locker.Unlock()
	if h >= f.heightWritten {
		return
	}
	f.addLocked(int32(f.heightWritten - h))
	f.heightWritten = h
}

// reset flow control window, the parameter hToRead is the height that has been read to by client,
// n is the window size.
// Resets the available window size based on the currently written height and the height read by the client.
func (f *pushFlowWithHeight) reset(hToRead uint64, n int32) {
	f.locker.Lock()
	defer f.locker.Unlock()
	// tn := n
	n -= int32(f.heightWritten + 1 - hToRead)
	if n < 0 {
		// fmt.Printf("internal error: reset flow control window to negative %d, height: %d, h: %d,n:%d",
		// 	n, f.heightWritten, hToRead, tn)
		return
	}
	f.resetLocked(n)
}
