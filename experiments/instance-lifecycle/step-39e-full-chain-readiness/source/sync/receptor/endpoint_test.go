/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import (
	"reflect"
	"testing"

	"chainmaker.org/chainmaker/protocol/v2/test"
	"github.com/test-go/testify/require"
)

func Test_endpointPool_Select(t *testing.T) {
	end1 := newEndpoint("remote1", blockState{
		height: 100,
	}, test.GoLogger{})
	end2 := newEndpoint("remote2", blockState{
		height: 110,
	}, test.GoLogger{})
	endPool := newEndpointPool(nil, test.GoLogger{}, end1, end2)
	endPool.AddEndpoint("remote3", blockState{
		height: 120,
	})
	endPool.MarkDead("remote3")

	var filter endpointFilterFunc = func(e *endpoint) bool {
		return e.isLiving() && e.Height() > 100
	}

	type args struct {
		filter endpointFilter
	}
	tests := []struct {
		name   string
		fields *endpointPool
		args   args
		want   []*endpoint
	}{
		{
			name:   "test",
			fields: endPool,
			args: args{
				filter: filter,
			},
			want: []*endpoint{
				end2,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := tt.fields
			got := p.Select(tt.args.filter)

			require.Equal(t, len(tt.want), len(got))
		})
	}
}

func Test_endpointPool_GetMaxHeight(t *testing.T) {
	end1 := newEndpoint("remote1", blockState{
		height: 100,
	}, test.GoLogger{})
	end2 := newEndpoint("remote2", blockState{
		height: 110,
	}, test.GoLogger{})
	endPool := newEndpointPool(nil, test.GoLogger{}, end1, end2)
	endPool.AddEndpoint("remote3", blockState{
		height: 120,
	})
	endPool.MarkDead("remote3")
	tests := []struct {
		name   string
		fields *endpointPool
		want   uint64
	}{
		{
			name:   "test",
			fields: endPool,
			want:   110,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := tt.fields
			if got := p.GetMaxHeight(); got != tt.want {
				t.Errorf("endpointPool.GetMaxHeight() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_sortEndpoints(t *testing.T) {
	end1 := newEndpoint("node1", blockState{
		height: 100,
	}, test.GoLogger{})
	end1.FailFor(10, metricTypeVerify)
	end2 := newEndpoint("node2", blockState{
		height: 100,
	}, test.GoLogger{})
	end2.FailFor(10, metricTypeGet)
	end3 := newEndpoint("node3", blockState{
		height: 100,
	}, test.GoLogger{})

	type args struct {
		height    uint64
		endpoints []*endpoint
	}
	tests := []struct {
		name string
		args args
		want []*endpoint
	}{
		{
			name: "test1",
			args: args{
				height:    10,
				endpoints: []*endpoint{end1, end2, end3},
			},
			want: []*endpoint{end3, end2},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := getValidEndpointsSorted(tt.args.height, tt.args.endpoints); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("sortEndpoints() = %v, want %v", got, tt.want)
			}
		})
	}
}
