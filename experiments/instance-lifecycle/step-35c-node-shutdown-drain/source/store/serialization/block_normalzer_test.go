/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */
package serialization

import (
	"reflect"
	"testing"

	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
)

func TestNormalBlockNormalizer_NormalizeBlock(t *testing.T) {
	type args struct {
		blockWithRWSet *storePb.BlockWithRWSet
	}
	tests := []struct {
		name    string
		fields  *NormalBlockNormalizer
		args    args
		want    []byte
		want1   *BlockWithSerializedInfo
		wantErr bool
	}{
		{
			name:   "test1",
			fields: NewNormalProtobufBlockNormalizer(),
			args:   args{blockWithRWSet: createBlockAndRWSets("testchain1", 1, 100)},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := tt.fields.NormalizeBlock(tt.args.blockWithRWSet)
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockSerializer.Serialize() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			ngot, err := tt.fields.NormalizeFromSerialization(&got.SerializationNormalized)
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockSerializer.NormalizeFromSerialization() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, ngot) {
				t.Errorf("NormalBlockSerializer.DeserializeBlock() got = %v, want %v", got, ngot)
			}
		})
	}
}

func TestNormalBlockNormalizer_deserializeBatch(t *testing.T) {
	type fields struct {
		sinkCodec Serializer
	}
	type args struct {
		bytesList [][]byte
		to        interface{}
	}
	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := &NormalBlockNormalizer{
				sinkCodec: tt.fields.sinkCodec,
			}
			if err := s.deserializeBatch(tt.args.bytesList, tt.args.to); (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockNormalizer.deserializeBatch() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
