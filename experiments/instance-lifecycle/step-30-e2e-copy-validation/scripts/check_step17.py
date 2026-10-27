"""Read original Step17 logs without invoking old writers."""
from pathlib import Path
from collections import defaultdict,Counter
import csv,json,hashlib
P=Path(__file__).resolve().parents[1];S=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-17-real-node');idx=defaultdict(list)
for mode in ['baseline','optimized']:
 f=S/'network'/mode/'stdout.log'
 for line,text in enumerate(f.read_text().splitlines(),1):
  if text.startswith('STEP17 '):
   r=json.loads(text[7:])
   if r['kind']=='invoke'and r['depth']==0:idx[mode,r['tx_id'],r['contract']].append(r)
rows=[]
for r in csv.DictReader((S/'samples.csv').open()):
 if r['phase']!='warm':continue
 inv=idx[r['mode'],r['tx_id'],r['contract']];assert len(inv)==int(r['vm_attempts'])and inv
 rows.append(dict(origin_step=17,batch=r['batch'],workers=r['workers'],contract=r['contract'],mode=r['mode'],tx_id=r['tx_id'],attempts=len(inv),all_root_invoke_ns=sum(x['invoke_ns']for x in inv),last_root_invoke_ns=inv[-1]['invoke_ns'],client_ns=r['client_ns']))
with(P/'historical/STEP17_TX_JOIN.csv').open('w',newline='')as f:w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
result=dict(thermal_client_responses=len(rows),root_invocations_for_responses=sum(r['attempts']for r in rows),transactions_with_multiple_root_attempts=sum(r['attempts']>1 for r in rows),attempt_histogram=dict(Counter(r['attempts']for r in rows)),all_reexecution_workers4=all(r['workers']=='4'for r in rows if r['attempts']>1),one_worker_all_one=all(r['attempts']==1 for r in rows if r['workers']=='1'),recomputed_from_original_stdout=True)
assert result['thermal_client_responses']==5248 and result['root_invocations_for_responses']==6008 and result['transactions_with_multiple_root_attempts']==382
(P/'audit/step17-raw-check.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
