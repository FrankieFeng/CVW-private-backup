/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package protobuf

import (
	"fmt"

	"github.com/gogo/protobuf/proto"
)

// Serializer protobuf serializer
type Serializer struct {
}

// NewSerializer new protobuf serializer.
func NewSerializer() *Serializer {
	return &Serializer{}
}

// Encode serialize a proto.Message object into a character slice.
func (s *Serializer) Encode(in interface{}) ([]byte, error) {
	obj, ok := in.(proto.Message)
	if !ok {
		return nil, fmt.Errorf("obj is not proto message")
	}
	bz, err := proto.Marshal(obj)
	if err != nil {
		return nil, err
	}
	return bz, nil
}

// Decode deserialize a byte slice into a proto.Message object.
func (s *Serializer) Decode(data []byte, out interface{}) error {
	obj, ok := out.(proto.Message)
	if !ok {
		return fmt.Errorf("obj is not proto message")
	}
	return proto.Unmarshal(data, obj)
}
