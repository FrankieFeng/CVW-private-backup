from pathlib import Path
import os,sys,json,subprocess
P=Path(__file__).resolve().parents[1]
def command(script,args,home,diag=False):
 label=args[0];kind='seed'if script=='seed.py'else'case';result=P/'raw_logs'/f'{label}-{kind}.json'
 if result.exists():assert json.loads(result.read_text())['passed'];return
 assert not(P/'STOP_SHARED.json').exists(),'infrastructure gate failed; no automatic resume'
 env=dict(os.environ,STEP36_HOME=str(home),CM39C_DIAGNOSTIC='1'if diag else'0');cmd=[sys.executable,str(P/'scripts'/script)]+args;(P/'audit'/f'{label}-orchestration.json').write_text(json.dumps({'argv':cmd,'home':str(home),'diagnostic':diag},indent=2));r=subprocess.run(cmd,env=env);assert r.returncode==0,label
if __name__=='__main__':
 if sys.argv[1]=='seeds':
  for con in ['compute','bigInput','exchange']:
   for fl in ['plain','A']:command('seed.py',[f'seed-{con}-{fl}',con,fl],Path(f'/tmp/cvw-step39c-seed-{con}-{fl}'))
 elif sys.argv[1]=='pre':
  for case in ['compute_hashCal','bigInput_inputSize','exchange_buyNow']:
   for g in ['E0','E1','E2','E3']:
    label=f'pre-{case}-{g}';command('case_run.py',[label,case,g,'precheck','0'],Path('/tmp/cvw-step39c-'+label),True)
 elif sys.argv[1]=='formal':
  assert json.loads((P/'SMOKE_COMPLETE.json').read_text())['passed'],'all smoke checks required'
  orders=[['E0','E1','E2','E3'],['E3','E2','E1','E0'],['E1','E0','E3','E2']]
  for batch in [1,2,3]:
   for j,case in enumerate(['compute_hashCal','bigInput_inputSize','exchange_buyNow']):
    order=orders[batch-1];shift=2*(j%2);order=order[shift:]+order[:shift]
    (P/'audit'/f'order-{case}-b{batch}.json').write_text(json.dumps(order))
    for g in order:
     label=f'formal-{case}-b{batch}-{g}';command('case_run.py',[label,case,g,'formal',str(batch)],Path('/tmp/cvw-step39c-'+label))

    from parity import check
    proof=check([P/'raw_logs'/f'formal-{case}-b{batch}-{g}-case.json'for g in ['E0','E1','E2','E3']],f'formal-{case}-b{batch}')
    assert proof['passed'],'four-group correctness mismatch: stop'
