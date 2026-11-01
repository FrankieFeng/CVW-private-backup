"""Read-only raw-log reconstruction. Rewrites derived tables only; never runs a test."""
from pathlib import Path
import json,csv,re,base64,hashlib
P=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def write(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for x in rows for k in x))
 with(P/name).open('w',newline='')as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
def events(name,prefix):return [json.loads(x[len(prefix):])for x in(P/'raw_logs'/name).read_text().splitlines()if x.startswith(prefix)]
threads=[];resources=[];identities=[]
for label in ['original-single','original-multi','original-fd-wake','rebuilt-baseline-single','rebuilt-baseline-multi','patched-single','patched-multi']:
 log=(P/'raw_logs'/f'{label}.log').read_text();trace=(P/'raw_logs'/f'{label}-pthread.log').read_text();frames=P/'audit'/f'{label}-frames.json'
 ids={x['id']for x in load(frames)if x['nearest_function']=='virtual_mio::selector::Selector::new'}if frames.exists()else {17}
 starts={int(i):int(tid)for i,tid in re.findall(r'START id=(\d+) tid=(\d+)',trace)}
 exited={int(i)for i in re.findall(r'EXIT id=(\d+)',trace)}
 snaps=events(f'{label}.log','SNAP ')
 for s in snaps:
  tids={x['tid']for x in s['tasks']};alive=[starts[i]for i in ids if i in starts and starts[i]in tids]
  threads.append(dict(run=label,checkpoint=s['tag'],threads=s['threads'],selector_threads_alive=len(alive),selector_tids=';'.join(map(str,sorted(alive))),selector_EXIT_events_in_entire_log=sum(i in exited for i in ids),maxrss_mib=s['maxrss_kib']/1024,mono_ns=s['mono_ns']))
 for i in sorted(ids):
  tid=starts.get(i);ss=[t for s in snaps for t in s['tasks']if t['tid']==tid]
  identities.append(dict(run=label,creation_id=i,tid=tid,phase='wasi_env_new',function='virtual_mio::selector::Selector::new',observed_names=sorted({t['name']for t in ss}),wait_points=sorted({t['wchan']for t in ss}),exit_record=i in exited))
 resources.append(dict(run=label,kind='C',rss_peak_mib=max(s['maxrss_kib']for s in snaps)/1024,threads_observed_peak=max(s['threads']for s in snaps),threads_idle=snaps[-1]['threads'],exit_status=0 if 'code=exited/status=0'in log else 'missing',native_sha=load(P/'audit'/f'{label}-command.json')['sha']))
write('THREAD_BEFORE_AFTER.csv',threads);(P/'audit/thread-identities.json').write_text(json.dumps(identities,indent=2))
for f in sorted((P/'raw_logs').glob('*-outcome.json')):
 x=load(f);owner=x.get('owner')or{};r=dict(run=x['label'],kind='node'if 'stop_s'in x else'prototype',rss_peak_mib=x.get('peak_rss_kib',0)/1024,threads_observed_peak=x.get('peak_threads'),exit_status=(x.get('systemd')or{}).get('ExecMainStatus'),reason=x.get('reason'),pid_exited=x.get('pid_exited',x.get('all_owned_processes_stopped')),cgroup_empty=x.get('cgroup_empty'),stores_created=owner.get('stores_created'),stores_closed=owner.get('stores_closed'),instances_created=owner.get('instances_created'),instances_closed=owner.get('instances_closed'),managed_pending=owner.get('managed_pending'),stop_call_s=x.get('stop_s'))
 snaps=sorted((P/'raw_logs').glob(x['label']+'-snapshot-*.json'))
 for s in snaps:
  z=load(s)
  if z['tag']=='idle2':r.update(threads_idle=z['os_threads'],heap_idle_mib=z['go_heap']/1024**2)
 resources.append(r)
write('RESOURCE_SUMMARY.csv',resources)
state=[];details=[]
for c in ['compute','exchange']:
 a=load(P/f'raw_logs/original-{c}-receipts/target-G0.json')
 for variant in ['baseline','patched']:
  b=load(P/f'raw_logs/{variant}-{c}-receipts/target-G0.json')
  check={k:a[k]==b[k]for k in ['business_input','before_hash','after_hash','status','actual_result','actual_rwset']}
  calls=lambda x:[{k:v for k,v in y.items()if k not in ['begin_ns','end_ns','invoke_seconds_inclusive','callmethod_seconds_nested']}for y in x['inclusive_call_records_do_not_sum']]
  check['calls_and_gas']=calls(a)==calls(b)
  state.append(dict(scope='prototype',case=c,comparison='original-vs-'+variant,checks=check,gas_original=a['actual_result'].get('gas_used',0),gas_other=b['actual_result'].get('gas_used',0),subcalls=sum(x['depth']>0 for x in b['inclusive_call_records_do_not_sum'])))
# Node equivalence: preserve TxID/height originals, normalize only explicit variable transaction metadata.
def norm(x):
 if isinstance(x,dict):return {k:norm(v)for k,v in x.items()if k not in ['tx_id','TxId','BlockHeight']}
 if isinstance(x,list):return [norm(v)for v in x]
 if isinstance(x,str):
  try:
   d=base64.b64decode(x,validate=True).decode();j=json.loads(d)
   if isinstance(j,dict)and'TxId'in j:return {'decoded_tx_info':norm(j)}
  except (ValueError,UnicodeError):pass
 return x
def client(label):return {x['input']['Tag']:x['result']for x in map(json.loads,(P/'raw_logs'/f'{label}-client.jsonl').read_text().splitlines())}
a,b=client('baseline-node'),client('patched-node')
for tag in ['w0-bigNumCal','w0-buyNow','w1-bigNumCal','w1-buyNow']:
 ra,rb=a[tag]['response'],b[tag]['response'];ta,tb=a[tag+'-committed']['transaction'],b[tag+'-committed']['transaction'];ca=ta['transaction']['result']['contract_result'];cb=tb['transaction']['result']['contract_result']
 checks={'rpc_status':ra.get('code',0)==rb.get('code',0)==0,'contract_result_gas_events':norm(ca)==norm(cb),'committed_rwset_normalized':norm(ta['rw_set'])==norm(tb['rw_set'])}
 tx=rb['tx_id'];ev=events('patched-node-node.log','STEP35 ');calls=[x for x in ev if x.get('event')=='invoke_end'and x.get('tx_id')==tx];checks['six_actual_subcalls']=sum(x['depth']>0 for x in calls)==(6 if'bu' in tag else 0)
 state.append(dict(scope='node',case=tag,comparison='rebuilt-baseline-vs-patched',checks=checks,gas_original=ca.get('gas_used',0),gas_other=cb.get('gas_used',0),subcalls=sum(x['depth']>0 for x in calls)))
 details.extend(dict(case=tag,depth=x['depth'],contract=x['contract'],method=x['method'],gas=x['gas'],tx_id=tx)for x in calls)
(P/'audit/correctness-details.json').write_text(json.dumps(state,indent=2));(P/'audit/node-call-details.json').write_text(json.dumps(details,indent=2))
print(json.dumps(state,indent=2));assert all(all(x['checks'].values())for x in state),'parity mismatch, inspect raw logs'
