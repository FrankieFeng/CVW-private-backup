#!/usr/bin/env python3
"""Fixed serial-only matrix, no reruns/overwrites; systemd cgroup + soft monitors."""
from pathlib import Path
import subprocess,json,time,hashlib,os
P=Path(__file__).resolve().parents[1]
V=P.parents[2]/'chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'
LIB=V/'wasmer-go/packaged/lib/linux-amd64'
def run(cmd):return subprocess.run(cmd,capture_output=True,text=True)
def save(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def mem():
 d={k:int(v.split()[0])for k,v in (s.split(':',1)for s in Path('/proc/meminfo').read_text().splitlines())}
 return d['MemAvailable'],d['SwapTotal']-d['SwapFree']
assert hashlib.sha256((LIB/'libwasmer.so').read_bytes()).hexdigest()=='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9'
assert not any((P/'raw_logs').glob('*-outcome.json')), 'Already attempted; inspect PROGRESS and logs, do not repeat.'
binary=P/'serial-native'
cmd=['gcc','-std=c11','-Wall','-Wextra','-Werror','-O0','-g','-I'+str(V/'wasmer-go/packaged/include'),str(P/'scripts/serial.c'),'-L'+str(LIB),'-Wl,-rpath,'+str(LIB),'-lwasmer','-o',str(binary)]
r=run(cmd);save(P/'evidence/build.json',{'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
save(P/'evidence/serial-artifact.json',{'sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'ldd':run(['ldd',str(binary)]).stdout})
for mode in ['same','different']:
 available,swap=mem();assert available>=8*1024*1024 and swap<=1024*1024,'global resource gate'
 unit='step21b-serial-'+mode
 log=P/'raw_logs'/f'{mode}.log';assert not log.exists()
 cmd=['systemd-run','--user','--unit='+unit,'-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=45s','-p','TimeoutStopSec=5s','-p','KillMode=control-group','-p','RemainAfterExit=yes','-p','StandardOutput=append:'+str(log),'-p','StandardError=inherit','/usr/bin/timeout','30s',str(binary),mode]
 save(P/'raw_logs'/f'{mode}-command.json',cmd)
 with (P/'PROGRESS.md').open('a')as f:f.write('\n即将执行串行 '+mode+'；恢复先查unit '+unit+'，已有log时禁止重复运行。\n')
 r=run(cmd);save(P/'raw_logs'/f'{mode}-launch.json',{'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
 start=time.monotonic();peak_rss=peak_threads=0;stop=None;stats={}
 with (P/'raw_logs'/f'{mode}-resources.jsonl').open('w')as f:
  while time.monotonic()-start<50:
   s=run(['systemctl','--user','show',unit,'-p','MainPID','-p','ExecMainStatus','-p','Result','-p','ActiveState','-p','SubState','-p','ControlGroup'])
   stats=dict(x.split('=',1)for x in s.stdout.splitlines()if '='in x);pid=int(stats.get('MainPID','0'))
   rss=threads=0
   if pid:
    try:
     cg=Path('/sys/fs/cgroup')/stats['ControlGroup'].lstrip('/')
     for child in (cg/'cgroup.procs').read_text().split():
      try:
       st=dict(x.split(':',1)for x in Path('/proc',child,'status').read_text().splitlines()if ':'in x)
       rss+=int(st.get('VmRSS','0').split()[0]);threads+=int(st.get('Threads','0').split()[0])
      except FileNotFoundError:pass
    except FileNotFoundError:pass
   peak_rss=max(peak_rss,rss);peak_threads=max(peak_threads,threads)
   av,sw=mem();f.write(json.dumps({'elapsed_s':time.monotonic()-start,'rss_kib':rss,'threads':threads,'available_kib':av,'swap_used_kib':sw,'systemd':stats})+'\n');f.flush()
   if rss>1536*1024 or threads>220 or av<8*1024*1024 or sw>1024*1024:stop='resource_guard';run(['systemctl','--user','stop',unit]);break
   if stats.get('SubState')=='exited' or stats.get('ActiveState')in ['failed','inactive']:break
   time.sleep(.02)
  else:stop='monitor_timeout';run(['systemctl','--user','stop',unit])
 text=log.read_text() if log.exists()else ''
 ok=not stop and stats.get('ExecMainStatus')=='0' and text.count('RESULT ')==3 and 'PASS serial native only'in text
 run(['systemctl','--user','stop',unit]);post=run(['systemctl','--user','show',unit,'-p','MainPID','-p','ActiveState']).stdout
 save(P/'raw_logs'/f'{mode}-outcome.json',{'passed':ok,'stop':stop,'systemd_before_stop':stats,'post_stop':post,'peak_sampled_rss_kib':peak_rss,'peak_sampled_threads':peak_threads,'calls':text.count('RESULT '),'scope':'single main OS thread C API, no WASI, no Go binding, no business/gas certification'})
 with (P/'PROGRESS.md').open('a')as f:f.write('\n串行 '+mode+' 结束，passed='+str(ok)+'；结果和退出状态见raw_logs/'+mode+'-outcome.json。\n')
 if not ok:raise SystemExit('Stopped after failed serial check; no further scenario')
