from pathlib import Path
import subprocess,json,sys,os
P=Path(__file__).resolve().parents[1];METHODS=['identity_address','identity_callerAddress','erc721_balanceOf','erc721_tokenLatestTxInfo','raffle_raffle'];GROUPS=['G0','G1','G2','G3','G4']
def run(script,args,home,kind):
 label=args[0];out=P/'raw_logs'/f'{label}-{kind}.json'
 if out.exists():assert json.loads(out.read_text())['passed'];return
 assert not(P/'STOP_SHARED.json').exists(),'stop marker retained'
 env=dict(os.environ,STEP36_HOME=str(home),CM39C_DIAGNOSTIC='0');cmd=[sys.executable,str(P/'scripts'/script)]+args;(P/'audit'/f'{label}-orchestration.json').write_text(json.dumps({'argv':cmd,'home':str(home)},indent=2))
 with(P/'raw_logs'/f'{label}-driver.log').open('w')as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0 and json.loads(out.read_text())['passed'],label
 print('DONE',label,flush=True)
if sys.argv[1]=='seeds':
 for c in ['identity','erc721','raffle']:
  for fl in ['plain','A']:run('seed.py',[f'seed-v1-{c}-{fl}',c,fl],Path(f'/tmp/cvw-shaneg5-seed-v1-{c}-{fl}'),'seed')
elif sys.argv[1]=='pre':
 for m in METHODS:
  for g in GROUPS:
   label=f'pre-{m}-{g}';run('case.py',[label,m,g,'pre','0'],Path('/tmp/cvw-shaneg5-'+label),'case')
 from correctness import compare
 for m in METHODS:assert compare([P/'raw_logs'/f'pre-{m}-{g}-case.json'for g in GROUPS])
 (P/'SMOKE_GATE.json').write_text(json.dumps({'passed':True,'cases':25,'formal_before_gate':len(list((P/'raw_logs').glob('formal-*-case.json')))},indent=2));assert not list((P/'raw_logs').glob('formal-*-case.json'))
elif sys.argv[1]=='formal':
 assert json.loads((P/'SMOKE_GATE.json').read_text())['passed']
 for b in [1,2,3]:
  for i,m in enumerate(METHODS):
   orders=[GROUPS,list(reversed(GROUPS)),['G2','G4','G1','G3','G0']];order=orders[b-1];shift=i%5;order=order[shift:]+order[:shift];(P/'audit'/f'order-{m}-b{b}.json').write_text(json.dumps(order))
   for g in order:
    label=f'formal-{m}-b{b}-{g}';run('case.py',[label,m,g,'formal',str(b)],Path('/tmp/cvw-shaneg5-'+label),'case')
   from correctness import compare
   assert compare([P/'raw_logs'/f'formal-{m}-b{b}-{g}-case.json'for g in GROUPS]),m
