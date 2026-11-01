/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package store

import (
	"encoding/json"
	"os"
	"path"
	"path/filepath"
	"reflect"
	"testing"

	storePb "chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/protocol/v2/test"
	"chainmaker.org/chainmaker/store/v2/bigfilterdb"
	"chainmaker.org/chainmaker/store/v2/blockdb"
	"chainmaker.org/chainmaker/store/v2/conf"
	"chainmaker.org/chainmaker/store/v2/contracteventdb"
	"chainmaker.org/chainmaker/store/v2/historydb"
	"chainmaker.org/chainmaker/store/v2/indexer"
	"chainmaker.org/chainmaker/store/v2/resultdb"
	"chainmaker.org/chainmaker/store/v2/rolling_window_cache"
	"chainmaker.org/chainmaker/store/v2/statedb"
	"chainmaker.org/chainmaker/store/v2/txexistdb"
)

func genTestConfig() *conf.StorageConfig {
	config := &conf.StorageConfig{}
	cJson := `{
"StorePath":"./data/org1/ledgerData1",
"DbPrefix":"","WriteBufferSize":0,
"BloomFilterBits":0,
"BlockWriteBufferSize":0,
"DisableHistoryDB":false,
"DisableResultDB":false,
"DisableContractEventDB":true,
"LogDBWriteAsync":false,
"BlockDbConfig":{
	"Provider":"leveldb",
	"LevelDbConfig":{
		"store_path":"./data/org1/blocks"
	},
	"BadgerDbConfig":null,
	"SqlDbConfig":null
},
"TxExistDbConfig":{
	"Provider":"leveldb",
	"LevelDbConfig":{
		"store_path":"./data/org1/txexist"
	},
	"BadgerDbConfig":null,
	"SqlDbConfig":null
},
"StateDbConfig":{
	"Provider":"leveldb",
	"LevelDbConfig":{"store_path":"./data/org1/statedb"},
	"BadgerDbConfig":null,
	"SqlDbConfig":null,
	"BloomConfig": {
		"Enable": true,
    	"DumpPath": "./bloom",
    	"KeysCapacity": 200000000,
    	"FalsePositiveRate": 0.01,
    	"DumpPerBlocksCommitted": 10
	}
},
"HistoryDbConfig":{
	"Provider":"leveldb",
	"LevelDbConfig":{"store_path":"./data/org1/history"},
	"BadgerDbConfig":null,"SqlDbConfig":null
},
"ResultDbConfig":{
	"Provider":"leveldb",
	"LevelDbConfig":{"store_path":"./data/org1/result"},
	"BadgerDbConfig":null,
	"SqlDbConfig":null
},
"ContractEventDbConfig":{
	"Provider":"sql",
	"LevelDbConfig":null,
	"BadgerDbConfig":null,
	"SqlDbConfig":{
		"dsn":"root:password@tcp(127.0.0.1:3306)/",
		"sqldb_type":"mysql"
	}
},
"UnArchiveBlockHeight":0,
"Encryptor":"sm4",
"EncryptKey":"1234567890123456"
}`
	//config.DisableBigFilter = true
	if err := json.Unmarshal([]byte(cJson), config); err != nil {
		panic(err)
	}
	return config
}

func Test_storeBuilder_create(t *testing.T) {
	basePath := "./data"
	defer os.RemoveAll(basePath)
	config := &conf.StorageConfig{
		StorePath:              basePath + "/ledgerData1",
		DbPrefix:               "",
		WriteBufferSize:        0,
		BloomFilterBits:        0,
		BlockWriteBufferSize:   0,
		DisableHistoryDB:       false,
		DisableResultDB:        false,
		DisableContractEventDB: true,
		DisableBlockFileDb:     false,
		WALEncryptMode:         "async",
		Encryptor:              "sm4",
		EncryptKey:             "1234567890123456",
		WriteBlockType:         1,
		ReadBFDBTimeOut:        3000,
		BlockDbConfig: &conf.DbConfig{
			Provider: "leveldb",
			LevelDbConfig: map[string]interface{}{
				"store_path": basePath + "/blocks",
			},
			BadgerDbConfig: nil,
			SqlDbConfig:    nil,
		},
		TxExistDbConfig: &conf.DbConfig{
			Provider: "leveldb",
			LevelDbConfig: map[string]interface{}{
				"store_path": basePath + "/txexist",
			},
			BadgerDbConfig: nil,
			SqlDbConfig:    nil,
		},
		StateDbConfig: &conf.DbConfig{
			Provider: "leveldb",
			LevelDbConfig: map[string]interface{}{
				"store_path": basePath + "/statedb",
			},
			BadgerDbConfig: nil,
			SqlDbConfig:    nil,
			BloomConfig: &conf.BloomConfig{
				Enable:                 false,
				DumpPath:               basePath + "/ledgerData1/bloom",
				KeysCapacity:           200000000,
				FalsePositiveRate:      0.01,
				DumpPerBlocksCommitted: 10,
			},
		},
		ResultDbConfig: &conf.DbConfig{
			Provider: "leveldb",
			LevelDbConfig: map[string]interface{}{
				"store_path": basePath + "/resultdb",
			}},
		ContractEventDbConfig: &conf.DbConfig{
			Provider:       "sql",
			LevelDbConfig:  nil,
			BadgerDbConfig: nil,
			SqlDbConfig: map[string]interface{}{
				"dsn":        "root:password@tcp(127.0.0.1:3306)/",
				"sqldb_type": "mysql",
			},
		},
		HistoryDbConfig: &conf.HistoryDbConfig{
			DbConfig: conf.DbConfig{
				Provider:       "leveldb",
				LevelDbConfig:  map[string]interface{}{"store_path": "./data/org1/history"},
				BadgerDbConfig: nil,
				SqlDbConfig:    nil,
			},
		},
		BigFilter:            &conf.BigFilterConfig{},
		EnableBigFilter:      false,
		DisableStateCache:    true,
		UnArchiveBlockHeight: 0,
	}
	builder := newStoreBuilder("chain1", config, test.GoLogger{}, nil)
	var (
		// binLogger binlog.BinLogger
		binLogger       indexer.BinLoggerIndexer
		blockDB         blockdb.BlockDB
		stateDB         statedb.StateDB
		historyDB       historydb.HistoryDB
		contractEventDB contracteventdb.ContractEventDB
		resultDB        resultdb.ResultDB
		txExistDB       txexistdb.TxExistDB
		commonDB        protocol.DBHandle
		// walLog          *wal.Log
		walLog      *indexer.WalIndexer
		bigFilterDB bigfilterdb.BigFilterDB
		rwCache     rolling_window_cache.RollingWindowCache
	)
	type args struct {
		out interface{}
	}
	tests := []struct {
		name      string
		fields    *storeBuilder
		args      args
		wantErr   bool
		shouldNil bool
	}{
		{
			name:      "create_binLogger",
			fields:    builder,
			args:      args{out: &binLogger},
			wantErr:   false,
			shouldNil: false,
		},
		{
			name:    "create_blockdb",
			fields:  builder,
			args:    args{out: &blockDB},
			wantErr: false,
		},
		{
			name:    "create_stateDB",
			fields:  builder,
			args:    args{out: &stateDB},
			wantErr: false,
		},
		{
			name:    "create_historyDB",
			fields:  builder,
			args:    args{out: &historyDB},
			wantErr: false,
		},
		{
			name:      "create_contractEventDB",
			fields:    builder,
			args:      args{out: &contractEventDB},
			wantErr:   false,
			shouldNil: true,
		},
		{
			name:    "create_resultDB",
			fields:  builder,
			args:    args{out: &resultDB},
			wantErr: false,
		},
		{
			name:    "create_txExistDB",
			fields:  builder,
			args:    args{out: &txExistDB},
			wantErr: false,
		},
		{
			name:    "create_commonDB",
			fields:  builder,
			args:    args{out: &commonDB},
			wantErr: false,
		},
		{
			name:      "create_wal",
			fields:    builder,
			args:      args{out: &walLog},
			wantErr:   false,
			shouldNil: true,
		},
		{
			name:      "create_bigFilterDB",
			fields:    builder,
			args:      args{out: &bigFilterDB},
			wantErr:   false,
			shouldNil: true,
		},
		{
			name:    "create_rwCache",
			fields:  builder,
			args:    args{out: &rwCache},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := tt.fields
			if err := s.create(tt.args.out); (err != nil) != tt.wantErr {
				t.Errorf("storeBuilder.create() error = %v, wantErr %v", err, tt.wantErr)
			}
			if (reflect.ValueOf(tt.args.out).Elem().IsZero()) != tt.shouldNil {
				str := "nil"
				if !reflect.ValueOf(tt.args.out).Elem().IsZero() {
					str = "not nil"
				}
				should := "should"
				if !tt.shouldNil {
					should = "should not"
				}
				t.Errorf("storeBuilder.create()[%s] failed, out is %v, but %v is nil", reflect.ValueOf(tt.args.out).Elem().Type().Name(), str, should)
			}
		})
	}
}

func Test_storeBuilder_Build(t *testing.T) {
	dbConfig := genTestConfig()
	defer os.RemoveAll(filepath.Dir(dbConfig.StorePath))
	chainId := "chain_test"
	builder := newStoreBuilder(chainId, dbConfig, test.GoLogger{}, nil)
	defer func() {
		os.RemoveAll("data")
		if dbConfig.StateDbConfig.EnableBloom() {
			os.RemoveAll(path.Join(dbConfig.StateDbConfig.BloomConfig.DumpPath, chainId))
		}
	}()
	tests := []struct {
		name    string
		fields  *storeBuilder
		want    protocol.BlockchainStore
		wantErr bool
	}{
		{
			name:   "store_build",
			fields: builder,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := tt.fields
			got, err := b.Build()
			if (err != nil) != tt.wantErr {
				t.Errorf("storeBuilder.Build() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			_ = got.InitGenesis(createConfigBlockWithRWSets(chainId))
			h, _ := got.GetLastHeight()
			for i := h + 1; i < h+10; i++ {
				_ = got.PutBlock(createBlockAndRWSets(chainId, uint64(i), 10000))
				// got.PutBlock(createBlockAndRWSets(chainId, 2, 10000))
			}
			h, _ = got.GetLastHeight()
			block, _ := got.GetBlockWithRWSets(h / 2)
			for _, tx := range block.Block.Txs {
				_, err := got.GetTx(tx.Payload.TxId)
				if err != nil {
					panic(err)
				}
			}
			// t.Log(got.GetLastHeight())
			// t.Log(got.GetBlockWithRWSets(h))
		})
	}
}

func createConfigBlockWithRWSets(chainId string) *storePb.BlockWithRWSet {
	block := createConfigBlock(chainId, 0)
	var txRWSets = getTxRWSets()
	txRWSets[0].TxId = block.Txs[0].Payload.TxId
	return &storePb.BlockWithRWSet{
		Block:    block,
		TxRWSets: txRWSets,
	}
}
