package wasmer

// Prepared REAL cross-contract fixture. Compilation only in Step21C.
// All guest entry tests unconditionally skip until the separate Step21B safety decision.
import (
	"bytes"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/sha256"
	"crypto/x509"
	"encoding/hex"
	"encoding/json"
	"encoding/pem"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"testing"
	"time"

	"chainmaker.org/chainmaker/chainconf/v2"
	cmcert "chainmaker.org/chainmaker/common/v2/cert"
	cmcrypto "chainmaker.org/chainmaker/common/v2/crypto"
	"chainmaker.org/chainmaker/common/v2/crypto/asym"
	logger "chainmaker.org/chainmaker/logger/v2"
	ac "chainmaker.org/chainmaker/pb-go/v2/accesscontrol"
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	config "chainmaker.org/chainmaker/pb-go/v2/config"
	"chainmaker.org/chainmaker/pb-go/v2/syscontract"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/vm/v2"
)

// Configuration is versioned separately from any executed performance data.
type s21cArtifact struct{ Contract, Path, SHA256 string }
type s21cManifest struct {
	Artifacts                []s21cArtifact
	InputsFile, InputsSHA256 string
}
type s21cCall struct {
	ID                int     `json:"id"`
	Depth             int     `json:"depth"`
	Contract          string  `json:"contract"`
	Method            string  `json:"method"`
	TxID              string  `json:"tx_id"`
	BeginNS           int64   `json:"begin_ns"`
	EndNS             int64   `json:"end_ns"`
	InvokeSeconds     float64 `json:"invoke_seconds_inclusive"`
	CallMethodSeconds float64 `json:"callmethod_seconds_nested"`
	GasUsed           uint64  `json:"gas_used_actual"`
	Code              uint32  `json:"code"`
	Result            string  `json:"result"`
	Message           string  `json:"message"`
}

type s21cStore struct {
	protocol.BlockchainStore // unexpected/unimplemented node methods fail, never fabricate success
	contracts                map[string]*common.Contract
	code                     map[string][]byte
	cfg                      *config.ChainConfig
}

func (s *s21cStore) GetContractByName(name string) (*common.Contract, error) {
	c, ok := s.contracts[name]
	if !ok {
		return nil, fmt.Errorf("unregistered contract %s", name)
	}
	b, e := c.Marshal()
	if e != nil {
		return nil, e
	}
	clone := &common.Contract{}
	e = clone.Unmarshal(b)
	return clone, e
}
func (s *s21cStore) GetContractBytecode(name string) ([]byte, error) {
	b, ok := s.code[name]
	if !ok {
		return nil, fmt.Errorf("unregistered code %s", name)
	}
	return append([]byte(nil), b...), nil
}
func (s *s21cStore) GetLastChainConfig() (*config.ChainConfig, error) { return s.cfg, nil }

type s21cSnapshot struct {
	SnapshotMock // only unused APIs retain explicit panic; GetKey/config/store below are real
	store        *s21cStore
	ledger       map[string]map[string][]byte
}

func (s *s21cSnapshot) GetBlockchainStore() protocol.BlockchainStore { return s.store }
func (s *s21cSnapshot) GetLastChainConfig() *config.ChainConfig      { return s.store.cfg }
func (s *s21cSnapshot) GetBlockHeight() uint64                       { return 111 }
func (s *s21cSnapshot) GetKey(_ int, name string, key []byte) ([]byte, error) {
	return append([]byte(nil), s.ledger[name][string(key)]...), nil
}
func (s *s21cSnapshot) hash() string {
	b, _ := json.Marshal(s.ledger)
	h := sha256.Sum256(b)
	return hex.EncodeToString(h[:])
}
func (s *s21cSnapshot) commit(rw *common.TxRWSet) {
	for _, w := range rw.TxWrites {
		if s.ledger[w.ContractName] == nil {
			s.ledger[w.ContractName] = map[string][]byte{}
		}
		if w.Value == nil {
			delete(s.ledger[w.ContractName], string(w.Key))
		} else {
			s.ledger[w.ContractName][string(w.Key)] = append([]byte(nil), w.Value...)
		}
	}
}

// Restricted public identity fixture, NOT a node authentication substitute.
// NewMember validates the configured key and derives its UID; no business result is returned here.
type s21cMember struct {
	member *ac.Member
	pk     cmcrypto.PublicKey
	uid    string
}

func (m *s21cMember) GetMemberId() string            { return m.uid }
func (m *s21cMember) GetOrgId() string               { return m.member.OrgId }
func (m *s21cMember) GetRole() protocol.Role         { return protocol.Role("CLIENT") }
func (m *s21cMember) GetUid() string                 { return m.uid }
func (m *s21cMember) GetPk() cmcrypto.PublicKey      { return m.pk }
func (m *s21cMember) GetMember() (*ac.Member, error) { return m.member, nil }
func (m *s21cMember) Verify(_ string, _ []byte, _ []byte) error {
	return errors.New("Step21C fixture does not authenticate node transaction signatures")
}

type s21cAC struct {
	protocol.AccessControlProvider
	member *s21cMember
}

func (a *s21cAC) GetHashAlg() string { return "SHA256" }
func (a *s21cAC) NewMember(m *ac.Member) (protocol.Member, error) {
	if m == nil || m.MemberType != ac.MemberType_PUBLIC_KEY || m.OrgId != a.member.member.OrgId || !bytes.Equal(m.MemberInfo, a.member.member.MemberInfo) {
		return nil, errors.New("identity not registered in Step21C fixture")
	}
	return a.member, nil
}
func (a *s21cAC) VerifyTxPrincipal(_ *common.Transaction, _ string, _ uint32) (bool, error) {
	return false, errors.New("node ACL policy verification is outside this BlockVersion=1 VM fixture")
}

type s21cFixture struct {
	t         *testing.T
	snapshot  *s21cSnapshot
	manager   protocol.VmManager
	instances *InstancesManager
	member    *s21cMember
	calls     []s21cCall
	nextID    int
	output    string
}

// This adapter observes actual RuntimeInstance.InvokeTime; it never manufactures a callee result.
type s21cObservedManager struct {
	protocol.VmInstancesManager
	actual  *InstancesManager
	fixture *s21cFixture
}

func (m *s21cObservedManager) NewRuntimeInstance(ctx protocol.TxSimContext, chain, method, path string, c *common.Contract, code []byte, log protocol.Logger) (protocol.RuntimeInstance, error) {
	r, e := m.actual.NewRuntimeInstance(ctx, chain, method, path, c, code, log)
	if e != nil {
		return nil, e
	}
	actual, ok := r.(*RuntimeInstance)
	if !ok {
		return nil, errors.New("unexpected real runtime type")
	}
	return &s21cObservedRuntime{actual: actual, fixture: m.fixture}, nil
}

type s21cObservedRuntime struct {
	actual  *RuntimeInstance
	fixture *s21cFixture
}

func (r *s21cObservedRuntime) Invoke(c *common.Contract, method string, code []byte, params map[string][]byte, ctx protocol.TxSimContext, gas uint64) (*common.ContractResult, protocol.ExecOrderTxType) {
	f := r.fixture
	id := f.nextID
	f.nextID++
	depth := ctx.GetDepth()
	s21cEmit(map[string]interface{}{"event": "invoke_enter", "id": id, "contract": c.Name, "method": method, "depth": depth, "tx_id": ctx.GetTx().Payload.TxId})
	result, order, begin, end, total, call := r.actual.InvokeTime(c, method, code, params, ctx, gas)
	row := s21cCall{ID: id, Depth: depth, Contract: c.Name, Method: method, TxID: ctx.GetTx().Payload.TxId, BeginNS: begin, EndNS: end, InvokeSeconds: total, CallMethodSeconds: call, GasUsed: result.GasUsed, Code: result.Code, Result: string(result.Result), Message: result.Message}
	f.calls = append(f.calls, row)
	s21cEmit(map[string]interface{}{"event": "invoke_return", "call": row})
	return result, order
}
func s21cEmit(row interface{}) {
	b, e := json.Marshal(row)
	if e != nil {
		panic(e)
	}
	fmt.Printf("STEP21C %s\n", b)
}

func s21cPrepare(t *testing.T, manifestPath, output string) *s21cFixture {
	t.Helper()
	// Required parent observer is detection, not a Store execution lock. It remains enabled.
	if !step21aGuardEnabled || !step21Enabled {
		t.Fatal("Step21A observations/guard must remain enabled")
	}
	data, e := os.ReadFile(manifestPath)
	if e != nil {
		t.Fatal(e)
	}
	var manifest s21cManifest
	if e = json.Unmarshal(data, &manifest); e != nil {
		t.Fatal(e)
	}
	// Public P-256 generator point. No private key, signing material or certificate is generated/written.
	curve := elliptic.P256()
	der, e := x509.MarshalPKIXPublicKey(&ecdsa.PublicKey{Curve: curve, X: curve.Params().Gx, Y: curve.Params().Gy})
	if e != nil {
		t.Fatal(e)
	}
	pubPEM := pem.EncodeToMemory(&pem.Block{Type: "PUBLIC KEY", Bytes: der})
	pk, e := asym.PublicKeyFromPEM(pubPEM)
	if e != nil {
		t.Fatal(e)
	}
	ski, e := cmcert.ComputeSKI(cmcrypto.HASH_TYPE_SHA256, pk.ToStandardKey())
	if e != nil {
		t.Fatal(e)
	}
	member := &s21cMember{member: &ac.Member{OrgId: "step21c-fixture-org", MemberType: ac.MemberType_PUBLIC_KEY, MemberInfo: pubPEM}, pk: pk, uid: hex.EncodeToString(ski)}
	cfg := &config.ChainConfig{ChainId: ChainId, Contract: &config.ContractConfig{EnableSqlSupport: false}, Vm: &config.Vm{AddrType: config.AddrType_CHAINMAKER}, Crypto: &config.CryptoConfig{Hash: "SHA256"}}
	store := &s21cStore{contracts: map[string]*common.Contract{}, code: map[string][]byte{}, cfg: cfg}
	for _, a := range manifest.Artifacts {
		b, err := os.ReadFile(a.Path)
		if err != nil {
			t.Fatal(err)
		}
		h := sha256.Sum256(b)
		if hex.EncodeToString(h[:]) != a.SHA256 {
			t.Fatal("changed WASM " + a.Contract)
		}
		if a.Contract != "exchange" && a.Contract != "identity" && a.Contract != "erc721" {
			t.Fatal("unexpected registered contract")
		}
		store.code[a.Contract] = b
		store.contracts[a.Contract] = &common.Contract{Name: a.Contract, Version: "1.0.0", RuntimeType: common.RuntimeType_WASMER, Status: common.ContractStatus_NORMAL, Creator: &ac.MemberFull{OrgId: member.member.OrgId, MemberType: ac.MemberType_PUBLIC_KEY, MemberInfo: pubPEM, MemberId: member.uid, Role: "CLIENT", Uid: member.uid}}
	}
	if len(store.contracts) != 3 {
		t.Fatal("three actual WASM contracts required")
	}
	snap := &s21cSnapshot{store: store, ledger: map[string]map[string][]byte{}}
	cfgBytes, e := cfg.Marshal()
	if e != nil {
		t.Fatal(e)
	}
	// Configuration state is supplied as node context, not a fabricated business write.
	snap.ledger[syscontract.SystemContract_CHAIN_CONFIG.String()] = map[string][]byte{syscontract.SystemContract_CHAIN_CONFIG.String(): cfgBytes}
	base := NewInstancesManager(ChainId)
	f := &s21cFixture{t: t, snapshot: snap, instances: base, member: member, output: output}
	observed := &s21cObservedManager{VmInstancesManager: base, actual: base, fixture: f}
	f.manager = vm.NewVmManager(map[common.RuntimeType]protocol.VmInstancesManager{common.RuntimeType_WASMER: observed}, "", &s21cAC{member: member}, nil, &chainconf.ChainConf{ChainConf: cfg}, logger.GetLogger("step21c-real-fixture"))
	previous := protocol.ParametersValueMaxLength
	protocol.ParametersValueMaxLength = protocol.DefaultParametersValueMaxSize * 1024 * 1024
	t.Cleanup(func() { protocol.ParametersValueMaxLength = previous })
	return f
}

type s21cReceipt struct {
	Label             string                 `json:"label"`
	TxID              string                 `json:"tx_id"`
	Contract          string                 `json:"contract"`
	Method            string                 `json:"method"`
	Input             map[string]string      `json:"business_input"`
	BeforeHash        string                 `json:"before_hash"`
	AfterHash         string                 `json:"after_hash"`
	RunContractWallNS int64                  `json:"runcontract_wall_ns_not_primary_metric"`
	Status            common.TxStatusCode    `json:"status"`
	Result            *common.ContractResult `json:"actual_result"`
	RWSet             *common.TxRWSet        `json:"actual_rwset"`
	Calls             []s21cCall             `json:"inclusive_call_records_do_not_sum"`
}

func (f *s21cFixture) run(label, contract, method, txID string, input map[string]string) *s21cReceipt {
	t := f.t
	t.Helper()
	meta, e := f.snapshot.store.GetContractByName(contract)
	if e != nil {
		t.Fatal(e)
	}
	code, e := f.snapshot.store.GetContractBytecode(contract)
	if e != nil {
		t.Fatal(e)
	}
	params := map[string][]byte{}
	kv := []*common.KeyValuePair{}
	keys := make([]string, 0, len(input))
	for k := range input {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		params[k] = []byte(input[k])
		kv = append(kv, &common.KeyValuePair{Key: k, Value: []byte(input[k])})
	}
	tx := &common.Transaction{Payload: &common.Payload{ChainId: ChainId, TxType: common.TxType_INVOKE_CONTRACT, TxId: txID, Timestamp: 1700000000, ContractName: contract, Method: method, Parameters: kv}, Sender: &common.EndorsementEntry{Signer: f.member.member}}
	ctx := vm.NewTxSimContext(f.manager, f.snapshot, tx, BlockVersion, logger.GetLogger("step21c-real-fixture"))
	f.calls = nil
	f.nextID = 0
	before := f.snapshot.hash()
	begin := time.Now()
	result, _, status := f.manager.RunContract(meta, method, code, params, ctx, 0, common.TxType_INVOKE_CONTRACT)
	wall := time.Since(begin).Nanoseconds()
	rw := ctx.GetTxRWSet(result.Code == 0 && status == common.TxStatusCode_SUCCESS)
	if result.Code == 0 && status == common.TxStatusCode_SUCCESS {
		f.snapshot.commit(rw)
	}
	r := &s21cReceipt{Label: label, TxID: txID, Contract: contract, Method: method, Input: input, BeforeHash: before, AfterHash: f.snapshot.hash(), RunContractWallNS: wall, Status: status, Result: result, RWSet: rw, Calls: append([]s21cCall(nil), f.calls...)}
	b, e := json.MarshalIndent(r, "", "  ")
	if e != nil {
		t.Fatal(e)
	}
	if e = os.MkdirAll(f.output, 0755); e != nil {
		t.Fatal(e)
	}
	if e = os.WriteFile(filepath.Join(f.output, label+".json"), append(b, '\n'), 0644); e != nil {
		t.Fatal(e)
	}
	return r
}
func (f *s21cFixture) state(contract, key, field string) string {
	return string(f.snapshot.ledger[contract][string(protocol.GetKeyStr(key, field))])
}
func (f *s21cFixture) close() {
	// Post-scenario drain is cleanup only. It does not protect successive child calls in one root.
	names := []string{}
	for name := range f.snapshot.store.contracts {
		names = append(names, name)
	}
	sort.Strings(names)
	for _, name := range names {
		if p := f.instances.instanceMap[name+"_1.0.0"]; p != nil {
			step21ClosePool(f.t, p)
		}
	}
}

// Compiled assertions to be enabled only after independent Step21B review, not in this task.
func s21cPreparedScenario(t *testing.T, manifest, output string) {
	f := s21cPrepare(t, manifest, output)
	defer f.close()
	for _, name := range []string{"identity", "erc721", "exchange"} {
		args := map[string]string{}
		// Explicit admin parameter avoids depending on caller-address defaults; actual guest decides state.
		if name == "identity" {
			args["adminAddress"] = "8acfaca5eeec9f6f7c23c4ffac969b86f27799b0"
		}
		if name == "erc721" {
			args = map[string]string{"name": "Step21C", "symbol": "S21C", "tokenURI": "http://chainmaker.org.cn/"}
		}
		r := f.run("init-"+name, name, "init_contract", "step21c-init-"+name, args)
		if r.Result.Code != 0 || r.Status != common.TxStatusCode_SUCCESS {
			t.Fatalf("real init failed %s: %s", name, r.Result.Message)
		}
	}
	data, e := os.ReadFile(manifest)
	if e != nil {
		t.Fatal(e)
	}
	var m s21cManifest
	if e = json.Unmarshal(data, &m); e != nil {
		t.Fatal(e)
	}
	inputsBytes, e := os.ReadFile(m.InputsFile)
	if e != nil {
		t.Fatal(e)
	}
	h := sha256.Sum256(inputsBytes)
	if hex.EncodeToString(h[:]) != m.InputsSHA256 {
		t.Fatal("changed frozen inputs")
	}
	var inputs []map[string]string
	if e = json.Unmarshal(inputsBytes, &inputs); e != nil || len(inputs) < 3 {
		t.Fatal("missing input sequence")
	}
	expected := []string{"identity/addWriteList", "identity/isApprovedUser", "identity/isApprovedUser", "erc721/mint", "erc721/setApprovalForAll2", "erc721/transferFrom"}
	for i := 0; i < 3; i++ {
		in := inputs[i]
		r := f.run(fmt.Sprintf("success-%d", i+1), "exchange", "buyNow", fmt.Sprintf("step21c-buy-%03d", i+1), in)
		if r.Result.Code != 0 || string(r.Result.Result) != "buyNow success" || r.Status != common.TxStatusCode_SUCCESS {
			t.Fatalf("full real buyNow failed: %s", r.Result.Message)
		}
		calls := append([]s21cCall(nil), r.Calls...)
		sort.Slice(calls, func(i, j int) bool { return calls[i].ID < calls[j].ID })
		if len(calls) != 7 || calls[0].Depth != 0 {
			t.Fatal("unexpected root/callee count")
		}
		for j, c := range calls[1:] {
			if c.Contract+"/"+c.Method != expected[j] || c.Depth != 1 || c.Code != 0 {
				t.Fatal("actual callee path/result mismatch")
			}
		}
		if f.state("identity", "identity", in["from"]) != "1" || f.state("identity", "identity", in["to"]) != "1" {
			t.Fatal("whitelist state missing")
		}
		if f.state("erc721", "tokenIds", in["tokenId"]) != in["to"] {
			t.Fatal("owner did not transfer")
		}
		if f.state("erc721", "operatorApprove", in["from"]+"_"+f.member.uid) != "1" {
			t.Fatal("operator approval missing")
		}
		found := false
		for _, event := range r.Result.ContractEvent {
			if event.Topic == "buyNow" && event.ContractName == "exchange" {
				found = true
			}
		}
		if !found {
			t.Fatal("actual buyNow event missing")
		}
	}
	// Duplicate token and invalid input must not be committed. No fabricated rollback response.
	bad := f.run("negative-duplicate", "exchange", "buyNow", "step21c-negative-duplicate", inputs[0])
	if bad.Result.Code == 0 || bad.BeforeHash != bad.AfterHash || len(bad.RWSet.TxWrites) != 0 {
		t.Fatal("duplicate-token error or rollback differs")
	}
	invalid := map[string]string{}
	for k, v := range inputs[0] {
		invalid[k] = v
	}
	invalid["from"] = "bad"
	bad = f.run("negative-address", "exchange", "buyNow", "step21c-negative-address", invalid)
	if bad.Result.Code == 0 || bad.BeforeHash != bad.AfterHash || len(bad.RWSet.TxWrites) != 0 {
		t.Fatal("invalid-address error or rollback differs")
	}
}

func TestStep21CRealCrossContractPrepared(t *testing.T) {
	t.Skip("Step21C static preparation only: Step21B Store/lifecycle safety has not been established; no guest execution or formal load authorized")
	// Kept type-checked but unreachable until the independent safety decision changes this test.
	s21cPreparedScenario(t, "step21c-manifest.json", "step21c-receipts")
}
