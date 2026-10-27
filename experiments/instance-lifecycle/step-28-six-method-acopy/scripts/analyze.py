from pathlib import Path
import json,csv,statistics as st,random,math,hashlib,base64,itertools
P=Path(__file__).resolve().parents[1]
def dump(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (P/name).open('w',newline='')as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
def q(a,p):
 a=sorted(a);pos=(len(a)-1)*p;i=int(pos);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(pos-i)
def js(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').encode()
def h(x):return hashlib.sha256(js(x)).hexdigest()
def apply(ledger,r):
 if r.get('status',0)!=0 or r['actual_result'].get('code',0)!=0:return
 for w in r['actual_rwset'].get('tx_writes',[]):
  c=w['contract_name'];k=base64.b64decode(w['key']).decode();ledger.setdefault(c,{})
  if 'value'not in w:ledger[c].pop(k,None)
  else:ledger[c][k]=w['value']
def ledger(folder,g,case,exception=''):
 config_receipt=json.loads((P/'raw_logs/preflight-buyNow-b1-s01-G0-receipts/setup-identity-G0.json').read_text())
 config_reads=[w for w in config_receipt['actual_rwset']['tx_reads']if w['contract_name']=='CHAIN_CONFIG'];assert len(config_reads)==1
 l={'CHAIN_CONFIG':{'CHAIN_CONFIG':config_reads[0]['value']}};names=['identity','erc721','exchange']if case=='buyNow'else[{'bigNumCal':'compute','hashCal':'compute','normalCal':'compute'}.get(case,case)]
 for c in names:
  r=json.loads((folder/f'setup-{c}-{g}.json').read_text());assert h(l)==r['before_hash'];apply(l,r);assert h(l)==r['after_hash']
 if exception=='duplicate':l['erc721']['tokenIds#1']=base64.b64encode(b'8acfaca5eeec9f6f7c23c4ffac969b86f27799b0').decode()
 initial=json.loads(json.dumps(l));r=json.loads((folder/f'target-{g}.json').read_text());assert h(l)==r['before_hash'];apply(l,r);assert h(l)==r['after_hash']
 # Derived from actual committed RW sets and verified against in-process full-ledger SHA256.
 (folder/f'target-{g}-ledger.json').write_text(json.dumps(dict(initial=initial,final=l,derivation='replayed actual successful RW sets; verified exact native ledger SHA256',initial_sha=h(initial),final_sha=h(l)),indent=2)+'\n')
 return l
blocks=[json.loads(f.read_text())for f in sorted((P/'raw_logs').glob('*-block.json'))];outcomes=[json.loads(f.read_text())for f in sorted((P/'raw_logs').glob('*-outcome.json'))]
build=json.loads((P/'environment.json').read_text());fingerprint=hashlib.sha256(js(build['source_hashes'])).hexdigest()
bylabel={r['label']:r for r in outcomes};meta={label:b for b in blocks for label in b['labels']};timing=[];roots={};resources=[];prep=[];correct=[]
for o in outcomes:
 label=o['label'];text=(P/'raw_logs'/f'{label}.log').read_text();events=[json.loads(s[7:])for s in text.splitlines()if s.startswith('STEP22 ')];devents=[json.loads(s[8:])for s in text.splitlines()if s.startswith('STEP21C ')]
 managers=[x for x in devents if x.get('event')=='manager_closed']
 resources.append(dict(label=label,case=o['case'],phase=o['phase'],batch=o['batch'],slot=o['slot'],single=o['single'],passed=o['passed'],peak_rss_kib=o['peak_rss_kib'],peak_threads=o['peak_threads'],all_owned_processes_stopped=o['all_owned_processes_stopped'],cgroup_empty=o['cgroup_empty'],created=managers[-1]['created']if managers else'',closed=managers[-1]['closed']if managers else'',managed_end=o.get('owner',{}).get('managed_objects',''),managed_pending=o.get('owner',{}).get('managed_pending',''),go_heap_peak_boundary=max([x.get('host_after',{}).get('host_heap_objects_bytes',0)for x in o['boundaries']]+[0])))
 for x in events:
  if x['event']in['module','template']:prep.append(dict(label=label,case=o['case'],phase=o['phase'],event=x['event'],**x['data']))
  if x['event']!='sample':continue
  r=x['data'];r['s1_to_s2_ns']=r['to_s2_ns']-r['to_s1_ns'];r['s2_to_s3_ns']=r['to_s3_ns']-r['to_s2_ns'];row=dict(code_snapshot_commit='e7924d8',execution_git_head='c8c46ee + recorded experiment files',code_parent='c8c46ee',guest_source_commit='95903a3',host_source_fingerprint=fingerprint,binary_sha256=build['binary_sha'],label=label,case=o['case'],phase=o['phase'],batch=o['batch'],slot=o['slot'],order=o['order'],single=o['single'],valid_block=bool(meta.get(label,{}).get('valid',False)),**r);timing.append(row)
  if r['tx_id']==f"step28-{o['case']}-fixed" and r['depth']==0 and label in meta:roots[(o['case'],o['phase'],o['batch'],o['slot'],r['group'])]=row
for b in blocks:
 finals=[]
 for label in b['labels']:
  o=bylabel[label];assert o['passed'];folder=P/'raw_logs'/f'{label}-receipts'
  for g in ([o['single']]if o['single']else ['G0','G1','G2']):finals.append(ledger(folder,g,b['case']))
 assert finals[0]==finals[1]==finals[2]
 correct.append(dict(case=b['case'],phase=b['phase'],batch=b['batch'],slot=b['slot'],gas=b['parity']['gas'],calls=b['parity']['calls'],gas_result_rwset_events=True,full_final_ledger=True,root_children_parity=True,valid=True,table_function_identity='not_tested',general_exception_paths='not_tested'))
for o in outcomes:
 if o['exception']:ledger(P/'raw_logs'/f"{o['label']}-receipts",o['single'],'buyNow',o['exception'])
main=[r for r in timing if r['phase']=='formal'and r['depth']==0 and r['tx_id']==f"step28-{r['case']}-fixed"and r['valid_block']]
metrics=['invoke_ns','s1_to_s2_ns','s2_to_s3_ns','newinstance_ns','copy_ns','to_s1_ns','to_s2_ns','to_s3_ns','start_ns','wasi_initialize_ns','wasi_imports_ns','export_call_ns','callmethod_ns','close_ns']
summary=[];effects=[];strata=[];stages=[]
for ci,case in enumerate(['bigNumCal','hashCal','normalCal','fact','erc721','buyNow']):
 rows=[r for r in main if r['case']==case]
 if not rows:continue
 batches=sorted(set(r['batch']for r in rows));ids=sorted(set((r['batch'],r['slot'])for r in rows));lookup={(r['batch'],r['slot'],r['group']):r for r in rows}
 for g in ['G0','G1','G2']:
  gr=[r for r in rows if r['group']==g]
  for metric in metrics:
   a=[r[metric]/1e6 for r in gr];summary.append(dict(case=case,group=g,metric=metric,n=len(a),batches=len(batches),mean_ms=st.mean(a),median_ms=st.median(a),p95_ms=q(a,.95)))
 for ei,(left,right)in enumerate([('G0','G1'),('G1','G2'),('G0','G2')]):
  ds={k:(lookup[(*k,left)]['invoke_ns']-lookup[(*k,right)]['invoke_ns'])/1e6 for k in ids};dist=[];rng=random.Random(280027+ci*10+ei)
  for rep in range(10000):
   sampled=[]
   for b in rng.choices(batches,k=len(batches)):
    ks=[k for k in ids if k[0]==b];sampled.extend(ds[k]for k in rng.choices(ks,k=len(ks)))
   dist.append(st.median(sampled))
  la=[lookup[(*k,left)]['invoke_ns']/1e6 for k in ids];ra=[lookup[(*k,right)]['invoke_ns']/1e6 for k in ids];positive=sum(v>0 for v in ds.values())
  effects.append(dict(case=case,left=left,right=right,n=len(ds),batches=len(batches),paired_save_median_ms=st.median(ds.values()),paired_save_mean_ms=st.mean(ds.values()),ci95_low_ms=q(dist,.025),ci95_high_ms=q(dist,.975),positive_count=positive,positive_fraction=positive/len(ds),left_median_ms=st.median(la),right_median_ms=st.median(ra),left_p95_ms=q(la,.95),right_p95_ms=q(ra,.95),p95_change_ms=q(ra,.95)-q(la,.95),median_pair_relative_percent=st.median([100*ds[k]/(lookup[(*k,left)]['invoke_ns']/1e6)for k in ids])))
  for typ in ['batch','order','left_before_right']:
   keys=set(k[0]for k in ids)if typ=='batch'else set(lookup[(*k,left)]['order']for k in ids)if typ=='order'else{True,False}
   for value in sorted(keys):
    ks=[k for k in ids if(k[0]if typ=='batch'else lookup[(*k,left)]['order']if typ=='order'else lookup[(*k,left)]['order'].split(',').index(left)<lookup[(*k,left)]['order'].split(',').index(right))==value]
    if ks:strata.append(dict(case=case,left=left,right=right,stratum=typ,value=value,n=len(ks),paired_save_median_ms=st.median(ds[k]for k in ks),positive_count=sum(ds[k]>0 for k in ks)))
  for metric in metrics:
   v=[(lookup[(*k,left)][metric]-lookup[(*k,right)][metric])/1e6 for k in ids];stages.append(dict(case=case,left=left,right=right,metric=metric,n=len(v),paired_save_median_ms=st.median(v),paired_save_mean_ms=st.mean(v),positive_fraction=sum(x>0 for x in v)/len(v)))
dump('TIMING.csv',timing);dump('SUMMARY.csv',summary);dump('PAIRED_EFFECTS.csv',effects);dump('STRATIFIED_EFFECTS.csv',strata);dump('STAGE_EFFECTS.csv',stages);dump('RESOURCE_SUMMARY.csv',resources);dump('MODULE_PREPARATION.csv',prep);dump('CORRECTNESS.csv',correct)
(P/'analysis.json').write_text(json.dumps(dict(blocks=len(blocks),formal_blocks=sum(b['phase']=='formal'for b in blocks),formal_calls=len(main),processes=len(outcomes),failed_processes=sum(not o['passed']for o in outcomes),bootstrap='10000 hierarchical batch→whole-block; fixed seed280027 +case*10+edge; linear percentile',effects=effects),indent=2)+'\n')
print('analyzed',len(main),'formal roots;',len(effects),'effects')
