from pathlib import Path
import json,csv,base64,hashlib,collections
P=Path(__file__).resolve().parents[1];GUEST={'compute','fact','identity','erc721','exchange'}
def write(name,rows):
 if not rows:return
 fields=list(dict.fromkeys(k for row in rows for k in row));
 with(P/name).open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def read(label):return [json.loads(x)for x in(P/'raw_logs'/f'{label}-client.jsonl').read_text().splitlines()]
def events(label):return [json.loads(x[7:])for x in(P/'raw_logs'/f'{label}-node.log').read_text().splitlines()if x.startswith('STEP35 ')]
def hashj(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def norm_rw(rw,kind):
 out=[]
 for x in rw.get(kind,[]):
  if x.get('contract_name')not in GUEST:continue
  x=dict(x);key=base64.b64decode(x.get('key','')).decode(errors='replace')
  if key.endswith('_latestTxInfo')and x.get('value'):
   v=json.loads(base64.b64decode(x['value']));v.pop('TxId',None);v.pop('BlockHeight',None);x['value']=v
  out.append(x)
 return sorted(out,key=lambda x:(x.get('contract_name',''),x.get('key','')))
def norm_events(evs):return [{k:v for k,v in e.items()if k!='tx_id'}for e in evs]
resource=[];inv=[];checks=[];rounds=[]
for f in sorted((P/'raw_logs').glob('*-outcome.json')):
 r=json.loads(f.read_text());lab=r.get('label',f.stem.replace('-outcome',''));owner=r.get('owner')or{};row={'label':lab,'reason':r.get('reason',''),'peak_rss_mib':r['peak_rss_kib']/1024 if 'peak_rss_kib'in r else'not_recorded','peak_threads':r.get('peak_threads','not_recorded'),'supervisor_stop_s':r.get('stop_s','not_recorded'),'pid_exited':r.get('pid_exited','not_recorded'),'cgroup_empty':r.get('cgroup_empty','not_recorded')};row.update({k:owner.get(k,'not_recorded')for k in ['stores_created','stores_closed','instances_created','instances_closed','managed_pending']})
 manager_log=P/'raw_logs'/f'{lab}.log'
 if manager_log.exists():
  ms=[json.loads(x[8:])for x in manager_log.read_text().splitlines()if x.startswith('STEP21C ')and 'owner_closed'in x]
  if ms:row.update({k:ms[-1].get(k,'not_recorded')for k in ['stores_created','stores_closed','instances_created','instances_closed','managed_pending']})
 log=P/'raw_logs'/f'{lab}-node.log'
 if log.exists():
  es=events(lab);ends=[x for x in es if x['event']=='invoke_end'];row['vm_depth0_invokes']=sum(x.get('depth')==0 for x in ends);row['vm_depth_positive_invokes']=sum(x.get('depth',0)>0 for x in ends);row['module_prepares']=sum(x['event']=='module_prepared'for x in es);row['module_hits']=sum(x['event']=='module_hit'for x in es);st=[x for x in es if x['event']=='stop_finished'];row['StopVM_ms']=st[-1]['stop_ns']/1e6 if st else'not_recorded'
  inv.extend(dict(process=lab,**x)for x in ends)
  for e in ends:checks.append({'scope':lab,'check':'runtime_store_differs_from_compile_store','contract':e['contract'],'instance_id':e['instance_id'],'result':e.get('store_id')!=e.get('compile_store_id')if e.get('store_id')else'not_created'})
  if 'six-waves'in lab:
   for i,x in enumerate(ends):
    if x.get('depth')==0:rounds.append({'ordinal':i,'contract':x['contract'],'method':x['method'],'go_heap_mib':x['go_heap']/1024**2,'go_num_gc':x.get('go_num_gc'),'managed_pending':x['managed_pending'],'runtime_stores_outstanding':x['stores_created']-x['stores_closed'],'runtime_instances_outstanding':x['instances_created']-x['instances_closed']})
 resource.append(row)
write('RESOURCE_SUMMARY.csv',resource);write('INVOCATIONS.csv',inv);write('RESOURCE_BOUNDARIES.csv',rounds)
a={x['input']['Tag']:x for x in read('node-small-baseline')};b={x['input']['Tag']:x for x in read('node-small-copy')};parity=[];ledgers=[{},{}]
for tag in a:
 if tag.endswith('-committed'):
  ra=a[tag]['result']['transaction']['rw_set'];rb=b[tag]['result']['transaction']['rw_set'];reads=norm_rw(ra,'tx_reads')==norm_rw(rb,'tx_reads');writes=norm_rw(ra,'tx_writes')==norm_rw(rb,'tx_writes');parity.append({'tag':tag,'type':'committed_rwset','reads_equal_normalized':reads,'writes_equal_normalized':writes,'writes_n':len(ra.get('tx_writes',[]))});assert reads and writes,(tag,ra,rb)
  for ledger,rw in zip(ledgers,[ra,rb]):
   for v in norm_rw(rw,'tx_writes'):ledger[(v['contract_name'],v['key'])]=v.get('value','')
 elif a[tag]['input'].get('Op')in ['invoke','query']:
  ar=a[tag]['result']['response'];br=b[tag]['result']['response'];ac=ar.get('contract_result',{});bc=br.get('contract_result',{});row={'tag':tag,'type':'client_result','baseline_status':ar.get('code',0),'copy_status':br.get('code',0),'baseline_gas':ac.get('gas_used',0),'copy_gas':bc.get('gas_used',0),'result_equal':ac.get('result')==bc.get('result'),'contract_message_equal':ac.get('message','')==bc.get('message',''),'contract_code_equal':ac.get('code',0)==bc.get('code',0),'gas_equal':ac.get('gas_used')==bc.get('gas_used'),'events_equal_normalized':norm_events(ac.get('contract_event',[]))==norm_events(bc.get('contract_event',[]))};parity.append(row);assert row['gas_equal']and row['result_equal']and row['contract_message_equal']and row['contract_code_equal']and row['events_equal_normalized']and row['baseline_status']==row['copy_status'],row
assert ledgers[0]==ledgers[1]
parity.append({'tag':'final_business_ledger_replay','type':'derived_from_all_committed_write_sets','writes_equal_normalized':True,'business_keys':len(ledgers[0]),'hash':hashj(sorted((str(k),v)for k,v in ledgers[0].items()))})
write('COPY_PARITY.csv',parity)
expected=[('identity','addWriteList'),('identity','isApprovedUser'),('identity','isApprovedUser'),('erc721','mint'),('erc721','setApprovalForAll2'),('erc721','transferFrom')]
for lab in ['node-small-baseline','node-small-copy','node-small-restart-converge','node-small-six-waves']:
 es=events(lab);starts=[x for x in es if x['event']=='invoke_begin'];ends=[x for x in es if x['event']=='invoke_end'];roots=[x for x in ends if x.get('contract')=='exchange'and x.get('method')=='buyNow'and x.get('depth')==0 and x['code']==0]
 for root in roots:
  children=[x for x in starts if x['tx_id']==root['tx_id']and x['depth']==1];got=[(x['contract'],x['method'])for x in children];assert got==expected,(lab,got);checks.append({'scope':lab,'check':'real_six_children','tx_id':root['tx_id'],'result':True,'child_count':len(children)})
 for x in read(lab):
  if x['input']['Tag']=='duplicate-buyNow-committed':assert len(x['result']['transaction']['rw_set'].get('tx_writes',[]))==0;checks.append({'scope':lab,'check':'failed_duplicate_committed_zero_writes','result':True})
write('CORRECTNESS_CHECKS.csv',checks)
# Exact original raw files remain untouched; hashed manifest supports auditing.
files={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in(P/'raw_logs').rglob('*')if f.is_file()};(P/'audit/raw_manifest.json').write_text(json.dumps(files,indent=2));print(json.dumps({'resource_processes':len(resource),'node_invokes':len(inv),'copy_parity_rows':len(parity),'successful_buyNow_roots':sum(x['check']=='real_six_children'for x in checks),'business_ledger_equal':True},indent=2))
