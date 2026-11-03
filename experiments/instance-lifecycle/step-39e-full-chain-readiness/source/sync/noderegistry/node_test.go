/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package noderegistry

import (
	"testing"

	"chainmaker.org/chainmaker/pb-go/v2/sync"
	"github.com/test-go/testify/require"
)

func Test_nodeSets_add(t *testing.T) {
	nds := newNodeSets()
	ok := nds.add(&sync.NodeInform{
		Id: "node1",
	})
	require.True(t, ok)
	ok = nds.add(&sync.NodeInform{
		Id: "node1",
	})
	require.False(t, ok)
	ok = nds.add(&sync.NodeInform{
		Id:     "node1",
		Height: 100,
	})
	require.False(t, ok)

	ok = nds.remove("node1")
	require.True(t, ok)

	ok = nds.add(&sync.NodeInform{
		Id:     "node1",
		Height: 100,
	})
	require.True(t, ok)
}

func Test_nodeSets_update(t *testing.T) {
	nds := newNodeSets()
	ok := nds.update(&sync.NodeInform{
		Id: "node1",
	})
	require.False(t, ok)

	ok = nds.add(&sync.NodeInform{
		Id: "node1",
	})
	require.True(t, ok)
	ok = nds.update(&sync.NodeInform{
		Id:     "node1",
		Height: 100,
	})
	require.True(t, ok)

	ok = nds.update(&sync.NodeInform{
		Id:     "node1",
		Height: 100,
	})
	require.False(t, ok)

	ok = nds.remove("node1")
	require.True(t, ok)

	ok = nds.update(&sync.NodeInform{
		Id:     "node1",
		Height: 110,
	})
	require.False(t, ok)
}

func Test_nodeSets_remote(t *testing.T) {
	nds := newNodeSets()
	ok := nds.remove("node1")
	require.False(t, ok)

	ok = nds.add(&sync.NodeInform{
		Id: "node1",
	})
	require.True(t, ok)
	ok = nds.remove("node1")
	require.True(t, ok)
}

func Test_nodeSets_isLiving(t *testing.T) {
	nds := newNodeSets()
	living := nds.isLiving("node1")
	require.False(t, living)

	ok := nds.add(&sync.NodeInform{
		Id: "node1",
	})
	require.True(t, ok)
	living = nds.isLiving("node1")
	require.True(t, living)

	ok = nds.remove("node1")
	require.True(t, ok)

	living = nds.isLiving("node1")
	require.False(t, living)
}

func Test_nodeSets_list(t *testing.T) {
	nds := newNodeSets()
	nds.add(&sync.NodeInform{
		Id: "node1",
	})

	nds.add(&sync.NodeInform{
		Id: "node2",
	})

	nds.add(&sync.NodeInform{
		Id: "node3",
	})

	require.Equal(t, 3, len(nds.listNodes()))
	require.Equal(t, 3, len(nds.listLivingNodes()))

	nds.remove("node1")
	require.Equal(t, 3, len(nds.listNodes()))
	require.Equal(t, 2, len(nds.listLivingNodes()))

	nds.add(&sync.NodeInform{
		Id: "node4",
	})
	require.Equal(t, 4, len(nds.listNodes()))
	require.Equal(t, 3, len(nds.listLivingNodes()))
}
