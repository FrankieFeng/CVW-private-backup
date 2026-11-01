/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package indexer

import (
	"reflect"

	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/store/v2/serialization"
)

var _ serialization.Serializer = (*indexerCodec)(nil)

// indexerCodec is a serializer based on native codec provided by indexer.
// Because indexer organizes and serializes complete blocks in its own way,
// that is: a certain sub-object/type of sub-objects in BlockWithRWSet object are serialized separately
// using native codec, and then a complete serialized object is formed.
// Therefore, the native codec can only deserialize sub-serialized objects,
// but not the serialized object of the entire BlockWithRWSet.
// indexerCodec is to solve this problem and add support for the serialization method of BlockWithRWSet objects.
type indexerCodec struct {
	indexer *NormalBlockFileIndexer
}

func newIndexerCodec(indexer *NormalBlockFileIndexer) *indexerCodec {
	return &indexerCodec{
		indexer: indexer,
	}
}

// Encode if the encoded object is BlockWithRWSet, BlockSerializer will be used to serialize the Block,
// otherwise the native serialization method will be used.
// Currently only a simple judgment is made, please pay attention to the use.
func (c *indexerCodec) Encode(in interface{}) ([]byte, error) {
	switch obj := in.(type) {
	case *storePb.BlockWithRWSet:
		_, bz, _, err := c.indexer.indexFor(obj)
		if err != nil {
			return nil, err
		}
		return bz, err
	case storePb.BlockWithRWSet:
		_, bz, _, err := c.indexer.indexFor(&obj)
		if err != nil {
			return nil, err
		}
		return bz, err
	default:
		bz, err := c.indexer.BlockNormalizer().Serializer().Encode(obj)
		if err != nil {
			return nil, err
		}
		return c.indexer.assembler.Plate(bz)
	}
}

// Decode if the decoded object is BlockWithRWSet, BlockSerializer will be used to deserialize the Block,
// otherwise the native deserialization method will be used.
// Currently only a simple judgment is made, please pay attention to the use
func (c *indexerCodec) Decode(bz []byte, out interface{}) error {
	switch obj := out.(type) {
	case *storePb.BlockWithRWSet:
		block, err := c.indexer.recoveryBlockFromBytes(bz)
		if err != nil {
			return err
		}
		reflect.ValueOf(obj).Elem().Set(reflect.ValueOf(*block))
	case **storePb.BlockWithRWSet:
		block, err := c.indexer.recoveryBlockFromBytes(bz)
		if err != nil {
			return err
		}
		reflect.ValueOf(obj).Elem().Set(reflect.ValueOf(block))
	default:
		rbz, err := c.indexer.assembler.Deplate(bz)
		if err != nil {
			return err
		}
		return c.indexer.BlockNormalizer().Serializer().Decode(rbz, obj)
	}
	return nil
}
