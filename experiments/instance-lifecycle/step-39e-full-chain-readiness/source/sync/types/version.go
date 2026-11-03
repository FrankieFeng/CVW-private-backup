/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package types

import "fmt"

const (
	// Version 同步协议版本号
	Version = uint8(16)
)

// ParseVersion 版本号解析
// 版本号：uint8 8个字节
// 前四个字节为大版本，后四个字节为小版本号
// 例如： v1.0版本：0001 0000 => 16
func ParseVersion(v uint8) string {
	h := v >> 4
	l := v << 4 >> 4
	return fmt.Sprintf("v%d.%d", h, l)
}
