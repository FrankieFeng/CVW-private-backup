/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

type connState uint8

const (
	//stateInit init state
	stateInit connState = iota
	//stateSyncSend a sync request has been sent
	stateSyncSend
	//stateSyncReceive a sync request has been received
	stateSyncReceive
	// //stateEstablish a connection has been established
	// stateEstablished

	//stateOpen a connection has been opened for working
	stateOpen
	//stateClose a connection has been closed
	stateClose
	//stateHalfCloseLocal a connection just been closed by the local
	stateHalfCloseLocal
	//stateHalfCloseRemote a connection just been closed by the remote
	stateHalfCloseRemote
)

// String output the state name.
func (s connState) String() string {
	switch s {
	case stateInit:
		return "init_state"
	case stateSyncSend:
		return "sync_send_state"
	case stateSyncReceive:
		return "sync_received_state"
	case stateOpen:
		return "open_state"
	case stateClose:
		return "closed_state"
	case stateHalfCloseLocal:
		return "local_close_state"
	case stateHalfCloseRemote:
		return "remote_close_state"
	}
	return "unknown"
}
