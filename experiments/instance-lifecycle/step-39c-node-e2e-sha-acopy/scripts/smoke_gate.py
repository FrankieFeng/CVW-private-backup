from pathlib import Path
import json,hashlib,csv,sys
P=Path(__file__).resolve().parents[1];D=P/'raw_logs';assert not(P/'STOP_SHARED.json').exists()
def load(n):return json.loads((D/n).read_text())
checks=[]
def check(name,cond,detail=''):
 checks.append({'check':name,'passed':bool(cond),'detail':detail});assert cond,name
for case in ['compute_hashCal','bigInput_inputSize','exchange_buyNow']:
 for g in ['E0','E1','E2','E3']:
  x=load(f'pre-{case}-{g}-case.json');check(case+' '+g+' real SDK smoke',x['passed'])
  a=x['artifact_after'];check(case+' '+g+' registry identity limits',a['max_entries']==8 and a['max_bytes']==64*1024**2 and a['bytes']<=64*1024**2 and a['entries']<=8)
  if g=='E3':check(case+' cold register and hot hit',x['artifact_initial']['entries']==0 and x['artifact_after_cold']['registrations']>0 and a['hits']>x['artifact_after_cold']['hits'])
  else:check(case+' '+g+' SHA Artifact off',a['entries']==0 and a['registrations']==0)
 check(case+' four-group business parity',load('pre-'+case+'-parity.json')['passed'])
 check(case+' restart rollback',load('smoke-rollback-'+case+'-postcheck.json')['passed'])
cap=load('cap-full-capacity.json');check('real8 capacity and ninth rejection, Reset recovery',cap['passed']and cap['full_rejected']['entries']==8 and cap['reset_state']['entries']==0 and cap['recovered']['entries']==1)
u2=load('smoke-upgrade-r2-upgrade.json');up=[r for r in u2['rows']if r['input']['Op']=='upgrade'];check('real version upgrade committed with3 endorsements',up[0]['success'])
a=u2['upgraded'];b=u2['rejected'];a['items']=sorted(a['items'],key=lambda x:(x['name'],x['version'],x['sha']));b['items']=sorted(b['items'],key=lambda x:(x['name'],x['version'],x['sha']));check('same-version different WASM denied with unchanged cache',not up[1]['success']and a==b)
check('upgrade continuation, Manager Reset',load('smoke-upgrade-r3-upgrade.json')['passed']);check('node restart reloads upgraded bytes',load('smoke-upgrade-restart-upgrade.json')['passed']);budget=load('smoke-budget-reset-upgrade.json');check('Reset preserves32-root Owner budget',budget['passed']and budget['owner_before_reset']['accepted']==budget['owner_after_reset']['accepted']and budget['owner_after_reset']['limit']==32)
check('inflight Reset plus SIGTERM drains',load('smoke-inflight-inflight.json')['passed']);check('accepted tx persisted after restart',load('smoke-inflight-restart-restart.json')['passed'])
for f in sorted(D.glob('*-outcome.json')):
 x=json.loads(f.read_text());o=x.get('owner')or{};check(f.stem+' native lifecycle',not x['reason']and x['systemd']['ExecMainStatus']=='0'and x['pid_exited']and x['cgroup_empty']and o.get('managed_pending')==0 and o.get('stores_created')==o.get('stores_closed')and o.get('instances_created')==o.get('instances_closed'))
 log=(D/(x['label']+'-node.log')).read_text();ev=[json.loads(l[7:])for l in log.splitlines()if l.startswith('STEP35 ')];last=[e for e in ev if e['event']=='cache_closed'];check(f.stem+' artifact Stop cleared',bool(last)and last[-1]['artifact']['Entries']==0 and last[-1]['artifact']['Bytes']==0 and last[-1]['artifact']['Closed'])
check('all formal slots still unexecuted at admission',not list(D.glob('formal-*-case.json')))
(P/'SMOKE_COMPLETE.json').write_text(json.dumps({'passed':True,'checks':checks,'formal_executed_before_gate':0,'recovered_orchestration_failures':['cap-seed0','cap-seed1','smoke-upgrade','smoke-upgrade-r1','smoke-upgrade-r2'],'note':'all raw false status retained; authenticated upgrade proof inr2 followed by successful continuation/restart; no runtime guard bypass'},indent=2))
with(P/'PROGRESS.md').open('a')as f:f.write('\nSMOKE_GATE PASSED: '+str(len(checks))+'checks, SDK business/commit, real upgrade, invalid same-version upgrade, Reset/budget, Stop/inflight/restart, capacity8 rejection and resource balance. Formal transactions before gate=0. Next: study.py formal (3batches×3methods×4groups×10=360).\n')
print('SMOKE PASSED',len(checks),'checks; approved bounded formal phase')
