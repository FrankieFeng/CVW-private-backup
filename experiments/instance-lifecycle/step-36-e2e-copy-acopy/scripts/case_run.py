from harness import *
import copy
label,case,group,phase,batch=sys.argv[1:];batch=int(batch);cases=json.loads((P/'inputs/cases.json').read_text());cfg=cases[case];cname=cfg['contract'];n=cfg.get('precheck_n',1) if phase=='precheck'else cfg['formal_n'];flavor='A'if group in ['G2','G3']else'plain';seed=Path('/tmp/cvw-step36-seed-'+cname+'-'+flavor);out={'label':label,'case':case,'group':group,'phase':phase,'batch':batch,'planned':n,'passed':False,'status':'FAILED_RUNTIME','records':[]};node=client=None;projection={};metadata=[];failedrow=None
# Setup rows all precede window; distinct mutable targets prevent duplicate-token failures.
def prepare():
 base=cfg['params'];mutable_token=cname in ['erc721','exchange']and cfg['method']in ['mint','mint2','transferFrom','approve','buyNow'];addresses=cname=='identity'and cfg['method']in ['addWriteList','removeWriteList'];targets=[];setups=[];seen=set()
 for i in range(n):
  params=copy.deepcopy(base)
  token=str(1001+i)if mutable_token else None
  if token is not None:params['tokenId']=token
  if addresses:params['address']=params['address'][:-4]+format(1001+i,'04x')
  for st in cfg['setup']:
   sp=copy.deepcopy(st['params'])
   if token and 'tokenId'in sp:sp['tokenId']=token
   if addresses and 'address'in sp:sp['address']=params['address']
   key=json.dumps([st['method'],sp],sort_keys=True)
   if key not in seen:seen.add(key);setups.append({'Op':'invoke','Contract':cname,'Method':st['method'],'Params':sp,'Phase':'setup','Tag':'setup-'+str(len(setups))})
  targets.append({'Op':'invoke','Contract':cname,'Method':cfg['method'],'Params':params,'Phase':phase,'Tag':'target-'+str(i)})
 return setups,targets

def committed(row,tag):
 global failedrow
 resp=row.get('response')or{};tx=resp.get('tx_id')
 if not tx:raise RuntimeError('missing TxID '+str(row.get('error')))
 verify=client.batch([{'Op':'rwset','Path':tx,'Tag':tag+'-commit','Phase':'verification'}]);v=verify['rows'][0];info=v.get('transaction');assert v.get('success')and info,'transaction not queryable'
 assert info['block_height']==resp.get('tx_block_height')and info['block_height']>0,'height mismatch'
 stored=info['transaction']['result']['contract_result'];orig=resp.get('contract_result')or{};assert stored==orig,'RPC/committed result mismatch'
 rw=info.get('rw_set')or{}
 for w in rw.get('tx_writes',[]):projection[(w['contract_name'],w['key'])]=w.get('value')
 item={'row':row,'committed':info,'tag':tag};out['records'].append(item);metadata.append({'tag':tag,'tx_id':tx,'height':info['block_height'],'timestamp':info.get('block_timestamp')});return item
try:
 assert seed.exists(),'missing seed';clone(seed,H);node=Node(label,group);client=Client(label);setups,targets=prepare()
 for j in setups+targets:j['TxID']=hashlib.sha256((case+'|'+phase+'|'+str(batch)+'|'+j['Tag']).encode()).hexdigest()
 for j in setups:
  res=client.batch([j]);r=res['rows'][0];failedrow=r;committed(r,j['Tag']);good(r)
 # Query only warms compiled Module/template; no block submission or executed Instance reuse.
 warm=copy.deepcopy(targets[0]);warm['Op']='query';warm['Phase']='warmup';warm['Tag']='warmup';warm['TxID']=hashlib.sha256((case+'|'+phase+'|'+str(batch)+'|warmup').encode()).hexdigest()
 if cname=='identity'and cfg['method']in ['alterAdminAddress','removeWriteList']:warm['Method']='address';warm['Params']={}
 if cname in ['erc721','exchange']and cfg['method']in ['mint','mint2','buyNow']:warm['Params']['tokenId']='9001'
 w=client.batch([warm]);out['warmup']=w;failedrow=w['rows'][0];good(failedrow)
 out['initial_projection']=dict((c+'|'+k,v)for(c,k),v in projection.items());verify_state(projection,label+'-before')
 result=client.batch(targets);out['window']=result
 # The real formal batch contains no queries or Python loop delays.
 for r in result['rows']:
  failedrow=r;committed(r,r['input']['Tag']);good(r)
  text=base64.b64decode((r['response'].get('contract_result')or{}).get('result','')).decode(errors='replace');expected=cfg.get('expected_sequence',[cfg.get('expected','')]*n)[int(r['input']['Tag'].split('-')[-1])];assert not expected or text.startswith(expected),(text,expected)
 assert result['attempted']==n and result['successful_responses']==n,'partial batch'
 verify_state(projection,label+'-after');out.update(passed=True,status='PASSED'if phase=='formal'else'READY',metadata=metadata,projection=[{'Contract':c,'Key':k,'Expected':v}for(c,k),v in projection.items()])
except BaseException as e:
 out['error']=repr(e)
 if 'missing seed'in str(e):out['status']='BLOCKED_BUILD'
 elif out.get('window')is None:out['status']='BLOCKED_FIXTURE'
 if failedrow:out['failed_row']=failedrow
finally:
 if client:client.close()
 if node:
  z=node.close();out['node']=z;owner=z.get('owner')or{};safe=not z['reason']and z['systemd'].get('ExecMainStatus')=='0'and z['pid_exited']and z['cgroup_empty']and owner.get('managed_pending')==0 and owner.get('stores_created')==owner.get('stores_closed')and owner.get('instances_created')==owner.get('instances_closed')
  if not safe:
   out.update(passed=False,status='BLOCKED_SAFETY');(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'node':z,'reason':'shared runtime/guard failure; stop entire round'},indent=2))
 (P/'raw_logs'/f'{label}-case.json').write_text(json.dumps(out,indent=2));print('CASE',label,out['status'],out.get('error',''),flush=True)
 with(P/'PROGRESS.md').open('a')as f:f.write('\n'+label+' '+out['status']+'; raw logs/state/receipts saved. '+out.get('error','')[:200]+'\n')
 if not out['passed']:raise SystemExit(2)
