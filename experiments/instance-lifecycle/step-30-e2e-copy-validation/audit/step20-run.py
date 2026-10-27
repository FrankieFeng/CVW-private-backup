"""Bounded Step-20 synchronous fresh replay using unchanged saved binaries."""
from pathlib import Path
import argparse
import base64
import json
import os
import random
import select
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
LIB = Path('/home/frankie/mygitprojects/.worktrees/cvw-step17/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib/linux-amd64')
MODES = ['baseline', 'optimized']


def ctl(*args):
    return subprocess.run(['systemctl', '--user', *args], capture_output=True, text=True, timeout=10)


def run(kind, batch, n):
    label = kind+'-'+batch
    rawpath = ROOT/(label+'-requests.jsonl')
    assert not rawpath.exists(), 'refuse overwrite'
    detailed = kind == 'trace'
    node = ROOT/('chainmaker-trace' if detailed else 'chainmaker-original')
    binary = ROOT/('client-trace' if detailed else 'client-original')
    mapping = dict(baseline=0, optimized=1)
    if detailed and batch == 'b':
        mapping = dict(baseline=1, optimized=0)
    units, pids, client, err = [], {}, None, None
    status = dict(label=label, n_pairs=n, detailed=detailed, mapping=mapping, state='starting')
    for port in [27801, 27802, 28801, 28802]:
        with socket.socket() as s:
            assert s.connect_ex(('127.0.0.1', port)) != 0, 'port occupied'
    raw = rawpath.open('x')
    resources = (ROOT/(label+'-resources.jsonl')).open('x')
    try:
        for mode in MODES:
            home = ROOT/'network'/mode
            log = home/(label+'.log')
            assert not log.exists()
            unit = 'step-20-'+label+'-'+mode
            env = {'CM_STATIC_MEMORY_COPY': str(mapping[mode]), 'CM_FRESH_INVOKE': '1',
                   'CM_STEP17_SERIALIZE_VM': '1', 'CM_STEP17_OBSERVE': '1',
                   'CM_STEP19_TRACE': '1' if detailed else '0',
                   'CM_STEP16_SERIALIZED_MODULE': '',
                   'CM_STEP17_ARTIFACT_DIR': str(BASE/'step-17-real-node/compiled'),
                   'LD_LIBRARY_PATH': str(LIB), 'GOMAXPROCS': '4'}
            cmd = ['systemd-run', '--user', '--collect', '--unit='+unit, '--working-directory='+str(home),
                   '-p', 'MemoryMax=3G', '-p', 'TasksMax=256', '-p', 'RuntimeMaxSec=120s',
                   '-p', 'TimeoutStopSec=5s', '-p', 'KillMode=control-group',
                   '-p', 'StandardOutput=append:'+str(log), '-p', 'StandardError=inherit']
            cmd += ['--setenv='+k+'='+v for k, v in env.items()]
            cmd += [str(node), 'start', '-c', str(home/'config/wx-org1.chainmaker.org/chainmaker.yml')]
            (ROOT/(label+'-'+mode+'-command.json')).write_text(json.dumps(cmd, indent=2)+'\n')
            r = subprocess.run(cmd, capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            units.append(unit)
            deadline = time.monotonic()+5
            while True:
                pid = int(ctl('show', unit, '-p', 'MainPID', '--value').stdout.strip() or '0')
                if pid:
                    pids[mode] = pid
                    break
                assert time.monotonic() < deadline
                time.sleep(.02)

        def sample(phase):
            for mode, pid in pids.items():
                proc = Path(f'/proc/{pid}')
                assert proc.exists(), 'node exited'
                row = dict(label=label, phase=phase, endpoint=mode, policy='copy' if mapping[mode] else 'baseline',
                           pid=pid, mono_ns=time.monotonic_ns())
                for line in (proc/'status').read_text().splitlines():
                    k, _, v = line.partition(':')
                    if k in ['VmRSS', 'VmHWM', 'VmSize', 'Threads']:
                        row[k] = int(v.split()[0])
                stat = (proc/'stat').read_text().split()
                row['cpu_ticks'] = int(stat[13])+int(stat[14])
                resources.write(json.dumps(row)+'\n')
                resources.flush()
                assert row.get('VmRSS', 0) < 2560*1024, 'RSS soft limit'
                assert row.get('Threads', 0) < 220, 'threads soft limit'

        deadline = time.monotonic()+45
        for port in [27801, 27802]:
            while True:
                sample('startup')
                try:
                    with socket.create_connection(('127.0.0.1', port), .1):
                        break
                except OSError:
                    assert time.monotonic() < deadline, 'startup timeout'
                    time.sleep(.1)
        err = (ROOT/(label+'-client.stderr')).open('x')
        client = subprocess.Popen([str(binary)], cwd=ROOT, env=dict(os.environ, STEP17_ROOT=str(ROOT)),
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err, text=True, bufsize=1)

        def request(endpoint, phase, pair):
            tag = f'step-20:{label}:{phase}:{pair}'
            job = dict(Mode=endpoint, Op='invoke', Contract='compute', Method='bigNumCal', Params={}, Tag=tag)
            sent = time.monotonic_ns()
            client.stdin.write(json.dumps([job])+'\n')
            client.stdin.flush()
            deadline = time.monotonic()+15
            while True:
                sample(phase)
                assert time.monotonic() < deadline, 'client watchdog'
                ready, _, _ = select.select([client.stdout], [], [], .05)
                if not ready:
                    continue
                line = client.stdout.readline()
                assert line, 'client exited'
                if line.startswith('RESULT '):
                    r = json.loads(line[7:])[0]
                    break
            received = time.monotonic_ns()
            r.update(kind=kind, batch=batch, phase=phase, pair=pair, endpoint=endpoint,
                     mode='optimized' if mapping[endpoint] else 'baseline',
                     driver_send_mono_ns=sent, driver_receive_mono_ns=received)
            raw.write(json.dumps(r)+'\n')
            raw.flush()
            resp = r.get('response') or {}
            cr = resp.get('contract_result') or {}
            assert not r.get('error') and resp.get('code', 0) == cr.get('code', 0) == 0, r
            assert base64.b64decode(cr.get('result', '')) == b'success bigNumCal: 607723520', r
            assert cr.get('gas_used') == 106028 and resp.get('tx_block_height', 0) > 0, r

        order = MODES if batch != 'b' else list(reversed(MODES))
        for mode in order:
            request(mode, 'cold', -1)
        for i in range(5):
            for mode in order:
                request(mode, 'warmup', i)
        rng = random.Random(20261023+sum(map(ord, label)))
        for i in range(n):
            order = MODES[:]
            rng.shuffle(order)
            for mode in order:
                request(mode, 'warm', i)
            if (i+1) % 10 == 0:
                print(label, i+1, 'pairs completed', flush=True)
        sample('finished')
        status.update(state='completed', owned_pids=pids)
    except Exception as exc:
        status.update(state='stopped', error=str(exc), owned_pids=pids)
        raise
    finally:
        if client is not None:
            client.terminate()
            try:
                client.wait(timeout=3)
            except subprocess.TimeoutExpired:
                client.kill()
                client.wait()
        if err:
            err.close()
        for unit in units:
            ctl('stop', unit)
        assert all(not Path(f'/proc/{pid}').exists() for pid in pids.values()), 'owned node remains'
        status['all_owned_nodes_stopped'] = True
        (ROOT/(label+'-status.json')).write_text(json.dumps(status, indent=2)+'\n')
        raw.close()
        resources.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--kind', choices=['low', 'trace'], required=True)
    p.add_argument('--batch', required=True)
    p.add_argument('--pairs', type=int, required=True)
    a = p.parse_args()
    run(a.kind, a.batch, a.pairs)
