/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */
package encrypt

import (
	"encoding/binary"
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"
	"time"

	"chainmaker.org/chainmaker/common/v2/wal"
	"chainmaker.org/chainmaker/protocol/v2/test"
	td "chainmaker.org/chainmaker/store/v2/test"
	tbf "chainmaker.org/chainmaker/store/v2/types/blockfile"
	"github.com/stretchr/testify/assert"
)

const walPath = "./wal"

func initWalFiles(walPath string, fileCount int, blocksPerFile int) (*wal.Log, error) {
	// walPath := "./wal"
	opts := wal.DefaultOptions
	blockSize := len(td.MockBlk)
	opts.SegmentSize = blocksPerFile * blockSize
	totalBlocks := fileCount * blocksPerFile
	log, err := wal.Open(walPath, opts)
	if err != nil {
		return nil, err
	}
	for i := 1; i <= totalBlocks; i++ {
		if err := log.Write(uint64(i), td.MockBlk); err != nil {
			return nil, err
		}
	}
	return log, nil
}

func initTestWalEncryptManager(walPath string) *WalEncryptManager {
	m, err := NewWalEncryptManager(walPath,
		buildEncryptor("aes", "1234567890123456"), &test.GoLogger{})
	if err != nil {
		panic(err)
	}
	return m
}

// uint32(crc32)+len(data)+data
func getRawBytesFromWalBytes(walBytes []byte) [][]byte {
	var rawBytes [][]byte
	for len(walBytes) > 0 {
		walBytes = walBytes[4:]
		size, n := binary.Uvarint(walBytes)
		if size > uint64(len(walBytes)-n) {
			size = uint64(len(walBytes) - n)
		}
		rawBytes = append(rawBytes, walBytes[n:n+int(size)])
		walBytes = walBytes[n+int(size):]
	}
	return rawBytes
}

func TestWalEncryptManager_EncryptAndRead(t *testing.T) {
	_ = os.MkdirAll(walPath, 0600)
	defer os.RemoveAll(walPath)
	m := initTestWalEncryptManager(walPath)
	_, err := initWalFiles(walPath, 10, 2)
	if err != nil {
		panic(err)
	}
	type args struct {
		segment string
	}
	tests := []struct {
		name    string
		fields  *WalEncryptManager
		args    args
		wantErr bool
	}{
		// TODO: Add test cases.
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(1),
			},
			wantErr: false,
		},
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(3),
			},
			wantErr: false,
		},
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(5),
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mgr := tt.fields
			mgr.EncryptAsync(tt.args.segment)
		})
	}
	for {
		if m.fileIndexEncrypted == 5 {
			break
		}
		time.Sleep(time.Second)
	}
	t.Logf("%d", m.fileIndexEncrypted)
	bytes, err := m.Read(walNamingCoverter{}.IndexToName(5))
	assert.Nil(t, err)
	rawBytes := getRawBytesFromWalBytes(bytes)
	assert.Equal(t, td.MockBlk, rawBytes[0])

	bytes, err = m.Read(walNamingCoverter{}.IndexToName(7))
	assert.Nil(t, err)
	rawBytes = getRawBytesFromWalBytes(bytes)
	assert.Equal(t, td.MockBlk, rawBytes[0])

	//非解密形式读取文件，数据不相等
	f, err := tbf.OpenFile(filepath.Join(walPath, walNamingCoverter{}.IndexToName(5)), os.O_RDONLY, 0)
	assert.Nil(t, err)
	bytes, err = ioutil.ReadAll(f)
	assert.Nil(t, err)
	rawBytes = getRawBytesFromWalBytes(bytes)
	assert.NotEqual(t, td.MockBlk, rawBytes[0])
	f.Close()
	//00000000000000000007 为非加密文件，可以以普通形式打开
	f, err = tbf.OpenFile(filepath.Join(walPath, walNamingCoverter{}.IndexToName(7)), os.O_RDONLY, 0)
	assert.Nil(t, err)
	bytes, err = ioutil.ReadAll(f)
	assert.Nil(t, err)
	rawBytes = getRawBytesFromWalBytes(bytes)
	assert.Equal(t, td.MockBlk, rawBytes[0])
	f.Close()
}

func TestWalEncryptManager_TruncateFront(t *testing.T) {
	_ = os.MkdirAll(walPath, 0600)
	defer os.RemoveAll(walPath)
	m := initTestWalEncryptManager(walPath)
	_, err := initWalFiles(walPath, 10, 2)
	if err != nil {
		panic(err)
	}
	type args struct {
		segment string
	}
	tests := []struct {
		name    string
		fields  *WalEncryptManager
		args    args
		wantErr bool
	}{
		// TODO: Add test cases.
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(1),
			},
			wantErr: false,
		},
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(3),
			},
			wantErr: false,
		},
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(5),
			},
			wantErr: false,
		},
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(7),
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mgr := tt.fields
			mgr.EncryptAsync(tt.args.segment)
		})
	}
	for {
		if m.fileIndexEncrypted == 7 {
			break
		}
		time.Sleep(time.Second)
	}
	t.Logf("%d", m.fileIndexEncrypted)
	//将5读出来
	bytes, err := m.Read(walNamingCoverter{}.IndexToName(5))
	assert.Nil(t, err)
	os.Remove(filepath.Join(walPath, walNamingCoverter{}.IndexToName(5)))
	//将5写入明文
	err = ioutil.WriteFile(filepath.Join(walPath, walNamingCoverter{}.IndexToName(5)), bytes, 0600)
	assert.Nil(t, err)
	//检测确实是明文
	f, err := tbf.OpenFile(filepath.Join(walPath, walNamingCoverter{}.IndexToName(5)), os.O_RDONLY, 0)
	assert.Nil(t, err)
	bytes, err = ioutil.ReadAll(f)
	assert.Nil(t, err)
	rawBytes := getRawBytesFromWalBytes(bytes)
	assert.Equal(t, td.MockBlk, rawBytes[0])
	f.Close()

	//告知walEncryptManager删除5之前的文件,这样可以对5重新加密
	_ = m.TruncateFront(5)
	assert.Equal(t, uint64(5), m.truncateBeforeIndex)
	//重新加密5
	m.EncryptAsync(walNamingCoverter{}.IndexToName(5))
	//等加密完成
	for {
		if m.truncateBeforeIndex == 0 {
			break
		}
		time.Sleep(time.Second)
	}
	assert.GreaterOrEqual(t, uint64(7), m.fileIndexEncrypted)
	//检测确实重新加密过
	bytes, err = m.Read(walNamingCoverter{}.IndexToName(5))
	assert.Nil(t, err)
	rawBytes = getRawBytesFromWalBytes(bytes)
	assert.Equal(t, td.MockBlk, rawBytes[0])
}

func TestWalEncryptManager_TruncateAfter(t *testing.T) {
	_ = os.MkdirAll(walPath, 0600)
	defer os.RemoveAll(walPath)
	m := initTestWalEncryptManager(walPath)
	_, err := initWalFiles(walPath, 20, 2)
	if err != nil {
		panic(err)
	}
	type args struct {
		segment string
	}
	tests := []struct {
		name    string
		fields  *WalEncryptManager
		args    args
		wantErr bool
	}{
		// TODO: Add test cases.
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(1),
			},
			wantErr: false,
		},
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(3),
			},
			wantErr: false,
		},
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(5),
			},
			wantErr: false,
		},
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: walNamingCoverter{}.IndexToName(7),
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mgr := tt.fields
			mgr.EncryptAsync(tt.args.segment)
		})
	}
	for {
		if m.fileIndexEncrypted == 7 {
			break
		}
		time.Sleep(time.Second)
	}
	//lock阻塞goroutine加密流程
	m.mu.Lock()
	for i := 9; i < 20; i += 2 {
		m.EncryptAsync(walNamingCoverter{}.IndexToName(uint64(i)))
	}
	err = m.TruncateBack(13)
	assert.Nil(t, err)
	m.mu.Unlock()
	for {
		if m.fileIndexEncrypted == 11 {
			break
		}
		time.Sleep(time.Second)
	}
	t.Logf("%d", m.fileIndexEncrypted)
	//此时13及之后的为明文
	f, err := tbf.OpenFile(filepath.Join(walPath, walNamingCoverter{}.IndexToName(13)), os.O_RDONLY, 0)
	assert.Nil(t, err)
	bytes, err := ioutil.ReadAll(f)
	assert.Nil(t, err)
	rawBytes := getRawBytesFromWalBytes(bytes)
	assert.Equal(t, td.MockBlk, rawBytes[0])
	f.Close()
	//11不为密文
	f, err = tbf.OpenFile(filepath.Join(walPath, walNamingCoverter{}.IndexToName(11)), os.O_RDONLY, 0)
	assert.Nil(t, err)
	bytes, err = ioutil.ReadAll(f)
	assert.Nil(t, err)
	rawBytes = getRawBytesFromWalBytes(bytes)
	assert.NotEqual(t, td.MockBlk, rawBytes[0])
	f.Close()

	assert.GreaterOrEqual(t, uint64(11), m.fileIndexEncrypted)
	//检测确实重新加密过
	bytes, err = m.Read(walNamingCoverter{}.IndexToName(11))
	assert.Nil(t, err)
	rawBytes = getRawBytesFromWalBytes(bytes)
	assert.Equal(t, td.MockBlk, rawBytes[0])
}
