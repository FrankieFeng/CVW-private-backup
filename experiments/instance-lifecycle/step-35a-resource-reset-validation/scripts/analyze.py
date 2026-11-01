from pathlib import Path
import csv,json,collections,hashlib
P=Path(__file__).resolve().parents[1]
def write(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/name).open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader();w.writerows(rows)
rows=[]
for f in sorted((P/'raw_logs').glob('*-snapshot-*.json')):
 x=json.loads(f.read_text());d=x['native_diagnostic'];st=dict(s.split(':',1)for s in x['proc_status'].splitlines()if':'in s);label=f.name.split('-snapshot-')[0];ep=sum('epoll'in t['wchan']for t in x['thread_details']);r={'process':label,'checkpoint':x['tag'],'diagnostic_forced_collection':x['tag'].startswith('forced-'),'rss_mib':int(st['VmRSS'].split()[0])/1024,'heap_mib':x['go_heap']/1024**2,'heap_sys_mib':x['go_heap_sys']/1024**2,'heap_idle_mib':x['go_heap_idle']/1024**2,'heap_released_mib':x['go_heap_released']/1024**2,'gc_count':x['go_num_gc'],'gc_pause_total_ms':x['go_pause_total_ns']/1e6,'goroutines':x['goroutines'],'os_threads':x['os_threads'],'epoll_wait_threads':ep,'go_thread_create_records':x.get('go_thread_create_records','not_recorded'),'modules_cached':x['modules_cached'],'stores_created':x['stores_created'],'stores_closed':x['stores_closed'],'instances_created':x['instances_created'],'instances_closed':x['instances_closed'],'managed_pending':x['managed_pending'],'wasi_created':d['wasi_created'],'wasi_closed':d['wasi_closed'],'import_containers_created':d['import_containers_created'],'import_containers_closed':d['import_containers_closed'],'host_function_registrations':d['host_function_registrations'],'glibc_inuse_mib':d['glibc_inuse_bytes']/1024**2,'glibc_free_mib':d['glibc_free_bytes']/1024**2,'glibc_arena_mib':d['glibc_arena_bytes']/1024**2,'glibc_mmap_mib':d['glibc_mmap_bytes']/1024**2,'store_last_strong_delete':d.get('store_last_strong_delete','not_recorded'),'store_shared_strong_delete':d.get('store_shared_strong_delete','not_recorded'),'wall_ns':x['wall_ns'],'source':str(f.relative_to(P))};rows.append(r)
 assert x['inflight']==0
 assert x['instances_created']==x['instances_closed']
 assert d['wasi_created']==d['wasi_closed']and d['host_function_registrations']==0
 assert d['import_containers_created']==d['import_containers_closed']
 assert x['stores_created']-x['stores_closed']==x['modules_cached']
rows.sort(key=lambda r:(r['process'],r['wall_ns']));write('RESOURCE_SUMMARY.csv',rows)
outs=[json.loads(f.read_text())for f in sorted((P/'raw_logs').glob('*-outcome.json'))];write('PROCESS_SUMMARY.csv',[{'process':r['label'],'rss_peak_mib':r['peak_rss_kib']/1024,'threads_peak':r['peak_threads'],'reason':r['reason'],'exit_status':r['systemd']['ExecMainStatus'],'pid_exited':r['pid_exited'],'cgroup_empty':r['cgroup_empty'],**r['owner']}for r in outs])
resetrows=[];calls=[];checks=[]
for out in outs:
 label=out['label'];txt=(P/'raw_logs'/f'{label}-node.log').read_text();ev=[json.loads(l[7:])for l in txt.splitlines()if l.startswith('STEP35 ')];starts=[x for x in ev if x['event']=='manager_reset_begin'];ends=[x for x in ev if x['event']=='manager_reset_end'];assert len(starts)==len(ends)
 for i,(a,b)in enumerate(zip(starts,ends)):
  assert b['error']=='<nil>'
  resetrows.append({'process':label,'sequence':i+1,'inflight_on_entry':a['inflight'],'duration_ms':b['reset_ns']/1e6,'error':b['error'],'begin_wall_ns':a['wall_ns'],'end_wall_ns':b['wall_ns'],'public_Manager_entry':True})
 calls.extend(dict(process=label,**x)for x in ev if x['event']=='invoke_end')
 # All new root/child runtime Store pointers differ from the cached Module's compile Store.
 assert all(x.get('store_id')!=x.get('compile_store_id')for x in ev if x['event']=='invoke_end')
 for f in (P/'raw_logs').glob(label+'*-client.jsonl'):
  for l in f.read_text().splitlines():
   x=json.loads(l);inp=x['input'];o=x['result'];
   if inp.get('Op')=='rwset':
    info=o.get('transaction');assert info and not o.get('error');tr=info['transaction'];cr=tr.get('result',{}).get('contract_result',{});checks.append({'process':label,'tag':inp['Tag'],'tx_id':inp.get('Path'),'committed_query':True,'result_code':cr.get('code',0),'gas':cr.get('gas_used',0),'rw_writes':len(info['rw_set'].get('tx_writes',[]))});assert cr.get('code',0)==0
 # Verify all successful buyNow roots have the six actual Guest children.
 for root in [x for x in ev if x['event']=='invoke_end'and x.get('contract')=='exchange'and x.get('depth')==0 and x['code']==0]:
  seq=[(x['contract'],x['method'])for x in ev if x['event']=='invoke_begin'and x['tx_id']==root['tx_id']and x['depth']==1];assert seq==[('identity','addWriteList'),('identity','isApprovedUser'),('identity','isApprovedUser'),('erc721','mint'),('erc721','setApprovalForAll2'),('erc721','transferFrom')],seq
 assert out['owner']['managed_pending']==0 and out['owner']['stores_created']==out['owner']['stores_closed']and out['owner']['instances_created']==out['owner']['instances_closed']and out['pid_exited']and out['cgroup_empty']and not out['reason']
write('RESET_EVENTS.csv',resetrows);write('INVOCATIONS.csv',calls);write('COMMIT_CHECKS.csv',checks)
# Submitted-during-reset transactions: distinguish submission from actual VM admission. Do not assume RPC receipt means VM entry.
ordering=[]
for label in ['reset1']:
 rs=[json.loads(l)for f in(P/'raw_logs').glob(label+'-second-client.jsonl')for l in f.read_text().splitlines()];ev=[json.loads(l[7:])for l in(P/'raw_logs'/f'{label}-node.log').read_text().splitlines()if l.startswith('STEP35 ')]
 endevents=[x for x in ev if x['event']=='manager_reset_end'];
 for x in rs:
  if x['input'].get('Op')!='invoke':continue
  resp=x['result']['response'];tx=resp['tx_id'];entries=[e for e in ev if e['event']=='invoke_begin'and e['tx_id']==tx and e['depth']==0];assert len(entries)==1
  before=[e for e in endevents if e['wall_ns']<=entries[0]['wall_ns']];ordering.append({'tag':x['input']['Tag'],'tx_id':tx,'entered_VM_after_Reset_end':bool(before),'client_status':resp.get('code',0),'root_VM_count':len(entries)})
write('ADMISSION_ORDER.csv',ordering)
native_rows=[]
for name in ['native-store-only','native-wasi-close','native-wasi-idle10']:
 for l in(P/'raw_logs'/f'{name}.log').read_text().splitlines():
  if l.startswith('{'):native_rows.append({'process':name,**json.loads(l)})
write('NATIVE_THREAD_CONTROLS.csv',native_rows)
rawhash={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in(P/'raw_logs').rglob('*')if f.is_file()};(P/'audit/raw-manifest.json').write_text(json.dumps(rawhash,indent=2));print(json.dumps({'snapshots':len(rows),'manager_resets':len(resetrows),'committed_new_business_requests':len(checks),'VM_invokes_including_children':len(calls),'all_owned_node_processes_exited':True},indent=2))
