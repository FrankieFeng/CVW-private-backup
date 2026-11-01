/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package slru

import (
	"container/list"
)

// cachedList is a wrapper of container/list.List.
// It keeps unused elements in the hope that it can be reused.
type cachedList struct {
	*list.List
	// delimitation used to separate used and unused elements.
	delimitation *list.Element
	count        int
}

// newCachedList returns a new cachedList.
func newCachedList() *cachedList {
	list := list.New()
	return &cachedList{
		List:         list,
		delimitation: list.PushBack(0),
	}
}

// PushBack adds an element to the back of the list.
func (l *cachedList) PushBack(v interface{}) *list.Element {
	return l.push(v, false)
}

// PushFront adds an element to the front of the list.
func (l *cachedList) PushFront(v interface{}) *list.Element {
	return l.push(v, true)
}

// Remove removes an element from the list.
func (l *cachedList) Remove(ele *list.Element) interface{} {
	v := ele.Value
	l.List.MoveToBack(ele)
	ele.Value = nil
	l.count--
	return v
}

// Front returns the first element of the list.
func (l *cachedList) Front() *list.Element {
	if l.count == 0 {
		return nil
	}
	return l.List.Front()
}

// Back returns the last element of the list.
func (l *cachedList) Back() *list.Element {
	if l.count == 0 {
		return nil
	}
	return l.delimitation.Prev()
}

// Len returns the number of elements in the list.
func (l *cachedList) Len() int {
	return l.count
}

// push adds an element to list.
// If there are unused elements which at the back of the list but is not delimitation, it will be reused and
// moved to the front of the list if front is true, otherwise it will be moved to the before of
// the delimitation.
func (l *cachedList) push(v interface{}, front bool) *list.Element {
	ele := l.List.Back()
	if l.delimitation == ele {
		if front {
			ele = l.List.PushFront(v)
		} else {
			ele = l.List.InsertBefore(v, l.delimitation)
		}
	} else {
		ele.Value = v
		if front {
			l.List.MoveToFront(ele)
		} else {
			l.List.MoveBefore(ele, l.delimitation)
		}
	}
	l.count++
	return ele
}
