from pathlib import Path
import json,subprocess,sys,os
P=Path(__file__).resolve().parents[1]
for case in ['compute_hashCal','bigInput_inputSize']:
 for g in ['E0','E3']:
  assert not(P/'STOP_SHARED.json').exists();source=P/'raw_logs'/f'formal-{case}-b3-{g}-case.json';x=json.loads(source.read_text());assert x['passed'];label=f'restart-{case}-{g}';result=P/'raw_logs'/f'{label}-restart.json'
  if result.exists():assert json.loads(result.read_text())['passed'];continue
  home=Path('/tmp/cvw-step39e-'+x['label']);argv=[sys.executable,str(P/'scripts/restart.py'),label,case,g,str(source)];(P/'evidence'/f'{label}-command.json').write_text(json.dumps({'argv':argv,'home':str(home)},indent=2))
  with(P/'raw_logs'/f'{label}-driver.log').open('w')as out:r=subprocess.run(argv,env=dict(os.environ,STEP36_HOME=str(home),CM39C_DIAGNOSTIC='0'),stdout=out,stderr=subprocess.STDOUT)
  assert r.returncode==0 and json.loads(result.read_text())['passed'],label
  print('DONE',label,flush=True)
