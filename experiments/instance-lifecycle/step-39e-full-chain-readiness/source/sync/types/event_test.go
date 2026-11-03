/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package types

import (
	"testing"

	"github.com/golang/mock/gomock"

	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"

	"github.com/test-go/testify/require"
)

func TestEvent(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	eventList := testData()
	for _, e := range eventList {
		require.Equal(t, e.EventType(), e.Type)
		require.Equal(t, e.EventNode(), e.SyncNode)
	}
}

func testData() []*NodeEvent {
	return []*NodeEvent{
		{
			Type: EventAddNode,
			SyncNode: &syncPb.NodeInform{
				Id:     "node2",
				Height: 100,
			},
		},
		{
			Type: EventUpdateNode,
			SyncNode: &syncPb.NodeInform{
				Id:     "node2",
				Height: 102,
			},
		},
		{
			Type: EventDelNode,
			SyncNode: &syncPb.NodeInform{
				Id:     "node2",
				Height: 100,
			},
		},
		{
			Type: 10,
			SyncNode: &syncPb.NodeInform{
				Id:     "node3",
				Height: 100,
			},
		},
	}
}
