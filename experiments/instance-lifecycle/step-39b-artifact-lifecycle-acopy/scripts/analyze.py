from pathlib import Path
import json,csv,re,statistics as st,random,hashlib,collections
P=Path(__file__).resolve().parents[1]
def save(n,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def q(v,p):
 a=sorted(v);k=(len(a)-1)*p;i=int(k);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(k-i)
def ci(by,key):
 rng=random.Random(int(hashlib.sha256(key.encode()).hexdigest()[:16],16));bs=list(by);vals=[]
 for _ in range(10000):
  a=[]
  for b in rng.choices(bs,k=len(bs)):a.extend(rng.choices(by[b],k=len(by[b])))
  vals.append(st.median(a))
 return q(vals,.025),q(vals,.975)
rows=[];resources=[];costs=[];checks=[];lifecycle=[]
for file in sorted((P/'raw_logs').glob('*-outcome.json')):
 z=json.loads(file.read_text());label=z['label'];o=z['owner'];resources.append(dict(run=label,passed=z['passed'],exit_code=z['exit_code'],rss_peak_mib=z['rss_peak_mib']or'not_sampled',threads_peak=z['threads_peak']or'not_sampled',stores_created=o.get('stores_created','not_applicable'),stores_closed=o.get('stores_closed','not_applicable'),instances_created=o.get('instances_created','not_applicable'),instances_closed=o.get('instances_closed','not_applicable'),pending=o.get('managed_pending','not_applicable'),pid_exited=z['pid_exited'],owner_expected=bool(o)))
 text=(P/'raw_logs'/f'{label}.log').read_text()
 for line in text.splitlines():
  if line.startswith('STEP39 '):
   ev=json.loads(line[7:])
   if ev.get('event')=='lifecycle_check':lifecycle.append(dict(run=label,**ev))
 if z['test']!='TestStep39VM':continue
 targets=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP38 ')and'"target"'in l];nodes=[json.loads(l[7:])for l in text.splitlines()if l.startswith('STEP35 ')]
 assert 'STEP39 {"contract"'not in text,'unexpected in-window cost JSON'
 for t in targets:
  tx=t['tx_id'];vm=[r for r in nodes if r.get('event')=='invoke_end'and r.get('tx_id')==tx];root=[r for r in vm if r['depth']==0];assert len(root)==1;r=root[0]
  arts=t['artifact_costs'];assert len(arts)==len(vm);art=next(a for a in arts if a['Contract']==r['contract']);rc={x['stage']:x for x in art['Costs']};invoke=[x for x in art['Costs']if x['stage'].startswith('invoke_')and x['stage'].endswith('_sha')];prep=[x for x in art['Costs']if x['stage']=='prepare_sha'];clones=[x for x in art['Costs']if x['stage']=='runtime_clone'];keysha=lambda c:sum(x['count']for a in arts for x in a['Costs']if x['stage']in c)
  outer=re.findall(r'REUSE_VM tx='+tx+r' .*?begin_ns=(\d+) end_ns=(\d+) code=(\d+) gas=(\d+) depth=(\d+)',text);outer=[(int(a),int(b))for a,b,c,g,d in outer if int(d)==0];assert len(outer)==1
  row=dict(run=label,case=z['case'],group=z['strategy'],batch=z['batch'],slot=t['slot'],phase=t['phase'],verification=z['verify'],diagnostic=label.startswith('diag-'),tx_id=tx,factory_invoke_ms=(outer[0][1]-outer[0][0])/1e6,runcontract_ms=t['runcontract_ns']/1e6,owner_invoke_ms=r['invoke_ns']/1e6,runtime_create_ms=rc['runtime_create']['ns']/1e6,prepare_ms=rc['prepare_total']['ns']/1e6,invoke_sha_count=sum(x['count']for x in invoke),invoke_sha_input_bytes=sum(x['bytes']for x in invoke),invoke_sha_ms=sum(x['ns']for x in invoke)/1e6,prepare_sha_count=sum(x['count']for x in prep),prepare_sha_ms=sum(x['ns']for x in prep)/1e6,runtime_clone_count=sum(x['count']for x in clones),runtime_clone_bytes=sum(x['bytes']for x in clones),runtime_clone_ms=sum(x['ns']for x in clones)/1e6,artifact_acquire_ms=rc.get('artifact_acquire',{}).get('ns',0)/1e6,all_invokes=len(vm),all_invoke_sha_count=keysha(['invoke_input_sha','invoke_snapshot_sha']),all_prepare_sha_count=keysha(['prepare_sha']),all_runtime_clone_bytes=sum(x['bytes']for a in arts for x in a['Costs']if x['stage']=='runtime_clone'),start_ms=r['start_ns']/1e6,newinstance_restore_ms=(r['newinstance_ns']+r.get('copy_ns',0))/1e6,restore_ms=r.get('copy_ns',0)/1e6,close_ms=r['close_ns']/1e6,host_envelope_allocs=t['host_envelope_allocs'],host_envelope_alloc_bytes=t['host_envelope_alloc_bytes'],host_heap=t['host_heap'],gas=t['result'].get('gas_used',0),range_count=r['range_count'],copy_bytes=r['copy_bytes'],rss_peak_mib=z['rss_peak_mib'],threads_peak=z['threads_peak'])
  rows.append(row)
  for a in arts:
   for x in a['Costs']:costs.append(dict(run=label,case=z['case'],group=z['strategy'],phase=t['phase'],diagnostic=label.startswith('diag-'),tx_id=tx,contract=a['Contract'],rid=a['RID'],root=a['Contract']==r['contract'],**x))
  checks.append(dict(run=label,tx_id=tx,phase=t['phase'],vm_calls=len(vm),all_success=all(e['code']==0 and e['error']=='<nil>'for e in vm),independent_stores=all(e['store_id']!=e['compile_store_id']for e in vm),memory_checked=z['verify'],full_initial_memory_equal=all(e.get('initial_memory_match',False)for e in vm)if z['verify']else'not_checked_in_formal'))
main=[r for r in rows if r['phase']=='formal'and r['run'].startswith('formal-')];assert len(main)==72
assert all(r['runtime_clone_count']==1 for r in main)
assert all(r['invoke_sha_count']==(1 if r['group']in ['G1','G3']else 2)for r in main)
assert all(r['prepare_sha_count']==(0 if r['group']in ['G1','G3']else 1)for r in main)
assert all(r['all_invokes']==(7 if r['case']=='exchange_buyNow'else 1)for r in main)
save('RESULTS.csv',rows);save('COSTS.csv',costs);save('RESOURCE_SUMMARY.csv',resources);save('CORRECTNESS_CHECKS.csv',checks);save('LIFECYCLE_CHECKS.csv',lifecycle)
summary=[];effects=[];orderrows=[]
metrics=['factory_invoke_ms','runcontract_ms','runtime_create_ms','runtime_clone_ms','artifact_acquire_ms','prepare_ms','invoke_sha_ms','newinstance_restore_ms','restore_ms','start_ms','owner_invoke_ms','close_ms','host_envelope_alloc_bytes']
for case in sorted({r['case']for r in main}):
 d={g:{(int(r['batch']),r['slot']):r for r in main if r['case']==case and r['group']==g}for g in ['G0','G1','G2','G3']}
 for group,a in d.items():
  for metric in metrics:
   v=[r[metric]for r in a.values()];summary.append(dict(case=case,group=group,metric=metric,N=len(v),independent_batches=3,mean=st.mean(v),p50=st.median(v),p95=q(v,.95)))
 for left,right in [('G0','G1'),('G2','G3'),('G1','G3'),('G0','G2'),('G0','G3')]:
  for metric in metrics:
   by=collections.defaultdict(list)
   for k in d[left]:by[k[0]].append(d[left][k][metric]-d[right][k][metric])
   v=[x for values in by.values()for x in values];lo,hi=ci(by,case+left+right+metric);effects.append(dict(case=case,left=left,right=right,metric=metric,N=len(v),independent_batches=3,saving_median=st.median(v),saving_mean=st.mean(v),ci95_low=lo,ci95_high=hi,positive_fraction=sum(x>0 for x in v)/len(v),batch1=st.median(by[1]),batch2=st.median(by[2]),batch3=st.median(by[3])))
   for batch,vals in by.items():
    order=json.loads((P/'audit'/f'order-{case}-b{batch}.json').read_text());orderrows.append(dict(case=case,left=left,right=right,batch=batch,metric=metric,order='>'.join(order),right_after_left=order.index(right)>order.index(left),N=len(vals),saving_median=st.median(vals)))
save('SUMMARY.csv',summary);save('PAIRED_EFFECTS.csv',effects);save('ORDER_EFFECTS.csv',orderrows)
# Root result parity is already checked by the runner; verify each child gas/name/depth sequence too.
child=[]
for prefix,batches in [('pre',['pre']),('formal',[1,2,3])]:
 for case in ['compute_hashCal','exchange_buyNow','bigInput_inputSize']:
  for batch in batches:
   sequences=[]
   for g in ['G0','G1','G2','G3']:
    label=f'pre-{case}-{g}'if prefix=='pre'else f'formal-{case}-b{batch}-{g}';text=(P/'raw_logs'/f'{label}.log').read_text();sequences.append([(r['tx_id'],r['contract'],r['method'],r['depth'],r['gas'],r['code'])for l in text.splitlines()if l.startswith('STEP35 ')for r in [json.loads(l[7:])]if r['event']=='invoke_end'])
   assert all(x==sequences[0]for x in sequences),(case,batch,'child Gas mismatch');child.append(dict(case=case,batch=batch,phase=prefix,all_layer_gas_equal=True,executed_invokes=len(sequences[0])))
save('CHILD_GAS_PARITY.csv',child)
for r in effects:
 if (r['left'],r['right'])in [('G0','G1'),('G2','G3')]and r['metric']in ['factory_invoke_ms','runcontract_ms']:print(r)
