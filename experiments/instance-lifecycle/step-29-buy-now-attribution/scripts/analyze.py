from pathlib import Path
import csv,json,statistics as st,random,hashlib,base64
from spans import P,extract,within,duration
from check_pair import check

def dump(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/name).open('w',newline='')as f:w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
def q(a,p):
 a=sorted(a);pos=(len(a)-1)*p;i=int(pos);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(pos-i)
def bootstrap(ds,seed):
 rng=random.Random(seed);bs=sorted(set(k[0]for k in ds));dist=[]
 for _ in range(10000):
  vals=[]
  for b in rng.choices(bs,k=len(bs)):
   ks=[k for k in ds if k[0]==b];vals.extend(ds[k]for k in rng.choices(ks,k=len(ks)))
  dist.append(st.median(vals))
 return q(dist,.025),q(dist,.975)
def js(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
def h(x):return hashlib.sha256(js(x)).hexdigest()
def apply(l,r):
 if r.get('status',0)!=0 or r['actual_result'].get('code',0)!=0:return
 for w in r['actual_rwset'].get('tx_writes',[]):
  d=l.setdefault(w['contract_name'],{});k=base64.b64decode(w['key']).decode()
  if 'value'in w:d[k]=w['value']
  else:d.pop(k,None)
def ledger(folder,g,exception):
 rr=json.loads((folder/f'setup-identity-{g}.json').read_text());read=next(x for x in rr['actual_rwset']['tx_reads']if x['contract_name']=='CHAIN_CONFIG');l={'CHAIN_CONFIG':{'CHAIN_CONFIG':read['value']}}
 for c in ['identity','erc721','exchange']:
  r=json.loads((folder/f'setup-{c}-{g}.json').read_text());assert h(l)==r['before_hash'];apply(l,r);assert h(l)==r['after_hash']
 if exception=='duplicate':l['erc721']['tokenIds#1']=base64.b64encode(b'8acfaca5eeec9f6f7c23c4ffac969b86f27799b0').decode()
 before=json.loads(json.dumps(l));r=json.loads((folder/f'target-{g}.json').read_text());assert h(l)==r['before_hash'];apply(l,r);assert h(l)==r['after_hash']
 (folder/f'target-{g}-ledger.json').write_text(json.dumps(dict(initial=before,final=l,initial_sha=h(before),final_sha=h(l),derivation='replay real committed RW sets; native snapshot SHA256 verified'),indent=2)+'\n')
 return l
outcomes=[json.loads(f.read_text())for f in sorted((P/'raw_logs').glob('*-outcome.json'))];blocks=[json.loads(f.read_text())for f in sorted((P/'raw_logs').glob('*-block.json'))];valid={label:b for b in blocks for label in b['labels']};timing=[];roots=[];res=[];spans=[];children=[];correct=[];prep=[]
for o in outcomes:
 label=o['label'];text=(P/'raw_logs'/f'{label}.log').read_text();events=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP22 ')];ds=[json.loads(l[8:])for l in text.splitlines()if l.startswith('STEP21C ')];manager=[x for x in ds if x['event']=='manager_closed'][-1]
 command=json.loads((P/'raw_logs'/f'{label}-command.json').read_text());meta=dict(label=label,mode='trace'if o['trace']else'plain',batch=o['batch'],slot=o['slot'],phase=o['phase'],group=o['single'],order=o['order'],binary_sha256=command['binary_sha256'],parent_commit='29950ab',valid_block=label in valid)
 res.append(dict(**meta,passed=o['passed'],peak_rss_kib=o['peak_rss_kib'],peak_threads=o['peak_threads'],heap_peak_boundary=max([x['host_after']['host_heap_objects_bytes']for x in o['boundaries']]+[0]),created=manager['created'],closed=manager['closed'],managed_end=o['owner']['managed_objects'],managed_pending=o['owner']['managed_pending'],cgroup_empty=o['cgroup_empty'],all_owned_processes_stopped=o['all_owned_processes_stopped']))
 samples=[x['data']for x in events if x['event']=='sample']
 for x in events:
  if x['event']in['template','module']:prep.append(dict(**meta,event=x['event'],**{k:v for k,v in x['data'].items()if k!='group'}))
 for r in samples:timing.append(dict(**meta,**{k:v for k,v in r.items()if k!='group'}))
 target=[r for r in samples if r['tx_id']=='step28-buyNow-fixed'];root=next(r for r in target if r['depth']==0)
 if not o['exception']:
  assert len(target)==7;child=[r for r in target if r['depth']==1]
  m=dict(root);m['root_export_residual_ns']=root['export_call_ns']-sum(x['invoke_ns']for x in child);m['children_invoke_sum_ns']=sum(x['invoke_ns']for x in child)
  m['all7_newinstance_plus_copy_ns']=sum(x['newinstance_ns']+x['copy_ns']for x in target);m['all7_start_ns']=sum(x['start_ns']for x in target);m['all7_close_ns']=sum(x['close_ns']for x in target)
  if o['trace']:
   extra,detail,ss=extract(label);assert extra['root_export_ns']==root['export_call_ns'];assert extra['children_invoke_sum_ns']==m['children_invoke_sum_ns'];m.update(extra)
   if not any(x['kind']=='fixture_bytecode_clone'for x in ss):
    for k in ['fixture_bytecode_clone_outside_child_ns','fixture_contract_metadata_outside_child_ns','manager_logger_infof_outside_child_ns','manager_logger_debugf_outside_child_ns']:m[k]=None
   for r in detail:children.append(dict(**meta,**r))
   for r in ss:spans.append(dict(**meta,**r))
  roots.append(dict(**meta,**{k:v for k,v in m.items()if k!='group'}))
for b in blocks:
 finals=[];receipts=[]
 for label in b['labels']:
  o=next(o for o in outcomes if o['label']==label);assert o['passed'];folder=P/'raw_logs'/f'{label}-receipts';finals.append(ledger(folder,o['single'],o['exception']));receipts.append(json.loads((folder/f"target-{o['single']}.json").read_text()))
 assert finals[0]==finals[1]==finals[2]
 if not b['exception']:check(receipts[0],receipts[1],True);check(receipts[1],receipts[2],True)
 correct.append(dict(phase=b['phase'],trace=b['trace'],batch=b['batch'],slot=b['slot'],exception=b['exception'],gas=receipts[0]['actual_result'].get('gas_used',0),all_three_semantic_equal=True,final_ledger_equal=True,call_count=len(receipts[0]['inclusive_call_records_do_not_sum']),table_identity='not_tested'))
main=[r for r in roots if r['phase']=='formal'and r['valid_block']];effects=[];summary=[];strata=[]
base_metrics=['invoke_ns','newinstance_ns','copy_ns','start_ns','export_call_ns','callmethod_ns','close_ns','to_s1_ns','to_s2_ns','to_s3_ns','root_export_residual_ns','children_invoke_sum_ns','all7_newinstance_plus_copy_ns','all7_start_ns','all7_close_ns']
trace_metrics=['root_syscall_sum_ns','root_syscall_excluding_child_ns','outside_observed_root_syscall_ns','cross_prepare_sum_ns','cross_return_sum_ns','cross_no_child_wacsi_ns','cross_get_gas_ns','cross_set_gas_ns','final_get_gas_ns','fixture_bytecode_clone_outside_child_ns','fixture_contract_metadata_outside_child_ns','manager_logger_infof_outside_child_ns','manager_logger_debugf_outside_child_ns','json_encode_STEP22_outside_child_ns','json_encode_STEP21C_outside_child_ns','stdout_STEP22_outside_child_ns','stdout_STEP21C_outside_child_ns']
for mode in ['plain','trace']:
 rr=[r for r in main if r['mode']==mode];lookup={(r['batch'],r['slot'],r['group']):r for r in rr};ids=sorted(set((r['batch'],r['slot'])for r in rr));metrics=base_metrics+(trace_metrics if mode=='trace'else[])
 for g in ['G0','G1','G2']:
  for metric in metrics:
   a=[r[metric]/1e6 for r in rr if r['group']==g];summary.append(dict(mode=mode,group=g,metric=metric,n=len(a),mean_ms=st.mean(a),median_ms=st.median(a),p95_ms=q(a,.95)))
 for edge,(left,right)in enumerate([('G0','G1'),('G1','G2'),('G0','G2')]):
  for mi,metric in enumerate(metrics):
   ds={k:(lookup[(*k,left)][metric]-lookup[(*k,right)][metric])/1e6 for k in ids};lo,hi=bootstrap(ds,290029+mi*10+edge)
   la=[lookup[(*k,left)][metric]/1e6 for k in ids];ra=[lookup[(*k,right)][metric]/1e6 for k in ids]
   effects.append(dict(mode=mode,left=left,right=right,metric=metric,n=len(ds),paired_save_median_ms=st.median(ds.values()),paired_save_mean_ms=st.mean(ds.values()),ci95_low_ms=lo,ci95_high_ms=hi,positive_count=sum(v>0 for v in ds.values()),left_median_ms=st.median(la),right_median_ms=st.median(ra),left_p95_ms=q(la,.95),right_p95_ms=q(ra,.95)))
   if metric in ['invoke_ns','root_export_residual_ns','cross_prepare_sum_ns','fixture_bytecode_clone_outside_child_ns']:
    for typ in ['batch','left_before_right']:
     for value in ([1,2,3]if typ=='batch'else[True,False]):
      ks=[k for k in ids if(k[0]if typ=='batch'else lookup[(*k,left)]['order'].split(',').index(left)<lookup[(*k,left)]['order'].split(',').index(right))==value]
      if ks:strata.append(dict(mode=mode,left=left,right=right,metric=metric,stratum=typ,value=value,n=len(ks),paired_save_median_ms=st.median(ds[k]for k in ks)))
lookup={(r['batch'],r['slot'],r['mode'],r['group']):r for r in main};ids=sorted(set((r['batch'],r['slot'])for r in main));obs=[]
for g in ['G0','G1','G2']:
 for metric in ['invoke_ns','root_export_residual_ns']:
  ds={k:(lookup[(*k,'trace',g)][metric]-lookup[(*k,'plain',g)][metric])/1e6 for k in ids};lo,hi=bootstrap(ds,290039)
  obs.append(dict(group=g,metric=metric,n=len(ds),trace_minus_plain_median_ms=st.median(ds.values()),ci95_low_ms=lo,ci95_high_ms=hi))
for b,s in ids:
 for g in ['G0','G1','G2']:
  labels=[lookup[b,s,mode,g]['label']for mode in ['plain','trace']];rs=[json.loads((P/'raw_logs'/f'{label}-receipts'/f'target-{g}.json').read_text())for label in labels];check(rs[0],rs[1],True)
dump('TIMING.csv',timing);dump('ROOT_TIMING.csv',roots);dump('SUMMARY.csv',summary);dump('PAIRED_EFFECTS.csv',effects);dump('STRATIFIED_EFFECTS.csv',strata);dump('OBSERVATION_EFFECTS.csv',obs);dump('RESOURCE_SUMMARY.csv',res);dump('CORRECTNESS.csv',correct);dump('HOST_SPANS.csv',spans);dump('CHILD_PREPARATION.csv',children);dump('MODULE_PREPARATION.csv',prep)
(P/'analysis.json').write_text(json.dumps(dict(formal_roots=len(main),formal_triple_blocks=sum(b['phase']=='formal'for b in blocks),processes=len(outcomes),failures=sum(not o['passed']for o in outcomes),original_family='Step18 P0/plain, unchanged Step28 WASM',new_and_historical_samples_not_mixed=True),indent=2)+'\n')
print('analyzed',len(main),'formal roots')
variants=json.loads((P/'inputs/variants.json').read_text());volume=[];shares={}
for g in ['G0','G1','G2']:
 sizes={c:Path(variants[c+'-'+g]['path']).stat().st_size for c in ['identity','erc721']}
 volume.append(dict(group=g,identity_wasm_bytes=sizes['identity'],erc721_wasm_bytes=sizes['erc721'],loads_identity=3,loads_erc721=3,root_export_fixture_clone_bytes=3*sum(sizes.values())))
 a=[x for x in main if x['mode']=='trace'and x['group']==g];shares[g]=dict(clone_fraction_of_prepare_median=st.median(x['fixture_bytecode_clone_outside_child_ns']/x['cross_prepare_sum_ns']for x in a),clone_fraction_of_residual_median=st.median(x['fixture_bytecode_clone_outside_child_ns']/x['root_export_residual_ns']for x in a))
dump('BYTECODE_VOLUME.csv',volume);(P/'audit/clone-share.json').write_text(json.dumps(shares,indent=2)+'\n')
