"""Offline: keep all raw attempts, derive bounded-process paired performance only."""
from pathlib import Path
from collections import defaultdict
import csv,json,math,statistics,random,hashlib
from check_pair import check,receipt,setup_check
P=Path(__file__).resolve().parents[1]
def read(f):return json.loads(f.read_text())
def write(name,rows):
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with(P/name).open('w',newline='')as f:
  w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
def quantile(xs,p):
 xs=sorted(xs);return xs[max(0,math.ceil(p*len(xs))-1)]
def ev(label):
 data=[]
 for line in(P/'raw_logs'/f'{label}.log').read_text(errors='replace').splitlines():
  if line.startswith('STEP22 '):data.append(json.loads(line[7:]))
 return data
outcomes=[read(f)for f in sorted((P/'raw_logs').glob('*-outcome.json'))]
timings=[];prep=[];resources=[];correct=[];targets={};buy_stages=[]
for o in outcomes:
 label=o['label'];events=ev(label);samples=[x['data']for x in events if x['event']=='sample'];mods={(x['data']['contract'],x['data']['variant']):x['data']for x in events if x['event']=='module'}
 for x in events:
  if x['event']in ['module','template','cache_closed','preparation_total']:prep.append(dict(label=label,phase=o['phase'],event=x['event'],**x['data']))
 boundary=o.get('boundaries',[])
 resources.append(dict(label=label,contract=o['contract'],phase=o['phase'],batch=o['batch'],slot=o['slot'],passed=o['passed'],exit=o['systemd'].get('ExecMainStatus'),reason=o['reason'],peak_rss_mib=o['peak_rss_kib']/1024,peak_threads=o['peak_threads'],boundary_threads=json.dumps([x['Threads']for x in boundary]),owner_after_threads=(o.get('owner')or{}).get('Threads'),owner_after_rss_mib=(o.get('owner')or{}).get('VmRSS',0)/1024,managed_pending=(o.get('owner')or{}).get('managed_pending'),all_processes_stopped=o['all_owned_processes_stopped'],cgroup_empty=o['cgroup_empty']))
 counts=defaultdict(int)
 for s in samples:
  if o['passed']:
   assert s['code']==0 and s.get('call_error_observed')=='<nil>' and s['managed_before']==s['managed_after']
  is_target=s['depth']==0 and s['method']!='init_contract';idx=counts[s['variant']]if is_target else -1
  if is_target:counts[s['variant']]+=1
  row=dict(label=label,phase=o['phase'],batch=o['batch'],process_slot=o['slot'],module_first=o['module_first'],pair_slot=idx,is_target=is_target,passed_process=o['passed'],**s)
  row['static_init_ns']=s['newinstance_ns']+s['copy_ns'];row['s0_s1_ns']=s['to_s1_ns'];row['s1_s2_ns']=s['to_s2_ns']-s['to_s1_ns'];row['s2_s3_ns']=s['to_s3_ns']-s['to_s2_ns'];row['post_s3_ns']=s['invoke_ns']-s['to_s3_ns'];row['module_prepare_ns_once_outside_invoke']=mods[(s['contract'],s['variant'])]['module_prepare_ns'];row['module_cache_key']=mods[(s['contract'],s['variant'])]['cache_key']
  assert row['s1_s2_ns']>=0 and row['s2_s3_ns']>=0 and row['post_s3_ns']>=0
  root_slot=idx if is_target else (0 if o['contract']=='exchange'and s['method']!='init_contract'else -1)
  boundary=next((q for q in o.get('boundaries',[])if q.get('variant')==s['variant']and q.get('pair')==root_slot),None)
  row['rss_after_root_kib']=boundary['VmRSS']if boundary else ''
  row['threads_after_root']=boundary['Threads']if boundary else ''
  row['resource_scope']='post-root boundary; see sampled process timeline; not per-callee instantaneous RSS'if boundary else'initialization boundary not individually observed'
  timings.append(row)
  if is_target:targets[(label,idx,s['variant'])]=row
  if o['contract']=='exchange'and s['method']!='init_contract':buy_stages.append(dict(label=label,batch=o['batch'],phase=o['phase'],**s))
 if o['contract']!='exchange'and o['passed']:
  assert setup_check(label)==1
  for i in range(o['pairs']):correct.append(dict(label=label,contract=o['contract'],phase=o['phase'],pair_slot=i,**check(receipt(label,i,'A0'),receipt(label,i,'A1')),table_function_identity='not_tested',exception_paths='not_tested'))
write('TIMING.csv',timings);write('MODULE_PREPARATION.csv',prep);write('RESOURCE_SUMMARY.csv',resources);write('BUY_NOW_STAGES.csv',buy_stages)
# Preserve observed counts; never synthesize a missing half-pair.
pairs=[];measurements=['newinstance_ns','copy_ns','static_init_ns','wasi_imports_ns','s0_s1_ns','s1_s2_ns','s2_s3_ns','callmethod_ns','close_ns','invoke_ns']
for o in outcomes:
 if o['contract']=='exchange'or not o['passed']:continue
 for i in range(o['pairs']):
  a=targets[(o['label'],i,'A0')];b=targets[(o['label'],i,'A1')]
  pairs.append(dict(contract=o['contract'],batch=o['batch'],process=o['label'],process_slot=o['slot'],pair_slot=i,phase=o['phase'],first='A0'if timings.index(a)<timings.index(b)else'A1',module_first=o['module_first'],**{v+'_'+k:r[k]/1e6 for v,r in [('A0',a),('A1',b)]for k in measurements},**{k+'_saving_ms':(a[k]-b[k])/1e6 for k in measurements}))
for phase in ['preflight','formal']:
 batches=sorted(set(o['batch']for o in outcomes if o['contract']=='exchange'and o['phase']==phase))
 for batch in batches:
  os=[o for o in outcomes if o['contract']=='exchange'and o['phase']==phase and o['batch']==batch]
  v={o['single']:o for o in os}
  if not all(k in v and v[k]['passed']for k in ['A0','A1']):continue
  aa,bb=[receipt(v[k]['label'],0,k)for k in ['A0','A1']];cc=check(aa,bb,True);correct.append(dict(label='exchange-b'+str(batch),contract='exchange',phase=phase,pair_slot=0,**cc,table_function_identity='not_tested',exception_paths='not_tested',callee_internal_complete_rwset='not_tested'))
  a,b=[targets[(v[k]['label'],0,k)]for k in ['A0','A1']]
  pairs.append(dict(contract='exchange',batch=batch,process='exchange-b'+str(batch),process_slot=0,pair_slot=0,phase=phase,first='A0'if v['A0']['wall_start_order']<v['A1']['wall_start_order']else'A1',module_first='split_equal',**{v+'_'+k:r[k]/1e6 for v,r in [('A0',a),('A1',b)]for k in measurements},**{k+'_saving_ms':(a[k]-b[k])/1e6 for k in measurements}))
write('CORRECTNESS.csv',correct);write('PAIRED_SAMPLES.csv',pairs)
formal=[r for r in pairs if r['phase']=='formal'];effects=[];summaries=[];by_batch=[];by_order=[]
def interval(rr,key,n=10000):
 rng=random.Random(240027);batches=sorted(set(r['batch']for r in rr));clusters={b:defaultdict(list)for b in batches}
 for r in rr:clusters[r['batch']][r['process']].append(r[key])
 values=[]
 for _ in range(n):
  sample=[]
  for batch in rng.choices(batches,k=len(batches)):
   pp=list(clusters[batch]);chosen=rng.choices(pp,k=len(pp))
   for proc in chosen:sample.extend(clusters[batch][proc])
  values.append(statistics.median(sample))
 return quantile(values,.025),quantile(values,.975)
for c in sorted(set(r['contract']for r in formal)):
 rr=[r for r in formal if r['contract']==c]
 for k in measurements:
  savings=[r[k+'_saving_ms']for r in rr];lo,hi=interval(rr,k+'_saving_ms')
  effects.append(dict(contract=c,metric=k,independent_batches=len(set(r['batch']for r in rr)),process_pairs_or_clusters=len(set(r['process']for r in rr)),valid_pairs=len(rr),saving_median_ms=statistics.median(savings),saving_mean_ms=statistics.mean(savings),ci95_low_ms=lo,ci95_high_ms=hi,positive_pairs=sum(x>0 for x in savings),positive_fraction=sum(x>0 for x in savings)/len(savings),ci_method='hierarchical batch/process paired bootstrap; seed240027;10000;median'))
  for v in ['A0','A1']:
   vals=[r[v+'_'+k]for r in rr];summaries.append(dict(contract=c,variant=v,metric=k,n=len(vals),median_ms=statistics.median(vals),p95_ms=quantile(vals,.95),mean_ms=statistics.mean(vals)))
 for batch in sorted(set(r['batch']for r in rr)):
  subset=[r for r in rr if r['batch']==batch]
  for k in measurements:by_batch.append(dict(contract=c,batch=batch,metric=k,n=len(subset),saving_median_ms=statistics.median(r[k+'_saving_ms']for r in subset),saving_mean_ms=statistics.mean(r[k+'_saving_ms']for r in subset),positive_fraction=statistics.mean(r[k+'_saving_ms']>0 for r in subset)))
 for field in ['first','module_first']:
  for value in sorted(set(r[field]for r in rr)):
   sub=[r for r in rr if r[field]==value];lo,hi=interval(sub,'invoke_ns_saving_ms');by_order.append(dict(contract=c,factor=field,value=value,n=len(sub),invoke_saving_median_ms=statistics.median(r['invoke_ns_saving_ms']for r in sub),ci95_low_ms=lo,ci95_high_ms=hi,positive_fraction=statistics.mean(r['invoke_ns_saving_ms']>0 for r in sub)))
write('PAIRED_EFFECTS.csv',effects);write('SUMMARY.csv',summaries);write('BATCH_EFFECTS.csv',by_batch);write('ORDER_SENSITIVITY.csv',by_order)
verification=dict(processes=len(outcomes),all_passed=all(o['passed']for o in outcomes),all_stopped=all(o['all_owned_processes_stopped']and o['cgroup_empty']for o in outcomes),all_managed_zero=all((o.get('owner')or{}).get('managed_pending')==0 for o in outcomes),formal_pairs={c:sum(r['contract']==c for r in formal)for c in sorted(set(r['contract']for r in formal))},semantic_pair_checks=len(correct),all_semantic_pairs_equal=all(r['semantic_equal']for r in correct),module_caching='once per contract/variant per bounded process, not per Invoke',long_lived_store='not_tested',table_function_identity='not_tested',exception_paths='not_tested',native_parallelism=False)
(P/'verification.json').write_text(json.dumps(verification,indent=2)+'\n');print(json.dumps(verification,indent=2))
for r in effects:
 if r['metric']in ['static_init_ns','s0_s1_ns','invoke_ns']:print(r)
