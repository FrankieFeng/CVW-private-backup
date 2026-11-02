/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package slru

import (
	"bytes"
	"crypto/rand"
	"testing"
)

func TestCache_Add(t *testing.T) {
	cache := NewS4LRU(S4LRUConfig{
		Capacity: 100,
		Memory:   10240,
		Cost: func(v interface{}) int64 {
			bz := v.([]byte)
			return int64(len(bz))
		},
	})
	type args struct {
		key   string
		value interface{}
	}
	tests := []struct {
		name   string
		fields *S4LRU
		args   args
		want   bool
	}{
		{
			name:   "add1",
			fields: cache,
			args: args{
				key:   "key1",
				value: genRandomBytes(50),
			},
			want: true,
		},
		{
			name:   "add2",
			fields: cache,
			args: args{
				key:   "key2",
				value: genRandomBytes(60),
			},
			want: true,
		},
		{
			name:   "add3",
			fields: cache,
			args: args{
				key:   "key3",
				value: genRandomBytes(3000),
			},
			want: true,
		},
		{
			name:   "add4",
			fields: cache,
			args: args{
				key:   "key4",
				value: genRandomBytes(1000),
			},
			want: true,
		},
	}
	var keys []string
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := tt.fields
			if got := c.Set(tt.args.key, tt.args.value); got != tt.want {
				t.Errorf("Cache.Add() = %v, want %v", got, tt.want)
			}
			for _, k := range keys {
				c.Get(k)
			}
			if v, _ := c.Get(tt.args.key); v == nil || !bytes.Equal(v.([]byte), tt.args.value.([]byte)) {
				t.Errorf("Cache.Get() = %s, want %s", v, tt.args.value)
			}
			keys = append(keys, tt.args.key)
		})
	}
	for _, k := range keys {
		if v, _ := cache.Get(k); v == nil {
			t.Errorf("Cache.Get() = %s, want %s", v, k)
		}
	}
}

const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

func genRandomBytes(size int) []byte {
	bytes := make([]byte, size)
	if _, err := rand.Read(bytes); err != nil {
		panic(err)
	}
	for i, b := range bytes {
		bytes[i] = charset[b%byte(len(charset))]
	}
	return bytes
}
