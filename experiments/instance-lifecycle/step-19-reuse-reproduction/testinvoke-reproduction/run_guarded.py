"""Run one unchanged TestInvoke process with cgroup/resource/race stop guards."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import time


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--label', required=True)
    p.add_argument('--policy', choices=['R0', 'R1'], required=True)
    p.add_argument('--race', action='store_true')
    a = p.parse_args()
    out = Path(os.environ.get('STEP19_OUTPUT_DIR', Path(__file__).resolve().parent)).resolve()
    vm = Path(os.environ.get('STEP19_VM_DIR', '/home/frankie/mygitprojects/.worktrees/cvw-step19-reuse/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0')).resolve()
    log = out/(a.label+'.log')
    assert not log.exists(), 'preserve prior output'
    unit = 'step19-ti-'+a.label.lower()
    binary = out/('testinvoke-race.test' if a.race else 'testinvoke.test')
    cmd = ['systemd-run', '--user', '--collect', '--unit='+unit, '--working-directory='+str(vm),
           '-p', 'MemoryMax=2G', '-p', 'TasksMax=256', '-p', 'RuntimeMaxSec=90s',
           '-p', 'TimeoutStopSec=5s', '-p', 'KillMode=control-group', '-p', 'RemainAfterExit=yes',
           '-p', 'StandardOutput=append:'+str(log), '-p', 'StandardError=inherit',
           '--setenv=CM_REUSE_EXPERIMENT='+a.policy, '--setenv=GOMAXPROCS=4',
           '--setenv=GORACE=halt_on_error=1 exitcode=66',
           '--setenv=LD_LIBRARY_PATH='+str(vm/'wasmer-go/packaged/lib/linux-amd64'),
           str(binary), '-test.run=^TestInvoke$', '-test.v', '-test.count=1', '-test.timeout=60s',
           '-invoke_contract_name=compute', '-invoke_contract_method=bigNumCal',
           '-invoke_contract_type=go', '-invoke_test_time=100']
    (out/(a.label+'-command.json')).write_text(json.dumps(cmd, indent=2)+'\n')
    r = subprocess.run(cmd, capture_output=True, text=True)
    (out/(a.label+'-launch.txt')).write_text(r.stdout+r.stderr)
    assert r.returncode == 0
    rows, last, reason, pid = [], {}, '', 0
    begin = time.monotonic()
    try:
        while time.monotonic()-begin < 95:
            show = subprocess.run(['systemctl', '--user', 'show', unit, '-p', 'ActiveState',
                                   '-p', 'SubState', '-p', 'MainPID', '-p', 'ExecMainStatus', '-p', 'Result'],
                                  capture_output=True, text=True).stdout
            last = dict(s.split('=', 1) for s in show.splitlines() if '=' in s)
            pid = int(last.get('MainPID', '0'))
            status = Path(f'/proc/{pid}/status')
            if pid and status.exists():
                rec = dict(unix_ns=time.time_ns(), pid=pid)
                try:
                    for line in status.read_text().splitlines():
                        k, _, v = line.partition(':')
                        if k in ['VmRSS', 'VmSize', 'Threads']:
                            rec[k] = int(v.split()[0])
                except FileNotFoundError:
                    pass
                rows.append(rec)
                if rec.get('VmRSS', 0) > 1536*1024 or rec.get('Threads', 0) > 220:
                    reason = 'resource_soft_limit'
                    break
            data = log.read_text(errors='replace') if log.exists() else ''
            if 'WARNING: DATA RACE' in data:
                reason = 'go_data_race'
                break
            if last.get('SubState') == 'exited' or last.get('ActiveState') in ['inactive', 'failed'] or not last:
                reason = 'process_finished'
                break
            time.sleep(.02)
        else:
            reason = 'external_timeout'
    finally:
        subprocess.run(['systemctl', '--user', 'stop', unit], capture_output=True, text=True, timeout=10)
        assert not pid or not Path(f'/proc/{pid}').exists(), 'owned process still running'
        (out/(a.label+'-resources.jsonl')).write_text(''.join(json.dumps(x)+'\n' for x in rows))
        data = log.read_text(errors='replace') if log.exists() else ''
        result = dict(label=a.label, policy=a.policy, race=a.race, reason=reason,
                      race_detected='WARNING: DATA RACE' in data, systemd=last,
                      elapsed_wall_s=time.monotonic()-begin,
                      peak_rss_mib=max([x.get('VmRSS', 0) for x in rows] or [0])/1024,
                      peak_threads=max([x.get('Threads', 0) for x in rows] or [0]),
                      original_entry_pass='--- PASS: TestInvoke' in data,
                      requested_calls=100, stopped=True)
        (out/(a.label+'-result.json')).write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result))
    assert reason == 'process_finished' and not result['race_detected'] and result['original_entry_pass'], result
    assert last.get('ExecMainStatus') == '0', last


if __name__ == '__main__':
    main()
