"""Record or resume the exact Step-21 small-sample checks; never hides failure."""
from pathlib import Path
import json
import hashlib
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
cases=json.loads((ROOT/'cases.json').read_text())
environment=json.loads((ROOT/'environment.json').read_text())
for name,key in [('step21.test','normal_binary_sha256'),('step21-race.test','race_binary_sha256')]:
    if environment.get(key):
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==environment[key], 'changed binary; do not reuse stored checks'
outcomes=[]
for case in cases:
    valid=True
    for policy in ['R0','R1']:
        label=f'{case["case"]}-smoke-{policy.lower()}'
        saved=ROOT/'raw_logs'/(label+'-outcome.json')
        if not saved.exists():
            r=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/run.py'),'--case',case['case'],
                              '--batch','smoke','--policy',policy,'--n','3'],capture_output=True,text=True)
            with (ROOT/'smoke-driver.log').open('a') as f:f.write(r.stdout+r.stderr)
        result=json.loads(saved.read_text())
        outcomes.append(result)
        (ROOT/'preflight-outcomes.json').write_text(json.dumps(outcomes,indent=2)+'\n')
        if not result['execution_safe_observed']:raise SystemExit('STOP: small-sample safety failure')
        valid=valid and result['semantic_successes']==3
    case['preflight_valid']=valid
(ROOT/'case-preflight.json').write_text(json.dumps(cases,indent=2)+'\n')
for case in cases:
    if not case['preflight_valid']:continue
    for policy in ['R0','R1']:
        label=f'{case["case"]}-race-smoke-{policy.lower()}'
        saved=ROOT/'raw_logs'/(label+'-outcome.json')
        if not saved.exists():
            r=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/run.py'),'--case',case['case'],
                              '--batch','race-smoke','--policy',policy,'--n','3','--race'],capture_output=True,text=True)
            with (ROOT/'race-driver.log').open('a') as f:f.write(r.stdout+r.stderr)
        result=json.loads(saved.read_text())
        if not result['execution_safe_observed'] or result['semantic_successes']!=3:
            raise SystemExit('STOP: race/safety/business check failure')
