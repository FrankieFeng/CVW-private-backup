/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package indexer

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"reflect"
	"testing"

	acPb "chainmaker.org/chainmaker/pb-go/v2/accesscontrol"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2/test"
	"chainmaker.org/chainmaker/store/v2/binlog"
	"chainmaker.org/chainmaker/store/v2/serialization"
)

var userContractName = "contract1"

type memBinLog struct {
	*binlog.MemBinlog
}

func newMemBinLog() *memBinLog {
	return &memBinLog{
		MemBinlog: binlog.NewMemBinlog(&test.GoLogger{}),
	}
}

func (m *memBinLog) WriteAndLocate(height uint64, data []byte) (*storePb.StoreInfo, error) {
	fileName, offset, bytesLen, err := m.Write(height+1, data)
	if err != nil {
		return nil, err
	}
	return &storePb.StoreInfo{
		FileName: fileName,
		Offset:   offset,
		ByteLen:  bytesLen,
	}, nil
}
func (m *memBinLog) ReadAndLocate(height uint64, _ *ReadOptions) ([]byte, *storePb.StoreInfo, error) {
	data, fileName, offset, bytesLen, err := m.ReadLastSegSection(height+1, true)
	if err != nil {
		return nil, nil, nil
	}
	return data, &storePb.StoreInfo{
		FileName: fileName,
		Offset:   offset,
		ByteLen:  bytesLen,
	}, err
}
func (m *memBinLog) ReadAt(fiIndex *storePb.StoreInfo) ([]byte, error) {
	return m.ReadFileSection(fiIndex, 0)
}

func initTestNormalIndexer() *NormalBlockFileIndexer {
	return NewNormalBlockFileIndexer(newMemBinLog(),
		serialization.NewNormalProtobufBlockNormalizer(),
		&test.GoLogger{})
}

func createBlock(chainId string, height uint64, txNum int) *commonPb.Block {
	block := &commonPb.Block{
		Header: &commonPb.BlockHeader{
			ChainId:      chainId,
			BlockHeight:  height,
			BlockVersion: 3000000,
			Proposer: &acPb.Member{
				OrgId:      "org1",
				MemberInfo: []byte("User1"),
			},
		},
		Txs: []*commonPb.Transaction{},
	}
	for i := 0; i < txNum; i++ {
		tx := &commonPb.Transaction{
			Payload: &commonPb.Payload{
				ChainId: chainId,
				TxType:  commonPb.TxType_INVOKE_CONTRACT,
				TxId:    generateTxId(chainId, height, i),
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
	block.Txs[0].Payload.TxId = generateTxId(chainId, height, 0)
	block.Dag = &commonPb.DAG{
		Vertexes: []*commonPb.DAG_Neighbor{{
			Neighbors: []uint32{0, 1, 2},
		}},
	}

	return block
}

func generateBlockHash(chainId string, height uint64) []byte {
	blockHash := sha256.Sum256([]byte(fmt.Sprintf("%s-%d", chainId, height)))
	return blockHash[:]
}

func generateTxId(chainId string, height uint64, index int) string {
	txIdBytes := sha256.Sum256([]byte(fmt.Sprintf("%s-%d-%d", chainId, height, index)))
	return hex.EncodeToString(txIdBytes[:])
}

func createBlockAndRWSets(chainId string, height uint64, txNum int) (*commonPb.Block, []*commonPb.TxRWSet) {
	block := createBlock(chainId, height, txNum)
	var txRWSets []*commonPb.TxRWSet

	for i := 0; i < txNum; i++ {
		key := fmt.Sprintf("key_%d", i)
		value := fmt.Sprintf("value_%d_value_0_e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254e99588bd06b5830d1c968c12cad42e968b4ce6c32a5ce37bad9818c33d659254", i)
		txRWset := &commonPb.TxRWSet{
			TxId: block.Txs[i].Payload.TxId,
			TxWrites: []*commonPb.TxWrite{
				{
					Key:          []byte(key),
					Value:        []byte(value),
					ContractName: userContractName,
				},
			},
		}
		txRWSets = append(txRWSets, txRWset)
	}

	return block, txRWSets
}

func toAbsIndex(parent, child *storePb.StoreInfo) *storePb.StoreInfo {
	return &storePb.StoreInfo{
		FileName: parent.FileName,
		Offset:   parent.Offset + child.Offset,
		ByteLen:  child.ByteLen,
	}
}

func TestNormalBlockFileIndexer_AddBlockAndIndex(t *testing.T) {
	indexer := initTestNormalIndexer()
	type args struct {
		fiIndex *storePb.StoreInfo
	}
	tests := []struct {
		name    string
		fields  *NormalBlockFileIndexer
		args    args
		want    *storePb.SerializedBlock
		wantErr bool
	}{
		// TODO: Add test cases.
		{
			name:   "case1",
			fields: indexer,
			args: args{
				fiIndex: &storePb.StoreInfo{
					FileName: "test",
					Offset:   0,
					ByteLen:  0,
				},
			},
			want:    nil,
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := tt.fields
			block, rwset := createBlockAndRWSets("test", 0, 1)
			brw := &storePb.BlockWithRWSet{
				Block:    block,
				TxRWSets: rwset,
			}
			normal, index, err := b.WriteBlock(&storePb.BlockWithRWSet{
				Block:    block,
				TxRWSets: rwset,
			})
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockFileIndexer.AddBlock() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			_, info, err := b.IndexForBlock(brw)
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockFileIndexer.AddBlock() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(normal, &info.BlockNormalized) {
				t.Errorf("NormalBlockFileIndexer.IndexForBlock() = %v, want %v", normal, info.BlockNormalized)
				return
			}
			// if !reflect.DeepEqual(index, info.BlockIndex) {
			// 	t.Errorf("NormalBlockFileIndexer.IndexForBlock() = %v, want %v", index, info.BlockIndex)
			// 	return
			// }

			brwGot, err := b.IndexBlockAt(index.Index)
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockFileIndexer.IndexBlockAt() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(brw, brwGot) {
				t.Errorf("NormalBlockFileIndexer.IndexBlockAt() = %v, want %v", brw, brwGot)
				return
			}
			meteGot, err := b.IndexBlockMetaAt(toAbsIndex(index.Index, index.MetaIndex))
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockFileIndexer.IndexBlockMetaAt() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if !reflect.DeepEqual(normal.Meta, meteGot) {
				t.Errorf("NormalBlockFileIndexer.IndexBlockMetaAt() = %v, want %v", brw, brwGot)
				return
			}

			txGot, err := b.IndexTxAt(toAbsIndex(index.Index, index.TxsIndex[0]))
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockFileIndexer.IndexRWSetAt() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if !reflect.DeepEqual(normal.Txs[0], txGot) {
				t.Errorf("NormalBlockFileIndexer.IndexRWSetAt() = %v, want %v", normal.Txs[0], txGot)
				return
			}

			rwGot, err := b.IndexRWSetAt(toAbsIndex(index.Index, index.RWSetsIndex[0]))
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockFileIndexer.IndexRWSetAt() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if !reflect.DeepEqual(normal.TxRWSets[0], rwGot) {
				t.Errorf("NormalBlockFileIndexer.IndexRWSetAt() = %v, want %v", normal.TxRWSets[0], rwGot)
				return
			}
		})
	}
}

func TestNormalBlockFileIndexer_SpreadOut(t *testing.T) {
	indexer := initTestNormalIndexer()
	type args struct {
	}
	tests := []struct {
		name    string
		fields  *NormalBlockFileIndexer
		args    args
		want    *serialization.SerializationNormalized
		wantErr bool
	}{
		{
			name:    "case1",
			fields:  indexer,
			want:    nil,
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := tt.fields
			block, rwset := createBlockAndRWSets("test", 1, 1)
			brw := &storePb.BlockWithRWSet{
				Block:    block,
				TxRWSets: rwset,
			}
			normal, err := indexer.BlockNormalizer().NormalizeBlock(brw)
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockFileIndexer.NormalizeBlock() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			bytes, _, err := indexer.Assembly(&normal.SerializationNormalized)
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockFileIndexer.IndexFor() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			got, err := b.Disassembly(bytes)
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockFileIndexer.SpreadOut() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, &normal.SerializationNormalized) {
				t.Errorf("NormalBlockFileIndexer.SpreadOut() = %v, want %v", got, tt.want)
				return
			}

			normalGot, err := indexer.BlockNormalizer().NormalizeFromSerialization(got)
			if (err != nil) != tt.wantErr {
				t.Errorf("NormalBlockFileIndexer.NormalizeFromSerialization() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(normal, normalGot) {
				t.Errorf("NormalBlockFileIndexer.NormalizeFromSerialization() = %v, want %v", normal, normalGot)
			}
		})
	}
}
