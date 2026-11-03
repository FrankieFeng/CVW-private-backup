/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

// Package errors provides a custom error type and related functionality.
package errors

import "strconv"

// ErrCode is a custom error type used to represent error codes
type ErrCode int

const (
	// ErrCodeNon no error.
	ErrCodeNon ErrCode = 0
	// ErrCodeBuildData build data fragment failed.
	ErrCodeBuildData ErrCode = 1
	// errCode the boundary between common errors and terminate errors.
	errCode ErrCode = 10000
	// ErrCodeRuleNotMeet the sync rule is not allowed.
	ErrCodeRuleNotMeet ErrCode = 10001
	// ErrCodeProtoIncompatible the sync proto version is not compatible.
	ErrCodeProtoIncompatible ErrCode = 100002
)

var codeErrors = [...]string{
	ErrCodeBuildData: "build data fragment failed",
}

var terminateErrors = [...]string{
	ErrCodeRuleNotMeet - errCode:       "rule not allowed",
	ErrCodeProtoIncompatible - errCode: "protocol incompatible",
}

// Error returns the string representation of an ErrCode
func (e ErrCode) Error() string {
	if e > errCode {
		terminatedNo := e - errCode
		if 0 <= int(terminatedNo) && int(terminatedNo) < len(terminateErrors) {
			s := terminateErrors[terminatedNo]
			// Return error message if defined
			if s != "" {
				return s
			}
		}
	} else {
		// Check if ErrCode is within range of defined error messages
		if 0 <= int(e) && int(e) < len(codeErrors) {
			s := codeErrors[e]
			// Return error message if defined
			if s != "" {
				return s
			}
		}
	}

	// Return default error message with error code as string
	return "errno " + strconv.Itoa(int(e))
}

// Terminate returns true if the error code caused the connection to terminate.
func (e ErrCode) Terminate() bool {
	return e > errCode
}

// Occurred returns true if the error occurred.
func (e ErrCode) Occurred() bool {
	return e != ErrCodeNon && e != errCode
}
