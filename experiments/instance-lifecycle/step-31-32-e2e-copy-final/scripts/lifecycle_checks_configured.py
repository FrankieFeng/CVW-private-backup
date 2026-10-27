"""Two existing, bounded ownership checks. Never starts a node/client or sends RPC."""
from pathlib import Path
import json,subprocess,time,hashlib
P=Path(__file__).resolve().parents[1]
S=Path('/home/frankie/mygitprojects/.worktrees/cvw-step29/experiments/instance-lifecycle/step-29-buy-now-attribution')
B=S/'binaries/build3.test';LIB=S/'source/vm/wasmer-go/packaged/lib/linux-amd64'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def cmd(a):return subprocess.run(a,capture_output=True,text=True,timeout=10)
def mem():
 d={l.split(':')[0]:int(l.split()[1])for l in Path('/proc/meminfo').read_text().splitlines()if l.startswith(('MemAvailable:','SwapTotal:','SwapFree:'))};return d['MemAvailable'],d['SwapTotal']-d['SwapFree']
def run(test):
 label={'TestStep22ModuleLifecycle':'cached-module-fresh-configured','TestStep21DOwnerFailure':'owner-errors-configured'}[test];out=P/'raw_logs'/f'{label}-outcome.json'
 if out.exists():
  result=json.loads(out.read_text());assert result['passed'];return result
 assert not(P/'STOP_CONFIGURED.json').exists();log=P/'raw_logs'/f'{label}.log';assert not log.exists(),'inspect incomplete unit before resuming'
 assert sha(B)=='940ccc3adf6e4d03be01ee40c36fcb17861eb4517546d53c6da86aad41716f91'
 assert sha(LIB/'libwasmer.so')=='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9'
 av,sw=mem();assert av>=8*1024**2 and sw<=1024**2
 unit='step31-'+label
 env={'CM_REUSE_EXPERIMENT':'R1','CM_STEP21A_POOL':'capacity','CM_STEP21A_STORE_GUARD':'1','CM_STEP21_OBSERVE':'1','E22_ENABLED':'0','E27_ENABLED':'0','E27_DIAG':'0','E29_TRACE':'0','D_POLICY':'R1','D_FORCE_GC':'0','GOMAXPROCS':'2','GOGC':'100','LD_LIBRARY_PATH':str(LIB)}
 argv=['systemd-run','--user','--unit='+unit,'-p','MemoryMax=1G','-p','TasksMax=128','-p','RuntimeMaxSec=30s','-p','TimeoutStopSec=5s','-p','KillMode=control-group','-p','RemainAfterExit=yes','-p','StandardOutput=append:'+str(log),'-p','StandardError=inherit','--working-directory='+str(S/'source/vm')]+['--setenv='+k+'='+v for k,v in env.items()]+[str(B),'-test.run=^'+test+'$','-test.v','-test.count=1','-test.timeout=20s']
 save(P/'raw_logs'/f'{label}-command.json',dict(argv=argv,binary_sha=sha(B),purpose='safety protocol probe only; no real node admission implied'))
 save(P/'state.json',dict(active_unit=unit,next='inspect outcome/unit before retry'))
 with(P/'PROGRESS.md').open('a')as f:f.write('\n启动既有protocol probe '+test+'；命令已保存，未启动节点。\n')
 launch=cmd(argv);assert launch.returncode==0,launch.stderr
 peakrss=peakt=0;pids=set();cg='';begin=time.monotonic();reason='exited';stats={}
 with(P/'raw_logs'/f'{label}-resources.jsonl').open('w')as f:
  while time.monotonic()-begin<35:
   z=cmd(['systemctl','--user','show',unit,'-p','MainPID','-p','ExecMainStatus','-p','SubState','-p','ActiveState','-p','ControlGroup']);stats=dict(l.split('=',1)for l in z.stdout.splitlines()if'='in l);pid=int(stats.get('MainPID','0'));rss=threads=0;cg=stats.get('ControlGroup')or cg
   if pid:
    pids.add(pid)
    try:
     status=dict(l.split(':',1)for l in Path(f'/proc/{pid}/status').read_text().splitlines()if':'in l);rss=int(status.get('VmRSS','0').split()[0]);threads=int(status.get('Threads','0'))
    except FileNotFoundError:pass
   peakrss=max(peakrss,rss);peakt=max(peakt,threads);av,sw=mem()
   f.write(json.dumps(dict(elapsed_seconds=time.monotonic()-begin,pid=pid,rss_kib=rss,threads=threads,available_kib=av,swap_kib=sw,systemd=stats))+'\n');f.flush()
   if rss>768*1024 or threads>125 or av<8*1024**2 or sw>1024**2:reason='resource_guard';break
   if stats.get('SubState')=='exited'or stats.get('ActiveState')in ['failed','inactive']:break
   time.sleep(.02)
  else:reason='watchdog'
 stop=cmd(['systemctl','--user','stop',unit]);text=log.read_text(errors='replace');events=[json.loads(l[8:])for l in text.splitlines()if l.startswith('STEP21C ')]
 for e in events:peakrss=max(peakrss,e.get('VmRSS',0));peakt=max(peakt,e.get('Threads',0))
 closed=[e for e in events if e.get('event')=='owner_closed'];pidended=all(not Path(f'/proc/{p}').exists()for p in pids);cgp=Path('/sys/fs/cgroup')/cg.lstrip('/');cgempty=not cgp.exists()or not(cgp/'cgroup.procs').read_text().strip()
 passed=reason=='exited'and stats.get('ExecMainStatus')=='0'and'--- PASS: '+test in text and bool(closed)and closed[-1]['managed_pending']==0 and pidended and cgempty and stop.returncode==0 and peakrss<=768*1024 and peakt<=125
 result=dict(test=test,passed=passed,reason=reason,peak_rss_kib=peakrss,peak_threads=peakt,go_heap_bytes=None,go_heap_status='not_collected_in_reused_probe',pid_stopped=pidended,cgroup_empty=cgempty,owner_closed=closed[-1]if closed else None,events=events,binary_sha=sha(B),node_test=False)
 save(out,result);save(P/'state.json',dict(active_unit=None,last=label,next='continue finite audit'if passed else'stop; inspect preserved probe failure'))
 if not passed:save(P/'STOP_CONFIGURED.json',result)
 with(P/'PROGRESS.md').open('a')as f:f.write('\n完成probe '+test+'：passed='+str(passed)+'，PID/cgroup清空='+str(pidended and cgempty)+'；不代表真实节点已准入。\n')
 print(json.dumps({k:v for k,v in result.items()if k not in ['events','owner_closed']}),flush=True);assert passed
 return result
if __name__=='__main__':
 initial=(P/'raw_logs/cached-module-fresh.log').read_text();assert initial.startswith('panic: CM_REUSE_EXPERIMENT must explicitly be R0 or R1')and '--- PASS:'not in initial and 'STEP21C 'not in initial
 # Correcting required configuration does not waive owner/resource assertions; retain original STOP unchanged.
 for test in ['TestStep22ModuleLifecycle','TestStep21DOwnerFailure']:run(test)
