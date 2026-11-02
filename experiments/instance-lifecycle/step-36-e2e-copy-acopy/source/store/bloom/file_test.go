/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package bloom

import (
	"crypto/rand"
	"fmt"
	"io"
	"math/big"
	"os"
	"testing"

	"github.com/bits-and-blooms/bloom/v3"
)

func TestWriteMeta(t *testing.T) {
	testFile := "bloom1.log"
	defer func() {
		os.Remove(testFile)
	}()
	f, err := newBloomFile(testFile)
	if err != nil {
		t.Error(err)
		return
	}
	defer func() {
		f.close()
	}()
	for i := 0; i < 3; i++ {
		meta := &bloomMeta{
			id:    f.id + 1,
			label: 1,
		}
		meta.checksum = meta.sum64()
		err = f.writeMeta(meta)
		if err != nil {
			t.Error(err)
		}
		_ = f.init()
		if *f.bloomMeta() != *meta {
			t.Error("meta not match")
		}
	}
}

func Test_bloomFile_dump_load(t *testing.T) {
	testFile := "bloom2.log"
	defer func() {
		os.Remove(testFile)
	}()
	f, err := newBloomFile(testFile)
	if err != nil {
		t.Error(err)
		t.Fail()
	}
	n, fp := 10000, 0.001
	filter := bloom.NewWithEstimates(uint(n), fp)
	size, _ := filter.WriteTo(io.Discard)
	type args struct {
		label  uint64
		filter *BloomFilter
	}
	tests := []struct {
		name    string
		fields  *bloomFile
		args    args
		wantErr bool
	}{
		{
			name:   "test1",
			fields: f,
			args: args{label: 1, filter: &BloomFilter{
				BloomFilter: filter,
				file:        f,
				fp:          fp,
				entries:     uint(n),
				writeSize:   size,
			}},
		},
		{
			name:   "test2",
			fields: f,
			args: args{label: 1, filter: &BloomFilter{
				BloomFilter: filter,
				file:        f,
				fp:          fp,
				entries:     uint(n),
				writeSize:   size,
			}},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			f := &bloomFile{
				header: tt.fields.header,
				meta:   tt.fields.meta,
				file:   tt.fields.file,
				id:     tt.fields.id,
			}
			b := new(big.Int).SetInt64(1000)
			n, _ := rand.Int(rand.Reader, b)
			for i := 0; i < 10; i++ {
				filter.Add([]byte(fmt.Sprintf("test%d", n)))
			}
			if err := f.dump(tt.args.label, tt.args.filter); (err != nil) != tt.wantErr {
				t.Errorf("bloomFile.dump() error = %v, wantErr %v", err, tt.wantErr)
			}

			tmpFilter := &BloomFilter{}
			_, _ = tmpFilter.loadFromFile(f)

			if !tmpFilter.Equal(tt.args.filter.BloomFilter) {
				t.Errorf("bloomFile.load() filter not match")
			}
		})
	}
}
