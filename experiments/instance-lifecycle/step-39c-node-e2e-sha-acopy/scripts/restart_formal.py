from pathlib import Path
import json,os,subprocess,sys
P=Path(__file__).resolve().parents[1]
for path in sorted((P/'raw_logs').glob('formal-*-case.json')):
 x=json.loads(path.read_text());assert x['passed'];label='restart-'+x['label'];out=P/'raw_logs'/f'{label}-postcheck.json'
 if out.exists():assert json.loads(out.read_text())['passed'];continue
 assert not(P/'STOP_SHARED.json').exists()
 home='/tmp/cvw-step39c-'+x['label'];cmd=[sys.executable,str(P/'scripts/postcheck.py'),label,str(path),'none'];(P/'audit'/f'{label}-orchestration.json').write_text(json.dumps({'argv':cmd,'home':home}));r=subprocess.run(cmd,env=dict(os.environ,STEP36_HOME=home));assert r.returncode==0,label
