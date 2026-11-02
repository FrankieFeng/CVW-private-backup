"""Recompute completed Step38, preserve all raw logs/outcomes."""
from pathlib import Path
import csv,json,re,collections,statistics as st,random,hashlib
P=Path(__file__).resolve().parents[1]
def save(n,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/n).open('w',newline='')as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def q(v,p):
 a=sorted(v);k=(len(a)-1)*p;i=int(k);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(k-i)
def ci(by,key):
 seed=int(hashlib.sha256(key.encode()).hexdigest()[:16],16);rng=random.Random(seed);bs=list(by);out=[]
 for _ in range(10000):
  v=[]
  for b in rng.choices(bs,k=len(bs)):v.extend(rng.choices(by[b],k=len(by[b])))
  out.append(st.median(v))
 return q(out,.025),q(out,.975)
resources=[];A=[];B=[];strategies={};costs=[];cold=[];rawchecks=[]
for f in sorted((P/'raw_logs').glob('*-outcome.json')):
 z=json.loads(f.read_text());label=z['label'];o=z.get('owner')or{};resources.append(dict(run=label,part=z['part'],case=z['case'],strategy=z['strategy'],batch=z['batch'],verify=z['verify'],allocation_diagnostic=z['alloc'],passed=z['passed'],exit_code=z['exit_code'],rss_peak_mib=z['rss_peak_mib'],threads_peak=z['threads_peak'],stores_created=o.get('stores_created','not_recorded'),stores_closed=o.get('stores_closed','not_recorded'),instances_created=o.get('instances_created','not_recorded'),instances_closed=o.get('instances_closed','not_recorded'),pending=o.get('managed_pending','not_recorded'),pid_exited=z['pid_exited'],native_loaded=z['native_loaded'],reason=z['reason']))
 text=(P/'raw_logs'/f'{label}.log').read_text();nodes=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP35 ')];events=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP38 ')]
 rawchecks.extend(dict(run=label,**e)for e in events if e.get('event')=='memory_check')
 for e in nodes:
  if e['event']=='module_prepared':cold.append(dict(run=label,**e))
 if not z['passed']or z['test']!='TestStep38VM':continue
 for t in events:
  if t.get('event')!='target':continue
  tx=t['tx_id'];vm=[e for e in nodes if e['event']=='invoke_end'and e['tx_id']==tx];root=[e for e in vm if e['depth']==0];assert len(root)==1,(label,tx,len(root));r=root[0]
  for ev in vm:
   k=(ev['contract'],z['strategy']);strategies[k]=dict(contract=ev['contract'],strategy=z['strategy'],range_count=ev.get('range_count',0),copy_bytes=ev.get('copy_bytes',0),copy_enabled=z['strategy']!='F0')
  outer=re.findall(r'REUSE_VM tx='+tx+r' .*?begin_ns=(\d+) end_ns=(\d+) code=(\d+) gas=(\d+) depth=(\d+)',text);outer=[(int(a),int(b))for a,b,code,gas,depth in outer if int(depth)==0];assert len(outer)==1
  row=dict(run=label,part=z['part'],case=z['case'],strategy=z['strategy'],batch=z['batch'],slot=t['slot'],phase=t['phase'],verification_run=z['verify'],allocation_diagnostic=z['alloc'],tx_id=tx,root_instance_id=r['instance_id'],root_store_id=r['store_id'],root_instances=1,child_instances=len(vm)-1,range_count=r.get('range_count',0),copy_bytes=r.get('copy_bytes',0),newinstance_ms=r['newinstance_ns']/1e6,restore_ms=r.get('copy_ns',0)/1e6,newinstance_restore_ms=(r['newinstance_ns']+r.get('copy_ns',0))/1e6,newinstance_restore_start_ms=(r['newinstance_ns']+r.get('copy_ns',0)+r['start_ns'])/1e6,init_through_s2_ms=r['s2_ns']/1e6,owner_invoke_ms=r['invoke_ns']/1e6,factory_invoke_ms=(outer[0][1]-outer[0][0])/1e6,runcontract_ms=t['runcontract_ns']/1e6,start_ms=r['start_ns']/1e6,callmethod_ms=r['callmethod_ns']/1e6,close_ms=r['close_ns']/1e6,s0_s1_ms=r['s1_ns']/1e6,all_instance_restore_ms=sum(e.get('copy_ns',0)for e in vm)/1e6,all_instance_init_ms=sum(e['newinstance_ns']+e.get('copy_ns',0)for e in vm)/1e6,host_envelope_allocs=t['host_envelope_allocs'],host_envelope_alloc_bytes=t['host_envelope_alloc_bytes'],host_heap=t['host_heap'],gas=t['result'].get('gas_used',0),rss_peak_mib=z['rss_peak_mib'],threads_peak=z['threads_peak'],initial_memory_match=r.get('initial_memory_match','not_checked_in_timing_run'))
  if label.startswith('A-'):A.append(row)
  elif label.startswith('B-'):B.append(row)
  root_cost_id=next((e['call_id']for e in t['costs']or[] if e['stage']=='runtime_bytecode_clone'),None)
  for e in t['costs']or[]:
   costs.append(dict(run=label,case=z['case'],strategy=z['strategy'],batch=z['batch'],slot=t['slot'],phase=t['phase'],verification_run=z['verify'],root_call=e['call_id']==root_cost_id,tx_id=tx,**e))
# Valid target formal only; allocations diagnostics never mixed with timing-only.
main=[r for r in A if r['phase']=='formal'and not r['verification_run']];timingB=[r for r in B if r['phase']=='formal'and not r['allocation_diagnostic']];allocB=[r for r in B if r['phase']=='formal'and r['allocation_diagnostic']]
assert len(main)==360,(len(main),'A expected10*3*6*2');assert len(timingB)==60 and len(allocB)==20
save('VM_INVOKE_BENCHMARK.csv',A+B);save('RANGE_BENCHMARK.csv',[{k:r[k]for k in ['run','case','part','strategy','batch','slot','phase','verification_run','allocation_diagnostic','range_count','copy_bytes','restore_ms','newinstance_restore_ms','newinstance_restore_start_ms','init_through_s2_ms','owner_invoke_ms','factory_invoke_ms','all_instance_restore_ms','all_instance_init_ms']}for r in A+B]);save('RANGE_STRATEGIES.csv',list(strategies.values()));save('RESOURCE_SUMMARY.csv',resources);save('MEMORY_CHECKS.csv',rawchecks);save('MODULE_PREPARATION.csv',cold);save('COST_OBSERVATIONS.csv',costs)
metrics=['restore_ms','newinstance_restore_ms','newinstance_restore_start_ms','init_through_s2_ms','owner_invoke_ms','factory_invoke_ms','runcontract_ms','start_ms','callmethod_ms','close_ms','s0_s1_ms','all_instance_init_ms'];summary=[];paired=[];orders=[]
for case in sorted({r['case']for r in main}):
 d={g:{(int(r['batch']),r['slot']):r for r in main if r['case']==case and r['strategy']==g}for g in ['F0','C0','C1','C2','C3','C4']}
 for g,a in d.items():
  for m in metrics:
   v=[r[m]for r in a.values()];summary.append(dict(case=case,strategy=g,metric=m,N=len(v),batches=3,mean=st.mean(v),p50=st.median(v),p95=q(v,.95)))
 for left,right in [('C0','C1'),('C0','C2'),('C0','C3'),('C0','C4'),('F0','C0'),('F0','C2'),('F0','C3'),('F0','C4'),('C2','C3'),('C3','C4')]:
  a,b=d[left],d[right];assert a.keys()==b.keys()
  for m in metrics:
   by=collections.defaultdict(list)
   for k in sorted(a):by[k[0]].append(a[k][m]-b[k][m])
   vals=[v for vv in by.values()for v in vv];lo,hi=ci(by,case+left+right+m);paired.append(dict(case=case,left=left,right=right,metric=m,N=len(vals),independent_batches=3,saving_median=st.median(vals),saving_mean=st.mean(vals),ci95_low=lo,ci95_high=hi,positive_fraction=sum(v>0 for v in vals)/len(vals),batch1=st.median(by[1]),batch2=st.median(by[2]),batch3=st.median(by[3]),all_batches_positive=all(st.median(v)>0 for v in by.values())))
 # B vs A C0 diagnostic comparison is separated in both order and instrumentation.
 a=d['C0'];b={(int(r['batch']),r['slot']):r for r in timingB if r['case']==case}
 for m in ['factory_invoke_ms','owner_invoke_ms','restore_ms']:
  v=[b[k][m]-a[k][m]for k in a];orders.append(dict(case=case,comparison='B timing-only minus A C0',metric=m,N=len(v),median_added_ms=st.median(v),mean_added_ms=st.mean(v),causal_instrumentation_effect='not_identified: all B later than A; includes order/environment'))
save('SUMMARY.csv',summary);save('PAIRED_EFFECTS.csv',paired);save('INSTRUMENTATION_COMPARISON.csv',orders)
# Costs carry runtime ID; root runtime is first runtime clone in each target. Child IDs are retained.
cc=[]
for c in costs:
 if c['phase']!='formal' or c.get('verification_run') or not c['run'].startswith('B-'):continue
 cc.append(c)
shaStages={'runtime_bytecode_clone','invoke_two_SHA','prepare_SHA'};wasi=[c for c in cc if c['stage']not in shaStages];sha=[c for c in cc if c['stage']in shaStages]
save('STORE_WASI_BREAKDOWN.csv',wasi);save('WASM_COPY_SHA_BREAKDOWN.csv',sha)
cs=[]
for case in sorted({c['case']for c in cc}):
 for mode in [False,True]:
  for name in sorted({c['stage']for c in cc}):
   a=[c for c in cc if c['case']==case and c['allocation_diagnostic']==mode and c['stage']==name]
   if not a:continue
   v=[c['ns']/1e6 for c in a];cs.append(dict(case=case,stage=name,allocation_diagnostic=mode,call_observations=len(a),root_and_children='combined observations; IDs retained in raw CSV',p50_ms=st.median(v),mean_ms=st.mean(v),p95_ms=q(v,.95),sum_ms=sum(v),sum_input_bytes=sum(c['input_bytes']for c in a),mean_allocs=st.mean(c['allocs']for c in a)if mode else'not_sampled',mean_alloc_bytes=st.mean(c['alloc_bytes']for c in a)if mode else'not_sampled',native_alloc_bytes='not_measured'))
save('COST_SUMMARY.csv',cs)
(P/'audit/analysis.json').write_text(json.dumps({'formal_A_calls':len(main),'formal_B_timing_calls':len(timingB),'formal_B_allocation_calls':len(allocB),'A_methods':len({x['case']for x in main}),'contracts':8,'A_independent_batches':3,'A_paired_blocks_per_method':6,'resource_processes':len(resources),'failed_processes':[r['run']for r in resources if not r['passed']],'max_rss_mib':max(r['rss_peak_mib']for r in resources),'max_threads':max(r['threads_peak']for r in resources),'native_nodes_started':0},indent=2));print((P/'audit/analysis.json').read_text())
