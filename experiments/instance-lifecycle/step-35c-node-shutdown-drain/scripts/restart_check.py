from node_smoke import Node,Client,P,H,jobs,good,record
import json,sys
label,previous=sys.argv[1:];n=Node(label);c=None;checks={}
try:
 c=Client(label)
 old=json.loads((P/'raw_logs'/f'{previous}-case.json').read_text());response=old['business']['row']['response'];tx=response['tx_id']
 row=c.call({'Op':'rwset','Path':tx,'Tag':'persisted-prior-stop'});assert row.get('transaction')and not row.get('error'),row
 tr=row['transaction']['transaction'];actual=tr['result']['contract_result'];expect=response['contract_result'];assert actual.get('gas_used',0)==expect.get('gas_used',0)and actual.get('result')==expect.get('result')
 checks['prior_tx_persisted']=True;checks['tx_id']=tx;checks['gas']=actual.get('gas_used',0)
 if previous.endswith('-active'):
  job=dict(Op='query',Contract='erc721',Method='ownerOf',Params={'tokenId':'8102'},Tag='owner-before');before=good(c.call(job));failed=record(c,dict(jobs('8101')[-1],Tag='duplicate-buyNow'),False);resp=failed.get('response')or{};assert resp.get('code',0)!=0 or(resp.get('contract_result')or{}).get('code',0)!=0
  row=c.call({'Op':'rwset','Path':resp['tx_id'],'Tag':'failed-rwset-check'});assert row.get('transaction')and not row.get('error');rw=row['transaction'].get('rw_set')or{};assert not rw.get('tx_writes'),rw
  after=good(c.call(dict(job,Tag='owner-after')));assert before['contract_result']['result']==after['contract_result']['result'];checks.update(rollback_writes_empty=True,owner_unchanged=True,failed_tx_id=resp['tx_id'])
 (P/'raw_logs'/f'{label}-persistence.json').write_text(json.dumps(checks,indent=2))
finally:
 if c:c.close()
 result=n.close();assert not result['reason']and result['systemd'].get('ExecMainStatus')=='0',result
with(P/'PROGRESS.md').open('a')as f:f.write('\nRestart check '+label+' PASS, '+json.dumps(checks)+'\n')
