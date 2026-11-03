from harness import *
from correctness import check_target
label,case,group,phase,batch=sys.argv[1:];batch=int(batch);cfg=json.loads((P/'inputs/cases.json').read_text())[case];ctl=json.loads((P/'inputs/variants-control.json').read_text())[group];seed=Path(json.loads((P/'inputs/seeds.json').read_text())[cfg['contract']+('-A'if ctl['A']else'-plain')]);N=cfg['precheck_n']if phase=='pre'else cfg['formal_n'];node=client=None;proj={};out={'label':label,'case':case,'group':group,'phase':phase,'batch':batch,'planned':N,'passed':False,'setups':[],'records':[]}
def make(tag,method=None,params=None,op='invoke'):
 return {'Op':op,'Contract':cfg['contract'],'Method':method or cfg['method'],'Params':cfg['params']if params is None else params,'Tag':tag,'Phase':phase,'TxID':hashlib.sha256((case+'|'+phase+'|'+str(batch)+'|'+tag).encode()).hexdigest()}
def receipt(row):
 r=good(row);v=client.batch([{'Op':'rwset','Path':r['tx_id'],'Tag':'receipt','Phase':'verification'}])['rows'][0];assert v['success']and v['transaction'];info=v['transaction'];assert info['block_height']==r['tx_block_height']>0 and info['transaction']['result']['contract_result']==r['contract_result']
 for w in(info.get('rw_set')or{}).get('tx_writes',[]):proj[(w['contract_name'],w['key'])]=w.get('value')
 return info
try:
 clone(seed,H);node=Node(label,group);out['preflight']=node.preflight;client=Client(label);out['artifact_initial']=manager('artifact')
 for i,s in enumerate(cfg['setup']):
  row=client.batch([make('setup-'+str(i),s['method'],s['params'])])['rows'][0];info=receipt(row);out['setups'].append({'row':row,'committed':info})
 if out['setups']:
  out['probe']=out['setups'][-1];height=out['probe']['committed']['block_height']
 else:
  row=client.batch([make('readiness-probe')])['rows'][0];info=receipt(row);check_target(out,row,0);out['probe']={'row':row,'committed':info};height=info['block_height']
 out['post_probe_gate']=ready_gate(label+'-post-probe',height)
 warm=client.batch([make('warmup',op='query')])['rows'][0];good(warm);check_target(out,warm,0);out['warmup']=warm;out['artifact_before']=manager('artifact');out['before_window_gate']=ready_gate(label+'-before-window',height)
 out['initial_projection']=[{'Contract':c,'Key':k,'Expected':v}for(c,k),v in proj.items()];verify_state(proj,label+'-initial')
 window=client.batch([make('target-'+str(i))for i in range(N)]);out['window']=window;assert window['attempted']==N and window['successful_responses']==N
 for i,row in enumerate(window['rows']):
  info=receipt(row);text=check_target(out,row,i);out['records'].append({'row':row,'committed':info,'expected_checked':True,'decoded_result':text})
 out['final_projection']=[{'Contract':c,'Key':k,'Expected':v}for(c,k),v in proj.items()];verify_state(proj,label+'-final');out['after_window_gate']=ready_gate(label+'-after-window',out['records'][-1]['committed']['block_height']);out['artifact_after']=manager('artifact');out['owner_after']=manager('state');assert out['owner_after']['accepted']==N+2 and out['owner_after']['limit']==32
 if ctl['sha']:assert out['artifact_after']['entries']==1 and out['artifact_after']['hits']>out['artifact_before']['hits']and out['artifact_after']['bytes']<=64*1024*1024
 else:assert out['artifact_after']['entries']==0
 if any(r['elapsed_ns']>1_000_000_000 for r in window['rows']):raise RuntimeError('seconds-level latency: retain fullwindow and pause for phase review')
 out['passed']=True
except BaseException as e:
 out['error']=repr(e);(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'stage':'readiness_business_resource','error':repr(e)},indent=2))
finally:
 if client:client.close()
 if node:
  z=node.close();out['node']=z;o=z.get('owner')or{};safe=not z['reason']and z['systemd']['ExecMainStatus']=='0'and z['pid_exited']and z['cgroup_empty']and o.get('managed_pending')==0 and o.get('stores_created')==o.get('stores_closed')and o.get('instances_created')==o.get('instances_closed');out['passed']=out['passed']and safe
  if not safe:(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'stage':'shutdown','node':z}))
 (P/'raw_logs'/f'{label}-case.json').write_text(json.dumps(out,indent=2));print('CASE',label,out['passed'],out.get('error',''),flush=True)
 with(P/'PROGRESS.md').open('a')as f:f.write('\n'+label+' '+str(out['passed'])+' '+out.get('error','')+'\n')
 if not out['passed']:raise SystemExit(2)
