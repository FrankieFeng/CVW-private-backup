package cache

import (
	"sync"

	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/store/v2/globals"
)

// BlockBatch is a kv batcher with block height.
type BlockBatch struct {
	Height  uint64
	Batcher protocol.StoreBatcher
}

// FIFOBlockCache is a thread-safe FIFO cache for continuous blocks.
type FIFOBlockCache struct {
	mutex         sync.RWMutex
	pendingBlocks *ringBuffer
	logger        protocol.Logger
	lastHeight    uint64
	autoScale     bool
}

// NewAutoScaleFIFOBlockCache create a a new FIFOBlockCache instance
// which can scale it's capacity automatically.
func NewAutoScaleFIFOBlockCache(initCapacity int, logger protocol.Logger) *FIFOBlockCache {
	return newFIFOBlockCache(initCapacity, true, logger)
}

// NewFIFOBlockCache creates a new FIFOBlockCache instance with fixed capacity.
func NewFIFOBlockCache(blockWriteBufferSize int, logger protocol.Logger) *FIFOBlockCache {
	return newFIFOBlockCache(blockWriteBufferSize, false, logger)
}

func newFIFOBlockCache(capacity int, autoScale bool, logger protocol.Logger) *FIFOBlockCache {
	if capacity <= 0 {
		capacity = globals.BlockCacheDefaultSize
	}
	return &FIFOBlockCache{
		pendingBlocks: newRingBuffer(capacity),
		logger:        logger,
		autoScale:     autoScale,
	}
}

// PushBlock push a block to head of the cache.
// Note:block height must be continuous.
func (c *FIFOBlockCache) PushBlock(bt *BlockBatch) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	if c.lastHeight > 0 && bt.Height != c.lastHeight+1 {
		panic("block height is not continuous")
	}
	for {
		if c.pendingBlocks.push(bt) {
			break
		}
		if !c.autoScale {
			panic("block cache is full")
		}
		if !c.pendingBlocks.resize(c.scaleSize()) {
			panic("block cache is full, but resize failed")
		}
	}
	c.lastHeight = bt.Height
	if c.logger != nil {
		c.logger.Debugf("add block[%d] to cache, block size:%d", bt.Height, c.pendingBlocks.size())
	}
}

// PopBlock removes and returns the min height block from the cache.
// bool is false if the cache is empty.
func (c *FIFOBlockCache) PopBlock() (*BlockBatch, bool) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	return c.pendingBlocks.pop()
}

// PopBlockIf the block at the head of the cache will be popped out
// when it meets the condition of the given function.
// It is usually used to maintain the consistency of peek and pop data.
func (c *FIFOBlockCache) PopBlockIf(fn func(*BlockBatch) bool) (*BlockBatch, bool) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	batch, ok := c.pendingBlocks.peek(0)
	if !ok {
		return nil, false
	}
	if !fn(batch) {
		return nil, false
	}
	c.pendingBlocks.pop()
	return batch, true
}

// PeekMinBlock returns the min height block from the cache.
// bool is false if the cache is empty.
func (c *FIFOBlockCache) PeekMinBlock() (*BlockBatch, bool) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	return c.pendingBlocks.peek(0)
}

// Get returns the latest value associated with the key.
// bool is false if the key is not found.
func (c *FIFOBlockCache) Get(key []byte) ([]byte, bool) {
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	var (
		v   []byte
		err = errValueNotFound
	)
	c.rIterLocked(func(batch protocol.StoreBatcher) bool {
		v, err = batch.Get(key)
		return err != errValueNotFound
	})
	if err != nil {
		return nil, false
	}
	return v, true
}

// Has checks if the key exists in the cache.
// ok is true if the key exists.
// deleted is true if the key exists but has been deleted.
func (c *FIFOBlockCache) Has(key []byte) (deleted bool, ok bool) {
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	var (
		v   []byte
		err = errValueNotFound
	)
	c.rIterLocked(func(batch protocol.StoreBatcher) bool {
		v, err = batch.Get(key)
		return err != errValueNotFound
	})
	switch err {
	case nil:
		return v == nil, true
	case errValueNotFound:
		return
	default:
		panic(err)
	}
}

func (c *FIFOBlockCache) rIterLocked(call func(batch protocol.StoreBatcher) bool) {
	size := c.pendingBlocks.size()
	if size == 0 {
		return
	}
	for i := size - 1; i >= 0; i-- {
		if batch, ok := c.pendingBlocks.peek(i); ok {
			if call(batch.Batcher) {
				return
			}
		}
	}
}

// KVRange returns a map of key-value pairs in the range [startKey, endKey).
func (c *FIFOBlockCache) KVRange(startKey []byte, endKey []byte) (map[string][]byte, error) {
	keyMap := make(map[string][]byte)
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	c.rIterLocked(func(batch protocol.StoreBatcher) bool {
		batchKV := batch.KVs()
		for k, v := range batchKV {
			if k >= string(startKey) && k < string(endKey) {
				if _, exist := keyMap[k]; !exist {
					keyMap[k] = v
				}
			}
		}
		return false
	})

	return keyMap, nil
}

// GetBatch returns the batcher at the specified height.
// error is returned if the batcher is not found.
// func (c *FIFOBlockCache) GetBatch(height uint64) (protocol.StoreBatcher, error) {
// 	c.mutex.RLock()
// 	defer c.mutex.RUnlock()
// 	bh := c.lastHeight - uint64(c.pendingBlocks.size())
// 	batcher, exist := c.pendingBlocks.peek(int(height - bh))
// 	if !exist {
// 		return nil, errValueNotFound
// 	}
// 	return batcher.Batcher, nil
// }

// Size returns the count of blocks in the cache.
func (c *FIFOBlockCache) Size() int {
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	return c.pendingBlocks.size()
}

// Clear remove all data.
func (c *FIFOBlockCache) Clear() {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	c.pendingBlocks.reset()
	c.lastHeight = 0
}

func (c *FIFOBlockCache) scaleSize() int {
	capacity := c.pendingBlocks.capacity()
	if capacity < 1024 {
		return capacity * 2
	}
	return capacity * 5 / 4
}
