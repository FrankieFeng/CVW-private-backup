"""Confirm the frozen 95903a3 eight-cell experiment; no new optimization or rebuild."""
from pathlib import Path
import hashlib, json, os, subprocess, time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
WT = Path('/home/frankie/mygitprojects/.worktrees/cvw-step18-phase2')
VM = WT / 'chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'
CONTRACTS = ['compute', 'erc721', 'fact']

def main():
    runs = [('confirm-a', 'plain', 181951), ('probe-a', 'probe', 181961),
            ('confirm-b', 'plain', 181952), ('probe-b', 'probe', 181962),
            ('confirm-c', 'plain', 181953)]
    # Confirm actual binary/manifest identity before each independent worker.
    audit = json.loads((OUT / 'audit.json').read_text())
    assert hashlib.sha256((ROOT/'step18.test').read_bytes()).hexdigest() == audit['binary_sha']
    env = dict(os.environ, GOROOT='/usr/local/go', GOTOOLCHAIN='local', GOMAXPROCS='1',
               CM_INSTANCE_LIFECYCLE_TRACE='0', S15_MANIFEST=str(ROOT/'manifest-full.json'),
               S16_ARTIFACTS=str(ROOT/'artifacts'), S18_FULL='1', S16_N='150')
    for batch, mode, seed in runs:
        dest = OUT / batch
        dest.mkdir(exist_ok=False)
        metadata = dict(batch=batch, mode=mode, seed=seed, n=150, warmup_rounds=5,
                        cpu=min(os.sched_getaffinity(0)), binary_sha256=audit['binary_sha'],
                        base_commit='95903a3', branch='experiment/step18-phase2',
                        started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                        status=[])
        (dest/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
        for contract in CONTRACTS:
            print(batch, mode, contract, '150 paired rounds x 8 cells', flush=True)
            worker = dict(env, S18_MODE=mode, S18_DIAG='1' if mode=='probe' else '0',
                          S18_CONTRACT=contract, S15_CONTRACT=f'{contract}-a0p0-{mode}',
                          S16_SEED=str(seed), S16_OUT=str(dest/(contract+'.jsonl')))
            with (dest/(contract+'.log')).open('x') as log:
                p = subprocess.run(['taskset','-c',str(metadata['cpu']),'/usr/bin/time','-v',
                                    '-o',str(dest/(contract+'.resources.txt')),str(ROOT/'step18.test'),
                                    '-test.run=^TestStep18Pilot$','-test.v','-test.timeout=10m'],
                                   cwd=VM,env=worker,stdout=log,stderr=subprocess.STDOUT)
            metadata['status'].append(dict(contract=contract,exit_code=p.returncode))
            (dest/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
            if p.returncode:
                raise RuntimeError((dest/(contract+'.log')).read_text()[-3000:])

def validate():
    dest = OUT / 'validation'
    dest.mkdir(exist_ok=False)
    env = dict(os.environ, GOROOT='/usr/local/go', GOTOOLCHAIN='local', GOMAXPROCS='1',
               CM_INSTANCE_LIFECYCLE_TRACE='0', S15_MANIFEST=str(ROOT/'manifest-full.json'),
               S16_ARTIFACTS=str(ROOT/'artifacts'))
    for contract in CONTRACTS:
        for pv in [0,1]:
            name = f'{contract}-p{pv}-checks'
            with (dest/(name+'.log')).open('x') as log:
                subprocess.run([str(ROOT/'step18.test'),'-test.run=^TestStep18Checks$', '-test.v'],
                               cwd=VM,env=dict(env,S18_CONTRACT=contract,S18_P=str(pv),
                                              S16_OUT=str(dest/(name+'.jsonl'))),
                               stdout=log,stderr=subprocess.STDOUT,check=True)
    for spec in json.loads((ROOT/'manifest-full.json').read_text()):
        if spec['flavor'] != 'plain':
            continue
        name = spec['label']
        with (dest/(name+'.log')).open('x') as log:
            subprocess.run([str(ROOT/'step18.test'),'-test.run=^TestStep16Validation$', '-test.v'],
                           cwd=VM,env=dict(env,S15_CONTRACT=name,S16_OUT=str(dest/(name+'.jsonl'))),
                           stdout=log,stderr=subprocess.STDOUT,check=True)
    print('validation finished', flush=True)

if __name__ == '__main__':
    import sys
    validate() if '--validate' in sys.argv else main()
