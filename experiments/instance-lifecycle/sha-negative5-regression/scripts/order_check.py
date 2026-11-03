"""One bounded reverse-order diagnostic, never merged into the three primary batches."""
from pathlib import Path
import subprocess,json,sys,os
P=Path(__file__).resolve().parents[1]
for g in ['G3','G4']:
 assert not(P/'STOP_SHARED.json').exists();label='ordercheck-raffle-'+g;out=P/'raw_logs'/f'{label}-case.json'
 if out.exists():assert json.loads(out.read_text())['passed'];continue
 home=Path('/tmp/cvw-shaneg5-'+label);cmd=[sys.executable,str(P/'scripts/case.py'),label,'raffle_raffle',g,'ordercheck','4'];(P/'audit'/f'{label}-orchestration.json').write_text(json.dumps({'argv':cmd,'home':str(home),'order':'G3 then G4','scope':'supplementary,6transactions,excluded from main3batchstatistics'},indent=2))
 with(P/'raw_logs'/f'{label}-driver.log').open('w')as f:r=subprocess.run(cmd,env=dict(os.environ,STEP36_HOME=str(home),CM39C_DIAGNOSTIC='0'),stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0 and json.loads(out.read_text())['passed'];print('DONE',label,flush=True)
from correctness import compare
assert compare([P/'raw_logs'/f'ordercheck-raffle-{g}-case.json'for g in ['G3','G4']])
