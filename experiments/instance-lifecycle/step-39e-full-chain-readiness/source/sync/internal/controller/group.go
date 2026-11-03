/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

// Package controller provides a way to manage the lifecycle of goroutines.
package controller

import (
	"fmt"
	"sync"
)

// GoRoutineGroup a group of goroutines controller the lifecycle.
type GoRoutineGroup struct {
	wg sync.WaitGroup
}

// NewGoRoutineGroup new goroutine group
func NewGoRoutineGroup() *GoRoutineGroup {
	return new(GoRoutineGroup)
}

// Run run a goroutine
func (g *GoRoutineGroup) Run(fn func()) {
	g.wg.Add(1)
	go func() {
		defer g.wg.Done()
		fn()
	}()
}

// RunSafety run a goroutine with recovery.
func (g *GoRoutineGroup) RunSafety(fn func()) {
	g.wg.Add(1)
	go RunSafe(func() {
		defer g.wg.Done()
		fn()
	})
}

// Wait wait all goroutines exit.
func (g *GoRoutineGroup) Wait() {
	g.wg.Wait()
}

// RunSafe exec the function fn with recovery.
func RunSafe(fn func()) {
	defer func() {
		if p := recover(); p != nil {
			fmt.Println("RunSafe panic: ", p)
		}
	}()

	fn()
}
