package main

import (
	"bufio"
	pb "chainmaker.org/chainmaker/pb-go/v2/common"
	sdk "chainmaker.org/chainmaker/sdk-go/v2"
	sdkutils "chainmaker.org/chainmaker/sdk-go/v2/utils"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"sort"
 "strings"
	"time"
)

type Job struct {
	Op, Contract, Method, Tag, Path, TxID, Phase, Version string
	Params                                       map[string]string
}
type Prepared struct {
	J  Job
	KV []*pb.KeyValuePair
}

func main() {
	cc, e := sdk.NewChainClient(sdk.WithConfPath(os.Getenv("STEP17_ROOT") + "/network/baseline/sdk.yml"))
	if e != nil {
		panic(e)
	}
	defer cc.Stop()
	epoch := time.Now()
	scan := bufio.NewScanner(os.Stdin)
	scan.Buffer(make([]byte, 4096), 24*1024*1024)
	for scan.Scan() {
		var jobs []Job
		if e = json.Unmarshal(scan.Bytes(), &jobs); e != nil {
			panic(e)
		}
		prepared := make([]Prepared, len(jobs))
		for i, j := range jobs {
			if j.TxID == "" {
				var b [32]byte
				if _, e = rand.Read(b[:]); e != nil {
					panic(e)
				}
				j.TxID = hex.EncodeToString(b[:])
			}
			keys := []string{}
			for k := range j.Params {
				keys = append(keys, k)
			}
			sort.Strings(keys)
			kv := []*pb.KeyValuePair{}
			for _, k := range keys {
				kv = append(kv, &pb.KeyValuePair{Key: k, Value: []byte(j.Params[k])})
			}
			prepared[i] = Prepared{j, kv}
		}
		rows := []map[string]interface{}{}
		var first, last int64
		success := 0
		for _, p := range prepared {
			j := p.J
			r := map[string]interface{}{"input": j, "request_id": os.Getenv("STEP36_REQUEST_NAMESPACE")+"/"+j.TxID}
			var resp *pb.TxResponse
			var info interface{}
			var err error
			begin := time.Now()
			t0 := begin.Sub(epoch).Nanoseconds()
			if j.Op == "rwset" {
				info, err = cc.GetTxWithRWSetByTxId(j.Path)
			} else if j.Op == "deploy" || j.Op=="upgrade" {
				var payload *pb.Payload
				if j.Op=="upgrade"{payload,err=cc.CreateContractUpgradePayload(j.Contract,j.Version,j.Path,pb.RuntimeType_WASMER,p.KV)}else{payload, err = cc.CreateContractCreatePayload(j.Contract, "1.0.0", j.Path, pb.RuntimeType_WASMER, p.KV)}
				if err == nil {
					var en *pb.EndorsementEntry
					base := os.Getenv("STEP17_ADMIN")
					en, err = sdkutils.MakeEndorserWithPath(base+".sign.key", base+".sign.crt", payload)
					if err == nil {
						endorsers:=[]*pb.EndorsementEntry{en}
 if j.Op=="upgrade" {endorsers=nil;paths:=strings.Split(os.Getenv("STEP39C_UPGRADE_ADMINS"),",");if len(paths)!=3{err=fmt.Errorf("upgrade requires3 configured development admin paths")}else{for _,base:=range paths{var item *pb.EndorsementEntry;item,err=sdkutils.MakeEndorserWithPath(base+".sign.key",base+".sign.crt",payload);if err!=nil{break};endorsers=append(endorsers,item)}}}
 if err==nil{resp, err = cc.SendContractManageRequest(payload, endorsers, 60, true)}
					}
				}
			} else if j.Op == "query" {
				resp, err = cc.QueryContract(j.Contract, j.Method, p.KV, 60)
			} else {
				resp, err = cc.InvokeContract(j.Contract, j.Method, j.TxID, p.KV, 60, true)
			}
			end := time.Now()
			t1 := end.Sub(epoch).Nanoseconds()
			r["sdk_start_mono_ns"] = t0
			r["sdk_end_mono_ns"] = t1
			r["sdk_start_wall_ns"] = begin.UnixNano()
			r["sdk_end_wall_ns"] = end.UnixNano()
			r["elapsed_ns"] = end.Sub(begin).Nanoseconds()
			r["response"] = resp
			r["transaction"] = info
			if err != nil {
				r["error"] = err.Error()
			}
			ok := err == nil && ((info != nil) || (resp != nil && resp.Code == 0 && (resp.ContractResult == nil || resp.ContractResult.Code == 0)))
			r["success"] = ok
			rows = append(rows, r)
			if first == 0 {
				first = t0
			}
			last = t1
			if ok {
				success++
			} else {
				break
			}
		}
		b, _ := json.Marshal(map[string]interface{}{"rows": rows, "window_start_mono_ns": first, "window_end_mono_ns": last, "window_ns": last - first, "attempted": len(rows), "planned": len(jobs), "successful_responses": success, "serial": true})
		fmt.Printf("RESULT %s\n", b)
	}
	if scan.Err() != nil {
		panic(scan.Err())
	}
}
