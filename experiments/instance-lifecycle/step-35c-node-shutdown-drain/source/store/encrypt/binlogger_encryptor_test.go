/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package encrypt

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"chainmaker.org/chainmaker/common/v2/crypto"
	"chainmaker.org/chainmaker/common/v2/crypto/sym/aes"
	"chainmaker.org/chainmaker/common/v2/crypto/sym/sm4"
	"chainmaker.org/chainmaker/protocol/v2/test"
	td "chainmaker.org/chainmaker/store/v2/test"
	tbf "chainmaker.org/chainmaker/store/v2/types/blockfile"
	"github.com/stretchr/testify/assert"
)

var (
	binlogPath = "./binlogg"
)

func buildEncryptor(encryptor, key string) crypto.SymmetricKey {
	switch strings.ToLower(encryptor) {
	case "sm4":
		return &sm4.SM4Key{Key: []byte(key)}
	default:
		return &aes.AESKey{Key: []byte(key)}
	}
}

func initTestBinloggerEncryptManager() *BinloggerEncryptManager {
	m, err := NewBinloggerEncryptManager(binlogPath,
		buildEncryptor("aes", "1234567890123456"), &test.GoLogger{})
	if err != nil {
		panic(err)
	}
	return m
}

type mockBinLogger struct {
	path        string
	segmentSize int
	fileWrite   *os.File
	sizeWriten  int
	index       uint64
	coverter    blockFileNamingCoverter
}

func newMockBinLogger(path string, segmentSize int) *mockBinLogger {
	return &mockBinLogger{
		path:        path,
		segmentSize: segmentSize,
		coverter:    blockFileNamingCoverter{},
	}
}

func (m *mockBinLogger) Write(index uint64, data []byte) (fileName string, offset, blkLen uint64, err error) {
	if m.fileWrite == nil || m.sizeWriten >= m.segmentSize {
		if err = m.cycle(); err != nil {
			return "", 0, 0, err
		}
		m.sizeWriten = 0
	}
	n, err := m.fileWrite.Write(data)
	if err != nil {
		return "", 0, 0, err
	}
	m.index = index
	m.sizeWriten += n
	return m.fileWrite.Name(), uint64(n - len(data)), uint64(n), nil
}

func (m *mockBinLogger) newFile() error {
	segName := m.coverter.IndexToName(m.index + 1)
	f, err := os.OpenFile(filepath.Join(m.path, segName), os.O_RDWR|os.O_CREATE, 0600)
	if err != nil {
		return err
	}
	m.fileWrite = f
	return nil
}

func (m *mockBinLogger) cycle() error {
	if m.fileWrite == nil {
		return m.newFile()
	}
	if err := m.fileWrite.Sync(); err != nil {
		return err
	}
	if err := m.fileWrite.Close(); err != nil {
		return err
	}
	return m.newFile()
}

func initFiles(path string, fileCount int, blocksPerFile int) error {
	blockSize := len(td.MockBlk)
	fileSize := blocksPerFile * blockSize
	totalBlocks := fileCount * blocksPerFile
	blog := newMockBinLogger(path, fileSize)
	for i := 1; i <= totalBlocks; i++ {
		if _, _, _, err := blog.Write(uint64(i), td.MockBlk); err != nil {
			return err
		}
	}
	return nil
}

func TestBinloggerEncryptManager_EncryptAndRead(t *testing.T) {
	_ = os.MkdirAll(binlogPath, 0600)
	defer os.RemoveAll(binlogPath)
	m := initTestBinloggerEncryptManager()
	err := initFiles(binlogPath, 10, 2)
	if err != nil {
		panic(err)
	}
	type args struct {
		segment string
	}
	tests := []struct {
		name    string
		fields  *BinloggerEncryptManager
		args    args
		wantErr bool
	}{
		// TODO: Add test cases.
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: "00000000000000000001.fdb",
			},
			wantErr: false,
		},
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: "00000000000000000003.fdb",
			},
			wantErr: false,
		},
		{
			name:   "encrypt",
			fields: m,
			args: args{
				segment: "00000000000000000005.fdb",
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
	f, err := m.OpenFileReader(filepath.Join(binlogPath, "00000000000000000005.fdb"))
	assert.Nil(t, err)
	bytes, err := ioutil.ReadAll(f)
	assert.Nil(t, err)
	assert.Equal(t, td.MockBlk, bytes[:len(td.MockBlk)])
	f.Close()
	f, err = m.OpenFileReader(filepath.Join(binlogPath, "00000000000000000007.fdb"))
	assert.Nil(t, err)
	bytes, err = ioutil.ReadAll(f)
	assert.Nil(t, err)
	assert.Equal(t, td.MockBlk, bytes[:len(td.MockBlk)])
	f.Close()

	//非解密形式读取文件，数据不相等
	f, err = tbf.OpenFile(filepath.Join(binlogPath, "00000000000000000005.fdb"), os.O_RDONLY, 0)
	assert.Nil(t, err)
	bytes, err = ioutil.ReadAll(f)
	assert.Nil(t, err)
	assert.NotEqual(t, td.MockBlk, bytes[:len(td.MockBlk)])
	f.Close()
	//00000000000000000007.fdb为非加密文件，可以以普通形式打开
	f, err = tbf.OpenFile(filepath.Join(binlogPath, "00000000000000000007.fdb"), os.O_RDONLY, 0)
	assert.Nil(t, err)
	bytes, err = ioutil.ReadAll(f)
	assert.Nil(t, err)
	assert.Equal(t, td.MockBlk, bytes[:len(td.MockBlk)])
	f.Close()
}
