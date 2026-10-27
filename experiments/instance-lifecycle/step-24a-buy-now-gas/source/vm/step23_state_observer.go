package wasmer

import (
	"chainmaker.org/chainmaker/protocol/v2"
	"fmt"
)

// Transparent, single-call forwarding observer. It never invokes an extra state
// API and never obtains/merges the transaction's internal read/write maps.
type a23StateOperation struct {
	Sequence int    `json:"sequence"`
	CallID   int    `json:"call_id"`
	Kind     string `json:"kind"`
	Contract string `json:"contract"`
	Key      []byte `json:"key"`
	Value    []byte `json:"value,omitempty"`
	Error    string `json:"error"`
}

var a23AllOperations []a23StateOperation

type a23StateContext struct {
	protocol.TxSimContext
	call *a23Call
}

func a23RecordState(c *a23Call, kind, contract string, key, value []byte, err error) {
	op := a23StateOperation{Sequence: len(a23AllOperations) + 1, CallID: c.CallID, Kind: kind, Contract: contract, Key: append([]byte(nil), key...), Value: append([]byte(nil), value...), Error: fmt.Sprint(err)}
	c.StateOps = append(c.StateOps, op)
	a23AllOperations = append(a23AllOperations, op)
}
func (s *a23StateContext) Get(contract string, key []byte) ([]byte, error) {
	value, err := s.TxSimContext.Get(contract, key)
	a23RecordState(s.call, "Get", contract, key, value, err)
	return value, err
}
func (s *a23StateContext) Put(contract string, key, value []byte) error {
	k := append([]byte(nil), key...)
	v := append([]byte(nil), value...)
	err := s.TxSimContext.Put(contract, key, value)
	a23RecordState(s.call, "Put", contract, k, v, err)
	return err
}
func (s *a23StateContext) Del(contract string, key []byte) error {
	k := append([]byte(nil), key...)
	err := s.TxSimContext.Del(contract, key)
	a23RecordState(s.call, "Del", contract, k, nil, err)
	return err
}
func a23ObserveState(ctx protocol.TxSimContext, c *a23Call) protocol.TxSimContext {
	if !eTraceEnabled {
		return ctx
	}
	return &a23StateContext{TxSimContext: ctx, call: c}
}
