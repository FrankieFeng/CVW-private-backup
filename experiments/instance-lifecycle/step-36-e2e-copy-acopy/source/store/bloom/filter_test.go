/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package bloom

import (
	"fmt"
	"os"
	"testing"
)

func TestBloomFilter_Dump_Load(t *testing.T) {
	path := "./test.dump"
	n, fp := 1000000, 0.01
	filter, err := newBloomFilter(uint(n), fp, path)
	if err != nil {
		t.Errorf("NewBloomFilter() error = %v", err)
		t.Fail()
	}
	defer func() {
		os.Remove(path)
	}()
	type args struct {
		label uint64
	}
	tests := []struct {
		name    string
		fields  *BloomFilter
		args    args
		wantErr bool
	}{
		{
			name:   "test1",
			fields: filter,
			args: args{
				label: 1,
			},
		},
		{
			name:   "test2",
			fields: filter,
			args: args{
				label: 1,
			},
		},
	}
	for l, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			f := &BloomFilter{
				BloomFilter:   tt.fields.BloomFilter,
				file:          tt.fields.file,
				entries:       tt.fields.entries,
				fp:            tt.fields.fp,
				writeSize:     tt.fields.writeSize,
				lastDumpLabel: tt.fields.lastDumpLabel,
			}
			for i := 0; i < 10; i++ {
				filter.Add([]byte(fmt.Sprintf("test%d", i+l*100)))
			}
			if err = f.Dump(tt.args.label); (err != nil) != tt.wantErr {
				t.Errorf("BloomFilter.Dump() error = %v, wantErr %v", err, tt.wantErr)
			}
			// f.load(path)
			tmpFilter := &BloomFilter{}
			_, _ = tmpFilter.loadFromFile(tt.fields.file)
			if !tmpFilter.BloomFilter.Equal(f.BloomFilter) {
				t.Errorf("loaded filter mismatch with original error = %v, wantErr %v", err, tt.wantErr)
			}
			for i := 0; i < 10; i++ {
				if !tmpFilter.Test([]byte(fmt.Sprintf("test%d", i+l*100))) {
					t.Errorf("loaded filter can't test key")
					t.Fail()
				}
			}
		})
	}
}

// func BenchmarkDump(b *testing.B) {
// 	filter, _ := newBloomFilter(100000, 0.01, "./test.dump")
// 	defer func() {
// 		os.Remove("./test.dump")
// 	}()
// 	for i := 0; i < b.N; i++ {
// 		filter.Dump(uint64(i))
// 	}
// }
