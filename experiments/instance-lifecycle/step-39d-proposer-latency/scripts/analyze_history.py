from pathlib import Path
import json,csv,statistics as st,hashlib,collections
P=Path(__file__).resolve().parents[1];C=P.parent/'step-39c-node-e2e-sha-acopy';D=C/'raw_logs'
def load(n):return list(csv.DictReader((C/n).open()))
def save(n,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def q(xs,p):
 a=sorted(xs);x=(len(a)-1)*p;i=int(x);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(x-i)
alltx=load('E2E_RESULTS.csv');out=[];stateevents=[];digests=[];window=[];slotstats=[];strata=[]
for label in sorted({r['run']for r in alltx}):
 raw=D/(label+'-node.log');digests.append(dict(path=str(raw),sha256=hashlib.sha256(raw.read_bytes()).hexdigest()));ev=[json.loads(l[8:])for l in raw.read_text().splitlines()if l.startswith('STEP35C ')];ev.sort(key=lambda e:(e['mono_ns'],e['seq']));first=next(e for e in ev if e['event']=='proposer_ready'and e['ready']);states=[e for e in ev if e['event']=='proposer_ready'];puts=[e for e in ev if e['event']=='put_end'];rows=sorted([r for r in alltx if r['run']==label],key=lambda r:int(r['slot']))
 for e in states:stateevents.append(dict(run=label,**e,since_first_ready_ms=(e['mono_ns']-first['mono_ns'])/1e6))
 for r in rows:
  same=[e for e in ev if e.get('tx_id')==r['tx_id']];get=lambda name:next(e for e in same if e['event']==name and (not name.startswith('vm_invoke')or e.get('depth')==0));a=get('rpc_tx_begin');b=get('vm_invoke_begin');v=get('vm_invoke_end');z=get('rpc_tx_end');pb=next(e for e in ev if e['event']=='put_begin'and e['height']==int(r['block_height']));pe=next(e for e in puts if e['height']==int(r['block_height']));prevput=[e for e in puts if e['mono_ns']<pb['mono_ns']];pp=prevput[-1]if prevput else None
  pre=[e for e in states if e['mono_ns']<=a['mono_ns']];state=pre[-1]['ready']if pre else None;previous=pre[-1]if pre else None;after=[e for e in states if a['mono_ns']<e['mono_ns']<=b['mono_ns']];cursor=a['mono_ns'];false=0
  for e in after:
   if state is False:false+=e['mono_ns']-cursor
   state=e['ready'];cursor=e['mono_ns']
  if state is False:false+=b['mono_ns']-cursor
  recovery=next((e for e in after if e['ready']),None)
  e2e=float(r['e2e_ms']);row=dict(run=label,case=r['case'],group=r['group'],batch=int(r['batch']),request_number=int(r['slot'])+1,tx_id=r['tx_id'],block_height=int(r['block_height']),sdk_start_wall_ns=int(r['sdk_start_wall_ns']),sdk_end_wall_ns=int(r['sdk_end_wall_ns']),sdk_start_client_mono_ns=int(r['sdk_start_mono_ns']),sdk_end_client_mono_ns=int(r['sdk_end_mono_ns']),rpc_begin_node_mono_ns=a['mono_ns'],vm_begin_node_mono_ns=b['mono_ns'],vm_end_node_mono_ns=v['mono_ns'],put_begin_node_mono_ns=pb['mono_ns'],put_end_node_mono_ns=pe['mono_ns'],rpc_end_node_mono_ns=z['mono_ns'],rpc_begin_wall_ns=a['wall_ns'],vm_begin_wall_ns=b['wall_ns'],put_end_wall_ns=pe['wall_ns'],rpc_end_wall_ns=z['wall_ns'],e2e_ms=e2e,factory_ms=float(r['vm_factory_ms']),owner_invoke_ms=float(r['vm_owner_ms']),rpc_to_vm_ms=(b['mono_ns']-a['mono_ns'])/1e6,vm_end_to_put_begin_ms=(pb['mono_ns']-v['mono_ns'])/1e6,put_ms=(pe['mono_ns']-pb['mono_ns'])/1e6,put_end_to_rpc_end_ms=(z['mono_ns']-pe['mono_ns'])/1e6,previous_committed_height=pp['height']if pp else'not_recorded_in_process',put_end_interval_ms=(pe['mono_ns']-pp['mono_ns'])/1e6 if pp else'not_recorded',rpc_since_first_ready_ms=(a['mono_ns']-first['mono_ns'])/1e6,vm_since_first_ready_ms=(b['mono_ns']-first['mono_ns'])/1e6,ready_at_rpc=pre[-1]['ready']if pre else'not_recorded',last_ready_change_node_mono_ns=previous['mono_ns']if previous else'not_recorded',first_ready_recovery_node_mono_ns=recovery['mono_ns']if recovery else'no_true_between_rpc_and_vm',ready_recovery_since_first_ready_ms=(recovery['mono_ns']-first['mono_ns'])/1e6 if recovery else'no_true_between_rpc_and_vm',ready_false_overlap_ms=false/1e6,slow_gt_1000ms=e2e>1000,txpool_inventory='not_recorded',tbft_round='not_recorded',raw_node_log=str(raw),raw_case=str(D/(label+'-case.json')))
  out.append(row)
 t=next(t for t in load('TPS_RESULTS.csv')if t['run']==label);rr=[r for r in out if r['run']==label];slow=[r for r in rr if r['slow_gt_1000ms']];dur=float(t['window_seconds']);values=[r['e2e_ms']for r in rr];window.append(dict(run=label,case=rows[0]['case'],group=rows[0]['group'],batch=rows[0]['batch'],N=len(rr),p50_ms=st.median(values),p95_ms=q(values,.95),mean_ms=st.mean(values),successfully_committed=int(t['unique_confirmed_commits']),failures=t['failures'],timeouts=t['timeouts'],actual_window_seconds=dur,actual_submit_tps=float(t['submission_tps']),slow_N=len(slow),slow_sdk_seconds=sum(r['e2e_ms']for r in slow)/1000,slow_sdk_fraction_of_actual_window=sum(r['e2e_ms']for r in slow)/dur/1000,slow_pre_vm_seconds=sum(r['rpc_to_vm_ms']for r in slow)/1000,slow_pre_vm_fraction_of_actual_window=sum(r['rpc_to_vm_ms']for r in slow)/dur/1000,slow_false_overlap_seconds=sum(r['ready_false_overlap_ms']for r in slow)/1000,intercall_bookkeeping_seconds=dur-sum(values)/1000))
for case in sorted({r['case']for r in out}):
 for pos in range(1,11):
  rr=[r for r in out if r['case']==case and r['request_number']==pos];slotstats.append(dict(case=case,request_number=pos,N=len(rr),e2e_p50_ms=st.median(r['e2e_ms']for r in rr),e2e_p95_ms=q([r['e2e_ms']for r in rr],.95),e2e_mean_ms=st.mean(r['e2e_ms']for r in rr),pre_vm_p50_ms=st.median(r['rpc_to_vm_ms']for r in rr),factory_p50_ms=st.median(r['factory_ms']for r in rr),slow_N=sum(r['slow_gt_1000ms']for r in rr)))
 for g in ['E0','E1','E2','E3']:
  for kind in ['all_original','slow_only_diagnostic','other_requests_diagnostic']:
   rr=[r for r in out if r['case']==case and r['group']==g and (kind=='all_original'or r['slow_gt_1000ms']==(kind=='slow_only_diagnostic'))]
   if not rr:continue
   z=dict(case=case,group=g,stratum=kind,N=len(rr),independent_batches=3)
   for metric in ['e2e_ms','rpc_to_vm_ms','factory_ms','owner_invoke_ms','put_ms']:
    vs=[r[metric]for r in rr];z.update({metric+'_mean':st.mean(vs),metric+'_p50':st.median(vs),metric+'_p95':q(vs,.95)})
   z['submit_tps']='not_defined_for_filtered_stratum'if kind!='all_original'else sum(w['successfully_committed']for w in window if w['case']==case and w['group']==g)/sum(w['actual_window_seconds']for w in window if w['case']==case and w['group']==g);strata.append(z)
assert len(out)==360 and sum(r['slow_gt_1000ms']for r in out)==24
assert all(r['request_number']==5 and r['block_height']==6 for r in out if r['slow_gt_1000ms'])
save('TIMELINE.csv',out);save('WINDOW_ANALYSIS.csv',window);save('REQUEST_POSITION.csv',slotstats);save('STRATIFIED_DIAGNOSTIC.csv',strata)
(P/'evidence/proposer-events.jsonl').write_text(''.join(json.dumps(r)+'\n'for r in stateevents));(P/'evidence/historical-log-hashes.json').write_text(json.dumps(digests,indent=2))
slow=[r for r in out if r['slow_gt_1000ms']];print('All360 reconstructed;24 slow; height6/ordinal5 fixed; recovery2s range',min(r['ready_recovery_since_first_ready_ms']for r in slow),max(r['ready_recovery_since_first_ready_ms']for r in slow));print('slow budgetfraction',min(w['slow_sdk_fraction_of_actual_window']for w in window if w['slow_N']),max(w['slow_sdk_fraction_of_actual_window']for w in window if w['slow_N']))
