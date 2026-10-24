"""Step-21 bounded TestInvoke runner; each condition is a fresh process."""
from pathlib import Path
import argparse
import base64
import json
import os
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
VM = Path('/home/frankie/mygitprojects/.worktrees/cvw-step21/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0')


def semantic_success(case, sample, params):
    if sample['code'] != 0:
        return False
    data = base64.b64decode(sample.get('result') or '').decode(errors='replace')
    method = case['method']
    if method == 'bigNumCal':
        return data == 'success bigNumCal: 607723520'
    if method == 'normalCal':
        return data == 'success normalCal: 666'
    if method == 'hashCal':
        import hashlib
        return data == 'success hashCal '+hashlib.sha256(b'ChainMaker Performance Test').hexdigest()
    if method == 'mint':
        return data == 'mint success'
    if method == 'buyNow':
        return data == 'buyNow success'
    if method == 'saveAndFindByFileHash':
        try:
            r = json.loads(data)
            return r.get('fileHash') == params['file_hash'] and r.get('fileName') == params['file_name'] and str(r.get('time')) == params['time']
        except (ValueError, AttributeError):
            return False
    return False


def run(case, batch, policy, n, race=False):
    label = f'{case["case"]}-{batch}-{policy.lower()}'
    log = ROOT/'raw_logs'/(label+'.log')
    assert not log.exists(), 'refuse overwrite'
    unit = 'step21-'+label.lower()
    binary = ROOT/('step21-race.test' if race else 'step21.test')
    # Reusing stored preflight results with another binary must never be silent.
    import hashlib
    environment = json.loads((ROOT/'environment.json').read_text())
    expected = environment.get('race_binary_sha256' if race else 'normal_binary_sha256')
    if expected:
        assert hashlib.sha256(binary.read_bytes()).hexdigest() == expected, 'binary changed: use a new experiment record'
    assert hashlib.sha256(Path(case['wasm_path']).read_bytes()).hexdigest() == case['wasm_sha256']
    assert hashlib.sha256(Path(case['inputs_file']).read_bytes()).hexdigest() == case['inputs_sha256']
    cmd = ['systemd-run', '--user', '--collect', '--unit='+unit, '--working-directory='+str(VM),
           '-p', 'MemoryMax=2G', '-p', 'TasksMax=256', '-p', 'RuntimeMaxSec=60s',
           '-p', 'TimeoutStopSec=5s', '-p', 'KillMode=control-group', '-p', 'RemainAfterExit=yes',
           '-p', 'StandardOutput=append:'+str(log), '-p', 'StandardError=inherit',
           '--setenv=CM_REUSE_EXPERIMENT='+policy, '--setenv=CM_STEP21_OBSERVE=1',
           '--setenv=GOMAXPROCS=4', '--setenv=GOGC=100', '--setenv=GORACE=halt_on_error=1 exitcode=66',
           '--setenv=LD_LIBRARY_PATH='+str(VM/'wasmer-go/packaged/lib/linux-amd64'),
           str(binary), '-test.run=^TestInvoke$', '-test.v', '-test.count=1', '-test.timeout=45s',
           '-invoke_contract_name='+case['contract'], '-invoke_contract_method='+case['method'],
           '-invoke_contract_type=go', '-invoke_test_time='+str(n), '-step21_inputs='+case['inputs_file']]
    (ROOT/'raw_logs'/(label+'-command.json')).write_text(json.dumps(cmd, indent=2)+'\n')
    started = subprocess.run(cmd, capture_output=True, text=True)
    assert started.returncode == 0, started.stderr
    begin = time.monotonic()
    samples, last, pid, reason = [], {}, 0, ''
    try:
        while time.monotonic()-begin < 65:
            show = subprocess.run(['systemctl', '--user', 'show', unit, '-p', 'MainPID', '-p', 'SubState',
                                   '-p', 'ActiveState', '-p', 'ExecMainStatus', '-p', 'Result', '-p', 'MemoryPeak',
                                   '-p', 'CPUUsageNSec', '-p', 'ControlGroup'], capture_output=True, text=True).stdout
            last = dict(s.split('=', 1) for s in show.splitlines() if '=' in s)
            pid = int(last.get('MainPID', '0'))
            path = Path(f'/proc/{pid}/status')
            if pid and path.exists():
                row = dict(mono_ns=time.monotonic_ns(), pid=pid)
                try:
                    for s in path.read_text().splitlines():
                        k, _, v = s.partition(':')
                        if k in ['VmRSS', 'VmHWM', 'VmSize', 'Threads']:
                            row[k] = int(v.split()[0])
                    stat = Path(f'/proc/{pid}/stat').read_text().split()
                    row['cpu_ticks'] = int(stat[13])+int(stat[14])
                    samples.append(row)
                except FileNotFoundError:
                    pass
                if row.get('VmRSS', 0) > 1536*1024 or row.get('Threads', 0) > 220:
                    reason = 'resource_threshold'
                    break
            if last.get('SubState') == 'exited' or last.get('ActiveState') in ['inactive', 'failed']:
                reason = 'process_exited'
                break
            time.sleep(.03)
        else:
            reason = 'external_timeout'
    finally:
        subprocess.run(['systemctl', '--user', 'stop', unit], capture_output=True, timeout=10)
        assert not pid or not Path(f'/proc/{pid}').exists(), 'owned process remains'
        (ROOT/'raw_logs'/(label+'-resources.jsonl')).write_text(''.join(json.dumps(x)+'\n' for x in samples))
        text = log.read_text(errors='replace') if log.exists() else ''
        events = [json.loads(s[7:]) for s in text.splitlines() if s.startswith('STEP21 ')]
        calls = [r for r in events if r['event'] == 'sample']
        inputs = json.loads(Path(case['inputs_file']).read_text())
        valid = sum(semantic_success(case, r, inputs[r['index']]) for r in calls)
        race_detected = 'WARNING: DATA RACE' in text
        safe = reason == 'process_exited' and last.get('ExecMainStatus') == '0' and not race_detected
        safe = safe and any(r['event'] == 'closed' and r.get('worker_exited') for r in events)
        safe = safe and '--- PASS: TestInvoke' in text and '--- FAIL: TestInvoke' not in text
        safe = safe and 'fatal error:' not in text and 'panic:' not in text
        outcome = dict(label=label, case=case['case'], batch=batch, policy=policy, requested=n, race=race,
                       observed_calls=len(calls), semantic_successes=valid, raw_code_zero=sum(r['code'] == 0 for r in calls),
                       execution_safe_observed=safe, lifecycle_closed=any(r['event'] == 'closed' for r in events),
                       reason=reason, race_detected=race_detected, systemd=last, all_owned_processes_stopped=True,
                       wall_s=time.monotonic()-begin,
                       rss_sample_peak_mib=max([r.get('VmRSS', 0) for r in samples] or [0])/1024,
                       threads_sample_peak=max([r.get('Threads', 0) for r in samples] or [0]),
                       native_store_safety='unproved; Go race and bounded success are not a native safety certification')
        (ROOT/'raw_logs'/(label+'-outcome.json')).write_text(json.dumps(outcome, indent=2)+'\n')
        print(json.dumps(outcome), flush=True)
    return outcome


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--case', required=True)
    p.add_argument('--batch', required=True)
    p.add_argument('--policy', choices=['R0', 'R1'], required=True)
    p.add_argument('--n', type=int, required=True)
    p.add_argument('--race', action='store_true')
    a = p.parse_args()
    c = next(c for c in json.loads((ROOT/'cases.json').read_text()) if c['case'] == a.case)
    r = run(c, a.batch, a.policy, a.n, a.race)
    if not r['execution_safe_observed']:
        raise SystemExit(2)
    if r['semantic_successes'] != a.n:
        raise SystemExit(3)
