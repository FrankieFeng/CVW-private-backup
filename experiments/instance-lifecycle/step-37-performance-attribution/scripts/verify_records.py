"""Independent raw receipt validation and read-only replay of historical normalization."""
from pathlib import Path
import json,csv,base64,collections,hashlib
P=Path(__file__).resolve().parents[1];S=P.parent/'step-36-e2e-copy-acopy'
def norm(x,meta):
 ids={m['tx_id']:m['tag']for m in meta}
 if isinstance(x,dict):
  history={'Field','Value','TxId','Timestamp','BlockHeight','Key'}<=set(x)or{'field','value','txId','timestamp','blockHeight','key'}<=set(x)
  return {ids.get(k,k):('<history-time>'if history and k.lower()=='timestamp'else'<height>'if k in ['BlockHeight','blockHeight']and('TxId'in x or'txId'in x)else norm(v,meta))for k,v in x.items()if k!='tx_id'}
 if isinstance(x,list):return [norm(v,meta)for v in x]
 if isinstance(x,str):
  if x in ids:return '<'+ids[x]+'>'
  try:return {'bytes':norm(json.loads(base64.b64decode(x,validate=True).decode()),meta)}
  except (ValueError,UnicodeError):
   try:return norm(json.loads(x),meta)if x.startswith(('{','['))else x
   except ValueError:return x
 return x
def sig(x):
 meta=x['metadata'];rows=[]
 for it in x['records']:
  r=it['row'];cr=r['response'].get('contract_result')or{};rw=it['committed'].get('rw_set')or{}
  rows.append(dict(tag=it['tag'],result=norm(cr,meta),reads=sorted((norm(v,meta)for v in rw.get('tx_reads',[])),key=lambda v:json.dumps(v,sort_keys=True)),writes=sorted((norm(v,meta)for v in rw.get('tx_writes',[])),key=lambda v:json.dumps(v,sort_keys=True))))
 return dict(rows=rows,projection=sorted((norm(v,meta)for v in x['projection']),key=lambda v:json.dumps(v,sort_keys=True)),initial=norm(x['initial_projection'],meta))
r=list(csv.DictReader((P/'RECOMPUTED_TRANSACTIONS.csv').open()));group=collections.defaultdict(dict);resources=[];receipts=0;fallbacks=0
for run in sorted({x['run']for x in r}):
 x=json.loads((S/'raw_logs'/f'{run}-case.json').read_text());z=x['node'];o=z['owner'];assert z['pid_exited']and z['cgroup_empty']and z['systemd']['ExecMainStatus']=='0'and o['stores_created']==o['stores_closed']and o['instances_created']==o['instances_closed']and o['managed_pending']==0
 for it in x['records']:
  if not it['tag'].startswith('target'):continue
  a=it['row']['response'];b=it['committed'];assert a['tx_id']==b['transaction']['payload']['tx_id']and a['tx_block_height']==b['block_height']>0 and a['contract_result']==b['transaction']['result']['contract_result'];receipts+=1
 group[x['case'],x['batch']][x['group']]=sig(x)
 resources.append(dict(run=run,case=x['case'],group=x['group'],batch=x['batch'],rss_peak_mib=z['peak_rss_kib']/1024,threads_peak=z['peak_threads'],stores_created=o['stores_created'],stores_closed=o['stores_closed'],instances_created=o['instances_created'],instances_closed=o['instances_closed'],stop_seconds=z['stop_s'],pid_exited=z['pid_exited'],cgroup_empty=z['cgroup_empty']))
 fallback=0
 for l in(S/'raw_logs'/f'{run}-node.log').open():
  if l.startswith('STEP35 ')and json.loads(l[7:])['event']=='copy_fallback':fallback+=1
 fallbacks+=fallback
for k,x in group.items():assert len(x)==4 and all(x[g]==x['G0']for g in x),k
with(P/'RESOURCE_ANALYSIS.csv').open('w',newline='')as f:w=csv.DictWriter(f,list(resources[0]));w.writeheader();w.writerows(resources)
(P/'audit/record-verification.json').write_text(json.dumps(dict(formal_receipts_verified=receipts,paired_four_group_blocks_verified=len(group),copy_fallbacks=fallbacks,normalization='historical rule reproduced; history metadata normalized, not byte-for-byte global ledger equivalence',max_formal_rss_mib=max(x['rss_peak_mib']for x in resources)),indent=2));print((P/'audit/record-verification.json').read_text())
