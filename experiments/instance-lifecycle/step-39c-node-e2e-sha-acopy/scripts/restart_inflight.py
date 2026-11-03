from harness import *
label=sys.argv[1];source=json.loads((P/'raw_logs/smoke-inflight-inflight.json').read_text());n=c=None;out={'passed':False,'label':label,'tx_id':source['tx_id']}
try:
 n=Node(label,'E3');c=Client(label);out['initial_artifact']=manager('artifact');assert out['initial_artifact']['entries']==0
 row=c.batch([{'Op':'rwset','Path':source['tx_id'],'Tag':'inflight-committed-after-restart','Phase':'verification'}])['rows'][0];info=row.get('transaction');assert row['success']and info and info['block_height']>0 and(info['transaction']['result'].get('contract_result')or{}).get('code',0)==0
 out['committed']=row;out['continued']=c.batch([{'Op':'invoke','Contract':'compute','Method':'hashCal','Params':{},'Tag':'after-restart-business','Phase':'lifecycle'}]);good(out['continued']['rows'][0]);out['passed']=True
finally:
 if c:c.close()
 if n:
  z=n.close();out['node']=z;o=z.get('owner')or{};safe=not z['reason']and z['systemd'].get('ExecMainStatus')=='0'and o.get('managed_pending')==0 and o.get('stores_created')==o.get('stores_closed')and o.get('instances_created')==o.get('instances_closed')and z['pid_exited']and z['cgroup_empty'];out['passed']=out['passed']and safe
  if not safe:(P/'STOP_SHARED.json').write_text(json.dumps({'stage':'restart-inflight','node':z}))
 (P/'raw_logs'/f'{label}-restart.json').write_text(json.dumps(out,indent=2));assert out['passed'],label
