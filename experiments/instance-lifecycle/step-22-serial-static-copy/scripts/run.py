from pathlib import Path
import argparse,subprocess,json,time,hashlib,sys,shutil
P=Path(__file__).resolve().parents[1]
MIRROR=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-22-serial-static-copy')
def save(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def mirror():
 for folder in ['audit','raw_logs','inputs']:
  for f in (P/folder).rglob('*'):
   if f.is_file():d=MIRROR/f.relative_to(P);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
 for name in ['PROGRESS.md','state.json','environment.json','samples.csv','per_run_summary.csv','STOP.json']:
  if (P/name).exists():shutil.copyfile(P/name,MIRROR/name)
def memory():
 d={x.split(':',1)[0]:int(x.split()[1])for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith(('MemAvailable:','SwapTotal:','SwapFree:'))};return d['MemAvailable'],d['SwapTotal']-d['SwapFree']
def run(a):
 label=a.label;out=P/'raw_logs'/f'{label}-outcome.json'
 if out.exists():r=json.loads(out.read_text());print('retained',label,r['passed'],flush=True);return r
 assert not (P/'STOP.json').exists(),'safety stop retained; do not automatically resume'
 log=P/'raw_logs'/f'{label}.log';assert not log.exists(),'incomplete attempt: inspect unit before rerun'
 available,swap=memory();assert available>=8*1024**2 and swap<=1024**2
 native=P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so';assert hashlib.sha256(native.read_bytes()).hexdigest()=='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9'
 test='TestStep22ModuleLifecycle'if a.contract=='probe'else'TestStep22Serial'
 env={'E22_ENABLED':'1','E22_CONTRACT':a.contract,'E22_METHOD':{'compute':'bigNumCal','fact':'saveAndFindByFileHash','erc721':'mint','exchange':'buyNow','probe':''}[a.contract],'E22_SINGLE_VARIANT':a.single,'E22_PHASE':a.phase,'E22_PAIRS':str(a.pairs),'E22_SEED':str(a.seed),'E22_CONFIG_SHA':json.loads((P/'environment.json').read_text())['config_sha'],'CM_REUSE_EXPERIMENT':'R1','CM_STEP21A_POOL':'capacity','CM_STEP21A_STORE_GUARD':'1','CM_STEP21_OBSERVE':'1','D_POLICY':'R1','D_N':'1','D_MANIFEST':str(P/'inputs'/f'{a.contract}-manifest.json'),'D_OUTPUT':str(P/'raw_logs'/f'{label}-receipts'),'GOMAXPROCS':'2','GOGC':'100','LD_LIBRARY_PATH':str(native.parent)}
 binary=Path(a.binary).resolve() if a.binary else P/'binaries/step22.test'
 sha=hashlib.sha256(binary.read_bytes()).hexdigest()
 expected=a.binary_sha if a.binary else json.loads((P/'environment.json').read_text())['binary_sha256']
 assert expected and sha==expected,'explicit expected SHA required for a replay binary'
 unit='step22-'+label
 cmd=['systemd-run','--user','--unit='+unit,'-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=60s','-p','TimeoutStopSec=5s','-p','KillMode=control-group','-p','RemainAfterExit=yes','-p','StandardOutput=append:'+str(log),'-p','StandardError=inherit','--working-directory='+str(P/'source/vm')]+['--setenv='+k+'='+v for k,v in env.items()]+[str(binary),'-test.run=^'+test+'$','-test.v','-test.count=1','-test.timeout=45s']
 save(P/'raw_logs'/f'{label}-command.json',dict(argv=cmd,binary_sha256=sha));state=dict(phase=a.phase,active_unit=unit,label=label,next_action='inspect current unit then read outcome, never relaunch existing label');save(P/'state.json',state)
 with (P/'PROGRESS.md').open('a')as f:f.write('\n即将执行 '+label+'；原始命令已保存，unit='+unit+'，pairs='+str(a.pairs)+'。\n')
 mirror();r=subprocess.run(cmd,capture_output=True,text=True);save(P/'raw_logs'/f'{label}-launch.json',dict(exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stderr
 begin=time.monotonic();stats={};peak_rss=peak_threads=0;reason='exited';pid=0
 with(P/'raw_logs'/f'{label}-resources.jsonl').open('w')as f:
  while time.monotonic()-begin<65:
   z=subprocess.run(['systemctl','--user','show',unit,'-p','MainPID','-p','ExecMainStatus','-p','ActiveState','-p','SubState','-p','Result'],capture_output=True,text=True);stats=dict(x.split('=',1)for x in z.stdout.splitlines()if'='in x);pid=int(stats.get('MainPID','0'));rss=threads=0
   if pid:
    try:
     d=dict(x.split(':',1)for x in Path(f'/proc/{pid}/status').read_text().splitlines()if':'in x);rss=int(d.get('VmRSS','0').split()[0]);threads=int(d.get('Threads','0'))
    except FileNotFoundError:pass
   peak_rss=max(peak_rss,rss);peak_threads=max(peak_threads,threads);av,sw=memory();f.write(json.dumps(dict(elapsed=time.monotonic()-begin,rss_kib=rss,threads=threads,available_kib=av,swap_kib=sw,systemd=stats))+'\n');f.flush()
   if rss>1536*1024 or threads>220 or av<8*1024**2 or sw>1024**2:reason='resource_guard';break
   if stats.get('SubState')=='exited'or stats.get('ActiveState')in['inactive','failed']:break
   time.sleep(.025)
  else:reason='monitor_timeout'
 text=log.read_text(errors='replace')if log.exists()else''
 passed=reason=='exited'and stats.get('ExecMainStatus')=='0'and'--- PASS: '+test in text and'--- FAIL:'not in text and'"event":"owner_closed"'in text and'panic:'not in text and'fatal error:'not in text
 subprocess.run(['systemctl','--user','stop',unit],capture_output=True,timeout=10);assert not pid or not Path(f'/proc/{pid}').exists()
 outcome=dict(label=label,contract=a.contract,phase=a.phase,pairs=a.pairs,seed=a.seed,single=a.single,passed=passed,reason=reason,peak_rss_kib=peak_rss,peak_threads=peak_threads,wall_s=time.monotonic()-begin,systemd=stats,all_owned_processes_stopped=True)
 save(out,outcome)
 if not passed:save(P/'STOP.json',dict(label=label,reason=reason,stop_all=True))
 with(P/'PROGRESS.md').open('a')as f:f.write('\n完成 '+label+'：'+json.dumps(outcome,ensure_ascii=False)+'；日志/资源/receipt已落盘。'+('下一步仅分析失败，禁止续跑。'if not passed else'下一步读取outcome后按登记阶段继续。')+'\n')
 save(P/'state.json',dict(phase='stopped'if not passed else a.phase,active_unit=None,last=label,next_action='analyze only'if not passed else'continue registered next stage'))
 subprocess.run([sys.executable,'-B',str(P/'scripts/reduce_raw.py')],check=True);mirror();print(json.dumps(outcome),flush=True);return outcome
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('contract',choices=['probe','compute','fact','erc721','exchange']);p.add_argument('--pairs',type=int,default=1);p.add_argument('--phase',default='preflight',choices=['probe','preflight','formal']);p.add_argument('--seed',type=int,default=2200);p.add_argument('--single',choices=['','A0','A1'],default='');p.add_argument('--binary',default='');p.add_argument('--binary-sha',default='');a=p.parse_args();assert 1<=a.pairs<=3
 r=run(a)
 if not r['passed']:raise SystemExit(2)
