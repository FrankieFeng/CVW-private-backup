/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package conn

import (
	"sync"

	"chainmaker.org/chainmaker/sync/v2/types"
)

type pushWindow struct {
	sync.Mutex
	buf []ringEle
	rx  int    // read index of buf
	rh  uint64 // next read block height
	wh  uint64 // maximum height already written ignoring data holes
	eh  uint64 // expected next write height
}

func newPushWindow(from uint64, size int) *pushWindow {
	return &pushWindow{
		buf: make([]ringEle, size),
		rh:  from,
		eh:  from,
	}
}

func (w *pushWindow) put(data types.DataFragment) (uint64, int) {
	w.Lock()
	defer w.Unlock()
	pos := w.writePos(data.Height)
	if pos < 0 {
		return w.eh, 0 //w.vacancy()
	}
	w.buf[pos] = ringEle{
		valid: true,
		data:  data,
	}
	if data.Height > w.wh {
		w.wh = data.Height
	}
	if data.Height == w.eh {
		w.eh = w.nextExpectHeight()
	}
	return w.eh, 0 //w.vacancy()
}

func (w *pushWindow) nextExpectHeight() uint64 {
	for {
		pos := w.writePos(w.eh)
		if pos < 0 {
			return w.eh
		}
		if w.buf[pos].valid {
			w.eh++
			continue
		}
		return w.eh
	}
}

func (w *pushWindow) writePos(h uint64) int {
	dt := int(h - w.rh)
	if dt < 0 || dt >= len(w.buf) {
		return -1
	}
	return (w.rx + dt) % len(w.buf)
}

// func (w *pushWindow) vacancy() int {
// 	return len(w.buf) - int(w.wh-w.rh+1)
// }

func (w *pushWindow) cap() int {
	return len(w.buf)
}

func (w *pushWindow) fetch() (types.DataFragment, bool) {
	w.Lock()
	defer w.Unlock()
	defer func() {
		w.rh++
	}()
	if w.rh >= w.eh {
		w.eh = w.rh + 1
		w.eh = w.nextExpectHeight()
	}
	if w.rh > w.wh {
		return types.DataFragment{
			Height: w.rh,
		}, false
	}
	rx := w.rx % w.cap()
	defer func() {
		w.buf[rx].valid = false
		w.rx++
	}()
	if !w.buf[rx].valid {
		return types.DataFragment{
			Height: w.rh,
		}, false
	}
	return w.buf[rx].data, true
}

func (w *pushWindow) reset(h uint64) uint64 {
	w.Lock()
	defer w.Unlock()
	if h >= w.wh || h < w.rh {
		return w.eh
	}
	for i := h; i <= w.wh; i++ {
		w.buf[w.writePos(i)].valid = false
	}
	w.wh = h - 1
	if h < w.eh {
		w.eh = h
	}
	return w.eh
}

func (w *pushWindow) readHeight() uint64 {
	return w.rh
}

func (w *pushWindow) writeMaxHeight() uint64 {
	return w.wh
}

type windowController struct {
	*pushWindow
	countNoUpdate     int
	missCont          int
	thresholdToUpdate int
}

// newWindowController create a new window controller.
// The parameter size is the size of the window.
// Calc the threshold based on the size that controls when to update the peer window.
// If the threshold is too small, it will be set to the window size.
// If the threshold is too large, it will be set to 4.
func newWindowController(from uint64, size int) *windowController {
	threshold := size / 2
	if threshold > 4 {
		threshold = 4
	} else if threshold < 1 {
		threshold = size
	}

	return &windowController{
		pushWindow:        newPushWindow(from, size),
		thresholdToUpdate: threshold,
	}
}

// fetch get data arranged by height one by one from the cache window.
// If data does not exist add miss count, otherwise reset the count.
func (wc *windowController) fetch() (types.DataFragment, bool) {
	wc.countNoUpdate++
	data, ok := wc.pushWindow.fetch()
	if !ok {
		wc.missCont++
	} else {
		wc.missCont = 0
	}
	return data, ok
}

// If the number of failures exceeds two, there may be a problem with the sliding window
// of the peer node and it needs to be reset.
// Because the reset value is an absolute value,the height is required as a reference value.
func (wc *windowController) needUpdateWindow() (uint64, uint16) {
	if wc.missCont >= 2 {
		wc.countNoUpdate = 0
		return wc.readHeight(), uint16(wc.cap())
	}

	if wc.countNoUpdate >= wc.thresholdToUpdate {
		s := wc.countNoUpdate
		wc.countNoUpdate = 0
		return 0, uint16(s)
	}
	return 0, 0
}
