"""Reconstruct saved lifecycle evidence only. Does not start nodes or rewrite raw logs."""
from pathlib import Path
import json,csv,base64,hashlib
P=Path(__file__).resolve().parents[1];R=Path('/home/frankie/mygitprojects')
def load(p):return json.loads(p.read_text())
def ev(label,prefix='STEP35C '):return [json.loads(l[len(prefix):])for l in(P/'raw_logs'/f'{label}-node.log').read_text().splitlines()if l.startswith(prefix)]
def table(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/name).open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
resources=[];phases=[];checks=[]
for path in sorted((P/'raw_logs').glob('*-outcome.json')):
 x=load(path);label=x['label'];owner=x.get('owner')or{};events=ev(label);count=lambda v:sum(e['event']==v for e in events)
 first=lambda v:next((e['mono_ns']for e in events if e['event']==v),None)
 a,b=first('rpc_stop_begin'),first('db_close_end');isfinal=label.startswith('candidate-')or label.startswith('restart-candidate-')
 code=x['systemd'].get('ExecMainStatus');row=dict(run=label,cohort='final_matrix'if label.startswith('candidate-')else'final_restart'if label.startswith('restart-candidate-')else'exploratory_or_failure',exit_code=code,rss_peak_mib=x['peak_rss_kib']/1024,threads_peak=x['peak_threads'],stores_created=owner.get('stores_created'),stores_closed=owner.get('stores_closed'),instances_created=owner.get('instances_created'),instances_closed=owner.get('instances_closed'),managed_pending=owner.get('managed_pending'),core_jobs_begin=count('commit_job_begin'),core_jobs_end=count('commit_job_end'),put_begin=count('put_begin'),put_end=count('put_end'),db_write_begin=count('db_write_begin'),db_write_end=count('db_write_end'),wal_cleanup_begin=count('wal_cleanup_begin'),wal_cleanup_end=count('wal_cleanup_end'),rpc_requests_begin=count('rpc_request_begin'),rpc_requests_end=count('rpc_request_end'),core_drained=count('core_drain_end'),ledger_drained=count('ledger_drain_end'),diagnostic_stopped=count('diagnostic_stopped'),protocol_stop_ms=(b-a)/1e6 if a is not None and b is not None else '',driver_cleanup_ms=x['stop_s']*1000,pid_exited=x['pid_exited'],cgroup_empty=x['cgroup_empty'])
 vm=ev(label,'STEP35 ');heaps=[e['go_heap']for e in vm if 'go_heap'in e];goros=[e['goroutines']for e in vm if 'goroutines'in e]
 row['go_heap_boundary_peak_mib']=max(heaps)/1024**2 if heaps else 'not_recorded'
 row['goroutines_snapshot_max']=max(goros) if goros else 'not_recorded'
 row['archive_drained']=count('archive_workers_drained')
 resources.append(row)
 for e in events:phases.append(dict(run=label,**e))
 if isfinal:
  verify={'exit0':code=='0','owner_balanced':owner.get('stores_created')==owner.get('stores_closed')and owner.get('instances_created')==owner.get('instances_closed'),'pending0':owner.get('managed_pending')==0,'core_tasks_balanced':count('commit_job_begin')==count('commit_job_end'),'puts_balanced':count('put_begin')==count('put_end'),'writes_balanced':count('db_write_begin')==count('db_write_end'),'WAL_balanced':count('wal_cleanup_begin')==count('wal_cleanup_end'),'rpc_balanced':count('rpc_request_begin')==count('rpc_request_end'),'diagnostic_exited':count('diagnostic_stopped')==1,'resource_limits':x['peak_rss_kib']<1536*1024 and x['peak_threads']<220,'all_processes_gone':x['pid_exited']and x['cgroup_empty']}
  closes=[e['mono_ns']for e in events if e['event']=='db_close_begin'];writes=[e['mono_ns']for e in events if e['event']=='db_write_end'];verify['writes_before_DB_close']=not writes or min(closes)>max(writes)
  verify['archive_drained']=count('archive_workers_drained')==1
  checks.append(dict(run=label,checks=verify));assert all(verify.values()),(label,verify)
table('RESOURCE_SUMMARY.csv',resources);table('LIFECYCLE_EVENTS.csv',phases)
# Same Step35B real-node ledger, token input and native build; transaction metadata alone normalized.
def norm(x):
 if isinstance(x,dict):return {k:norm(v)for k,v in x.items()if k not in ['tx_id','TxId','BlockHeight']}
 if isinstance(x,list):return [norm(v)for v in x]
 if isinstance(x,str):
  try:
   d=json.loads(base64.b64decode(x,validate=True).decode())
   if isinstance(d,dict)and'TxId'in d:return {'tx_metadata':norm(d)}
  except (ValueError,UnicodeError):pass
 return x
def client(p):return {x['input']['Tag']:x['result']for x in map(json.loads,p.read_text().splitlines())}
a=client(R/'.worktrees/cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/raw_logs/patched-node-client.jsonl');b=client(P/'raw_logs/candidate-normal-client.jsonl')
parity=[]
for tag in ['w0-bigNumCal','w0-buyNow','w1-bigNumCal','w1-buyNow']:
 ca=a[tag+'-committed']['transaction'];cb=b[tag+'-committed']['transaction'];va=ca['transaction']['result']['contract_result'];vb=cb['transaction']['result']['contract_result'];tx=b[tag]['response']['tx_id'];calls=[e for e in ev('candidate-normal','STEP35 ')if e['event']=='invoke_end'and e['tx_id']==tx]
 z={'result_gas_events':norm(va)==norm(vb),'committed_rwsets':norm(ca['rw_set'])==norm(cb['rw_set']),'real_children':sum(e['depth']>0 for e in calls)==(6 if'buyNow'in tag else 0)};assert all(z.values()),(tag,z)
 parity.append(dict(case=tag,gas=vb.get('gas_used',0),checks=z,tx_id=tx,subcalls=sum(e['depth']>0 for e in calls)))
(P/'audit/parity.json').write_text(json.dumps(parity,indent=2));(P/'audit/lifecycle-checks.json').write_text(json.dumps(checks,indent=2))
loaded=[]
for f in sorted((P/'raw_logs').glob('*-loaded-maps.txt')):
 paths={line.split()[-1]for line in f.read_text().splitlines()if'libwasmer.so'in line}
 for path in paths:
  sha=hashlib.sha256(Path(path).read_bytes()).hexdigest();assert sha=='56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc';loaded.append({'run':f.stem,'path':path,'sha256':sha})
(P/'audit/loaded-native.json').write_text(json.dumps(loaded,indent=2))
print('final lifecycle cases',len(checks),'all passed; parity',len(parity),'passed; native unchanged')
