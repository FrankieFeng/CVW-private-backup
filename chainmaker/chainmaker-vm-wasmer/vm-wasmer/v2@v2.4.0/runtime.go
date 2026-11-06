/*
Copyright (C) BABEC. All rights reserved.
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
SPDX-License-Identifier: Apache-2.0
*/
package wasmer

import (
	"chainmaker.org/chainmaker/logger/v2"
	commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	wasmer "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"fmt"
	"time"
)

const (
	InitContractFunc           = "init_contract"
	UpgradeContractFunc        = "upgrade"
	runtimeGasLimit     uint64 = 1<<31 - 1
)

type RuntimeInstance struct {
	pool             *vmPool // legacy source compatibility; no live Instance is leased from it
	log              *logger.CMLogger
	chainId          string
	instancesManager *InstancesManager
	contract         commonPb.Contract
	raw              []byte
}

// Pool is retained for source compatibility. Manager-created runtimes return nil.
func (r *RuntimeInstance) Pool() *vmPool { return r.pool }
func (r *RuntimeInstance) Invoke(c *commonPb.Contract, method string, raw []byte, params map[string][]byte, tx protocol.TxSimContext, gas uint64) (*commonPb.ContractResult, protocol.ExecOrderTxType) {
	result, order, _ := r.invokeFresh(c, method, raw, params, tx, gas)
	return result, order
}

// InvokeTime uses exactly the same safe native path as Invoke.
func (r *RuntimeInstance) InvokeTime(c *commonPb.Contract, method string, raw []byte, params map[string][]byte, tx protocol.TxSimContext, gas uint64) (result *commonPb.ContractResult, order protocol.ExecOrderTxType, start, end int64, elapsed, call float64) {
	start = time.Now().UnixNano()
	result, order, call = r.invokeFresh(c, method, raw, params, tx, gas)
	end = time.Now().UnixNano()
	elapsed = float64(end-start) / 1e9
	return
}
func setGasByExport(instance *wasmer.Instance, gas uint64) error {
	setGasFn, err := instance.Exports.GetRawFunction("SetGas")
	if err != nil {
		return err
	}
	defer setGasFn.Close()

	_, err = setGasFn.Call(int64(gas))
	return err
}

func getGasByExport(instance *wasmer.Instance) (uint64, error) {
	getGasFn, err := instance.Exports.GetRawFunction("GetGas")
	if err != nil {
		return 0, err
	}
	defer getGasFn.Close()

	result, err := getGasFn.Call()
	if err != nil {
		return 0, err
	}

	switch v := result.(type) {
	case int32:
		return uint64(v), nil
	case uint32:
		return uint64(v), nil
	case int64:
		return uint64(v), nil
	case uint64:
		return v, nil
	default:
		return 0, fmt.Errorf("GetGas return type %T not supported", result)
	}
}
