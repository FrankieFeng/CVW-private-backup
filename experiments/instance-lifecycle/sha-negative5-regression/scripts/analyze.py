"""Read saved SDK/VM records. No node execution; no rewriting raw_logs."""
from pathlib import Path
import json,csv,re,statistics as st,itertools,math,base64
from correctness import signature,check_target
P=Path(__file__).resolve().parents[1];D=P/'raw_logs';METHODS=['identity_address','identity_callerAddress','erc721_balanceOf','erc721_tokenLatestTxInfo','raffle_raffle'];GROUPS=['G0','G1','G2','G3','G4'];CTL=json.loads((P/'inputs/variants-control.json').read_text());VS=json.loads((P/'inputs/variants.json').read_text());CF=json.loads((P/'inputs/cases.json').read_text())
def save(name,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with(P/name).open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def quant(v,p):
 a=sorted(v);x=(len(a)-1)*p;i=int(x);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(x-i)
def ci3(values):
 a=sorted(st.median(xs)for xs in itertools.product(values,repeat=3));return a[max(0,math.ceil(.025*len(a))-1)],a[max(0,math.ceil(.975*len(a))-1)]
rows=[];windows=[];resource=[];children=[];checks=[];startup=[]
for f in sorted(D.glob('*-case.json')):
 x=json.loads(f.read_text());assert x['passed'];label=x['label'];control=CTL[x['group']];variant=VS[CF[x['case']]['contract']+('-G2'if control['A']else'-G0')];log=(D/(label+'-node.log')).read_text();events=[json.loads(l[7:])for l in log.splitlines()if l.startswith('STEP35 ')];stages=[json.loads(l[8:])for l in log.splitlines()if l.startswith('STEP35C ')];prepared=[e for e in events if e['event']=='module_prepared'];assert prepared and all(e['source_sha']==variant['sha']for e in prepared)
 for gate in ['preflight','post_probe_gate','before_window_gate','after_window_gate']:
  a=x[gate]['final'];s=a['state'];assert a['passed']and s['run']==label and s['ready']and s['notified']==s['completed']and not s['consumer_active']and len(a['fence_ids'])==2
 assert x['after_window_gate']['final']['state']['last_completed_height']>=x['records'][-1]['committed']['block_height'];assert x['owner_after']['accepted']==len(x['records'])+2 and x['owner_after']['limit']==32
 if control['sha']:assert x['artifact_after']['entries']==1 and x['artifact_after']['hits']>x['artifact_before']['hits']
 else:assert x['artifact_after']['entries']==0
 assert x['artifact_after']['max_entries']==8 and x['artifact_after']['max_bytes']==64*1024*1024
 for pos,it in enumerate(x['records'],1):
  row=it['row'];resp=row['response'];tx=resp['tx_id'];comm=it['committed'];assert row['success']and comm['transaction']['payload']['tx_id']==tx and comm['transaction']['result']['contract_result']==resp['contract_result']and comm['block_height']==resp['tx_block_height']>0;check_target(x,row,pos-1)
  ee=[e for e in events if e['event']=='invoke_end'and e.get('tx_id')==tx];root=[e for e in ee if e['depth']==0];assert len(root)==1;root=root[0];sub=[e for e in ee if e['depth']>0];assert len(sub)==(1 if x['case']=='identity_callerAddress'else 0);assert all(e['code']==0 and e['error']=='<nil>'for e in ee);assert (root.get('copy_ns',0)>0)==control['copy']
  for e in sub:assert e['store_id']!=root['store_id'];children.append(dict(run=label,case=x['case'],group=x['group'],batch=x['batch'],phase=x['phase'],tx_id=tx,method=e['method'],depth=e['depth'],instance_id=e['instance_id'],store_id=e['store_id'],owner_invoke_ms=e['invoke_ns']/1e6,gas=e['gas']))
  ns=re.findall(r'REUSE_VM tx='+tx+r' .*?begin_ns=(\d+) end_ns=(\d+) code=(\d+) gas=(\d+) depth=0(?:\n|$)',log);assert len(ns)==1;start,end,code,gas=map(int,ns[0]);assert end>start and code==0 and gas==root['gas']
  # Original scheduler adds RWSet/event gas AFTER Runtime/Factory logging.
  rw=comm.get('rw_set')or{};rwbytes=sum(len(w['contract_name'].encode())+len(base64.b64decode(w['key']).replace(b'#',b''))+len(base64.b64decode(w.get('value','')))for w in rw.get('tx_reads',[])+rw.get('tx_writes',[])if w['contract_name']in ['identity','erc721','raffle'])
  eventbytes=sum(len(e['contract_name'].encode())+len(e['contract_version'].encode())+len(e['topic'].encode())+sum(len(s.encode())for s in e.get('event_data',[]))for e in resp['contract_result'].get('contract_event',[])if e['contract_name']in ['identity','erc721','raffle'])
  finalgas=resp['contract_result']['gas_used'];assert finalgas-gas==(rwbytes+9)//10+(eventbytes+9)//10,(label,tx,gas,finalgas,rwbytes,eventbytes)
  a=next(e for e in stages if e['event']=='rpc_tx_begin'and e.get('tx_id')==tx);v=next(e for e in stages if e['event']=='vm_invoke_begin'and e.get('tx_id')==tx and e['depth']==0);z=next(e for e in stages if e['event']=='rpc_tx_end'and e.get('tx_id')==tx);put=next(e for e in stages if e['event']=='put_end'and e['height']==comm['block_height']);assert put['mono_ns']<=z['mono_ns']
  r=dict(run=label,batch_id=x['batch'],phase=x['phase'],method=x['case'],variant=x['group'],request_number=pos,tx_id=tx,block_height=comm['block_height'],status='SUCCESS_CONFIRMED',sdk_e2e_ms=row['elapsed_ns']/1e6,factory_invoke_ms=(end-start)/1e6,owner_invoke_ms=root['invoke_ns']/1e6,newinstance_ms=root['newinstance_ns']/1e6,copy_restore_ms=root.get('copy_ns',0)/1e6,start_ms=root['start_ns']/1e6,callmethod_ms=root['callmethod_ns']/1e6,close_ms=root['close_ns']/1e6,rpc_to_owner_entry_ms=(v['mono_ns']-a['mono_ns'])/1e6,gas=finalgas,factory_logged_gas=gas,post_vm_rw_event_gas=finalgas-gas,root_executions=1,child_executions=len(sub),instance_id=root['instance_id'],store_id=root['store_id'],wasm_sha256=variant['sha'],sdk_start_mono_ns=row['sdk_start_mono_ns'],sdk_end_mono_ns=row['sdk_end_mono_ns'],sdk_start_wall_ns=row['sdk_start_wall_ns'],sdk_end_wall_ns=row['sdk_end_wall_ns'],rpc_begin_node_mono_ns=a['mono_ns'],put_end_node_mono_ns=put['mono_ns'],rpc_end_node_mono_ns=z['mono_ns'],raw_case=str(f.relative_to(P)));rows.append(r)
 n=len(x['records']);w=x['window'];assert n==w['attempted']==w['successful_responses'];duration=w['window_ns']/1e9;rr=[r for r in rows if r['run']==label];assert len({r['tx_id']for r in rr})==n;assert all(w['window_start_mono_ns']<=r['sdk_start_mono_ns']<r['sdk_end_mono_ns']<=w['window_end_mono_ns']for r in rr)
 wr=dict(run=label,phase=x['phase'],method=x['case'],variant=x['group'],batch_id=x['batch'],N=n,successful_commits=n,failures=0,timeouts=0,window_start_mono_ns=w['window_start_mono_ns'],window_end_mono_ns=w['window_end_mono_ns'],window_seconds=duration,submit_tps=n/duration)
 for metric in ['sdk_e2e_ms','factory_invoke_ms','owner_invoke_ms','newinstance_ms','copy_restore_ms','start_ms','callmethod_ms','close_ms','rpc_to_owner_entry_ms']:
  vals=[r[metric]for r in rr];wr[metric+'_mean']=st.mean(vals);wr[metric+'_p50']=st.median(vals);wr[metric+'_p95']=quant(vals,.95)
 windows.append(wr);startup.append(dict(run=label,method=x['case'],variant=x['group'],phase=x['phase'],launch_to_components_gate_ms=x['preflight']['launch_to_gate_ns']/1e6,cold_probe_sdk_ms=x['probe']['row']['elapsed_ns']/1e6,first_module_template_prepare_ms=prepared[0]['prepare_ns']/1e6,artifact_entries=x['artifact_after']['entries'],artifact_bytes=x['artifact_after']['bytes'],artifact_hits_before=x['artifact_before']['hits'],artifact_hits_after=x['artifact_after']['hits'],owner_accepted=x['owner_after']['accepted'],owner_limit=32))
for f in sorted(D.glob('*-outcome.json')):
 x=json.loads(f.read_text());o=x['owner'];assert x['systemd']['ExecMainStatus']=='0'and not x['reason']and x['pid_exited']and x['cgroup_empty']and o['managed_pending']==0 and o['stores_created']==o['stores_closed']and o['instances_created']==o['instances_closed'];resource.append(dict(run=x['label'],rss_peak_mib=x['peak_rss_kib']/1024,threads_peak=x['peak_threads'],stop_seconds=x['stop_s'],stores_created=o['stores_created'],stores_closed=o['stores_closed'],instances_created=o['instances_created'],instances_closed=o['instances_closed'],managed_pending=0,exit_code=0,go_heap_boundary_peak_bytes=max((json.loads(l[7:]).get('go_heap',0) for l in(D/(x['label']+'-node.log')).read_text().splitlines() if l.startswith('STEP35 ')),default=0)))
# Check corresponding batch fixtures exactly, never normalize tx IDs or history fields.
for phase,batches in [('pre',[0]),('formal',[1,2,3])]:
 for method in METHODS:
  for b in batches:
   xx=[json.loads((D/(f'pre-{method}-{g}-case.json'if phase=='pre'else f'formal-{method}-b{b}-{g}-case.json')).read_text())for g in GROUPS];sig=signature(xx[0]);assert all(signature(x)==sig for x in xx);checks.append(dict(phase=phase,method=method,batch=b,all_five_exact_equal=True))
assert len([r for r in rows if r['phase']in ['pre','formal']])==370 and sum(r['phase']=='formal'for r in rows)==345
summary=[];effects=[]
METRICS=['sdk_e2e_ms','factory_invoke_ms','owner_invoke_ms','newinstance_ms','copy_restore_ms','start_ms','callmethod_ms','close_ms']
for method in METHODS:
 for variant in GROUPS:
  rr=[r for r in rows if r['phase']=='formal'and r['method']==method and r['variant']==variant];ww=[r for r in windows if r['phase']=='formal'and r['method']==method and r['variant']==variant]
  for metric in METRICS:
   vals=[r[metric]for r in rr];summary.append(dict(method=method,variant=variant,metric=metric,N=len(vals),independent_batches=3,mean=st.mean(vals),p50=st.median(vals),p95=quant(vals,.95),p99='insufficient_samples',submit_tps=sum(w['N']for w in ww)/sum(w['window_seconds']for w in ww)))
 for left,right in [('G0','G1'),('G0','G2'),('G0','G3'),('G3','G4'),('G0','G4')]:
  for metric in METRICS:
   a={int(w['batch_id']):w[metric+'_mean']for w in windows if w['phase']=='formal'and w['method']==method and w['variant']==left};b={int(w['batch_id']):w[metric+'_mean']for w in windows if w['phase']=='formal'and w['method']==method and w['variant']==right};ds=[a[k]-b[k]for k in [1,2,3]];lo,hi=ci3(ds);la=next(s for s in summary if s['method']==method and s['variant']==left and s['metric']==metric);rb=next(s for s in summary if s['method']==method and s['variant']==right and s['metric']==metric)
   effects.append(dict(method=method,left=left,right=right,metric=metric,effect_unit='matched_batch_window_MEAN_difference',independent_pairs=3,left_transactions=la['N'],right_transactions=rb['N'],paired_saving_median=st.median(ds),paired_saving_mean=st.mean(ds),ci95_low=lo,ci95_high=hi,positive_fraction=sum(d>0 for d in ds)/3,batch1=ds[0],batch2=ds[1],batch3=ds[2],all_batches_positive=all(d>0 for d in ds),paired_reduction_percent_median=st.median((a[k]-b[k])/a[k]*100 if a[k]!=0 else float('nan')for k in [1,2,3]),p50_difference_ms=la['p50']-rb['p50'],ci_method='27 exhaustive matched-batch bootstrap draws; n=3; exploratory,no multiple-testing correction'))
save('E2E_RESULTS.csv',rows);save('VM_RESULTS.csv',[{k:r[k]for k in ['run','batch_id','phase','method','variant','request_number','tx_id','factory_invoke_ms','owner_invoke_ms','newinstance_ms','copy_restore_ms','start_ms','callmethod_ms','close_ms','gas','factory_logged_gas','post_vm_rw_event_gas','status','root_executions','child_executions','wasm_sha256']}for r in rows]);save('SUMMARY.csv',summary);save('WINDOWS.csv',windows);save('PAIRED_EFFECTS.csv',effects);save('RESOURCE_SUMMARY.csv',resource);save('STARTUP_CACHE.csv',startup);save('CHILD_CALLS.csv',children);(P/'audit/correctness-checks.json').write_text(json.dumps(checks,indent=2))
orderrows=[]
for e in effects:
 if e['metric']not in ['factory_invoke_ms','sdk_e2e_ms']:continue
 for b in [1,2,3]:
  order=json.loads((P/'audit'/f'order-{e["method"]}-b{b}.json').read_text());orderrows.append(dict(method=e['method'],left=e['left'],right=e['right'],metric=e['metric'],batch=b,saving=e['batch'+str(b)],order='>'.join(order),right_after_left=order.index(e['right'])>order.index(e['left'])))
save('ORDER_EFFECTS.csv',orderrows)
extra=[]
if (D/'ordercheck-raffle-G4-case.json').exists():
 a=json.loads((D/'ordercheck-raffle-G3-case.json').read_text());b=json.loads((D/'ordercheck-raffle-G4-case.json').read_text());assert signature(a)==signature(b)
 for metric in ['factory_invoke_ms','sdk_e2e_ms']:
  aa=[r[metric]for r in rows if r['phase']=='ordercheck'and r['variant']=='G3'];bb=[r[metric]for r in rows if r['phase']=='ordercheck'and r['variant']=='G4'];extra.append(dict(method='raffle_raffle',metric=metric,order='G3>G4',G3_mean=st.mean(aa),G4_mean=st.mean(bb),window_mean_saving=st.mean(aa)-st.mean(bb),independent_diagnostic_pairs=1,excluded_from_main_statistics=True))
 save('ORDER_CHECK.csv',extra)
print('COMPLETE',len(rows),'targets:345formal+25pre+supplementary;primary20fivegroupbatchparities;resources',len(resource))
for e in effects:
 if e['metric']=='sdk_e2e_ms'and(e['left'],e['right'])in[('G0','G3'),('G3','G4'),('G0','G4')]:print(e['method'],e['left']+'→'+e['right'],[round(e[k],3)for k in ['paired_saving_median','ci95_low','ci95_high','batch1','batch2','batch3']])
