package cache

import (
	"crypto/rand"
	"fmt"
	"math/big"
	"reflect"
	"strings"
	"testing"
	"time"

	"chainmaker.org/chainmaker/protocol/v2/test"
	"chainmaker.org/chainmaker/store/v2/types"
)

func TestFIFOBlockCache_Get(t *testing.T) {
	cache := NewFIFOBlockCache(10, test.GoLogger{})
	for i := 1; i <= 10; i++ {
		batch := types.NewUpdateBatch()
		batch.Put([]byte(fmt.Sprintf("key%d", i)), []byte(fmt.Sprintf("value%d", i)))
		for j := 0; j < 10; j++ {
			batch.Put(randBytes(4), randBytes(10))
		}
		cache.PushBlock(&BlockBatch{
			Height:  uint64(i),
			Batcher: batch,
		})
	}
	type args struct {
		key []byte
	}
	tests := []struct {
		name   string
		fields *FIFOBlockCache
		args   args
		want   []byte
		want1  bool
	}{
		// TODO: Add test cases.
		{
			name:   "get",
			fields: cache,
			args:   args{key: []byte("key1")},
			want:   []byte("value1"),
			want1:  true,
		},
		{
			name:   "get",
			fields: cache,
			args:   args{key: []byte("key100")},
			want:   nil,
			want1:  false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := tt.fields

			got, got1 := c.Get(tt.args.key)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("FIFOBlockCache.Get() got = %v, want %v", got, tt.want)
			}
			if got1 != tt.want1 {
				t.Errorf("FIFOBlockCache.Get() got1 = %v, want %v", got1, tt.want1)
			}
		})
	}
}

func TestFIFOBlockCache_Has(t *testing.T) {
	cache := NewFIFOBlockCache(10, test.GoLogger{})
	for i := 1; i <= 10; i++ {
		batch := types.NewUpdateBatch()
		batch.Put([]byte(fmt.Sprintf("key%d", i)), []byte(fmt.Sprintf("value%d", i)))
		for j := 0; j < 10; j++ {
			batch.Put(randBytes(4), randBytes(10))
		}
		cache.PushBlock(&BlockBatch{
			Height:  uint64(i),
			Batcher: batch,
		})
		if i%2 == 0 {
			batch.Delete([]byte(fmt.Sprintf("key%d", i)))
		}
	}

	type args struct {
		key []byte
	}
	tests := []struct {
		name        string
		fields      *FIFOBlockCache
		args        args
		wantDeleted bool
		wantOk      bool
	}{
		// TODO: Add test cases.
		{
			name:        "has",
			fields:      cache,
			args:        args{key: []byte("key1")},
			wantDeleted: false,
			wantOk:      true,
		},
		{
			name:        "has",
			fields:      cache,
			args:        args{key: []byte("key2")},
			wantDeleted: true,
			wantOk:      true,
		},
		{
			name:        "has",
			fields:      cache,
			args:        args{key: []byte("key100")},
			wantDeleted: false,
			wantOk:      false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := tt.fields
			gotDeleted, gotOk := c.Has(tt.args.key)
			if gotDeleted != tt.wantDeleted {
				t.Errorf("FIFOBlockCache.Has() gotDeleted = %v, want %v", gotDeleted, tt.wantDeleted)
			}
			if gotOk != tt.wantOk {
				t.Errorf("FIFOBlockCache.Has() gotOk = %v, want %v", gotOk, tt.wantOk)
			}
		})
	}
}

func TestFIFOBlockCache_PushBlockPanic(t *testing.T) {
	cache := NewFIFOBlockCache(10, test.GoLogger{})
	defer func() {
		if r := recover(); !strings.Contains(r.(string), "cache is full") {
			t.Errorf("The code did not panic with unexpected error: %v", r)
		}
	}()
	for i := 1; i <= 11; i++ {
		batch := types.NewUpdateBatch()
		batch.Put([]byte(fmt.Sprintf("key%d", i)), []byte(fmt.Sprintf("value%d", i)))
		for j := 0; j < 10; j++ {
			batch.Put(randBytes(4), randBytes(10))
		}
		cache.PushBlock(&BlockBatch{
			Height:  uint64(i),
			Batcher: batch,
		})
	}
}

func TestAutoScaleFIFOBlockCache_PushBlock(t *testing.T) {
	cache := NewAutoScaleFIFOBlockCache(10, test.GoLogger{})
	defer func() {
		if r := recover(); r != nil {
			t.Errorf("The code did not panic with unexpected error: %v", r)
		}
	}()
	count1 := 500
	for i := 1; i <= count1; i++ {
		batch := types.NewUpdateBatch()
		batch.Put([]byte(fmt.Sprintf("key%d", i)), []byte(fmt.Sprintf("value%d", i)))
		for j := 0; j < 10; j++ {
			batch.Put(randBytes(4), randBytes(10))
		}
		cache.PushBlock(&BlockBatch{
			Height:  uint64(i),
			Batcher: batch,
		})
	}
	t.Logf("cache count: %d, cap: %d", cache.pendingBlocks.size(), cache.pendingBlocks.capacity())
	time.Sleep(time.Second)
	count2 := 1000
	for i := count1 + 1; i <= count1+count2; i++ {
		batch := types.NewUpdateBatch()
		batch.Put([]byte(fmt.Sprintf("key%d", i)), []byte(fmt.Sprintf("value%d", i)))
		for j := 0; j < 10; j++ {
			batch.Put(randBytes(4), randBytes(10))
		}
		cache.PushBlock(&BlockBatch{
			Height:  uint64(i),
			Batcher: batch,
		})
	}
	t.Logf("cache count: %d, cap: %d", cache.pendingBlocks.size(), cache.pendingBlocks.capacity())

	cache.Clear()
	t.Logf("cache count: %d, cap: %d", cache.pendingBlocks.size(), cache.pendingBlocks.capacity())

	cache.pendingBlocks.resize(10)
	if cache.pendingBlocks.capacity() != 10 {
		t.Errorf("resize failed")
	}
}

func BenchmarkFifoBlockCache_Get(b *testing.B) {
	cache := NewFIFOBlockCache(10, test.GoLogger{})
	for i := 1; i <= 10; i++ {
		batch := types.NewUpdateBatch()
		batch.Put([]byte(fmt.Sprintf("key%d", i)), []byte(fmt.Sprintf("value%d", i)))
		for j := 0; j < 10; j++ {
			batch.Put(randBytes(4), randBytes(10))
		}
		cache.PushBlock(&BlockBatch{
			Height:  uint64(i),
			Batcher: batch,
		})
	}
	b.ResetTimer()
	b.Run("get", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			cache.Get([]byte("key0"))
		}
	})
}

func BenchmarkCacheMgr_Get(b *testing.B) {
	cache := NewStoreCacheMgr("", 10, test.GoLogger{})
	for i := 1; i <= 10; i++ {
		batch := types.NewUpdateBatch()
		batch.Put([]byte(fmt.Sprintf("key%d", i)), []byte(fmt.Sprintf("value%d", i)))
		for j := 0; j < 10; j++ {
			batch.Put(randBytes(4), randBytes(10))
		}
		cache.AddBlock(uint64(i), batch)
	}
	b.ResetTimer()
	b.Run("get", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			cache.Get("key0")
		}
	})
}

const letterBytes = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

func randBytes(n int) []byte {
	b := make([]byte, n)
	max := new(big.Int).SetInt64(int64(len(letterBytes)))
	for i := range b {
		n, _ := rand.Int(rand.Reader, max)
		b[i] = letterBytes[n.Int64()]
	}
	return b
}
