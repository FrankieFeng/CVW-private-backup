from pathlib import Path
import json,base64
P=Path(__file__).resolve().parents[1]
SENDER='628aafcf44e1dd25ebb0415e8f1d7026329eebfa'
def check_target(out,row,index):
 cfg=json.loads((P/'inputs/cases.json').read_text())[out['case']];cr=row['response'].get('contract_result')or{};assert row['success']and cr.get('code',0)==0
 text=base64.b64decode(cr.get('result','')).decode();method=cfg['method']
 if method=='address':assert text==SENDER,text
 elif method=='callerAddress':assert text=='call contract success :'+SENDER,text
 elif method=='balanceOf':assert text=='1',text
 elif method=='tokenLatestTxInfo':
  assert text.startswith('tokenLatestTxInfo is ');actual=json.loads(text[len('tokenLatestTxInfo is '):]);mint=out['setups'][0];assert actual=={'TxId':mint['row']['response']['tx_id'],'BlockHeight':mint['committed']['block_height'],'From':'0'*40,'To':cfg['setup'][0]['params']['to']},actual
 elif method=='raffle':assert text==cfg['expected_sequence'][index],text
 else:raise AssertionError(method)
 return text

def signature(x):
 def rw(info,key):return sorted((info.get('rw_set')or{}).get(key,[]),key=lambda v:json.dumps(v,sort_keys=True))
 return {'setups':[(a['row']['response']['tx_id'],a['row']['response']['contract_result'],rw(a['committed'],'tx_reads'),rw(a['committed'],'tx_writes'))for a in x['setups']],'targets':[(a['row']['response']['tx_id'],a['row']['response']['contract_result'],rw(a['committed'],'tx_reads'),rw(a['committed'],'tx_writes'))for a in x['records']],'initial':sorted(x['initial_projection'],key=lambda v:json.dumps(v,sort_keys=True)),'final':sorted(x['final_projection'],key=lambda v:json.dumps(v,sort_keys=True))}
def compare(paths):
 data=[json.loads(Path(f).read_text())for f in paths];assert all(x['passed']for x in data);baseline=signature(data[0]);checks=[]
 for x in data[1:]:
  other=signature(x);equal=baseline==other;checks.append({'variant':x['group'],'equal':equal})
  if not equal:(P/'raw_logs'/f'{x["label"]}-mismatch.json').write_text(json.dumps({'baseline':baseline,'other':other},indent=2))
 result={'passed':all(x['equal']for x in checks),'method':data[0]['case'],'phase':data[0]['phase'],'batch':data[0]['batch'],'checks':checks};(P/'raw_logs'/f'{data[0]["phase"]}-{data[0]["case"]}-b{data[0]["batch"]}-parity.json').write_text(json.dumps(result,indent=2))
 if not result['passed']:(P/'STOP_SHARED.json').write_text(json.dumps({'stage':'parity','result':result}));return False
 return True
