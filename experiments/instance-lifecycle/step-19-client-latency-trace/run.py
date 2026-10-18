"""Small isolated compute trace; never starts or alters step-17 nodes."""
from pathlib import Path
import json, os, random, socket, subprocess, time

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'step-17-real-node'
LIB = Path('/home/frankie/mygitprojects/.worktrees/cvw-step19/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib/linux-amd64')

def main():
    # Refuse to overwrite results or share live listening ports.
    assert not (ROOT / 'requests.jsonl').exists()
    for port in [27401, 27402]:
        with socket.socket() as s:
            assert s.connect_ex(('127.0.0.1', port)) != 0, port
    with (ROOT / 'requests.jsonl').open('x') as raw:
        for batch in ['a', 'b']:
            mapping = {'baseline': 0, 'optimized': 1} if batch == 'a' else {'baseline': 1, 'optimized': 0}
            processes, files, client = [], [], None
            try:
                for endpoint, enabled in mapping.items():
                    home = ROOT / 'network' / endpoint
                    env = dict(os.environ, CM_STATIC_MEMORY_COPY=str(enabled), CM_FRESH_INVOKE='1',
                               CM_STEP17_SERIALIZE_VM='1', CM_STEP17_OBSERVE='1', CM_STEP19_TRACE='1',
                               CM_STEP17_ARTIFACT_DIR=str(OLD / 'compiled'), LD_LIBRARY_PATH=str(LIB), GOMAXPROCS='4')
                    env.pop('CM_STEP16_SERIALIZED_MODULE', None)
                    log = (home / f'stdout-{batch}.log').open('xb', buffering=0)
                    files.append(log)
                    p = subprocess.Popen([str(ROOT / 'chainmaker'), 'start', '-c',
                                          str(home / 'config/wx-org1.chainmaker.org/chainmaker.yml')],
                                         cwd=home, env=env, stdout=log, stderr=subprocess.STDOUT)
                    processes.append(p)
                    (home / f'pid-{batch}').write_text(str(p.pid))
                deadline = time.monotonic() + 60
                for port in [27401, 27402]:
                    while True:
                        assert all(p.poll() is None for p in processes), 'node exited; inspect stdout'
                        try:
                            with socket.create_connection(('127.0.0.1', port), .5):
                                break
                        except OSError:
                            assert time.monotonic() < deadline, 'node readiness timeout'
                            time.sleep(.25)
                env = dict(os.environ, STEP17_ROOT=str(ROOT))
                errlog = (ROOT / f'client-{batch}.stderr').open('x')
                files.append(errlog)
                client = subprocess.Popen([str(ROOT / 'client')], cwd=ROOT, env=env,
                                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          stderr=errlog, text=True)

                def request(endpoint, phase, pair):
                    tag = f'{batch}:{phase}:{pair}'
                    job = dict(Mode=endpoint, Op='invoke', Contract='compute', Method='bigNumCal', Params={}, Tag=tag)
                    client.stdin.write(json.dumps([job]) + '\n')
                    client.stdin.flush()
                    while True:
                        line = client.stdout.readline()
                        assert line, 'client exited'
                        if line.startswith('RESULT '):
                            row = json.loads(line[7:])[0]
                            break
                    row.update(batch=batch, phase=phase, pair=pair, endpoint=endpoint,
                               mode='optimized' if mapping[endpoint] else 'baseline')
                    raw.write(json.dumps(row) + '\n')
                    raw.flush()
                    resp = row.get('response') or {}
                    cr = resp.get('contract_result') or {}
                    valid = not row.get('error') and resp.get('code', 0) == 0 and cr.get('code', 0) == 0 and bool(cr.get('result'))
                    if phase == 'warm':
                        assert valid, row
                    return valid

                for endpoint in mapping:
                    request(endpoint, 'cold', -1)
                    successes = 0
                    for i in range(10):
                        successes += request(endpoint, 'warmup', i)
                        if successes == 5:
                            break
                    assert successes == 5, 'warmup failed'
                rng = random.Random(191901 if batch == 'a' else 191902)
                for pair in range(30):
                    order = list(mapping)
                    rng.shuffle(order)
                    for endpoint in order:
                        request(endpoint, 'warm', pair)
                    if pair % 10 == 9:
                        print(batch, pair + 1, 'pairs complete', flush=True)
            finally:
                if client is not None:
                    client.stdin.close()
                    try:
                        client.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        client.terminate()
                        client.wait(timeout=10)
                for p in processes:
                    if p.poll() is None:
                        p.terminate()
                for p in processes:
                    try:
                        p.wait(timeout=20)
                    except subprocess.TimeoutExpired:
                        p.kill()
                        p.wait()
                for f in files:
                    f.close()

if __name__ == '__main__':
    main()
