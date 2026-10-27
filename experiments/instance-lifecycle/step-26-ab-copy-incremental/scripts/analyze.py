"""Recompute paired effects from raw Step25 logs/receipts. No VM or native tools invoked."""
from pathlib import Path
from collections import defaultdict
import csv,json,statistics,random,hashlib
from check_pair import local,setup_check
P=Path(__file__).resolve().parents[1];B=P.parent/'step-25-ab-copy-screening';mapping={'G1':'G1','G2':'G2','G4':'G3'};cases={'compute','fact','erc721'}
metrics=['newinstance_ns','copy_ns','static_init_ns','wasi_imports_ns','s0_s1_ns','s1_s2_ns','s2_s3_ns','start_ns','callmethod_ns','export_call_ns','close_ns','invoke_ns']
def write(n,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rs)
def q(xs,p):
 a=sorted(xs);x=(len(a)-1)*p;i=int(x);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(x-i)
def ci(rr,k='invoke_ns_saving_ms'):
 tree=defaultdict(lambda:defaultdict(list))
 for r in rr:tree[r['batch']][r['label']].append(r[k])
 bs=list(tree);rng=random.Random(250027);draws=[]
 for _ in range(10000):
  sample=[]
  for b in rng.choices(bs,k=len(bs)):
   ps=list(tree[b])
   for proc in rng.choices(ps,k=len(ps)):sample+=tree[b][proc]
  draws.append(statistics.median(sample))
 return q(draws,.025),q(draws,.975)
timing=[];pairs=[];resources=[];correct=[];preps=[];targets={};configs={};initial=defaultdict(set)
for f in sorted((P/'raw_logs').glob('*-outcome.json')):
 o=json.loads(f.read_text());label=o['label'];assert o['passed']and o['all_owned_processes_stopped']and o['cgroup_empty']
 command=json.loads((P/'raw_logs'/f'{label}-command.json').read_text());lines=(P/'raw_logs'/f'{label}.log').read_text().splitlines();es=[(i,json.loads(l[7:]))for i,l in enumerate(lines,1)if l.startswith('STEP22 ')];life=[json.loads(l[8:])for l in lines if l.startswith('STEP21C ')];mgr=next(x for x in life if x['event']=='manager_closed');owner=o['owner'];assert mgr['created']==mgr['closed']and mgr['in_flight']==0 and owner['managed_objects']==owner['managed_pending']==0
 configs[label]=command;mods={x['data']['variant']:x['data']for _,x in es if x['event']=='module'}
 for _,e in es:
  if e['event']in ['module','template','cache_closed']:preps.append({'label':label,'phase':o['phase'],'case':o['contract'],'data_origin':'Step25','old_group':e['data'].get('group'),'new_group':mapping.get(e['data'].get('group'),'outside_new_matrix'),**{k:v for k,v in e['data'].items()if k!='group'},'event':e['event']})
 resources.append({'label':label,'case':o['contract'],'phase':o['phase'],'data_origin':'Step25 reused','new_process':False,'batch':o['batch'],'old_left':o['left'],'old_right':o['right'],'left':mapping.get(o['left'],'outside_new_matrix'),'right':mapping.get(o['right'],'outside_new_matrix'),'rss_peak_mib':o['peak_rss_kib']/1024,'thread_peak':o['peak_threads'],'go_heap_alloc_max':max(x.get('go_heap_alloc',0)for x in o['boundaries']),'go_heap_inuse_max':max(x.get('go_heap_inuse',0)for x in o['boundaries']),'created':mgr['created'],'closed':mgr['closed'],'managed_remaining':owner['managed_objects'],'pending_remaining':owner['managed_pending'],'owner_end_threads':owner['Threads'],'owner_end_rss_kib':owner['VmRSS'],'exit_code':o['systemd']['ExecMainStatus'],'all_stopped':True,'cgroup_empty':True,'reason':o['reason']})
 counts=defaultdict(int);ids=[]
 for line,e in es:
  if e['event']!='sample':continue
  s=e['data'];assert s['code']==0 and s['call_error_observed']=='<nil>'and s['managed_before']==s['managed_after'];ids.append(s['instance_id']);is_target=s['method']!='init_contract'and s['depth']==0;slot=counts[s['variant']]if is_target else-1
  if is_target:counts[s['variant']]+=1
  old=o['left']if s['variant']=='A0'else o['right'];bound=next((x for x in o['boundaries']if x['variant']==s['variant']and x['pair']==slot),{})
  r={'label':label,'case':o['contract'],'data_origin':'Step25 reused','phase':o['phase'],'batch':o['batch'],'pair_slot':slot,'is_target':is_target,'source_log_line':line,'old_group':old,'group':mapping.get(old,'outside_new_matrix'),'old_left':o['left'],'old_right':o['right'],'module_first':o['module_first'],'binary_sha':command['binary_sha256'],**s}
  r.update(static_init_ns=s['newinstance_ns']+s['copy_ns'],s0_s1_ns=s['to_s1_ns'],s1_s2_ns=s['to_s2_ns']-s['to_s1_ns'],s2_s3_ns=s['to_s3_ns']-s['to_s2_ns'],rss_after_kib=bound.get('VmRSS'),threads_after=bound.get('Threads'),go_heap_alloc_after=bound.get('go_heap_alloc'),module_prepare_ns_outside_invoke=mods[s['variant']]['module_prepare_ns'],cache_key=mods[s['variant']]['cache_key'],source_wasm_sha=mods[s['variant']]['source_sha'],copy_enabled=mods[s['variant']]['copy_enabled'],execution_wasm_sha=mods[s['variant']]['module_wasm_sha'])
  assert all(r[k]>=0 for k in ['s1_s2_ns','s2_s3_ns']);timing.append(r)
  if is_target:targets[label,slot,s['variant']]=r
 assert len(ids)==len(set(ids))==mgr['created'],'executed Instance reused'
 assert setup_check(label)==1
 for i,check in enumerate(local(label,o['pairs'])):
  a=targets[label,i,'A0'];b=targets[label,i,'A1'];assert a['gas']==b['gas']==check['gas'];initial[o['contract']].add(check['before_hash'])
  correct.append({'label':label,'case':o['contract'],'phase':o['phase'],'pair_slot':i,'old_left':o['left'],'old_right':o['right'],**check,'s1_checked':o['phase']=='preflight','fresh_unique_ids':True,'table_identity':'not_tested','exceptions':'not_tested','cross_contract':'not_tested'})
  if o['phase']=='preflight':assert len(a['s1_hash'])==len(b['s1_hash'])==64
  if o['phase']!='formal':continue
  r={'label':label,'case':o['contract'],'data_origin':'Step25 reused','left':mapping[o['left']],'right':mapping[o['right']],'old_left':o['left'],'old_right':o['right'],'batch':o['batch'],'pair_slot':i,'first':'A0'if(i+o['first'])%2==0 else'A1','module_first':o['module_first'],'gas_left':a['gas'],'gas_right':b['gas']}
  for k in metrics:r['left_'+k+'_ms']=a[k]/1e6;r['right_'+k+'_ms']=b[k]/1e6;r[k+'_saving_ms']=(a[k]-b[k])/1e6
  pairs.append(r)
assert len(pairs)==162 and len(resources)==96 and all(len(x)==1 for x in initial.values())
effects=[];stages=[];batches=[];orders=[]
expected=list(csv.DictReader((P/'audit/original_step25/PAIRED_EFFECTS.csv').open()))
for c,a,b in sorted({(r['case'],r['left'],r['right'])for r in pairs}):
 rr=[r for r in pairs if(r['case'],r['left'],r['right'])==(c,a,b)];assert len(rr)==18 and len({r['label']for r in rr})==9 and len({r['batch']for r in rr})==3;ds=[r['invoke_ns_saving_ms']for r in rr];lo,hi=ci(rr);bm=[]
 for batch in [1,2,3]:
  sub=[r for r in rr if r['batch']==batch];assert len(sub)==6;med=statistics.median(r['invoke_ns_saving_ms']for r in sub);bm.append(med);bl,bh=ci(sub);batches.append({'case':c,'left':a,'right':b,'batch':batch,'pairs':6,'processes':3,'saving_median_ms':med,'ci95_low_ms':bl,'ci95_high_ms':bh,'positive_pairs':sum(r['invoke_ns_saving_ms']>0 for r in sub)})
 e={'case':c,'left':a,'right':b,'old_left':rr[0]['old_left'],'old_right':rr[0]['old_right'],'n_pairs':18,'original_independent_batches':3,'original_independent_processes':9,'new_batches':0,'left_median_ms':statistics.median(r['left_invoke_ns_ms']for r in rr),'right_median_ms':statistics.median(r['right_invoke_ns_ms']for r in rr),'left_p95_ms':q([r['left_invoke_ns_ms']for r in rr],.95),'right_p95_ms':q([r['right_invoke_ns_ms']for r in rr],.95),'paired_saving_median_ms':statistics.median(ds),'ci95_low_ms':lo,'ci95_high_ms':hi,'positive_pairs':sum(x>0 for x in ds),'positive_fraction':sum(x>0 for x in ds)/18,'batch_medians_ms':json.dumps(bm),'all_batch_medians_positive':all(x>0 for x in bm),'source':'Step25 be88d9a raw reused','ci_method':'hierarchical batch/process bootstrap;10000;seed250027;linear_quantile;median'}
 old=next(x for x in expected if(x['case'],x['left'],x['right'])==(c,e['old_left'],e['old_right']))
 for k in ['paired_saving_median_ms','ci95_low_ms','ci95_high_ms','left_p95_ms','right_p95_ms']:assert abs(float(old[k])-e[k])<1e-10,('recomputation differs',c,a,b,k)
 effects.append(e)
 for k in metrics:
  vals=[r[k+'_saving_ms']for r in rr];stages.append({'case':c,'left':a,'right':b,'metric':k,'n_pairs':18,'left_median_ms':statistics.median(r['left_'+k+'_ms']for r in rr),'right_median_ms':statistics.median(r['right_'+k+'_ms']for r in rr),'paired_saving_median_ms':statistics.median(vals)})
 for factor in ['first','module_first']:
  for value in ['A0','A1']:
   ss=[r for r in rr if r[factor]==value];l,h=ci(ss);orders.append({'case':c,'left':a,'right':b,'factor':factor,'value':value,'actual_first_group':a if value=='A0'else b,'pairs':len(ss),'processes':len({r['label']for r in ss}),'paired_saving_median_ms':statistics.median(r['invoke_ns_saving_ms']for r in ss),'ci95_low_ms':l,'ci95_high_ms':h})
for n,rs in [('TIMING.csv',timing),('PAIRED_SAMPLES.csv',pairs),('PAIRED_EFFECTS.csv',effects),('BATCH_EFFECTS.csv',batches),('ORDER_SENSITIVITY.csv',orders),('STAGE_EFFECTS.csv',stages),('CORRECTNESS.csv',correct),('RESOURCE_SUMMARY.csv',resources),('MODULE_PREPARATION.csv',preps)]:write(n,rs)
verify={'new_guest_runs':0,'new_compilations':0,'reused_formal_pairs':len(pairs),'formal_processes':81,'reused_preflight_processes':15,'semantic_pairs_verified':len(correct),'all_raw_pair_checks_pass':True,'fresh_instance_ids_unique_per_process':True,'initial_hash_one_per_case':True,'recomputed_effects_match_step25':True,'overall_positive_ci_edges':sum(e['ci95_low_ms']>0 for e in effects),'order_strata_with_ci_crossing_zero':sum(e['ci95_low_ms']<=0<=e['ci95_high_ms']for e in orders),'max_original_rss_mib':max(r['rss_peak_mib']for r in resources),'max_original_go_heap_alloc_mib':max(r['go_heap_alloc_max']for r in resources)/1048576,'max_original_threads':max(r['thread_peak']for r in resources),'all_original_processes_stopped':True,'table_identity':'not_tested','exceptions':'not_tested','cross_contract':'not_tested','node':'not_tested'}
(P/'verification.json').write_text(json.dumps(verify,indent=2)+'\n');print(json.dumps(verify,indent=2))
