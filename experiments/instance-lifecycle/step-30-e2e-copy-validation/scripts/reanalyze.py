"""Offline historical Step20 replay. Never launches a node, client or compiler."""
from pathlib import Path
from collections import defaultdict,Counter
import json,csv,base64,statistics as st,math,hashlib
P=Path(__file__).resolve().parents[1];RAW=P/'raw_logs/historical-step20'
def write(name,rows,fields=None):
 keys=fields or list(dict.fromkeys(k for r in rows for k in r))
 with(P/name).open('w',newline='')as f:w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
def stats(a):return dict(n=len(a),mean_ms=st.mean(a)/1e6,median_ms=st.median(a)/1e6,p95_ms=sorted(a)[math.ceil(.95*len(a))-1]/1e6)
rows=[];vms=[];resources=[];pairs=[];summary=[];effects=[];throughput=[];checks=[]
for label in ['low-smoke','low-a']:
 index=defaultdict(list)
 for endpoint in ['baseline','optimized']:
  file=RAW/f'{label}-{endpoint}-vm.log'
  for line,s in enumerate(file.read_text().splitlines(),1):
   if not s.startswith('STEP17 '):continue
   r=json.loads(s[7:])
   if r['kind']=='pool':assert r['fresh']and r['source_sha']=='e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507';continue
   if r['kind']!='invoke':continue
   vms.append(dict(origin_step=20,is_step30_new=False,label=label,endpoint=endpoint,source_file=str(file.relative_to(P)),source_line=line,**r));index[endpoint,r['tx_id']].append(r)
 file=RAW/f'{label}-requests.jsonl';jobs=[json.loads(s)for s in file.read_text().splitlines()];local=[]
 for line,r in enumerate(jobs,1):
  resp=r.get('response')or{};cr=resp.get('contract_result')or{};tx=resp.get('tx_id');vm=[x for x in index[r['endpoint'],tx]if x['depth']==0];success=not r.get('error')and resp.get('code',0)==0 and cr.get('code',0)==0
  assert success and len(vm)==1 and base64.b64decode(cr['result'])==b'success bigNumCal: 607723520'and cr['gas_used']==106028 and resp['tx_block_height']>0
  assert all(x['gas']==106028 and x['code']==0 and x['optimized']==(r['mode']=='optimized')for x in vm)
  sample=dict(origin_step=20,is_step30_new=False,row_kind='completed_response',label=label,phase=r['phase'],pair=r['pair'],group='G0'if r['mode']=='baseline'else'G1',endpoint=r['endpoint'],request_id=r['tag'],tx_id=tx,client_elapsed_ns=r['elapsed_ns'],sdk_begin_mono_ns='',sdk_end_mono_ns='',driver_send_mono_ns=r['driver_send_mono_ns'],driver_receive_mono_ns=r['driver_receive_mono_ns'],client_success=True,response_code=resp.get('code',0),business_code=cr.get('code',0),gas=cr['gas_used'],result_base64=cr['result'],response_block_height=resp['tx_block_height'],commit_evidence='node synchronous result with positive block height; not independently ledger-verified',commit_complete_mono_ns='',root_attempts=len(vm),sum_root_invoke_ns=sum(x['invoke_ns']for x in vm),s1_ns=vm[-1]['s1_ns'],s2_ns=vm[-1]['s2_ns'],s3_ns=vm[-1]['s3_ns'],copy_ns=vm[-1]['copy_ns'],wasi_plus_start_ns=vm[-1]['s2_ns']-vm[-1]['s1_ns'],newinstance_ns='',start_only_ns='',callmethod_ns='',close_ns='',addtx_to_vm_ns='',instance_id=vm[-1]['instance_id'],source_client_file=str(file.relative_to(P)),source_client_line=line,validity='historical_resource_censored_partial_batch'if label=='low-a'else'historical_small_smoke')
  sample['client_minus_sum_root_ns']=sample['client_elapsed_ns']-sample['sum_root_invoke_ns'];rows.append(sample);local.append(sample)
 formal=[r for r in local if r['phase']=='warm'];pg=defaultdict(dict)
 for r in formal:pg[r['pair']][r['group']]=r
 matched=[(i,g['G0'],g['G1'])for i,g in sorted(pg.items())if set(g)=={'G0','G1'}]
 for i,b,o in matched:
  assert(b['gas'],b['result_base64'])==(o['gas'],o['result_base64']);first='G0'if b['driver_send_mono_ns']<o['driver_send_mono_ns']else'G1'
  pairs.append(dict(origin_step=20,is_step30_new=False,label=label,pair=i,first_group=first,g0_tx=b['tx_id'],g1_tx=o['tx_id'],client_saved_ns=b['client_elapsed_ns']-o['client_elapsed_ns'],root_vm_saved_ns=b['sum_root_invoke_ns']-o['sum_root_invoke_ns'],remainder_saved_ns=b['client_minus_sum_root_ns']-o['client_minus_sum_root_ns']))
 for g in ['G0','G1']:
  allg=[r for r in formal if r['group']==g];matchedg=[b if g=='G0'else o for _,b,o in matched]
  for scope,gr in [('all_completed_formal',allg),('complete_pairs_only',matchedg)]:
   for metric in ['client_elapsed_ns','sum_root_invoke_ns','s1_ns','copy_ns','wasi_plus_start_ns','client_minus_sum_root_ns']:summary.append(dict(origin_step=20,is_step30_new=False,label=label,group=g,scope=scope,metric=metric,**stats([r[metric]for r in gr]),validity=gr[0]['validity']))
  begin=min(r['driver_send_mono_ns']for r in allg);end=max(r['driver_receive_mono_ns']for r in allg);secs=(end-begin)/1e9
  common=dict(origin_step=20,is_step30_new=False,label=label,group=g,status='historical_descriptive',window_begin_driver_mono_ns=begin,window_end_driver_mono_ns=end,window_wall_seconds=secs)
  throughput.append(dict(**common,metric='client_success_response_rate',numerator=len(set(r['tx_id']for r in allg)),denominator_seconds=secs,value_per_second=len(allg)/secs,definition='successful unique responses / driver observation wall span; includes alternating other endpoint requests; not saturated node TPS'))
  throughput.append(dict(**common,metric='independently_confirmed_commit_tps',numerator='',denominator_seconds='',value_per_second='',definition='missing independent ledger commit event/window; synchronous block height alone not this window'))
  throughput.append(dict(**common,metric='vm_factory_equivalent_tps',numerator='',denominator_seconds='',value_per_second='',definition='missing per-Tx vm_factory outer timer; STEP17 timer begins after root lock'))
  seconds=sum(r['sum_root_invoke_ns']for r in allg)/1e9
  throughput.append(dict(**common,metric='step17_inner_root_vm_equivalent_rate',numerator=len(allg),denominator_seconds=seconds,value_per_second=len(allg)/seconds,definition='N / sum STEP17 after-lock root Invoke seconds; not Wang exact timer, not node throughput'))
 for metric,key in [('client_elapsed_ns','client_saved_ns'),('sum_root_invoke_ns','root_vm_saved_ns'),('client_minus_sum_root_ns','remainder_saved_ns')]:
  a=[p[key]for p in pairs if p['label']==label];effects.append(dict(origin_step=20,is_step30_new=False,label=label,left='G0',right='G1',metric=metric,n=len(a),paired_save_median_ms=st.median(a)/1e6,paired_save_mean_ms=st.mean(a)/1e6,positive_count=sum(x>0 for x in a),ci95_low_ms='',ci95_high_ms='',ci_status='not_estimated_for_censored_single_partial_batch'if label=='low-a'else'not_estimated_small_smoke',status='historical_descriptive_only'))
 rr=[json.loads(s)for s in(RAW/f'{label}-resources.jsonl').read_text().splitlines()]
 for endpoint in ['baseline','optimized']:
  a=[x for x in rr if x['endpoint']==endpoint];warm=[x for x in a if x['phase']=='warm'];first,last=warm[0],warm[-1];resources.append(dict(origin_step=20,is_step30_new=False,label=label,endpoint=endpoint,rss_peak_mib=max(x['VmRSS']for x in a)/1024,first_warm_rss_mib=first['VmRSS']/1024,last_rss_mib=last['VmRSS']/1024,rss_growth_warm_mib=(last['VmRSS']-first['VmRSS'])/1024,threads_peak=max(x['Threads']for x in a),go_heap_bytes='',go_heap_status='not_collected',rss_soft_limit_mib=2560,threads_soft_limit=220,node_memorymax_mib=3072,stop_error=json.loads((RAW/f'{label}-status.json').read_text()).get('error',''),status='historical_actual_sampled_peak'))
 checks.append(dict(origin_step=20,label=label,completed_responses=len(local),paired_formal=len(matched),all_saved_responses_success=True,gas_set='106028',root_attempts_per_response=1,commit_status='node reported sync result with block height',independent_commit_status='not_verified',rwset='not_collected',events='response_only; not_independently_verified',final_ledger='not_verified',rollback='not_tested',new_step30=False))
assert len(rows)==207 and len(vms)==207 and len({r['tx_id']for r in rows})==207 and len({r['instance_id']for r in rows})==207
pending=json.loads((RAW/'incomplete_request.json').read_text());rows.append(dict(origin_step=20,is_step30_new=False,row_kind='resource_censored_request',label='low-a',phase='warm',pair=88,group='G0',request_id='',tx_id='',client_elapsed_ns='',client_success='',commit_evidence='unknown: queued to client pipe; SDK start/TxID/response not captured',validity='excluded_no_completed_response; retained',source_client_file='raw_logs/historical-step20/incomplete_request.json'))
for left,right in [('G0','G1'),('G0','G2')]:effects.append(dict(origin_step=30,is_step30_new=True,label='step30_not_run',left=left,right=right,metric='client_elapsed_ns',n=0,paired_save_median_ms='',paired_save_mean_ms='',ci95_low_ms='',ci95_high_ms='',ci_status='not_measured',status='blocked_store_owner_finalizer_and_resource_gate'))
for g in ['G0','G1','G2']:
 for metric in ['client_success_response_rate','independently_confirmed_commit_tps','vm_factory_equivalent_tps']:throughput.append(dict(origin_step=30,is_step30_new=True,label='step30_not_run',group=g,status='blocked_not_measured',metric=metric,numerator='',denominator_seconds='',value_per_second='',definition='no new client/node request executed'))
write('E2E_SAMPLES.csv',rows);write('PAIRED_EFFECTS.csv',effects);write('THROUGHPUT.csv',throughput);write('RESOURCE_SUMMARY.csv',resources);write('historical/VM_INVOCATIONS.csv',vms);write('historical/PAIR_DELTAS.csv',pairs);write('historical/SUMMARY.csv',summary);write('historical/CORRECTNESS.csv',checks)
write('EXECUTION_STATUS.csv',[dict(group=g,planned_blocks=60,new_completed_blocks=0,new_requests_sent=0,status='blocked',reason='node binary lacks proven Store owner/finalizer protocol; prior RSS growth unresolved'+('; same-family A node integration missing'if g=='G2'else''))for g in ['G0','G1','G2']])
for p in pairs:assert p['client_saved_ns']==p['root_vm_saved_ns']+p['remainder_saved_ns']
(P/'audit/reanalysis-check.json').write_text(json.dumps(dict(new_step30_requests=0,historical_completed_responses=207,historical_unique_txids=207,historical_root_vm_events=207,historical_low_a_complete_pairs=88,historical_low_a_unpaired_completed=1,historical_pending_unknown=1,per_pair_mean_accounting_identity=True,historical_rwsets_final_ledger_missing=True,cross_process_timestamp_subtraction=False),indent=2)+'\n')
print('offline Step20 reanalysis complete: 207 historical responses +1 censored; 0 new Step30 requests')
