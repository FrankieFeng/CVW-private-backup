/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"testing"
)

func Test_settingList_Push(t *testing.T) {
	slist := newSettingList()
	type args struct {
		new *setting
	}

	tests := []struct {
		name   string
		fields *settingList
		args   args
	}{
		{
			name:   "test",
			fields: slist,
			args: args{
				new: &setting{
					version:     1,
					blockHeight: 1,
				},
			},
		},
		{
			name:   "test",
			fields: slist,
			args: args{
				new: &setting{
					version:     2,
					blockHeight: 10,
				},
			},
		},
		{
			name:   "test",
			fields: slist,
			args: args{
				new: &setting{
					version:     3,
					blockHeight: 20,
				},
			},
		},
		{
			name:   "test",
			fields: slist,
			args: args{
				new: &setting{
					version:     4,
					blockHeight: 10,
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := tt.fields
			l.Push(tt.args.new)
		})
	}

	var pre *settingLinker
	for ele := slist.Front(); ele != nil; ele = ele.Next() {
		if pre != nil {
			if pre.blockHeight >= ele.blockHeight {
				t.Fatal("blockHeight error")
			}
			if pre.version >= ele.version {
				t.Fatal("version error")
			}
		}
		t.Log(ele.version, ele.blockHeight)
		pre = ele
	}
}
