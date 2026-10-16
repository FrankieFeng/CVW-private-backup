from pathlib import Path
import sys,json,collections,csv,statistics
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'step-15-copy-attribution'));from common import stats,csvwrite
obs=[];pools=[]
for mode in ['baseline','optimized']:
 for l in (O/'network'/mode/'stdout.log').read_text(errors='replace').splitlines():
  if l.startswith('STEP17 '):
   r=json.loads(l[7:]);r['mode']=mode
   (obs if r['kind']=='invoke' else pools).append(r)
index=collections.defaultdict(list)
for r in obs:index[(r['mode'],r['tx_id'],r['contract'])].append(r)
samples=[];checks=[];cross=[]
for f in sorted(O.glob('bench-*-w*.jsonl')):
 for l in f.read_text().splitlines():
  r=json.loads(l);tag=r['tag'];resp=r.get('response') or {};cr=resp.get('contract_result') or {};node=index.get((r['mode'],resp.get('tx_id'),r['contract']),[])
  if not node:continue
  # A transaction may be rescheduled. Keep all VM invocations separately, choose last for joined segment view.
  q=node[-1];row=dict(batch=tag.split(':')[0],workers=int(f.stem.split('-w')[1]),phase='cold' if ':cold:' in tag else 'warmup' if ':warmup:' in tag else 'warm',contract=r['contract'],mode=r['mode'],pair=tag,tx_id=resp.get('tx_id'),client_ns=r['elapsed_ns'],vm_attempts=len(node),code=cr.get('code',0),gas=cr.get('gas_used',0),result=cr.get('result',''),rpc_code=resp.get('code',0),error=r.get('error',''),**{k:q[k] for k in ['s1_ns','s2_ns','s3_ns','copy_ns','invoke_ns','instance_id']})
  samples.append(row)
  if r['contract']=='exchange':
   children=[z for z in obs if z['tx_id']==row['tx_id'] and z['mode']==r['mode'] and z['contract']!='exchange']
   cross.append(dict(pair=tag,mode=r['mode'],phase=row['phase'],children=len(children),all_child_code_zero=all(z['code']==0 for z in children),methods=';'.join(z['contract']+'.'+z['method'] for z in children)))
csvwrite(O/'samples.csv',samples);csvwrite(O/'vm_invocations.csv',obs);csvwrite(O/'cache_events.csv',pools);csvwrite(O/'cross_contract.csv',cross)
groups=collections.defaultdict(list);paired=collections.defaultdict(dict)
metrics=['client_ns','s1_ns','s2_ns','s3_ns','copy_ns','invoke_ns']
for r in samples:
 if r['phase']=='warm':
  groups[(r['batch'],r['workers'],r['contract'],r['mode'])].append(r);paired[r['pair']][r['mode']]=r
summary=[]
for (batch,w,c,m),rows in groups.items():
 for metric in metrics:summary.append(dict(batch=batch,workers=w,contract=c,mode=m,metric=metric,**stats([r[metric] for r in rows],seed=17017)))
effects=collections.defaultdict(list);pairrows=[]
for tag,g in paired.items():
 if set(g)!=set(['baseline','optimized']):continue
 b,o=g['baseline'],g['optimized'];eq=b['code']==o['code']==0 and b['gas']==o['gas'] and b['result']==o['result'] and b['rpc_code']==o['rpc_code']==0 and not b['error'] and not o['error'];checks.append(dict(pair=tag,contract=b['contract'],business_and_gas='pass' if eq else 'fail',baseline_gas=b['gas'],optimized_gas=o['gas'],result_equal=b['result']==o['result']))
 for metric in metrics:
  d=o[metric]-b[metric];effects[(b['batch'],b['workers'],b['contract'],metric)].append(d);pairrows.append(dict(pair=tag,contract=b['contract'],metric=metric,optimized_minus_baseline_ns=d))
paired_summary=[dict(batch=b,workers=w,contract=c,metric=m,**stats(v,seed=17018)) for (b,w,c,m),v in effects.items()]
csvwrite(O/'summary.csv',summary);csvwrite(O/'paired_effects.csv',paired_summary);csvwrite(O/'paired_samples.csv',pairrows);csvwrite(O/'correctness_pairs.csv',checks)
ids=collections.Counter((r['mode'],r['instance_id']) for r in obs);print('fresh IDs',len(ids),'repeated',sum(n>1 for n in ids.values()));print('joined samples',len(samples),'pairs',len(checks),'fails',sum(r['business_and_gas']!='pass' for r in checks))
for r in paired_summary:
 if r['metric']=='client_ns':print(r['batch'],r['workers'],r['contract'],*[round(r[k]/1e6,4) for k in ['median_ns','ci95_low_ns','ci95_high_ns']])
