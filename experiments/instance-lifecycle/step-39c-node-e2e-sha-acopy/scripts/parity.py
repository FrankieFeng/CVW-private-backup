from pathlib import Path
import json,base64,hashlib
P=Path(__file__).resolve().parents[1]
def norm(x,meta):
 ids={m['tx_id']:m['tag']for m in meta}
 if isinstance(x,dict):
  history={'Field','Value','TxId','Timestamp','BlockHeight','Key'}<=set(x)or{'field','value','txId','timestamp','blockHeight','key'}<=set(x)
  return {ids.get(k,k):('<history-time>'if history and k.lower()=='timestamp'else'<height>'if k in ['BlockHeight','blockHeight']and('TxId'in x or'txId'in x)else norm(v,meta))for k,v in x.items()if k!='tx_id'}
 if isinstance(x,list):return [norm(v,meta)for v in x]
 if isinstance(x,str):
  if x in ids:return '<'+ids[x]+'>'
  try:
   decoded=base64.b64decode(x,validate=True).decode();return {'bytes':norm(json.loads(decoded),meta)}
  except (ValueError,UnicodeError):
   try:return norm(json.loads(x),meta)if x.startswith(('{','['))else x
   except ValueError:return x
 return x

def signature(out):
 meta=out['metadata'];rows=[]
 for it in out['records']:
  r=it['row'];cr=r['response'].get('contract_result')or{};rw=it['committed'].get('rw_set')or{}
  rows.append({'tag':it['tag'],'result':norm(cr,meta),'reads':sorted((norm(v,meta)for v in rw.get('tx_reads',[])),key=lambda v:json.dumps(v,sort_keys=True)),'writes':sorted((norm(v,meta)for v in rw.get('tx_writes',[])),key=lambda v:json.dumps(v,sort_keys=True))})
 projection=sorted((norm(v,meta)for v in out['projection']),key=lambda v:json.dumps(v,sort_keys=True))
 return {'rows':rows,'projection':projection,'initial':norm(out['initial_projection'],meta)}
def check(paths,label):
 items=[json.loads(Path(p).read_text())for p in paths];assert all(x['passed']for x in items);a=signature(items[0]);checks=[]
 for x in items[1:]:
  b=signature(x);z={'group':x['group'],'matches':a==b};checks.append(z)
  if a!=b:(P/'raw_logs'/f'{label}-mismatch-{x["group"]}.json').write_text(json.dumps({'baseline':a,'other':b},indent=2))
 out={'passed':all(x['matches']for x in checks),'checks':checks,'labels':[x['label']for x in items]};(P/'raw_logs'/f'{label}-parity.json').write_text(json.dumps(out,indent=2));return out
