package wasmer

// Local prototype. No exported mutable artifact bytes. The caller must not mutate
// its input concurrently during acquire/Invoke, just as for the original Clone/SHA.
import (
	"bytes"
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"sync"
	"sync/atomic"
	
)

type e39Key struct{ Chain, Config, Name, Version string }
type e39Artifact struct {
	key    e39Key
	raw    []byte
	digest string
}
type e39Registry struct {
	mu      sync.Mutex
	entries map[e39Key]*e39Artifact
}
type e39Cost struct {
	Stage string `json:"stage"`
	NS    int64  `json:"ns"`
	Count int    `json:"count"`
	Bytes int    `json:"bytes"`
}

var e39Mode = os.Getenv("E39_MODE")
var e39Next atomic.Uint64

func e39Emit(x interface{}) {
	b, e := json.Marshal(x)
	if e != nil {
		panic(e)
	}
	fmt.Printf("STEP39 %s\n", b)
}
func (r *nodeFreshRuntime) hash(stage string, b []byte) string {
	
	s := nodeSHA(b)
	
	return s
}
func (g *e39Registry) acquire(chain, config string, c *common.Contract, raw []byte, costs *[]e39Cost) (*e39Artifact, error) {
	
	
	if c == nil || c.Name == "" || c.Version == "" || len(raw) == 0 {
		return nil, errors.New("invalid artifact")
	}
	k := e39Key{chain, config, c.Name, c.Version}
	g.mu.Lock()
	defer g.mu.Unlock()
	if g.entries == nil {
		g.entries = make(map[e39Key]*e39Artifact)
	}
	if a := g.entries[k]; a != nil && bytes.Equal(a.raw, raw) {
		return a, nil
	}
	if _, ok := g.entries[k]; !ok && len(g.entries) >= 8 {
		return nil, errors.New("bounded artifact registry full")
	}
	
	owned := append([]byte(nil), raw...)
	
	
	digest := nodeSHA(owned)
	
	a := &e39Artifact{key: k, raw: owned, digest: digest}
	g.entries[k] = a
	return a, nil
}
