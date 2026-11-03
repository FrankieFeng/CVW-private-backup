/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package receptor

import (
	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"github.com/gogo/protobuf/proto"
)

// bytesToSliceData converts a byte slice to a SliceData.
func bytesToSliceData(bytes []byte) (*syncPb.SliceData, error) {
	data := new(syncPb.SliceData)
	// Unmarshal the byte slice into the SliceData structure.
	if err := proto.Unmarshal(bytes, data); err != nil {
		return nil, err
	}
	return data, nil
}
