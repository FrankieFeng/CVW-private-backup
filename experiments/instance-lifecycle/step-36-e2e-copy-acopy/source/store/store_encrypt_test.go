/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package store

import (
	"reflect"
	"testing"
)

func Test_encryptor_Encrypt(t *testing.T) {
	symmetricKey, _ := buildEncryptor("sm4", "1234567890123456", nil)
	type args struct {
		plain []byte
	}
	tests := []struct {
		name    string
		fields  *encryptor
		args    args
		want    []byte
		wantErr bool
	}{
		{
			name: "test1",
			fields: &encryptor{
				SymmetricKey:    symmetricKey,
				encryptMaxBytes: 16,
			},
			args: args{
				plain: []byte{magicE[0], 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a'},
			},
			want: []byte{magicE[0], 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a'},
		},
		{
			name: "test2",
			fields: &encryptor{
				SymmetricKey:    symmetricKey,
				encryptMaxBytes: 16,
			},
			args: args{
				plain: []byte{'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a'},
			},
			want: []byte{'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a'},
		},
		{
			name: "test3",
			fields: &encryptor{
				SymmetricKey:    symmetricKey,
				encryptMaxBytes: 16,
			},
			args: args{
				plain: []byte{magicN[0], 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a'},
			},
			want: []byte{magicN[0], 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a'},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			e := &encryptor{
				SymmetricKey:    tt.fields.SymmetricKey,
				encryptMaxBytes: tt.fields.encryptMaxBytes,
			}
			got, err := e.Encrypt(tt.args.plain)
			if (err != nil) != tt.wantErr {
				t.Errorf("encryptor.Encrypt() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			t.Logf("encryptor.Encrypt() got = %v, len = %d", got, len(got))
			dgot, err := e.Decrypt(got)
			if (err != nil) != tt.wantErr {
				t.Errorf("encryptor.Decrypt() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(dgot, tt.want) {
				t.Errorf("encryptor.Decrypt() = %v, want %v", got, tt.want)
			}
		})
	}
}
