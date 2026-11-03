from harness import *
label,stage=sys.argv[1:];n=c=None;out={'label':label,'stage':stage,'passed':False,'rows':[]}
try:
 if stage=='seed0':clone(SOURCE,H,True)
 n=Node(label,'E0'if stage.startswith('seed')else'E3');c=Client(label);v=json.loads((P/'inputs/variants.json').read_text())['compute-G2']
 def record(job,expect=True):
  row=c.batch([job])['rows'][0];out['rows'].append(row)
  if expect:
   if row.get('transaction')is not None:assert row.get('success')
   else:good(row)
  return row
 if stage.startswith('seed'):
  indices={'seedfix12':[1,2],'seedfix45':[4,5]}.get(stage)
  if indices is None:
   start=3*int(stage[-1]);indices=list(range(start,start+3))
  for i in indices:
   r=record({'Op':'deploy','Contract':f'cap{i}','Path':v['path'],'Params':{},'Tag':f'deploy-cap{i}','Phase':'capacity-deployment'});tx=r['response']['tx_id'];z=record({'Op':'rwset','Path':tx,'Tag':f'confirm-cap{i}'});assert z['transaction']['block_height']==r['response']['tx_block_height'];print('CAP DEPLOY',i,flush=True)
 else:
  out['initial']=manager('artifact');assert out['initial']['max_entries']==8 and out['initial']['max_bytes']==64*1024**2
  for i in range(8):
   record({'Op':'query','Contract':f'cap{i}','Method':'hashCal','Params':{},'Tag':f'fill-{i}','Phase':'capacity-query'});state=manager('artifact');out.setdefault('states',[]).append(state);assert state['entries']==i+1;print('CAP FILL',i+1,'rssMiB',n.peakR/1024,flush=True)
  r=record({'Op':'query','Contract':'cap8','Method':'hashCal','Params':{},'Tag':'ninth-rejected','Phase':'capacity-query'},False);assert not r['success']and'bounded artifact registry full'in json.dumps(r),r
  state=manager('artifact');assert state['entries']==8 and state['rejects']>=1;out['full_rejected']=state
  out['reset']=manager('reset',True);assert out['reset']['error']=='<nil>';out['reset_state']=manager('artifact');assert out['reset_state']['entries']==0 and out['reset_state']['bytes']==0
  record({'Op':'query','Contract':'cap8','Method':'hashCal','Params':{},'Tag':'ninth-after-reset','Phase':'capacity-query'});out['recovered']=manager('artifact');assert out['recovered']['entries']==1
 out['passed']=True
finally:
 if c:c.close()
 if n:
  z=n.close();out['node']=z;o=z.get('owner')or{};safe=not z['reason']and z['systemd'].get('ExecMainStatus')=='0'and o.get('managed_pending')==0 and o.get('stores_created')==o.get('stores_closed')and o.get('instances_created')==o.get('instances_closed')and z['pid_exited']and z['cgroup_empty'];out['passed']=out['passed']and safe
  if not safe:(P/'STOP_SHARED.json').write_text(json.dumps({'stage':'capacity','node':z,'label':label},indent=2))
 (P/'raw_logs'/f'{label}-capacity.json').write_text(json.dumps(out,indent=2));assert out['passed'],label+' failed; see preserved capacity.json'
