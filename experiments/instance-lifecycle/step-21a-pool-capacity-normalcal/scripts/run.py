"""Bounded, observable one-process runner. Each attempt persists before returning."""
from pathlib import Path
import argparse,json,subprocess,sys,time,hashlib,re,csv,math,statistics,base64,os
ROOT=Path(__file__).resolve().parent.parent
VM=Path('/home/frankie/mygitprojects/.worktrees/cvw-step21a/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0')

def progress(message,next_action,unit=None,blocked=None):
    p=ROOT/'state.json';state=json.loads(p.read_text());state.update(active_unit=unit,next_action=next_action,blocked=blocked,last_update=time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(p)
    with (ROOT/'PROGRESS.md').open('a') as f:f.write('\n### '+time.strftime('%Y-%m-%d %H:%M:%S')+'\n\n'+message+'\n\n下一条待执行：'+next_action+'\n')

def reduce_attempt(label,outcome):
    text=(ROOT/'raw_logs'/(label+'.log')).read_text(errors='replace');calls=[];acquires=[];b5=[];events=[]
    for line,s in enumerate(text.splitlines(),1):
        if s.startswith('STEP21 '):
            r=json.loads(s[7:]);r['line']=line
            if r['event']=='sample':calls.append(r)
            if r['event']=='acquire':acquires.append(r)
        if s.startswith('REUSE_EVENT '):events.append(dict(json.loads(s[12:]),line=line))
        if 'b5_profile sample_id=' in s:b5.append(dict(re.findall(r'(\w+)=([^\s]*)',s)))
    expected='success normalCal: 666' if outcome['method']=='normalCal' else 'success bigNumCal: 607723520'
    rows=[]
    for i,c in enumerate(calls):
        r=dict(label=label,pool=outcome['pool'],policy=outcome['policy'],phase=outcome['phase'],index=c['index'],method=outcome['method'],invoke_ns=c['end_ns']-c['begin_ns'],callmethod_ns=round(c['callmethod_s']*1e9),gas=c['gas'],code=c['code'],input_sha256=c['input_sha256'],result=base64.b64decode(c.get('result') or '').decode(errors='replace'),source_line=c['line'])
        r['business_success']=c['code']==0 and r['result']==expected
        if i<len(acquires):
            r.update({k:acquires[i][k] for k in ['getinstance_ns','channel_receive_ns','empty_branch','queue_after_receive','instance_id']})
        if i<len(b5):r.update({'b5_'+k:int(v) for k,v in b5[i].items() if k.endswith('_ns') or k in ['syscall_count','parameter_bytes']})
        rows.append(r)
    def write(file,values,fields=None):
        keys=fields or list(dict.fromkeys(k for r in values for k in r))
        with file.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(values)
    write(ROOT/'raw_logs'/(label+'-samples.csv'),rows,['label','pool','policy','phase','index','method'] if not rows else None)
    success=sum(r['business_success'] for r in rows)
    before=[e for e in events if e['event']=='enqueue_before'];done=[e for e in events if e['event']=='enqueue_done']
    summary=dict(label=label,pool=outcome['pool'],policy=outcome['policy'],phase=outcome['phase'],method=outcome['method'],requested=outcome['n'],observed=len(rows),success=success,gas_distribution=json.dumps({str(g):sum(r['gas']==g for r in rows) for g in sorted({r['gas'] for r in rows})}),guard_overlap=outcome['guard_overlap'],execution_ok=outcome['execution_ok'],primary_accepted=outcome['phase']=='formal' and outcome['execution_ok'] and success==100,status=outcome['status'],peak_rss_mib=outcome['peak_rss_mib'],peak_threads=outcome['peak_threads'],enqueue_unfinished=len(before)-len(done),created=sum(e['event']=='create' for e in events),closed=sum(e['event']=='close_done' for e in events))
    for name,field in [('invoke','invoke_ns'),('callmethod','callmethod_ns'),('channel','channel_receive_ns'),('b5_export','b5_export_call_ns')]:
        vals=[r[field]/1e6 for r in rows if field in r]
        summary.update({name+'_mean_ms':statistics.mean(vals) if vals else '',name+'_p50_ms':statistics.median(vals) if vals else '',name+'_p95_ms':sorted(vals)[math.ceil(.95*len(vals))-1] if vals else ''})
    summary['vm_log_tps_diagnostic_only']=success/(sum(r['invoke_ns'] for r in rows if r['business_success'])/1e9) if success and sum(r['invoke_ns'] for r in rows if r['business_success'])>0 else ''
    (ROOT/'raw_logs'/(label+'-summary.json')).write_text(json.dumps(summary,indent=2)+'\n')
    allsum=[json.loads(f.read_text()) for f in sorted((ROOT/'raw_logs').glob('*-summary.json'))];write(ROOT/'summary.csv',allsum)
    return summary

def run(a):
    label=f'{a.phase}-{a.method}-{a.pool}-{a.policy.lower()}-{a.batch}'
    saved=ROOT/'raw_logs'/(label+'-outcome.json')
    if saved.exists():
        o=json.loads(saved.read_text());print('RESUME: retained',label,flush=True);reduce_attempt(label,o);return o
    assert not (ROOT/'STOP.json').exists(),'safety STOP exists; no new attempts'
    unit='step21a-'+label.lower();log=ROOT/'raw_logs'/(label+'.log')
    assert not log.exists(),'incomplete prior log: inspect actual unit before any rerun'
    env=json.loads((ROOT/'environment.json').read_text());binary=ROOT/'binaries/step21a.test'
    assert hashlib.sha256(binary.read_bytes()).hexdigest()==env['binary_sha256']
    case=next(c for c in json.loads((ROOT/'cases.json').read_text()) if c['method']==a.method)
    assert hashlib.sha256(Path(case['wasm_path']).read_bytes()).hexdigest()==case['wasm_sha256']
    assert hashlib.sha256(Path(case['inputs_file']).read_bytes()).hexdigest()==case['inputs_sha256']
    test='TestStep21AIsolatedGuest' if a.phase=='isolated' else 'TestInvoke'
    cmd=['systemd-run','--user','--collect','--unit='+unit,'--working-directory='+str(VM),'-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=60s','-p','TimeoutStopSec=5s','-p','KillMode=control-group','-p','RemainAfterExit=yes','-p','StandardOutput=append:'+str(log),'-p','StandardError=inherit','--setenv=CM_REUSE_EXPERIMENT='+a.policy,'--setenv=CM_STEP21A_POOL='+a.pool,'--setenv=CM_STEP21A_STORE_GUARD=1','--setenv=CM_STEP21_OBSERVE=1','--setenv=GOMAXPROCS=4','--setenv=GOGC=100','--setenv=LD_LIBRARY_PATH='+str(VM/'wasmer-go/packaged/lib/linux-amd64'),str(binary),'-test.run=^'+test+'$','-test.v','-test.count=1','-test.timeout=45s','-invoke_contract_name=compute','-invoke_contract_method='+a.method,'-invoke_contract_type=go','-invoke_test_time='+str(a.n),'-step21_inputs='+case['inputs_file']]
    (ROOT/'raw_logs'/(label+'-command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
    progress('即将执行：`python3 -B scripts/run.py '+' '.join(sys.argv[1:])+'`；原始命令见raw_logs/'+label+'-command.json。','先检查systemctl --user show '+unit+'；不可重复启动',unit)
    start=subprocess.run(cmd,capture_output=True,text=True);assert start.returncode==0,start.stderr
    begin=time.monotonic();resources=[];last={};reason='';pid=0;stack_signal=False
    try:
        while time.monotonic()-begin<65:
            mem={s.split(':',1)[0]:int(s.split()[1]) for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith(('MemAvailable:','SwapTotal:','SwapFree:'))}
            if mem['MemAvailable']<8*1024**2 or mem['SwapTotal']-mem['SwapFree']>1024**2:reason='global_resource_floor';break
            sh=subprocess.run(['systemctl','--user','show',unit,'-p','MainPID','-p','ActiveState','-p','SubState','-p','ExecMainStatus','-p','CPUUsageNSec','-p','Result'],capture_output=True,text=True)
            last=dict(s.split('=',1) for s in sh.stdout.splitlines() if '=' in s);pid=int(last.get('MainPID','0'))
            if pid and Path(f'/proc/{pid}/status').exists():
                row=dict(mono_ns=time.monotonic_ns(),wall_ns=time.time_ns(),pid=pid,MemAvailable_kib=mem['MemAvailable'],SwapUsed_kib=mem['SwapTotal']-mem['SwapFree'])
                try:
                    for s in Path(f'/proc/{pid}/status').read_text().splitlines():
                        k,_,v=s.partition(':')
                        if k in ['VmRSS','VmHWM','VmSize','Threads']:row[k]=int(v.split()[0])
                    st=Path(f'/proc/{pid}/stat').read_text().split();row.update(cpu_ticks=int(st[13])+int(st[14]),last_cpu=int(st[38]))
                    row['leader_schedstat']=Path(f'/proc/{pid}/schedstat').read_text().strip()
                except FileNotFoundError:pass
                resources.append(row)
                if row.get('VmRSS',0)>1536*1024 or row.get('Threads',0)>220:reason='resource_threshold';break
            text=log.read_text(errors='replace') if log.exists() else ''
            if 'maintenance drain timeout' in text and pid and not stack_signal:
                subprocess.run(['systemctl','--user','kill','--kill-whom=main','--signal=SIGQUIT',unit],capture_output=True);stack_signal=True
            if last.get('SubState')=='exited' or last.get('ActiveState') in ['failed','inactive']:reason='exited';break
            time.sleep(.05)
        else:reason='external_timeout'
    finally:
        subprocess.run(['systemctl','--user','stop',unit],capture_output=True,timeout=10)
        assert not pid or not Path(f'/proc/{pid}').exists(),'owned process remains'
        (ROOT/'raw_logs'/(label+'-resources.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in resources))
        text=log.read_text(errors='replace') if log.exists() else ''
        overlap='STEP21A_GUARD ' in text
        ok=reason=='exited' and '--- PASS:' in text and '--- FAIL:' not in text and 'worker_exited":true' in text and not overlap and 'panic:' not in text and 'fatal error:' not in text
        outcome=dict(label=label,pool=a.pool,policy=a.policy,phase=a.phase,method=a.method,n=a.n,batch=a.batch,status='store_guard_stopped' if overlap else 'passed' if ok else reason,execution_ok=ok,guard_overlap=overlap,peak_rss_mib=max([r.get('VmRSS',0) for r in resources] or [0])/1024,peak_threads=max([r.get('Threads',0) for r in resources] or [0]),systemd=last,all_owned_processes_stopped=True,stack_signal=stack_signal,wall_s=time.monotonic()-begin)
        saved.write_text(json.dumps(outcome,indent=2)+'\n');summary=reduce_attempt(label,outcome)
        nextcmd='python3 -B scripts/suite.py (会跳过已有完成结果)'
        if not ok:
            (ROOT/'STOP.json').write_text(json.dumps(dict(reason=outcome['status'],label=label,no_formal_launch=True,stack_file=str(log)),indent=2)+'\n');nextcmd='仅分析现有raw_logs及STOP.json；禁止继续正式矩阵'
        progress('已落盘'+label+'：'+json.dumps(summary,ensure_ascii=False)+'；CSV已更新。',nextcmd,None,None if ok else outcome['status'])
        print(json.dumps(outcome),flush=True)
    return outcome

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pool',choices=['original','capacity'],required=True);p.add_argument('--policy',choices=['R0','R1'],required=True);p.add_argument('--method',choices=['bigNumCal','normalCal'],required=True);p.add_argument('--phase',choices=['isolated','preflight','formal'],required=True);p.add_argument('--batch',default='a');p.add_argument('--n',type=int,required=True)
    a=p.parse_args();o=run(a)
    if not o['execution_ok']:raise SystemExit(2)
