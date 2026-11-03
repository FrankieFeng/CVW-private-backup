/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// Package rand provides functionality for generating random numbers.
package rand

import (
	"crypto/rand"
	"encoding/binary"
	"fmt"
	"math/big"
	mrand "math/rand"

	"time"
)

func init() {
	mrand.Seed(time.Now().UnixNano())
}

// Uint32 returns a pseudo-random 32-bit value as a uint32.
func Uint32() uint32 {
	bytes := [4]byte{}
	if _, err := rand.Read(bytes[:]); err != nil {
		fmt.Printf("rand Uint32 error: %v\n", err)
		return 0
	}
	return binary.BigEndian.Uint32(bytes[:])
}

// Uint64 returns a pseudo-random 64-bit value as a uint64.
func Uint64() uint64 {
	bytes := [8]byte{}
	if _, err := rand.Read(bytes[:]); err != nil {
		fmt.Printf("rand Uint64 error: %v\n", err)
		return 0
	}
	return binary.BigEndian.Uint64(bytes[:])
}

// Read generates len(out) random bytes and writes them into out.
func Read(out []byte) (int, error) {
	return rand.Read(out)
}

// Intn returns, as an int, a non-negative pseudo-random number in the half-open interval [0,n).
func Intn(n int) int {
	v, err := rand.Int(rand.Reader, big.NewInt(int64(n)))
	if err != nil {
		fmt.Printf("rand Intn error: %v\n", err)
		return 0
	}
	return int(v.Int64())
}
