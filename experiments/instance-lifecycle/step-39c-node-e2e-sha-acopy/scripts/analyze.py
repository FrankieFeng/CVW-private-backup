from pathlib import Path
import json,csv,re,statistics as st,collections,itertools,math
from parity import check
P=Path(__file__).resolve().parents[1];D=P/'raw_logs'
def save(n,rows,fields=None):
 keys=fields or list(dict.fromkeys(k for r in rows for k in r))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def q(v,p):
 a=sorted(v);k=(len(a)-1)*p;i=int(k);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(k-i)
def inverse(v,p):return sorted(v)[max(0,math.ceil(p*len(v))-1)]
def ci(by):
 bs=list(by);v=[st.median([x for b in combo for x in by[b]])for combo in itertools.product(bs,repeat=len(bs))];return inverse(v,.025),inverse(v,.975)
resources=[];samples=[];tps=[];cold=[];stage=[];statechecks=[]
for f in sorted(D.glob('*-outcome.json')):
 x=json.loads(f.read_text());o=x.get('owner')or{};txt=(D/(x['label']+'-node.log')).read_text();ev=[json.loads(l[7:])for l in txt.splitlines()if l.startswith('STEP35 ')];last=[e for e in ev if e['event']=='cache_closed'];artifact=last[-1].get('artifact',{})if last else{};heaps=[e.get('go_heap',0)for e in ev]
 resources.append(dict(run=x['label'],phase='formal'if x['label'].startswith('formal-')else'smoke_or_seed',rss_peak_mib=x['peak_rss_kib']/1024,threads_peak=x['peak_threads'],go_heap_boundary_peak_bytes=max(heaps,default=0),stop_s=x['stop_s'],exit_code=x['systemd'].get('ExecMainStatus'),reason=x['reason'],pid_exited=x['pid_exited'],cgroup_empty=x['cgroup_empty'],stores_created=o.get('stores_created'),stores_closed=o.get('stores_closed'),instances_created=o.get('instances_created'),instances_closed=o.get('instances_closed'),managed_pending=o.get('managed_pending'),artifact_stop_entries=artifact.get('Entries'),artifact_stop_bytes=artifact.get('Bytes'),artifact_stop_closed=artifact.get('Closed')))
for f in sorted(D.glob('formal-*-case.json')):
 x=json.loads(f.read_text());assert x['passed']and x['phase']=='formal'and x['window']['planned']==10;label=x['label'];txt=(D/(label+'-node.log')).read_text();events=[json.loads(l[7:])for l in txt.splitlines()if l.startswith('STEP35 ')];traces=[json.loads(l[8:])for l in txt.splitlines()if l.startswith('STEP35C ')];rec=x['records'];assert len(rec)==10
 ids=set();window=x['window'];start,end=window['window_start_mono_ns'],window['window_end_mono_ns'];assert end>start;committed=0
 for item in rec:
  row=item['row'];r=row['response'];info=item['committed'];tx=r['tx_id'];assert tx not in ids;ids.add(tx)
  assert row['success']and r.get('code',0)==0 and(r.get('contract_result')or{}).get('code',0)==0
  assert info['transaction']['payload']['tx_id']==tx and info['block_height']==r['tx_block_height']and info['block_height']>0 and info['transaction']['result']['contract_result']==r['contract_result']
  assert start<=row['sdk_start_mono_ns']<row['sdk_end_mono_ns']<=end;committed+=1
  vm=[e for e in events if e['event']=='invoke_end'and e.get('tx_id')==tx];roots=[e for e in vm if e['depth']==0];children=[e for e in vm if e['depth']>0];assert len(roots)==1;root=roots[0];assert len(children)==(6 if x['case']=='exchange_buyNow'else 0)
  assert all(e['code']==0 and e['error']=='<nil>'for e in vm)
  outer=re.findall(r'REUSE_VM tx='+tx+r' .*?begin_ns=(\d+) end_ns=(\d+) code=(\d+) gas=(\d+) depth=(\d+)',txt);outer=[(int(a),int(b))for a,b,c,g,d in outer if int(d)==0];assert len(outer)==1;factory=(outer[0][1]-outer[0][0])/1e6;elapsed=row['elapsed_ns']/1e6
  z=dict(run=label,case=x['case'],group=x['group'],batch=x['batch'],slot=int(item['tag'].split('-')[-1]),tag=item['tag'],tx_id=tx,block_height=info['block_height'],sdk_start_mono_ns=row['sdk_start_mono_ns'],sdk_end_mono_ns=row['sdk_end_mono_ns'],sdk_start_wall_ns=row['sdk_start_wall_ns'],sdk_end_wall_ns=row['sdk_end_wall_ns'],e2e_ms=elapsed,success=True,committed=True,failed=False,timeout=False,gas=r['contract_result'].get('gas_used',0),vm_factory_ms=factory,vm_owner_ms=root['invoke_ns']/1e6,root_executions=len(roots),child_executions=len(children),newinstance_ms=root['newinstance_ns']/1e6,copy_ms=root.get('copy_ns',0)/1e6,start_ms=root['start_ns']/1e6,callmethod_ms=root['callmethod_ns']/1e6,close_ms=root['close_ns']/1e6,e2e_minus_factory_ms=elapsed-factory,window_start_mono_ns=start,window_end_mono_ns=end,raw_case=str(f.relative_to(P)))
  samples.append(z)
  same=[e for e in traces if e.get('tx_id')==tx]
  def stamp(name,ee):
   a=[v['mono_ns']for v in ee if v['event']==name];return a[0]if len(a)==1 else None
  a=stamp('rpc_tx_begin',same);b=stamp('rpc_tx_end',same);pb=stamp('put_begin',[e for e in traces if e.get('height')==info['block_height']]);pe=stamp('put_end',[e for e in traces if e.get('height')==info['block_height']]);vb=[e for e in same if e['event']=='vm_invoke_begin'and e.get('depth')==0];ve=[e for e in same if e['event']=='vm_invoke_end'and e.get('depth')==0]
  stage.append(dict(run=label,case=x['case'],group=x['group'],batch=x['batch'],slot=z['slot'],tx_id=tx,block_height=info['block_height'],rpc_ms=(b-a)/1e6 if a is not None and b is not None else'not_matched',put_ms=(pe-pb)/1e6 if pb is not None and pe is not None else'not_matched',rpc_begin_to_vm_begin_ms=(vb[0]['mono_ns']-a)/1e6 if len(vb)==1 and a is not None else'not_matched',vm_end_to_put_begin_ms=(pb-ve[0]['mono_ns'])/1e6 if len(ve)==1 and pb is not None else'not_matched',put_end_to_rpc_end_ms=(b-pe)/1e6 if b is not None and pe is not None else'not_matched',put_end_not_after_rpc_end=pe<=b if pe is not None and b is not None else'not_matched'))
 duration=(end-start)/1e9
 tps.append(dict(run=label,case=x['case'],group=x['group'],batch=x['batch'],planned=10,sent=window['attempted'],successful_responses=window['successful_responses'],unique_confirmed_commits=committed,failures=0,timeouts=0,window_start_mono_ns=start,window_end_mono_ns=end,window_seconds=duration,submission_tps=committed/duration,client_completion_tps=window['successful_responses']/duration,vm_log_equivalent_tps=len(rec)/sum(r['vm_factory_ms']/1000 for r in samples if r['run']==label),success_rate=committed/window['attempted'],owner_accepted=x['owner_after']['accepted'],owner_limit=x['owner_after']['limit'],artifact_entries=x['artifact_after']['entries'],artifact_bytes=x['artifact_after']['bytes'],artifact_hits=x['artifact_after']['hits']))
 for phase,key in [('cold','cold'),('warmup','warmup')]:
  row=x[key]['rows'][0];cold.append(dict(run=label,case=x['case'],group=x['group'],batch=x['batch'],phase=phase,success=row['success'],elapsed_ms=row['elapsed_ns']/1e6,op=row['input']['Op'],note='query-only; not formal confirmed transaction'))
 statechecks.append(dict(run=label,initial_state_verified=True,final_state_verified=True,committed_results_equal=True,all_calls_success=True,all_child_gas=[(e['contract'],e['method'],e['gas'])for e in events if e['event']=='invoke_end'and e.get('depth',0)>0]))
assert len(samples)==360 and len(tps)==36
save('E2E_RESULTS.csv',samples);save('TPS_RESULTS.csv',tps);save('RESOURCE_SUMMARY.csv',resources);save('COLD_WARM.csv',cold);save('NODE_STAGES.csv',stage);save('STATE_CHECKS.csv',statechecks)
summary=[];effects=[];tpse=[];orders=[]
metrics=['e2e_ms','vm_factory_ms','e2e_minus_factory_ms','vm_owner_ms','newinstance_ms','copy_ms','start_ms','callmethod_ms','close_ms']
for case in ['compute_hashCal','bigInput_inputSize','exchange_buyNow']:
 d={g:{(r['batch'],r['slot']):r for r in samples if r['case']==case and r['group']==g}for g in ['E0','E1','E2','E3']}
 for g,a in d.items():
  tv=[r for r in tps if r['case']==case and r['group']==g]
  for m in metrics:
   v=[r[m]for r in a.values()];summary.append(dict(case=case,group=g,metric=m,N=len(v),independent_batches=3,mean=st.mean(v),p50=st.median(v),p95=q(v,.95),p99='insufficient_sample_size',successful_commits=sum(z['unique_confirmed_commits']for z in tv),pooled_tps=sum(z['unique_confirmed_commits']for z in tv)/sum(z['window_seconds']for z in tv),tps_batch1=next(z['submission_tps']for z in tv if z['batch']==1),tps_batch2=next(z['submission_tps']for z in tv if z['batch']==2),tps_batch3=next(z['submission_tps']for z in tv if z['batch']==3)))
 for left,right in [('E0','E1'),('E1','E2'),('E2','E3'),('E0','E3')]:
  for m in metrics:
   by=collections.defaultdict(list);percent=[]
   for k in sorted(d[left]):by[k[0]].append(d[left][k][m]-d[right][k][m]);percent.append((d[left][k][m]-d[right][k][m])/d[left][k][m]*100 if d[left][k][m]!=0 else float('nan'))
   vals=[x for v in by.values()for x in v];lo,hi=ci(by);effects.append(dict(case=case,left=left,right=right,metric=m,N=len(vals),independent_batches=3,paired_saving_median=st.median(vals),paired_saving_mean=st.mean(vals),paired_reduction_percent_median=st.median(percent),ci95_low=lo,ci95_high=hi,positive_fraction=sum(x>0 for x in vals)/len(vals),batch1=st.median(by[1]),batch2=st.median(by[2]),batch3=st.median(by[3]),ci_method='27 batch-cluster draws; retain10serial pairs per batch; inverse empiricalCDF'))
   for b in [1,2,3]:
    order=json.loads((P/'audit'/f'order-{case}-b{b}.json').read_text());orders.append(dict(case=case,left=left,right=right,batch=b,metric=m,N=10,saving_median=st.median(by[b]),order='>'.join(order),right_after_left=order.index(right)>order.index(left)))
  a={r['batch']:r for r in tps if r['case']==case and r['group']==left};b={r['batch']:r for r in tps if r['case']==case and r['group']==right};lt=sum(v['unique_confirmed_commits']for v in a.values())/sum(v['window_seconds']for v in a.values());rt=sum(v['unique_confirmed_commits']for v in b.values())/sum(v['window_seconds']for v in b.values());draw=[]
  for combo in itertools.product([1,2,3],repeat=3):
   aa=sum(a[k]['unique_confirmed_commits']for k in combo)/sum(a[k]['window_seconds']for k in combo);bb=sum(b[k]['unique_confirmed_commits']for k in combo)/sum(b[k]['window_seconds']for k in combo);draw.append((bb/aa-1)*100)
  tpse.append(dict(case=case,left=left,right=right,independent_batches=3,left_tps=lt,right_tps=rt,absolute_tps_change=rt-lt,pooled_increase_percent=(rt/lt-1)*100,ci95_low_percent=inverse(draw,.025),ci95_high_percent=inverse(draw,.975),batch1_percent=(b[1]['submission_tps']/a[1]['submission_tps']-1)*100,batch2_percent=(b[2]['submission_tps']/a[2]['submission_tps']-1)*100,batch3_percent=(b[3]['submission_tps']/a[3]['submission_tps']-1)*100))
 for b in [1,2,3]:assert check([D/f'formal-{case}-b{b}-{g}-case.json'for g in ['E0','E1','E2','E3']],f'formal-{case}-b{b}')['passed']
save('SUMMARY.csv',summary);save('PAIRED_EFFECTS.csv',effects);save('TPS_EFFECTS.csv',tpse);save('ORDER_EFFECTS.csv',orders)
for r in effects:
 if r['metric']=='e2e_ms':print(r['case'],r['left']+'→'+r['right'],round(r['paired_saving_median'],3),[round(r[k],3)for k in ['ci95_low','ci95_high','batch1','batch2','batch3']])
# Post-hoc slow samples are diagnostic only, never excluded from main statistics.
slow=[];overlap=[]
for run in sorted({r['run']for r in samples}):
 txt=(D/(run+'-node.log')).read_text();ev=[json.loads(l[8:])for l in txt.splitlines()if l.startswith('STEP35C ')];states=[e for e in ev if e['event']=='proposer_ready'];go=[json.loads(l[7:])for l in txt.splitlines()if l.startswith('STEP35 ')];rootstarts={e['tx_id']:e for e in go if e['event']=='invoke_begin'and e.get('depth')==0}
 for r in [z for z in samples if z['run']==run]:
  tx=r['tx_id'];a=next(e['mono_ns']for e in ev if e.get('tx_id')==tx and e['event']=='rpc_tx_begin');b=next(e['mono_ns']for e in ev if e.get('tx_id')==tx and e['event']=='vm_invoke_begin'and e.get('depth')==0)
  prev=[e for e in states if e['mono_ns']<=a];state=prev[-1]['ready']if prev else None;last=a;false=0
  for e in [s for s in states if a<s['mono_ns']<b]:
   if state is False:false+=e['mono_ns']-last
   last=e['mono_ns'];state=e['ready']
  if state is False:false+=b-last
  z=dict(run=run,case=r['case'],group=r['group'],batch=r['batch'],slot=r['slot'],tx_id=tx,e2e_ms=r['e2e_ms'],factory_ms=r['vm_factory_ms'],rpc_to_vm_ms=(b-a)/1e6,proposer_false_overlap_ms=false/1e6,root_begin_go_heap_bytes=rootstarts[tx]['go_heap'],kept_in_main=True);overlap.append(z)
  if r['e2e_ms']>1000:slow.append(z)
assert len(slow)==24 and all(r['slot']==4 for r in slow)
save('SLOW_SAMPLES.csv',slow);save('PROPOSER_OVERLAP.csv',overlap)
batchsummary=[];p95effects=[]
for run in sorted({r['run']for r in samples}):
 rr=[r for r in samples if r['run']==run];tt=next(t for t in tps if t['run']==run);v=[r['e2e_ms']for r in rr];batchsummary.append(dict(run=run,case=tt['case'],group=tt['group'],batch=tt['batch'],N=len(rr),mean_ms=st.mean(v),p50_ms=st.median(v),p95_ms=q(v,.95),p99='insufficient_sample_size',successful_commits=tt['unique_confirmed_commits'],window_seconds=tt['window_seconds'],tps=tt['submission_tps'],vm_factory_p50_ms=st.median([r['vm_factory_ms']for r in rr])))
for case in ['compute_hashCal','bigInput_inputSize','exchange_buyNow']:
 d={g:{b:[r['e2e_ms']for r in samples if r['case']==case and r['group']==g and r['batch']==b]for b in [1,2,3]}for g in ['E0','E1','E2','E3']}
 for left,right in [('E0','E1'),('E1','E2'),('E2','E3'),('E0','E3')]:
  draws=[]
  for combo in itertools.product([1,2,3],repeat=3):draws.append(q([v for b in combo for v in d[left][b]],.95)-q([v for b in combo for v in d[right][b]],.95))
  aa=q([v for b in [1,2,3]for v in d[left][b]],.95);bb=q([v for b in [1,2,3]for v in d[right][b]],.95);p95effects.append(dict(case=case,left=left,right=right,left_p95_ms=aa,right_p95_ms=bb,p95_distribution_difference_ms=aa-bb,relative_reduction_percent=(aa-bb)/aa*100,ci95_low=inverse(draws,.025),ci95_high=inverse(draws,.975),note='paired batch resampling of marginal P95; not median individual latency difference'))
save('BATCH_SUMMARY.csv',batchsummary);save('P95_EFFECTS.csv',p95effects)
for t in tps:
 rs=[r for r in samples if r['run']==t['run']];t['window_start_wall_ns']=rs[0]['sdk_start_wall_ns'];t['window_end_wall_ns']=rs[-1]['sdk_end_wall_ns']
save('TPS_RESULTS.csv',tps)
