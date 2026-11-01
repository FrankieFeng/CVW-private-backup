from pathlib import Path
import subprocess,json,os,time,socket,threading,signal,hashlib,select,sys
P=Path(__file__).resolve().parents[1];R=Path('/home/frankie/mygitprojects');H=Path(os.environ.get('STEP35_HOME','/tmp/cvw-step35-isolated'));LIB=P/'libraries'/os.environ['STEP35B_VARIANT'];GUARD_R=1536*1024;GUARD_T=220
class Node:
 def __init__(self,label,copy=0):
  self.label=label;self.unit='step35b-node-'+label;self.log=P/'raw_logs'/f'{label}-node.log';assert not self.log.exists();self.stopmon=threading.Event();self.reason='';self.peakR=self.peakT=0;self.pid=0;self.pids=set();self.cgroup=''
  native=LIB/'libwasmer.so';assert native.exists(); native_sha=hashlib.sha256(native.read_bytes()).hexdigest()
  env={'CM_SAFE_FRESH_NODE':'1','CM_SAFE_FRESH_CONFIG':'native6.0.1/'+native_sha+'/compiler-locked/gas-step34/maxpages512/v35b','CM_STATIC_MEMORY_COPY':str(copy),'CM_REUSE_EXPERIMENT':'R1','CM_STEP21A_POOL':'capacity','CM_STEP21A_STORE_GUARD':'1','CM_STEP21_OBSERVE':'1','LD_LIBRARY_PATH':str(LIB),'GOMAXPROCS':'2','GOGC':'100','CM_STEP35A_CONTROL':str(H/'manager.sock')}
  self.argv=['systemd-run','--user','--unit='+self.unit,'-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=180s','-p','TimeoutStopSec=10s','-p','KillMode=control-group','-p','RemainAfterExit=yes','-p','StandardOutput=append:'+str(self.log),'-p','StandardError=inherit','--working-directory='+str(H)]+['--setenv='+k+'='+v for k,v in env.items()]+[str(P/'binaries'/os.environ.get('STEP35_NODE_BINARY','node')),'start','-c',str(H/'config/wx-org1.chainmaker.org/chainmaker.yml')]
  (P/'raw_logs'/f'{label}-command.json').write_text(json.dumps({'argv':self.argv,'native_sha':hashlib.sha256(native.read_bytes()).hexdigest(),'binary_sha':hashlib.sha256((P/'binaries'/os.environ.get('STEP35_NODE_BINARY','node')).read_bytes()).hexdigest()},indent=2));subprocess.run(self.argv,check=True,capture_output=True);self.thread=threading.Thread(target=self.monitor,daemon=True);self.thread.start();deadline=time.monotonic()+45
  while time.monotonic()<deadline:
   if self.reason:
    self.close();raise RuntimeError(self.reason)
   try:
    with socket.create_connection(('127.0.0.1',27535),.2):return
   except OSError:time.sleep(.05)
  self.close();raise RuntimeError('RPC startup timeout')
 def props(self):return dict(x.split('=',1)for x in subprocess.check_output(['systemctl','--user','show',self.unit,'-p','MainPID','-p','ExecMainStatus','-p','Result','-p','ActiveState','-p','ControlGroup'],text=True).splitlines()if'='in x)
 def monitor(self):
  with(P/'raw_logs'/f'{self.label}-resources.jsonl').open('w')as f:
   while not self.stopmon.is_set():
    d=self.props();self.pid=int(d.get('MainPID','0'));rss=threads=0
    if self.pid:self.pids.add(self.pid)
    if d.get('ControlGroup'):self.cgroup=d['ControlGroup']
    try:
     st=dict(x.split(':',1)for x in Path(f'/proc/{self.pid}/status').read_text().splitlines()if':'in x);rss=int(st['VmRSS'].split()[0]);threads=int(st['Threads']);self.peakR=max(self.peakR,rss);self.peakT=max(self.peakT,threads)
     mp=P/'raw_logs'/f'{self.label}-loaded-maps.txt'
     if not mp.exists():
      lines=[x for x in Path(f'/proc/{self.pid}/maps').read_text().splitlines()if 'libwasmer'in x]
      if lines:mp.write_text('\n'.join(lines)+'\n')
    except (FileNotFoundError,ProcessLookupError,KeyError):pass
    mem=dict(x.split(':',1)for x in Path('/proc/meminfo').read_text().splitlines()if':'in x);avail=int(mem['MemAvailable'].split()[0]);swap=int(mem['SwapTotal'].split()[0])-int(mem['SwapFree'].split()[0]);f.write(json.dumps({'monotonic_s':time.monotonic(),'rss_kib':rss,'threads':threads,'available_kib':avail,'swap_kib':swap,'systemd':d})+'\n');f.flush()
    if rss>GUARD_R or threads>GUARD_T or avail<8*1024**2 or swap>1024**2:
     self.reason='resource_guard';subprocess.run(['systemctl','--user','kill','--signal=SIGTERM',self.unit],capture_output=True);return
    if d.get('ActiveState')=='failed':self.reason='node_failed';return
    self.stopmon.wait(.025)
 def close(self):
  begin=time.monotonic();subprocess.run(['systemctl','--user','stop',self.unit],capture_output=True);self.stopmon.set();self.thread.join(2);d=self.props();txt=self.log.read_text(errors='replace');owners=[json.loads(x[8:])for x in txt.splitlines()if x.startswith('STEP21C ')and 'owner_closed'in x];out={'label':self.label,'reason':self.reason,'peak_rss_kib':self.peakR,'peak_threads':self.peakT,'stop_s':time.monotonic()-begin,'systemd':d,'owner':owners[-1]if owners else None,'owned_pids':sorted(self.pids),'pid_exited':all(not Path(f'/proc/{pid}').exists()for pid in self.pids)};cg=Path('/sys/fs/cgroup')/self.cgroup.lstrip('/');out['cgroup_empty']=not self.cgroup or not cg.exists()or not(cg/'cgroup.procs').read_text().strip();(P/'raw_logs'/f'{self.label}-outcome.json').write_text(json.dumps(out,indent=2));print(out,flush=True);return out
class Client:
 def __init__(self,label):
  self.label=label;env=dict(os.environ,STEP17_ROOT=str(H),STEP17_ADMIN=str(R/'chainmaker-go/build/crypto-config/wx-org1.chainmaker.org/user/admin1/admin1'));self.log=(P/'raw_logs'/f'{label}-client.jsonl').open('a');self.p=subprocess.Popen([str(P/'binaries/client1')],cwd=H,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=open(P/'raw_logs'/f'{label}-client.stderr','a'),text=True)
 def call(self,job):
  job=dict(Mode='baseline',**job);self.p.stdin.write(json.dumps([job])+'\n');self.p.stdin.flush();deadline=time.monotonic()+70
  while time.monotonic()<deadline:
   ready,_,_=select.select([self.p.stdout],[],[],.25)
   if not ready:continue
   line=self.p.stdout.readline()
   if not line:raise RuntimeError('client exited')
   if line.startswith('RESULT '):
    row=json.loads(line[7:])[0];self.log.write(json.dumps({'input':job,'result':row})+'\n');self.log.flush();print(job.get('Tag'),row.get('error'),(row.get('response')or{}).get('code'),flush=True);return row
  raise RuntimeError('client bound timeout')
 def close(self):
  self.p.stdin.close()
  try:self.p.wait(timeout=5)
  except subprocess.TimeoutExpired:self.p.terminate();self.p.wait(timeout=5)
  self.log.close()
def good(row):
 resp=row.get('response')or{};cr=resp.get('contract_result')or{};assert row.get('response') is not None and not row.get('error')and resp.get('code',0)==0 and cr.get('code',0)==0,row;return resp
def record(c,job,expect=True):
 row=c.call(job);resp=good(row)if expect else row.get('response',{});tx=resp.get('tx_id');
 if tx:
  rw=c.call({'Op':'rwset','Path':tx,'Tag':job['Tag']+'-committed'});assert not rw.get('error')and rw.get('transaction'),rw
 return row
FROM='8acfaca5eeec9f6f7c23c4ffac969b86f27799b0';TO='818fac1ac51525aeedf619a9a339b95854930159'
def jobs(token='1001'):
 return [dict(Op='invoke',Contract='compute',Method='bigNumCal',Params={},Tag='bigNumCal'),dict(Op='invoke',Contract='fact',Method='saveAndFindByFileHash',Params={'file_hash':'005521f27d745a04999c6d09f559764f9c44376a','file_name':'aoteman.jpg','time':'1792827547'},Tag='fact'),dict(Op='invoke',Contract='erc721',Method='mint',Params={'to':FROM,'tokenId':token,'metadata':'http://chainmaker.org.cn/'},Tag='mint'),dict(Op='invoke',Contract='exchange',Method='buyNow',Params={'from':FROM,'to':TO,'tokenId':str(int(token)+1),'metadata':'http://chainmaker.org.cn/'},Tag='buyNow')]
def main():
 label=sys.argv[1];action=sys.argv[2];n=Node(label,int(sys.argv[3])if len(sys.argv)>3 else 0);c=None
 try:
  c=Client(label)
  if action=='deploy':
   manifest=json.loads((P/'inputs/manifest.json').read_text())
   for name in ['compute','fact','identity','erc721','exchange']:
    args={'name':'huanletoken','symbol':'hlt','tokenURI':'https://chainmaker.org.cn'}if name=='erc721'else{}
    record(c,dict(Op='deploy',Contract=name,Path=manifest[name]['path'],Params=args,Tag='deploy-'+name))
  if action in ['deploy','repeat','converge']:
   waves=int(os.environ.get('STEP35_WAVES','2'))if action=='converge'else 1;assert 1<=waves<=6
   for wave in range(waves):
    for j in jobs(str(int(os.environ.get('STEP35_TOKEN_BASE','3001'))+wave*10)if action=='converge'else'1001'if action=='deploy'else'2001'):
     j['Tag']=str(wave)+'-'+j['Tag'] if action=='converge'else j['Tag'];record(c,j)
   for token in ([os.environ.get('STEP35_TOKEN_BASE','3001'),str(int(os.environ.get('STEP35_TOKEN_BASE','3001'))+1)]if action=='converge'else['1001','1002']if action=='deploy'else['2001','2002']):
    row=c.call(dict(Op='query',Contract='erc721',Method='ownerOf',Params={'tokenId':token},Tag='owner-'+token));good(row)
   row=record(c,dict(Op='invoke',Contract='exchange',Method='buyNow',Params=jobs(os.environ.get('STEP35_TOKEN_BASE','3001')if action=='converge'else'1001'if action=='deploy'else'2001')[-1]['Params'],Tag='duplicate-buyNow'),False);resp=row.get('response')or{};assert resp.get('code',0)!=0 or(resp.get('contract_result')or{}).get('code',0)!=0,'duplicate unexpectedly succeeded'
  elif action=='inflight':
   # Observe actual entry before signalling. Cold cache makes this a real accepted VM job, no artificial hold/Sleep.
   done=threading.Event()
   def stop_active():
    deadline=time.monotonic()+20
    while time.monotonic()<deadline and not done.is_set():
     txt=n.log.read_text(errors='replace')
     if '"event":"invoke_begin"'in txt:
      stamp={'event':'SIGTERM_after_actual_invoke_begin','monotonic_s':time.monotonic(),'pid':n.pid};(P/'raw_logs'/f'{label}-stop-trigger.json').write_text(json.dumps(stamp));subprocess.run(['systemctl','--user','kill','--signal=SIGTERM',n.unit],capture_output=True);return
     done.wait(.001)
   th=threading.Thread(target=stop_active);th.start()
   try:c.call(jobs()[0])
   finally:done.set();th.join(2)
  assert not n.reason,n.reason
 finally:
  if c:c.close()
  out=n.close()
  with(P/'PROGRESS.md').open('a')as f:f.write('\nNode '+label+' finished; action='+action+'; outcome='+json.dumps(out)+'\n')
if __name__=='__main__':main()
