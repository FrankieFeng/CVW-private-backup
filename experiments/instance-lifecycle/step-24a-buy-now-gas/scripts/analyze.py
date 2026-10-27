"""Recompute every output from retained events/outcomes; no timing/TPS inference."""
from pathlib import Path
import csv,json,collections
from compare import load,compare,digest,shape
P=Path(__file__).resolve().parents[1]
def write(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/name).open('w')as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
allruns=[];traces=[];calls=[];warm=[];summ=[];state=[];pairs=[];resources=[]
for path in sorted((P/'raw_logs').glob('*-outcome.json')):
 o=json.loads(path.read_text());label=o['label'];allruns.append(o|{'eligible_formal':o['passed'] and o['stage']=='formal' and label.startswith('safe-')})
 events=[json.loads(l)for l in(P/'raw_logs'/f'{label}-events.jsonl').read_text().splitlines()]
 life=[json.loads(l[8:])for l in(P/'raw_logs'/f'{label}.log').read_text().splitlines()if l.startswith('STEP21C ')]
 end=next(e for e in life if e['event']=='owner_closed');manager=next(e for e in life if e['event']=='manager_closed')
 assert end['managed_objects']==0 and end['managed_pending']==0 and manager['created']==manager['closed'] and manager['in_flight']==0
 resources.append({'label':label,'eligible':o['passed'],'stage':o['stage'],'condition':o['condition'],'created':manager['created'],'closed':manager['closed'],'managed_remaining':end['managed_objects'],'pending_remaining':end['managed_pending'],'owner_end_threads':end['Threads'],'owner_end_rss_kib':end['VmRSS'],'peak_sampled_threads':o['peak_sampled_threads'],'peak_sampled_rss_kib':o['peak_sampled_rss_kib']})
 for e in events:
  if e['event']=='gas':traces.append({'label':label,'eligible':o['passed'],'stage':o['stage'],'block':o['block'],'condition':o['condition'],**{k:v for k,v in e.items()if k not in ['event','condition','experiment_stage','run_label','block']}})
  if e['event']=='warm_record':warm.append({'label':label,'stage':o['stage'],'block':o['block'],**e})
 if not o['passed']:continue
 d=load(label)
 assert not any(e['event']=='json_cache'for e in events),'live reader unexpectedly enabled'
 assert len([e for e in events if e['event']=='original_module_prepared'])==3
 assert all(e['copy_enabled']==False for e in events if e['event']in ['original_module_prepared','root_checked'])
 if o['stage']!='formal':continue
 for c in d['calls']:
  calls.append({'label':label,'block':o['block'],'condition':o['condition'],**{k:c[k] for k in ['call_id','parent_call_id','caller','contract','method','depth','tx_id','instance_id','instance_uses_before','source_sha','gas_in_cumulative','gas_out_cumulative','initial_ledger_sha']},'local_increment':c['gas_out_cumulative']-c['gas_in_cumulative'],'inputs_sha':digest(c['actual_parameters']),'result_sha':digest(c['actual_result']),'state_operations_sha':digest(c['own_state_operations'])})
 gs=[e for e in d['gas']if e['call_id']==6]
 a=next(e for e in gs if e['seq']==36);b=next(e for e in gs if e['seq']==37)
 assert (a['host'],a['when'],b['host'],b['when'])==('DeleteState','after','log_message','before')
 c=d['calls'][6]
 summ.append({'block':o['block'],'condition':o['condition'],'label':label,'root_gas':d['calls'][0]['gas_out_cumulative'],'transfer_in':c['gas_in_cumulative'],'delete_after':a['gas_absolute'],'log_before':b['gas_absolute'],'window_increment':b['gas_absolute']-a['gas_absolute'],'transfer_out':c['gas_out_cumulative'],'transfer_local_increment':c['gas_out_cumulative']-c['gas_in_cumulative'],'target_instance':c['instance_id'],'target_uses_before':c['instance_uses_before'],'before_hash':d['receipt']['before_hash'],'after_hash':d['receipt']['after_hash'],'root_rwset_sha':digest(d['receipt']['actual_rwset']),'root_result_b64':d['calls'][0]['actual_result']['result'],'peak_sampled_rss_kib':o['peak_sampled_rss_kib'],'peak_sampled_threads':o['peak_sampled_threads']})
for mode in ['R0','R1','S0','J','U']:compare(f'safe-preflight-{mode}-off',f'safe-preflight-{mode}-on',True)
for block in range(1,4):
 for mode in ['R0','S0','J','U']:
  a=load(f'safe-block{block}-R1');b=load(f'safe-block{block}-{mode}');r=compare(a['label'],b['label'])
  # All five histories must have identical host call order, even when Gas differs.
  assert [shape(e)for e in a['gas']]==[shape(e)for e in b['gas']]
  for row in r['calls']:state.append({'block':block,'reference':'R1','condition':mode,**row})
  first=r['trace'].get('first')or{}
  pairs.append({'block':block,'reference':'R1','condition':mode,'root_delta_condition_minus_R1':r['root_delta_b_minus_a'],'semantic_equal':r['all_business_equal'],'gas_equal':r['all_call_gas_equal'],'trace_status':r['trace']['status'],'first_call_id':first.get('a',{}).get('call_id'),'first_seq':first.get('a',{}).get('seq'),'first_host':first.get('a',{}).get('host'),'first_when':first.get('a',{}).get('when')})
 # JSON warm target and retained normal target must match at EVERY observed Gas point.
 compare(f'safe-block{block}-R0',f'safe-block{block}-J',True)
write('RESOURCE_LIFECYCLE.csv',resources);write('ALL_RUNS.csv',allruns);write('GAS_TRACE.csv',traces);write('CALLS.csv',calls);write('WARM_RECORDS.csv',warm);write('BLOCK_SUMMARY.csv',summ);write('STATE_COMPARISON.csv',state);write('PAIRED_GAS.csv',pairs)
v={'all_processes':len(allruns),'passed_processes':sum(r['passed']for r in allruns),'failed_processes':sum(not r['passed']for r in allruns),'formal_processes':len(summ),'formal_blocks':3,'preflight_probe_parity_conditions':5,'business_equal_comparisons':len(pairs),'all_owned_processes_stopped':all(r['all_owned_processes_stopped']for r in allruns),'max_sampled_rss_kib':max(r['peak_sampled_rss_kib']for r in allruns),'max_sampled_threads':max(r['peak_sampled_threads']for r in allruns),'condition_root_gas':{m:sorted({r['root_gas']for r in summ if r['condition']==m})for m in ['R0','R1','S0','J','U']},'internal_json_cache_state':'not_tested_decoder_failed','table_function_identity':'not_tested','exception_paths':'not_tested','copy_new_tests':False}
(P/'audit/verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
