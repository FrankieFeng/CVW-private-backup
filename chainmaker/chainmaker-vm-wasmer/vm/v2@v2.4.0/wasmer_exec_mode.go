package vm

import "chainmaker.org/chainmaker/protocol/v2"

// 本文件把调度器的出块/重放角色传给 Wasmer，用来选择新建或复用实例。
const (
	// WasmerExecDefault keeps the contract install option and CM_WASMER_FORCE_NO_REUSE.
	WasmerExecDefault int32 = 0
	// WasmerExecProposeNoReuse is kept for older call sites.
	// Proposer and verifier both reuse pooled instances.
	WasmerExecProposeNoReuse int32 = 1
	// WasmerExecReplayReuse reuses a pooled instance.
	WasmerExecReplayReuse int32 = 2
	// WasmerExecForceFresh runs one transaction on a newly created instance.
	WasmerExecForceFresh int32 = 3
	// WasmerMaxInstanceUse discards a pooled instance after this many executions.
	WasmerMaxInstanceUse int32 = 50
)

// SetWasmerExecMode records how this transaction should obtain a wasmer instance.
func SetWasmerExecMode(ctx protocol.TxSimContext, mode int32) {
	sim, ok := ctx.(*txSimContextImpl)
	if !ok || sim == nil {
		return
	}
	sim.wasmerExecMode = mode
}

// GetWasmerExecMode is read by the wasmer runtime through a type assertion.
func (s *txSimContextImpl) GetWasmerExecMode() int32 {
	if s == nil {
		return WasmerExecDefault
	}
	return s.wasmerExecMode
}

// RunOnWarmupScratch runs fn on a new sim context that shares this transaction's
// snapshot and tx, with an empty read/write set. Writes made by fn are discarded.
func (s *txSimContextImpl) RunOnWarmupScratch(fn func(protocol.TxSimContext)) {
	if s == nil || fn == nil || s.snapshot == nil {
		return
	}
	scratch := NewTxSimContext(s.vmManager, s.snapshot, s.tx, s.blockVersion, s.logger)
	if impl, ok := scratch.(*txSimContextImpl); ok && impl != nil {
		impl.wasmerExecMode = s.wasmerExecMode
	}
	fn(scratch)
}
