/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package serialization

import (
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
)

// Normalize the block data according to the standardized definition of storage.
// The entire data storage process is based on normalized data.
// The normalization process splits and serializes the data,
// so only the normalizer knows how to serialize and deserialize the data.
// Then, we need to organize and store the normalized data into the log file,
// so the organizer of the normalized data knows how the data is listed,
// and it will generate index information for the listed data.

// BlockNormalizer Organize blocks into a standard format for storage definition,
// and subsequent processes operate based on this format.
// It splits block data and serializes and deserializes the split data.
type BlockNormalizer interface {
	// NormalizeBlock Organize blocks into a standard format for storage definition.
	NormalizeBlock(blockWithRWSet *storePb.BlockWithRWSet) (*BlockNormalized, error)
	// NormalizeFromSerialization restore normalized data from serialized data
	NormalizeFromSerialization(*SerializationNormalized) (*BlockNormalized, error) //
	// Serializer get the serializer used by BlockNormalizer,
	// so that users can deserialize the character data in BlockNormalized.
	Serializer() Serializer
}

// Serializer serializes and deserializes Objects
type Serializer interface {
	Encode(interface{}) ([]byte, error)
	Decode([]byte, interface{}) error
}
