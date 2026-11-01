/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package encrypt

import (
	"fmt"
	"io"
	"os"
	"strconv"

	"chainmaker.org/chainmaker/common/v2/crypto"
	"chainmaker.org/chainmaker/protocol/v2"
)

var (
	truncateBackMark = "TB"
)

type walNamingCoverter struct {
}

// NameToIndex convert segment name to index.
func (c walNamingCoverter) NameToIndex(segName string) (uint64, error) {
	return strconv.ParseUint(segName[:20], 10, 64)
}

// IndexToName convert segment index to name.
func (c walNamingCoverter) IndexToName(index uint64) string {
	return fmt.Sprintf("%020d", index)
}

// NameIsValid check whether the segment name is a legal name.
func (c walNamingCoverter) NameIsValid(segName string) bool {
	return len(segName) == 20
}

// WalEncryptManager wal file encrypt manager.
type WalEncryptManager struct {
	*fileEncryptManager
	truncateBeforeIndex uint64
	truncateBackIndex   uint64
	truncateAfterChan   chan chan error
}

// NewWalEncryptManager new wal encrypt manager
func NewWalEncryptManager(path string, encryptor crypto.SymmetricKey,
	logger protocol.Logger) (*WalEncryptManager, error) {
	m, err := newFileEncryptManager(path, encryptor, logger, walNamingCoverter{})
	if err != nil {
		return nil, err
	}
	em := &WalEncryptManager{
		fileEncryptManager: m,
		truncateAfterChan:  make(chan chan error, 1),
	}

	// When a file is written, the user will put it into the encryption queue.
	// Therefore, after startup, the previously unencrypted files need to be put into the encryption queue
	// again to avoid encryption holes (unencrypted files exist in the file sequence)
	filesNeedEncrypted, err := em.getBackwardFiles()
	if err != nil {
		return nil, err
	}
	go em.processEncryptQueue()
	//不对wal最新的文件进行加密
	for i := len(filesNeedEncrypted) - 1; i >= 1; i-- {
		m.EncryptAsync(filesNeedEncrypted[i])
	}
	return em, nil
}

// EncryptAsync Encrypts a segment file asynchronously.
func (m *WalEncryptManager) EncryptAsync(segment string) {
	m.fileEncryptManager.EncryptAsync(segment)
}

func (m *WalEncryptManager) Read(segFile string) ([]byte, error) {
	rd, err := m.openFileForReadWithJudge(segFile, func(index uint64) bool {
		return index <= m.fileIndexEncrypted && index > m.truncateBackIndex
	})
	if err != nil {
		return nil, err
	}
	defer rd.Close()
	return io.ReadAll(rd)
}

// TruncateFront truncate操作和读文件存在一定的间隙，即虽然加密器知晓被truncate了，但不知道index对应的文件是否真正的是非加密的
// 所以在TruncateFront之后，需要保证调用者再次读取的时候，文件已经是非加密的了
func (m *WalEncryptManager) TruncateFront(index uint64) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.truncateBeforeIndex = index
	return nil
}

// TruncateBack for TruncateBack, the encryption index value needs to be moved to the index specified by
// the parameter, and then the files waiting to be encrypted are filtered that file index >= index
// no longer need to be encrypted.
func (m *WalEncryptManager) TruncateBack(index uint64) error {
	m.truncateBackIndex = index
	errCh := make(chan error)
	m.truncateAfterChan <- errCh
	m.filesToEncryptedCh <- truncateBackMark
	return <-errCh
}

// processEncryptQueue process encrypt queue.
// Dealing with three situations:
// 1. TruncateBack: Filter files waiting to be encrypted in the queue whose index ​​less than truncateBackIndex
// will be placed in the priority queue that will not block the main process,​ ​greater than truncateBackIndex
// will be ignored. If the maximum index of the encrypted file is greater than truncateBackIndex,
// truncateBackIndex is used to overwrite the maximum index value written to the file.
// 2. TruncateFront: Files waiting to be encrypted in the queue whose index ​​less than TruncateFront
// will be ignored.
// 3. Normal: All files waiting to be encrypted in the queue will be encrypted.
func (m *WalEncryptManager) processEncryptQueue() {
	var (
		errCh            chan error
		firstEncryptChan = make(chan string, cap(m.filesToEncryptedCh))
		encryptQueue     chan string
		notify           = func(err error) {
			select {
			case errCh <- err:
			default:
			}
			errCh = nil
		}
	)
	for {
		select {
		// Prioritize encryption of files in the queue because they have smaller index values.
		case fileName := <-encryptQueue:
			if err := m.encrypt(fileName); err != nil {
				m.logger.Error(err)
			}
			continue
		default:
		}
		select {
		case errCh = <-m.truncateAfterChan:
			// If m.filesToEncryptedCh receives the message first and the first element is truncateBackMark,
			// truncateBackIndex will be set to 0.
			if m.truncateBackIndex == 0 {
				notify(nil)
			} else if m.fileIndexEncrypted > m.truncateBackIndex {
				if err := m.writeIndexToFile(m.truncateBackIndex); err != nil {
					m.truncateBackIndex = 0
					notify(err)
				}
				m.fileIndexEncrypted = m.truncateBackIndex
			}
		default:
			fileName, ok := <-m.filesToEncryptedCh
			if !ok {
				return
			}

			if done, queue := m.doTruncateAfter(fileName, firstEncryptChan); done {
				// When doTruncateAfter puts elements into firstEncryptChan, it needs to keep the return
				// value queue as nil to prevent unnecessary errors and complexity caused by
				// synchronous production and consumption.
				// queue not nil means that the truncateAfter operation has been completed,
				// can start consumption to encrypt files.
				if encryptQueue = queue; encryptQueue != nil {
					m.truncateBackIndex = 0
					notify(nil)
				}
				continue
			}
			index, err := m.coverter.NameToIndex(fileName)
			if err != nil {
				m.logger.Errorf("name[%s] to index error: %v", fileName, err)
				continue
			}
			// Ignore files with index values ​​< truncateBeforeIndex
			if m.doTruncateBefore(fileName, index) {
				continue
			}
			if err := m.encryptWithIndex(fileName, index); err != nil {
				m.logger.Error(err)
			}
		}
	}
}

func (m *WalEncryptManager) doTruncateBefore(fileName string, fileIndex uint64) bool {
	if m.truncateBeforeIndex > 0 {
		if fileIndex == m.truncateBeforeIndex {
			if err := m.reencryptPreviousFile(fileName); err != nil {
				m.logger.Errorf("reencrypt previous file [%s] error: %v", fileName, err)
			}
			m.logger.Infof("reencrypt previous file index [%s], ok", fileName)
			return true
		}
		//之前的文件将会被删除，不做处理
		return fileIndex < m.truncateBeforeIndex
	}
	return false
}

// doTruncateAfter do truncate after operation.
// Put the file names with index less than truncateBackIndex into the priority queue(firstEncryptChan)
// to be encrypted, other files will be ignore.
// If the file name is TB means that the truncateAfter operation has been completed, the queue will be
// returned to start encryption of the files in the queue.
// The return value done indicates whether the truncateAfter operation was performed, ture is performed.
// If encryptQueue is not nil, it means that the truncateAfter operation has been completed and
// start encryption of the files in the queue
func (m *WalEncryptManager) doTruncateAfter(fileName string,
	firstEncryptChan chan string) (done bool, encryptQueue chan string) {
	if m.truncateBackIndex > 0 {
		done = true
		// After the file diversion is completed, the encryption process of the previous files
		// will be started
		if fileName == truncateBackMark {
			encryptQueue = firstEncryptChan
			return
		}
		index, err := m.coverter.NameToIndex(fileName)
		if err != nil {
			m.logger.Errorf("name[%s] to index error: %v", fileName, err)
			return
		}
		// Use a higher priority channel to process the previous files sequentially.
		if index < m.truncateBackIndex {
			firstEncryptChan <- fileName
		}
	}
	return
}

// reencryptPreviousFile 只是对之前的文件做一个重新加密，而不修改持有的加密索引值
func (m *WalEncryptManager) reencryptPreviousFile(segFile string) error {
	srcFile, encryptedFile, err := m.genFileEncrypted(segFile)
	if err != nil {
		return err
	}
	m.mu.Lock()
	defer m.mu.Unlock()
	if err := os.Rename(encryptedFile, srcFile); err != nil {
		return err
	}
	m.truncateBeforeIndex = 0
	return nil
}

func (m *WalEncryptManager) getBackwardFiles() ([]string, error) {
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
