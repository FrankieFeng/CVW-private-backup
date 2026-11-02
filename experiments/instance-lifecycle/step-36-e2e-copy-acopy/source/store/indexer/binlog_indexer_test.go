/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package indexer

import (
	"reflect"
	"testing"

	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2/test"
	"chainmaker.org/chainmaker/store/v2/serialization"
)

func initTestBinLoggerIndexer() BinLoggerIndexer {
	return NewBinLoggerIndexer(newMemBinLog(),
		serialization.NewNormalProtobufBlockNormalizer(),
		&test.GoLogger{})
}

func Test_binLoggerIndexer_ReadBlock(t *testing.T) {
	indexer := initTestBinLoggerIndexer()
	type args struct {
		height uint64
		opts   []ReadOption
	}
	tests := []struct {
		name    string
		fields  BinLoggerIndexer
		args    args
		want    *storePb.BlockWithRWSet
		want1   *storePb.StoreInfo
		wantErr bool
	}{
		// TODO: Add test cases.
		{
			name:   "case1",
			fields: indexer,
			args: args{
				height: 0,
				opts: []ReadOption{
					WithFromLatestFile(),
				},
			},
			want:    nil,
			want1:   nil,
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := tt.fields

			block, rwset := createBlockAndRWSets("test", tt.args.height, 1)
			brw := &storePb.BlockWithRWSet{
				Block:    block,
				TxRWSets: rwset,
			}
			_, index, err := b.WriteBlock(brw)
			if (err != nil) != tt.wantErr {
				t.Errorf("binLoggerIndexer.AddBlock() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			got, got1, err := b.ReadBlock(tt.args.height, tt.args.opts...)
			if (err != nil) != tt.wantErr {
				t.Errorf("binLoggerIndexer.ReadBlock() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, brw) {
				t.Errorf("binLoggerIndexer.ReadBlock() got = %v, want %v", got, brw)
			}
			if !reflect.DeepEqual(got1, index.Index) {
				t.Errorf("binLoggerIndexer.ReadBlock() got1 = %v, want %v", got1, index.Index)
			}
		})
	}
}
