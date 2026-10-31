from pathlib import Path
import subprocess,json,os,time,hashlib
P=Path(__file__).resolve().parents[1];B=Path('/home/frankie/mygitprojects/.worktrees/cvw-step34/experiments/instance-lifecycle/step-34-safe-fresh-runtime');NATIVE=P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so';assert hashlib.sha256(NATIVE.read_bytes()).hexdigest()=='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9'
def run(name,copy):
 label=os.environ.get('STEP35_TEST_LABEL',f'manager-{name}-copy{copy}');log=P/'raw_logs'/f'{label}.log';assert not log.exists();manifest=B/'inputs'/('exchange-smoke-G0-manifest.json' if name=='exchange'else name+'-smoke-manifest.json');env={'CM_SAFE_FRESH_NODE':'1','CM_SAFE_FRESH_CONFIG':'native6.0.1/dcdfa716/compiler-original/gas-step34/maxpages512/v35','CM_STATIC_MEMORY_COPY':str(copy),'CM_REUSE_EXPERIMENT':'R1','CM_STEP21A_POOL':'capacity','CM_STEP21A_STORE_GUARD':'1','CM_STEP21_OBSERVE':'1','D_POLICY':'R1','D_MANIFEST':str(manifest),'D_OUTPUT':str(P/'raw_logs'/f'{label}-receipts'),'E22_CONTRACT':name,'LD_LIBRARY_PATH':str(NATIVE.parent),'GOMAXPROCS':'2'}
 argv=['systemd-run','--user','--unit=step35-'+label,'--collect','-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=60s','-p','TimeoutStopSec=5s','-p','KillMode=control-group','-p','StandardOutput=append:'+str(log),'-p','StandardError=inherit','--working-directory='+str(P/'source/vm')]+['--setenv='+k+'='+v for k,v in env.items()]+[str(P/'binaries/vm5.test'),'-test.run=^TestStep35Manager$','-test.v','-test.timeout=45s'];(P/'raw_logs'/f'{label}-command.json').write_text(json.dumps(argv,indent=2));subprocess.run(argv,check=True,capture_output=True);unit='step35-'+label;start=time.monotonic();peakR=peakT=0;failure=''
 while time.monotonic()-start<65:
  props=dict(x.split('=',1)for x in subprocess.check_output(['systemctl','--user','show',unit,'-p','MainPID','-p','ActiveState'],text=True).splitlines()if'='in x);pid=int(props.get('MainPID','0'))
  if pid:
   try:
    st=dict(x.split(':',1)for x in Path(f'/proc/{pid}/status').read_text().splitlines()if':'in x);rss=int(st['VmRSS'].split()[0]);threads=int(st['Threads']);peakR=max(peakR,rss);peakT=max(peakT,threads)
    if rss>1536*1024 or threads>220:failure='resource guard';break
   except (FileNotFoundError,ProcessLookupError,KeyError):pass
  if props.get('ActiveState')in ['inactive','failed']:break
  time.sleep(.025)
 subprocess.run(['systemctl','--user','stop',unit],capture_output=True);txt=log.read_text();out={'label':label,'passed':not failure and '--- PASS: TestStep35Manager'in txt and '--- FAIL:'not in txt,'peak_rss_kib':peakR,'peak_threads':peakT,'reason':failure,'wall_s':time.monotonic()-start};(P/'raw_logs'/f'{label}-outcome.json').write_text(json.dumps(out,indent=2));print(out,flush=True);assert out['passed'],txt[-4500:]
if __name__=='__main__':
 import sys
 run(sys.argv[1],int(sys.argv[2]))
