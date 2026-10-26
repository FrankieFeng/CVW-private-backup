from pathlib import Path
import subprocess,json,sys
P=Path(__file__).resolve().parents[1]
def run(label,contract,pairs=1,phase='preflight',seed=2200):
 cmd=[sys.executable,'-B',str(P/'scripts/run.py'),label,contract,'--pairs',str(pairs),'--phase',phase,'--seed',str(seed)]
 r=subprocess.run(cmd);assert r.returncode==0,'STOP: inspect retained failure, do not continue'
run('v4-lifecycle','probe',phase='probe')
for c in ['compute','fact']:run('v4-preflight-'+c,c,seed=2201)
for c in ['compute','fact']:
 for batch in range(1,4):run(f'{c}-batch-{batch}',c,pairs=3,phase='formal',seed=22000+batch)
