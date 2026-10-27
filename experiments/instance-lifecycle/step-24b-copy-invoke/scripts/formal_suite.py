from pathlib import Path
import json
from run import run,P
from check_pair import local,setup_check
# Gate uses actual successful preflight and retained pilot slots, never measured savings.
gate={}
for c in ['compute','fact','erc721']:
 for label,n in [('preflight-'+c,1),(c+'-b1-p00',2)]:
  o=json.loads((P/'raw_logs'/f'{label}-outcome.json').read_text());assert o['passed']and o['all_owned_processes_stopped']and o['cgroup_empty'];local(label,n);assert setup_check(label)==1
 gate[c]=True
(P/'audit/formal-extension-gate.json').write_text(json.dumps({'preflights_and_pilots_passed':gate,'process_pair_budget':2,'sustained_store_budget_increased':False,'same_guard_limits':True},indent=2))
for b in range(1,4):
 for slot in range(15):
  names=['compute','fact','erc721'];offset=(slot+b-1)%3;names=names[offset:]+names[:offset]
  for c in names:
   label=f'{c}-b{b}-p{slot:02d}'
   o=run(label,c,pairs=2,phase='formal',batch=b,slot=slot,seed=22003+(slot+b-1)%2,module_first='A0'if(slot+b-1)%2==0 else'A1')
   local(label,2);assert setup_check(label)==1
  (P/'audit/suite-checkpoint.json').write_text(json.dumps({'batch':b,'slot_completed':slot,'next_action':'next registered slot only if no STOP','all_prior_semantics_checked':True},indent=2))
 with(P/'PROGRESS.md').open('a')as f:f.write(f'\n正式批{b}完成：每合约15进程×2对，逐对语义/真实init一致，资源包络及进程终结通过；未依据耗时筛选样本。\n')
print('REGISTERED CORE SUITE COMPLETE',flush=True)
