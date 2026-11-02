/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package encrypt

import (
	"fmt"
	"path/filepath"
	"strings"

	"chainmaker.org/chainmaker/common/v2/crypto"
	"chainmaker.org/chainmaker/protocol/v2"
	tbf "chainmaker.org/chainmaker/store/v2/types/blockfile"
)

type blockFileNamingCoverter struct {
}

// NameToIndex convert segment name in block file to index
func (c blockFileNamingCoverter) NameToIndex(segName string) (uint64, error) {
	return tbf.SegmentNameToUint64(segName)
}

// IndexToName convert segment index in block file to name
func (c blockFileNamingCoverter) IndexToName(index uint64) string {
	return fmt.Sprintf("%s%s", tbf.Uint64ToSegmentName(index), tbf.DBFileSuffix)
}

// NameIsValid check whether the segment name is a legal block file name.
func (c blockFileNamingCoverter) NameIsValid(segName string) bool {
	strs := strings.SplitN(segName, ".", 2)
	if len(strs) != 2 {
		return false
	}
	name, suffix := strs[0], strs[1]
	return len(name) == tbf.DBFileNameLen && suffix == tbf.DBFileSuffix[1:]
}

// BinloggerEncryptManager adapt binlog file encryption interface based on fileEncryptManager
// Added encryption logic for backward files at startup.
type BinloggerEncryptManager struct {
	*fileEncryptManager
}

// NewBinloggerEncryptManager path: keep the same path as blockfiledb
func NewBinloggerEncryptManager(path string, encryptor crypto.SymmetricKey,
	logger protocol.Logger) (*BinloggerEncryptManager, error) {
	m, err := newFileEncryptManager(path, encryptor, logger, blockFileNamingCoverter{})
	if err != nil {
		return nil, err
	}

	em := &BinloggerEncryptManager{m}
	// When a file is written, the user will put it into the encryption queue.
	// Therefore, after startup, the previously unencrypted files need to be put into the encryption queue
	// again to avoid encryption holes (unencrypted files exist in the file sequence)
	filesNeedEncrypted, err := em.getBackwardFiles()
	if err != nil {
		return nil, err
	}
	go em.processEncryptQueue()
	for i := len(filesNeedEncrypted) - 1; i >= 0; i-- {
		m.EncryptAsync(filesNeedEncrypted[i])
	}
	return em, nil
}

// EncryptAsync Encrypts a segment file asynchronously.
// It will add the segment name to the filesToEncryptedCh channel,
// which will be processed in the processEncryptQueue goroutine.
func (m *BinloggerEncryptManager) EncryptAsync(segment string) {
	m.fileEncryptManager.EncryptAsync(segment)
}

// OpenFileReader strictly speaking, you need to verify that the path is consistent with
// the path of BinloggerEncryptManager to prevent the file from being found or parsed incorrectly.
func (m *BinloggerEncryptManager) OpenFileReader(path string) (FileReader, error) {
	segName := filepath.Base(path)
	return m.openFileForRead(segName)
}

func (m *BinloggerEncryptManager) processEncryptQueue() {
	for fileName := range m.filesToEncryptedCh {
		if err := m.encrypt(fileName); err != nil {
			m.logger.Error(err)
		}
	}
}

// getBackwardFiles
func (m *BinloggerEncryptManager) getBackwardFiles() ([]string, error) {
	index := m.fileIndexEncrypted
	files, err := sortedFiles(m.path)
	if err != nil {
		return nil, err
	}
	var filesNeedEncrypted []string
	for i := len(files) - 1; i >= 0; i-- {
		file := files[i]
		if !m.coverter.NameIsValid(file) {
			continue
		}
		idx, err := m.coverter.NameToIndex(file)
		if err != nil {
			return nil, err
		}
		if idx > index {
			filesNeedEncrypted = append(filesNeedEncrypted, file)
		} else {
			break
		}
	}
	return filesNeedEncrypted, nil
}
