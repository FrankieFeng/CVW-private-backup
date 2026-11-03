/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/
package receptor

import (
	"testing"

	"chainmaker.org/chainmaker/localconf/v2"
)

func TestConfig_String(t *testing.T) {
	tests := []struct {
		name   string
		fields *Config
		want   string
	}{
		// TODO: Add test cases.
		{
			name: "test",
			fields: &Config{
				WithRWSet: true,
				ExposeConf: &localconf.SyncConfig{
					BlockPoolSize:    12,
					ConnTimeoutScale: 10,
					FromNodes: []string{
						"node1",
					},
					IdealHeightDistance:          2,
					WaitPeriodSecondsAfterLatest: 10,
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := tt.fields
			r.complete()
			t.Log(r.String())
			// if got := r.String(); got != tt.want {
			// 	t.Errorf("Config.String() = %v, want %v", got, tt.want)
			// }
		})
	}
}
