from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
def receipt(label,slot,v):return json.loads((P/'raw_logs'/f'{label}-receipts'/f'pair-{slot:03d}-{v}.json').read_text())
def check(a,b,exchange=False):
 for k in ['tx_id','contract','method','business_input','before_hash','after_hash','status','actual_result','actual_rwset']:assert a[k]==b[k],f'pair semantic mismatch {k}'
 assert a['status']==0 and a['actual_result'].get('code',0)==0
 fields=['id','depth','contract','method','tx_id','gas_used_actual','code','result','message']
 ac=sorted(a['inclusive_call_records_do_not_sum'],key=lambda r:r['id']);bc=sorted(b['inclusive_call_records_do_not_sum'],key=lambda r:r['id'])
 assert[{k:r.get(k)for k in fields}for r in ac]==[{k:r.get(k)for k in fields}for r in bc]
 assert len(ac)==(7 if exchange else 1)and all(r['code']==0 for r in ac)
 if exchange:
  assert [(r['contract'],r['method'],r['depth'])for r in ac]==[('exchange','buyNow',0),('identity','addWriteList',1),('identity','isApprovedUser',1),('identity','isApprovedUser',1),('erc721','mint',1),('erc721','setApprovalForAll2',1),('erc721','transferFrom',1)]
 return dict(gas=a['actual_result'].get('gas_used',0),calls=len(ac),semantic_equal=True,before_hash=a['before_hash'],after_hash=a['after_hash'])
def local(label,n=1):return[check(receipt(label,i,'A0'),receipt(label,i,'A1'))for i in range(n)]
def setup_check(label):
 folder=P/'raw_logs'/f'{label}-receipts';n=0
 for a in folder.glob('setup-*-A0.json'):
  b=folder/(a.name[:-7]+'A1.json')
  assert b.exists(),b
  check(json.loads(a.read_text()),json.loads(b.read_text()));n+=1
 return n
