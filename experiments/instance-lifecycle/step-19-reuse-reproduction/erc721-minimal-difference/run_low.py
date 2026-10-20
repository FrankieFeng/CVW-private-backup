"""Single-contract bounded serial comparison. No pressure/concurrent mode.

Uses the unchanged saved node binary; cgroup containment and external request
quiescence do not certify arbitrary concurrent native Store access.
"""
from pathlib import Path
import json, os, re, select, socket, subprocess, time

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[4]
VM = PROJECT / '.worktrees/cvw-step19-reuse/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'
LIB = VM / 'wasmer-go/packaged/lib/linux-amd64'
ENV = json.loads((ROOT/'environment.json').read_text())
INPUTS = json.loads((ROOT/'inputs.json').read_text())
PATTERN = re.compile(r'tx id:([a-f0-9]+),\s*contractName:([^,]+),\s*contractMethod:([^,]+),.*?'
                     r'runtimeContractResult:(\d+)\s*,\s*startTime:(\d+),\s*endTime:(\d+),\s*executionTime:([\d.]+) s')


def ctl(*args, **kwargs):
    return subprocess.run(['systemctl','--user',*args],capture_output=True,text=True,**kwargs)


def events(home):
    return [json.loads(line[12:]) for line in (home/'stdout.log').read_text(errors='replace').splitlines()
            if line.startswith('REUSE_EVENT ')]


def invoke_logs(home):
    result=[];seen=set()
    for path in sorted((home/'log').glob('system.log*')):
        if not path.is_file() or path.resolve() in seen: continue
        seen.add(path.resolve())
        for number,line in enumerate(path.read_text(errors='replace').splitlines(),1):
            if 'vm_factory.go:' not in line: continue
            match=PATTERN.search(line)
            if match:
                result.append(dict(tx_id=match[1],contract=match[2],method=match[3],code=int(match[4]),
                                   begin_ns=int(match[5]),end_ns=int(match[6]),printed_seconds=match[7],
                                   file=str(path),line=number))
    return result


def run_case(batch, policy, raw, resources):
    mode='baseline' if policy=='R0' else 'optimized'
    home=ROOT/batch/'network'/mode; port=27601 if policy=='R0' else 27602
    unit=f'step19-erc-min-{batch}-{policy.lower()}'
    assert not (home/'stdout.log').exists(), 'refuse to overwrite'
    for number in [port,port+1000]:
        with socket.socket() as sock: assert sock.connect_ex(('127.0.0.1',number))!=0, 'port in use'
    cmd=['systemd-run','--user','--collect','--unit='+unit,'--working-directory='+str(home),
         '-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=90s',
         '-p','TimeoutStopSec=5s','-p','KillMode=control-group',
         '-p','StandardOutput=append:'+str(home/'stdout.log'),'-p','StandardError=inherit',
         '--setenv=CM_REUSE_EXPERIMENT='+policy,'--setenv=LD_LIBRARY_PATH='+str(LIB),
         '--setenv=GOMAXPROCS=4',str(ROOT/'chainmaker'),'start','-c',
         str(home/'config/wx-org1.chainmaker.org/chainmaker.yml')]
    launch=subprocess.run(cmd,capture_output=True,text=True)
    (home/'launch.txt').write_text(launch.stdout+launch.stderr);assert launch.returncode==0
    client=None;errlog=None;pid=0;baseline_rss=None;invoke_count=0;last_start=0
    try:
        deadline=time.monotonic()+5
        while pid==0:
            value=ctl('show',unit,'-p','MainPID','--value').stdout.strip()
            pid=int(value or 0);assert time.monotonic()<deadline;time.sleep(.05)
        (home/'pid').write_text(str(pid))
        properties=ctl('show',unit,'-p','ControlGroup','-p','MemoryMax','-p','TasksMax','-p','RuntimeMaxUSec')
        (home/'unit-properties.txt').write_text(properties.stdout)
        assert 'MemoryMax=2147483648' in properties.stdout and 'TasksMax=256' in properties.stdout

        def sample(label):
            process=Path(f'/proc/{pid}');assert process.exists(), 'node exited'
            status={}
            for line in (process/'status').read_text().splitlines():
                key,_,value=line.partition(':')
                if key in ['VmRSS','VmHWM','VmSize','Threads']:status[key]=int(value.split()[0])
            assert status, 'node terminated'
            stat=(process/'stat').read_text().split()
            row=dict(batch=batch,policy=policy,label=label,unix_ns=time.time_ns(),
                     monotonic_ns=time.monotonic_ns(),cpu_ticks=int(stat[13])+int(stat[14]),**status)
            resources.write(json.dumps(row)+'\n');resources.flush()
            assert status['VmRSS']<1536*1024,'RSS soft limit'
            assert status['Threads']<220,'thread soft limit'
            if baseline_rss is not None:assert status['VmRSS']-baseline_rss<256*1024,'post-deploy RSS growth limit'
            return row

        deadline=time.monotonic()+45
        while True:
            sample('startup')
            try:
                with socket.create_connection(('127.0.0.1',port),.1):break
            except OSError:
                assert time.monotonic()<deadline,'startup timeout';time.sleep(.1)
        errlog=(home/'client.stderr').open('x')
        ce=dict(os.environ,STEP17_ROOT=str(ROOT/batch),STEP17_ADMIN=str(PROJECT/'chainmaker-go/build/crypto-config/wx-org1.chainmaker.org/user/admin1/admin1'))
        client=subprocess.Popen([str(ROOT/'client')],cwd=ROOT,env=ce,stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,stderr=errlog,text=True,bufsize=1)

        def request(job,phase,index):
            job=dict(job,Mode=mode,Tag=f'{batch}:{policy}:{phase}:{index}')
            client.stdin.write(json.dumps([job])+'\n');client.stdin.flush()
            deadline=time.monotonic()+15
            while True:
                sample(phase+':wait');assert time.monotonic()<deadline,'request timeout'
                ready,_,_=select.select([client.stdout],[],[],.05)
                if not ready:continue
                line=client.stdout.readline();assert line,'client exited'
                if not line.startswith('RESULT '):continue
                row=json.loads(line[7:])[0];row.update(batch=batch,policy=policy,phase=phase,index=index)
                raw.write(json.dumps(row)+'\n');raw.flush();assert not row.get('error'),row
                if job['Op']=='rwset':
                    info=row.get('transaction') or {};assert info.get('transaction') and info.get('block_height',0)>0,row
                else:
                    response=row.get('response') or {};cr=response.get('contract_result') or {}
                    assert response.get('code',0)==0 and cr.get('code',0)==0 and response.get('tx_id'),row
                    if phase in ['warmup','sample']:assert cr.get('result'), 'empty mint result'
                return row

        def quiesce():
            # The current ABI has unsafe concurrent Store access. Never overlap a new
            # business request with a known unfinished close/create pipeline here.
            expected_creates=6+(invoke_count if policy=='R1' else 0)
            expected_closes=1+(invoke_count if policy=='R1' else 0)
            deadline=time.monotonic()+2
            while True:
                sample('quiesce');ee=events(home)
                count=lambda name:sum(e['event']==name for e in ee)
                assert count('create_begin')<=expected_creates,'unexpected creation/concurrent execution'
                assert count('acquire_wait')==0,'pool waiting in serial low-load test'
                if (count('create')==count('create_begin')==expected_creates and
                    count('close_done')==count('close_begin')==expected_closes and
                    count('enqueue_done')==5+(invoke_count if policy=='R1' else 0)):
                    # All explicit native lifecycle work has returned before another RPC.
                    break
                assert time.monotonic()<deadline,'close/refill did not quiesce';time.sleep(.02)

        request(dict(Op='deploy',Contract='erc721',Path=ENV['wasm_path'],Params={}), 'deploy',0)
        invoke_count=1;quiesce()
        assert len([x for x in invoke_logs(home) if x['method']=='init_contract'])==1, 'original INFO logger missing or repeated'
        baseline_rss=sample('post-deploy')['VmRSS']
        mint_rows=[]
        for i,params in enumerate(INPUTS):
            while time.monotonic()-last_start<.2:sample('spacing');time.sleep(.02)
            last_start=time.monotonic()
            row=request(dict(Op='invoke',Contract='erc721',Method='mint',Params=params), 'warmup' if i<5 else 'sample',i)
            mint_rows.append(row);invoke_count+=1;quiesce()
            matches=[x for x in invoke_logs(home) if x['tx_id']==row['response']['tx_id'] and x['method']=='mint']
            assert len(matches)==1 and matches[0]['code']==0,'missing/repeated/failed original mint log'
        for i,row in enumerate(mint_rows):
            request(dict(Op='rwset',Contract='erc721',Path=row['response']['tx_id']), 'commit-check',i)
        sample('before-idle')
        for _ in range(10):time.sleep(.1);sample('idle')
        print(batch,policy,'completed: 5 warmup + 10 measured candidate mints, original INFO and commit checks',flush=True)
    finally:
        if client is not None:
            client.terminate()
            try:client.wait(timeout=3)
            except subprocess.TimeoutExpired:client.kill();client.wait()
        if errlog:errlog.close()
        stopped=ctl('stop',unit,timeout=10)
        (home/'stop.txt').write_text(stopped.stdout+stopped.stderr)
        # A process killed by the hard watchdog is a failed run, not a performance result.
        assert not Path(f'/proc/{pid}').exists() if pid else True,'owned node still running'


def main():
    assert not (ROOT/'requests.jsonl').exists(),'preserve existing results'
    status=[]
    with (ROOT/'requests.jsonl').open('x') as raw,(ROOT/'resources.jsonl').open('x') as resources:
        try:
            for batch,order in [('a',['R0','R1']),('b',['R1','R0'])]:
                for policy in order:
                    run_case(batch,policy,raw,resources)
                    status.append(dict(batch=batch,policy=policy,status='completed'))
        except Exception as exc:
            status.append(dict(status='stopped',reason=str(exc)))
            print('STOP',str(exc)[:1200],flush=True)
        finally:(ROOT/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    assert len(status)==4 and all(x['status']=='completed' for x in status),status


if __name__=='__main__':main()
