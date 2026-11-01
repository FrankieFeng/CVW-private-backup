/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package encrypt

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func Test_indexer(t *testing.T) {
	indexer, err := newIndexer(".")
	if err != nil {
		t.Fatal(err)
	}
	defer os.Remove(filepath.Join(".", indexFileName))
	var lastIndex uint64
	type args struct {
		idx uint64
	}
	tests := []struct {
		name    string
		fields  *indexFile
		args    args
		wantErr bool
	}{
		{
			name:   "test1",
			fields: indexer,
			args: args{
				idx: 13,
			},
			wantErr: false,
		},
		{
			name:   "test2",
			fields: indexer,
			args: args{
				idx: 10,
			},
			wantErr: false,
		},
		{
			name:   "test2",
			fields: indexer,
			args: args{
				idx: 16,
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			i := tt.fields
			if err = i.Write(tt.args.idx); (err != nil) != tt.wantErr {
				t.Errorf("indexer.Write() error = %v, wantErr %v", err, tt.wantErr)
			}
			lastIndex = tt.args.idx
		})
	}
	indexer.Close()
	indexer, err = newIndexer(".")
	if err != nil {
		t.Fatal(err)
	}
	idx := indexer.GetIndex()
	t.Logf("idx: %d", idx)
	if idx != lastIndex {
		t.Errorf("indexer.GetIndex() expected %d, but got %d", lastIndex, idx)
	}

}

func Test_sortedFiles(t *testing.T) {
	path := "test"
	files := []string{
		"0000000000000000000001",
		"0000000000000000000005",
		"0000000000000000000010",
		"0000000000000000000011",
		"0000000000000000000020",
		"0000000000000000000100",
	}
	_ = os.Mkdir(path, 0755)
	defer os.RemoveAll(path)
	for _, name := range files {
		f, err := os.Create(filepath.Join(path, name))
		if err == nil {
			f.Close()
		}
	}
	fs, err := sortedFiles(path)
	if err != nil {
		t.Fatal(err)
	}
	t.Logf("%v", fs)

	if !reflect.DeepEqual(fs, files) {
		t.Fatalf("sortedFiles() expected %v, but got %v", files, fs)
	}
}
