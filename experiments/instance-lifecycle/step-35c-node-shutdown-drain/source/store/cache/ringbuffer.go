package cache

// var (
// 	errRingBufferEmpty = errors.New("ring buffer is empty")
// 	errRingBufferFull  = errors.New("ring buffer is full")
// )

// ringBuffer is a not thread-safe ring buffer
type ringBuffer struct {
	data  []*BlockBatch
	w, r  int
	cap   int
	count int
}

// newRingBuffer create a new ring buffer with the given capacity.
func newRingBuffer(cap int) *ringBuffer {
	return &ringBuffer{
		data: make([]*BlockBatch, cap),
		cap:  cap,
	}
}

// push add the value to the end of the ring buffer which will cause the write cursor to move forward.
// If the ring buffer is full, the addition fails and return false.
func (rb *ringBuffer) push(value *BlockBatch) bool {
	if rb.count == rb.cap {
		return false
	}

	rb.data[rb.w] = value
	rb.w = (rb.w + 1) % rb.cap
	rb.count++
	return true
}

// pop remove the first value from the ring buffer which will cause the read cursor to move forward.
// return false when the ring buffer is empty
func (rb *ringBuffer) pop() (*BlockBatch, bool) {
	if rb.count == 0 {
		return nil, false
	}

	value := rb.data[rb.r]
	rb.data[rb.r] = nil
	rb.r = (rb.r + 1) % rb.cap
	rb.count--
	return value, true
}

// peek get the value at index i from the ring buffer will not cause the read cursor to move.
// return false when the index is out of range.
func (rb *ringBuffer) peek(i int) (*BlockBatch, bool) {
	if i < 0 || i >= rb.count {
		return nil, false
	}
	index := (rb.r + i) % rb.cap
	return rb.data[index], true
}

// resize resize the ring buffer to the given capacity.
func (rb *ringBuffer) resize(cap int) bool {
	if cap < rb.count || cap == rb.cap {
		return false
	}
	newData := make([]*BlockBatch, cap)
	for i := 0; i < rb.count; i++ {
		newData[i] = rb.data[(rb.r+i)%rb.cap]
	}
	rb.data = newData
	rb.cap = cap
	rb.r = 0
	rb.w = rb.count
	return true
}

// reset clear all data in the ring buffer and reset the read and write cursor.
func (rb *ringBuffer) reset() {
	for {
		if rb.w == rb.r {
			break
		}
		rb.data[rb.r] = nil
		rb.r = (rb.r + 1) % rb.cap
	}
	rb.w, rb.r, rb.count = 0, 0, 0
}

// size returns the count of values in the ring buffer.
func (rb *ringBuffer) size() int {
	return rb.count
}

// capacity returns the capacity of the ring buffer.
func (rb *ringBuffer) capacity() int {
	return rb.cap
}
