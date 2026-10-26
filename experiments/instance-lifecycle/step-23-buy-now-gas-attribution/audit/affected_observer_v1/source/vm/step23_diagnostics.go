package wasmer

import (
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	w "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"syscall"
)

// All observers run on the existing owner. No guest call is added by these helpers.
type a23Call struct {
	CallID              int                    `json:"call_id"`
	ParentCallID        int                    `json:"parent_call_id"`
	Depth               int                    `json:"depth"`
	Caller              string                 `json:"caller"`
	Contract            string                 `json:"contract"`
	Method              string                 `json:"method"`
	TxID                string                 `json:"tx_id"`
	InstanceID          int                    `json:"instance_id"`
	InstanceGoID        string                 `json:"instance_go_id"`
	StoreID             string                 `json:"store_id"`
	ModuleID            string                 `json:"module_go_id"`
	Variant             string                 `json:"variant"`
	CacheKey            string                 `json:"cache_key"`
	SourceSHA           string                 `json:"source_sha"`
	UsesBefore          int                    `json:"instance_uses_before"`
	Params              json.RawMessage        `json:"actual_parameters"`
	InputSHA            string                 `json:"input_sha"`
	LedgerBefore        string                 `json:"initial_ledger_sha"`
	RWBefore            json.RawMessage        `json:"visible_rw_before"`
	RWAfter             json.RawMessage        `json:"visible_rw_after"`
	GasIn               uint64                 `json:"gas_in_cumulative"`
	GasOut              uint64                 `json:"gas_out_cumulative"`
	GetterRemaining     uint64                 `json:"getter_remaining_final"`
	GetterVerifications int                    `json:"getter_verifications"`
	BeforeSetRemaining  *uint64                `json:"remaining_before_setgas,omitempty"`
	BeforeSetStatus     string                 `json:"before_setgas_status"`
	Result              *common.ContractResult `json:"actual_result"`
	CallError           string                 `json:"call_error_observed"`
	BridgeSeq           int                    `json:"bridge_seq_count"`
}

var a23Stack []*a23Call
var a23Calls = map[*SimContext]*a23Call{}
var a23LedgerBefore string

func a23Hash(b []byte) string { h := sha256.Sum256(b); return hex.EncodeToString(h[:]) }
func a23JSON(x interface{}) json.RawMessage {
	b, e := json.Marshal(x)
	if e != nil {
		panic(e)
	}
	return b
}
func a23RW(ctx protocol.TxSimContext) json.RawMessage {
	// GetTxRWSet is intentionally NOT used: it releases iterators. This API only
	// merges into newly allocated Go maps. Snapshots are cumulative visible sets.
	result := map[string]interface{}{}
	for _, n := range []string{"identity", "erc721", "exchange"} {
		reads, writes := ctx.GetTxRWMapByContractName(n)
		result[n] = map[string]interface{}{"reads": reads, "writes": writes}
	}
	return a23JSON(result)
}
func a23Enter(id, depth int, contract *common.Contract, method string, params map[string][]byte, ctx protocol.TxSimContext, gas uint64) *a23Call {
	w.ManagedAssert()
	parent := -1
	caller := "external"
	if len(a23Stack) > 0 {
		p := a23Stack[len(a23Stack)-1]
		parent = p.CallID
		caller = p.Contract
	}
	j := a23JSON(params)
	c := &a23Call{CallID: id, ParentCallID: parent, Depth: depth, Caller: caller, Contract: contract.Name, Method: method, TxID: ctx.GetTx().Payload.TxId, Params: j, InputSHA: a23Hash(j), RWBefore: a23RW(ctx), GasIn: gas, LedgerBefore: a23LedgerBefore}
	a23Stack = append(a23Stack, c)
	eEmit(map[string]interface{}{"event": "call_enter", "call_id": id, "parent_call_id": parent, "caller": caller, "contract": c.Contract, "method": method, "depth": depth, "tx_id": c.TxID, "gas_in_cumulative": gas, "input_sha": c.InputSHA, "owner_tid": syscall.Gettid()})
	return c
}
func a23Bind(c *a23Call, inst *w.Instance, id, used int, storeID, moduleID, key, variant, sourceSHA string) {
	c.InstanceID = id
	c.InstanceGoID = fmt.Sprintf("%p", inst)
	c.UsesBefore = used
	c.StoreID = storeID
	c.ModuleID = moduleID
	c.CacheKey = key
	c.Variant = variant
	c.SourceSHA = sourceSHA
}
func a23BeforeSet(c *a23Call, inst *w.Instance) {
	c.BeforeSetStatus = "not_observed_probe_off"
	if !eTraceEnabled {
		return
	}
	slot := eSlots[c.Contract]
	mem, e := inst.Exports.GetMemory("memory")
	if e != nil {
		panic(e)
	}
	d := mem.Data()
	if slot.Slot+8 > uint64(len(d)) {
		panic("verified slot out of bounds")
	}
	ptr := binary.LittleEndian.Uint64(d[slot.Slot : slot.Slot+8])
	if ptr == 0 {
		c.BeforeSetStatus = "registry_not_initialized_before_SetGas"
		return
	}
	if ptr+8 > uint64(len(d)) {
		panic("counter pointer out of bounds")
	}
	remain := binary.LittleEndian.Uint64(d[ptr : ptr+8])
	c.BeforeSetRemaining = &remain
	c.BeforeSetStatus = "prior_instance_state; not current-call charged Gas"
}
func a23Enrich(sc *SimContext, fields map[string]interface{}) {
	if c := a23Calls[sc]; c != nil {
		fields["call_id"] = c.CallID
		fields["parent_call_id"] = c.ParentCallID
		fields["caller"] = c.Caller
		fields["store_id"] = c.StoreID
		fields["module_go_id"] = c.ModuleID
		fields["instance_uses_before"] = c.UsesBefore
		fields["variant"] = c.Variant
		fields["owner_tid"] = syscall.Gettid()
	}
}
func a23Bridge(sc *SimContext, when string, isLen bool, gas uint64, result *common.ContractResult) {
	if !eTraceEnabled {
		return
	}
	c := a23Calls[sc]
	if c == nil {
		panic("bridge without current call")
	}
	if when == "before_wacsi" {
		c.BridgeSeq++
	}
	fields := map[string]interface{}{"event": "bridge_gas", "tx_id": c.TxID, "contract": c.Contract, "method": c.Method, "depth": c.Depth, "when": when, "is_len": isLen, "bridge_seq": c.BridgeSeq, "gas_argument_or_return_cumulative": gas, "parent_remaining_readonly": eRawGas(sc.Instance, sc.Contract.Name)}
	if result != nil {
		fields["callee_result_gas_cumulative"] = result.GasUsed
		fields["callee_code"] = result.Code
		fields["callee_result"] = result.Result
	}
	a23Enrich(sc, fields)
	eEmit(fields)
}
func a23Finish(c *a23Call, result *common.ContractResult, ctx protocol.TxSimContext) {
	w.ManagedAssert()
	if len(a23Stack) == 0 || a23Stack[len(a23Stack)-1] != c {
		panic("diagnostic call stack mismatch")
	}
	c.RWAfter = a23RW(ctx)
	c.Result = result
	c.GasOut = result.GasUsed
	eEmit(map[string]interface{}{"event": "call_record", "record": c, "owner_tid": syscall.Gettid()})
	a23Stack = a23Stack[:len(a23Stack)-1]
}
