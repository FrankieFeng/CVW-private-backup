from node_smoke import Node,Client,jobs,P,H,record
import socket,http.client,json,threading,time,subprocess,sys
class U(http.client.HTTPConnection):
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(self.timeout);self.sock.connect(str(H/('drain-'+sys.argv[1]+'.sock')))
def ctl(path):
 c=U('localhost',timeout=2);c.request('POST' if path=='/release' else 'GET',path);r=c.getresponse();x=json.loads(r.read());c.close();return x
def main():
 label,case=sys.argv[1:];n=Node(label);c=None;result={}
 try:
  if case=='idle':return
  c=Client(label)
  def request():
   try:result['row']=record(c,jobs('18001')[0])
   except BaseException as e:result['error']=repr(e)
  t=threading.Thread(target=request);t.start();deadline=time.monotonic()+25
  while time.monotonic()<deadline:
   try:
    if ctl('/state')['phase']=='db_write':break
   except OSError:pass
   if n.reason:raise RuntimeError(n.reason)
   threading.Event().wait(.001)
  else:raise RuntimeError('write hold not reached')
  subprocess.run(['systemctl','--user','kill','--signal=SIGTERM',n.unit],check=True,capture_output=True)
  deadline=time.monotonic()+4;close_seen=False
  while time.monotonic()<deadline:
   if '"event":"db_close_begin"'in n.log.read_text():close_seen=True;break
   if n.props().get('MainPID')=='0':break
   threading.Event().wait(.001)
  try:result['release']=ctl('/release')
  except OSError as e:result['release_error']=repr(e)
  result['db_close_while_writer_held']=close_seen;t.join(20);assert not t.is_alive();(P/'raw_logs'/f'{label}-trigger.json').write_text(json.dumps(result,indent=2))
 finally:
  if c:c.close()
  n.close()
if __name__=='__main__':main()
