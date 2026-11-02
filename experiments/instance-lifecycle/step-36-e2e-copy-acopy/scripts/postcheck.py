from harness import *
label,path,probe=sys.argv[1:];x=json.loads(Path(path).read_text());cname=x['records'][-1]['row']['input']['Contract'];group=x['group'];n=client=None;out={'label':label,'case':x['case'],'group':group,'source':path,'passed':False,'rows':[]}
try:
 n=Node(label,group,ready=False);client=Client(label)
 for it in x['records']:
  if not it['tag'].startswith('target'):continue
  resp=it['row']['response'];tx=resp['tx_id'];r=client.batch([{'Op':'rwset','Path':tx,'Tag':'restart-'+it['tag'],'Phase':'restart'}])['rows'][0];info=r.get('transaction');assert r['success']and info and info['block_height']==resp['tx_block_height']and info['transaction']['result']['contract_result']==resp['contract_result'];out['rows'].append(r)
 projection={(a['Contract'],a['Key']):a['Expected']for a in x['projection']};verify_state(projection,label+'-restart')
 if probe!='none':
  cfg=json.loads((P/'inputs/cases.json').read_text())[x['case']];method=cfg['method']if probe=='empty-raffle'else'__step36_missing_export__';params=cfg['params']if probe=='empty-raffle'else{}
  fail=client.batch([{'Op':'invoke','Contract':cname,'Method':method,'Params':params,'Tag':'error-probe','Phase':'exception'}])['rows'][0];resp=fail.get('response')or{};assert not fail['success']and resp.get('tx_id')and resp.get('code',0)!=0,fail
  found=client.batch([{'Op':'rwset','Path':resp['tx_id'],'Tag':'error-probe-commit','Phase':'verification'}])['rows'][0];info=found.get('transaction');assert found['success']and info and not(info.get('rw_set')or{}).get('tx_writes'),info
  verify_state(projection,label+'-after-failure');out['exception']={'kind':probe,'row':fail,'committed':info,'writes_empty':True,'ledger_projection_unchanged':True}
 out['passed']=True
finally:
 if client:client.close()
 if n:
  z=n.close();out['node']=z;o=z.get('owner')or{};safe=not z['reason']and z['systemd'].get('ExecMainStatus')=='0'and o.get('managed_pending')==0 and o.get('stores_created')==o.get('stores_closed')and o.get('instances_created')==o.get('instances_closed')and z['pid_exited']and z['cgroup_empty'];out['passed']=out['passed']and safe
  if not safe:(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'node':z,'stage':'restart/exception'},indent=2))
 (P/'raw_logs'/f'{label}-postcheck.json').write_text(json.dumps(out,indent=2));print('POSTCHECK',label,out['passed'],flush=True);assert out['passed'],out
 with(P/'PROGRESS.md').open('a')as f:f.write('\nPostcheck '+label+' PASS; committed tx/readback'+(' + genuine error rollback'if probe!='none'else'')+' verified after restart, source'+Path(path).name+'\n')
