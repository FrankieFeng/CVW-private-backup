//go:build !go1.18
// +build !go1.18

/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package serialization

import "reflect"

// since go 1.18, reflect.Ptr was changed to reflect.Pointer
const (
	reflectKindPointer reflect.Kind = reflect.Ptr
)
