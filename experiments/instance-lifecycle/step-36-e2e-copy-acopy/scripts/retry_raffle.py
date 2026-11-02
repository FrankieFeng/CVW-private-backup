from pathlib import Path
import subprocess,os,json,sys
from parity import check
P=Path(__file__).resolve().parents[1];case='raffle_raffle';groups=['G0','G1','G2','G3'];orders=[groups,['G2','G3','G0','G1'],['G1','G0','G3','G2']]
for b in range(4):
 phase='precheck'if b==0 else'formal';paths=[]
 for g in(groups if b==0 else orders[b-1]):
  label='r1-'+case+'-b'+str(b)+'-'+g;out=P/'raw_logs'/f'{label}-case.json'
  if not out.exists():
   with(P/'raw_logs'/f'{label}-driver.log').open('w')as f:z=subprocess.run([sys.executable,str(P/'scripts/case_run.py'),label,case,g,phase,str(b)],env=dict(os.environ,STEP36_HOME='/tmp/cvw-step36-'+label),stdout=f,stderr=subprocess.STDOUT)
   print(label,z.returncode,flush=True)
   if z.returncode:raise RuntimeError('retry failed; retain and stop '+label)
  paths.append(out)
 paths.sort(key=lambda p:json.loads(p.read_text())['group']);z=check(paths,'r1-raffle-b'+str(b));assert z['passed'],z
 cs=json.loads((P/'inputs/cases.json').read_text());cs[case].update(status='READY'if b==0 else'PASSED'if b==3 else'READY',reason='revision1 actual3draw sequence correct, old failure retained',actual_batches=b,actual_per_group=b*3);(P/'inputs/cases.json').write_text(json.dumps(cs,indent=2))
 with(P/'PROGRESS.md').open('a')as f:f.write('\nRaffle revision1 batch'+str(b)+' all4groups PASS, receipts/state/gas parity.\n')
