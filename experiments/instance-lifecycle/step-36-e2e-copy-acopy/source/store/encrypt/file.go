/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package encrypt

import (
	"io"
	"io/ioutil"
	"os"

	"chainmaker.org/chainmaker/common/v2/crypto"
	tbf "chainmaker.org/chainmaker/store/v2/types/blockfile"
)

// FileReader aliases
type FileReader = tbf.FileReader

// EncryptedFile represents an encrypted file that implements the FileReader interface.
type EncryptedFile struct {
	enctyptor crypto.SymmetricKey
	file      *tbf.File
	plaintext []byte
	pos       int
}

func openEncryptedFileForRead(name string, encryptor crypto.SymmetricKey) (*EncryptedFile, error) {
	f, err := tbf.OpenFile(name, os.O_RDONLY, 0)
	if err != nil {
		return nil, err
	}
	return &EncryptedFile{
		enctyptor: encryptor,
		file:      f,
	}, nil
}

// Read reads the data. If the data has not been decrypted, decrypt it first and then read it.
func (f *EncryptedFile) Read(b []byte) (int, error) {
	n, err := f.readAt(b, int64(f.pos))
	f.pos += n
	return n, err
}

// ReadAt reads the data. If the data has not been decrypted, decrypt it first and then read it.
func (f *EncryptedFile) ReadAt(b []byte, off int64) (n int, err error) {
	return f.readAt(b, off)
}

func (f *EncryptedFile) readAt(b []byte, off int64) (n int, err error) {
	if f.plaintext == nil {
		plaintext, err := decryptForFile(f.file.File, f.enctyptor)
		if err != nil {
			return 0, err
		}
		f.plaintext = plaintext
	}
	if off >= int64(len(f.plaintext)) {
		return 0, io.EOF
	}
	n = copy(b, f.plaintext[off:])
	return n, nil
}

// Seek reposition the read position. Same as os.File seek behavior.
func (f *EncryptedFile) Seek(offset int64, whence int) (int64, error) {
	var off int64
	switch whence {
	case io.SeekStart:
		off = offset
	case io.SeekCurrent:
		off = int64(f.pos) + offset
	case io.SeekEnd:
		off = int64(len(f.plaintext)) + offset
	}
	if off < 0 {
		return 0, os.ErrInvalid
	}
	f.pos = int(off)
	return off, nil
}

// Lock the file
func (f *EncryptedFile) Lock() error {
	return f.file.Lock()
}

// Unlock the file
func (f *EncryptedFile) Unlock() error {
	return f.file.Unlock()
}

// Size returns the decrypted file size. If the file is not decrypted, decrypt it first.
func (f *EncryptedFile) Size() (int64, error) {
	if f.plaintext == nil {
		plaintext, err := decryptForFile(f.file.File, f.enctyptor)
		if err != nil {
			return 0, err
		}
		f.plaintext = plaintext
	}
	return int64(len(f.plaintext)), nil
}

// Close file
func (f *EncryptedFile) Close() error {
	return f.file.Close()
}

func decryptForFile(f *os.File, enctyptor crypto.SymmetricKey) ([]byte, error) {
	ciphertext, err := ioutil.ReadAll(f)
	if err != nil {
		return nil, err
	}
	plaintext, err := enctyptor.Decrypt(ciphertext)
	if err != nil {
		return nil, err
	}
	return plaintext, nil
}
