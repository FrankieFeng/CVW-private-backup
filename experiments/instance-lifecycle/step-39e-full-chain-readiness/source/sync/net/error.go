/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package net

import (
	"errors"

	ierrs "chainmaker.org/chainmaker/sync/v2/internal/errors"
)

var (
	//ErrListenerClosed listener has been closed
	ErrListenerClosed = ierrs.ErrListenerClosed
	//ErrConnClosed use a connection has been closed
	ErrConnClosed = ierrs.ErrConnClosed
	//ErrCloseRepeat close a connection has been closed.
	ErrCloseRepeat = errors.New("connection is already closed")
)
