"""Recompute completed Step36 data only. Do not run while formal nodes are active."""
from pathlib import Path
import json,csv,re,statistics as st,random,math,hashlib,collections
P=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def q(x,p):
 y=sorted(x);k=(len(y)-1)*p;i=int(k);return y[i]+(y[min(i+1,len(y)-1)]-y[i])*(k-i)
def table(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/name).open('w',newline='')as f:
  if keys:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def events(label):
 log=(P/'raw_logs'/f'{label}-node.log').read_text();vm=[loadline(l[7:])for l in log.splitlines()if l.startswith('STEP35 ')];node=[loadline(l[8:])for l in log.splitlines()if l.startswith('STEP35C ')];outer=[]
 for m in re.finditer(r'REUSE_VM tx=(\S+) contract=(\S+) method=(\S+) begin_ns=(\d+) end_ns=(\d+) code=(\d+) gas=(\d+) depth=(\d+)',log):
  tx,c,method,a,b,code,gas,depth=m.groups();outer.append(dict(tx_id=tx,contract=c,method=method,ns=int(b)-int(a),depth=int(depth),code=int(code)))
 return vm,node,outer
def loadline(s):return json.loads(s)
cases=load(P/'inputs/cases.json');transactions=[];windows=[];resources=[];modules=[];buckets=collections.defaultdict(list);nodeevents=[]
for path in sorted((P/'raw_logs').glob('*-case.json')):
 x=load(path);label=x['label'];vm,ne,outer=events(label);owner=(x.get('node')or{}).get('owner')or{};snap=[e for e in vm if e.get('event')=='resource_snapshot'];heap=[e['go_heap']for e in vm if'go_heap'in e];gor=[e['goroutines']for e in vm if'goroutines'in e]
 z=x.get('node')or{};resources.append(dict(run=label,case=x['case'],group=x['group'],phase=x['phase'],batch=x['batch'],passed=x['passed'],status=x['status'],rss_peak_mib=z.get('peak_rss_kib',0)/1024,threads_peak=z.get('peak_threads'),go_heap_boundary_peak_mib=max(heap)/1024**2 if heap else 'not_recorded',goroutines_snapshot_max=max(gor)if gor else'not_recorded',stores_created=owner.get('stores_created'),stores_closed=owner.get('stores_closed'),instances_created=owner.get('instances_created'),instances_closed=owner.get('instances_closed'),pending=owner.get('managed_pending'),exit_code=(z.get('systemd')or{}).get('ExecMainStatus'),pid_exited=z.get('pid_exited'),cgroup_empty=z.get('cgroup_empty'),diagnostic_stopped=sum(e['event']=='diagnostic_stopped'for e in ne),core_jobs_begin=sum(e['event']=='commit_job_begin'for e in ne),core_jobs_end=sum(e['event']=='commit_job_end'for e in ne),puts_begin=sum(e['event']=='put_begin'for e in ne),puts_end=sum(e['event']=='put_end'for e in ne)))
 for e in vm:
  if e['event']=='module_prepared':modules.append(dict(run=label,**e))
 committed={it['row']['request_id']:it for it in x['records']}
 win=x.get('window');rs=win.get('rows',[])if win else[]
 valid=x['passed']and cases[x['case']]['status']=='PASSED'and x['phase']=='formal';confirmed=0;unique=set();seq=[]
 for i,r in enumerate(rs):
  resp=r.get('response')or{};cr=resp.get('contract_result')or{};tx=resp.get('tx_id');it=committed.get(r['request_id']);root=[e for e in vm if e.get('event')=='invoke_end'and e.get('depth')==0 and e.get('tx_id')==tx];sub=[e for e in vm if e.get('event')=='invoke_end'and e.get('depth',0)>0 and e.get('tx_id')==tx];ou=[e for e in outer if e['tx_id']==tx and e['depth']==0]
  ok=bool(r['success']and it and it['committed']['block_height']==resp.get('tx_block_height')and tx not in unique);unique.add(tx);confirmed+=ok
  row=dict(run=label,case=x['case'],contract=cases[x['case']]['contract'],method=cases[x['case']]['method'],group=x['group'],batch=x['batch'],slot=i,phase=x['phase'],valid_main=valid and ok,success_response=bool(r['success']),confirmed=ok,request_id=r['request_id'],tx_id=tx,block_height=resp.get('tx_block_height'),gas=cr.get('gas_used',0),response_code=resp.get('code',0),contract_code=cr.get('code',0),error=r.get('error',''),sdk_start_mono_ns=r['sdk_start_mono_ns'],sdk_end_mono_ns=r['sdk_end_mono_ns'],sdk_start_wall_ns=r['sdk_start_wall_ns'],sdk_end_wall_ns=r['sdk_end_wall_ns'],e2e_ms=r['elapsed_ns']/1e6,vm_root_invokes=len(root),vm_sub_invokes=len(sub),vm_factory_ms=sum(e['ns']for e in ou)/1e6 if ou else None,vm_inner_ms=sum(e['invoke_ns']for e in root)/1e6 if root else None,newinstance_ms=sum(e.get('newinstance_ns',0)for e in root)/1e6 if root else None,copy_ms=sum(e.get('copy_ns',0)for e in root)/1e6 if root else None,start_ms=sum(e.get('start_ns',0)for e in root)/1e6 if root else None,s0_s1_ms=sum(e.get('s1_ns',0)for e in root)/1e6 if root else None,callmethod_ms=sum(e.get('callmethod_ns',0)for e in root)/1e6 if root else None,close_ms=sum(e.get('close_ns',0)for e in root)/1e6 if root else None,raw_file=str(path))
  transactions.append(row);seq.append(row)
  if row['valid_main']:buckets[(x['case'],x['group'])].append(row)
  for e in root+sub:nodeevents.append(dict(run=label,**e))
 if win:
  assert win['window_start_mono_ns']==rs[0]['sdk_start_mono_ns']and win['window_end_mono_ns']==rs[-1]['sdk_end_mono_ns'];seconds=win['window_ns']/1e9
  windows.append(dict(run=label,case=x['case'],group=x['group'],batch=x['batch'],phase=x['phase'],valid_main=valid,planned=win['planned'],attempted=win['attempted'],successful_responses=win['successful_responses'],confirmed_unique=confirmed,failed=win['attempted']-win['successful_responses'],timeout_count=sum(bool(re.search('timeout|deadline',str(r.get('error',''))+' '+str(r.get('response','')),re.I))for r in rs),start_mono_ns=win['window_start_mono_ns'],end_mono_ns=win['window_end_mono_ns'],window_seconds=seconds,submitted_tps=confirmed/seconds,client_completed_tps=win['successful_responses']/seconds,vm_log_equivalent_tps=sum(r['vm_root_invokes']for r in seq)/(sum(r['vm_factory_ms']for r in seq)/1000)if seq and all(r['vm_factory_ms']is not None and r['vm_factory_ms']>0 for r in seq)else None,full_receipt_verified=confirmed==win['planned']))
stat=[]
metrics=['e2e_ms','vm_factory_ms','vm_inner_ms','newinstance_ms','copy_ms','start_ms','s0_s1_ms','callmethod_ms','close_ms']
for(case,g),rs in sorted(buckets.items()):
 for metric in metrics:
  v=[r[metric]for r in rs if r[metric]is not None]
  if v:stat.append(dict(case=case,group=g,metric=metric,batch='all',N=len(v),independent_batches=len({r['batch']for r in rs}),mean=st.mean(v),median=st.median(v),p50=st.median(v),p95=q(v,.95)))
 for b in sorted({r['batch']for r in rs}):
  v=[r['e2e_ms']for r in rs if r['batch']==b];stat.append(dict(case=case,group=g,metric='e2e_ms',batch=b,N=len(v),independent_batches=1,mean=st.mean(v),median=st.median(v),p50=st.median(v),p95=q(v,.95)))
# Direct paired hierarchical bootstrap: resample batches then slots, all members paired.
effects=[];orderrows=[]
orders=[['G0','G1','G2','G3'],['G2','G3','G0','G1'],['G1','G0','G3','G2']]
for case,cfg in cases.items():
 if cfg['status']!='PASSED':continue
 for left,right in [('G0','G1'),('G1','G2'),('G0','G2'),('G0','G3'),('G3','G2')]:
  a={(r['batch'],r['slot']):r for r in buckets[(case,left)]};b={(r['batch'],r['slot']):r for r in buckets[(case,right)]};assert a.keys()==b.keys()
  for metric in ['e2e_ms','vm_factory_ms','vm_inner_ms','start_ms','s0_s1_ms']:
   if any(a[k][metric]is None or b[k][metric]is None for k in a):continue
   data={k:a[k][metric]-b[k][metric]for k in a};by=collections.defaultdict(list)
   for (batch,slot),v in data.items():by[batch].append(v)
   seed=int(hashlib.sha256((case+left+right+metric).encode()).hexdigest()[:16],16);rng=random.Random(seed);bs=list(by);boots=[]
   for z in range(10000):
    vv=[]
    for batch in rng.choices(bs,k=len(bs)):vv.extend(rng.choices(by[batch],k=len(by[batch])))
    boots.append(st.median(vv))
   med=[st.median(by[batch])for batch in sorted(by)];vals=list(data.values());pct=[100*data[k]/a[k][metric]for k in a if a[k][metric]>0]
   effects.append(dict(case=case,left=left,right=right,metric=metric,N=len(vals),batches=len(by),paired_saving_median=st.median(vals),ci95_low=q(boots,.025),ci95_high=q(boots,.975),positive_fraction=sum(v>0 for v in vals)/len(vals),paired_pct_median=st.median(pct)if pct else'',batch1=med[0],batch2=med[1],batch3=med[2],all_batches_positive=all(v>0 for v in med),bootstrap_seed=seed,bootstrap_draws=10000))
   if metric=='e2e_ms':
    for pos in ['left-first','right-first']:
     vv=[v for(batch,slot),v in data.items()if (orders[batch-1].index(left)<orders[batch-1].index(right))==(pos=='left-first')];orderrows.append(dict(case=case,left=left,right=right,stratum=pos,N=len(vv),median_saving=st.median(vv)if vv else''))
    for s in ['first-slot','later-slots']:
     vv=[v for(batch,slot),v in data.items()if(slot==0)==(s=='first-slot')];orderrows.append(dict(case=case,left=left,right=right,stratum=s,N=len(vv),median_saving=st.median(vv)if vv else''))
table('RAW_TRANSACTIONS.csv',transactions);table('THROUGHPUT.csv',windows);table('STATISTICS.csv',stat);table('PAIRED_EFFECTS.csv',effects);table('ORDER_EFFECTS.csv',orderrows);table('RESOURCE_SUMMARY.csv',resources);table('MODULE_PREPARATION.csv',modules);table('VM_EVENTS.csv',nodeevents)
(P/'audit/recompute.json').write_text(json.dumps({'cases':len(cases),'statuses':dict(collections.Counter(c['status']for c in cases.values())),'all_target_rows':len(transactions),'valid_main_rows':sum(x['valid_main']for x in transactions),'valid_windows':sum(x['valid_main']for x in windows),'CI':'hierarchical batch/slot paired median bootstrap10000, exploratory only3clusters','original_logs_unchanged':True},indent=2));print((P/'audit/recompute.json').read_text())
