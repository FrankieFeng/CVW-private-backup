from pathlib import Path
import argparse,subprocess,json,time,hashlib,sys
P=Path(__file__).resolve().parents[1]
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def cmd(args):return subprocess.run(args,capture_output=True,text=True)
def mem():
 d={s.split(':',1)[0]:int(s.split()[1])for s in Path('/proc/meminfo').read_text().splitlines()if s.startswith(('MemAvailable:','SwapTotal:','SwapFree:'))};return d['MemAvailable'],d['SwapTotal']-d['SwapFree']
def run(label,contract,left='G0',right='G1',pairs=1,phase='preflight',first=0,module_first='A0',batch=0,slot=0,copy_check=False):
 wall_start_order=time.time_ns()
 out=P/'raw_logs'/f'{label}-outcome.json'
 if out.exists():return json.loads(out.read_text())
 assert not(P/'STOP.json').exists(),'STOP retained: analyze only'
 log=P/'raw_logs'/f'{label}.log';assert not log.exists(),'incomplete attempt: inspect state/unit'
 av,sw=mem();assert av>=8*1024**2 and sw<=1024**2,'global resource gate'
 assert 1<=pairs<=2 and contract in ['compute','fact','erc721','normal']
 name='compute' if contract=='normal' else contract
 variants=json.loads((P/'inputs/variants.json').read_text());a=variants[name+'-'+left]
 manifest=P/'inputs'/f'{label}-manifest.json';save(manifest,{'Artifacts':[{'Contract':name,'Path':a['path'],'SHA256':a['sha']}]})
 native=P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so';assert hashlib.sha256(native.read_bytes()).hexdigest()=='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9'
 binary=P/'binaries/build2.test';sha=hashlib.sha256(binary.read_bytes()).hexdigest();assert sha==json.loads((P/'audit/build2-outcome.json').read_text())['binary_sha']
 env={'E22_ENABLED':'1','E22_CONTRACT':name,'E22_METHOD':{'compute':'bigNumCal','fact':'saveAndFindByFileHash','erc721':'mint','normal':'normalCal'}[contract],'E22_PHASE':phase,'E22_PAIRS':str(pairs),'E25_VARIANTS':str(P/'inputs/variants.json'),'E25_LEFT':left,'E25_RIGHT':right,'E25_FIRST':str(first),'E25_COPY_CHECK':'1'if copy_check else'0','E24_MODULE_FIRST':module_first,'E22_CONFIG_SHA':json.loads((P/'environment.json').read_text())['config_sha'],'CM_REUSE_EXPERIMENT':'R1','CM_STEP21A_POOL':'capacity','CM_STEP21A_STORE_GUARD':'1','CM_STEP21_OBSERVE':'1','D_POLICY':'R1','D_N':'1','D_MANIFEST':str(manifest),'D_OUTPUT':str(P/'raw_logs'/f'{label}-receipts'),'GOMAXPROCS':'2','GOGC':'100','LD_LIBRARY_PATH':str(native.parent)}
 unit='step25-'+label;test='TestStep25Serial'
 argv=['systemd-run','--user','--unit='+unit,'-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=60s','-p','TimeoutStopSec=5s','-p','KillMode=control-group','-p','RemainAfterExit=yes','-p','StandardOutput=append:'+str(log),'-p','StandardError=inherit','--working-directory='+str(P/'source/vm')]+['--setenv='+k+'='+v for k,v in env.items()]+[str(binary),'-test.run=^'+test+'$','-test.v','-test.count=1','-test.timeout=45s']
 save(P/'raw_logs'/f'{label}-command.json',dict(argv=argv,binary_sha256=sha,batch=batch,slot=slot,left=left,right=right,copy_check=copy_check,env=env));save(P/'state.json',dict(active_unit=unit,label=label,next='inspect existing unit/outcome before continuing'))
 with(P/'PROGRESS.md').open('a')as f:f.write('\n启动 '+label+'，unit='+unit+'，pairs='+str(pairs)+'；命令已保存。\n')
 z=cmd(argv);save(P/'raw_logs'/f'{label}-launch.json',dict(exit=z.returncode,stdout=z.stdout,stderr=z.stderr));assert z.returncode==0,z.stderr
 begin=time.monotonic();rss_peak=threads_peak=0;stats={};reason='exited';pids=set();cgroup=''
 with(P/'raw_logs'/f'{label}-resources.jsonl').open('w')as f:
  while time.monotonic()-begin<65:
   z=cmd(['systemctl','--user','show',unit,'-p','MainPID','-p','ExecMainStatus','-p','ActiveState','-p','SubState','-p','Result','-p','ControlGroup']);stats=dict(x.split('=',1)for x in z.stdout.splitlines()if'='in x);pid=int(stats.get('MainPID','0'));rss=threads=0
   if stats.get('ControlGroup'):cgroup=stats['ControlGroup']
   if pid:
    pids.add(pid)
    try:
     ds=dict(s.split(':',1)for s in Path(f'/proc/{pid}/status').read_text().splitlines()if':'in s);rss=int(ds.get('VmRSS','0').split()[0]);threads=int(ds.get('Threads','0'))
    except FileNotFoundError:pass
   rss_peak=max(rss,rss_peak);threads_peak=max(threads,threads_peak);av,sw=mem()
   f.write(json.dumps(dict(elapsed_s=time.monotonic()-begin,rss_kib=rss,threads=threads,available_kib=av,swap_kib=sw,systemd=stats))+'\n');f.flush()
   limit_t=220 if contract=='exchange'else 125;limit_r=1536*1024 if contract=='exchange'else 768*1024
   if rss>limit_r or threads>limit_t or av<8*1024**2 or sw>1024**2:reason='resource_guard';break
   if stats.get('SubState')=='exited'or stats.get('ActiveState')in ['failed','inactive']:break
   time.sleep(.025)
  else:reason='monitor_timeout'
 text=log.read_text(errors='replace')if log.exists()else''
 events=[json.loads(s[8:])for s in text.splitlines()if s.startswith('STEP21C ')]
 boundaries=[e for e in events if e.get('event')=='boundary'];owners=[e for e in events if e.get('event')=='owner_closed'];managers=[e for e in events if e.get('event')=='manager_closed']
 if boundaries:
  rss_peak=max(rss_peak,max(e.get('VmRSS',0)for e in boundaries));threads_peak=max(threads_peak,max(e.get('Threads',0)for e in boundaries))
 limit_t=220 if contract=='exchange'else 125;limit_r=1536*1024 if contract=='exchange'else 768*1024
 if rss_peak>limit_r or threads_peak>limit_t:reason='resource_guard_boundary'
 passed=reason=='exited'and stats.get('ExecMainStatus')=='0'and'--- PASS: '+test in text and'--- FAIL:'not in text and bool(owners)and owners[-1]['managed_pending']==0 and bool(managers)and managers[-1]['created']==managers[-1]['closed']and managers[-1]['in_flight']==0 and'panic:'not in text and'fatal error:'not in text
 stop=cmd(['systemctl','--user','stop',unit]);post=cmd(['systemctl','--user','show',unit,'-p','MainPID','-p','ActiveState']).stdout
 stopped=all(not Path(f'/proc/{pid}').exists()for pid in pids)
 cgpath=Path('/sys/fs/cgroup')/cgroup.lstrip('/')
 cg_empty=not cgpath.exists()or not(cgpath/'cgroup.procs').read_text().strip()
 passed=passed and stopped and cg_empty and stop.returncode==0
 outcome=dict(wall_start_order=wall_start_order,label=label,contract=contract,phase=phase,pairs=pairs,first=first,left=left,right=right,copy_check=copy_check,module_first=module_first,batch=batch,slot=slot,passed=passed,reason=reason,peak_rss_kib=rss_peak,peak_threads=threads_peak,wall_s=time.monotonic()-begin,systemd=stats,post_stop=post,all_owned_processes_stopped=stopped,cgroup_empty=cg_empty,boundaries=boundaries,owner=owners[-1]if owners else None)
 save(out,outcome)
 if not passed:save(P/'STOP.json',dict(label=label,reason=reason,stop_all=True))
 save(P/'state.json',dict(active_unit=None,last=label,next='continue registered gate'if passed else'analyze only'))
 with(P/'PROGRESS.md').open('a')as f:f.write('\n结束 '+label+'：passed='+str(passed)+'，reason='+reason+'，peak_threads='+str(threads_peak)+'，RSS_KiB='+str(rss_peak)+'，PID/cgroup结束='+str(stopped and cg_empty)+'。\n')
 print(json.dumps({k:v for k,v in outcome.items()if k not in ['boundaries','owner','systemd']}),flush=True)
 if not passed:raise RuntimeError('retained STOP: '+label)
 return outcome
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('contract');p.add_argument('--left',default='G0');p.add_argument('--right',default='G1');p.add_argument('--pairs',type=int,default=1);p.add_argument('--phase',default='preflight');p.add_argument('--first',type=int,default=0);p.add_argument('--module-first',default='A0');p.add_argument('--batch',type=int,default=0);p.add_argument('--slot',type=int,default=0);p.add_argument('--copy-check',action='store_true');a=p.parse_args();run(**vars(a))
