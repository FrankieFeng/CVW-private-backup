/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package types

import (
	"fmt"
	"testing"

	"github.com/golang/mock/gomock"

	"github.com/test-go/testify/require"

	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
)

func TestWatcher(t *testing.T) {
	fmt.Println("====== Start test watcher ======")
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	w := NewEventWatcher(nil)

	events := initEventData()
	for _, e := range events {
		err := w.SendEvent(e)
		require.Nil(t, err)
		e1 := <-w.ResultChan()
		require.Equal(t, e, e1)
	}
	fmt.Println("====== finish test watcher ======")
}

func initEventData() []*NodeEvent {
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
