from pathlib import Path
import itertools,json,sys,statistics,hashlib
from run import run,save,P
from check_pair import check
CASES=['bigNumCal','hashCal','normalCal','fact','erc721','buyNow'];PERMS=list(itertools.permutations(['G0','G1','G2','G3']))
def mirror_progress():
 dst=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-32-all-contracts-acopy/PROGRESS.md');dst.write_text((P/'PROGRESS.md').read_text())
def parity(labels,case,exception=False):
 rs=[]
 for label in labels:
  for f in sorted((P/'raw_logs'/f'{label}-receipts').glob('target-G[0-3].json')):rs.append(json.loads(f.read_text()))
 assert len(rs)==4,'four groups required'
 for a,b in zip(rs,rs[1:]):
  if exception:
   for k in ['business_input','before_hash','after_hash','status','actual_result','actual_rwset']:assert a[k]==b[k],k
   fields=['id','depth','contract','method','tx_id','gas_used_actual','code','result','message']
   ac=sorted(a['inclusive_call_records_do_not_sum'],key=lambda r:r['id']);bc=sorted(b['inclusive_call_records_do_not_sum'],key=lambda r:r['id']);assert [{k:r.get(k)for k in fields}for r in ac]==[{k:r.get(k)for k in fields}for r in bc]
   assert a['actual_result'].get('code',0)!=0 and a['before_hash']==a['after_hash']
  else:check(a,b,case=='buyNow')
 return dict(gas=rs[0]['actual_result'].get('gas_used',0),calls=len(rs[0]['inclusive_call_records_do_not_sum']),gas_result_rwset_events=True,initial_final_ledger=True,exception=exception)
def block(case,batch,slot,phase):
 prefix=f'{phase}-{case}-b{batch}-s{slot:02d}';meta=P/'raw_logs'/f'{prefix}-block.json'
 if meta.exists():return json.loads(meta.read_text())
 # Williams balanced four-group schedule; within each10-block batch every position has2 or3 of each group.
 import random
 groupnames=['G0','G1','G2','G3'];random.Random(320027+batch*100+CASES.index(case)).shuffle(groupnames)
 patterns=[(0,1,3,2),(1,2,0,3),(2,3,1,0),(3,0,2,1)]
 schedule=patterns*2+[patterns[(batch-1)%4],patterns[batch%4]]
 random.Random(320127+batch*100+CASES.index(case)).shuffle(schedule)
 perm=tuple(groupnames[j]for j in schedule[slot-1]);order=','.join(perm)
 chunks=[','.join(perm[i:i+(1 if case=='buyNow'else 2)]) for i in range(0,4,1 if case=='buyNow'else 2)]
 labels=[]
 try:
  for i,chunk in enumerate(chunks):
   label=prefix+'-c'+str(i);run(label,case,phase=phase,order=order,batch=batch,slot=slot,single=chunk);labels.append(label)
  result=parity(labels,case);x=dict(case=case,batch=batch,slot=slot,phase=phase,order=order,labels=labels,valid=True,parity=result);save(meta,x);print('VALID BLOCK',prefix,flush=True);mirror_progress();return x
 except Exception as e:
  save(P/'STOP.json',dict(case=case,block=prefix,labels=labels,reason=str(e)));mirror_progress();raise
if __name__=='__main__':
 action=sys.argv[1]
 if action=='preflight':
  for case in CASES:block(case,1,1,'preflight')
  for kind in ['empty','duplicate']:
   out=P/'raw_logs'/f'exception-{kind}-parity.json'
   if out.exists():continue
   labs=[]
   for g in ['G0','G1','G2','G3']:
    label='exception-'+kind+'-'+g;run(label,'buyNow',phase='exception',single=g,exception=kind);labs.append(label)
   save(out,parity(labs,'buyNow',True));mirror_progress()
 elif action=='formal':
  assert all((P/'raw_logs'/f'preflight-{c}-b1-s01-block.json').exists()for c in CASES)
  assert all((P/'raw_logs'/f'exception-{k}-parity.json').exists()for k in ['empty','duplicate'])
  for b in range(1,4):
   for slot in range(1,11):
    for case in CASES:block(case,b,slot,'formal')
   print('BATCH COMPLETED',b,flush=True);mirror_progress()
 else:raise ValueError(action)
