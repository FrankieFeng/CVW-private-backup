from pathlib import Path
import subprocess,os,time,json,hashlib,threading,sys,re
P=Path(__file__).resolve().parents[1];ROOT=Path('/home/frankie/mygitprojects');LIB=ROOT/'.worktrees/cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/libraries/patched';SHA='56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc'
def execute(label,part,case='compute_hashCal',strategy='C0',batch='pre',verify=False,alloc=False,test='TestStep39VM',binary_label=None,expect_owner=True):
 assert not(P/'STOP_SHARED.json').exists(),'guard file retained; audit before resume'
 out=P/'raw_logs'/f'{label}-outcome.json'
 if out.exists():
  x=json.loads(out.read_text());assert x['passed'],'failed run preserved; use new label only after diagnosis';return x
 log=P/'raw_logs'/f'{label}.log';assert not log.exists(),'incomplete run retained; inspect process first'
 binary=P/'binaries'/(binary_label or 'vm-perf');assert binary.exists();assert hashlib.sha256((LIB/'libwasmer.so').read_bytes()).hexdigest()==SHA
 env={'LD_LIBRARY_PATH':str(LIB),'GOMAXPROCS':'2','GOGC':'100','E39B_A_WASM':'/home/frankie/mygitprojects/.worktrees/cvw-step36/experiments/instance-lifecycle/step-36-e2e-copy-acopy/inputs/compute-G2.wasm','D_POLICY':'R1','D_MANIFEST':str(P/'inputs'/f'{case}-{strategy}-manifest.json'),'D_OUTPUT':str(P/'raw_logs'/f'{label}-receipts'),'E38_CASE_FILE':str(P/'inputs'/f'{case}-case.json'),'E38_BATCH':str(batch),'E38_STRATEGY':'C0','E39_MODE':('B'if strategy in ['G1','G3']else'A'),'E39B_GROUP':strategy,'E38_VERIFY_MEMORY':str(int(verify)),'E38_ALLOC':str(int(alloc)),'CM_SAFE_FRESH_NODE':'1','CM_SAFE_FRESH_CONFIG':'native6.0.1/'+SHA+'/compiler-locked/gas-step34/maxpages512/v36','CM_STATIC_MEMORY_COPY':'1','CM_REUSE_EXPERIMENT':'R1','CM_STEP21A_POOL':'capacity','CM_STEP21A_STORE_GUARD':'1','CM_STEP21_OBSERVE':'1','CM35C_TRACE':'1'}
 unit='step39b-'+label;cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit='+unit,'-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=90s','-p','TimeoutStopSec=5s','-p','KillMode=control-group','--working-directory='+str(P/'source'/'vm')]+['--setenv='+k+'='+v for k,v in env.items()]+[str(binary),'-test.run=^'+test+'$','-test.v','-test.timeout=75s'];(P/'raw_logs'/f'{label}-command.json').write_text(json.dumps({'argv':cmd,'binary_sha':hashlib.sha256(binary.read_bytes()).hexdigest(),'native_sha':SHA},indent=2))
 peakR=peakT=0;reason='';pid=0;pidset=set();loaded=False
 with log.open('w')as f:
  proc=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);deadline=time.monotonic()+100
  while proc.poll()is None:
   if not pid:
    z=subprocess.run(['systemctl','--user','show',unit,'-p','MainPID','--value'],capture_output=True,text=True)
    if z.stdout.strip().isdigit():pid=int(z.stdout.strip())
   if pid:
    pidset.add(pid)
    try:
     txt=Path(f'/proc/{pid}/status').read_text();v=re.search(r'^VmRSS:\s+(\d+)',txt,re.M);t=re.search(r'^Threads:\s+(\d+)',txt,re.M);rss=int(v[1])if v else 0;th=int(t[1])if t else 0;peakR=max(peakR,rss);peakT=max(peakT,th)
     if not loaded:
      maps='\n'.join(l for l in Path(f'/proc/{pid}/maps').read_text().splitlines()if'libwasmer'in l)
      if maps:(P/'raw_logs'/f'{label}-maps.txt').write_text(maps);loaded=True;assert str(LIB/'libwasmer.so')in maps
     if rss>1536*1024 or th>220:reason='RSS1536MiB/thread220 guard'
    except FileNotFoundError:pass
   if time.monotonic()>deadline:reason='bounded timeout'
   if reason:subprocess.run(['systemctl','--user','kill','--signal=SIGABRT',unit],capture_output=True);break
   time.sleep(.025) # observer polling only; never spaces business requests.
  try:code=proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.kill();code=proc.wait();reason=reason or'observer timeout'
 text=log.read_text();owners=[json.loads(l[8:])for l in text.splitlines()if l.startswith('STEP21C ')and'"owner_closed"'in l];owner=owners[-1]if owners else{};pid_exited=all(not Path(f'/proc/{p}').exists()for p in pidset)
 passed=code==0 and not reason and pid_exited and (not expect_owner or bool(owner)and owner['managed_pending']==0 and owner['stores_created']==owner['stores_closed']and owner['instances_created']==owner['instances_closed'])
 x=dict(label=label,part=part,case=case,strategy=strategy,batch=batch,verify=verify,alloc=alloc,test=test,passed=passed,exit_code=code,rss_peak_mib=peakR/1024,threads_peak=peakT,owner=owner,pid_exited=pid_exited,native_loaded=loaded,reason=reason)
 out.write_text(json.dumps(x,indent=2));print('DONE',label,passed,'rss',round(x['rss_peak_mib'],1),'threads',peakT,flush=True)
 if reason or not pid_exited or owner and(owner.get('managed_pending')!=0 or owner.get('stores_created')!=owner.get('stores_closed')or owner.get('instances_created')!=owner.get('instances_closed')):(P/'STOP_SHARED.json').write_text(json.dumps(x,indent=2))
 with(P/'PROGRESS.md').open('a')as f:f.write('\n'+label+' '+('PASS'if passed else'FAIL')+'; raw log/outcome/command retained.\n')
 assert passed,log.read_text()[-3500:]
 return x
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='memory':execute('memory-A','A',test='TestStep38Memory')
 elif mode=='one':execute(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],batch=sys.argv[6],verify=len(sys.argv)>7 and sys.argv[7]=='verify',alloc=len(sys.argv)>7 and sys.argv[7]=='alloc')
