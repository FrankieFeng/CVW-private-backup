from pathlib import Path
import json,csv,statistics as st,random,hashlib,sys,os
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'))
# Semantic equality helper copied locally, not importing writable historical analysis.
def check(a,b,exchange=False,success=True):
 for k in ['tx_id','contract','method','business_input','before_hash','after_hash','status','actual_result','actual_rwset']:assert a[k]==b[k],(k,a['contract'])
 if success:assert a['status']==0 and a['actual_result'].get('code',0)==0
 fields=['id','depth','contract','method','tx_id','gas_used_actual','code','result','message'];ac=sorted(a['inclusive_call_records_do_not_sum'],key=lambda r:r['id']);bc=sorted(b['inclusive_call_records_do_not_sum'],key=lambda r:r['id']);assert [{k:x.get(k)for k in fields}for x in ac]==[{k:x.get(k)for k in fields}for x in bc]
 if success:assert len(ac)==(7 if exchange else 1) and all(x['code']==0 for x in ac)
 if exchange and success:assert [(x['contract'],x['method'])for x in ac]==[('exchange','buyNow'),('identity','addWriteList'),('identity','isApprovedUser'),('identity','isApprovedUser'),('erc721','mint'),('erc721','setApprovalForAll2'),('erc721','transferFrom')]
def readcsv(f):return list(csv.DictReader(f.open()))
def dump(n,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r));f=(P/n).open('w',newline='');w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows);f.close()
def q(xs,p):a=sorted(xs);v=(len(a)-1)*p;i=int(v);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(v-i)
prefix=os.environ.get('E34_RESULT_PREFIX','v9-')
outs=[json.loads(f.read_text())for f in sorted((P/'raw_logs').glob('*-outcome.json'))];samples=[];resources=[];mods=[];events=[]
for o in outs:
 label=o['label'];text=(P/'raw_logs'/f'{label}.log').read_text(errors='replace');es=[json.loads(x[7:])for x in text.splitlines()if x.startswith('STEP22 ')];owner=o.get('owner')or{};ds=[json.loads(x[8:])for x in text.splitlines()if x.startswith('STEP21C ')];mgr=[x for x in ds if x.get('event')=='manager_closed'];bounds=o.get('boundaries',[])
 resources.append(dict(label=label,case=o['case'],phase=o['phase'],independent=o.get('independent'),fault=o.get('fault',''),passed=o['passed'],reason=o['reason'],rss_peak_kib=o['peak_rss_kib'],threads_peak=o['peak_threads'],heap_boundary_peak_bytes=max([x.get('host_after',{}).get('host_heap_objects_bytes',0)for x in bounds]+[0]),stores_created=owner.get('stores_created',''),stores_delete_calls=owner.get('stores_closed',''),instances_created=owner.get('instances_created',''),instances_delete_calls=owner.get('instances_closed',''),count_basis='C API successful creations/deletions; not Rust Rc Drop telemetry',managed_pending=owner.get('managed_pending',''),in_flight_end=mgr[-1]['in_flight']if mgr else'NA',pids_stopped=o['all_owned_processes_stopped'],cgroup_empty=o['cgroup_empty']))
 for e in es:
  if e['event']=='sample':samples.append(dict(label=label,phase=o['phase'],case=o['case'],independent=o.get('independent'),batch=o['batch'],passed_process=o['passed'],**e['data']))
  if e['event']in ['module','template']:mods.append(dict(label=label,event=e['event'],**e['data']))
 for x in text.splitlines():
  if x.startswith('STEP34 '):events.append(dict(label=label,**json.loads(x[7:])))
correct=[];historic=[]
OLD=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-32-all-contracts-acopy/raw_logs')
for f in sorted((P/'raw_logs').glob(prefix+'verify-*-block.json')):
 b=json.loads(f.read_text());rs={};assert all(l.startswith(prefix)for l in b['labels'])
 for lab in b['labels']:
  for r in(P/'raw_logs'/f'{lab}-receipts').glob('target-G?.json'):rs[r.stem[-2:]]=json.loads(r.read_text())
 assert set(rs)=={'G0','G1','G2','G3'}
 for g in ['G1','G2','G3']:check(rs['G0'],rs[g],b['case']=='exchange')
 for g,r in rs.items():
  ref=next((p for p in OLD.glob('formal-*-receipts/target-'+g+'.json')if json.loads(p.read_text())['contract']==r['contract']and json.loads(p.read_text())['method']==r['method']),None);assert ref is not None
  check(json.loads(ref.read_text()),r,b['case']=='exchange');historic.append(dict(case=b['case'],batch=b['batch'],group=g,reference=str(ref),semantic_equal=True,performance_comparison=False))
 correct.append(dict(case=b['case'],batch=b['batch'],N_groups=4,gas=rs['G0']['actual_result'].get('gas_used',0),calls_per_target=len(rs['G0']['inclusive_call_records_do_not_sum']),four_group_gas_result_rwset_events_ledger_equal=True,Step32_semantics_equal=True,table_identity='not_tested'))
cost=[];pairrows=[]
for c in ['compute','fact','erc721','exchange']:
 vals=[];nv=[];ov=[];by=[]
 for f in sorted((P/'raw_logs').glob(prefix+'cost-*-'+c+'-pair.json')):
  p=json.loads(f.read_text());pair={};assert all(l.startswith(prefix)for l in p['labels'])
  for lab in p['labels']:
   o=next(x for x in outs if x['label']==lab);r=json.loads((P/'raw_logs'/f'{lab}-receipts/target-G0.json').read_text());s=next(x for x in samples if x['label']==lab and x['tx_id']==r['tx_id']and x['depth']==0 and x['group']=='G0');pair['new'if o['independent']else'control']=(r,s)
  check(pair['control'][0],pair['new'][0],c=='exchange');new=pair['new'][1]['invoke_ns']/1e6;old=pair['control'][1]['invoke_ns']/1e6;nv.append(new);ov.append(old);vals.append(new-old);by.append(dict(case=c,batch=p['batch'],control_ms=old,new_ms=new,extra_ms=new-old,labels=json.dumps(p['labels'])))
 pairrows.extend(by)
 rng=random.Random(340034+len(cost));bs=[st.median(rng.choices(vals,k=len(vals)))for _ in range(10000)]
 cost.append(dict(case=c,N_pairs=len(vals),control_median_ms=st.median(ov),independent_median_ms=st.median(nv),paired_extra_median_ms=st.median(vals),paired_extra_mean_ms=st.mean(vals),ci95_low_ms=q(bs,.025),ci95_high_ms=q(bs,.975),batch_deltas_ms=json.dumps(vals),interpretation='positive=new independent Store slower; 3-pair exploratory not fixed universal constant; not Copy effect'))
dump('TIMING.csv',samples);dump('RESOURCE_SUMMARY.csv',resources);dump('CORRECTNESS.csv',correct);dump('HISTORICAL_SEMANTIC_CHECK.csv',historic);dump('LIFECYCLE_EVENTS.csv',[dict(label=e['label'],event=e['event'],details=json.dumps(e['data']))for e in events]);dump('MODULE_PREPARATION.csv',mods);dump('ARCHITECTURE_COST.csv',cost);dump('ARCHITECTURE_COST_PAIRS.csv',pairrows)
summary=dict(processes=len(outs),passed=sum(o['passed']for o in outs),failed=[o['label']for o in outs if not o['passed']],correctness_blocks=len(correct),correctness_root_calls=len(correct)*4,real_buyNow_roots=sum(r['case']=='exchange'for r in correct)*4,correctness_buyNow_children=sum(r['case']=='exchange'for r in correct)*4*6,cost_pairs=len(pairrows),stats='linear P95; direct paired new-control; seeded 10000 bootstrap n3 exploratory',final_build_sha=json.loads((P/'audit'/(({'v9-':'build9','v8-':'build8','v7-':'build7'}.get(prefix,'build6'))+'-outcome.json')).read_text())['binary_sha'])
(P/'analysis.json').write_text(json.dumps(summary,indent=2));print(summary);print(cost)
