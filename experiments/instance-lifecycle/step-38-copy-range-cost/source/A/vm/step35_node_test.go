package wasmer

import (
	common "chainmaker.org/chainmaker/pb-go/v2/common"
	vm "chainmaker.org/chainmaker/vm/v2"
	"context"
	"os"
	"testing"
	"time"
)

func TestStep35Manager(t *testing.T) {
	f := s21cPrepare(t, os.Getenv("D_MANIFEST"), os.Getenv("D_OUTPUT"))
	m := NewInstancesManager(ChainId)
	if m.safeErr != nil || m.safe == nil {
		t.Fatalf("manager: %v", m.safeErr)
	}
	f.manager.(*vm.VmManagerImpl).InstanceManagers[common.RuntimeType_WASMER] = m
	defer func() {
		if e := m.StopVM(); e != nil {
			t.Error(e)
		}
	}()
	name := os.Getenv("E22_CONTRACT")
	names := []string{name}
	if name == "exchange" {
		names = []string{"identity", "erc721", "exchange"}
	}
	for _, c := range names {
		args := map[string]string{}
		if c == "erc721" {
			args = map[string]string{"name": "huanletoken", "symbol": "hlt", "tokenURI": "https://chainmaker.org.cn"}
		}
		r := f.run("init-"+c, c, "init_contract", "step35-init-"+c, args)
		if r.Result.Code != 0 || r.Status != 0 {
			t.Fatalf("init %s %+v", c, r.Result)
		}
	}
	method := map[string]string{"compute": "bigNumCal", "fact": "saveAndFindByFileHash", "erc721": "mint", "exchange": "buyNow"}[name]
	p := map[string]string{}
	switch name {
	case "fact":
		p = map[string]string{"file_hash": "005521f27d745a04999c6d09f559764f9c44376a", "file_name": "aoteman.jpg", "time": "1792827547"}
	case "erc721":
		p = map[string]string{"to": "8acfaca5eeec9f6f7c23c4ffac969b86f27799b0", "tokenId": "1", "metadata": "http://chainmaker.org.cn/"}
	case "exchange":
		p = map[string]string{"from": "8acfaca5eeec9f6f7c23c4ffac969b86f27799b0", "to": "818fac1ac51525aeedf619a9a339b95854930159", "tokenId": "1", "metadata": "http://chainmaker.org.cn/"}
	}
	initial := e22Clone(f.snapshot.ledger)
	r := f.run("target", name, method, "step35-target", p)
	if r.Result.Code != 0 || r.Status != 0 {
		t.Fatalf("target: %+v", r.Result)
	}
	if name == "exchange" {
		if string(r.Result.Result) != "buyNow success" || f.state("erc721", "tokenIds", p["tokenId"]) != p["to"] {
			t.Fatal("buyNow state")
		}
	} else {
		e22Expected(t, f, name, p, r)
	}
	f.snapshot.ledger = e22Clone(initial)
	m.ResetAllPool()
	r2 := f.run("after-reset", name, method, "step35-target", p)
	if r.Result.GasUsed != r2.Result.GasUsed || r2.Result.Code != 0 || r.AfterHash != r2.AfterHash {
		t.Fatalf("reset changed semantics %+v %+v", r.Result, r2.Result)
	}
	before := f.snapshot.hash()
	bad := f.run("missing", name, "step35_missing", "step35-missing", map[string]string{})
	if bad.Result.Code == 0 || bad.AfterHash != before {
		t.Fatal("missing method rollback")
	}
	// Exercise actual StopVM while an accepted Owner operation is in flight using channels, no sleeps.
	entered, release := make(chan struct{}), make(chan struct{})
	job := make(chan error, 1)
	go func() {
		job <- m.safe.owner.Do(context.Background(), func() error { close(entered); <-release; return nil })
	}()
	<-entered
	stopped := make(chan error, 1)
	go func() { stopped <- m.StopVM() }()
	select {
	case e := <-stopped:
		t.Fatalf("stop returned before in-flight completion: %v", e)
	default:
	}
	close(release)
	if e := <-job; e != nil {
		t.Fatal(e)
	}
	select {
	case e := <-stopped:
		if e != nil {
			t.Fatal(e)
		}
	case <-time.After(5 * time.Second):
		t.Fatal("stop timeout")
	}
	if e := m.StopVM(); e != nil {
		t.Fatal(e)
	}
}

func TestStep35Admission(t *testing.T) {
	t.Setenv("CM_SAFE_FRESH_NODE", "0")
	m0 := NewInstancesManager(ChainId)
	if m0.StartVM() == nil {
		t.Fatal("legacy unmanaged path admitted")
	}
	t.Setenv("CM_SAFE_FRESH_NODE", "1")
	t.Setenv("CM_SAFE_FRESH_CONFIG", "")
	m := NewInstancesManager(ChainId)
	if m.StartVM() == nil {
		t.Fatal("missing config accepted")
	}
	t.Setenv("CM_SAFE_FRESH_CONFIG", "test")
	t.Setenv("CM_REUSE_EXPERIMENT", "R0")
	m = NewInstancesManager(ChainId)
	if m.StartVM() == nil {
		t.Fatal("R0 accepted")
	}
}
