from pathlib import Path
import argparse,json
from run import run
from check_pair import local
P=Path(__file__).resolve().parents[1]
TASKS=[('original','R0','R1'),('step18','R0','R1'),('original','R1','C1'),('step18','R1','C1'),('step18','R1','C2'),('step18','C1','C2')]
def check(label,fam,a,b,n=2,phase='preflight',**kw):
 o=run(label,'normal',left=a,right=b,pairs=n,phase=phase,family=fam,**kw);assert o['passed']
 try:
  results=local(label,n);es=[json.loads(l[7:])for l in(P/'raw_logs'/f'{label}.log').read_text().splitlines()if l.startswith('STEP22 ')];ss=[e['data']for e in es if e['event']=='sample'and e['data']['method']=='normalCal'and e['data']['pair_slot']>=0]
  assert len(ss)==2*n
  for s in ss:
   assert s['code']==0 and s['call_error_observed']=='<nil>'
   if s['group']=='R0':assert s['reused']and s['newinstance_ns']==s['start_ns']==s['close_ns']==0 and s['managed_call_begin']==s['managed_call_end']
   else:assert not s['reused']and s['uses_before']==0 and s['managed_before']==s['managed_after']
   if phase=='preflight'and not s['reused']:assert s.get('s1_hash')
  if(a,b)==('R0','R1'):
   assert len({s['store_id']for s in ss})==len({s['module_id']for s in ss})==1
   ids={s['instance_id']for s in ss if s['group']=='R0'};assert len(ids)==1
   fresh={s['instance_id']for s in ss if s['group']=='R1'};assert len(fresh)==n and ids.isdisjoint(fresh)
  else:assert len({s['store_id']for s in ss})==2
 except Exception as e:(P/'STOP.json').write_text(json.dumps({'label':label,'reason':'offline lifecycle/semantics '+str(e)}));raise
 (P/'raw_logs'/f'{label}-checks.json').write_text(json.dumps({'strict_semantic_pairs':len(results),'shared_exact_store_module':(a,b)==('R0','R1'),'passed':True})+'\n')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['preflight','formal','diagnostic']);args=ap.parse_args()
 if args.stage=='preflight':
  for fam,a,b in TASKS:check(f'pre-{fam}-{a}-{b}',fam,a,b)
 elif args.stage=='formal':
  for fam,a,b in TASKS:assert(P/'raw_logs'/f'pre-{fam}-{a}-{b}-checks.json').exists(),'preflight gate missing'
  for batch in range(1,4):
   tasks=TASKS if batch%2 else list(reversed(TASKS))
   for edge,(fam,a,b)in enumerate(tasks):
    for slot in range(5):
     first=(batch+slot+edge)%2;check(f'{fam}-b{batch}-{a}-{b}-p{slot}',fam,a,b,phase='formal',batch=batch,slot=slot,first=first,module_first='A1'if first else'A0')
   with(P/'PROGRESS.md').open('a')as f:f.write(f'\n正式批{batch}六个family/edge全部完成，各10对，原日志/receipt/check即时落盘。\n')
 else:
  for batch in range(1,4):
   for fam,a,b,warm in [('original','R0','R1',True),('step18','C1','C2',False)]:check(f'diag-{fam}-b{batch}-{a}-{b}',fam,a,b,n=1,phase='diagnostic',batch=batch,slot=0,first=batch%2,module_first='A1'if batch%2 else'A0',diag=True,warm=warm)
