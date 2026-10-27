"""Offline analysis; all raw attempts retained, only completed valid formal pairs enter effects."""
from pathlib import Path
from collections import defaultdict
import json,csv,statistics,random,hashlib,math
from check_pair import local,setup_check
P=Path(__file__).resolve().parents[1]
METRICS=['newinstance_ns','copy_ns','static_init_ns','wasi_imports_ns','s0_s1_ns','s1_s2_ns','s2_s3_ns','start_ns','callmethod_ns','export_call_ns','close_ns','invoke_ns']
def save(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/name).open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def q(xs,p):
 xs=sorted(xs);v=(len(xs)-1)*p;i=int(v);return xs[i]+(xs[min(i+1,len(xs)-1)]-xs[i])*(v-i)
def interval(rows,key='invoke_ns_saving_ms'):
 batches=defaultdict(lambda:defaultdict(list))
 for r in rows:batches[r['batch']][r['label']].append(r[key])
 rng=random.Random(250027);bs=list(batches);vals=[]
 for _ in range(10000):
  sample=[]
  for b in rng.choices(bs,k=len(bs)):
   procs=batches[b];ps=list(procs)
   for p in rng.choices(ps,k=len(ps)):sample+=procs[p]
  vals.append(statistics.median(sample))
 return q(vals,.025),q(vals,.975)
rows=[];resources=[];preps=[];pairs=[];correct=[];targets={};observed=[]
for path in sorted((P/'raw_logs').glob('*-outcome.json')):
 o=json.loads(path.read_text());label=o['label'];observed.append(o);cmd=json.loads((P/'raw_logs'/f'{label}-command.json').read_text())
 es=[json.loads(l[7:])for l in(P/'raw_logs'/f'{label}.log').read_text(errors='replace').splitlines()if l.startswith('STEP22 ')]
 life=[json.loads(l[8:])for l in(P/'raw_logs'/f'{label}.log').read_text(errors='replace').splitlines()if l.startswith('STEP21C ')]
 manager=next((e for e in life if e['event']=='manager_closed'),{});owner=o.get('owner')or{}
 resources.append({'label':label,'case':o['contract'],'left':o['left'],'right':o['right'],'phase':o['phase'],'batch':o['batch'],'passed':o['passed'],'exit':o['systemd'].get('ExecMainStatus'),'reason':o['reason'],'rss_peak_mib':o['peak_rss_kib']/1024,'thread_peak':o['peak_threads'],'go_heap_alloc_max':max((x.get('go_heap_alloc',0)for x in o['boundaries']),default=0),'go_heap_inuse_max':max((x.get('go_heap_inuse',0)for x in o['boundaries']),default=0),'go_heap_sys_max':max((x.get('go_heap_sys',0)for x in o['boundaries']),default=0),'owner_end_threads':owner.get('Threads'),'owner_end_rss_kib':owner.get('VmRSS'),'created':manager.get('created'),'closed':manager.get('closed'),'managed_remaining':owner.get('managed_objects'),'pending_remaining':owner.get('managed_pending'),'all_stopped':o['all_owned_processes_stopped'],'cgroup_empty':o['cgroup_empty'],'binary_sha':cmd['binary_sha256']})
 if o['passed']:assert manager['created']==manager['closed']and owner['managed_objects']==owner['managed_pending']==0
 for e in es:
  if e['event']in ['template','module','cache_closed']:preps.append({'label':label,'case':o['contract'],'phase':o['phase'],'batch':o['batch'],'event':e['event'],**e['data']})
 counts=defaultdict(int)
 for e in es:
  if e['event']!='sample':continue
  s=e['data'];is_target=s['depth']==0 and s['method']!='init_contract';slot=counts[s['variant']]if is_target else-1
  if is_target:counts[s['variant']]+=1
  group=o['left']if s['variant']=='A0'else o['right'];bound=next((x for x in o['boundaries']if x.get('variant')==s['variant']and x.get('pair')==slot),{})
  r={'label':label,'case':o['contract'],'group':group,'left':o['left'],'right':o['right'],'phase':o['phase'],'batch':o['batch'],'process_slot':o['slot'],'pair_slot':slot,'module_first':o['module_first'],'is_target':is_target,'eligible':o['passed']and o['phase']=='formal','copy_check':o['copy_check'],'binary_sha':cmd['binary_sha256'],**s}
  r.update(static_init_ns=s['newinstance_ns']+s['copy_ns'],s0_s1_ns=s['to_s1_ns'],s1_s2_ns=s['to_s2_ns']-s['to_s1_ns'],s2_s3_ns=s['to_s3_ns']-s['to_s2_ns'],post_s3_ns=s['invoke_ns']-s['to_s3_ns'],rss_after_kib=bound.get('VmRSS'),threads_after=bound.get('Threads'),go_heap_alloc_after=bound.get('go_heap_alloc'),go_heap_inuse_after=bound.get('go_heap_inuse'))
  if o['passed']:assert s['code']==0 and s['call_error_observed']=='<nil>'and s['managed_before']==s['managed_after']and r['s1_s2_ns']>=0 and r['s2_s3_ns']>=0
  rows.append(r)
  if is_target:targets[label,slot,s['variant']]=r
 if not o['passed']:continue
 assert setup_check(label)==1
 for i,check in enumerate(local(label,o['pairs'])):
  a=targets[label,i,'A0'];b=targets[label,i,'A1'];c={'label':label,'case':o['contract'],'left':o['left'],'right':o['right'],'batch':o['batch'],'phase':o['phase'],'pair_slot':i,**check,'s1_checked':o['phase']=='preflight','table_identity':'not_tested','exceptions':'not_tested','cross_contract':'not_tested'};correct.append(c)
  if o['phase']=='preflight':assert a.get('s1_hash')and b.get('s1_hash')
  if o['phase']!='formal':continue
  r={'label':label,'case':o['contract'],'left':o['left'],'right':o['right'],'batch':o['batch'],'pair_slot':i,'module_first':o['module_first'],'first':'A0'if(i+o['first'])%2==0 else'A1','gas_left':a['gas'],'gas_right':b['gas']}
  for k in METRICS:r['left_'+k+'_ms']=a[k]/1e6;r['right_'+k+'_ms']=b[k]/1e6;r[k+'_saving_ms']=(a[k]-b[k])/1e6
  pairs.append(r)
effects=[];stages=[];batchrows=[];orders=[]
for case,left,right in sorted({(r['case'],r['left'],r['right'])for r in pairs}):
 rr=[r for r in pairs if(r['case'],r['left'],r['right'])==(case,left,right)];ds=[r['invoke_ns_saving_ms']for r in rr];lo,hi=interval(rr)
 bm=[]
 for batch in sorted({r['batch']for r in rr}):
  sub=[r for r in rr if r['batch']==batch];d=[r['invoke_ns_saving_ms']for r in sub];bm.append(statistics.median(d));batchrows.append({'case':case,'left':left,'right':right,'batch':batch,'n':len(sub),'left_median_ms':statistics.median(r['left_invoke_ns_ms']for r in sub),'right_median_ms':statistics.median(r['right_invoke_ns_ms']for r in sub),'paired_median_ms':statistics.median(d),'positive_fraction':sum(x>0 for x in d)/len(d)})
 effects.append({'case':case,'left':left,'right':right,'n_pairs':len(rr),'independent_batches':len(bm),'independent_processes':len({r['label']for r in rr}),'left_mean_ms':statistics.mean(r['left_invoke_ns_ms']for r in rr),'left_median_ms':statistics.median(r['left_invoke_ns_ms']for r in rr),'left_p95_ms':q([r['left_invoke_ns_ms']for r in rr],.95),'right_mean_ms':statistics.mean(r['right_invoke_ns_ms']for r in rr),'right_median_ms':statistics.median(r['right_invoke_ns_ms']for r in rr),'right_p95_ms':q([r['right_invoke_ns_ms']for r in rr],.95),'paired_saving_median_ms':statistics.median(ds),'paired_saving_mean_ms':statistics.mean(ds),'ci95_low_ms':lo,'ci95_high_ms':hi,'positive_pairs':sum(x>0 for x in ds),'positive_fraction':sum(x>0 for x in ds)/len(ds),'batch_medians_ms':json.dumps(bm),'all_batch_medians_positive':all(x>0 for x in bm),'status':'screening_3_batches'if len(bm)==3 and len(rr)==18 else'exploratory_partial','ci_method':'hierarchical batch/process bootstrap;10000;seed250027;median;linear_quantile'})
 for k in METRICS:stages.append({'case':case,'left':left,'right':right,'metric':k,'n':len(rr),'left_median_ms':statistics.median(r['left_'+k+'_ms']for r in rr),'right_median_ms':statistics.median(r['right_'+k+'_ms']for r in rr),'paired_saving_median_ms':statistics.median(r[k+'_saving_ms']for r in rr)})
 for key in ['first','module_first']:
  for value in ['A0','A1']:
   ss=[r for r in rr if r[key]==value]
   if ss:
    l,h=interval(ss);orders.append({'case':case,'left':left,'right':right,'factor':key,'value':value,'n':len(ss),'paired_median_ms':statistics.median(r['invoke_ns_saving_ms']for r in ss),'ci95_low_ms':l,'ci95_high_ms':h})
save('TIMING.csv',rows);save('PAIRED_SAMPLES.csv',pairs);save('PAIRED_EFFECTS.csv',effects);save('STAGE_EFFECTS.csv',stages);save('BATCH_EFFECTS.csv',batchrows);save('ORDER_SENSITIVITY.csv',orders);save('RESOURCE_SUMMARY.csv',resources);save('MODULE_PREPARATION.csv',preps);save('CORRECTNESS.csv',correct)
v={'processes':len(observed),'passed':sum(o['passed']for o in observed),'failed':sum(not o['passed']for o in observed),'formal_pairs':len(pairs),'semantic_pairs_checked':len(correct),'all_stopped':all(o['all_owned_processes_stopped']and o['cgroup_empty']for o in observed),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'max_observed_rss_mib':max((r['rss_peak_mib']for r in resources),default=0),'max_observed_threads':max((r['thread_peak']for r in resources),default=0),'scope':'bounded serial reference manager, not original pool or real node','table_identity':'not_tested','exceptions':'not_tested','reuse_arm':'not_tested'}
(P/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
