from pathlib import Path
import subprocess,json,time,sys,hashlib,os
P=Path(__file__).resolve().parents[1]
label,test,policy,method,n=sys.argv[1:];n=int(n)
assert test in ['Gas','Normal','Module']and policy in ['R0','R1']and 1<=n<=3
assert not (P/'raw_logs'/f'{label}.log').exists(),'existing attempt; inspect progress, do not rerun'
def call(cmd):return subprocess.run(cmd,capture_output=True,text=True)
def save(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def memory():
 d={k:int(v.split()[0])for k,v in (x.split(':',1)for x in Path('/proc/meminfo').read_text().splitlines())};return d['MemAvailable'],d['SwapTotal']-d['SwapFree']
a,s=memory();assert a>=8*1024*1024 and s<=1024*1024,'global resource gate'
lib=P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so'
assert hashlib.sha256(lib.read_bytes()).hexdigest()=='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9'
binary=P/'binaries/step21e.test';unit='step21e-'+label;log=P/'raw_logs'/f'{label}.log'
manifest=P/'audit'/({'fact':'fact','erc721':'erc721','buyNow':'exchange'}.get(method,'compute')+'-manifest.json')
env={'CM_REUSE_EXPERIMENT':policy,'CM_STEP21A_POOL':'capacity','CM_STEP21A_STORE_GUARD':'1','CM_STEP21_OBSERVE':'1','D_POLICY':policy,'D_N':str(n),'D_METHOD':method,'D_MANIFEST':str(manifest),'D_OUTPUT':str(P/'raw_logs'/f'{label}-receipts'),'GOMAXPROCS':'2','GOGC':'100','E_COUNTERS':str(P/'audit/gas-slots.json'),'E_INPUTS':str(P/'audit/gas-inputs.json'),'E_GAS_TRACE':os.environ.get('E_GAS_TRACE','1'if test=='Gas'else'0'),'E_ORDER':os.environ.get('E_ORDER','ABBAAB')}
cmd=['systemd-run','--user','--unit='+unit,'-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=60s','-p','TimeoutStopSec=5s','-p','KillMode=control-group','-p','RemainAfterExit=yes','-p','StandardOutput=append:'+str(log),'-p','StandardError=inherit','--working-directory='+str(P/'source/vm')]+['--setenv='+k+'='+v for k,v in env.items()]+[str(binary),'-test.run=^TestStep21E'+test+'$','-test.v','-test.count=1','-test.timeout=45s']
save(P/'raw_logs'/f'{label}-command.json',{'argv':cmd,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'scope':test,'n':n,'policy':policy,'method':method})
with(P/'PROGRESS.md').open('a')as f:f.write('\n即将执行 '+label+'；unit='+unit+'；binary/命令已落盘。恢复先查unit，不重复启动已有日志。\n')
r=call(cmd);save(P/'raw_logs'/f'{label}-launch.json',{'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
start=time.monotonic();peak_rss=peak_threads=0;reason='exited';stats={};cgroup=''
with (P/'raw_logs'/f'{label}-resources.jsonl').open('w')as f:
 while time.monotonic()-start<65:
  r=call(['systemctl','--user','show',unit,'-p','MainPID','-p','ControlGroup','-p','ExecMainStatus','-p','Result','-p','ActiveState','-p','SubState'])
  stats=dict(x.split('=',1)for x in r.stdout.splitlines()if '='in x);pid=int(stats.get('MainPID','0'));rss=threads=0
  if stats.get('ControlGroup'):cgroup=stats['ControlGroup']
  if pid:
   try:
    cg=Path('/sys/fs/cgroup')/cgroup.lstrip('/')
    for child in (cg/'cgroup.procs').read_text().split():
     try:
      st=dict(x.split(':',1)for x in Path('/proc',child,'status').read_text().splitlines()if ':'in x);rss+=int(st.get('VmRSS','0').split()[0]);threads+=int(st.get('Threads','0'))
     except FileNotFoundError:pass
   except FileNotFoundError:pass
  peak_rss=max(peak_rss,rss);peak_threads=max(peak_threads,threads);a,s=memory()
  f.write(json.dumps({'elapsed_s':time.monotonic()-start,'rss_kib':rss,'threads':threads,'global_available_kib':a,'swap_used_kib':s,'systemd':stats})+'\n');f.flush()
  if rss>1536*1024 or threads>220 or a<8*1024*1024 or s>1024*1024:
   reason='resource_guard';call(['systemctl','--user','stop',unit]);break
  if stats.get('SubState')=='exited'or stats.get('ActiveState')in ['failed','inactive']:break
  time.sleep(.02)
 else:reason='monitor_timeout';call(['systemctl','--user','stop',unit])
text=log.read_text()if log.exists()else''
passed=reason=='exited'and stats.get('ExecMainStatus')=='0'and'--- PASS: TestStep21E'+test in text and '--- FAIL:'not in text and '"event":"owner_closed"'in text
call(['systemctl','--user','stop',unit]);post=call(['systemctl','--user','show',unit,'-p','MainPID','-p','ActiveState']).stdout
outcome={'passed':passed,'reason':reason,'status_before_stop':stats,'post_stop':post,'peak_sampled_rss_kib':peak_rss,'peak_sampled_threads':peak_threads,'wall_s':time.monotonic()-start,'test':test,'method':method,'policy':policy,'n':n}
save(P/'raw_logs'/f'{label}-outcome.json',outcome)
with(P/'PROGRESS.md').open('a')as f:f.write('\n已结束 '+label+'：'+json.dumps(outcome,ensure_ascii=False)+'；先分析再决定后续。\n')
print(json.dumps(outcome,indent=2));print(text[-3500:]);raise SystemExit(0 if passed else 1)
