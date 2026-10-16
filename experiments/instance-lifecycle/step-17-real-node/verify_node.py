#!/usr/bin/env python3
from pathlib import Path
import json,collections,sys,base64
from run import O,Client,record,job,specs,modes,restart,snapshot
sys.path.insert(0,str(O.parent/'step-15-copy-attribution'));from common import csvwrite

def rwsets():
 c=Client();raw=open(O/'ledger_validation.jsonl','a');allrows=[]
 # Fetch first and last warm transaction in each contract/batch/mode from the real committed ledger.
 groups=collections.defaultdict(list)
 for f in sorted(O.glob('bench-*-w*.jsonl')):
  for l in f.read_text().splitlines():
   r=json.loads(l)
   if ':cold:' not in r['tag'] and ':warmup:' not in r['tag']:groups[(f.name,r['contract'],r['mode'])].append(r)
 jobs=[]
 for group,rs in groups.items():
  for r in [rs[0],rs[-1]]:jobs.append(dict(Mode=r['mode'],Op='rwset',Contract=r['contract'],Path=r['response']['tx_id'],Tag=r['tag']))
 for i in range(0,len(jobs),16):allrows+=record(c,jobs[i:i+16],raw)
 checks=[];pairs=collections.defaultdict(dict)
 for r in allrows:pairs[r['tag']][r['mode']]=r
 def normalize(r):
  tx=r.get('transaction') or {};rw=tx.get('rw_set') or tx.get('rwset') or tx.get('tx_rw_set') or {}
  return sorted(rw.get('tx_writes',[]),key=lambda x:(x.get('contract_name',''),x.get('key','')))
 for tag,p in pairs.items():
  b,o=p['baseline'],p['optimized'];a,z=normalize(b),normalize(o)
  checks.append(dict(pair=tag,contract=b['contract'],baseline_writes=len(a),optimized_writes=len(z),writes='pass' if a==z and not b.get('error') and not o.get('error') else 'fail',baseline_error=b.get('error',''),optimized_error=o.get('error','')))
 csvwrite(O/'ledger_equivalence.csv',checks);print('ledger checks',len(checks),'failed',sum(r['writes']!='pass' for r in checks));c.close();raw.close()

def diagnostic():
 # Opt-in expensive full-memory hashes, entirely outside performance batches.
 import os
 os.environ['CM_INSTANCE_LIFECYCLE_TRACE']='1';restart();c=Client();f=open(O/'diagnostic.jsonl','a')
 for s in specs:
  for m in modes:record(c,[job(s,m,'diagnostic:'+s['label'],900000000001+specs.index(s))],f)
 for s in specs:
  for m in modes:record(c,[dict(Mode=m,Op='invoke',Contract=s['label'],Method='__missing_step17',Params={},Tag='missing:'+s['label'])],f)
 # Explicit application error and persisted real cross-contract owner state.
 for m in modes:
  record(c,[dict(Mode=m,Op='invoke',Contract='exchange',Method='buyNow',Params={},Tag='exchange-invalid-args'),dict(Mode=m,Op='invoke',Contract='erc721',Method='mint',Params={'to':'bad','tokenId':'1'},Tag='erc721-invalid-address')],f)
 for m in modes:
  record(c,[dict(Mode=m,Op='query',Contract='erc721',Method='ownerOf',Params={'tokenId':str(900000000001+4)},Tag='exchange-owner'),dict(Mode=m,Op='query',Contract='identity',Method='isApprovedUser',Params=specs[5]['params'],Tag='identity-whitelist')],f)
 c.close();f.close();snapshot('diagnostic-end')
if __name__=='__main__':
 {'ledger':rwsets,'diagnostic':diagnostic}[sys.argv[1]]()
