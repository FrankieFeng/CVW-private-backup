/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package types

import (
	"testing"

	"github.com/test-go/testify/require"
)

func TestVersion(t *testing.T) {
	require.Equal(t, "v1.0", ParseVersion(Version))

	v1 := uint8(1)
	v2 := uint8(2)
	v3 := uint8(17)
	v4 := uint8(254)
	v5 := uint8(255)

	require.Equal(t, "v0.1", ParseVersion(v1))
	require.Equal(t, "v0.2", ParseVersion(v2))
	require.Equal(t, "v1.1", ParseVersion(v3))
	require.Equal(t, "v15.14", ParseVersion(v4))
	require.Equal(t, "v15.15", ParseVersion(v5))
}
