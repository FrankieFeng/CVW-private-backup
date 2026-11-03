package wasmer

import (
	"os"
	"sync"
)

const e39bMaxBytes = 64 << 20

var e39bFault = os.Getenv("E39B_FAULT")

type e39bSnapshot struct {
	Entries, Bytes int
	Closed         bool
}

func (g *e39Registry) snapshot() e39bSnapshot {
	g.mu.Lock()
	defer g.mu.Unlock()
	return e39bSnapshot{len(g.entries), g.bytes, g.closed}
}
func (g *e39Registry) clear(closing bool) {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.entries = nil
	g.bytes = 0
	g.closed = g.closed || closing
}
func (g *e39Registry) discard(a *e39Artifact) {
	if a == nil {
		return
	}
	g.mu.Lock()
	defer g.mu.Unlock()
	if g.entries[a.key] == a {
		delete(g.entries, a.key)
		g.bytes -= len(a.raw)
	}
}

type e39bObservation struct {
	TxID, Contract, Mode string
	RID                  uint64
	Costs                []e39Cost
}

var e39bObsMu sync.Mutex
var e39bObs []e39bObservation

func e39bCollect(r *nodeFreshRuntime, tx string) {
	e39bObsMu.Lock()
	defer e39bObsMu.Unlock()
	e39bObs = append(e39bObs, e39bObservation{tx, r.contract.Name, e39Mode, r.rid, r.costs})
}
func e39bDrain() []e39bObservation {
	e39bObsMu.Lock()
	defer e39bObsMu.Unlock()
	r := e39bObs
	e39bObs = nil
	return r
}
