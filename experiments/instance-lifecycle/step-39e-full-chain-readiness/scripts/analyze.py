from pathlib import Path
import json,csv,statistics as st,re,itertools,math,hashlib,base64
P=Path(__file__).resolve().parents[1];D=P/'raw_logs'
def save(n,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def q(v,p):
 a=sorted(v);k=(len(a)-1)*p;i=int(k);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(k-i)
def ci(by,stat=st.median):
 xs=[stat([x for b in bs for x in by[b]])for bs in itertools.product(sorted(by),repeat=len(by))];xs.sort();return xs[max(0,math.ceil(len(xs)*.025)-1)],xs[max(0,math.ceil(len(xs)*.975)-1)]
variants=json.loads((P/'inputs/variants.json').read_text());results=[];windows=[];resources=[];gates=[];startup=[];parity=[]
for f in sorted(D.glob('*-case.json')):
 x=json.loads(f.read_text());assert x['passed'];label=x['label'];log=(D/(label+'-node.log')).read_text();ev=[json.loads(l[8:])for l in log.splitlines()if l.startswith('STEP35C ')];stage=[json.loads(l[7:])for l in log.splitlines()if l.startswith('STEP35 ')];rd=[json.loads(l[8:])for l in log.splitlines()if l.startswith('STEP39E ')]
 for name in ['preflight','full_gate','before_window_gate','after_window_gate']:
  z=x[name]['final'];s=z['state'];assert z['passed']and s['ready']and s['completed']==s['notified']==s['taken']and not s['consumer_active']and not s['closing']and s['run']==label and len(z['fence_ids'])==2
  gates.append(dict(run=label,case=x['case'],group=x['group'],phase=x['phase'],boundary=name,**{k:v for k,v in s.items()if k not in ['stages_ns','run']},fence_ids=z['fence_ids']))
 probe=x['probe']['rows'][0];pc=x['probe_committed'];assert probe['success']and pc['block_height']==probe['response']['tx_block_height']and x['full_gate']['final']['state']['last_completed_height']>=pc['block_height'];cold=[e for e in stage if e['event']=='module_prepared'];ss=x['preflight']['final']['state'];startup.append(dict(run=label,case=x['case'],group=x['group'],phase=x['phase'],batch=x['batch'],harness_launch_to_component_gate_ms=x['preflight']['launch_to_gate_ns']/1e6,node_chain_start_to_chain_started_ms=ss['stages_ns']['chain_started']/1e6,node_chain_start_to_business_gate_ms=x['full_gate']['final']['state']['since_chain_start_ns']/1e6,node_chain_start_to_registry_return_ms=ss['stages_ns']['registry_returned']/1e6,cold_first_business_sdk_ms=probe['elapsed_ns']/1e6,cold_module_template_prepare_ms=cold[0]['prepare_ns']/1e6 if cold else'not_recorded',warmup_query_sdk_ms=x['warmup']['rows'][0]['elapsed_ns']/1e6,note='startup, cold submitted probe and warmup all excluded from steady window; not discarded'))
 assert x['window']['attempted']==6 and x['window']['successful_responses']==6
 for pos,it in enumerate(x['records'],1):
  row=it['row'];resp=row['response'];tx=resp['tx_id'];info=it['committed'];assert info['transaction']['payload']['tx_id']==tx and info['transaction']['result']['contract_result']==resp['contract_result']and info['block_height']==resp['tx_block_height']>0;assert not(info.get('rw_set')or{}).get('tx_writes');assert resp['contract_result']['gas_used']==(120127 if x['case']=='compute_hashCal'else 52562)
  same=[e for e in ev if e.get('tx_id')==tx];a=next(e for e in same if e['event']=='rpc_tx_begin');v=next(e for e in same if e['event']=='vm_invoke_begin'and e['depth']==0);end=next(e for e in same if e['event']=='rpc_tx_end');pe=next(e for e in ev if e['event']=='put_end'and e['height']==info['block_height']);assert pe['mono_ns']<=end['mono_ns'];root=[e for e in stage if e['event']=='invoke_end'and e.get('tx_id')==tx];assert len(root)==1 and root[0]['code']==0;root=root[0];variant=variants[('compute' if x['case']=='compute_hashCal' else 'bigInput')+('-G2' if x['group']=='E3' else '-G0')];assert all(e['source_sha']==variant['sha'] for e in stage if e['event']=='module_prepared');assert (root.get('copy_ns',0)>0)==(x['group']=='E3');match=re.findall(r'REUSE_VM tx='+tx+r' .*?begin_ns=(\d+) end_ns=(\d+) code=(\d+) gas=(\d+) depth=0',log);assert len(match)==1;ns1,ns2,code,gas=map(int,match[0]);assert code==0
  r=dict(run=label,phase=x['phase'],case=x['case'],group=x['group'],batch=x['batch'],request_number=pos,tx_id=tx,block_height=info['block_height'],success=True,committed=True,gas=int(gas),wasm_sha256=variant['sha'],frozen_wasm_path=variant['path'],instance_id=root['instance_id'],store_id=root['store_id'],compile_store_id=root['compile_store_id'],e2e_ms=row['elapsed_ns']/1e6,sdk_start_mono_ns=row['sdk_start_mono_ns'],sdk_end_mono_ns=row['sdk_end_mono_ns'],sdk_start_wall_ns=row['sdk_start_wall_ns'],sdk_end_wall_ns=row['sdk_end_wall_ns'],rpc_begin_node_mono_ns=a['mono_ns'],vm_begin_node_mono_ns=v['mono_ns'],put_end_node_mono_ns=pe['mono_ns'],rpc_end_node_mono_ns=end['mono_ns'],rpc_to_vm_ms=(v['mono_ns']-a['mono_ns'])/1e6,factory_ms=(ns2-ns1)/1e6,owner_invoke_ms=root['invoke_ns']/1e6,newinstance_ms=root['newinstance_ns']/1e6,copy_ms=root.get('copy_ns',0)/1e6,start_ms=root['start_ns']/1e6,close_ms=root['close_ns']/1e6,slow_gt_1000ms=row['elapsed_ns']>1e9)
  assert not r['slow_gt_1000ms'];results.append(r)
 w=x['window'];rr=[r for r in results if r['run']==label];dur=w['window_ns']/1e9;assert w['window_ns']==w['window_end_mono_ns']-w['window_start_mono_ns'];assert all(w['window_start_mono_ns']<=r['sdk_start_mono_ns']<r['sdk_end_mono_ns']<=w['window_end_mono_ns']for r in rr);vals=[r['e2e_ms']for r in rr];windows.append(dict(run=label,phase=x['phase'],case=x['case'],group=x['group'],batch=x['batch'],N=6,mean_ms=st.mean(vals),p50_ms=st.median(vals),p95_ms=q(vals,.95),window_start_mono_ns=w['window_start_mono_ns'],window_end_mono_ns=w['window_end_mono_ns'],window_seconds=dur,confirmed=6,failures=0,timeouts=0,submit_tps=6/dur,rpc_to_vm_p50_ms=st.median(r['rpc_to_vm_ms']for r in rr),rpc_to_vm_max_ms=max(r['rpc_to_vm_ms']for r in rr),fifth_ms=rr[4]['e2e_ms'],height6_ms=next(r['e2e_ms']for r in rr if r['block_height']==6),owner_accepted=x['owner_after']['accepted'],owner_limit=x['owner_after']['limit'],artifact_entries=x['artifact_after']['entries'],artifact_bytes=x['artifact_after']['bytes']))
for f in sorted(D.glob('*-outcome.json')):
 x=json.loads(f.read_text());o=x['owner'];assert x['systemd']['ExecMainStatus']=='0'and not x['reason']and x['pid_exited']and x['cgroup_empty']and o['managed_pending']==0 and o['stores_created']==o['stores_closed']and o['instances_created']==o['instances_closed'];resources.append(dict(run=x['label'],rss_peak_mib=x['peak_rss_kib']/1024,threads_peak=x['peak_threads'],stop_seconds=x['stop_s'],stores_created=o['stores_created'],stores_closed=o['stores_closed'],instances_created=o['instances_created'],instances_closed=o['instances_closed'],managed_pending=0,exit_code=0,pid_exited=True,cgroup_empty=True))

# Independent expected-output check on ALL saved SDK business calls, including cold/warm/Reset/restart.
expected_checks=[]
for f in sorted(D.glob('*-client.jsonl')):
 for line in f.read_text().splitlines():
  obj=json.loads(line)
  for row in obj.get('rows',[]):
   inp=row['input']
   if inp['Op']not in ['invoke','query']or inp['Method']not in ['hashCal','inputSize']:continue
   cr=(row.get('response')or{}).get('contract_result')or{};actual=base64.b64decode(cr.get('result','')).decode();expected=('success hashCal '+hashlib.sha256(b'ChainMaker Performance Test').hexdigest())if inp['Method']=='hashCal'else str(len(inp['Params']['data'].encode()))
   assert row['success']and actual==expected and cr['gas_used']==(120127 if inp['Method']=='hashCal'else 52562),(f,inp['Tag'])
   expected_checks.append(dict(run=f.name,tag=inp['Tag'],phase=inp['Phase'],method=inp['Method'],expected=expected,actual=actual,gas=cr['gas_used'],passed=True))
(P/'evidence/expected-output-checks.json').write_text(json.dumps(expected_checks,indent=2))

assert len(results)==90 and sum(r['phase']=='formal'for r in results)==72
summary=[];paired=[]
for case in ['compute_hashCal','bigInput_inputSize']:
 d={g:{(r['batch'],r['request_number']):r for r in results if r['phase']=='formal'and r['case']==case and r['group']==g}for g in ['E0','E3']}
 for g,a in d.items():
  for metric in ['e2e_ms','rpc_to_vm_ms','factory_ms']:
   vals=[r[metric]for r in a.values()];ws=[w for w in windows if w['phase']=='formal'and w['case']==case and w['group']==g];summary.append(dict(case=case,group=g,metric=metric,N=len(vals),independent_batches=3,mean=st.mean(vals),p50=st.median(vals),p95=q(vals,.95),p99='insufficient_samples',pooled_submit_tps=18/sum(w['window_seconds']for w in ws),batch1_tps=next(w['submit_tps']for w in ws if w['batch']==1),batch2_tps=next(w['submit_tps']for w in ws if w['batch']==2),batch3_tps=next(w['submit_tps']for w in ws if w['batch']==3)))
 for metric in ['e2e_ms','rpc_to_vm_ms','factory_ms']:
  by={b:[d['E0'][(b,i)][metric]-d['E3'][(b,i)][metric]for i in range(1,7)]for b in [1,2,3]};vals=sum(by.values(),[]);lo,hi=ci(by);paired.append(dict(case=case,metric=metric,N=18,independent_batches=3,saving_median=st.median(vals),saving_mean=st.mean(vals),ci95_low=lo,ci95_high=hi,positive_fraction=sum(v>0 for v in vals)/len(vals),paired_percent_median=st.median((d['E0'][key][metric]-d['E3'][key][metric])/d['E0'][key][metric]*100 for key in d['E0']),batch1=st.median(by[1]),batch2=st.median(by[2]),batch3=st.median(by[3]),ci_method='27 exhaustive batch-cluster draws preserving6 serialpairs'))
 for b in [1,2,3]:
  xx=[json.loads((D/f'formal-{case}-b{b}-{g}-case.json').read_text())for g in ['E0','E3']]
  def signature(x):return[(it['row']['response']['tx_id'],it['row']['response']['contract_result'],sorted((it['committed'].get('rw_set')or{}).get('tx_reads',[]),key=lambda x:json.dumps(x,sort_keys=True)),sorted((it['committed'].get('rw_set')or{}).get('tx_writes',[]),key=lambda x:json.dumps(x,sort_keys=True)))for it in x['records']]
  assert signature(xx[0])==signature(xx[1]);parity.append(dict(case=case,batch=b,passed=True,exact_Gas_result_events_RWset=True))
save('RESULTS.csv',results);save('WINDOWS.csv',windows);save('SUMMARY.csv',summary);save('PAIRED_EFFECTS.csv',paired);save('STARTUP_COLD.csv',startup);save('GATE_EVIDENCE.csv',gates);save('RESOURCES.csv',resources);(P/'evidence/parity.json').write_text(json.dumps(parity,indent=2))
print('replayed',len(results),'targets,72formal,18validation; exactparity6pairedbatches; allgateandPutBlockchecks passed')
for r in summary:
 if r['metric']=='e2e_ms':print(r)
for r in paired:
 if r['metric']=='e2e_ms':print(r)
