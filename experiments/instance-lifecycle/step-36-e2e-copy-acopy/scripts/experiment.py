from pathlib import Path
import os,subprocess,json,csv,sys,time
from parity import check
P=Path(__file__).resolve().parents[1];cases=json.loads((P/'inputs/cases.json').read_text());state=P/'state.json';groups=['G0','G1','G2','G3'];orders=[groups,['G2','G3','G0','G1'],['G1','G0','G3','G2']]
def save():
 (P/'inputs/cases.json').write_text(json.dumps(cases,indent=2));rows=list(csv.DictReader((P/'METHOD_COVERAGE.csv').open()))
 for r in rows:
  if r['case']in cases:
   c=cases[r['case']];r.update(step36_status=c['status'],step36_reason=c.get('reason',''),actual_e2e_n=c.get('actual_per_group',0),batches=c.get('actual_batches',0))
 keys=list(rows[0])
 with(P/'METHOD_COVERAGE.csv').open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def invoke(script,args,home):
 if (P/'STOP_SHARED.json').exists():raise RuntimeError('shared stop; inspect before any new run')
 state.write_text(json.dumps({'script':script,'args':args,'home':home,'active':True},indent=2));print('START',*args,flush=True)
 log=P/'raw_logs'/(args[0]+'-driver.log');assert not log.exists(),'unfinished attempt retained'
 env=dict(os.environ,STEP36_HOME=home)
 with log.open('w')as f:r=subprocess.run([sys.executable,str(P/'scripts'/script),*args],env=env,stdout=f,stderr=subprocess.STDOUT)
 print(log.read_text()[-600:],flush=True);state.write_text(json.dumps({'script':script,'args':args,'active':False,'exit':r.returncode},indent=2));return r.returncode
# Build frozen ledger seeds; no formal samples in these processes.
for c in sorted({x['contract']for x in cases.values()}):
 for flavor in ['plain','A']:
  label='seed-'+c+'-'+flavor;out=P/'raw_logs'/f'{label}-seed.json'
  if out.exists():
   if json.loads(out.read_text())['passed']:continue
   raise RuntimeError('failed seed requires audit '+label)
  rc=invoke('seed.py',[label,c,flavor],'/tmp/cvw-step36-seed-'+c+'-'+flavor)
  if rc:raise RuntimeError('seed failed '+label)
for case,c in cases.items():
 if c['status']in ['PASSED','FAILED_CORRECTNESS','FAILED_RUNTIME','BLOCKED_FIXTURE','BLOCKED_BUILD']and c.get('attempted'):continue
 c['attempted']=True;paths=[];failed=False
 for g in groups:
  label='p-'+case+'-'+g;out=P/'raw_logs'/f'{label}-case.json'
  if not out.exists():invoke('case_run.py',[label,case,g,'precheck','0'],'/tmp/cvw-step36-'+label)
  x=json.loads(out.read_text());paths.append(out)
  if not x['passed']:c.update(status=x['status'],reason=x.get('error','precheck failed'));failed=True;break
 if failed:save();continue
 parity=check(paths,'precheck-'+case)
 if not parity['passed']:c.update(status='FAILED_CORRECTNESS',reason='precheck result/Gas/RWset/state parity mismatch; see raw mismatch');save();continue
 c.update(status='READY',reason='four-group real-node precheck passed');save()
 for b,order in enumerate(orders,1):
  paths=[]
  for g in order:
   label='f-'+case+'-b'+str(b)+'-'+g;out=P/'raw_logs'/f'{label}-case.json'
   if not out.exists():invoke('case_run.py',[label,case,g,'formal',str(b)],'/tmp/cvw-step36-'+label)
   x=json.loads(out.read_text());paths.append(out)
   if not x['passed']:c.update(status=x['status'],reason=x.get('error','formal failed'));failed=True;break
  if failed:break
  # Pair by tags, not the randomized physical order.
  paths.sort(key=lambda x:json.loads(x.read_text())['group']);z=check(paths,'formal-'+case+'-b'+str(b))
  if not z['passed']:c.update(status='FAILED_CORRECTNESS',reason='formal parity mismatch b'+str(b));failed=True;break
  c.update(actual_batches=b,actual_per_group=b*c['formal_n']);save()
 if not failed:c.update(status='PASSED',reason='3batches all four groups passed; exploratory lowN');save()
 print('METHOD',case,c['status'],flush=True)
(P/'COMPLETE.json').write_text(json.dumps({'methods':len(cases),'statuses':{s:sum(c['status']==s for c in cases.values())for s in sorted({c['status']for c in cases.values()})}},indent=2));print('ALL DONE',flush=True)
