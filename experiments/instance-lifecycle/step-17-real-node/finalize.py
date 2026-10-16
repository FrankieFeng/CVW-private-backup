from pathlib import Path
import json,hashlib,subprocess,shutil,platform,sys,collections,csv
O=Path(__file__).resolve().parent;R=Path('/home/frankie/mygitprojects');CV=R/'.worktrees/cvw-step17';N=R/'.worktrees/node-step17';VM=CV/'chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0';sha=lambda b:hashlib.sha256(b).hexdigest()
def git(d,*args):return subprocess.check_output(['git',*args],cwd=d)
# Prove original tracked workspaces were not modified by this experiment.
for name in ['CVW','chainmaker-go']:
 assert git(R/name,'diff','--binary')==(O/(name+'-before.patch')).read_bytes(),name
proto=O/'prototype';proto.mkdir(exist_ok=True)
files=['runtime.go','static_init_copy.go','vm_instances_manager.go','vm_pool.go','step17_node.go','step17_safety_test.go','step17_audit_test.go','step17_cache_key_test.go']
for f in files:shutil.copy2(VM/f,proto/f)
shutil.copy2(N/'experiment/step17client/main.go',proto/'client-verify.go')
s=(proto/'client-verify.go').read_text();s=s.replace(' if j.Op=="rwset" {info,err:=cc.GetTxWithRWSetByTxId(j.Path);row["elapsed_ns"]=time.Since(begin).Nanoseconds();row["transaction"]=info;if err!=nil{row["error"]=err.Error()};return row};','')
(proto/'client-benchmark.go').write_text(s)
(O/'prototype.patch').write_bytes(git(CV,'diff','--binary','4cdf6c51df36f3ff350baf120863edc893da7383','HEAD','--','chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'))
(O/'node-workspace.patch').write_bytes(git(N,'diff','--binary','86894c25c12cd633568c5fbe839ecaf16d7e3312','HEAD'))
branches={}
for name,d in [('cvw',CV),('node',N)]:branches[name]={'worktree':str(d),'head':git(d,'rev-parse','HEAD').decode().strip(),'branch':git(d,'branch','--show-current').decode().strip(),'clean':not git(d,'status','--porcelain').strip()}
(O/'branches.json').write_text(json.dumps(branches,indent=2)+'\n')
source={str(VM/f):sha((VM/f).read_bytes()) for f in files};source[str(N/'go.mod')]=sha((N/'go.mod').read_bytes());source[str(N/'go.sum')]=sha((N/'go.sum').read_bytes());source[str(N/'experiment/step17client/main.go')]=sha((N/'experiment/step17client/main.go').read_bytes());(O/'source_hashes.json').write_text(json.dumps(source,indent=2)+'\n')
raw=O/'raw';raw.mkdir(exist_ok=True)
for m in ['baseline','optimized']:shutil.copy2(O/'network'/m/'stdout.log',raw/(m+'-node.log'))
# Final status includes explicit failed/not-tested coverage, never inferred pass.
v=json.loads((O/'verification.json').read_text());v.update(original_tracked_workspaces_unchanged=True,production_nodes_modified=False,experiment_nodes_stopped=True,full_node_race='not_passed_storage_startup_races_prevent_business_coverage',full_node_race_details=['store/bloom ReadFrom checkptr','RollingWindowCacher.ResetRWCache recovery race','RollingWindowCacher.ResetRWCache InitGenesis fresh-ledger race'],cache_reset='confirmed_blocking_defect',cache_eviction='not_tested; fresh close lacks cleanup',shared_template_go_race_test='pass_separate_stores',selected_application_errors='pass',missing_method_reporting='known_baseline_defect',dynamic_table_reference_identity='not_tested',concurrent_per_transaction_order_equivalence='not_comparable_for_6_sampled_pairs')
assert not any(Path('/proc').glob('this_is_not_used'))
for m in ['baseline','optimized']:
 pid=int((O/'network'/m/'pid').read_text());p=Path(f'/proc/{pid}/stat');assert not p.exists() or p.read_text().split()[2]=='Z'
for f in ['race-safety.log','cache-key-safety.log','cache-lifecycle-audit.log']:assert 'PASS' in (O/f).read_text(),f
(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
# Supplemental chronological failures are kept intact, not retried into the performance corpus.
print(json.dumps(v,indent=2))
