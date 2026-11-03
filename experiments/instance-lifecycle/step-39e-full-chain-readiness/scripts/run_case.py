from harness import *
label,case,group,phase,batch=sys.argv[1:];batch=int(batch);cfg=json.loads((P/'inputs/cases.json').read_text())[case];cname=cfg['contract'];seed=Path('/tmp/cvw-step39e-seed-'+cname+('-A'if group=='E3'else'-plain'));out={'label':label,'case':case,'group':group,'phase':phase,'batch':batch,'passed':False,'records':[]};n=client=None

def job(tag,op='invoke'):
 return {'Op':op,'Contract':cname,'Method':cfg['method'],'Params':cfg['params'],'Phase':tag,'Tag':tag,'TxID':hashlib.sha256((case+'|'+phase+'|'+str(batch)+'|'+tag).encode()).hexdigest()}
def receipt(row):
 r=good(row);v=client.batch([{'Op':'rwset','Path':r['tx_id'],'Tag':'verify-'+r['tx_id'],'Phase':'verification'}])['rows'][0];assert v['success']and v['transaction'];x=v['transaction'];assert x['block_height']==r['tx_block_height']and x['block_height']>0 and x['transaction']['result']['contract_result']==r['contract_result'];assert not(x.get('rw_set')or{}).get('tx_writes');return x
try:
 assert not(P/'STOP_SHARED.json').exists();clone(seed,H);n=Node(label,group);out['preflight']=n.preflight;out['artifact_initial']=manager('artifact');out['owner_initial']=manager('state');client=Client(label)
 # Cold business is a REAL submitted transaction, outside the steady window.
 out['probe']=client.batch([job('cold-readiness-probe')]);row=out['probe']['rows'][0];out['probe_committed']=receipt(row);height=out['probe_committed']['block_height'];out['full_gate']=ready_gate(label+'-post-probe',height);out['artifact_after_probe']=manager('artifact')
 warm=client.batch([job('cache-warmup','query')]);good(warm['rows'][0]);out['warmup']=warm;out['before_window_gate']=ready_gate(label+'-before-window',height)
 targets=[job('target-'+str(i))for i in range(6)];window=client.batch(targets);out['window']=window
 assert window['attempted']==6 and window['successful_responses']==6
 for row in window['rows']:
  info=receipt(row);out['records'].append({'row':row,'committed':info})
 if any(r['elapsed_ns']>1_000_000_000 for r in window['rows']):raise RuntimeError('seconds-level target latency: preserve window and review before any expansion')
 out['after_window_gate']=ready_gate(label+'-after-window',out['records'][-1]['committed']['block_height']);out['owner_after']=manager('state');out['artifact_after']=manager('artifact');assert out['owner_after']['accepted']==8 and out['owner_after']['limit']==32
 if phase=='validation'and batch in [1,2]:
  before=manager('state');out['reset']=manager('reset',True);after=manager('state');assert before['accepted']==after['accepted']and after['limit']==32;out['reset_budget_before']=before;out['reset_budget_after']=after;out['artifact_after_reset']=manager('artifact');assert out['artifact_after_reset']['entries']==0
  row=client.batch([job('after-reset')])['rows'][0];out['after_reset_row']=row;out['after_reset_committed']=receipt(row);out['after_reset_gate']=ready_gate(label+'-after-reset',out['after_reset_committed']['block_height'])
 out['passed']=True
except BaseException as e:
 out['error']=repr(e);(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'stage':'business_or_gate','error':repr(e)},indent=2))
finally:
 if client:client.close()
 if n:
  z=n.close();out['node']=z;o=z.get('owner')or{};safe=not z['reason']and z['systemd']['ExecMainStatus']=='0'and z['pid_exited']and z['cgroup_empty']and o.get('managed_pending')==0 and o.get('stores_created')==o.get('stores_closed')and o.get('instances_created')==o.get('instances_closed');out['passed']=out['passed']and safe
  if not safe:(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'stage':'shutdown','node':z}))
 (P/'raw_logs'/f'{label}-case.json').write_text(json.dumps(out,indent=2));print('CASE',label,out['passed'],out.get('error',''),flush=True)
 with(P/'PROGRESS.md').open('a')as f:f.write('\n'+label+' '+str(out['passed'])+' '+out.get('error','')+'; logs/receipts/ready/probe/cold/formal/close saved.\n')
 if not out['passed']:raise SystemExit(2)
