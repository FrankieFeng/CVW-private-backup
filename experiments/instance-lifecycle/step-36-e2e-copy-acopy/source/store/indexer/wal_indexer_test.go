/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package indexer

import (
	"os"
	"reflect"
	"testing"

	"chainmaker.org/chainmaker/common/v2/wal"
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2/test"
	"chainmaker.org/chainmaker/store/v2/serialization"
)

func initTestWalIndexer(walPath string) *WalIndexer {
	log, err := wal.Open(walPath, wal.DefaultOptions)
	if err != nil {
		panic(err)
	}
	return NewWalIndexer(log,
		serialization.NewNormalProtobufBlockNormalizer(),
		&test.GoLogger{})
}
func TestWalIndexer_ReadBlock(t *testing.T) {
	walPath := "./wal"
	defer os.RemoveAll(walPath)
	indexer := initTestWalIndexer(walPath)
	type args struct {
		height uint64
	}
	tests := []struct {
		name    string
		fields  *WalIndexer
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
			_, _, err := b.WriteBlock(brw)
			if (err != nil) != tt.wantErr {
				t.Errorf("binLoggerIndexer.AddBlock() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			got, got1, err := b.ReadBlock(tt.args.height)
			if (err != nil) != tt.wantErr {
				t.Errorf("binLoggerIndexer.ReadBlock() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, brw) {
				t.Errorf("binLoggerIndexer.ReadBlock() got = %v, want %v", got, brw)
			}
			if got1 != nil {
				t.Errorf("binLoggerIndexer.ReadBlock() got1 = %v, want %v", got1, nil)
			}
		})
	}
}
