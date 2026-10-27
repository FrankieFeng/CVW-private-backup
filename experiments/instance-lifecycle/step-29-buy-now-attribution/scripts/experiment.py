import itertools,json,sys
from run import P,run,save
from check_pair import check
PERMS=list(itertools.permutations(['G0','G1','G2']))
def block(batch,slot,phase,trace,exception=''):
 order=','.join(PERMS[((batch-1)*10+slot-1)%6]);prefix=f'{phase}-b{batch}-s{slot:02d}-'+('trace'if trace else'plain')+('-'+exception if exception else'')
 labels=[];receipts=[]
 for g in order.split(','):
  label=prefix+'-'+g;run(label,'buyNow',phase=phase,order=order,batch=batch,slot=slot,single=g,exception=exception,trace=trace);labels.append(label);receipts.append(json.loads((P/'raw_logs'/f'{label}-receipts'/f'target-{g}.json').read_text()))
 if not exception:
  check(receipts[0],receipts[1],True);check(receipts[1],receipts[2],True)
 else:
  for a,b in zip(receipts,receipts[1:]):
   for k in ['before_hash','after_hash','actual_result','actual_rwset','status']:assert a[k]==b[k],k
   assert a['actual_result'].get('code',0)!=0 and a['before_hash']==a['after_hash']
   keys=['id','depth','contract','method','tx_id','gas_used_actual','code','result','message']
   assert [{k:r.get(k)for k in keys}for r in sorted(a['inclusive_call_records_do_not_sum'],key=lambda r:r['id'])]==[{k:r.get(k)for k in keys}for r in sorted(b['inclusive_call_records_do_not_sum'],key=lambda r:r['id'])]
 save(P/'raw_logs'/f'{prefix}-block.json',dict(batch=batch,slot=slot,phase=phase,trace=trace,order=order,exception=exception,labels=labels,valid=True));print('VALID',prefix,flush=True)
 return receipts
if __name__=='__main__':
 if sys.argv[1]=='preflight':
  a=block(1,1,'preflight',False);b=block(1,1,'preflight',True)
  for x,y in zip(a,b):check(x,y,True)
  for kind in ['empty','duplicate']:block(1,1,'exception',True,kind)
 else:
  assert(P/'audit/preflight-span-check.json').exists()
  for b in range(1,4):
   for s in range(1,11):
    receipts={}
    for trace in ([False,True]if ((b-1)*10+s)%2 else[True,False]):receipts[trace]=block(b,s,'formal',trace)
    for x,y in zip(receipts[False],receipts[True]):check(x,y,True)
