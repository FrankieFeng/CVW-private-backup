/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package bloom

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"reflect"
	"testing"

	acPb "chainmaker.org/chainmaker/pb-go/v2/accesscontrol"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/protocol/v2/test"
	"chainmaker.org/chainmaker/store/v2/conf"
	"chainmaker.org/chainmaker/store/v2/serialization"
	"chainmaker.org/chainmaker/store/v2/statedb"
	"github.com/golang/mock/gomock"
)

var (
	testChain    = "chain_test"
	testContract = "test_contract"
)

func createBlockAndRWSets(chainId string, height uint64, txNum int) *storePb.BlockWithRWSet {
	block := &commonPb.Block{
		Header: &commonPb.BlockHeader{
			ChainId:     chainId,
			BlockHeight: height,
			Proposer: &acPb.Member{
				OrgId:      "org1",
				MemberInfo: []byte("User1"),
				MemberType: 0,
			},
		},
	}

	for i := 0; i < txNum; i++ {
		tx := &commonPb.Transaction{
			Payload: &commonPb.Payload{
				ChainId:  chainId,
				TxId:     generateTxId(chainId, height, i),
				Sequence: uint64(i),
			},
			Sender: &commonPb.EndorsementEntry{
				Signer: &acPb.Member{
					OrgId:      "org1",
					MemberInfo: []byte("User1"),
				},
				Signature: []byte("signature1"),
			},
			Result: &commonPb.Result{
				Code: commonPb.TxStatusCode_SUCCESS,
				ContractResult: &commonPb.ContractResult{
					Result: []byte("ok"),
				},
			},
		}
		block.Txs = append(block.Txs, tx)
	}

	block.Header.BlockHash = generateBlockHash(chainId, height)
	var txRWSets []*commonPb.TxRWSet
	for i := 0; i < txNum; i++ {
		txRWset := &commonPb.TxRWSet{
			TxId: block.Txs[i].Payload.TxId,
			TxWrites: []*commonPb.TxWrite{
				{
					Key:          []byte(key(height, i)),
					Value:        []byte(value(height, i)),
					ContractName: testContract,
				},
			},
		}
		txRWSets = append(txRWSets, txRWset)
	}

	return &storePb.BlockWithRWSet{
		Block:    block,
		TxRWSets: txRWSets,
	}
}

func key(h uint64, tx int) string {
	return fmt.Sprintf("%d_key_%d", h, tx)
}

func value(h uint64, tx int) string {
	return fmt.Sprintf("%d_value_%d", h, tx)
}

func generateBlockHash(chainId string, height uint64) []byte {
	blockHash := sha256.Sum256([]byte(fmt.Sprintf("%s-%d", chainId, height)))
	return blockHash[:]
}

func generateTxId(chainId string, height uint64, index int) string {
	txIdBytes := sha256.Sum256([]byte(fmt.Sprintf("%s-%d-%d", chainId, height, index)))
	return hex.EncodeToString(txIdBytes[:])
}

func newStateDB(ctl *gomock.Controller) statedb.StateDB {
	kvs := map[string][]byte{}
	innerDB := statedb.NewMockStateDB(ctl)
	innerDB.EXPECT().CommitBlock(gomock.Any(), gomock.Any()).DoAndReturn(func(block *serialization.BlockWithSerializedInfo, isCache bool) error {
		for _, txRWSet := range block.TxRWSets {
			for _, txWrite := range txRWSet.TxWrites {
				k := keyGenerator(txWrite.ContractName, txWrite.Key)
				kvs[string(k)] = txWrite.Value
			}
		}
		return nil
	}).AnyTimes()
	innerDB.EXPECT().ReadObject(gomock.Any(), gomock.Any()).DoAndReturn(func(contractName string, key []byte) ([]byte, error) {
		k := keyGenerator(contractName, key)
		v, exist := kvs[string(k)]
		if exist {
			return v, nil
		}
		return nil, fmt.Errorf("key not exist")
	}).AnyTimes()
	innerDB.EXPECT().ReadObjects(gomock.Any(), gomock.Any()).DoAndReturn(func(contractName string, keys [][]byte) ([][]byte, error) {
		values := make([][]byte, len(keys))
		for i, k := range keys {
			v, exist := kvs[string(keyGenerator(contractName, k))]
			if exist {
				values[i] = v
			}
		}
		return values, nil
	}).AnyTimes()
	innerDB.EXPECT().Close().AnyTimes()
	return innerDB
}

func newTestBloomFilter(chainID string, conf *conf.BloomConfig, logger protocol.Logger) *BloomFilter {
	filter, err := NewBloomFilter(chainID, conf, logger, nil)
	if err != nil {
		panic(err)
	}
	return filter
}

func newTestBloomStateDB(ctl *gomock.Controller, chainID string, conf *conf.BloomConfig, logger protocol.Logger) *BloomStateDb {
	return NewBloomStateDb(newStateDB(ctl), newTestBloomFilter(chainID, conf, logger), logger)
}

func TestBloomStateDb_CommitBlock(t *testing.T) {
	ctl := gomock.NewController(t)
	defer ctl.Finish()
	_, block1, _ := serialization.SerializeBlock(createBlockAndRWSets(testChain, 1, 10))
	_, block2, _ := serialization.SerializeBlock(createBlockAndRWSets(testChain, 2, 10))
	bloomStateDB := newTestBloomStateDB(ctl, testChain, &conf.BloomConfig{
		Enable:                 true,
		DumpPath:               ".",
		KeysCapacity:           10000000,
		FalsePositiveRate:      0.01,
		DumpPerBlocksCommitted: 10,
		DumpWhenClose:          true,
	}, test.GoLogger{})
	defer func() {
		bloomStateDB.Close()
		os.RemoveAll(testChain)
	}()
	type args struct {
		blockWithRWSet *serialization.BlockWithSerializedInfo
		isCache        bool
	}
	tests := []struct {
		name    string
		fields  *BloomStateDb
		args    args
		wantErr bool
	}{
		{
			name:   "test1",
			fields: bloomStateDB,
			args: args{
				blockWithRWSet: block1,
				isCache:        true,
			},
		},
		{
			name:   "test1",
			fields: bloomStateDB,
			args: args{
				blockWithRWSet: block1,
				isCache:        false,
			},
		},
		{
			name:   "test2",
			fields: bloomStateDB,
			args: args{
				blockWithRWSet: block2,
				isCache:        true,
			},
		},
		{
			name:   "test2",
			fields: bloomStateDB,
			args: args{
				blockWithRWSet: block2,
				isCache:        false,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := &BloomStateDb{
				StateDB: tt.fields.StateDB,
				filter:  tt.fields.filter,
			}
			if err := b.CommitBlock(tt.args.blockWithRWSet, tt.args.isCache); (err != nil) != tt.wantErr {
				t.Errorf("BloomStateDb.CommitBlock() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestBloomStateDb_ReadObject(t *testing.T) {
	ctl := gomock.NewController(t)
	defer ctl.Finish()
	bloomStateDB := newTestBloomStateDB(ctl, testChain, &conf.BloomConfig{
		Enable:                 true,
		DumpPath:               ".",
		KeysCapacity:           10000000,
		FalsePositiveRate:      0.01,
		DumpPerBlocksCommitted: 10,
	}, &test.GoLogger{})
	defer func() {
		bloomStateDB.Close()
		os.RemoveAll(testChain)
	}()
	_, block1, _ := serialization.SerializeBlock(createBlockAndRWSets(testChain, 1, 10))
	_, block2, _ := serialization.SerializeBlock(createBlockAndRWSets(testChain, 2, 10))
	_ = bloomStateDB.CommitBlock(block1, true)
	_ = bloomStateDB.CommitBlock(block2, true)

	type args struct {
		contractName string
		key          []byte
	}
	tests := []struct {
		name    string
		fields  *BloomStateDb
		args    args
		want    []byte
		wantErr bool
	}{
		{
			name:   "test1",
			fields: bloomStateDB,
			args: args{
				contractName: testContract,
				key:          []byte(key(1, 1)),
			},
			want: []byte(value(1, 1)),
		},
		{
			name:   "test2",
			fields: bloomStateDB,
			args: args{
				contractName: testContract,
				key:          []byte(key(3, 1)),
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := tt.fields
			got, err := b.ReadObject(tt.args.contractName, tt.args.key)
			if (err != nil) != tt.wantErr {
				t.Errorf("BloomStateDb.ReadObject() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BloomStateDb.ReadObject() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBloomStateDb_ReadObjects(t *testing.T) {
	ctl := gomock.NewController(t)
	defer ctl.Finish()
	bloomStateDB := newTestBloomStateDB(ctl, testChain, &conf.BloomConfig{
		Enable:                 true,
		DumpPath:               ".",
		KeysCapacity:           10000000,
		FalsePositiveRate:      0.01,
		DumpPerBlocksCommitted: 10,
	}, test.GoLogger{})
	defer func() {
		bloomStateDB.Close()
		os.RemoveAll(testChain)
	}()
	_, block1, _ := serialization.SerializeBlock(createBlockAndRWSets(testChain, 1, 10))
	_, block2, _ := serialization.SerializeBlock(createBlockAndRWSets(testChain, 2, 10))
	_ = bloomStateDB.CommitBlock(block1, true)
	_ = bloomStateDB.CommitBlock(block2, true)
	type args struct {
		contractName string
		keys         [][]byte
	}
	tests := []struct {
		name    string
		fields  *BloomStateDb
		args    args
		want    [][]byte
		wantErr bool
	}{
		{
			name:   "test1",
			fields: bloomStateDB,
			args: args{
				contractName: testContract,
				keys: [][]byte{
					[]byte(key(1, 1)),
					[]byte(key(1, 2)),
					[]byte(key(2, 3)),
					[]byte(key(2, 4)),
				},
			},
			want: [][]byte{
				[]byte(value(1, 1)),
				[]byte(value(1, 2)),
				[]byte(value(2, 3)),
				[]byte(value(2, 4)),
			},
		},
		{
			name:   "test2",
			fields: bloomStateDB,
			args: args{
				contractName: testContract,
				keys: [][]byte{
					[]byte(key(1, 1)),
					[]byte(key(2, 1)),
					[]byte(key(3, 1)),
					[]byte(key(2, 4)),
				},
			},
			want: [][]byte{
				[]byte(value(1, 1)),
				[]byte(value(2, 1)),
				nil,
				[]byte(value(2, 4)),
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := tt.fields
			got, err := b.ReadObjects(tt.args.contractName, tt.args.keys)
			if (err != nil) != tt.wantErr {
				t.Errorf("BloomStateDb.ReadObjects() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BloomStateDb.ReadObjects() = %v, want %v", got, tt.want)
			}
		})
	}
}
