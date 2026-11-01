from pathlib import Path
import json,base64,csv
P=Path(__file__).resolve().parents[1];B=Path('/home/frankie/mygitprojects/.worktrees/cvw-step35/experiments/instance-lifecycle/step-35-node-fresh-integration');manifest=json.loads((B/'inputs/manifest.json').read_text());checks=[]
for lab in ['resource1','resource2','reset1','stop-reset-race']:
 events=[json.loads(l[7:])for l in(P/'raw_logs'/f'{lab}-node.log').read_text().splitlines()if l.startswith('STEP35 ')]
 for e in events:
  if e['event']=='module_prepared':assert e['source_sha']==manifest[e['contract']]['sha256']
 for f in(P/'raw_logs').glob(lab+'*-client.jsonl'):
  rs=[json.loads(l)for l in f.read_text().splitlines()];rw={x['input']['Path']:x['result']['transaction']['rw_set']for x in rs if x['input']['Op']=='rwset'}
  for x in rs:
   if x['input']['Op']!='invoke':continue
   o=x['result'].get('response')
   if not o:continue
   inp=x['input'];cr=o.get('contract_result')or{};assert o.get('code',0)==0 and cr.get('code',0)==0
   val=base64.b64decode(cr.get('result','')).decode();assert val==('buyNow success'if inp['Method']=='buyNow'else'success bigNumCal: 607723520');tx=o['tx_id'];assert tx in rw
   if inp['Method']=='buyNow':
    token=inp['Params']['tokenId'];owner=[v for v in rw[tx].get('tx_writes',[])if v.get('contract_name')=='erc721'and base64.b64decode(v['key']).decode()=='tokenIds#'+token];assert len(owner)==1 and base64.b64decode(owner[0]['value']).decode()==inp['Params']['to'];assert len(cr.get('contract_event',[]))==3
   else:assert cr.get('gas_used')==120135
   checks.append({'process':lab,'tag':inp['Tag'],'tx_id':tx,'method':inp['Method'],'gas':cr.get('gas_used'),'return_value':val,'committed':True,'business_checks':True})
with(P/'BUSINESS_CHECKS.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=list(checks[0]),lineterminator='\n');w.writeheader();w.writerows(checks)
print('frozen WASM + business semantics checked',len(checks))
