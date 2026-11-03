from pathlib import Path
import json,csv,re,statistics as st,random,hashlib,collections
P=Path(__file__).resolve().parents[1]
def save(n,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/n).open('w',newline='')as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def q(v,p):
 a=sorted(v);k=(len(a)-1)*p;i=int(k);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(k-i)
def ci(by,key):
 rng=random.Random(int(hashlib.sha256(key.encode()).hexdigest()[:16],16));bs=list(by);vals=[]
 for _ in range(10000):
  a=[]
  for b in rng.choices(bs,k=len(bs)):a.extend(rng.choices(by[b],k=len(by[b])))
  vals.append(st.median(a))
 return q(vals,.025),q(vals,.975)
rows=[];resources=[];costs=[];checks=[]
for file in sorted((P/'raw_logs').glob('*-outcome.json')):
 z=json.loads(file.read_text());label=z['label'];o=z['owner'];resources.append(dict(run=label,passed=z['passed'],exit_code=z['exit_code'],rss_peak_mib=z['rss_peak_mib'],threads_peak=z['threads_peak'],stores_created=o.get('stores_created'),stores_closed=o.get('stores_closed'),instances_created=o.get('instances_created'),instances_closed=o.get('instances_closed'),pending=o.get('managed_pending'),pid_exited=z['pid_exited']))
 if z['test']!='TestStep39VM' or label.startswith('lean-'):continue
 text=(P/'raw_logs'/f'{label}.log').read_text();targets=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP38 ')and'"target"'in l];nodes=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP35 ')];arts=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP39 ')and'"artifact_costs"'in l]
 for t in targets:
  tx=t['tx_id'];vm=[r for r in nodes if r.get('event')=='invoke_end'and r.get('tx_id')==tx];root=[r for r in vm if r['depth']==0];assert len(root)==1;r=root[0]
  art=[a for a in arts if a['tx_id']==tx];rootcost=next(a for a in art if a['contract']==r['contract'])['costs'];rc={x['stage']:x for x in rootcost};sha=[x for x in rootcost if 'sha'in x['stage']];clone=[x for x in rootcost if x['stage']=='runtime_clone']
  outer=re.findall(r'REUSE_VM tx='+tx+r' .*?begin_ns=(\d+) end_ns=(\d+) code=(\d+) gas=(\d+) depth=(\d+)',text);outer=[(int(a),int(b))for a,b,c,g,d in outer if int(d)==0];assert len(outer)==1
  row=dict(run=label,case=z['case'],mode=z['strategy'],batch=z['batch'],slot=t['slot'],phase=t['phase'],verification=z['verify'],tx_id=tx,factory_invoke_ms=(outer[0][1]-outer[0][0])/1e6,runcontract_ms=t['runcontract_ns']/1e6,owner_invoke_ms=r['invoke_ns']/1e6,runtime_create_ms=rc['runtime_create']['ns']/1e6,prepare_ms=rc['prepare_total']['ns']/1e6,root_sha_count=sum(x['count']for x in sha),root_sha_input_bytes=sum(x['bytes']for x in sha),root_sha_ms=sum(x['ns']for x in sha)/1e6,root_clone_count=sum(x['count']for x in clone),root_clone_bytes=sum(x['bytes']for x in clone),root_clone_ms=sum(x['ns']for x in clone)/1e6,artifact_acquire_ms=rc.get('artifact_acquire',{}).get('ns',0)/1e6,all_calls=len(vm),start_ms=r['start_ns']/1e6,restore_ms=r.get('copy_ns',0)/1e6,newinstance_ms=r['newinstance_ns']/1e6,close_ms=r['close_ns']/1e6,host_envelope_allocs=t['host_envelope_allocs'],host_envelope_alloc_bytes=t['host_envelope_alloc_bytes'],host_heap=t['host_heap'],gas=t['result'].get('gas_used',0),range_count=r['range_count'],copy_bytes=r['copy_bytes'],rss_peak_mib=z['rss_peak_mib'],threads_peak=z['threads_peak'],initial_memory_match=r.get('initial_memory_match','not_checked_in_formal'))
  row['all_call_sha_count']=sum(x['count']for a in art for x in a['costs']if 'sha'in x['stage']);row['all_call_clone_bytes']=sum(x['bytes']for a in art for x in a['costs']if x['stage']=='runtime_clone')
  rows.append(row)
  for a in art:
   for x in a['costs']:costs.append(dict(run=label,case=z['case'],mode=z['strategy'],phase=t['phase'],tx_id=tx,contract=a['contract'],rid=a['rid'],root=a['contract']==r['contract'],**x))
  checks.append(dict(run=label,tx_id=tx,phase=t['phase'],vm_calls=len(vm),all_gas_success=all(e['code']==0 and e['error']=='<nil>'for e in vm),stores_distinct=all(e['store_id']!=e['compile_store_id']for e in vm),full_memory_checked=z['verify'],initial_memory_match=all(e.get('initial_memory_match',False)for e in vm)if z['verify']else'not_checked_in_formal'))
main=[r for r in rows if r['phase']=='formal'and not r['verification']and r['run'].startswith('formal-')];assert len(main)==72
save('BENCHMARK.csv',rows);save('COSTS.csv',costs);save('RESOURCE_SUMMARY.csv',resources);save('CORRECTNESS_CHECKS.csv',checks)
summary=[];effects=[]
metrics=['factory_invoke_ms','runcontract_ms','runtime_create_ms','prepare_ms','root_sha_ms','root_clone_ms','artifact_acquire_ms','owner_invoke_ms','restore_ms','start_ms','host_envelope_allocs','host_envelope_alloc_bytes']
for case in sorted({r['case']for r in main}):
 d={g:{(int(r['batch']),r['slot']):r for r in main if r['case']==case and r['mode']==g}for g in 'ABCD'}
 for mode,a in d.items():
  for metric in metrics:
   v=[r[metric]for r in a.values()];summary.append(dict(case=case,mode=mode,metric=metric,N=len(v),independent_batches=3,mean=st.mean(v),p50=st.median(v),p95=q(v,.95)))
 for left,right in [('A','B'),('A','C'),('A','D'),('B','D'),('C','D')]:
  for metric in metrics:
   by=collections.defaultdict(list)
   for k in d[left]:by[k[0]].append(d[left][k][metric]-d[right][k][metric])
   v=[x for values in by.values()for x in values];lo,hi=ci(by,case+left+right+metric);effects.append(dict(case=case,left=left,right=right,metric=metric,N=len(v),batches=3,saving_median=st.median(v),saving_mean=st.mean(v),ci95_low=lo,ci95_high=hi,positive_fraction=sum(x>0 for x in v)/len(v),batch1=st.median(by[1]),batch2=st.median(by[2]),batch3=st.median(by[3])))
save('SUMMARY.csv',summary);save('PAIRED_EFFECTS.csv',effects)
for r in effects:
 if r['left']=='A'and r['right']=='D'and r['metric']in ['factory_invoke_ms','runcontract_ms','runtime_create_ms']:print(r)
lean=[]
for f in sorted((P/'raw_logs').glob('lean-*-outcome.json')):
 z=json.loads(f.read_text());text=(P/'raw_logs'/(z['label']+'.log')).read_text();assert '"artifact_costs"'not in text
 targets=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP38 ')and'"target"'in l]
 for t in targets:
  if t['phase']!='formal':continue
  tx=t['tx_id'];a=re.findall(r'REUSE_VM tx='+tx+r' .*?begin_ns=(\d+) end_ns=(\d+) code=(\d+) gas=(\d+) depth=(\d+)',text);a=[(int(s),int(e))for s,e,c,g,d in a if int(d)==0];assert len(a)==1
  lean.append(dict(run=z['label'],case=z['case'],mode=z['strategy'],batch=z['batch'],slot=t['slot'],factory_invoke_ms=(a[0][1]-a[0][0])/1e6,runcontract_ms=t['runcontract_ns']/1e6,host_envelope_allocs=t['host_envelope_allocs'],host_envelope_alloc_bytes=t['host_envelope_alloc_bytes']))
assert len(lean)==36
save('LEAN_SAMPLES.csv',lean);le=[]
for case in sorted({r['case']for r in lean}):
 d={mode:{(int(r['batch']),r['slot']):r for r in lean if r['case']==case and r['mode']==mode}for mode in 'AB'}
 for metric in ['factory_invoke_ms','runcontract_ms','host_envelope_allocs','host_envelope_alloc_bytes']:
  by=collections.defaultdict(list)
  for k in d['A']:by[k[0]].append(d['A'][k][metric]-d['B'][k][metric])
  v=[x for vv in by.values()for x in vv];lo,hi=ci(by,'lean'+case+metric);r=dict(case=case,metric=metric,N=len(v),independent_batches=3,A_p50=st.median([x[metric]for x in d['A'].values()]),B_p50=st.median([x[metric]for x in d['B'].values()]),A_p95=q([x[metric]for x in d['A'].values()],.95),B_p95=q([x[metric]for x in d['B'].values()],.95),saving_median=st.median(v),ci95_low=lo,ci95_high=hi,positive_fraction=sum(x>0 for x in v)/len(v),batch1=st.median(by[1]),batch2=st.median(by[2]),batch3=st.median(by[3]));le.append(r)
  if metric in ['factory_invoke_ms','runcontract_ms']:print('LEAN',r)
save('LEAN_EFFECTS.csv',le)
# Match each child cost and Gas boundary; do not sum inclusive Invoke windows.
child=[]
for phase in ['pre','formal']:
 for case in ['compute_hashCal','exchange_buyNow','bigInput_inputSize']:
  for batch in (['pre']if phase=='pre'else[1,2,3]):
   groups=[]
   for mode in 'ABCD':
    label=('pre-compute-A'if case=='compute_hashCal'and mode=='A'else 'pre-'+case+'-'+mode)if phase=='pre'else f'formal-{case}-b{batch}-{mode}'
    text=(P/'raw_logs'/f'{label}.log').read_text();groups.append([(r['tx_id'],r['contract'],r['method'],r['depth'],r['gas'],r['code'])for l in text.splitlines()if l.startswith('STEP35 ')for r in [json.loads(l[7:])]if r['event']=='invoke_end'])
   # Init tx ids are fixed too, include all layers and setup/warm/formal.
   assert all(x==groups[0]for x in groups),(phase,case,batch,'child Gas mismatch')
   child.append(dict(phase=phase,case=case,batch=batch,all_layer_gas_equal=True,executed_invokes=len(groups[0])))
save('CHILD_GAS_PARITY.csv',child)
order=[]
for cohort,rs in [('main',main),('lean',lean)]:
 for case in sorted({r['case']for r in rs}):
  for batch in [1,2,3]:
   if cohort=='main':seq=json.loads((P/'audit'/f'order-{case}-b{batch}.json').read_text())
   else:j=['compute_hashCal','exchange_buyNow','bigInput_inputSize'].index(case);seq=['A','B']if(batch+j)%2 else['B','A']
   pair={g:{r['slot']:r for r in rs if r['case']==case and int(r['batch'])==batch and r['mode']==g}for g in 'AB'}
   for metric in ['factory_invoke_ms','runcontract_ms']:
    v=[pair['A'][k][metric]-pair['B'][k][metric]for k in pair['A']];order.append(dict(cohort=cohort,case=case,batch=batch,order='>'.join(seq),B_after_A=seq.index('B')>seq.index('A'),metric=metric,N=len(v),saving_median=st.median(v)))
save('ORDER_EFFECTS.csv',order)
