from pathlib import Path
import json,csv,re,statistics as st,collections,random,hashlib,itertools
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
def save(n,r):
 keys=list(dict.fromkeys(k for x in r for k in x))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(r)
def q(v,p):
 v=sorted(v);k=(len(v)-1)*p;i=int(k);return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(k-i)
c=[r for r in read('COST_OBSERVATIONS.csv')if r['phase']=='formal'and r['verification_run']=='False'and r['run'].startswith('B-')and r['root_call']=='True'];rows=[]
for case in sorted({r['case']for r in c}):
 for mode in ['False','True']:
  for stage in sorted({r['stage']for r in c}):
   a=[r for r in c if r['case']==case and r['allocation_diagnostic']==mode and r['stage']==stage]
   if not a:continue
   v=[int(x['ns'])/1e6 for x in a];rows.append(dict(case=case,stage=stage,allocation_diagnostic=mode,N=len(a),p50_ms=st.median(v),mean_ms=st.mean(v),p95_ms=q(v,.95),mean_input_bytes=st.mean(int(x['input_bytes'])for x in a),mean_allocs=st.mean(int(x['allocs'])for x in a)if mode=='True'else'not_sampled',mean_alloc_bytes=st.mean(int(x['alloc_bytes'])for x in a)if mode=='True'else'not_sampled',native_alloc_bytes='not_measured'))
save('ROOT_COST_SUMMARY.csv',rows)
# Concurrently nested windows are never added. These four WASI/CM stages are sequential.
vm={ (r['run'],r['tx_id']):r for r in read('VM_INVOKE_BENCHMARK.csv')if r['part']=='B'and r['phase']=='formal'and r['allocation_diagnostic']=='False'};group=collections.defaultdict(dict)
for r in c:
 if r['allocation_diagnostic']=='False':group[r['run'],r['tx_id']][r['stage']]=int(r['ns'])/1e6
shares=[]
for key,stages in group.items():
 r=vm[key];init=float(r['s0_s1_ms']);shares.append(dict(case=r['case'],batch=r['batch'],slot=r['slot'],run=r['run'],tx_id=r['tx_id'],s0_s1_ms=init,new_store_ms=stages['new_store'],new_store_share_pct=100*stages['new_store']/init,wasi_import_sequential_ms=sum(stages[k]for k in ['wasi_builder','wasi_finalize','wasi_generate_imports','cm_get_imports']),wasi_import_share_pct=100*sum(stages[k]for k in ['wasi_builder','wasi_finalize','wasi_generate_imports','cm_get_imports'])/init,prepare_SHA_key_ms=stages['prepare_SHA'],runtime_clone_ms=stages['runtime_bytecode_clone'],invoke_two_SHA_ms=stages['invoke_two_SHA']))
save('ROOT_PREPARATION_SHARES.csv',shares)
cal=[];details=[]
for f in(P/'raw_logs').glob('cal-*-outcome.json'):
 z=json.loads(f.read_text());assert z['passed'];text=(P/'raw_logs'/f'{z["label"]}.log').read_text();t=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP38 ')];v=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP35 ')]
 for x in t:
  if x.get('event')!='target'or x['phase']!='formal':continue
  tx=x['tx_id'];r=next(e for e in v if e['event']=='invoke_end'and e['tx_id']==tx and e['depth']==0);outer=re.search(r'REUSE_VM tx='+tx+r' .*?begin_ns=(\d+) end_ns=(\d+) code=\d+ gas=\d+ depth=0',text);details.append(dict(case=z['case'],part=z['part'],batch=z['batch'],slot=x['slot'],tx_id=tx,owner_invoke_ms=r['invoke_ns']/1e6,factory_invoke_ms=(int(outer[2])-int(outer[1]))/1e6,restore_ms=r['copy_ns']/1e6))
for case in sorted({x['case']for x in details}):
 a={(r['batch'],r['slot']):r for r in details if r['case']==case and r['part']=='A'};b={(r['batch'],r['slot']):r for r in details if r['case']==case and r['part']=='B'};assert a.keys()==b.keys()
 for m in ['owner_invoke_ms','factory_invoke_ms','restore_ms']:
  by=collections.defaultdict(list)
  for k in a:by[k[0]].append(b[k][m]-a[k][m])
  vals=[v for x in by.values()for v in x];rng=random.Random(int(hashlib.sha256((case+m).encode()).hexdigest()[:16],16));boot=[]
  for _ in range(10000):
   v=[]
   for batch in rng.choices(list(by),k=3):v.extend(rng.choices(by[batch],k=2))
   boot.append(st.median(v))
  cal.append(dict(case=case,metric=m,N=len(vals),batches=3,median_added_ms=st.median(vals),ci95_low=q(boot,.025),ci95_high=q(boot,.975),direction='B timing-only minus A C0',scope='dedicated alternating order; timing observer, not allocation observer'))
save('INSTRUMENTATION_CALIBRATION.csv',cal);save('CALIBRATION_SAMPLES.csv',details)
# Holm sensitivity for the main C0 comparisons (post-hoc sensitivity, not preregistered), 3 independent batches.
e=read('PAIRED_EFFECTS.csv');fam=[r for r in e if r['left']=='C0'and r['right']in['C1','C2','C3','C4']and r['metric']in['restore_ms','factory_invoke_ms']]
for r in fam:
 m=[float(r['batch'+str(i)])for i in [1,2,3]];obs=abs(st.mean(m));dist=[abs(st.mean(x*s for x,s in zip(m,signs)))for signs in itertools.product([-1,1],repeat=3)];r['p_cluster_signflip']=sum(x>=obs-1e-12 for x in dist)/8
ordered=sorted(fam,key=lambda r:r['p_cluster_signflip']);prev=0
for i,r in enumerate(ordered):prev=max(prev,min(1,(len(ordered)-i)*r['p_cluster_signflip']));r['p_holm80']=prev
save('PRIMARY_SENSITIVITY.csv',fam)
print('root cost rows',len(rows),'calibration pairs',len(cal),'primary sensitivity tests',len(fam))
