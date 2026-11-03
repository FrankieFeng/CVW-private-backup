package wasmer

import "chainmaker.org/chainmaker/protocol/v2"

const ChainId = "chain02"
const BlockVersion = uint32(1)

type SnapshotMock struct{ protocol.Snapshot }


// Empty serial snapshot has no other already-executed transactions in its block.
func (SnapshotMock) GetSnapshotSize() int { return 0 }
