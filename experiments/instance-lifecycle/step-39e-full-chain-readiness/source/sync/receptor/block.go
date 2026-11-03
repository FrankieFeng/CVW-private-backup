/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import "chainmaker.org/chainmaker/pb-go/v2/store"

// Block implements the BlockReveal interface.
type Block struct {
	*store.BlockWithRWSet
	fromNode string
	endPool  *endpointPool
}

func newBlock(fromNode string, block *store.BlockWithRWSet, endPool *endpointPool) *Block {
	return &Block{
		BlockWithRWSet: block,
		fromNode:       fromNode,
		endPool:        endPool,
	}
}

// GetBlockWithRWSet get block info with rwset.
func (b *Block) GetBlockWithRWSet() *store.BlockWithRWSet {
	return b.BlockWithRWSet
}

// ReportVerifyResult report verification results of the block.
func (b *Block) ReportVerifyResult(success bool) {
	if !success && b.fromNode != "" {
		if end := b.endPool.GetEndpoint(b.fromNode); end != nil {
			end.FailFor(b.GetBlock().GetHeader().GetBlockHeight(), metricTypeVerify)
		}
	}
}
