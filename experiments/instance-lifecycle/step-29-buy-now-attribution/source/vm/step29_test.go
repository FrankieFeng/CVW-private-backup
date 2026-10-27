package wasmer

import (
	protocol "chainmaker.org/chainmaker/protocol/v2"
	"encoding/json"
	"fmt"
	"os"
	"time"
)

var e29On = os.Getenv("E29_TRACE") == "1"
var e29Epoch = time.Now()

type e29Span struct {
	Kind     string `json:"kind"`
	Contract string `json:"contract"`
	Method   string `json:"method"`
	Depth    int    `json:"depth"`
	Begin    int64  `json:"begin_ns"`
	End      int64  `json:"end_ns"`
}

var e29Spans = make([]e29Span, 0, 4096)

func e29Start() time.Time {
	if !e29On {
		return time.Time{}
	}
	return time.Now()
}
func e29Times(a, b time.Time, kind, c, m string, d int) {
	if !e29On {
		return
	}
	if len(e29Spans) >= cap(e29Spans) {
		panic("Step29 span bound")
	}
	e29Spans = append(e29Spans, e29Span{kind, c, m, d, a.Sub(e29Epoch).Nanoseconds(), b.Sub(e29Epoch).Nanoseconds()})
}
func e29End(a time.Time, kind, c, m string, d int) {
	if e29On {
		e29Times(a, time.Now(), kind, c, m, d)
	}
}
func e29Flush() {
	if !e29On {
		return
	}
	b, e := json.Marshal(e29Spans)
	if e != nil {
		panic(e)
	}
	fmt.Printf("STEP29 %s\n", b)
}

type e29Logger struct{ protocol.Logger }

func (l e29Logger) Infof(f string, a ...interface{}) {
	s := e29Start()
	l.Logger.Infof(f, a...)
	e29End(s, "manager_logger_infof", "", f, -1)
}
func (l e29Logger) Debugf(f string, a ...interface{}) {
	s := e29Start()
	l.Logger.Debugf(f, a...)
	e29End(s, "manager_logger_debugf", "", f, -1)
}
func (l e29Logger) Warnf(f string, a ...interface{}) {
	s := e29Start()
	l.Logger.Warnf(f, a...)
	e29End(s, "manager_logger_warnf", "", f, -1)
}
func (l e29Logger) Errorf(f string, a ...interface{}) {
	s := e29Start()
	l.Logger.Errorf(f, a...)
	e29End(s, "manager_logger_errorf", "", f, -1)
}
