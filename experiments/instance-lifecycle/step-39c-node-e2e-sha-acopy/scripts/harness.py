from pathlib import Path
import os,sys,json,time,socket,select,subprocess,threading,hashlib,shutil,http.client,base64,yaml
P=Path(__file__).resolve().parents[1];R=Path('/home/frankie/mygitprojects');H=Path(os.environ.get('STEP36_HOME','/tmp/cvw-step36-empty'));LIB=R/'.worktrees/cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/libraries/patched';SOURCE=Path('/tmp/cvw-step39c-template');GUARD_R=1536*1024;GUARD_T=220
# Reuse proven monitor and shutdown checks, not the original pool.
import importlib.util
spec=importlib.util.spec_from_file_location('owner_monitor',P/'scripts/monitor.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
class Node(old.Node):
 def __init__(self,label,group='E0',ready=True):
  assert not (P/'STOP_SHARED.json').exists(), 'shared infrastructure stop retained'
  # Port/config/file policy remains the inherited isolated monitor; override its module constants only in this process.
  old.P=P;old.H=H;old.LIB=LIB;os.environ['E39_MODE']='B'if group=='E3'else'A'
  os.environ['STEP35_NODE_BINARY']='node4'
  try:super().__init__(label,int(group in ['E1','E2','E3']))
  except BaseException as e:(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'error':repr(e),'stage':'node_startup'}));raise
  if not ready:return
  deadline=time.monotonic()+8
  while time.monotonic()<deadline:
   if self.reason:self.close();raise RuntimeError(self.reason)
   if '"event":"proposer_ready",' in self.log.read_text() and '"ready":true'in self.log.read_text():break
   threading.Event().wait(.002)
  else:self.close();raise RuntimeError('no observed Solo proposer readiness')
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
 else:shutil.copytree(source,dest,ignore=shutil.ignore_patterns('drain*.sock','manager.sock','sdk.log*'))
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
