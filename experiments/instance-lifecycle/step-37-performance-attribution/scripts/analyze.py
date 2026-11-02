"""Step37: independent read-only reanalysis of frozen Step36. Standard library only.
No node, compiler, historical script execution, or writes into Step36.
"""
from pathlib import Path
import json,csv,hashlib,statistics as st,random,itertools,collections,math,subprocess
P=Path(__file__).resolve().parents[1];S=P.parent/'step-36-e2e-copy-acopy';ROOT=Path('/home/frankie/mygitprojects')
def csvread(p):return list(csv.DictReader(p.open()))
def save(n,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with(P/n).open('w',newline='')as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def q(v,p):
 a=sorted(v);k=(len(a)-1)*p;i=int(k);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(k-i)
def boot(by,seed):
 rng=random.Random(seed);ks=list(by);v=[]
 for _ in range(10000):
  d=[]
  for k in rng.choices(ks,k=len(ks)):d.extend(rng.choices(by[k],k=len(by[k])))
  v.append(st.median(d))
 return q(v,.025),q(v,.975)
def pflip(by):
 # Cluster-level two-sided conditional sign randomization; no iid transaction assumption.
 m=[st.mean(v)for v in by.values()];obs=abs(st.mean(m));dist=[abs(st.mean(s*x for s,x in zip(ss,m)))for ss in itertools.product([-1,1],repeat=len(m))]
 return sum(x>=obs-1e-12 for x in dist)/len(dist)
def holm(rs):
 ranked=sorted(rs,key=lambda r:r['p_cluster_signflip']);last=0
 for i,r in enumerate(ranked):last=max(last,min(1,(len(rs)-i)*r['p_cluster_signflip']));r['p_holm_222']=last;r['holm_significant_005']=last<.05;r['p_statistic']='absolute mean of three batch mean paired differences; cluster sign symmetry assumed'
# Integrity: verify every saved checksum without modifying baseline files.
bad=[];checks=0;artifact_fallbacks=[]
for l in(S/'SHA256SUMS').read_text().splitlines():
 h,n=l.split('  ',1);f=S/n;checks+=1
 if not f.exists():
  alternate=ROOT/'.worktrees/cvw-step36/experiments/instance-lifecycle/step-36-e2e-copy-acopy'/n
  if alternate.exists():artifact_fallbacks.append(dict(relative=n,source=str(alternate),reason='ignored binary absent from Git worktree; checked at original frozen location'));f=alternate
 if not f.exists()or hashlib.sha256(f.read_bytes()).hexdigest()!=h:bad.append(n)
assert not bad,bad
C=json.loads((S/'inputs/cases.json').read_text());raw=csvread(S/'RAW_TRANSACTIONS.csv');valid=[r for r in raw if r['valid_main']=='True'];assert len(valid)==1728
byrun=collections.defaultdict(list)
for r in valid:byrun[r['run']].append(r)
T=[];stages=[];ledger=[]
for run,rr in byrun.items():
 x=json.loads((S/'raw_logs'/f'{run}-case.json').read_text());assert x['passed'] and x['phase']=='formal'
 rows=x['window']['rows'];assert len(rows)==len(rr)
 logs=(S/'raw_logs'/f'{run}-node.log').read_text().splitlines();vm=[json.loads(l[7:])for l in logs if l.startswith('STEP35 ')];ends=[e for e in vm if e['event']=='invoke_end']
 for i,r in enumerate(rr):
  a=rows[i];assert a['input']['Tag']=='target-'+str(i) and a['success'];assert a['response']['tx_id']==r['tx_id'];assert abs(a['elapsed_ns']/1e6-float(r['e2e_ms']))<1e-9
  roots=[e for e in ends if e.get('depth')==0 and e.get('tx_id')==r['tx_id']];subs=[e for e in ends if e.get('depth',0)>0 and e.get('tx_id')==r['tx_id']]
  assert roots and len(roots)==int(r['vm_root_invokes']) and len(subs)==int(r['vm_sub_invokes'])
  z={k:r[k]for k in ['run','case','group','tx_id','request_id','block_height']};z.update(batch=int(r['batch']),slot=int(r['slot']),e2e_ms=a['elapsed_ns']/1e6,vm_factory_ms=float(r['vm_factory_ms']),root_invokes=len(roots),sub_invokes=len(subs))
  for key,field in [('vm_inner_ms','invoke_ns'),('s0_s1_ms','s1_ns'),('newinstance_ms','newinstance_ns'),('copy_ms','copy_ns'),('start_ms','start_ns'),('callmethod_ms','callmethod_ns'),('close_ms','close_ns')]:
   z[key]=sum(e.get(field,0)for e in roots)/1e6;assert abs(z[key]-float(r[key]))<1e-8
  z['s1_s2_ms']=sum(e['s2_ns']-e['s1_ns']for e in roots)/1e6
  # Same-process envelope residual, deliberately not labeled pure Store/WASI/host time.
  z['outer_minus_owner_derived_ms']=z['vm_factory_ms']-z['vm_inner_ms']
  T.append(z)
  for e in roots+subs:stages.append(dict(run=run,**e))
 assert x['window']['window_ns']==rows[-1]['sdk_end_mono_ns']-rows[0]['sdk_start_mono_ns']
 ledger.append(dict(run=run,case=x['case'],group=x['group'],batch=x['batch'],N=len(rows),seconds=x['window']['window_ns']/1e9,tps=len(rows)/(x['window']['window_ns']/1e9)))
T.sort(key=lambda r:(r['case'],r['group'],r['batch'],r['slot']));buckets=collections.defaultdict(list)
for r in T:buckets[r['case'],r['group']].append(r)
metrics=['e2e_ms','vm_factory_ms','vm_inner_ms','s0_s1_ms','start_ms'];stats=[]
for(c,g),rr in sorted(buckets.items()):
 for m in metrics+['newinstance_ms','copy_ms','callmethod_ms','close_ms','s1_s2_ms']:
  v=[r[m]for r in rr];stats.append(dict(case=c,group=g,metric=m,N=len(v),mean=st.mean(v),p50=st.median(v),p95=q(v,.95),batches=len({r['batch']for r in rr})))
orders={1:['G0','G1','G2','G3'],2:['G2','G3','G0','G1'],3:['G1','G0','G3','G2']};effects=[];batchrows=[];interactions=[]
contrasts=[('G0','G1'),('G0','G3'),('G0','G2'),('G1','G2'),('G3','G2')]
old={(r['case'],r['left'],r['right'],r['metric']):r for r in csvread(S/'PAIRED_EFFECTS.csv')};repro=[]
for c in C:
 keyed={g:{(r['batch'],r['slot']):r for r in buckets[c,g]}for g in ['G0','G1','G2','G3']};keys=sorted(keyed['G0']);assert all(set(keyed[g])==set(keys)for g in keyed)
 for l,r in contrasts:
  a,b=keyed[l],keyed[r]
  for metric in metrics:
   data={k:a[k][metric]-b[k][metric]for k in keys};by=collections.defaultdict(list)
   for (batch,slot),v in data.items():by[batch].append(v)
   seed=int(hashlib.sha256((c+l+r+metric).encode()).hexdigest()[:16],16);lo,hi=boot(by,seed);vv=list(data.values());av=[a[k][metric]for k in keys];bv=[b[k][metric]for k in keys]
   winsA=[w for w in ledger if w['case']==c and w['group']==l];winsB=[w for w in ledger if w['case']==c and w['group']==r];ta={w['batch']:w['tps']for w in winsA};tb={w['batch']:w['tps']for w in winsB}
   pooledA=sum(w['N']for w in winsA)/sum(w['seconds']for w in winsA);pooledB=sum(w['N']for w in winsB)/sum(w['seconds']for w in winsB)
   out=dict(case=c,left=l,right=r,metric=metric,N=len(vv),batches=3,left_mean=st.mean(av),left_p50=st.median(av),left_p95=q(av,.95),right_mean=st.mean(bv),right_p50=st.median(bv),right_p95=q(bv,.95),paired_saving_median=st.median(vv),paired_saving_mean=st.mean(vv),paired_pct_median=st.median(100*data[k]/a[k][metric]for k in keys if a[k][metric]>0),ci95_low=lo,ci95_high=hi,positive_fraction=sum(v>0 for v in vv)/len(vv),batch1=st.median(by[1]),batch2=st.median(by[2]),batch3=st.median(by[3]),all_batches_positive=all(st.median(by[i])>0 for i in by),p_cluster_signflip=pflip(by),left_pooled_tps=pooledA,right_pooled_tps=pooledB,tps_gain=pooledB-pooledA,tps_gain_pct=100*(pooledB/pooledA-1),batch1_tps_gain=tb[1]-ta[1],batch2_tps_gain=tb[2]-ta[2],batch3_tps_gain=tb[3]-ta[3],evidence_grade='B',bootstrap_seed=seed,bootstrap_draws=10000)
   effects.append(out);o=old[c,l,r,metric];delta=max(abs(float(o[k])-out[k])for k in ['paired_saving_median','ci95_low','ci95_high','positive_fraction']);assert delta<1e-8,(c,l,r,metric,delta);repro.append(dict(case=c,left=l,right=r,metric=metric,max_abs_difference=delta))
   for batch in [1,2,3]:
    v=by[batch];batchrows.append(dict(case=c,left=l,right=r,metric=metric,stratum='batch',batch=batch,N=len(v),mean_saving=st.mean(v),median_saving=st.median(v),p95_saving=q(v,.95),left_position=orders[batch].index(l)+1,right_position=orders[batch].index(r)+1,tps_gain=tb[batch]-ta[batch]))
   if metric=='e2e_ms':
    for name,pred in [('left_first',lambda k:orders[k[0]].index(l)<orders[k[0]].index(r)),('right_first',lambda k:orders[k[0]].index(l)>orders[k[0]].index(r)),('first_slot',lambda k:k[1]==0),('later_slots',lambda k:k[1]>0)]:
     v=[x for k,x in data.items()if pred(k)];batchrows.append(dict(case=c,left=l,right=r,metric=metric,stratum=name,batch='mixed',N=len(v),mean_saving=st.mean(v)if v else'not_available',median_saving=st.median(v)if v else'not_available'))
 # Positive saving synergy means combination exceeds sum of separate savings.
 data={k:keyed['G1'][k]['e2e_ms']+keyed['G3'][k]['e2e_ms']-keyed['G0'][k]['e2e_ms']-keyed['G2'][k]['e2e_ms']for k in keys};by=collections.defaultdict(list)
 for (batch,slot),v in data.items():by[batch].append(v)
 seed=int(hashlib.sha256((c+'interaction').encode()).hexdigest()[:16],16);lo,hi=boot(by,seed)
 interactions.append(dict(case=c,N=len(keys),batches=3,saving_synergy_median=st.median(data.values()),saving_synergy_mean=st.mean(data.values()),ci95_low=lo,ci95_high=hi,cost_interaction_median=-st.median(data.values()),positive_synergy_fraction=sum(v>0 for v in data.values())/len(keys),batch1=st.median(by[1]),batch2=st.median(by[2]),batch3=st.median(by[3]),p_cluster_signflip=pflip(by),bootstrap_seed=seed,evidence_grade='B'))
family=[r for r in effects if r['metric']=='e2e_ms']+interactions;assert len(family)==222;holm(family)
for r in effects:
 if r['metric']!='e2e_ms':r.update(p_holm_222='not_in_primary_family',holm_significant_005='not_tested',p_statistic='absolute mean of three batch mean paired differences; cluster sign symmetry assumed')
classify=[]
for c in C:
 z=dict(case=c,contract=C[c]['contract'],method=C[c]['method'],N_per_group=len(buckets[c,'G0']),batches=3,coverage='PASSED',correctness='Step36 matched Gas/result/RWSet/events/written-key projection; exceptions limited')
 for l,r,name in [('G0','G1','copy'),('G0','G3','A'),('G0','G2','AC'),('G1','G2','A_on_copy'),('G3','G2','copy_on_A')]:
  e=next(e for e in effects if(e['case'],e['left'],e['right'],e['metric'])==(c,l,r,'e2e_ms'));z[name+'_exploratory_class']='CI_positive'if e['ci95_low']>0 else'CI_negative'if e['ci95_high']<0 else'uncertain';z[name+'_saving_ms']=e['paired_saving_median'];z[name+'_holm_class']='supported'if e['holm_significant_005']else'insufficient_cluster_evidence';z[name+'_three_batches_positive']=e['all_batches_positive']
 z['interaction_saving_synergy_ms']=next(i['saving_synergy_median']for i in interactions if i['case']==c);classify.append(z)
# Stage tables: no inferred Store/WASI/VM-external number.
phase=[]
for(c,g),rr in sorted(buckets.items()):
 for name,key in [('Store preparation','not_measured'),('WASI/import preparation','not_measured'),('NewInstance','newinstance_ms'),('Copy','copy_ms'),('_start','start_ms'),('S0_to_S1','s0_s1_ms'),('S1_to_S2','s1_s2_ms'),('S2_to_S3','not_measured'),('CallMethod','callmethod_ms'),('exportFunc.Call','not_measured'),('Close','close_ms'),('Owner Invoke','vm_inner_ms'),('Factory Invoke','vm_factory_ms'),('VM external remainder','not_measured'),('SDK E2E','e2e_ms')]:
  vals=[r[key]for r in rr]if key!='not_measured'else[];phase.append(dict(case=c,group=g,phase=name,N=len(vals),mean_ms=st.mean(vals)if vals else'not_measured',p50_ms=st.median(vals)if vals else'not_measured',p95_ms=q(vals,.95)if vals else'not_measured',boundary='sum of all root executions per TxID; nested phases not additive'if vals and key!='e2e_ms'else'direct SDK duration'if vals else'no isolated persisted timer'))
# Auto-selection uses uncorrected exploratory categories, never silently upgrades evidence.
look={(r['case'],r['left'],r['right']):r for r in effects if r['metric']=='e2e_ms'};selections=[]
def choose(cat,eligible,score):
 if eligible:
  c=max(eligible,key=score);selections.append(dict(category=cat,case=c,selection='automatic',rule='explicit predicates in scripts/analyze.py; exploratory unadjusted CI',evidence_grade='B'))
 else:selections.append(dict(category=cat,case='none',selection='no method meets criterion; do not force an example',evidence_grade='D'))
choose('Copy_positive',[c for c in C if look[c,'G0','G1']['ci95_low']>0],lambda c:look[c,'G0','G1']['paired_saving_median'])
choose('Copy_uncertain',[c for c in C if look[c,'G0','G1']['ci95_low']<=0<=look[c,'G0','G1']['ci95_high']],lambda c:look[c,'G0','G1']['ci95_high']-look[c,'G0','G1']['ci95_low'])
choose('Copy_negative',[c for c in C if look[c,'G0','G1']['ci95_high']<0],lambda c:-look[c,'G0','G1']['paired_saving_median'])
choose('A_only_positive_AC_not_further',[c for c in C if look[c,'G0','G3']['ci95_low']>0 and look[c,'G3','G2']['ci95_low']<=0],lambda c:look[c,'G0','G3']['paired_saving_median'])
choose('AC_better_than_all',[c for c in C if all(look[c,l,'G2']['ci95_low']>0 for l in ['G0','G1','G3'])],lambda c:look[c,'G0','G2']['paired_saving_median'])
choose('VM_gain_TPS_loss',[c for c in C if next(r for r in effects if(r['case'],r['left'],r['right'],r['metric'])==(c,'G0','G1','vm_inner_ms'))['paired_saving_median']>0 and look[c,'G0','G1']['tps_gain']<0],lambda c:-look[c,'G0','G1']['tps_gain'])
choose('multi_contract',[c for c in C if max(t['sub_invokes']for t in buckets[c,'G0'])>=6],lambda c:max(t['sub_invokes']for t in buckets[c,'G0']))
for n,r in [('RECOMPUTED_TRANSACTIONS.csv',T),('GROUP_STATISTICS.csv',stats),('PAIRED_EFFECTS.csv',effects),('BATCH_ANALYSIS.csv',batchrows),('INTERACTION_ANALYSIS.csv',interactions),('METHOD_CLASSIFICATION.csv',classify),('STAGE_BREAKDOWN.csv',phase),('CASE_SELECTION.csv',selections),('REPRODUCTION_CHECK.csv',repro)]:save(n,r)
report=dict(source_cvw_commit='abc2ce356ad821c451c788d19cded9cbe21d55fd',node_commit=subprocess.check_output(['git','-C',str(ROOT/'.worktrees/node-step36'),'rev-parse','HEAD'],text=True).strip(),checksum_files=checks,checksum_failures=bad,ignored_artifact_fallbacks=artifact_fallbacks,formal_transactions=len(T),formal_windows=len(ledger),independent_batches=3,methods=len(C),root_execution_count=sum(t['root_invokes']for t in T),paired_ci_reproductions=len(repro),max_ci_difference=max(x['max_abs_difference']for x in repro),holm_family_size=len(family),minimum_raw_cluster_p=min(x['p_cluster_signflip']for x in family),holm_significant=sum(x['holm_significant_005']for x in family),all_original_rows=len(raw),new_performance_runs=0)
(P/'audit/reanalysis.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
