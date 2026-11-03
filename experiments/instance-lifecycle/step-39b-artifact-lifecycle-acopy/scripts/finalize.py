from pathlib import Path
import subprocess,json,csv,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[2];V=P/'source/vm'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd):return subprocess.run(cmd,capture_output=True,text=True).stdout
lib=Path('/home/frankie/mygitprojects/.worktrees/cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/libraries/patched/libwasmer.so');assert sha(lib)=='56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc'
# Freeze the exact test file compiled into each binary, not just a hash of a subsequently expanded file.
cur=(V/'step39b_lifecycle_test.go').read_text();imports='\n "encoding/json"\n "crypto/sha256"\n "encoding/hex"'
perf=cur.split('\nfunc TestStep39BPinnedLifetime')[0].replace(imports,'')
r4=cur.split('\nfunc TestStep39BDrainBuyNow')[0].replace(imports,'')
r1=perf.split('\nfunc TestStep39BByteBudget')[0]
r1=r1.replace('\n ref:=weak.Make(held.(*nodeFreshRuntime).artifact)','')
block='''\n held=nil
 var beforeGC,afterGC runtime.MemStats;runtime.ReadMemStats(&beforeGC);attempts:=0
 for ;attempts<32;attempts++{e39bChurn=make([]byte,4<<20);e39bChurn[0]=byte(attempts);if ref.Value()==nil{break}}
 runtime.ReadMemStats(&afterGC);runtime.KeepAlive(m)
 e39bCheck(t,"manager_alive_but_stopped_artifact_collectible",ref.Value()==nil,map[string]interface{}{"bounded_churn_bytes":(attempts+1)*(4<<20),"natural_gc":afterGC.NumGC-beforeGC.NumGC});e39bChurn=nil
'''
r1=r1.replace(block,'')
(P/'audit/frozen-tests').mkdir(exist_ok=True)
variants={'perf':perf,'race':perf,'diag-r1':r1,'diag-r2':r1,'diag-r3':perf,'diag-r4':r4,'diag-r5':cur}
verified=[]
for label,text in variants.items():
 b=json.loads((P/'audit'/f'build-{label}-outcome.json').read_text());target=next(h for f,h in b['source_hashes'].items()if f.endswith('/step39b_lifecycle_test.go'))
 # Appended test snapshots may leave one additional separator newline at the boundary.
 candidates=[text,text.rstrip()+'\n',text+'\n',text.rstrip()+'\n\n'];match=next((x for x in candidates if hashlib.sha256(x.encode()).hexdigest()==target),None)
 assert match is not None,('frozen test reconstruction',label,target,hashlib.sha256(text.encode()).hexdigest())
 out=P/'audit/frozen-tests'/f'{label}-step39b_lifecycle_test.go.txt';out.write_text(match);verified.append({'binary':label,'test_sha':target,'snapshot':str(out.relative_to(P))})
 # All measured runtime .go source bytes are identical; diagnostic flag only differs by tree.
 for f,h in b['source_hashes'].items():
  if f.endswith('/step39b_lifecycle_test.go'):continue
  assert sha(P/f)==h,(label,f,'runtime mutated')
(P/'audit/source-frozen.json').write_text(json.dumps(verified,indent=2))
rs=list(csv.DictReader((P/'RESOURCE_SUMMARY.csv').open()));assert len(rs)==67
assert all(r['passed']=='True'and r['pid_exited']=='True'for r in rs)
assert all(r['stores_created']==r['stores_closed']and r['instances_created']==r['instances_closed']and r['pending']=='0'for r in rs if r['owner_expected']=='True')
assert all(r['passed']=='True'for r in csv.DictReader((P/'LIFECYCLE_CHECKS.csv').open()))
# Existing failure receipts provide state rollback evidence without a new experiment.
fail=[]
for name in ['invalid-module','injected-after-compile']:
 f=P/'raw_logs/lifecycle-Failure-receipts'/f'{name}.json';r=json.loads(f.read_text());assert r['actual_result']['code']!=0 and r['before_hash']==r['after_hash'];fail.append({'receipt':str(f.relative_to(P)),'guest_state_unchanged':True,'result':r['actual_result']})
(P/'audit/failure-state-parity.json').write_text(json.dumps(fail,indent=2))
# Verify accepted buyNow root and children complete before cache closure under Stop.
txt=(P/'raw_logs/supplement-DrainBuyNow.log').read_text();ev=[json.loads(l[7:])for l in txt.splitlines()if l.startswith('STEP35 ')];receipt=json.loads((P/'raw_logs/supplement-DrainBuyNow-receipts/drain-buyNow.json').read_text());tx=receipt['tx_id'];nodes=[e for e in ev if e.get('event')=='invoke_end'and e.get('tx_id')==tx];assert len(nodes)==7 and sum(e['depth']>0 for e in nodes)==6
stopindex=next(i for i,e in enumerate(ev)if e['event']=='stop_requested');startindex=next(i for i,e in enumerate(ev)if e['event']=='invoke_begin'and e.get('tx_id')==tx);endindex=max(i for i,e in enumerate(ev)if e['event']=='invoke_end'and e.get('tx_id')==tx);closeindex=next(i for i,e in enumerate(ev)if e['event']=='cache_closed');assert stopindex<startindex<endindex<closeindex
(P/'audit/drain-order.json').write_text(json.dumps({'passed':True,'invokes':7,'children':6,'event_indices':[stopindex,startindex,endindex,closeindex]},indent=2))
units=run(['systemctl','--user','list-units','--state=running','--no-legend']);assert not any('step39b-'in l for l in units.splitlines());assert not(P/'STOP_SHARED.json').exists()
info={'parent':'0dd9f76e4048130cafeb82c625d7450df4911320','branch':run(['git','-C',str(R),'branch','--show-current']).strip(),'native_path':str(lib),'native_sha':sha(lib),'go':run(['/usr/local/go/bin/go','version']).strip(),'os':run(['uname','-a']).strip(),'node_head':run(['git','-C','/home/frankie/mygitprojects/.worktrees/node-step36','rev-parse','HEAD']).strip(),'node_status':run(['git','-C','/home/frankie/mygitprojects/.worktrees/node-step36','status','--porcelain']),'new_nodes':0}
assert info['node_status']==''
(P/'audit/environment.json').write_text(json.dumps(info,indent=2));(P/'audit/cpu.txt').write_text(run(['lscpu']));(P/'audit/buildinfo-perf.txt').write_text(run(['/usr/local/go/bin/go','version','-m',str(P/'binaries/vm-perf')]))
cmd=['env','GOWORK='+str(P/'A.work'),'GOPROXY=off','/usr/local/go/bin/go','list','-m','-json','chainmaker.org/chainmaker/vm/v2','chainmaker.org/chainmaker/vm-wasmer/v2','chainmaker.org/chainmaker/store/v2'];(P/'audit/modules.json').write_text(run(cmd))
(P/'LIFECYCLE_COMPLETE.json').write_text(json.dumps({'passed':True,'checks':54,'managed_units':60,'total_units':67,'new_nodes':0,'scope':'bounded VM, not production/node certification'}))
(P/'PROGRESS.md').write_text('''# Step-39B 已完成\n\n基线0dd9f76e；experiment/step39b-artifact-lifecycle-acopy。\n\n1. 审计及独立工作树完成；Go1.24.1 reachable padding、P0、C0及原native SHA核实，未重编Guest。\n2. 单一Manager有界缓存治理完成：8项/64MiB、满拒绝、Reset清理、Stop关闭、prepare失败条件删除；原Owner不改。\n3. 实际VM生命周期、自然GC可回收、读并发Race、失败回滚、旧Runtime替换/Reset及Stop中真实buyNow6子调用通过。54条新生命周期check，另有继承身份拒绝/隔离新执行记录。\n4. 四组12进程功能预检通过，逐字节初始Memory相等。\n5. 3方法×4组×3批×2正式调用=72新正式调用；每进程2预热/2正式。另6诊断进程，不混入主统计。三批完整保存，未删反向样本。\n6. 统计/中文报告/源码diff/精确编译时测试快照及资源校验完成。67个受监控进程已退出，60个native Owner计数配平，未触发守卫。\n\n失败/准备纠正：首个诊断编译未用变量，保留build-diag.log；测试源码复制路径曾写错，diag-r2仍为旧测试文本，未用于性能或补充新检查。修正后用独立diag-r3/r4/r5标签，旧日志/二进制身份保留。没有覆盖失败现场。\n\n复算：python3 scripts/analyze.py；python3 scripts/report.py；python3 scripts/finalize.py。不重复有效实验。\n\n结论：有限VM范围生命周期闭环通过，建议下一轮有限节点Smoke/E2E，尚未运行节点。G2→G3三方法正向探索CI；G0→G1的hashCal CI跨零，保留不确定性。遵守原Owner32根调用预算、1536MiB/220线程，禁止自动扩样本。\n\n本轮停止，等待确认；不启动Step-39C、不推送。初始截断消息的笔记保存在旧step-39b-sha-artifact-lifecycle目录（只读预审），正式成果以当前指定目录为准。\n''')
files=[p for p in P.rglob('*')if p.is_file()and 'binaries'not in p.relative_to(P).parts and '__pycache__'not in p.parts and p.name not in ['libwasmer.so','SHA256SUMS']]
(P/'audit/SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(P))+'\n'for p in sorted(files)))
print('VALIDATED',len(rs),'units, exact frozen tests + unchanged runtime sources, drain business/order, no running node/test')
