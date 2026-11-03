from pathlib import Path
import subprocess,json,os,sys
P=Path(__file__).resolve().parents[1]
def run(script,args,home):
 label=args[0];kind='seed'if script=='seed.py'else'case';result=P/'raw_logs'/f'{label}-{kind}.json'
 if result.exists():assert json.loads(result.read_text())['passed'];return
 assert not(P/'STOP_SHARED.json').exists();env=dict(os.environ,STEP36_HOME=str(home),CM39C_DIAGNOSTIC='0');argv=[sys.executable,str(P/'scripts'/script)]+args;(P/'evidence'/f'{label}-command.json').write_text(json.dumps({'argv':argv,'home':str(home),'extra_env':{'CM39C_DIAGNOSTIC':'0'}},indent=2))
 with(P/'raw_logs'/f'{label}-driver.log').open('w')as f:r=subprocess.run(argv,env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0 and json.loads(result.read_text())['passed'],label
 print('DONE',label,flush=True)
if sys.argv[1]=='seeds':
 for c in ['compute','bigInput']:
  for fl in ['plain','A']:run('seed.py',[f'seed-{c}-{fl}',c,fl],Path(f'/tmp/cvw-step39e-seed-{c}-{fl}'))
elif sys.argv[1]=='validate':
 for b,c in enumerate(['compute_hashCal','bigInput_inputSize','compute_hashCal'],1):
  label=f'validate-b{b}-{c}';run('run_case.py',[label,c,'E0','validation',str(b)],Path('/tmp/cvw-step39e-'+label))
 proof={'passed':True,'independent_startups':3,'formal_already_executed':len(list((P/'raw_logs').glob('formal-*-case.json')))};assert proof['formal_already_executed']==0;(P/'VALIDATION_GATE.json').write_text(json.dumps(proof,indent=2))
elif sys.argv[1]=='formal':
 assert json.loads((P/'VALIDATION_GATE.json').read_text())['passed']
 for b in [1,2,3]:
  for i,c in enumerate(['compute_hashCal','bigInput_inputSize']):
   order=['E0','E3']if(b+i)%2 else['E3','E0']
   for g in order:
    label=f'formal-{c}-b{b}-{g}';run('run_case.py',[label,c,g,'formal',str(b)],Path('/tmp/cvw-step39e-'+label))
