from pathlib import Path
from collections import defaultdict
import csv,json,math,statistics,random
from check_pair import local
P=Path(__file__).resolve().parents[1]
MET=['newinstance_ns','copy_ns','static_init_ns','start_ns','s0_s1_ns','s1_s2_ns','s2_s3_ns','callmethod_ns','export_call_ns','close_ns','invoke_ns']
def write(n,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def q(xs,p):
 a=sorted(xs);i=(len(a)-1)*p;j=int(i);return a[j]+(a[min(j+1,len(a)-1)]-a[j])*(i-j)
def interval(rr,k):
 tree=defaultdict(lambda:defaultdict(list))
 for r in rr:tree[r['batch']][r['label']].append(r[k])
 bs=list(tree);rng=random.Random(270027);samples=[]
 for _ in range(10000):
  x=[]
  for b in rng.choices(bs,k=len(bs)):
   ps=list(tree[b])
   for p in rng.choices(ps,k=len(ps)):x+=tree[b][p]
  samples.append(statistics.median(x))
 return q(samples,.025),q(samples,.975)
timing=[];resources=[];prep=[];pairs=[];correct=[];diag=[];retained=[];targets={};allout=[]
for file in sorted((P/'raw_logs').glob('*-outcome.json')):
 o=json.loads(file.read_text());allout.append(o);label=o['label'];cmd=json.loads((P/'raw_logs'/f'{label}-command.json').read_text());ls=(P/'raw_logs'/f'{label}.log').read_text().splitlines();es=[(i,json.loads(l[7:]))for i,l in enumerate(ls,1)if l.startswith('STEP22 ')];life=[json.loads(l[8:])for l in ls if l.startswith('STEP21C ')];manager=next(x for x in life if x['event']=='manager_closed');owner=o['owner']
 assert o['passed']and o['all_owned_processes_stopped']and o['cgroup_empty']and manager['created']==manager['closed']and owner['managed_objects']==owner['managed_pending']==0
 for _,e in es:
  if e['event']in ['template','module','cache_closed']:prep.append({'label':label,'family':o['family'],'phase':o['phase'],'event':e['event'],**e['data']})
  if e['event']=='retained_instance_closed':retained.append({'label':label,'family':o['family'],'phase':o['phase'],**e['data']})
  if e['event']=='export_diagnostic':diag.append({'label':label,'family':o['family'],'phase':o['phase'],'warm':o['warm'],**e['data']})
 heapmax=max((x['host_after']['host_heap_objects_bytes']for x in o['boundaries']),default=0)
 resources.append({'label':label,'family':o['family'],'left':o['left'],'right':o['right'],'phase':o['phase'],'batch':o['batch'],'rss_peak_mib':o['peak_rss_kib']/1024,'threads_peak':o['peak_threads'],'host_heap_objects_max_mib':heapmax/1048576,'created':manager['created'],'closed':manager['closed'],'owner_managed':owner['managed_objects'],'owner_pending':owner['managed_pending'],'owner_end_threads':owner['Threads'],'owner_end_rss_kib':owner['VmRSS'],'exit':o['systemd']['ExecMainStatus'],'all_stopped':True,'cgroup_empty':True})
 ss=[]
 for line,e in es:
  if e['event']!='sample':continue
  s=e['data'];assert s['code']==0 and s['call_error_observed']=='<nil>';target=s['method']=='normalCal'and s['pair_slot']>=0
  if s['reused']:assert s['group']=='R0'and s['newinstance_ns']==s['copy_ns']==s['start_ns']==s['close_ns']==0 and s['managed_call_begin']==s['managed_call_end']
  else:
   assert s['uses_before']==0
   if s['policy']=='R1':assert s['managed_before']==s['managed_after']
  bound=next((b for b in o['boundaries']if b['pair']==s['pair_slot']and b['role']==s['role']),{})if target else{}
  before=bound.get('host_before',{});after=bound.get('host_after',{});lower=upper=0.;pauses=0
  if bound:
   counts=[b-a for a,b in zip(before['host_gc_pause_counts'],after['host_gc_pause_counts'])];assert all(x>=0 for x in counts)
   buckets=[float(x)for x in after['host_gc_pause_buckets_seconds']]
   for j,n in enumerate(counts):
    if not n:continue
    pauses+=n;lower+=max(0,buckets[j])*n;upper+=buckets[j+1]*n
  row={'label':label,'family':o['family'],'phase':o['phase'],'batch':o['batch'],'process_slot':o['slot'],'module_first':o['module_first'],'is_target':target,'source_log_line':line,'binary_sha':cmd['binary_sha256'],**s,'static_init_ns':s['newinstance_ns']+s['copy_ns'],'s0_s1_ns':s['to_s1_ns'],'s1_s2_ns':s['to_s2_ns']-s['to_s1_ns'],'s2_s3_ns':s['to_s3_ns']-s['to_s2_ns'],'host_gc_cycles_outer':after.get('host_gc_cycles',0)-before.get('host_gc_cycles',0)if bound else'','host_gc_pause_events_outer':pauses if bound else'','host_gc_pause_lower_ns':lower*1e9 if bound else'','host_gc_pause_upper_ns':upper*1e9 if bound and math.isfinite(upper)else'','host_heap_objects_after':after.get('host_heap_objects_bytes',''),'rss_after_kib':bound.get('VmRSS',''),'threads_after':bound.get('Threads',''),'guest_gc':'not_observed'}
  assert row['s1_s2_ns']>=0 and row['s2_s3_ns']>=0;timing.append(row)
  if target:targets[label,s['pair_slot'],s['role']]=row;ss.append(row)
 shared=(o['left'],o['right'])==('R0','R1')
 if shared:assert len({s['store_id']for s in ss})==len({s['module_id']for s in ss})==1
 else:assert len({s['store_id']for s in ss})==2
 for i,check in enumerate(local(label,o['pairs'])):
  a=targets[label,i,'A0'];b=targets[label,i,'A1'];assert a['gas']==b['gas']==check['gas']
  correct.append({'label':label,'family':o['family'],'phase':o['phase'],'batch':o['batch'],'pair':i,'left':o['left'],'right':o['right'],'same_store_module':shared,'left_instance':a['instance_id'],'right_instance':b['instance_id'],**check,'table_identity':'not_tested','exceptions':'not_tested'})
  r={'label':label,'family':o['family'],'phase':o['phase'],'left':o['left'],'right':o['right'],'batch':o['batch'],'slot':o['slot'],'pair':i,'first':'A0'if(i+o['first'])%2==0 else'A1','module_first':o['module_first'],'shared_store_module':shared,'left_uses_before':a['uses_before'],'right_uses_before':b['uses_before']}
  for k in MET:r['left_'+k+'_ms']=a[k]/1e6;r['right_'+k+'_ms']=b[k]/1e6;r[k+'_saving_ms']=(a[k]-b[k])/1e6
  r['export_and_invoke_sign_agree']=(r['export_call_ns_saving_ms']>0)==(r['invoke_ns_saving_ms']>0);pairs.append(r)
effects=[];batch=[];orders=[];byprior=[];summary=[]
formal=[r for r in pairs if r['phase']=='formal']
for fam,a,b in sorted({(r['family'],r['left'],r['right'])for r in formal}):
 rr=[r for r in formal if(r['family'],r['left'],r['right'])==(fam,a,b)]
 for k in MET:
  key=k+'_saving_ms';lo,hi=interval(rr,key);ds=[r[key]for r in rr];effects.append({'family':fam,'left':a,'right':b,'metric':k,'n_pairs':len(rr),'batches':len({r['batch']for r in rr}),'processes':len({r['label']for r in rr}),'left_median_ms':statistics.median(r['left_'+k+'_ms']for r in rr),'left_p95_ms':q([r['left_'+k+'_ms']for r in rr],.95),'right_median_ms':statistics.median(r['right_'+k+'_ms']for r in rr),'right_p95_ms':q([r['right_'+k+'_ms']for r in rr],.95),'paired_saving_median_ms':statistics.median(ds),'ci95_low_ms':lo,'ci95_high_ms':hi,'positive_pairs':sum(x>0 for x in ds),'positive_fraction':sum(x>0 for x in ds)/len(ds),'export_invoke_sign_agree_pairs':sum(r['export_and_invoke_sign_agree']for r in rr),'ci_method':'hierarchical batch/process;10000;seed270027;median;linear P95'})
  if k not in ['export_call_ns','invoke_ns']:continue
  for bb in sorted({r['batch']for r in rr}):
   sub=[r for r in rr if r['batch']==bb];batch.append({'family':fam,'left':a,'right':b,'metric':k,'batch':bb,'n_pairs':len(sub),'saving_median_ms':statistics.median(r[key]for r in sub),'positive_pairs':sum(r[key]>0 for r in sub)})
  for factor in ['first','module_first','pair']:
   if factor=='module_first'and(a,b)==('R0','R1'):continue
   for val in sorted({r[factor]for r in rr}):
    sub=[r for r in rr if r[factor]==val];l,h=interval(sub,key);orders.append({'family':fam,'left':a,'right':b,'metric':k,'factor':factor,'value':val,'n_pairs':len(sub),'saving_median_ms':statistics.median(r[key]for r in sub),'ci95_low_ms':l,'ci95_high_ms':h})
for n,rs in [('TIMING.csv',timing),('PAIRED_SAMPLES.csv',pairs),('PAIRED_EFFECTS.csv',effects),('BATCH_EFFECTS.csv',batch),('ORDER_SENSITIVITY.csv',orders),('RESOURCE_SUMMARY.csv',resources),('CORRECTNESS.csv',correct),('MODULE_PREPARATION.csv',prep),('EXPORT_DIAGNOSTICS.csv',diag),('RETAINED_CLOSE.csv',retained)]:write(n,rs)
v={'processes':len(allout),'all_passed':all(o['passed']for o in allout),'all_stopped':True,'formal_pairs':len(formal),'preflight_pairs':sum(r['phase']=='preflight'for r in pairs),'diagnostic_pairs':sum(r['phase']=='diagnostic'for r in pairs),'semantic_pairs':len(correct),'max_rss_mib':max(r['rss_peak_mib']for r in resources),'max_threads':max(r['threads_peak']for r in resources),'max_host_heap_objects_mib':max(r['host_heap_objects_max_mib']for r in resources),'guest_gc':'not_observed','original_C2':'blocked_unavailable_matching_A','Table_identity':'not_tested'}
(P/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
