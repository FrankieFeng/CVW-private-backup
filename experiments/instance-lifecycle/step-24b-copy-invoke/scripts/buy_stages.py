from pathlib import Path
import csv,json
P=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((P/'BUY_NOW_STAGES.csv').open()));detail=[];total=[]
for phase in ['preflight','formal']:
 for batch in sorted(set(int(r['batch'])for r in rows if r['phase']==phase)):
  groups={v:sorted([r for r in rows if r['phase']==phase and int(r['batch'])==batch and r['variant']==v],key=lambda r:int(r['instance_id']))for v in ['A0','A1']}
  if not all(groups.values()):continue
  assert all(len(x)==7 for x in groups.values())
  for seq,(a,b)in enumerate(zip(groups['A0'],groups['A1'])):
   assert(a['contract'],a['method'],a['depth'])==(b['contract'],b['method'],b['depth'])
   detail.append(dict(phase=phase,batch=batch,call_sequence=seq,contract=a['contract'],method=a['method'],depth=a['depth'],A0_wasi_ms=int(a['wasi_imports_ns'])/1e6,A1_wasi_ms=int(b['wasi_imports_ns'])/1e6,wasi_saving_ms=(int(a['wasi_imports_ns'])-int(b['wasi_imports_ns']))/1e6,static_init_saving_ms=(int(a['newinstance_ns'])+int(a['copy_ns'])-int(b['newinstance_ns'])-int(b['copy_ns']))/1e6,A0_invoke_ms=int(a['invoke_ns'])/1e6,A1_invoke_ms=int(b['invoke_ns'])/1e6))
  a,b=groups['A0'],groups['A1']
  def diff_metric(key,items):return(sum(int(x[key])for x in items[0])-sum(int(x[key])for x in items[1]))/1e6
  full=(int(a[0]['invoke_ns'])-int(b[0]['invoke_ns']))/1e6
  static=diff_metric('newinstance_ns',(a,b))+diff_metric('copy_ns',(a,b));wasi=diff_metric('wasi_imports_ns',(a,b));start=diff_metric('start_ns',(a,b));initialize=diff_metric('wasi_initialize_ns',(a,b));close=diff_metric('close_ns',(a,b))
  total.append(dict(phase=phase,batch=batch,full_invoke_saving_ms=full,all7_static_init_saving_ms=static,all7_wasi_imports_saving_ms=wasi,root_wasi_imports_saving_ms=diff_metric('wasi_imports_ns',(a[:1],b[:1])),six_child_wasi_imports_saving_ms=diff_metric('wasi_imports_ns',(a[1:],b[1:])),all7_start_saving_ms=start,all7_wasi_initialize_saving_ms=initialize,all7_close_saving_ms=close,other_disjoint_residual_saving_ms=full-static-wasi-start-initialize-close,note='Only root full Invoke; sum7 only disjoint creation/start/close phases, never sum nested Invoke/CallMethod'))
def write(name,rs):
 with(P/name).open('w',newline='')as f:
  w=csv.DictWriter(f,rs[0].keys());w.writeheader();w.writerows(rs)
write('BUY_NOW_STAGE_EFFECTS.csv',detail);write('BUY_NOW_DECOMPOSITION.csv',total)
print(json.dumps(total,indent=2))
