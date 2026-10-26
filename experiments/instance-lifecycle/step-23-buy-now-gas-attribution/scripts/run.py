"""One root per isolated, bounded process. Resume from saved outcomes, never rerun labels."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,time
P=Path(__file__).resolve().parents[1]
M=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-23-buy-now-gas-attribution')
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def mirror():
 for folder in ['audit','inputs','raw_logs']:
  for f in(P/folder).rglob('*'):
   if f.is_file():d=M/f.relative_to(P);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
 for name in ['PROGRESS.md','HISTORICAL_AUDIT.md','environment.json','state.json','STOP.json']:
  if(P/name).exists():shutil.copyfile(P/name,M/name)
def resources():
 d={l.split(':',1)[0]:int(l.split()[1])for l in Path('/proc/meminfo').read_text().splitlines()if l.startswith(('MemAvailable:','SwapTotal:','SwapFree:'))}
 return d['MemAvailable'],d['SwapTotal']-d['SwapFree']
def run(a):
 outcome=P/'raw_logs'/f'{a.label}-outcome.json'
 if outcome.exists():
  o=json.loads(outcome.read_text());assert o['passed'],'retained failure; inspect STOP';print('retained',a.label,flush=True);return o
 assert not(P/'STOP.json').exists(),'STOP retained; do not bypass'
 log=P/'raw_logs'/f'{a.label}.log';assert not log.exists(),'partial run: inspect active unit before recovery'
 av,sw=resources();assert av>=8*1024**2 and sw<=1024**2
 build=json.loads((P/'environment.json').read_text());binary=Path(build['binary']);assert hashlib.sha256(binary.read_bytes()).hexdigest()==build['binary_sha']
 native=P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so';assert hashlib.sha256(native.read_bytes()).hexdigest()==build['settings']['native_sha']
 policy='R0'if a.condition=='R0'else'R1'
 env=dict(E22_ENABLED='1',E22_CONFIG_SHA=build['config_sha'],E_COUNTERS=str(P/'inputs/gas-slots.json'),E_GAS_TRACE='1'if a.probe=='on'else'0',E23_CONDITION=a.condition,E23_STAGE=a.stage,E23_BLOCK=str(a.block),E23_LABEL=a.label,E23_INPUTS=str(P/'inputs/business.json'),D_POLICY=policy,D_N='1',D_MANIFEST=str(P/'inputs/manifest.json'),D_OUTPUT=str(P/'raw_logs'/f'{a.label}-receipts'),CM_REUSE_EXPERIMENT=policy,CM_STEP21A_POOL='capacity',CM_STEP21A_STORE_GUARD='1',CM_STEP21_OBSERVE='1',GOMAXPROCS='2',GOGC='100',LD_LIBRARY_PATH=str(native.parent))
 unit='step23-'+a.label
 cmd=['systemd-run','--user','--unit='+unit,'-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=60s','-p','TimeoutStopSec=5s','-p','KillMode=control-group','-p','RemainAfterExit=yes','-p','StandardOutput=append:'+str(log),'-p','StandardError=inherit','--working-directory='+str(P/'source/vm')]+['--setenv='+k+'='+v for k,v in env.items()]+[str(binary),'-test.run=^TestStep23BuyNow$','-test.v','-test.count=1','-test.timeout=45s']
 save(P/'raw_logs'/f'{a.label}-command.json',dict(argv=cmd,binary_sha=build['binary_sha'],env=env))
 save(P/'state.json',dict(phase=a.stage,active_unit=unit,label=a.label,next_action='inspect unit/outcome before retry, never duplicate label'))
 with(P/'PROGRESS.md').open('a')as f:f.write(f'\n开始 {a.label}，condition={a.condition} probe={a.probe} stage={a.stage} block={a.block}；unit={unit}，每进程最多1根。\n')
 mirror();r=subprocess.run(cmd,capture_output=True,text=True);save(P/'raw_logs'/f'{a.label}-launch.json',dict(exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stderr
 start=time.monotonic();peak_rss=peak_threads=0;stats={};reason='exited';pid=0
 try:
  with(P/'raw_logs'/f'{a.label}-resources.jsonl').open('w')as f:
   while time.monotonic()-start<65:
    z=subprocess.run(['systemctl','--user','show',unit,'-p','MainPID','-p','ExecMainStatus','-p','ActiveState','-p','SubState','-p','Result'],capture_output=True,text=True,check=True)
    stats=dict(l.split('=',1)for l in z.stdout.splitlines()if'='in l);pid=int(stats.get('MainPID','0'));rss=threads=0
    if pid:
     try:
      d=dict(l.split(':',1)for l in Path(f'/proc/{pid}/status').read_text().splitlines()if':'in l);rss=int(d.get('VmRSS','0').split()[0]);threads=int(d.get('Threads','0'))
     except FileNotFoundError:pass
    peak_rss=max(peak_rss,rss);peak_threads=max(peak_threads,threads);av,sw=resources()
    f.write(json.dumps(dict(elapsed_s=time.monotonic()-start,rss_kib=rss,threads=threads,available_kib=av,swap_kib=sw,systemd=stats))+'\n');f.flush()
    if rss>1536*1024 or threads>220 or av<8*1024**2 or sw>1024**2:reason='resource_guard';break
    if stats.get('SubState')=='exited'or stats.get('ActiveState')in ['failed','inactive']:break
    time.sleep(.025)
   else:reason='monitor_timeout'
 finally:
  subprocess.run(['systemctl','--user','stop',unit],capture_output=True,timeout=10)
 assert not pid or not Path(f'/proc/{pid}').exists(),'owned process survived stop'
 text=log.read_text(errors='replace');events=[];calls=[]
 for line in text.splitlines():
  if line.startswith('STEP23 '):
   x=json.loads(line[7:]);events.append(x)
   if x['event']=='call_record':calls.append(x)
 target=[c for c in calls if c['record']['tx_id']=='step21c-buy-001']
 passed=(reason=='exited'and stats.get('ExecMainStatus')=='0'and'--- PASS: TestStep23BuyNow'in text and'--- FAIL:'not in text and'panic:'not in text and'fatal error:'not in text and'"event":"owner_closed"'in text and len(target)==7 and all(c['record']['actual_result'].get('code',0)==0 and c['record']['call_error_observed']=='<nil>'for c in target))
 with(P/'raw_logs'/f'{a.label}-events.jsonl').open('w')as f:
  for c in events:f.write(json.dumps(c,sort_keys=True)+'\n')
 o=dict(label=a.label,condition=a.condition,probe=a.probe,stage=a.stage,block=a.block,passed=passed,reason=reason,systemd=stats,peak_sampled_rss_kib=peak_rss,peak_sampled_threads=peak_threads,wall_s=time.monotonic()-start,all_owned_processes_stopped=True,root_gas=next((c['record']['gas_out_cumulative']for c in target if c['record']['depth']==0),None))
 save(outcome,o)
 if not passed:save(P/'STOP.json',dict(stop_all=True,label=a.label,reason=reason))
 with(P/'PROGRESS.md').open('a')as f:f.write('\n结束 '+a.label+'：'+json.dumps(o,ensure_ascii=False)+'。原日志/events/receipt/资源即时落盘；'+('只分析失败，停止后续运行。'if not passed else'下一步核对当前块，再继续已登记阶段。')+'\n')
 save(P/'state.json',dict(phase=a.stage if passed else'stopped',active_unit=None,last=a.label,next_action='inspect data then registered next block'if passed else'analyze retained failure only'))
 mirror();print(json.dumps(o),flush=True);return o
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('condition',choices=['R0','R1','C1']);p.add_argument('--stage',choices=['preflight','lifecycle','copy'],default='preflight');p.add_argument('--block',type=int,default=0);p.add_argument('--probe',choices=['on','off'],default='on');a=p.parse_args()
 if not run(a)['passed']:raise SystemExit(2)
