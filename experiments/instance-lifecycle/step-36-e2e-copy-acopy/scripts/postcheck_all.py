from pathlib import Path
import json,subprocess,sys,os
P=Path(__file__).resolve().parents[1];seen=set();allpaths=[]
for p in sorted((P/'raw_logs').glob('*-case.json')):
 x=json.loads(p.read_text())
 if x['phase']=='formal'and x['batch']==3 and x['passed']:allpaths.append((p,x))
for p,x in allpaths:
 label='post-'+x['case']+'-'+x['group'];out=P/'raw_logs'/f'{label}-postcheck.json';contract=x['records'][-1]['row']['input']['Contract'];key=(contract,x['group']);probe='empty-raffle'if x['case']=='raffle_raffle'else'missing-export'if key not in seen else'none'
 if out.exists():assert json.loads(out.read_text())['passed'];seen.add(key);continue
 if(P/'STOP_SHARED.json').exists():raise RuntimeError('shared stop retained')
 h='/tmp/cvw-step36-'+x['label'];print('POST START',label,probe,flush=True)
 with(P/'raw_logs'/f'{label}-driver.log').open('w')as f:r=subprocess.run([sys.executable,str(P/'scripts/postcheck.py'),label,str(p),probe],env=dict(os.environ,STEP36_HOME=h),stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:print((P/'raw_logs'/f'{label}-driver.log').read_text()[-1200:]);raise RuntimeError('postcheck failed '+label)
 seen.add(key)
print('POST ALL PASS',len(allpaths),flush=True)
