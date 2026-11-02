/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0

*/

package blockhelper

import (
	"reflect"
	"testing"
)

func TestConstructTxIDKey(t *testing.T) {
	type args struct {
		txId string
	}
	tests := []struct {
		name string
		args args
		want []byte
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := ConstructTxIDKey(tt.args.txId); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("ConstructTxIDKey() = %v, want %v", got, tt.want)
			}
		})
	}
}
