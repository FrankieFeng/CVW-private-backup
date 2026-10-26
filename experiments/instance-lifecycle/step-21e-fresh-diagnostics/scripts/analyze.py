from pathlib import Path
import json,csv,re,statistics,hashlib
P=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def save(name,x):(P/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def csvout(name,rows):
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with(P/name).open('w',newline='')as f:
  w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
def events(label,prefix='STEP21E '):
 return [json.loads(s.split(prefix,1)[1])for s in(P/'raw_logs'/f'{label}.log').read_text().splitlines()if s.startswith(prefix)]
process=[];gas=[];profiles=[];normal=[];calls=[];boundaries=[]
for path in sorted((P/'raw_logs').glob('*-outcome.json')):
 label=path.name[:-13];o=read(path);ee=events(label);de=events(label,'STEP21C ')
 owner=[e for e in de if e['event']=='owner_closed'];manager=[e for e in de if e['event']=='manager_closed']
 process.append({'label':label,'passed':o['passed'],'test':o['test'],'n':o['n'],'policy':o['policy'],'rss_mib':o['peak_sampled_rss_kib']/1024,'threads':o['peak_sampled_threads'],'exit':o['status_before_stop'].get('ExecMainStatus'),'stopped':'MainPID=0'in o['post_stop'],'managed_pending':owner[-1]['managed_pending']if owner else None,'owner_tids':len(set(e['owner_tid']for e in de if 'owner_tid'in e)),'created':manager[-1]['created']if manager else None,'closed':manager[-1]['closed']if manager else None,'in_flight':manager[-1]['in_flight']if manager else None})
 for e in ee:
  if e['event']=='gas':gas.append({'label':label,**e})
  if e['event']=='export_profile':profiles.append({'label':label,**e})
 for rp in sorted((P/'raw_logs'/f'{label}-receipts').glob('*.json')):
  r=read(rp)
  for c in r['inclusive_call_records_do_not_sum']:calls.append({'label':label,'receipt':rp.name,**c})
 if o['test']=='Normal':
  rp=sorted((P/'raw_logs'/f'{label}-receipts').glob('measure*.json'));ps=[e for e in ee if e['event']=='export_profile'and e['method']=='normalCal'][1:]
  for r,p in zip(map(read,rp),ps):
   c=r['inclusive_call_records_do_not_sum'][0]
   normal.append({'label':label,'receipt':r['label'],'policy':p['policy'],'instance_id':p['instance_id'],'gas':r['actual_result']['gas_used'],'invoke_ms':c['invoke_seconds_inclusive']*1000,'callmethod_ms':c['callmethod_seconds_nested']*1000,'export_ms':p['export_ns']/1e6,'owner_thread_cpu_ms':p['owner_thread_cpu_ns']/1e6,'host_gc_count':p['host_gc_count'],'host_gc_pause_ns':p['host_gc_pause_ns'],'guest_gc':'not_observed'})
checks=[]
def semantic(r):
 result=dict(r['actual_result']);result.pop('gas_used',None)
 return {k:r[k]for k in ['before_hash','after_hash','business_input','actual_rwset']}|{'result_no_gas':result,'status':r['status']}
for name in ['fact','erc721']:
 rs={mode:[read(p)for p in sorted((P/'raw_logs'/f'{name}-{mode.lower()}-receipts').glob('equal*.json'))]for mode in ['R0','R1']}
 base=semantic(rs['R0'][0]);equal=all(semantic(r)==base for rows in rs.values()for r in rows);assert equal
 checks.append({'case':name,'same_business_input_initial_final_rwset_result_events':equal,'R0_gas':[r['actual_result']['gas_used']for r in rs['R0']],'R1_gas':[r['actual_result']['gas_used']for r in rs['R1']]})
 groups=[]
 for e in events(name+'-r0'):
  if e['event']=='gas'and e['tx_id']=='step21e-equal-000':
   if e['phase']=='set_gas':groups.append([])
   groups[-1].append(e)
 assert len(groups)==3
 for i,(a,b)in enumerate(zip(groups[0],groups[1])):
  assert(a['phase'],a['host'],a['when'])==(b['phase'],b['host'],b['when'])
  if a['gas_absolute']!=b['gas_absolute']:
   boundaries.append({'case':name,'previous_cold':groups[0][i-1],'previous_warm':groups[1][i-1],'first_different_cold':a,'first_different_warm':b,'delta':a['gas_absolute']-b['gas_absolute']});break
br={mode:read(next((P/'raw_logs'/f'buyNow-{mode.lower()}-receipts').glob('success-1.json')))for mode in ['R0','R1']}
assert semantic(br['R0'])==semantic(br['R1'])
root={mode:r['actual_result']['gas_used']for mode,r in br.items()};children=[]
for a,b in zip(sorted((c for c in br['R0']['inclusive_call_records_do_not_sum']if c['depth']==1),key=lambda c:c['id']),sorted((c for c in br['R1']['inclusive_call_records_do_not_sum']if c['depth']==1),key=lambda c:c['id'])):
 assert(a['contract'],a['method'],a['result'])==(b['contract'],b['method'],b['result'])
 children.append({'contract':a['contract'],'method':a['method'],'R0_instance':a['instance_id'],'R1_instance':b['instance_id'],'R0_gas_in':a['gas_in'],'R1_gas_in':b['gas_in'],'R0_gas_out_inclusive':a['gas_used_actual'],'R1_gas_out_inclusive':b['gas_used_actual'],'delta_out':b['gas_used_actual']-a['gas_used_actual'],'R0_local_delta':a['gas_used_actual']-a['gas_in'],'R1_local_delta':b['gas_used_actual']-b['gas_in']})
assert len(children)==6
checks.append({'case':'buyNow','same_business_input_initial_final_rwset_result_events':True,'root_gas':root,'six_real_children':children})
a=read(P/'raw_logs/fact-probe-1-receipts/equal-000.json');b=read(P/'raw_logs/fact-probe-off-receipts/equal-000.json');assert semantic(a)==semantic(b)and a['actual_result']['gas_used']==b['actual_result']['gas_used'];checks.append({'case':'trace_on_off_fact','same_semantics_and_gas':True,'gas':a['actual_result']['gas_used']})
# TransferFrom bracket: align own running meter relative to equal starting Gas.
gs={}
for mode in ['R0','R1']:
 gs[mode]=[e for e in events('buyNow-'+mode.lower())if e['event']=='gas'and e['method']=='transferFrom'];
for i,(a,b)in enumerate(zip(gs['R0'],gs['R1'])):
 if a['gas_absolute']!=b['gas_absolute']:
  boundaries.append({'case':'buyNow.transferFrom','previous_R0':gs['R0'][i-1],'previous_R1':gs['R1'][i-1],'first_different_R0':a,'first_different_R1':b,'delta':b['gas_absolute']-a['gas_absolute']});break
# Reparse historical B5 windows, join stable sample IDs instead of relying on report means.
H=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-21-instance-reuse-loss/capacity-fix-20261024-01')
history=[]
rows=[r for r in csv.DictReader((P/'audit/history-source/normal-primary-samples.csv').open())if r['case']=='compute-normalCal'and r['batch']in ['b','c','d']and r['primary_included']=='True']
for filename in sorted(set(r['source_file']for r in rows)):
 ids={r['index']:r for r in rows if r['source_file']==filename};profiles_by_id={}
 for line in (P/'audit/history-source'/Path(filename).name).read_text().splitlines():
  if 'b5_profile 'in line:
   d=dict(re.findall(r'(\w+)=([^\s]*)',line.split('b5_profile ',1)[1]));profiles_by_id[d['sample_id']]=d
 # The experiment emits b5 profiles and samples in the same transaction order; extract primary numeric index from full ordered profile list, index0 is first formal target (no warmup profile in these files).
 for idx,r in ids.items():
  source=(P/'audit/history-source'/Path(filename).name).read_text().splitlines();sample_line=int(r['source_line'])-1
  nearby=[line for line in source[:sample_line+1]if 'b5_profile 'in line]
  assert nearby
  d=dict(re.findall(r'(\w+)=([^\s]*)',nearby[-1].split('b5_profile ',1)[1]));
  assert d['method']=='normalCal' and int(d['total_ns'])==int(float(r['callmethod_ns'])) and d['instance_id']==r['instance_id']
  history.append({'batch':r['batch'],'policy':r['policy'],'index':idx,'instance_id':r['instance_id'],'sample_id':d['sample_id'],'invoke_ms':int(r['invoke_ns'])/1e6,'callmethod_ms':float(r['callmethod_ns'])/1e6,'export_ms':int(d['export_call_ns'])/1e6,'allocate_ms':int(d['allocate_ns'])/1e6,'syscall_ms':int(d['syscall_ns'])/1e6,'source_file':filename,'sample_line':r['source_line']})
assert len(history)==600
summary=[]
for label in ['normal-ab','normal-ba','history-bcd']:
 for mode in ['R0','R1']:
  rr=[r for r in(history if label=='history-bcd'else normal)if r['policy']==mode and(label=='history-bcd'or r['label']==label)]
  summary.append({'label':label,'policy':mode,'n':len(rr),**{k:statistics.mean(r[k]for r in rr)for k in ['invoke_ms','callmethod_ms','export_ms']},'owner_thread_cpu_ms':statistics.mean(r['owner_thread_cpu_ms']for r in rr)if label!='history-bcd'else None,'host_gc_count':sum(r['host_gc_count']for r in rr)if label!='history-bcd'else None})
csvout('processes.csv',process);csvout('gas_timeline.csv',gas);csvout('call_records.csv',calls);csvout('export_profiles.csv',profiles);csvout('normal_samples.csv',normal);csvout('normal_summary.csv',summary);csvout('audit/history-normal-samples.csv',history);save('audit/gas-equivalence.json',checks);save('audit/first-gas-divergence.json',boundaries)
verification={'processes':len(process),'all_passed':all(r['passed']for r in process),'all_stopped':all(r['stopped']for r in process),'all_native_registry_empty':all(r['managed_pending']==0 for r in process),'one_owner_per_process':all(r['owner_tids']==1 for r in process),'gas_semantics_checked':checks,'parallel_guest_execution':False,'hundred_fresh_executed':False,'history_rows':len(history)}
save('verification.json',verification)
print(json.dumps(checks,indent=2));print(json.dumps(summary,indent=2))
