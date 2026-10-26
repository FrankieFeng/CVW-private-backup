from pathlib import Path
import json,csv,statistics,hashlib
P=Path(__file__).resolve().parents[1]
def write(name,rows):
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with(P/name).open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def events(label):
 return [json.loads(s[len('STEP21C '):])for s in(P/'raw_logs'/f'{label}.log').read_text().splitlines()if s.startswith('STEP21C ')]
summaries=[];samples=[];timeline=[];allruns=[]
for f in sorted((P/'raw_logs').glob('*-outcome.json')):
 label=f.name[:-len('-outcome.json')];out=json.loads(f.read_text());es=events(label);calls=[e['call']for e in es if e['event']=='invoke_return'];done=[e for e in es if e['event']=='manager_closed'];owner=[e for e in es if e['event']=='owner_closed']
 row={'label':label,'final_version':label.startswith('final-'),'test':out['test'],'policy':out['policy'],'method':out['method'],'requested':out['n'],'process_passed':out['passed'],'exit':out['status_before_stop'].get('ExecMainStatus'),'root_calls_observed':sum(c['depth']==0 for c in calls),'all_vm_calls':len(calls),'successful_vm_calls':sum(c['code']==0 for c in calls),'peak_rss_mib':max([out['peak_sampled_rss_kib']]+[e.get('VmRSS',0)for e in es])/1024,'peak_threads':max([out['peak_sampled_threads']]+[e.get('Threads',0)for e in es]),'created':done[-1]['created']if done else None,'closed':done[-1]['closed']if done else None,'in_flight_final':done[-1]['in_flight']if done else None,'pending_native_final':owner[-1]['managed_pending']if owner else None,'owner_tid_count':len(set(e['owner_tid']for e in es if 'owner_tid'in e)),'clock_reversed_calls':sum(c['end_ns']<c['begin_ns']for c in calls)}
 allruns.append(row)
 if not label.startswith('final-')or out['test']=='OwnerFailure':continue
 assert out['passed']and row['created']==row['closed']and row['in_flight_final']==0 and row['pending_native_final']==0 and row['owner_tid_count']==1
 roots=[c for c in calls if c['depth']==0 and c['method']==out['method']]
 cre=[e for e in es if e['event']=='create_done'];cl=[e for e in es if e['event']=='close_done'];acq=[e for e in es if e['event']=='acquire']
 for e in es:
  if 'monotonic_ns'in e:timeline.append({'label':label,**e})
 for i,c in enumerate(roots):samples.append({'label':label,'policy':out['policy'],'method':out['method'],'index':i,**c,'duration_clock':'Go time.Sub monotonic'})
 count=len(roots);begins=[e['monotonic_ns']for e in es if e['event']=='create_begin'];ends=[e['monotonic_ns']for e in cre]
 summaries.append({**row,'target_successes':sum(c['code']==0 for c in roots),'target_calls':count,'invoke_mean_ms':statistics.mean(c['invoke_seconds_inclusive']for c in roots)*1000,'callmethod_mean_ms':statistics.mean(c['callmethod_seconds_nested']for c in roots)*1000,'first_invoke_ms':roots[0]['invoke_seconds_inclusive']*1000,'later_invoke_mean_ms':statistics.mean(c['invoke_seconds_inclusive']for c in roots[1:])*1000 if count>1 else '', 'create_mean_ms':statistics.mean(e['create_ns']for e in cre)/1e6,'compile_mean_ms':statistics.mean(e['compile_ns']for e in cre)/1e6,'close_mean_ms':statistics.mean(e['close_ns']for e in cl)/1e6,'acquire_mean_ms':statistics.mean(e['acquire_ns']for e in acq)/1e6,'channel_block_ns':sum(e['channel_block_ns']for e in acq),'queue_inventory':0,'observed_create_per_s_not_steady':len(cre)*1e9/(max(ends)-min(begins)),'steady_supply_rate':'not_established_synchronous_no_refill','root_gas_distribution':json.dumps({str(g):sum(c['gas_used_actual']==g for c in roots)for g in set(c['gas_used_actual']for c in roots)},sort_keys=True),'reported_tps':'not_reported_small_sample_new_mechanism'})
write('all_processes.csv',allruns);write('summary.csv',summaries);write('samples.csv',samples);write('lifecycle_events.csv',timeline)
correct=[]
for method in ['bigNumCal','normalCal','buyNow']:
 rs={s['policy']:[x for x in samples if x['label']==s['label']]for s in summaries if s['method']==method}
 if set(rs)=={'R0','R1'}:
  for a,b in zip(rs['R0'],rs['R1']):correct.append({'method':method,'index':a['index'],'R0_code':a['code'],'R1_code':b['code'],'result_equal':a['result']==b['result'],'R0_gas':a['gas_used_actual'],'R1_gas':b['gas_used_actual'],'gas_equal':a['gas_used_actual']==b['gas_used_actual']})
write('correctness.csv',correct)
verification={'final_processes':len([r for r in allruns if r['final_version']]),'final_processes_passed':all(r['process_passed']for r in allruns if r['final_version']),'final_business_targets':len(samples),'final_vm_calls':sum(r['all_vm_calls']for r in allruns if r['final_version']),'final_scope_counts_zero':all(r['pending_native_final']==0 for r in allruns if r['final_version']),'native_parallelism_executed':False,'hundred_fresh_calls_executed':False,'steady_state_claimed':False,'all_processes_stopped':all('MainPID=0' in json.loads(f.read_text())['post_stop']for f in(P/'raw_logs').glob('*-outcome.json'))}
(P/'verification.json').write_text(json.dumps(verification,indent=2))
print(json.dumps(verification,indent=2))
for r in summaries:print(r['label'], 'invoke_ms',round(r['invoke_mean_ms'],3),'call_ms',round(r['callmethod_mean_ms'],3),'create_ms',round(r['create_mean_ms'],3),'rss_mib',round(r['peak_rss_mib'],2),'gas',r['root_gas_distribution'])
