from pathlib import Path
import json,subprocess,sys,hashlib
P=Path(__file__).resolve().parents[1]
assert json.loads((P/'raw_logs/final-owner-outcome.json').read_text())['passed']
seq=[('final-big-r0','Compute','R0','bigNumCal','3'),('final-big-r1','Compute','R1','bigNumCal','3'),('final-normal-r1','Compute','R1','normalCal','3'),('final-normal-r0','Compute','R0','normalCal','3'),('final-exchange-r1','Exchange','R1','buyNow','1'),('final-exchange-r0','Exchange','R0','buyNow','1')]
for args in seq:
 outcome=P/'raw_logs'/f'{args[0]}-outcome.json'
 if outcome.exists():
  assert json.loads(outcome.read_text())['passed'],'Previous failure: inspect, do not auto retry'
  print('already passed',args[0],flush=True);continue
 if (P/'raw_logs'/f'{args[0]}.log').exists():raise SystemExit('Attempt exists, no outcome; inspect unit before recovery')
 out=P/'audit'/f'{args[0]}-driver.log'
 with out.open('w')as f:r=subprocess.run([sys.executable,'-B',str(P/'scripts/run.py'),*args],stdout=f,stderr=subprocess.STDOUT)
 print(args[0],outcome.read_text() if outcome.exists()else out.read_text()[-1000:],flush=True)
 if r.returncode:raise SystemExit('Safety stop after '+args[0])
