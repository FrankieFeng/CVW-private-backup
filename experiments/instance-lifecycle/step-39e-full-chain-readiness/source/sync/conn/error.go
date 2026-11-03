/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"errors"

	ierrs "chainmaker.org/chainmaker/sync/v2/internal/errors"
)

var (
	//ErrPushStreamAlreadyOpen there is already a stream opened.
	ErrPushStreamAlreadyOpen = errors.New("push stream is already open")
	//errBadValue received an incorrect push setting value.
	errBadValue = errors.New("bad value")
	//errIllegalMessage received messages that should not have been received.
	errIllegalMessage = errors.New("message is illegal")
	// ErrConnAlreadyServe occurs when the function 'Serve' of server connection is called repeatedly.
	ErrConnAlreadyServe = errors.New("server conn is already served")
	//ErrBlockHandlerNil occurs when the block handler passed to the server connection is null
	ErrBlockHandlerNil = errors.New("block handler cannot be nil")
	errCloseRemote     = errors.New("connection closed by remote")
	//ErrConnClosed occurs when send message by a closed connection.
	ErrConnClosed = ierrs.ErrConnClosed
	//ErrBadConnState occurs when the state of the connection exceeds the expected.
	//I think this error will never happen.
	ErrBadConnState = errors.New("bad connection state")
	//errUnexpectedMessage occurs when the received message does not match the current state.
	errUnexpectedMessage = errors.New("unexpected message")
	//errAlreadyExists something already exists
	errAlreadyExists  = errors.New("already exists")
	errSyncProtoWrong = errors.New("sync protocol wrong")
)
