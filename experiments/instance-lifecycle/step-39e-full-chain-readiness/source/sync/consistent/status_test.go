/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package consistent

import (
	"testing"

	"github.com/test-go/testify/require"
)

func TestStatus(t *testing.T) {
	syncNode := NewSyncNode(testNodeIds[0])
	require.Equal(t, testNodeIds[0], syncNode.ID())
	require.Equal(t, syncNode.statuses, syncNode.Statuses())

	newNodeStatus := NewNodeStatus()
	require.Equal(t, newNodeStatus, syncNode.StatusByType(TypeNodeState))

	newStatus := &NodeStatus{
		height: 100,
	}
	syncNode.UpdateStatus(newStatus)
	nodeStatus := syncNode.StatusByType(TypeNodeState)
	require.Equal(t, TypeNodeState, nodeStatus.Type())
	require.Equal(t, uint64(100), nodeStatus.Data())

}
