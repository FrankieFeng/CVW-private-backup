from pathlib import Path
import itertools,json,sys
from run import run,save,P
from check_pair import check
PERMS=list(itertools.permutations(['G0','G1','G2']))
CASES=['bigNumCal','hashCal','normalCal','fact','erc721','buyNow']
def parity(labels,case,exception=False):
 receipts=[]
 for label in labels:
  folder=P/'raw_logs'/f'{label}-receipts'
  for file in sorted(folder.glob('target-G*.json')):receipts.append(json.loads(file.read_text()))
 assert len(receipts)==3
 if exception:
  for a,b in zip(receipts,receipts[1:]):
   for k in ['business_input','before_hash','after_hash','status','actual_result','actual_rwset']:assert a[k]==b[k],k
   assert a['actual_result'].get('code',0)!=0 and a['before_hash']==a['after_hash']
  result={'exception_parity':True,'gas':receipts[0]['actual_result'].get('gas_used',0),'calls':len(receipts[0]['inclusive_call_records_do_not_sum'])}
 else:result=check(receipts[0],receipts[1],case=='buyNow');check(receipts[1],receipts[2],case=='buyNow')
 return result

def block(case,batch,slot,phase):
 order=','.join(PERMS[((batch-1)*10+slot-1)%6]);prefix=f'{phase}-{case}-b{batch}-s{slot:02d}'
 labels=[]
 for g in (order.split(',') if case=='buyNow' else ['']):
  label=prefix+('-'+g if g else '');run(label,case,phase=phase,order=order,batch=batch,slot=slot,single=g);labels.append(label)
 result=parity(labels,case);save(P/'raw_logs'/f'{prefix}-block.json',dict(case=case,batch=batch,slot=slot,phase=phase,order=order,labels=labels,valid=True,parity=result));print('VALID BLOCK',prefix,flush=True)
if __name__=='__main__':
 action=sys.argv[1]
 if action=='preflight':
  for case in CASES:block(case,1,1,'preflight')
  for kind in ['empty','duplicate']:
   labels=[]
   for g in ['G0','G1','G2']:
    label='exception-'+kind+'-'+g;run(label,'buyNow',phase='exception',single=g,exception=kind);labels.append(label)
   save(P/'raw_logs'/f'exception-{kind}-parity.json',parity(labels,'buyNow',True))
 elif action=='formal':
  assert all((P/'raw_logs'/f'preflight-{case}-b1-s01-block.json').exists() for case in CASES)
  assert all((P/'raw_logs'/f'exception-{kind}-parity.json').exists() for kind in ['empty','duplicate'])
  for batch in range(1,4):
   for slot in range(1,11):
    for case in CASES:block(case,batch,slot,'formal')
