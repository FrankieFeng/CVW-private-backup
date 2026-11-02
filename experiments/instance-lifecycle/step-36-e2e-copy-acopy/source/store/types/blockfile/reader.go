/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package blockfile

import (
	"os"

	"chainmaker.org/chainmaker/store/v2/utils"
)

// FileReader block file db file reader interface
type FileReader interface {
	//Read file read
	Read(b []byte) (int, error)
	//ReadAt read file at off
	ReadAt(b []byte, off int64) (int, error)
	//Seek
	Seek(offset int64, whence int) (int64, error)
	//Size the size of the file
	Size() (int64, error)
	//Lock lock file
	Lock() error
	//Unlock unlock file
	Unlock() error
	//Close
	Close() error
}

// OpenFile encapsulates os.OpenFile and returns a custom File
func OpenFile(name string, flag int, perm os.FileMode) (*File, error) {
	fi, err := os.OpenFile(name, flag, perm)
	if err != nil {
		return nil, err
	}
	return &File{fi}, nil
}

// File encapsulates os.File and implements the FileReader interface
type File struct {
	*os.File
}

// Lock file
func (f *File) Lock() error {
	return utils.FileLocker(f.File)
}

// Unlock file
func (f *File) Unlock() error {
	return utils.FileUnLocker(f.File)
}

// Size returns the size of the file
func (f *File) Size() (int64, error) {
	info, err := f.Stat()
	if err != nil {
		return 0, err
	}
	return info.Size(), err
}
