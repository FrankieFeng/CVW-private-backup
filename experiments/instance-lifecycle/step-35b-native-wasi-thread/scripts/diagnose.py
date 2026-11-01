from pathlib import Path
import os,json,time,threading,socket,http.client,urllib.parse,subprocess,sys
from node_smoke import Node,Client,jobs,record,good,P,H
class UnixHTTP(http.client.HTTPConnection):
 def connect(self):self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(self.timeout);self.sock.connect(str(H/'manager.sock'))
def control(path,method='GET'):
 cc=UnixHTTP('localhost',timeout=20);cc.request(method,path);r=cc.getresponse();data=r.read();cc.close();out=json.loads(data);assert r.status<400,(path,r.status,out);return out
def snapshot(label,tag):
 x=control('/snapshot?tag='+urllib.parse.quote(tag));(P/'raw_logs'/f'{label}-snapshot-{tag}.json').write_text(json.dumps(x,indent=2));assert x['native_diagnostic'].get('store_shared_strong_delete',0)==0, 'native Store delete retained other strong references; stop further calls'
 print('snapshot',tag,'heapMiB',round(x['go_heap']/1024**2,1),'threads',x['os_threads'],'goroutines',x['goroutines'],'cached',x['modules_cached'],flush=True);return x
def reset(label,tag):
 begin=time.monotonic();x=control('/reset','POST');x['wall_elapsed_s']=time.monotonic()-begin;(P/'raw_logs'/f'{label}-reset-{tag}.json').write_text(json.dumps(x,indent=2));assert x['error']=='<nil>',x;print('Manager Reset',tag,x,flush=True);return x
def quiet(label,tag):
 # No business requests in this explicit observation window; not a request interval/performance result.
 for i in range(3):
  if i:threading.Event().wait(.5)
  snapshot(label,tag+str(i))
def call_async(c,job,expect=True):
 result={}
 def f():
  try:result['row']=record(c,job,expect)
  except BaseException as e:result['error']=repr(e)
 th=threading.Thread(target=f);th.start();return th,result
def wait_event(n,offset,kind,deadline=8):
 end=time.monotonic()+deadline
 while time.monotonic()<end:
  if n.reason:raise RuntimeError(n.reason)
  text=n.log.read_text(errors='replace')[offset:]
  for l in text.splitlines():
   if l.startswith('STEP35 '):
    e=json.loads(l[7:])
    if e['event']==kind:return e
  threading.Event().wait(.001)
 raise RuntimeError('missing '+kind)
def main():
 label=sys.argv[1];mode=sys.argv[2];n=Node(label,0);c=c2=None
 try:
  c=Client(label);c2=Client(label+'-second');snapshot(label,'start')
  if mode=='resource':
   # Only two new compute/buyNow waves; reuse existing ledger, no redeploy/fact/mint regression.
   for i in range(int(os.environ.get("STEP35A_WAVES","2"))):
    for j in [jobs(str(int(os.environ.get("STEP35A_TOKEN_BASE","6001"))+10*i))[0],jobs(str(int(os.environ.get("STEP35A_TOKEN_BASE","6001"))+10*i))[-1]]:j['Tag']=f'w{i}-'+j['Tag'];record(c,j)
    snapshot(label,'wave'+str(i))
   quiet(label,'idle')
   reset(label,'idle1');snapshot(label,'after-reset1');reset(label,'idle2');snapshot(label,'after-reset2')
   # No forced GC or scavenging in Step-35B resource admission.
  elif mode in ['inflight','stop-race']:
   reset(label,'empty-idle');snapshot(label,'empty-after-reset')
   for index,name in enumerate(['compute','buyNow'] if mode=='inflight'else['compute']):
    job=jobs(str(7001+index*10))[0 if name=='compute'else -1];job['Tag']='active-'+name
    offset=len(n.log.read_text());th,res=call_async(c,job);entry=wait_event(n,offset,'invoke_begin');rs={}
    def rf():
     try:rs['result']=reset(label,'during-'+name)
     except BaseException as e:rs['error']=repr(e)
    rt=threading.Thread(target=rf);rt.start();state=control('/state');deadline=time.monotonic()+5
    while not state['resetting']and time.monotonic()<deadline:state=control('/state')
    assert state['resetting'],state;(P/'raw_logs'/f'{label}-admission-{name}.json').write_text(json.dumps(state,indent=2))
    if mode=='stop-race':
     subprocess.run(['systemctl','--user','kill','--signal=SIGTERM',n.unit],check=True,capture_output=True)
    else:
     queued=jobs()[0];queued['Tag']='submitted-during-reset-'+name;qt,qr=call_async(c2,queued,False)
    th.join(75);rt.join(25);assert not th.is_alive()and not rt.is_alive();(P/'raw_logs'/f'{label}-active-{name}-result.json').write_text(json.dumps({'business':res,'reset':rs},indent=2));assert 'error'not in rs,rs
    if mode!='stop-race':
     qt.join(75);assert not qt.is_alive()and'error'not in qr,qr;assert 'error'not in res,res;snapshot(label,'after-inflight-'+name)
   if mode!='stop-race':quiet(label,'final-idle')
  assert not n.reason,n.reason
 finally:
  if c:c.close()
  if c2:c2.close()
  out=n.close();with_progress={'label':label,'mode':mode,'outcome':out};
  with(P/'PROGRESS.md').open('a')as f:f.write('\nBounded diagnostic completed: '+json.dumps(with_progress)+'\n')
if __name__=='__main__':main()
