/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package errors

import "errors"

var (
	//ErrConnClosed use a connection has been closed
	ErrConnClosed = errors.New("connection closed")
	//ErrListenerClosed listener has been closed
	ErrListenerClosed = errors.New("listener closed")
	//ErrPushEOF occurs at the end of this push processing
	ErrPushEOF = errors.New("PUSH EOF")
)
