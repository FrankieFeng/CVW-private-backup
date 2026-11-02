from pathlib import Path
import json,csv,base64,hashlib,re,subprocess,collections
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
outcomes=[json.loads(f.read_text())for f in(P/'raw_logs').glob('*-outcome.json')];ok=[x for x in outcomes if x['passed']];assert all(x['pid_exited']and x['owner']['managed_pending']==0 and x['owner']['stores_created']==x['owner']['stores_closed']and x['owner']['instances_created']==x['owner']['instances_closed']for x in ok)
assert not(P/'STOP_SHARED.json').exists()
rows=read('VM_INVOKE_BENCHMARK.csv');a=[r for r in rows if r['part']=='A'and r['phase']=='formal'];b=[r for r in rows if r['part']=='B'and r['phase']=='formal'and r['allocation_diagnostic']=='False'];assert len(a)==360 and len(b)==60
assert all(int(r['child_instances'])==6 for r in a+b if r['case']=='exchange_buyNow')
# All independently stored A and B parity results must be true.
par=list((P/'raw_logs').glob('*-parity.json'));assert all(json.loads(f.read_text())['passed']for f in par)
# Semantic invariants from actual committed in-memory writes; no business implementation changes.
semantic=[]
for r in a+b:
 if r['case']not in ['erc721_mint','exchange_buyNow','fact_saveAndFindByFileHash']:continue
 receipt=json.loads((P/'raw_logs'/f'{r["run"]}-receipts'/('formal-'+r['slot']+'.json')).read_text());inp=receipt['business_input'];writes={(w['contract_name'],base64.b64decode(w['key']).decode()):base64.b64decode(w.get('value','')).decode()for w in receipt['actual_rwset'].get('tx_writes',[])}
 if r['case']in ['erc721_mint','exchange_buyNow']:assert writes['erc721','tokenIds#'+inp['tokenId']]==inp['to']
 else:assert writes['fact','fact_bytes#'+inp['file_hash']]=='{}';assert receipt['actual_result']['contract_event'][0]['event_data']==[inp['file_hash'],inp['file_name']]
 semantic.append(dict(run=r['run'],case=r['case'],slot=r['slot'],passed=True))
with(P/'SEMANTIC_STATE_CHECK.csv').open('w',newline='')as f:w=csv.DictWriter(f,list(semantic[0]));w.writeheader();w.writerows(semantic)
# Calibration business parity, separately from main performance.
cal={}
for x in outcomes:
 if not x['label'].startswith('cal-'):continue
 ev=[json.loads(l[7:])for l in(P/'raw_logs'/f'{x["label"]}.log').read_text().splitlines()if l.startswith('STEP38 ')];ev=[e for e in ev if e.get('event')=='target'and e['phase']=='formal'];cal[x['case'],x['batch'],x['part']]=[{k:e[k]for k in ['tx_id','result','rwset','before_hash','after_hash']}for e in ev]
for c,bt,part in cal:
 if part=='A':assert cal[c,bt,'A']==cal[c,bt,'B']
# Accurate actual source function lines, not guessed external offsets.
functions=[]
patterns=['prepareStaticMemory','func (p *staticMemoryPlan) restore','e38Coalesce','func e38Begin','func e38End','func (m *nodeFreshManager) runtime','func (r *nodeFreshRuntime) Invoke','func (r *nodeFreshRuntime) invoke','func (m *nodeFreshManager) prepare','func NewStore','func NewWasiStateBuilder','func (self *WasiStateBuilder) Finalize','func (self *WasiEnvironment) GenerateImportObject','func (self *WasiEnvironment) Initialize','func (b *vmBridgeManager) GetImports','func NewInstanceInStore','func (self *Memory) Data','func TestStep38']
for part in ['A','B']:
 v=P/'source'/part/'vm'
 for rel in ['step35_node.go','step35_static.go','step38_support.go','step38_driver_test.go','step38_correctness_test.go','vm_bridge.go','wasmer-go/instance.go','wasmer-go/memory.go','wasmer-go/store.go','wasmer-go/wasi.go']:
  f=v/rel
  for i,l in enumerate(f.read_text().splitlines(),1):
   if l.lstrip().startswith('func')and any(p in l for p in patterns):functions.append(dict(part=part,file=str(f),line=i,code=l.strip(),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
with(P/'audit/SOURCE_FUNCTIONS.csv').open('w',newline='')as f:w=csv.DictWriter(f,list(functions[0]));w.writeheader();w.writerows(functions)
# Protect immutable baseline and native; do not rewrite logs or binaries.
root=Path('/home/frankie/mygitprojects');lib=root/'.worktrees/cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/libraries/patched/libwasmer.so';assert hashlib.sha256(lib.read_bytes()).hexdigest()=='56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc'
required=['README.md','COPY_RANGE_SOURCE.md','COPY_RANGE_CORRECTNESS.md','RANGE_STRATEGIES.csv','RANGE_BENCHMARK.csv','VM_INVOKE_BENCHMARK.csv','STORE_WASI_BREAKDOWN.csv','WASM_COPY_SHA_BREAKDOWN.csv','INSTRUMENTATION.md','RESOURCE_SUMMARY.csv','NEGATIVE_RESULTS.md','OPTIMIZATION_DECISION.md','NEXT_STEP.md','PROGRESS.md'];assert all((P/f).exists()for f in required)
x={'formal_A_calls':len(a),'formal_B_time_calls':len(b),'all_parity_files':len(par),'semantic_state_checks':len(semantic),'calibration_blocks_verified':len(cal)//2,'successful_processes':len(ok),'failed_processes':[x['label']for x in outcomes if not x['passed']],'source_function_records':len(functions),'native_sha_unchanged':True,'new_nodes_started':0};(P/'audit/validation.json').write_text(json.dumps(x,indent=2));print(json.dumps(x,indent=2))
