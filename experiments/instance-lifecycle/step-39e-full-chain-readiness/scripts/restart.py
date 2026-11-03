from harness import *
label,case,group,source=sys.argv[1:];x=json.loads(Path(source).read_text());cfg=json.loads((P/'inputs/cases.json').read_text())[case];n=c=None;out={'label':label,'case':case,'group':group,'passed':False,'readbacks':[]}
def job(tag):return {'Op':'invoke','Contract':cfg['contract'],'Method':cfg['method'],'Params':cfg['params'],'Phase':'restart_probe','Tag':tag,'TxID':hashlib.sha256((label+'|'+tag).encode()).hexdigest()}
def verify(row):
 r=good(row);v=c.batch([{'Op':'rwset','Path':r['tx_id'],'Tag':'new-receipt','Phase':'verification'}])['rows'][0];assert v['success'];info=v['transaction'];assert info['block_height']==r['tx_block_height']and info['transaction']['result']['contract_result']==r['contract_result']and not(info.get('rw_set')or{}).get('tx_writes');return info
try:
 n=Node(label,group);out['preflight']=n.preflight;c=Client(label)
 for it in x['records']:
  r=it['row']['response'];v=c.batch([{'Op':'rwset','Path':r['tx_id'],'Tag':'old-receipt','Phase':'restart_readback'}])['rows'][0];assert v['success'];info=v['transaction'];assert info['block_height']==r['tx_block_height']and info['transaction']['result']['contract_result']==r['contract_result'];out['readbacks'].append(v)
 row=c.batch([job('restart-business')])['rows'][0];out['probe']=row;out['probe_committed']=verify(row);out['post_probe_gate']=ready_gate(label+'-post-probe',out['probe_committed']['block_height']);out['artifact_before_reset']=manager('artifact');before=manager('state');out['reset']=manager('reset',True);after=manager('state');assert before['accepted']==after['accepted']==1 and after['limit']==32;out['budget_before']=before;out['budget_after']=after;out['artifact_after_reset']=manager('artifact');assert out['artifact_after_reset']['entries']==0
 row=c.batch([job('restart-after-reset')])['rows'][0];out['after_reset_probe']=row;out['after_reset_committed']=verify(row);out['post_reset_gate']=ready_gate(label+'-post-reset',out['after_reset_committed']['block_height']);out['artifact_final']=manager('artifact');assert out['artifact_final']['entries']==(1 if group=='E3'else 0);out['passed']=True
except BaseException as e:
 out['error']=repr(e);(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'stage':'restart','error':repr(e)}))
finally:
 if c:c.close()
 if n:
  z=n.close();out['node']=z;o=z.get('owner')or{};safe=not z['reason']and z['systemd']['ExecMainStatus']=='0'and z['pid_exited']and z['cgroup_empty']and o.get('managed_pending')==0 and o.get('stores_created')==o.get('stores_closed')and o.get('instances_created')==o.get('instances_closed');out['passed']=out['passed']and safe
  if not safe:(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'stage':'restart_close','node':z}))
 (P/'raw_logs'/f'{label}-restart.json').write_text(json.dumps(out,indent=2));print('RESTART',label,out['passed'],out.get('error',''),flush=True)
 if not out['passed']:raise SystemExit(2)
