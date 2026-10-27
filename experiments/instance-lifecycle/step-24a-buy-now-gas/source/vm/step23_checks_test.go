package wasmer

import (
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	"encoding/json"
	"os"
	"sort"
	"testing"
)

func TestStep23BuyNow(t *testing.T) {
	if !e22Enabled {
		t.Fatal("explicit cached serial path required")
	}
	condition := os.Getenv("E23_CONDITION")
	if condition != "R0" && condition != "R1" && condition != "C1" {
		t.Fatal("unregistered condition")
	}
	if os.Getenv("D_POLICY") != "R1" && condition != "R0" {
		t.Fatal("Fresh policy mismatch")
	}
	defer dOwner(t)()
	var inputs struct {
		RootTxID  string            `json:"root_tx_id"`
		RootInput map[string]string `json:"root_input"`
		Initial   string            `json:"expected_initial_hash"`
		Final     string            `json:"expected_final_hash"`
	}
	b, e := os.ReadFile(os.Getenv("E23_INPUTS"))
	if e != nil {
		t.Fatal(e)
	}
	if json.Unmarshal(b, &inputs) != nil {
		t.Fatal("invalid frozen input")
	}
	f := s21cPrepare(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
	defer f.close()
	m := f.instances
	for _, n := range []string{"identity", "erc721", "exchange"} {
		c, _ := f.snapshot.store.GetContractByName(n)
		code, _ := f.snapshot.store.GetContractBytecode(n)
		if e = m.e22Prepare(c, code); e != nil {
			t.Fatal(e)
		}
	}
	m.e22.variant = "A0"
	if condition == "C1" {
		m.e22.variant = "A1"
	}
	m.e22.validate = true // Gas diagnosis only, never used as a performance sample.
	for _, n := range []string{"identity", "erc721", "exchange"} {
		args := map[string]string{}
		if n == "erc721" {
			args = map[string]string{"name": "huanletoken", "symbol": "hlt", "tokenURI": "https://chainmaker.org.cn"}
		}
		a23LedgerBefore = f.snapshot.hash()
		r := f.run("init-"+n, n, "init_contract", "step21c-init-"+n, args)
		if r.Result.Code != 0 || r.Status != common.TxStatusCode_SUCCESS {
			t.Fatalf("actual init failed %+v", r.Result)
		}
	}
	a23LedgerBefore = f.snapshot.hash()
	if a23LedgerBefore != inputs.Initial {
		t.Fatalf("initial ledger differs: %s", a23LedgerBefore)
	}
	r := f.run("target", "exchange", "buyNow", inputs.RootTxID, inputs.RootInput)
	if r.Result.Code != 0 || r.Status != common.TxStatusCode_SUCCESS || string(r.Result.Result) != "buyNow success" {
		t.Fatalf("actual root failed %+v", r.Result)
	}
	if r.BeforeHash != inputs.Initial || r.AfterHash != inputs.Final {
		t.Fatalf("business ledger differs %s %s", r.BeforeHash, r.AfterHash)
	}
	if f.state("erc721", "tokenIds", inputs.RootInput["tokenId"]) != inputs.RootInput["to"] {
		t.Fatal("owner did not transfer")
	}
	if f.state("identity", "identity", inputs.RootInput["from"]) != "1" || f.state("identity", "identity", inputs.RootInput["to"]) != "1" {
		t.Fatal("whitelist missing")
	}
	if f.state("erc721", "operatorApprove", inputs.RootInput["from"]+"_"+f.member.uid) != "1" {
		t.Fatal("operator approval missing")
	}
	expected := []string{"exchange/buyNow", "identity/addWriteList", "identity/isApprovedUser", "identity/isApprovedUser", "erc721/mint", "erc721/setApprovalForAll2", "erc721/transferFrom"}
	calls := append([]s21cCall(nil), r.Calls...)
	sort.Slice(calls, func(i, j int) bool { return calls[i].ID < calls[j].ID })
	if len(calls) != 7 {
		t.Fatal("root plus six real calls required")
	}
	for i, c := range calls {
		if c.ID != i || c.Contract+"/"+c.Method != expected[i] || c.Code != 0 || i > 0 && c.Depth != 1 {
			t.Fatal("real call graph/result differs")
		}
	}
	if len(a23Stack) != 0 || len(a23Calls) != 0 || len(eActive) != 0 {
		t.Fatal("observer stack not empty")
	}
	dEvent("boundary", map[string]interface{}{"condition": condition, "root_gas": r.Result.GasUsed})
	eEmit(map[string]interface{}{"event": "root_checked", "condition": condition, "gas": r.Result.GasUsed, "before": r.BeforeHash, "after": r.AfterHash, "real_child_count": 6, "table_function_identity": "not_tested", "exception_paths": "not_tested", "S1_memory_checked_on_each_creation": true})
}
