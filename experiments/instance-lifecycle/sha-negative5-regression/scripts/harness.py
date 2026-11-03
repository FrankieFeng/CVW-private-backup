from pathlib import Path
import os,sys,json,time,socket,select,subprocess,threading,hashlib,shutil,http.client,base64,yaml
P=Path(__file__).resolve().parents[1];R=Path('/home/frankie/mygitprojects');H=Path(os.environ.get('STEP36_HOME','/tmp/cvw-step36-empty'));LIB=R/'.worktrees/cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/libraries/patched';SOURCE=Path('/tmp/cvw-shaneg5-template');GUARD_R=1536*1024;GUARD_T=220
# Reuse proven monitor and shutdown checks, not the original pool.
import importlib.util
spec=importlib.util.spec_from_file_location('owner_monitor',P/'scripts/monitor.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
class Node(old.Node):
 def __init__(self,label,group='G0',ready=True):
  launch_begin=time.monotonic_ns()
  assert not (P/'STOP_SHARED.json').exists(), 'shared infrastructure stop retained'
  # Port/config/file policy remains the inherited isolated monitor; override its module constants only in this process.
  old.P=P;old.H=H;old.LIB=LIB;os.environ['E39_MODE']='B'if group=='G4'else'A'
  os.environ['STEP35_NODE_BINARY']='node-ready'
  try:super().__init__(label,int(group in ['G1','G3','G4']))
  except BaseException as e:(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'error':repr(e),'stage':'node_startup'}));raise
  self.launch_begin_ns=launch_begin
  if not ready:return
  try:self.preflight=ready_gate(label+'-preflight')
  except BaseException as e:
   self.close();(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'stage':'readiness','error':repr(e)}));raise
  self.preflight['launch_to_gate_ns']=time.monotonic_ns()-launch_begin
  (P/'raw_logs'/f'{label}-preflight.json').write_text(json.dumps(self.preflight,indent=2))

class Client:
 def __init__(self,label):
  self.label=label;self.log=(P/'raw_logs'/f'{label}-client.jsonl').open('a');self.stderr=(P/'raw_logs'/f'{label}-client.stderr').open('a');env=dict(os.environ,STEP39C_UPGRADE_ADMINS=','.join(str(R/f'chainmaker-go/build/crypto-config/wx-org{i}.chainmaker.org/user/admin1/admin1')for i in [1,2,3]),STEP36_REQUEST_NAMESPACE=label,STEP17_ROOT=str(H),STEP17_ADMIN=str(R/'chainmaker-go/build/crypto-config/wx-org1.chainmaker.org/user/admin1/admin1'))
  self.p=subprocess.Popen([str(P/'binaries/client3')],cwd=H,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,text=True)
 def batch(self,jobs):
  self.p.stdin.write(json.dumps(jobs,separators=(',',':'))+'\n');self.p.stdin.flush();deadline=time.monotonic()+min(150,65*len(jobs))
  while time.monotonic()<deadline:
   ready,_,_=select.select([self.p.stdout],[],[],.2)
   if not ready:continue
   line=self.p.stdout.readline()
   if not line:raise RuntimeError('client exited')
   if line.startswith('RESULT '):
    x=json.loads(line[7:]);self.log.write(json.dumps(x,separators=(',',':'))+'\n');self.log.flush();return x
  raise RuntimeError('client response timeout')
 def close(self):
  self.p.stdin.close()
  try:self.p.wait(timeout=5)
  except subprocess.TimeoutExpired:self.p.terminate();self.p.wait(timeout=5)
  self.log.close();self.stderr.close()
def clone(source,dest,clean=False):
 assert not dest.exists(),str(dest)
 if clean:
  dest.mkdir();shutil.copytree(source/'config',dest/'config');shutil.copytree(source/'network',dest/'network')
 else:shutil.copytree(source,dest,ignore=shutil.ignore_patterns('drain*.sock','manager.sock','readiness.sock','sdk.log*'))
 for f in dest.rglob('*.yml'):f.write_text(f.read_text().replace(str(source),str(dest)))
def good(row):
 assert row.get('success')and row.get('response')is not None,{'error':row.get('error'),'success':row.get('success'),'see':'raw client log'}
 r=row['response'];assert r.get('code',0)==0 and (r.get('contract_result')or{}).get('code',0)==0,row
 return r
class UnixHTTP(http.client.HTTPConnection):
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(self.timeout);self.sock.connect(str(H/('drain-'+sys.argv[1]+'.sock')))
def verify_state(projection,label):
 req=[{'Contract':c,'Key':k,'Expected':v}for(c,k),v in projection.items()];cc=UnixHTTP('localhost',timeout=10);cc.request('POST','/verify-state',json.dumps(req),{'Content-Type':'application/json'});resp=cc.getresponse();data=json.loads(resp.read());cc.close();(P/'raw_logs'/f'{label}-state.json').write_text(json.dumps(data,indent=2));assert resp.status==200 and all(x['match']and x['error']=='<nil>'for x in data),data;return data

class ManagerHTTP(http.client.HTTPConnection):
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(self.timeout);self.sock.connect(str(H/'manager.sock'))
def manager(endpoint,post=False):
 cc=ManagerHTTP('localhost',timeout=15);cc.request('POST'if post else'GET','/'+endpoint);resp=cc.getresponse();x=json.loads(resp.read());cc.close();assert resp.status==200,(resp.status,x)
 if isinstance(x,dict)and'items'in x:x['items']=sorted(x['items'],key=lambda a:(a['name'],a['version'],a['sha']))
 return x

class ReadinessHTTP(http.client.HTTPConnection):
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(self.timeout);self.sock.connect(str(H/'readiness.sock'))
def ready_gate(label,min_height=0):
 deadline=time.monotonic()+15;observations=[]
 while time.monotonic()<deadline:
  try:
   cc=ReadinessHTTP('localhost',timeout=4);cc.request('GET','/ready?min_height='+str(min_height));res=cc.getresponse();x=json.loads(res.read());cc.close();observations.append(x)
   if x.get('error'):raise RuntimeError('readiness rejected: '+x['error'])
   if x.get('passed'):
    st=x['state'];assert st['chain']=='step35'and st['run']==sys.argv[1]and st['ready']and st['completed']==st['notified']and st['last_completed_height']>=min_height and not st['consumer_active']and len(x['fence_ids'])==2
    out={'passed':True,'observations':observations,'final':x};(P/'raw_logs'/f'{label}-gate.json').write_text(json.dumps(out,indent=2));return out
  except (FileNotFoundError,ConnectionRefusedError):pass
  threading.Event().wait(.02)
 out={'passed':False,'observations':observations,'error':'readiness timeout15s'};(P/'raw_logs'/f'{label}-gate.json').write_text(json.dumps(out,indent=2));raise RuntimeError(out['error'])
