/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package bloom

import (
	"testing"

	"chainmaker.org/chainmaker/protocol/v2"
)

func TestLogger(t *testing.T) {
	var logger protocol.Logger = newLogger()
	logger.Info("test%d", 1)
	logger.Infof("test%d", 1)
	logger.Debug("test%d", 1)
	logger.Debugf("test%d", 1)
	logger.Warn("test%d", 1)
	logger.Warnf("test%d", 1)
	// logger.Error("test%d", 1)
	// logger.Errorf("test%d", 1)
	// logger.Panic("testaa%d", 1)
	logger.Debugw("test", "aa", struct {
		c int
	}{
		c: 10,
	}, "22", 33)
	// logger.Panicw("test", "aa", struct {
	// 	c int
	// }{
	// 	c: 10,
	// }, "22", 33)
}
