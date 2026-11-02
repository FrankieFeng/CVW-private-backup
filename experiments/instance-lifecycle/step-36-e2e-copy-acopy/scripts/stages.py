"""Post-hoc node-process monotonic event correlation; no new instrumentation."""
from pathlib import Path
import csv,json,collections
P=Path(__file__).resolve().parents[1]
T=[x for x in csv.DictReader((P/'RAW_TRANSACTIONS.csv').open())if x['valid_main']=='True'];events={};rows=[]
for t in T:
 run=t['run']
 if run not in events:
  events[run]=[json.loads(l[8:])for l in(P/'raw_logs'/f'{run}-node.log').read_text().splitlines()if l.startswith('STEP35C ')]
 es=events[run];tx=t['tx_id'];h=int(t['block_height']);same=[x for x in es if x.get('tx_id')==tx];out={k:t[k]for k in ['run','case','group','batch','slot','tx_id','block_height']}
 def stamp(name,ee):
  a=[x['mono_ns']for x in ee if x['event']==name]
  return a[0]if len(a)==1 else None
 a=stamp('rpc_tx_begin',same);b=stamp('rpc_tx_end',same);c=stamp('put_begin',[x for x in es if x.get('height')==h]);d=stamp('put_end',[x for x in es if x.get('height')==h]);v=[x for x in same if x['event']=='vm_invoke_begin'and x.get('depth')==0];ve=[x for x in same if x['event']=='vm_invoke_end'and x.get('depth')==0]
 out.update(node_rpc_start_mono_ns=a,node_rpc_end_mono_ns=b,put_start_mono_ns=c,put_end_mono_ns=d,root_executions=len(v))
 out['put_ms']=(d-c)/1e6 if c is not None and d is not None else None
 out['put_end_to_rpc_end_ms']=(b-d)/1e6 if b is not None and d is not None else None
 out['rpc_begin_to_first_vm_event_ms']=(min(x['mono_ns']for x in v)-a)/1e6 if v and a is not None else None
 out['last_vm_event_to_put_begin_ms']=(c-max(x['mono_ns']for x in ve))/1e6 if ve and c is not None else None
 out['node_rpc_ms']=(b-a)/1e6 if a is not None and b is not None else None
 # Event boundaries include logging; not a decomposition of cross-process SDK duration.
 rows.append(out)
with(P/'NODE_STAGES.csv').open('w',newline='')as f:w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
print('rows',len(rows),'put matched',sum(x['put_ms']is not None for x in rows),'rpc matched',sum(x['node_rpc_ms']is not None for x in rows),'negative residuals',sum(x['last_vm_event_to_put_begin_ms']is not None and x['last_vm_event_to_put_begin_ms']<0 for x in rows))
