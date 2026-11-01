from node_smoke import Node,Client,jobs,record,good,P,TO
import json,sys
label=sys.argv[1];n=Node(label,0);c=None
try:
 c=Client(label)
 record(c,jobs('9001')[0]);job=jobs('9001')[-1];record(c,job)
 before=good(c.call(dict(Op='query',Contract='erc721',Method='ownerOf',Params={'tokenId':'9002'},Tag='owner-before-failed-duplicate')))
 row=record(c,dict(job,Tag='duplicate-buyNow'),False);resp=row.get('response')or{};assert resp and (resp.get('code',0)!=0 or(resp.get('contract_result')or{}).get('code',0)!=0),'duplicate unexpectedly succeeded'
 after=good(c.call(dict(Op='query',Contract='erc721',Method='ownerOf',Params={'tokenId':'9002'},Tag='owner-after-failed-duplicate')))
 assert before['contract_result']['result']==after['contract_result']['result']
 (P/'raw_logs'/f'{label}-rollback.json').write_text(json.dumps({'duplicate_failed':True,'owner_unchanged':True,'before':before,'after':after},indent=2))
 assert not n.reason,n.reason
finally:
 if c:c.close()
 n.close()
