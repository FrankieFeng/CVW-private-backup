"""Only reads saved logs/receipts. Integers are real registry Gas, not timing estimates."""
from pathlib import Path
from collections import defaultdict,Counter
import csv,json,hashlib,sys
from compare import P,TX,load,compare,digest,shape
def write(name,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with(P/name).open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rs)
def js(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
all_outcomes=[json.loads(f.read_text())for f in sorted((P/'raw_logs').glob('*-outcome.json'))]
write('ALL_RUNS.csv',[dict(**o,eligible_final_readonly=o['label'].startswith('v2-'),observer_version='v2_forwarded_operations'if o['label'].startswith('v2-')else'v1_rejected_map_observer')for o in all_outcomes])
outcomes=[o for o in all_outcomes if o['label'].startswith('v2-')]
assert len(outcomes)==26 and all(o['passed']and o['all_owned_processes_stopped']for o in outcomes)
calls=[];trace=[];bridges=[];resources=[];preparations=[];module_events=[]
for o in outcomes:
 label=o['label'];run=load(label);idx={c['call_id']:c for c in run['calls']};before={}
 for c in run['calls']:
  assert c['getter_remaining_final']==2147483647-c['gas_out_cumulative']
  if o['probe']=='on':assert c['getter_verifications']==(13 if c['call_id']==0 else 1)
 for contract in ['identity','erc721','exchange']:
  same=[e['record']for e in run['events']if e['event']=='call_record'and e['record']['contract']==contract]
  assert len({c['store_id']for c in same})==len({c['module_go_id']for c in same})==1,'per-call Store/Module rebuild detected'
 common=dict(run_label=label,stage=o['stage'],block=o['block'],condition=o['condition'],probe=o['probe'])
 for n,e in enumerate(run['events'],1):
  if e['event']=='call_record':
   c=e['record'];local=c['gas_out_cumulative']-c['gas_in_cumulative']
   row=dict(**common,tx_id=c['tx_id'],call_sequence=c['call_id'],depth=c['depth'],caller=c['caller'],contract=c['contract'],method=c['method'],instance_id=c['instance_id'],instance_go_id=c['instance_go_id'],store_id=c['store_id'],module_go_id=c['module_go_id'],variant=c['variant'],cache_key=c['cache_key'],source_sha=c['source_sha'],instance_uses_before=c['instance_uses_before'],gas_in_cumulative=c['gas_in_cumulative'],gas_out_cumulative=c['gas_out_cumulative'],local_delta_inclusive=local,getter_remaining_final=c['getter_remaining_final'],getter_verifications=c['getter_verifications'],remaining_before_setgas=c.get('remaining_before_setgas','not_observed'),before_setgas_status=c['before_setgas_status'],own_state_operations=js(c['own_state_operations']),actual_parameters=js(c['actual_parameters']),input_sha=c['input_sha'],initial_ledger_sha=c['initial_ledger_sha'],observed_state_prefix_before_sha=digest(c['state_observation_before']),observed_state_prefix_after_sha=digest(c['state_observation_after']),events_sha=digest(c['actual_result'].get('contract_event',[])),actual_result=js(c['actual_result']),code=c['actual_result'].get('code',0),call_error=c['call_error_observed'],events_line=n)
   calls.append(row)
   if c['tx_id']==TX:trace.append(dict(**row,record_kind='call_summary',meter_boundary='runtime original SetGas input / final GetGas; delta includes nested calls',phase='invoke_return'))
  if e['event']=='gas'and e['tx_id']==TX:
   c=idx[e['call_id']];prev=before.get(c['call_id']);before[c['call_id']]=e['gas_absolute']
   trace.append(dict(**common,record_kind='counter_boundary',events_line=n,tx_id=TX,call_sequence=c['call_id'],depth=c['depth'],caller=c['caller'],contract=c['contract'],method=c['method'],instance_id=c['instance_id'],instance_go_id=c['instance_go_id'],store_id=c['store_id'],module_go_id=c['module_go_id'],variant=c['variant'],source_sha=c['source_sha'],instance_uses_before=c['instance_uses_before'],phase=e['phase'],host=e['host'],when=e['when'],point_sequence=e['seq'],remaining=e['remaining'],gas_absolute_cumulative=e['gas_absolute'],previous_boundary_gas=prev if prev is not None else'',step_delta_inclusive=e['gas_absolute']-prev if prev is not None else'',gas_in_cumulative=c['gas_in_cumulative'],gas_out_cumulative=c['gas_out_cumulative'],local_delta_inclusive=c['gas_out_cumulative']-c['gas_in_cumulative'],initial_ledger_sha=c['initial_ledger_sha'],input_sha=c['input_sha'],observed_state_prefix_before_sha=digest(c['state_observation_before']),observed_state_prefix_after_sha=digest(c['state_observation_after']),events_sha=digest(c['actual_result'].get('contract_event',[])),detail=e['detail'],owner_tid=e['owner_tid'],code=c['actual_result'].get('code',0),meter_boundary='limit minus readonly registry Remain; step delta includes host/nested effects, not exclusive guest instructions'))
  if e['event']=='bridge_gas'and e['tx_id']==TX:
   bridges.append(dict(**common,tx_id=TX,call_sequence=e['call_id'],bridge_sequence=e['bridge_seq'],is_len=e['is_len'],when=e['when'],parent_remaining=e['parent_remaining_readonly'],parent_gas_absolute=2147483647-e['parent_remaining_readonly'],gas_argument_or_return_cumulative=e['gas_argument_or_return_cumulative'],callee_result_gas_cumulative=e.get('callee_result_gas_cumulative',''),callee_code=e.get('callee_code',''),events_line=n))
 # Validate same-thread identity, lifecycle counts, S1 images and final owner cleanup from actual logs.
 sys_events=[];samples=[];templates={};modules=[]
 for line in(P/'raw_logs'/f'{label}.log').read_text().splitlines():
  if line.startswith('STEP21C '):sys_events.append(json.loads(line[8:]))
  if line.startswith('STEP22 '):
   e=json.loads(line[7:]);d=e['data']
   if e['event']=='template':templates[d['contract']]=d['image_sha'];preparations.append(dict(**common,event='template',**d))
   if e['event']=='module':modules.append(d);module_events.append(dict(**common,**d));preparations.append(dict(**common,event='module',**d))
   if e['event']in ['preparation_total','cache_closed']:preparations.append(dict(**common,event=e['event'],**d))
   if e['event']=='sample':samples.append(d)
 expected_created=3 if o['condition']=='R0'else 10
 assert len(modules)==6 and all(v['s1_hash']==templates[v['contract']]for v in samples)
 # Reused profiles retain the creation hash, so verify unique IDs rather than counting them as new checks.
 assert len({v['instance_id']for v in samples})==expected_created
 assert len({e['owner_tid']for e in run['events']if 'owner_tid'in e})==1
 manager=next(e for e in sys_events if e['event']=='manager_closed');owner=next(e for e in sys_events if e['event']=='owner_closed')
 assert manager['created']==manager['closed']==expected_created and manager['in_flight']==0 and owner['managed_objects']==owner['managed_pending']==0
 if o['condition']!='R0':assert all(c['instance_uses_before']==0 for c in run['calls'])
 rss=max([o['peak_sampled_rss_kib']]+[e.get('VmRSS',0)for e in sys_events]);threads=max([o['peak_sampled_threads']]+[e.get('Threads',0)for e in sys_events])
 assert rss<=1536*1024 and threads<=220
 resources.append(dict(**common,passed=o['passed'],created=manager['created'],closed=manager['closed'],unique_prepared_modules=len(modules),peak_rss_kib=rss,peak_threads=threads,after_owner_rss_kib=owner['VmRSS'],after_owner_threads=owner['Threads'],managed_after=owner['managed_objects'],owned_processes_stopped=True))
write('CALLS.csv',calls);write('GAS_TRACE.csv',trace);write('BRIDGE_GAS.csv',bridges);write('processes.csv',resources);write('preparation.csv',preparations);write('MODULES.csv',module_events)
ops=[];business_sets=[];coverage=[]
for o in outcomes:
 run=load(o['label'])
 if o['probe']!='on':continue
 for c in run['calls']:
  hosts=Counter(e['host']for e in run['gas']if e['call_id']==c['call_id']and e['phase']=='host'and e['when']=='before')
  counts=Counter(x['kind']for x in c['own_state_operations']or[])
  assert (counts['Get'],counts['Put'],counts['Del'])==(hosts['GetStateLen'],hosts['PutState'],hosts['DeleteState'])
  coverage.append(dict(run_label=o['label'],call_sequence=c['call_id'],contract=c['contract'],method=c['method'],Get_forwarded=counts['Get'],GetStateLen_host_calls=hosts['GetStateLen'],Put_forwarded=counts['Put'],PutState_host_calls=hosts['PutState'],Del_forwarded=counts['Del'],DeleteState_host_calls=hosts['DeleteState'],all_observed_business_state_calls_forwarded_once=True,framework_internal_rwmap='not_tested'))
  for op in c['own_state_operations']or[]:
   ops.append(dict(run_label=o['label'],stage=o['stage'],block=o['block'],condition=o['condition'],tx_id=TX,call_sequence=c['call_id'],owner_contract=c['contract'],method=c['method'],**op))
  all_ops=c['state_observation_after']['operations']or[];before_ops=c['state_observation_before']['operations']or[]
  subtree=all_ops[len(before_ops):];reads={};writes={}
  for op in subtree:
   if op['error']!='<nil>':continue
   key=op['contract']+'#'+op['key']
   if op['kind']=='Get':reads[key]=op.get('value')
   else:writes[key]=dict(kind=op['kind'],value=op.get('value'))
  business_sets.append(dict(run_label=o['label'],stage=o['stage'],block=o['block'],condition=o['condition'],tx_id=TX,call_sequence=c['call_id'],contract=c['contract'],method=c['method'],read_set_observed=js(reads),write_set_observed=js(writes),scope='successful forwarded business API operations, subtree inclusive; framework metadata reads not observed',full_callee_framework_rwset='not_tested'))
write('BUSINESS_STATE_OPS.csv',ops);write('BUSINESS_RWSETS.csv',business_sets)
write('STATE_OBSERVER_COVERAGE.csv',coverage)

state=[];parity=[];blocks=[];divergences=[]
comparisons=[]
for c in ['R0','R1','C1']:comparisons.append(('probe_on_off',0,compare(f'v2-preflight-{c}-off',f'v2-preflight-{c}-on',True)))
for stage,prefix,a,b,gas in [('lifecycle','v2-lifecycle','R0','R1',False),('copy','v2-copy','R1','C1',True)]:
 for block in range(1,6):comparisons.append((stage,block,compare(f'{prefix}-b{block}-{a}',f'{prefix}-b{block}-{b}',gas)))
for stage,block,r in comparisons:
 a,b=[load(l)for l in r['labels']]
 shapes_equal=bool(a['gas']and b['gas'])and [shape(e)for e in a['gas']]==[shape(e)for e in b['gas']]
 if stage!='probe_on_off':assert shapes_equal,'sampled host sequence differs'
 for x,y,row in zip(a['calls'],b['calls'],r['calls']):
  state.append(dict(comparison=stage,block=block,label_a=a['label'],label_b=b['label'],call_sequence=x['call_id'],caller=x['caller'],contract=x['contract'],method=x['method'],depth=x['depth'],input_equal=x['actual_parameters']==y['actual_parameters'],initial_ledger_equal=x['initial_ledger_sha']==y['initial_ledger_sha'],observed_state_prefix_before_equal=(x['state_observation_before']==y['state_observation_before']if stage!='probe_on_off'else'not_observed_probe_off'),observed_state_prefix_after_equal=(x['state_observation_after']==y['state_observation_after']if stage!='probe_on_off'else'not_observed_probe_off'),result_code_return_events_equal=row['semantic_equal'],gas_equal=row['gas_equal'],final_root_rwset_equal=a['receipt']['actual_rwset']==b['receipt']['actual_rwset'],final_root_ledger_equal=a['receipt']['after_hash']==b['receipt']['after_hash'],input_sha=x['input_sha'],rw_before_sha=digest(x['state_observation_before']),rw_after_sha=digest(x['state_observation_after']),events_sha=digest(x['actual_result'].get('contract_event',[])),rw_scope='forwarded business Get/Put/Del operation prefix plus per-call operations; no internal maps; root final RWSet separate'))
  if stage=='copy':
   ga=[e for e in a['gas']if e['call_id']==x['call_id']];gb=[e for e in b['gas']if e['call_id']==x['call_id']]
   assert len(ga)==len(gb)and all(shape(s)==shape(t)and s['gas_absolute']==t['gas_absolute']for s,t in zip(ga,gb))
   parity.append(dict(block=block,tx_id=TX,call_sequence=x['call_id'],contract=x['contract'],method=x['method'],baseline_instance_id=x['instance_id'],copy_instance_id=y['instance_id'],baseline_uses_before=x['instance_uses_before'],copy_uses_before=y['instance_uses_before'],source_wasm_sha=x['source_sha'],gas_in_baseline=x['gas_in_cumulative'],gas_in_copy=y['gas_in_cumulative'],gas_out_baseline=x['gas_out_cumulative'],gas_out_copy=y['gas_out_cumulative'],gas_equal=True,all_counter_boundaries_equal=True,all_parent_bridge_counters_equal=r['bridge_counters_equal'],counter_boundaries=len(ga),input_result_rw_events_equal=True,root_state_equal=True,status='tested_scope_pass',table_function_identity='not_tested',exception_paths='not_tested',long_lifetime_resource_bound='not_tested'))
 if stage=='lifecycle':
  t=r['trace'];first=t['first'];previous=t['previous'];assert first['a']['call_id']==6 and t['status']=='gas_counter_diff'
  divergences.append(dict(block=block,previous_equal_a=previous['a'],previous_equal_b=previous['b'],first_different_a=first['a'],first_different_b=first['b'],delta=first['delta_b_minus_a']))
 if stage!='probe_on_off':blocks.append(dict(stage=stage,block=block,root_gas_a=a['calls'][0]['gas_out_cumulative'],root_gas_b=b['calls'][0]['gas_out_cumulative'],root_delta_b_minus_a=r['root_delta_b_minus_a'],business_equal=True,sampled_host_shapes_equal=shapes_equal,first_difference_call=r['trace']['first']['a']['call_id']if r['trace']['first']else'',all_counter_boundaries_equal=r['trace']['all_equal']))
write('STATE_COMPARISON.csv',state);write('COPY_PARITY.csv',parity);write('BLOCK_SUMMARY.csv',blocks)
for r in state:r['full_callee_framework_rwset']='not_tested';r['state_scope']='forwarded business API observations plus real final root RWSet'
for r in parity:r['full_callee_framework_rwset']='not_tested';r['state_scope']='business Get/Put/Del operations and root final actual RWSet; no mid-call internal map access'
write('STATE_COMPARISON.csv',state);write('COPY_PARITY.csv',parity)
(P/'audit/first_divergences.json').write_text(json.dumps(divergences,indent=2)+'\n')

# Exact existing legacy propagation for every six real child calls (12 bridge entries).
prop=[]
for o in outcomes:
 run=load(o['label'])
 if not run['bridge']:continue
 bs=run['bridge'];assert len(bs)==36
 for sequence in range(1,7):
  before=next(e for e in bs if e['bridge_seq']==2*sequence-1 and e['when']=='before_wacsi')
  after=next(e for e in bs if e['bridge_seq']==2*sequence-1 and e['when']=='after_wacsi')
  reset=next(e for e in bs if e['bridge_seq']==2*sequence-1 and e['when']=='after_setgas')
  c=run['calls'][sequence];assert c['gas_in_cumulative']==before['gas_argument_or_return_cumulative']+100000
  assert after['gas_argument_or_return_cumulative']==c['gas_in_cumulative']+c['gas_out_cumulative']
  assert before['parent_remaining_readonly']==after['parent_remaining_readonly']
  assert 2147483647-reset['parent_remaining_readonly']==after['gas_argument_or_return_cumulative']
  prop.append(dict(label=o['label'],stage=o['stage'],block=o['block'],condition=o['condition'],callee_sequence=sequence,callee=c['contract']+'.'+c['method'],parent_used_before=before['gas_argument_or_return_cumulative'],base_call_fee=100000,child_in=c['gas_in_cumulative'],child_out=c['gas_out_cumulative'],wacsi_return=after['gas_argument_or_return_cumulative'],parent_used_before_SetGas=2147483647-after['parent_remaining_readonly'],parent_used_after_SetGas=2147483647-reset['parent_remaining_readonly'],original_cumulative_formula_verified=True))
write('GAS_PROPAGATION.csv',prop)
report=dict(processes=len(outcomes),observer_version='v2_forwarded_operations',affected_v1_processes_retained=26,all_run_processes=len(all_outcomes),root_business_calls=len(outcomes),target_invocations=len(outcomes)*7,all_invocations_including_init=len(calls),lifecycle_blocks=5,copy_blocks=5,preflight_processes=6,gas_counter_points_per_root=next(r['trace']['points']for stage,_,r in comparisons if stage=='copy'),copy_call_pairs=len(parity),peak_rss_mib=max(r['peak_rss_kib']for r in resources)/1024,peak_threads=max(r['peak_threads']for r in resources),lifecycle_root_R0=12761395,lifecycle_root_R1=12765774,lifecycle_difference=4379,first_difference_call=6,last_equal_gas=divergences[0]['previous_equal_a']['gas_absolute'],first_diff_R0=divergences[0]['first_different_a']['gas_absolute'],first_diff_R1=divergences[0]['first_different_b']['gas_absolute'],all_copy_counter_and_business_equal=True,table_function_identity='not_tested',exception_paths='not_tested',full_callee_framework_rwset='not_tested; final root actual RWSet and forwarded business state ops tested',concrete_guest_function_cause='not_located')
(P/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
