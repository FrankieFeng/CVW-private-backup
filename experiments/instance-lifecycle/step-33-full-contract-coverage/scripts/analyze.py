from pathlib import Path
import json,csv,statistics as st,random,math,hashlib,base64,collections
P=Path(__file__).resolve().parents[1]
CASES=[x['case']for x in json.loads((P/'inputs/cases.json').read_text())];CASE_META={x['case']:x for x in json.loads((P/'inputs/cases.json').read_text())};GROUPS=['G0','G1','G2','G3'];EDGES=[('G0','G1','A'),('G0','G2','Copy'),('G0','G3','A+Copy'),('G2','G3','A_given_Copy'),('G1','G3','Copy_given_A')]
def dump(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 if not keys:return
 with(P/name).open('w',newline='')as f:w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
def q(a,p):
 a=sorted(a);v=(len(a)-1)*p;i=int(v);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(v-i)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').encode()).hexdigest()
def apply(l,r):
 if r.get('status',0)!=0 or r['actual_result'].get('code',0)!=0:return
 for x in r['actual_rwset'].get('tx_writes',[]):
  c=x['contract_name'];k=base64.b64decode(x['key']).decode();l.setdefault(c,{})
  if 'value'in x:l[c][k]=x['value']
  else:l[c].pop(k,None)
def reconstruct(folder,g,case):
 configs=[]
 for f in (P/'raw_logs').glob('*-receipts/setup-identity-G0.json'):
  configs=[x for x in json.loads(f.read_text())['actual_rwset']['tx_reads']if x['contract_name']=='CHAIN_CONFIG']
  if configs:break
 assert len(configs)==1
 l={'CHAIN_CONFIG':{'CHAIN_CONFIG':configs[0]['value']}}
 c=CASE_META[case]['contract']
 setup=[folder/f'setup-{c}-{g}.json']+sorted(folder.glob(f'setup-business-*-{g}.json'))
 for f in setup:
  r=json.loads(f.read_text());assert digest(l)==r['before_hash'],(case,f,'initial');apply(l,r);assert digest(l)==r['after_hash'],(case,f,'final')
 initial=json.loads(json.dumps(l));r=json.loads((folder/f'target-{g}.json').read_text());case_input=json.loads(Path(CASE_META[case]['file']).read_text());assert r['business_input']==case_input['params'],(case,'input freeze');assert digest(l)==r['before_hash'];apply(l,r);assert digest(l)==r['after_hash']
 out=folder/f'target-{g}-ledger.json'
 if not out.exists():out.write_text(json.dumps(dict(initial=initial,final=l,initial_sha=digest(initial),final_sha=digest(l)),indent=2))
 return digest(l)
def boot(ds,seed):
 bs=sorted({k[0]for k in ds});by={b:[v for (bb,_),v in ds.items()if bb==b]for b in bs};rng=random.Random(seed);dist=[]
 for _ in range(10000):
  vals=[]
  for b in rng.choices(bs,k=len(bs)):vals.extend(rng.choices(by[b],k=len(by[b])))
  dist.append(st.median(vals))
 return q(dist,.025),q(dist,.975)
blocks=[json.loads(f.read_text())for f in sorted((P/'raw_logs').glob('*-block.json'))];meta={label:b for b in blocks for label in b['labels']};outcomes=[]
for f in sorted((P/'raw_logs').glob('*-outcome.json')):
 try:outcomes.append(json.loads(f.read_text()))
 except json.JSONDecodeError:continue
rows=[];resources=[];modules=[];correct=[]
for o in outcomes:
 label=o['label'];text=(P/'raw_logs'/f'{label}.log').read_text(errors='replace');events=[dict(json.loads(s[7:]),source_log_line=i)for i,s in enumerate(text.splitlines(),1)if s.startswith('STEP22 ')];de=[json.loads(s[8:])for s in text.splitlines()if s.startswith('STEP21C ')];ms=[x for x in de if x.get('event')=='manager_closed'];cc=[e['data']for e in events if e['event']=='cache_closed'];bounds=o.get('boundaries',[])
 resources.append(dict(label=label,case=o['case'],phase=o['phase'],batch=o['batch'],slot=o['slot'],groups=o['single'],passed=o['passed'],reason=o['reason'],peak_rss_kib=o['peak_rss_kib'],peak_threads=o['peak_threads'],go_heap_peak_bytes=max([x.get('host_after',{}).get('host_heap_objects_bytes',0)for x in bounds]+[0]),instances_created=ms[-1]['created']if ms else'',instances_closed=ms[-1]['closed']if ms else'',in_flight_end=ms[-1]['in_flight']if ms else'',stores_created=sum(e['event']=='module' for e in events),stores_closed=cc[-1].get('store_scopes_closed','')if cc else'',store_count_basis='module-owned Store scopes; not native Rc references',store_scopes_closed=cc[-1].get('store_scopes_closed','')if cc else'',modules_closed=cc[-1].get('module_scopes_closed','')if cc else'',managed_remaining=cc[-1]['managed_remaining']if cc else'',managed_pending=(o.get('owner')or{}).get('managed_pending',''),pids_stopped=o['all_owned_processes_stopped'],cgroup_empty=o['cgroup_empty'],max_rss_boundary_kib=max([x.get('VmRSS',0)for x in bounds]+[0]),end_rss_boundary_kib=bounds[-1].get('VmRSS','')if bounds else''))
 for e in events:
  if e['event']in ['module','template']:modules.append(dict(label=label,case=o['case'],phase=o['phase'],event=e['event'],**e['data']))
  if e['event']!='sample':continue
  r=e['data'];r['s1_to_s2_ns']=r['to_s2_ns']-r['to_s1_ns'];r['s2_to_s3_ns']=r['to_s3_ns']-r['to_s2_ns'];rows.append(dict(wasm_family='Step18-P0-plain',source_snapshot_commit=json.loads((P/'audit/SOURCE_SNAPSHOT.json').read_text())['source_snapshot_commit'],code_parent='7eccc36e',config_sha=json.loads((P/'environment.json').read_text())['config_sha'],source_log_line=e['source_log_line'],label=label,case=o['case'],phase=o['phase'],batch=o['batch'],slot=o['slot'],order=o['order'],chunk=o['single'],valid_block=bool(meta.get(label,{}).get('valid',False)),binary_sha256=json.loads((P/'raw_logs'/f'{label}-command.json').read_text())['binary_sha256'],**r))
for b in blocks:
 assert b['valid'];receipts=[];ledgers=[]
 for lab in b['labels']:
  folder=P/'raw_logs'/f'{lab}-receipts'
  for f in sorted(folder.glob('target-G[0-3].json')):
   g=f.stem[-2:];r=json.loads(f.read_text());receipts.append(r);ledgers.append(reconstruct(folder,g,b['case']))
 assert len(receipts)==4 and len(set(ledgers))==1
 for a,r in zip(receipts,receipts[1:]):
  for k in ['business_input','before_hash','after_hash','status','actual_result','actual_rwset']:assert a[k]==r[k],(b['case'],k)
 correct.append(dict(case=b['case'],phase=b['phase'],batch=b['batch'],slot=b['slot'],gas=b['gas'],calls_per_target=1,four_group_parity=True,full_ledger_reconstructed=True,table_identity='not_tested',general_exceptions='not_tested'))
dump('TIMING.csv',rows);dump('RESOURCE_SUMMARY.csv',resources);dump('MODULE_PREPARATION.csv',modules);dump('CORRECTNESS.csv',correct)
main=[r for r in rows if r['phase']=='formal'and r['valid_block']and r['depth']==0 and r['tx_id']=='step33-'+r['case']+'-fixed'];lookup={(r['case'],r['batch'],r['slot'],r['group']):r for r in main}
metrics=['invoke_ns','newinstance_ns','copy_ns','to_s1_ns','s1_to_s2_ns','s2_to_s3_ns','start_ns','callmethod_ns','export_call_ns','close_ns'];summary=[];effects=[];interaction=[];strata=[];stage=[];children=[];batchsummary=[]
for ci,case in enumerate(CASES):
 ids=sorted({(r['batch'],r['slot'])for r in main if r['case']==case})
 if not ids:continue
 assert all((case,*k,g)in lookup for k in ids for g in GROUPS)
 for g in GROUPS:
  for met in metrics:
   aa=[lookup[(case,*k,g)][met]/1e6 for k in ids];summary.append(dict(case=case,group=g,metric=met,N=len(aa),batches=len({k[0]for k in ids}),mean_ms=st.mean(aa),median_ms=st.median(aa),p50_ms=st.median(aa),p95_ms=q(aa,.95)))
  for batch in sorted({k[0]for k in ids}):
   aa=[lookup[(case,*k,g)]['invoke_ns']/1e6 for k in ids if k[0]==batch];batchsummary.append(dict(case=case,group=g,batch=batch,N=len(aa),mean_ms=st.mean(aa),median_ms=st.median(aa),p95_ms=q(aa,.95)))
 for ei,(l,r,name)in enumerate(EDGES):
  ds={k:(lookup[(case,*k,l)]['invoke_ns']-lookup[(case,*k,r)]['invoke_ns'])/1e6 for k in ids};lo,hi=boot(ds,320027+ci*100+ei)
  a=[lookup[(case,*k,l)]['invoke_ns']/1e6 for k in ids];b=[lookup[(case,*k,r)]['invoke_ns']/1e6 for k in ids];bms=[st.median(v for k,v in ds.items()if k[0]==bb)for bb in sorted({k[0]for k in ids})]
  effects.append(dict(case=case,effect=name,left=l,right=r,N=len(ds),batches=len(bms),left_median_ms=st.median(a),right_median_ms=st.median(b),left_p95_ms=q(a,.95),right_p95_ms=q(b,.95),paired_saving_median_ms=st.median(ds.values()),paired_saving_mean_ms=st.mean(ds.values()),ci95_low_ms=lo,ci95_high_ms=hi,positive_fraction=sum(x>0 for x in ds.values())/len(ds),median_pair_relative_percent=st.median(100*ds[k]/(lookup[(case,*k,l)]['invoke_ns']/1e6)for k in ids),batch_medians_ms=json.dumps(bms),all_batches_positive=all(x>0 for x in bms)))
  for kind,vals in [('batch',sorted({k[0]for k in ids})),('left_before_right',[False,True]),('order',sorted({lookup[(case,*k,l)]['order']for k in ids}))]:
   for val in vals:
    ks=[k for k in ids if (k[0]if kind=='batch'else lookup[(case,*k,l)]['order']if kind=='order'else lookup[(case,*k,l)]['order'].split(',').index(l)<lookup[(case,*k,l)]['order'].split(',').index(r))==val]
    if ks:strata.append(dict(case=case,effect=name,stratum=kind,value=val,N=len(ks),paired_saving_median_ms=st.median(ds[k]for k in ks),positive_fraction=sum(ds[k]>0 for k in ks)/len(ks)))
  for met in metrics[1:]:
   a=[(lookup[(case,*k,l)][met]-lookup[(case,*k,r)][met])/1e6 for k in ids];stage.append(dict(case=case,effect=name,metric=met,N=len(a),paired_saving_median_ms=st.median(a),paired_saving_mean_ms=st.mean(a)))
 raw={k:(lookup[(case,*k,'G0')]['invoke_ns']-lookup[(case,*k,'G1')]['invoke_ns']-lookup[(case,*k,'G2')]['invoke_ns']+lookup[(case,*k,'G3')]['invoke_ns'])/1e6 for k in ids};lo,hi=boot(raw,326027+ci)
 interaction.append(dict(case=case,N=len(raw),batches=len({k[0]for k in ids}),formula='G0-G1-G2+G3',interaction_cost_median_ms=st.median(raw.values()),interaction_cost_mean_ms=st.mean(raw.values()),interaction_cost_ci95_low_ms=lo,interaction_cost_ci95_high_ms=hi,synergy_saving_median_ms=-st.median(raw.values()),synergy_ci95_low_ms=-hi,synergy_ci95_high_ms=-lo,synergy_positive_fraction=sum(x<0 for x in raw.values())/len(raw),batch_interaction_cost_medians_ms=json.dumps([st.median(x for k,x in raw.items()if k[0]==b)for b in sorted({k[0]for k in ids})]),interpretation='raw positive=antagonism; negative=synergy'))
 if case=='buyNow':
  for k in ids:
   for g in GROUPS:
    root=lookup[(case,*k,g)];ch=[r for r in rows if r['label']==root['label']and r['group']==g and r['tx_id']==root['tx_id']and r['depth']==1];assert len(ch)==6
    children.append(dict(batch=k[0],slot=k[1],group=g,root_invoke_ms=root['invoke_ns']/1e6,root_export_ms=root['export_call_ns']/1e6,children_sum_invoke_ms=sum(x['invoke_ns']for x in ch)/1e6,root_export_residual_ms=(root['export_call_ns']-sum(x['invoke_ns']for x in ch))/1e6,children_sum_start_ms=sum(x['start_ns']for x in ch)/1e6))
checks=[]
for r in main:
 tests={'newinstance_plus_copy_within_s1':r['newinstance_ns']+r['copy_ns']<=r['to_s1_ns'],'s2_after_s1':r['to_s2_ns']>=r['to_s1_ns'],'s3_after_s2':r['to_s3_ns']>=r['to_s2_ns'],'export_nested_in_callmethod':r['export_call_ns']<=r['callmethod_ns'],'close_within_invoke':r['to_s3_ns']+r['close_ns']<=r['invoke_ns'],'no_business_reuse':not r['reused'],'callmethod_error_empty':r.get('call_error_observed','')in['','<nil>']}
 assert all(tests.values()),(r['label'],r['group'],tests)
 checks.append(dict(label=r['label'],case=r['case'],group=r['group'],batch=r['batch'],slot=r['slot'],**tests,remaining_after_s3_close_ns=r['invoke_ns']-r['to_s3_ns']-r['close_ns']))
dump('TIMING_WINDOW_VALIDATION.csv',checks)
dump('SUMMARY.csv',summary);dump('BATCH_SUMMARY.csv',batchsummary);dump('PAIRED_EFFECTS.csv',effects);dump('INTERACTION_ANALYSIS.csv',interaction);dump('STRATIFIED_EFFECTS.csv',strata);dump('STAGE_EFFECTS.csv',stage);dump('BUY_NOW_WINDOWS.csv',children)
(P/'analysis.json').write_text(json.dumps(dict(valid_formal_blocks=sum(b['phase']=='formal'for b in blocks),formal_root_calls=len(main),formal_real_child_calls=sum(r['phase']=='formal'and r['depth']==1 and r['valid_block']for r in rows),outcomes=len(outcomes),failed=sum(not o['passed']for o in outcomes),valid_by_case={c:len([r for r in main if r['case']==c])//4 for c in CASES},bootstrap='10000 batch to whole block; seed320027+case*100+edge; linear quantile',interaction_sign='positive raw=antagonism; negative raw=synergy'),indent=2))
dump('INPUT_MANIFEST.csv',[dict(case=c['case'],path=c['file'],sha256=hashlib.sha256(Path(c['file']).read_bytes()).hexdigest(),max_groups_per_process=c['max_groups_per_process'])for c in CASE_META.values()])
print('ANALYZED',len(main),'formal roots;',len(blocks),'all valid blocks; outcomes',len(outcomes),flush=True)
if children:
 d={(r['batch'],r['slot'],r['group']):r for r in children};out=[]
 for l,r,name in EDGES:
  for met in ['root_invoke_ms','root_export_ms','children_sum_invoke_ms','root_export_residual_ms','children_sum_start_ms']:
   vals=[d[(b,sl,l)][met]-d[(b,sl,r)][met]for b,sl,g in d if g==l];out.append(dict(effect=name,left=l,right=r,metric=met,N=len(vals),paired_saving_median_ms=st.median(vals),paired_saving_mean_ms=st.mean(vals)))
 dump('BUY_NOW_PAIRED_WINDOWS.csv',out)
