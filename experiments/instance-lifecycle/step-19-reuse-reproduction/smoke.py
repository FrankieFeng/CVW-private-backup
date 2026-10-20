"""Bounded isolated default-pool smoke. Refuses to overwrite results.

This is deliberately not a throughput benchmark. It never starts four nodes.
"""
from pathlib import Path
import json, os, select, socket, subprocess, time

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parents[3]
ROOT = Path(os.environ.get('REUSE_SMOKE_ROOT', str(ROOT)))
VM = BASE / '.worktrees/cvw-step19-reuse/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'
LIB = VM / 'wasmer-go/packaged/lib/linux-amd64'
ADMIN = BASE / 'chainmaker-go/build/crypto-config/wx-org1.chainmaker.org/user/admin1/admin1'
SPECS = json.loads((ROOT / 'contracts.json').read_text())


def main():
    assert not (ROOT / 'requests.jsonl').exists(), 'preserve results; use a new output directory'
    for port in [27501, 27502]:
        with socket.socket() as sock:
            assert sock.connect_ex(('127.0.0.1', port)) != 0, 'port already in use'
    raw = (ROOT / 'requests.jsonl').open('x')
    resources = (ROOT / 'resources.jsonl').open('x')
    outcomes = []
    for endpoint, policy, port in [('baseline', 'R0', 27501), ('optimized', 'R1', 27502)]:
        home = ROOT / 'network' / endpoint
        env = dict(os.environ, CM_REUSE_EXPERIMENT=policy, LD_LIBRARY_PATH=str(LIB), GOMAXPROCS='4')
        # These flags are absent from this VM implementation as well as unset here.
        for key in list(env):
            if key.startswith(('CM_STEP', 'CM_STATIC', 'CM_FRESH', 'CM_INSTANCE_LIFECYCLE')):
                env.pop(key)
        node = client = None
        files = []
        try:
            stdout = (home / 'stdout.log').open('xb', buffering=0)
            files.append(stdout)
            node = subprocess.Popen([str(ROOT / 'chainmaker'), 'start', '-c',
                                     str(home / 'config/wx-org1.chainmaker.org/chainmaker.yml')],
                                    cwd=home, env=env, stdout=stdout, stderr=subprocess.STDOUT)
            (home / 'pid').write_text(str(node.pid))

            def sample(label):
                assert node.poll() is None, f'{policy}: node exited {node.returncode}'
                status = {}
                for line in Path(f'/proc/{node.pid}/status').read_text().splitlines():
                    key, _, value = line.partition(':')
                    if key in ['VmRSS', 'VmHWM', 'VmSize', 'Threads']:
                        status[key] = int(value.split()[0])
                stat = Path(f'/proc/{node.pid}/stat').read_text().split()
                row = dict(policy=policy, label=label, monotonic_ns=time.monotonic_ns(),
                           unix_ns=time.time_ns(), cpu_user_ticks=int(stat[13]),
                           cpu_system_ticks=int(stat[14]), **status)
                resources.write(json.dumps(row) + '\n'); resources.flush()
                assert status['VmRSS'] < 4096 * 1024, 'RSS limit 4GiB exceeded'
                assert status['Threads'] < 1500, 'thread limit exceeded'
                return row

            deadline = time.monotonic() + 60
            while True:
                sample('startup')
                try:
                    with socket.create_connection(('127.0.0.1', port), .2):
                        break
                except OSError:
                    assert time.monotonic() < deadline, 'startup timeout'
                    time.sleep(.5)
            errlog = (home / 'client.stderr').open('x'); files.append(errlog)
            client_env = dict(os.environ, STEP17_ROOT=str(ROOT), STEP17_ADMIN=str(ADMIN))
            client = subprocess.Popen([str(ROOT / 'client')], cwd=ROOT, env=client_env,
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=errlog, text=True, bufsize=1)

            def request(job, phase, index):
                job = dict(job, Mode=endpoint, Tag=f'{policy}:{phase}:{index}')
                begin = time.monotonic_ns()
                client.stdin.write(json.dumps([job]) + '\n'); client.stdin.flush()
                deadline = time.monotonic() + 75
                while True:
                    sample(phase + ':wait')
                    assert time.monotonic() < deadline, 'RPC smoke watchdog timeout'
                    ready, _, _ = select.select([client.stdout], [], [], 1)
                    if not ready:
                        continue
                    line = client.stdout.readline()
                    assert line, 'SDK driver exited'
                    if not line.startswith('RESULT '):
                        continue
                    row = json.loads(line[7:])[0]
                    row.update(policy=policy, phase=phase, index=index,
                               window_begin_ns=begin, window_end_ns=time.monotonic_ns())
                    raw.write(json.dumps(row) + '\n'); raw.flush()
                    sample(phase + ':done')
                    assert not row.get('error'), row
                    if job['Op'] == 'rwset':
                        info = row.get('transaction') or {}
                        assert info.get('block_height', 0) > 0 and info.get('transaction'), row
                    else:
                        response = row.get('response') or {}
                        result = response.get('contract_result') or {}
                        assert response.get('code', 0) == 0 and result.get('code', 0) == 0, row
                        assert response.get('tx_id'), row
                    return row

            for spec in SPECS:
                request(dict(Op='deploy', Contract=spec['label'], Path=spec['paths']['original'], Params={}), 'deploy', 0)
                time.sleep(.2)
            for spec in SPECS:
                methods = ['bigNumCal', 'hashCal'] if spec['label'] == 'compute' else [spec['method']]
                for method in methods:
                    phase_rows = []
                    for i in range(23):
                        params = dict(spec['params'])
                        if spec['label'] == 'erc721':
                            params['tokenId'] = str(190000 + i)
                        if spec['label'] == 'fact':
                            params['file_hash'] = 'step19reuse-' + str(i)
                        row = request(dict(Op='invoke', Contract=spec['label'], Method=method,
                                           Params=params), 'warmup' if i < 3 else 'sample', i)
                        phase_rows.append(row)
                        time.sleep(.1)  # bounded smoke; includes deliberate gaps, not saturation TPS
                    for i, row in enumerate(phase_rows):
                        request(dict(Op='rwset', Contract=spec['label'], Path=row['response']['tx_id']), 'commit-check', i)
                    print(policy, spec['label'], method, '23 committed calls checked', flush=True)
                    sample('method-end:' + method)
            sample('before-idle')
            for _ in range(5):
                time.sleep(1); sample('idle')
            outcomes.append(dict(policy=policy, smoke='completed'))
        except Exception as exc:
            outcomes.append(dict(policy=policy, smoke='failed', error=str(exc)))
            print('STOP:', policy, str(exc)[:1500], flush=True)
            break  # do not expand/retry an unsafe or failed group
        finally:
            if client is not None:
                client.terminate()
                try: client.wait(timeout=5)
                except subprocess.TimeoutExpired: client.kill(); client.wait()
            if node is not None and node.poll() is None:
                node.terminate()
                try: node.wait(timeout=15)
                except subprocess.TimeoutExpired: node.kill(); node.wait()
            for handle in files: handle.close()
    raw.close(); resources.close()
    (ROOT / 'smoke-status.json').write_text(json.dumps(outcomes, indent=2) + '\n')
    assert all(row['smoke'] == 'completed' for row in outcomes) and len(outcomes) == 2, outcomes


if __name__ == '__main__':
    main()
