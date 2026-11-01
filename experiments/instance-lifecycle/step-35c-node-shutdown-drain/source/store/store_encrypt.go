/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package store

import (
	"chainmaker.org/chainmaker/common/v2/crypto"
)

var _ crypto.SymmetricKey = (*encryptor)(nil)

var (
	// magic number prefix for encrypted string whose length is greater than encryptMaxBytes
	magicE = []byte{0xED}
	// magic number prefix for no encrypted string whose length is greater than encryptMaxBytes
	magicN = []byte{0xB4}
)

// encryptor implemented the crypto.SymmetricKey interface
// and added the maximum encrypted string length judgment
type encryptor struct {
	crypto.SymmetricKey
	encryptMaxBytes int
}

func newEnctyptor(sink crypto.SymmetricKey, encryptMaxBytes int) *encryptor {
	return &encryptor{sink, encryptMaxBytes}
}

// Encrypt palin
func (e *encryptor) Encrypt(plain []byte) ([]byte, error) {
	return e.encryptWithOpts(plain, nil)
}

// EncryptWithOpts encrypt with opts
func (e *encryptor) EncryptWithOpts(plain []byte, opts *crypto.EncOpts) ([]byte, error) {
	return e.encryptWithOpts(plain, opts)
}

// encryptWithOpts if the plain length is greater than encryptMaxBytes, no encryption is performed and
// add a magic number prefix '0xB4' to the beginning of the raw string.
// If the length of encrypted plain is greater than encryptMaxBytes,
// it is marked with a magic number prefix '0xED'.
func (e *encryptor) encryptWithOpts(plain []byte, opts *crypto.EncOpts) ([]byte, error) {
	if e.encryptMaxBytes > 0 && len(plain) > e.encryptMaxBytes {
		to := make([]byte, 0, len(magicN)+len(plain))
		return append(append(to, magicN...), plain...), nil
	}
	var (
		bz  []byte
		err error
	)
	if opts == nil {
		bz, err = e.SymmetricKey.Encrypt(plain)
	} else {
		bz, err = e.SymmetricKey.EncryptWithOpts(plain, opts)
	}

	if err != nil {
		return bz, err
	}
	if e.encryptMaxBytes > 0 && len(bz) > e.encryptMaxBytes {
		to := make([]byte, 0, len(magicE)+len(bz))
		bz = append(append(to, magicE...), bz...)
	}
	return bz, err
}

// Decrypt ciphertext.
func (e *encryptor) Decrypt(ciphertext []byte) ([]byte, error) {
	return e.decryptWithOpts(ciphertext, nil)
}

// DecryptWithOpts decrypt with opts
func (e *encryptor) DecryptWithOpts(ciphertext []byte, opts *crypto.EncOpts) ([]byte, error) {
	return e.decryptWithOpts(ciphertext, opts)
}

func (e *encryptor) decryptWithOpts(ciphertext []byte, opts *crypto.EncOpts) ([]byte, error) {
	encrypted, text := e.isEncrypted(ciphertext)
	if !encrypted {
		return text, nil
	}
	if opts == nil {
		return e.SymmetricKey.Decrypt(text)
	}
	return e.SymmetricKey.DecryptWithOpts(text, opts)
}

func (e *encryptor) isEncrypted(ciphertext []byte) (bool, []byte) {
	if e.encryptMaxBytes > 0 && len(ciphertext) > e.encryptMaxBytes {
		if ciphertext[0] == magicE[0] {
			return true, ciphertext[len(magicE):]
		}
		return false, ciphertext[len(magicN):]
	}
	return true, ciphertext
}

// encryptCodec wraps SymmetricKey and implements the indexer.BytesCodec interface
type encryptCodec struct {
	cryptor crypto.SymmetricKey
}

func newEncryptCodec(sink crypto.SymmetricKey) *encryptCodec {
	return &encryptCodec{sink}
}

// Encode serialize bytes.
func (e *encryptCodec) Encode(plain []byte) ([]byte, error) {
	return e.cryptor.Encrypt(plain)
}

// Decode deserialize bytes.
func (e *encryptCodec) Decode(ciphertext []byte) ([]byte, error) {
	return e.cryptor.Decrypt(ciphertext)
}
