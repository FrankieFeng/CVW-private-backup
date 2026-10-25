package wasmer

// Host-only readiness probes. Never create an Engine/Store/Instance or execute guest code.
import (
	"encoding/json"
	"fmt"
	"strings"
	"testing"

	"chainmaker.org/chainmaker/common/v2/serialize"
	"chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/vm/v2"
)

func step21ReadinessRow(t *testing.T, row map[string]interface{}) {
	b, err := json.Marshal(row)
	if err != nil {
		t.Fatal(err)
	}
	fmt.Printf("BUYNow_READINESS %s\n", b)
}

func step21CaptureReadinessPanic(f func()) (p interface{}) {
	defer func() { p = recover() }()
	f()
	return nil
}

func TestStep21BuyNowReadiness(t *testing.T) {
	args := map[string][]byte{"from": []byte("8acfaca5eeec9f6f7c23c4ffac969b86f27799b0"), "to": []byte("818fac1ac51525aeedf619a9a339b95854930159"), "tokenId": []byte("1"), "metadata": []byte("http://chainmaker.org.cn/")}
	fillingBaseParams(args)
	tx := prepareTxSimContext(ChainId, BlockVersion, "exchange", "buyNow", args, SnapshotMock{})
	params := serialize.NewEasyCodec()
	params.AddBytes("address", []byte(string(args["from"])+","+string(args["to"])))
	request := serialize.NewEasyCodec()
	request.AddInt32("value_ptr", 0)
	request.AddString("contract_name", "identity")
	request.AddString("method", "addWriteList")
	request.AddBytes("param", params.Marshal())
	saved := protocol.ParametersValueMaxLength
	defer func() { protocol.ParametersValueMaxLength = saved }()
	if saved != 0 {
		t.Fatalf("fixture differs from expected Step21 baseline: limit=%d", saved)
	}
	w := vm.NewWacsi(log, nil)
	_, _, _, err := w.CallContract(&common.Contract{Name: "exchange"}, request.Marshal(), tx, make([]byte, 256), nil, 0, true)
	if err == nil || !strings.Contains(err.Error(), "length less than 0, but got 81") {
		t.Fatalf("unexpected first guard: %v", err)
	}
	step21ReadinessRow(t, map[string]interface{}{"probe": "original_parameter_limit", "limit": saved, "address_bytes": 81, "blocked": true, "error": err.Error()})

	protocol.ParametersValueMaxLength = protocol.DefaultParametersValueMaxSize * 1024 * 1024
	p := step21CaptureReadinessPanic(func() {
		_, _, _, e := w.CallContract(&common.Contract{Name: "exchange"}, request.Marshal(), tx, make([]byte, 256), nil, 0, true)
		if e != nil {
			t.Fatalf("unexpected error after limit restored: %v", e)
		}
	})
	if p == nil {
		t.Fatal("expected SnapshotMock chain-config blocker was absent")
	}
	step21ReadinessRow(t, map[string]interface{}{"probe": "default_limit_then_original_snapshot", "limit": protocol.ParametersValueMaxLength, "blocked": true, "panic": fmt.Sprint(p)})
	for _, name := range []string{"identity", "erc721"} {
		p = step21CaptureReadinessPanic(func() { _, _ = tx.GetContractBytecode(name) })
		if p == nil {
			t.Fatalf("unexpected registered bytecode for %s", name)
		}
		step21ReadinessRow(t, map[string]interface{}{"probe": "original_bytecode_registry", "contract": name, "blocked": true, "panic": fmt.Sprint(p)})
	}
	step21ReadinessRow(t, map[string]interface{}{"probe": "result_scope", "guest_invocations": 0, "performance_samples": 0, "diagnostic_pass_only": true, "full_buynow_ready": false})
}
