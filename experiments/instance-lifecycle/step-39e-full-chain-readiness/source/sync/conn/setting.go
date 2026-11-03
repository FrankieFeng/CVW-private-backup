/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"container/list"
	"sync"

	sp "chainmaker.org/chainmaker/sync/v2/setting"
)

const (
	//idSyncSettingVersion indicate the value is setting version number
	idSyncSettingVersion sp.ID = iota + 1
	//idSyncSettingBlockHeight indicate which block height does the setting take effect at.
	idSyncSettingBlockHeight
)

type settingList struct {
	sync.Mutex
	list *list.List
}

func newSettingList() *settingList {
	return &settingList{
		list: list.New(),
	}
}

// Push item to the list and sort by block height.
func (l *settingList) Push(new *setting) {
	l.Lock()
	defer l.Unlock()
	ele := l.list.Back()
	for ele != nil {
		s, _ := ele.Value.(*setting)
		if s.blockHeight < new.blockHeight {
			break
		}
		back := ele
		ele = ele.Prev()
		if s.version <= new.version {
			l.list.Remove(back)
		}
	}
	if ele == nil {
		l.list.PushFront(new)
		return
	}
	l.list.InsertAfter(new, ele)
}

// Front get the first setting in the list, not removing it from the list.
func (l *settingList) Front() *settingLinker {
	l.Lock()
	defer l.Unlock()
	return settingLinkOf(l.list.Front())
}

func settingLinkOf(ele *list.Element) *settingLinker {
	if ele == nil {
		return nil
	}
	return &settingLinker{
		setting: ele.Value.(*setting),
		ele:     ele,
	}
}

// Back get the last setting in the list,not removing it from the list.
func (l *settingList) Back() *settingLinker {
	l.Lock()
	defer l.Unlock()
	return settingLinkOf(l.list.Back())
}

// Pop get the first setting in the list and remove it from the list.
// func (l *settingList) Pop() *settingLinker {
// 	l.Lock()
// 	defer l.Unlock()
// 	ele := l.list.Front()
// 	if ele == nil {
// 		return nil
// 	}
// 	v := l.list.Remove(ele)
// 	return &settingLinker{
// 		setting: v.(*setting),
// 		ele:     ele,
// 	}
// }

// Remove the element from the list.
func (l *settingList) Remove(s *settingLinker) {
	l.Lock()
	defer l.Unlock()
	l.list.Remove(s.ele)
}

// GetByHeight get a element according to the incoming height 'h'
// is within the effective range of the setting.
// If not found, return nil.
func (l *settingList) GetByHeight(h uint64) *settingLinker {
	l.Lock()
	defer l.Unlock()
	setlink := settingLinkOf(l.list.Front())
	if setlink == nil {
		return nil
	}

	if setlink.Setting().blockHeight > h {
		return nil
	}
	for next := setlink.Next(); next != nil; next = setlink.Next() {
		if next.Setting().blockHeight > h {
			break
		}
		setlink = next
	}
	return setlink
}

type settingLinker struct {
	*setting
	ele *list.Element
}

type setting struct {
	version     uint32
	blockHeight uint64
	sp.UserSetting
}

// Clone generates a new setting instance based on the set.
func (set *setting) Clone() *setting {
	ins := *set
	return &ins
}

// update update the setting.
func (set *setting) update(settings []syncSetting) {
	for _, s := range settings {
		switch s.ID {
		case idSyncSettingVersion:
			set.version = uint32(s.Val)
		case idSyncSettingBlockHeight:
			set.blockHeight = s.Val
		default:
			set.UserSetting.Update(sp.Setting{ID: s.ID, Val: s.Val})
		}
	}
}

// Setting obtain the setting in the settingLinker.
func (s *settingLinker) Setting() *setting {
	if s == nil {
		return nil
	}
	// return s.ele.Value.(*setting)
	return s.setting
}

// Next get next element of current element, if not exist return nil.
func (s *settingLinker) Next() *settingLinker {
	if s == nil || s.ele == nil {
		return nil
	}
	next := s.ele.Next()
	if next == nil {
		return nil
	}
	return &settingLinker{
		setting: next.Value.(*setting),
		ele:     next,
	}
}

// Prev get previous element of the current element, if not exist return nil.
func (s *settingLinker) Prev() *settingLinker {
	if s == nil || s.ele == nil {
		return nil
	}
	prev := s.ele.Prev()
	if prev == nil {
		return nil
	}
	return &settingLinker{
		setting: prev.Value.(*setting),
		ele:     prev,
	}
}

// genSetting convert list of setting to struct.
func genSetting(settings []syncSetting) *setting {
	set := &setting{}
	set.update(settings)
	return set
}
