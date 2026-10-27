import json,csv,statistics as st
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def within(x,y):return x['begin_ns']>=y['begin_ns']and x['end_ns']<=y['end_ns']
def duration(x):return x['end_ns']-x['begin_ns']
def extract(label):
 text=(P/'raw_logs'/f'{label}.log').read_text();rows=[json.loads(s[7:])for s in text.splitlines()if s.startswith('STEP29 ')];assert len(rows)==1;sp=rows[0]
 root=next(x for x in sp if x['kind']=='invoke'and x['contract']=='exchange'and x['method']=='buyNow');export=next(x for x in sp if x['kind']=='export'and x['contract']=='exchange'and x['method']=='buyNow');assert within(export,root)
 children=sorted([x for x in sp if x['kind']=='invoke'and x['depth']==1 and within(x,export)],key=lambda x:x['begin_ns']);assert len(children)==6 and all(a['end_ns']<=b['begin_ns']for a,b in zip(children,children[1:]))
 syscalls=[x for x in sp if x['kind']=='syscall'and x['depth']==0 and within(x,export)];syscalls.sort(key=lambda x:x['begin_ns']);assert all(a['end_ns']<=b['begin_ns']for a,b in zip(syscalls,syscalls[1:]))
 childsum=sum(map(duration,children));syssum=sum(map(duration,syscalls));assert childsum<=syssum<=duration(export)
 metrics={'root_export_ns':duration(export),'children_invoke_sum_ns':childsum,'root_export_residual_ns':duration(export)-childsum,'root_syscall_sum_ns':syssum,'root_syscall_excluding_child_ns':syssum-childsum,'outside_observed_root_syscall_ns':duration(export)-syssum}
 for kind in ['cross_get_gas','cross_set_gas','cross_core','cross_wacsi']:
  metrics[kind+'_ns']=sum(duration(x)for x in sp if x['kind']==kind and x['depth']==0 and within(x,export))
 # Host diagnostic JSON/output outside child Invoke but within root export, not Guest JSON.
 for kind in ['json_encode_STEP22','json_encode_STEP21C','stdout_STEP22','stdout_STEP21C','manager_logger_infof','manager_logger_debugf','fixture_bytecode_clone','fixture_contract_metadata']:
  metrics[kind+'_outside_child_ns']=sum(duration(x)for x in sp if x['kind']==kind and within(x,export)and not any(within(x,c)for c in children))
 wacsi=[x for x in sp if x['kind']=='cross_wacsi'and x['depth']==0 and within(x,export)];detail=[]
 for i,c in enumerate(children,1):
  w=[x for x in wacsi if within(c,x)];assert len(w)==1;w=w[0]
  detail.append(dict(call_index=i,contract=c['contract'],method=c['method'],prepare_before_child_ns=c['begin_ns']-w['begin_ns'],bytecode_clone_before_child_ns=sum(duration(x)for x in sp if x['kind']=='fixture_bytecode_clone'and x['begin_ns']>=w['begin_ns']and x['end_ns']<=c['begin_ns']),child_invoke_ns=duration(c),return_after_child_ns=w['end_ns']-c['end_ns']))
 metrics['cross_prepare_sum_ns']=sum(x['prepare_before_child_ns']for x in detail);metrics['cross_return_sum_ns']=sum(x['return_after_child_ns']for x in detail)
 metrics['cross_no_child_wacsi_ns']=sum(duration(w)for w in wacsi if not any(within(c,w)for c in children))
 metrics['final_get_gas_ns']=sum(duration(x)for x in sp if x['kind']=='final_get_gas'and x['depth']==0 and within(x,root))
 return metrics,detail,sp
if __name__=='__main__':
 result={}
 for g in ['G0','G1','G2']:
  label='preflight-b1-s01-trace-'+g;m,c,s=extract(label);result[g]=dict(metrics=m,children=c,spans=len(s));print(g,{k:round(v/1e6,3)for k,v in m.items()})
 (P/'audit/preflight-span-check.json').write_text(json.dumps(result,indent=2)+'\n')
