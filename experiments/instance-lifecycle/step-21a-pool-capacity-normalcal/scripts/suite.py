"""Resume completed attempts; no invisible long-running worker, stop globally on guard/failure."""
from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parent.parent
if (ROOT/'STOP.json').exists():raise SystemExit('STOP retained: inspect PROGRESS.md, no tests launched')
# Safe real-guest diagnostics first. Changed inventory/pacing is explicitly NOT primary data.
for method in ['bigNumCal','normalCal']:
 for pool in ['original','capacity']:
  for policy in ['R0','R1']:
    cmd=[sys.executable,'-B',str(ROOT/'scripts/run.py'),'--pool',pool,'--policy',policy,'--method',method,'--phase','isolated','--n','3']
    r=subprocess.run(cmd);print('completed diagnostic',method,pool,policy,flush=True)
    if r.returncode:raise SystemExit('STOP: diagnostic unsafe/failed')
# Original empty-pool strategy preflight. Any failed safety condition stops ALL related execution.
for method in ['bigNumCal','normalCal']:
 for pool in ['original','capacity']:
  for policy in ['R0','R1']:
    r=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/run.py'),'--pool',pool,'--policy',policy,'--method',method,'--phase','preflight','--n','3'])
    if r.returncode:raise SystemExit('STOP: original strategy unsafe/failed; formal not launched')
for method in ['bigNumCal','normalCal']:
 for batch,order in [('a',['R0','R1']),('b',['R1','R0']),('c',['R0','R1'])]:
  for pool in (['original','capacity'] if batch!='b' else ['capacity','original']):
   for policy in order:
    r=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/run.py'),'--pool',pool,'--policy',policy,'--method',method,'--phase','formal','--batch',batch,'--n','100'])
    if r.returncode:raise SystemExit('STOP formal: guard/resource/lifecycle failure')
