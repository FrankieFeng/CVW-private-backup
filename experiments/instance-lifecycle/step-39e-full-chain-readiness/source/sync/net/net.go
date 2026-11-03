/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package net

import (
	"fmt"
	"strings"
	"sync/atomic"
	"time"

	"chainmaker.org/chainmaker/sync/v2/internal/rand"
)

var (
	//connSN connection serial number
	connSN             uint64
	heartBeatInterval  = 5 * time.Second
	heartBeatMissCount = 3
	//magic number is used to identify the message can be processed by themselves
	magicB = [2]byte{0xfe, 0xef}
	// MsgBusLocalNodeID message bus local node id.
	MsgBusLocalNodeID string
)

const (
	typeDial    uint8 = 1
	typeDialAck uint8 = 2
	typeClose   uint8 = 3
	typePing    uint8 = 4
	typePong    uint8 = 5
	typeReset   uint8 = 6
	typeData    uint8 = 7
)

// #nosec G404
func init() {
	connSN = rand.Uint64()
}

const (
	dialAckLen  = 4               // number of bytes in dialAckBytes
	dialMaxWait = 5 * time.Second //the wait time for dial ack message.
)

// func getConnMessageDispatcher(transport Transport) *connMessageDispatcher {
// 	dispatcherMu.Lock()
// 	if msgBusConnDispatchers == nil {
// 		msgBusConnDispatchers = make(map[Transport]*connMessageDispatcher)
// 	}
// 	dispatcher, exist := msgBusConnDispatchers[transport]
// 	if !exist {
// 		dispatcher = newConnMessageDispatcher(transport, types.MT_Conn)
// 		dispatcher.tag = "conn_msg dispatch"
// 		msgBusConnDispatchers[transport] = dispatcher
// 	}
// 	dispatcherMu.Unlock()
// 	return dispatcher
// }

// func initConnDispatcher(transport Transport) {
// 	once.Do(func() {
// 		msgBusConnMessageDispatcher = newConnMessageDispatcher(transport, types.MT_Conn)
// 	})
// }

func increaseSN() uint64 {
	return atomic.AddUint64(&connSN, 1)
}

func genConnID(nodeID string, id uint64) string {
	return fmt.Sprintf("%s#%d", nodeID, id)
}

func resolveConnID(connID string) (string, uint64) {
	idx := strings.Index(connID, "#")
	return connID[:idx], stringToUint64(connID[idx+1:])
}

func stringToUint64(in string) uint64 {
	var (
		ret uint64
	)
	for _, b := range in {
		ret *= 10
		ret += uint64(b - '0')
	}
	return ret
}

func bytesToUint64(in []byte) uint64 {
	var (
		ret uint64
	)
	for _, b := range in {
		ret = ret << 8
		ret |= uint64(b)
	}
	return ret
}
