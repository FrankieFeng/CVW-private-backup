from harness import *
label=sys.argv[1];mode=sys.argv[2];n=c=None;out={'label':label,'mode':mode,'passed':False,'rows':[]}
try:
 if mode=='upgrade':clone(Path('/tmp/cvw-step39c-seed-compute-plain'),H)
 n=Node(label,'E3');c=Client(label);vs=json.loads((P/'inputs/variants.json').read_text());plain=vs['compute-G0']['path'];aligned=vs['compute-G2']['path']
 def call(job,expect=True):
  row=c.batch([job])['rows'][0];out['rows'].append(row)
  if expect:
   if row.get('transaction')is not None:assert row.get('success')
   else:good(row)
  return row
 def query(tag):return call({'Op':'query','Contract':'compute','Method':'hashCal','Params':{},'Tag':tag,'Phase':'lifecycle'})
 out['initial']=manager('artifact');query('before');out['before']=manager('artifact')
 if mode in ['upgrade','retry','resume']:
  if mode!='resume':
   up=call({'Op':'upgrade','Contract':'compute','Version':'2.0.0','Path':aligned,'Params':{},'Tag':'upgrade-v2','Phase':'upgrade'});resp=up['response'];tx=resp['tx_id'];stored=call({'Op':'rwset','Path':tx,'Tag':'upgrade-confirm'});assert stored['transaction']['block_height']==resp['tx_block_height']
  query('after-version-upgrade');out['upgraded']=manager('artifact');assert any(a['name']=='compute'and a['version']=='2.0.0'and a['sha']==vs['compute-G2']['sha']for a in out['upgraded']['items'])
  beforeReject=manager('artifact');same=call({'Op':'upgrade','Contract':'compute','Version':'2.0.0','Path':plain,'Params':{},'Tag':'same-version-different-code','Phase':'expected-rejection'},False);assert not same['success'];out['rejected']=manager('artifact');assert out['rejected']==beforeReject
  query('after-rejected-upgrade');out['after_rejection']=manager('artifact');assert all(a['sha']==vs['compute-G2']['sha']for a in out['after_rejection']['items']if a['version']=='2.0.0')
  out['reset']=manager('reset',True);assert out['reset']['error']=='<nil>';out['reset_state']=manager('artifact');assert out['reset_state']['entries']==0 and out['reset_state']['bytes']==0
  query('after-reset');out['after_reset']=manager('artifact');assert out['after_reset']['entries']==1
 else:
  assert out['initial']['entries']==0;assert out['before']['entries']==1 and out['before']['items'][0]['version']=='2.0.0'and out['before']['items'][0]['sha']==vs['compute-G2']['sha']
  out['owner_before_reset']=manager('state');out['budget_reset']=manager('reset',True);out['owner_after_reset']=manager('state');assert out['budget_reset']['error']=='<nil>'and out['owner_after_reset']['accepted']==out['owner_before_reset']['accepted']and out['owner_after_reset']['limit']==32
  query('after-budget-preserving-reset')
 out['passed']=True
finally:
 if c:c.close()
 if n:
  z=n.close();out['node']=z;o=z.get('owner')or{};safe=not z['reason']and z['systemd'].get('ExecMainStatus')=='0'and o.get('managed_pending')==0 and o.get('stores_created')==o.get('stores_closed')and o.get('instances_created')==o.get('instances_closed')and z['pid_exited']and z['cgroup_empty'];out['passed']=out['passed']and safe
  if not safe:(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'stage':'upgrade','node':z},indent=2))
 (P/'raw_logs'/f'{label}-upgrade.json').write_text(json.dumps(out,indent=2));assert out['passed'],label+' failed; see upgrade.json'
