/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package types

// Buffer is a buffer
type Buffer struct {
	cap int
	buf []byte
}

// NewBuffer creates a new Buffer with the given capacity.
//
// Parameters:
// - cap: the capacity of the buffer
//
// Returns:
// - a pointer to the newly created Buffer
func NewBuffer(cap int) *Buffer {
	return &Buffer{
		cap: cap,
		buf: make([]byte, 0, cap),
	}
}

// Append appends the given data to the buffer.
func (b *Buffer) Append(data []byte) {
	b.buf = append(b.buf, data...)
}

// Discard all the data in the buffer.
func (b *Buffer) Discard() {
	b.buf = b.buf[:0]
}

// Reset clears the buffer and resets its capacity.
func (b *Buffer) Reset() {
	// Create a new empty byte slice with the same capacity as the original buffer.
	b.buf = make([]byte, 0, b.cap)
}

// Bytes returns the contents of the buffer as a byte slice.
func (b *Buffer) Bytes() []byte {
	return b.buf
}
