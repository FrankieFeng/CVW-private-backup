/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// Package setting provides the settings for the data synchronization.
package setting

// ID is a uint16 type, which is used to identify the setting type.
type ID uint16

const (
	// IDSyncMode indicate the mode of the data synchronization.
	// [0...20]reserved for system
	IDSyncMode ID = iota + 20
	//IdSyncSettingInitWindow indicate the initialization window size for the push stream.
	IdSyncSettingInitWindow
	// IDSyncWithRWSet indicate whether to send data with read-write set.
	IDSyncWithRWSet
)

// Setting is a struct that contains the ID and value of the setting.
// ID is the identifier of the setting.
// Val is the value of the setting, which is a uint64 type.
type Setting struct {
	ID  ID
	Val uint64
}

// UserSetting represents setting data for user logic.
type UserSetting struct {
	// ModeData is the mode of the data synchronization.
	ModeData SyncModeData
	// WithRWSet indicates whether to send data with read-write set.
	WithRWSet bool
	// WindowSize is the initialization window size for the push stream.
	WindowSize int
}

// Update updates the UserSetting with the given settings.
func (set *UserSetting) Update(settings ...Setting) {
	for _, s := range settings {
		switch s.ID {
		case IDSyncMode:
			set.ModeData = SyncModeData(s.Val)
		case IDSyncWithRWSet:
			set.WithRWSet = s.Val == 1
		case IdSyncSettingInitWindow:
			set.WindowSize = int(s.Val)
		}
	}
}
