/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package receptor

import (
	"fmt"
	"testing"

	"github.com/test-go/testify/require"
)

func TestMetricStat_Score(t *testing.T) {
	ms := NewMetricStat()
	ms.Bad(1, metricTypeVerify)
	ms.Bad(30, metricTypeVerify)
	score := ms.Score(35)
	require.Equal(t, 0, score)
	score = ms.Score(55)
	fmt.Println(score)
	require.NotEqual(t, 0, score)
}
