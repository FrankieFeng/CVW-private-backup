/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package encrypt

import (
	"fmt"
	"hash/crc32"
	"io"
	"io/ioutil"
	"os"
	"path/filepath"
	"sync"
	"time"
	"unsafe"

	"chainmaker.org/chainmaker/common/v2/crypto"
	"chainmaker.org/chainmaker/protocol/v2"
	tbf "chainmaker.org/chainmaker/store/v2/types/blockfile"
)

var (
	fileEncryptingSuffix             = ".enc"
	indexFileName                    = "enc.index"
	perm                 os.FileMode = 0644
)

// SegmentConverter used to convert segment names and index names.
// The file encryption manager will record the index value of the encrypted file.
type SegmentConverter interface {
	//NameToIndex convert segment name to index.
	NameToIndex(string) (uint64, error)
	//IndexToName convert segment index to name.
	IndexToName(uint64) string
	//NameIsValid check whether the segment name is a legal name.
	NameIsValid(string) bool
}

// fileEncryptManager encrypted file manager, providing the ability to encrypt log files.
// For encrypted files, you need to open and read them through fileEncryptManager,
// because 1. It knows which files are encrypted and which are not encrypted;
// 2. It knows how to decrypt encrypted files
type fileEncryptManager struct {
	mu                 sync.RWMutex
	path               string
	encryptor          crypto.SymmetricKey
	fileIndexEncrypted uint64
	indexFile          *indexFile
	filesToEncryptedCh chan string
	logger             protocol.Logger
	coverter           SegmentConverter
}

// NewfileEncryptManager create a new file encrypt manager
// The parameter encryptor used to encrypt files can't be nil.
// The parameter coverter is an interface for file name conversion which can convert
// file names and file indexes cannot be nil.
func newFileEncryptManager(path string, encryptor crypto.SymmetricKey,
	logger protocol.Logger, coverter SegmentConverter) (_ *fileEncryptManager, err error) {
	if encryptor == nil {
		panic("encryptor cannot be nil")
	}
	if coverter == nil {
		panic("coverter cannot be nil")
	}
	if err = os.MkdirAll(path, perm); err != nil {
		return nil, err
	}
	indexFile, err := newIndexer(path)
	if err != nil {
		return nil, err
	}
	defer func() {
		if err != nil {
			indexFile.Close()
		}
	}()
	m := &fileEncryptManager{
		path:               path,
		encryptor:          encryptor,
		indexFile:          indexFile,
		filesToEncryptedCh: make(chan string, 8),
		logger:             logger,
		coverter:           coverter,
	}

	m.fileIndexEncrypted, err = m.recovery()
	if err != nil {
		return nil, err
	}
	return m, nil
}

func (m *fileEncryptManager) recovery() (uint64, error) {
	//Read the index of encrypted fdb file from the encrypted index file.
	index := m.indexFile.GetIndex()
	// If the encrypted file corresponding to the index exists,
	// it means that the index has been written to the index file,
	// but the encrypted file has not yet replaced the original file, replace it once.
	encPath := fmt.Sprintf("%s%s", filepath.Join(m.path, m.coverter.IndexToName(index)), fileEncryptingSuffix)
	_, err := os.Stat(encPath)
	if err == nil {
		if err = os.Rename(encPath, encPath[:len(encPath)-len(fileEncryptingSuffix)]); err != nil {
			return 0, err
		}
	} else if !os.IsNotExist(err) {
		return 0, err
	}
	return index, nil
}

// OpenFileForRead open the fdb file.
// If the file index value is greater than the encrypted index value,
// it means that the file has not been encrypted yet and can be read directly.
// Otherwise, decrypt the file first and then read it.
func (m *fileEncryptManager) openFileForRead(name string) (FileReader, error) {
	return m.openFileForReadWithJudge(name, func(index uint64) bool {
		return index <= m.fileIndexEncrypted
	})
}

func (m *fileEncryptManager) openFileForReadWithJudge(name string,
	isEncryptedFile func(uint64) bool) (FileReader, error) {
	// name := filepath.Base(path)
	if !m.coverter.NameIsValid(name) {
		return nil, fmt.Errorf("[%s] is not expected file name", name)
	}

	fileIndex, err := m.coverter.NameToIndex(name)
	if err != nil {
		return nil, err
	}

	path := filepath.Join(m.path, name)
	m.mu.RLock()
	defer m.mu.RUnlock()
	if !isEncryptedFile(fileIndex) {
		return tbf.OpenFile(path, os.O_RDONLY, 0)
	}
	return openEncryptedFileForRead(path, m.encryptor)
}

// EncrySegmentFile provide the segment file name without the path to be encrypted,
// If too many encrypted files accumulate, it will cause blocking.
func (m *fileEncryptManager) EncryptAsync(segment string) {
	select {
	case m.filesToEncryptedCh <- segment:
	default:
		start := time.Now()
		m.filesToEncryptedCh <- segment
		m.logger.Warnf("waiting to encrypt segment %s, waiting time: %d ms",
			segment, time.Since(start).Milliseconds())
	}
}

// encrypt file logic, considering consistency,
// first create an encrypted file path/00010.fdb.enc based on the original file path/00010.fdb,
// then write the file index value '00010' into the encrypted index file,
// finally replace the original file with the encrypted file(path/00010.fdb.enc => path/00010.fdb),
// and update the current encrypted index value.
// When any step exits:
// 1. The encrypted file 00010.fdb.enc is not generated, the index of the encrypted file being read is '00009'
// at startup, and then f00010.fdb will be re-encrypted regardless of whether it has been encrypted.
// 2. The encrypted file 00010.fdb.enc is generated but the index '00010' of the encrypted file is not written
// to the index file. At this time, the index stored in the index file is '00009'. After startup, 00010.fdb
// will be re-encrypted  (it is unknown whether the encrypted file is complete and available);
// 3. The index value '00010' of the encrypted file is written to the index file.  After startup,
// determine whether 00010.fdb.enc exists. Existence means that the encrypted file did not successfully
// replace the original file, and the rename operation is performed directly. Non-existence means that
// the encryption of 00010.fdb has been completed.
func (m *fileEncryptManager) encrypt(segFile string) error {
	index, err := m.coverter.NameToIndex(segFile)
	if err != nil {
		return err
	}
	return m.encryptWithIndex(segFile, index)
}

func (m *fileEncryptManager) encryptWithIndex(segFile string, index uint64) error {
	if index < m.fileIndexEncrypted {
		return fmt.Errorf("segment index %d is less than encrypted index: %d", index, m.fileIndexEncrypted)
	}
	srcFile, encryptedFile, err := m.genFileEncrypted(segFile)
	if err != nil {
		return err
	}
	if err := m.writeIndexToFile(index); err != nil {
		return err
	}
	m.mu.Lock()
	defer m.mu.Unlock()
	if err := os.Rename(encryptedFile, srcFile); err != nil {
		return err
	}
	m.fileIndexEncrypted = index
	m.logger.Infof("encrypt segment index to %d", index)
	return nil
}

func (m *fileEncryptManager) genFileEncrypted(segFile string) (string, string, error) {
	file := filepath.Join(m.path, segFile)
	encryptedFile := fmt.Sprintf("%s%s", file, fileEncryptingSuffix)
	if err := m.encryptFile(file, encryptedFile); err != nil {
		return "", "", err
	}
	return file, encryptedFile, nil
}

func (m *fileEncryptManager) writeIndexToFile(index uint64) error {
	return m.indexFile.Write(index)
}

func (m *fileEncryptManager) encryptFile(in, out string) error {
	plaintext, err := ioutil.ReadFile(in)
	if err != nil {
		return err
	}
	ciphertext, err := m.encryptor.Encrypt(plaintext)
	if err != nil {
		return err
	}
	return ioutil.WriteFile(out, ciphertext, perm)
}

// Close close manager
func (m *fileEncryptManager) Close() error {
	if m.indexFile != nil {
		close(m.filesToEncryptedCh)
		indexFile := m.indexFile
		m.indexFile = nil
		return indexFile.Close()
	}
	return nil
}

func sortedFiles(path string) ([]string, error) {
	//os.ReadDir has sorted the files.
	files, err := os.ReadDir(path)
	if err != nil {
		return nil, err
	}
	fileNames := make([]string, 0, len(files))
	for _, file := range files {
		if file.Type().IsRegular() {
			fileNames = append(fileNames, file.Name())
		}
	}

	return fileNames, nil
}

const (
	size = int(unsafe.Sizeof([2]indexRecord{}))
)

type indexFile struct {
	id      uint64
	records [2]indexRecord
	file    *os.File
}

func newIndexer(path string) (*indexFile, error) {
	file, err := os.OpenFile(filepath.Join(path, indexFileName), os.O_RDWR|os.O_CREATE, perm)
	if err != nil {
		return nil, err
	}
	idxFile := &indexFile{
		file: file,
	}
	if err := idxFile.init(); err != nil {
		file.Close()
		return nil, err
	}
	return idxFile, nil
}

func (i *indexFile) init() error {
	err := i.read()
	switch err {
	case io.EOF:
		return nil
	case nil:
	default:
		return err
	}
	r0, r1 := &i.records[0], &i.records[1]
	if r0.id < r1.id {
		r0, r1 = r1, r0
	}
	if err := r0.validate(); err == nil {
		i.id = r0.id
		return nil
	}
	if err := r1.validate(); err == nil {
		i.id = r1.id
		return nil
	}
	return fmt.Errorf("index both invalid, accidental file corruption")
}

func (i *indexFile) Close() error {
	return i.file.Close()
}

func (i *indexFile) cursor() int {
	return int(i.id) & 1
}

func (i *indexFile) Write(idx uint64) error {
	i.id++
	cur := i.cursor()
	i.records[cur] = indexRecord{
		id:    i.id,
		index: idx,
	}
	i.records[cur].checksum = i.records[cur].sum32()
	_, err := i.file.WriteAt((*[size]byte)(unsafe.Pointer(&i.records))[:], 0)
	if err != nil {
		return err
	}
	return i.file.Sync()
}

func (i *indexFile) read() error {
	_, err := i.file.ReadAt((*[size]byte)(unsafe.Pointer(&i.records))[:], 0)
	return err
}

func (i *indexFile) GetIndex() uint64 {
	return i.records[i.cursor()].index
}

type indexRecord struct {
	// id is used to identify the order of records, because the index may be reset
	id       uint64
	index    uint64
	checksum uint32
}

func (r *indexRecord) sum32() uint32 {
	return crc32.ChecksumIEEE(((*[unsafe.Offsetof(indexRecord{}.checksum)]byte)(unsafe.Pointer(r)))[:])
}

func (r *indexRecord) validate() error {
	if r.checksum != r.sum32() {
		return fmt.Errorf("index: %d, validate checkSum fail", r.index)
	}
	return nil
}
