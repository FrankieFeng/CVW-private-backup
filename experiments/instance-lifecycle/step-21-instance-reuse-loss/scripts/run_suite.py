"""Formal suite: run only semantically valid preflight cases, retain E cases."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
assert not (ROOT/'suite-status.json').exists(), 'preserve prior suite; prepare a new output directory'
cases = json.loads((ROOT/'case-preflight.json').read_text())
records = []
for case in cases:
    if not case.get('preflight_valid'):
        records.append(dict(case=case['case'], state='E_preflight_business_failure', requested_formal=0))
        (ROOT/'suite-status.json').write_text(json.dumps(records, indent=2)+'\n')
        continue
    for policy in ['r0', 'r1']:
        check = json.loads((ROOT/'raw_logs'/f'{case["case"]}-race-smoke-{policy}-outcome.json').read_text())
        assert check['execution_safe_observed'] and check['semantic_successes'] == check['requested']
    method_ok = True
    for batch, order in [('a', ['R0', 'R1']), ('b', ['R1', 'R0']), ('c', ['R0', 'R1'])]:
        for policy in order:
            cmd = [sys.executable, '-B', str(ROOT/'scripts/run.py'), '--case', case['case'],
                   '--batch', batch, '--policy', policy, '--n', '100']
            run = subprocess.run(cmd, capture_output=True, text=True)
            with (ROOT/'formal-driver.log').open('a') as f:
                f.write(run.stdout+run.stderr)
            result = json.loads((ROOT/'raw_logs'/f'{case["case"]}-{batch}-{policy.lower()}-outcome.json').read_text())
            record = dict(case=case['case'], batch=batch, policy=policy, exit=run.returncode,
                          calls=result['observed_calls'], successes=result['semantic_successes'],
                          safe_observed=result['execution_safe_observed'])
            records.append(record)
            (ROOT/'suite-status.json').write_text(json.dumps(records, indent=2)+'\n')
            print(record, flush=True)
            if not result['execution_safe_observed']:
                raise SystemExit('STOP all execution: resource/race/lifecycle/process error')
            if result['semantic_successes'] != 100 or result['observed_calls'] != 100:
                method_ok = False
                break
        if not method_ok:
            break
