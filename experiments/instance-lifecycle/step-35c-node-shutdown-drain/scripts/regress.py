from node_smoke import Node,Client,jobs,P,H,record,good
from diagnose import control,snapshot,reset
from observe_run import ctl
import threading,time,subprocess,json,sys

def wait(n,predicate,seconds=20):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if n.reason:raise RuntimeError(n.reason)
  if predicate():return
  threading.Event().wait(.001)
 raise RuntimeError('diagnostic event timeout')
def signal(n):subprocess.run(['systemctl','--user','kill','--signal=SIGTERM',n.unit],check=True,capture_output=True)
def main():
 label,case=sys.argv[1:];n=Node(label);c=None;out={};res={};threads=[]
 try:
  c=Client(label)
  if case=='normal':
   for i in range(2):
    for j in [jobs(str(8101+i*10))[0],jobs(str(8101+i*10))[-1]]:j['Tag']='w'+str(i)+'-'+j['Tag'];record(c,j)
    snapshot(label,'wave'+str(i))
   snapshot(label,'idle0');snapshot(label,'idle1');snapshot(label,'idle2')
  elif case in ['reset','reset_after']:
   if case=='reset_after':record(c,jobs()[0])
   reset(label,'one');reset(label,'two');snapshot(label,'after-reset')
   if case=='reset_after':
    record(c,jobs('8101')[0]);record(c,jobs('8101')[-1])
  elif case in ['active','writer','reset_stop','active_reset_stop']:
   def request():
    try:res['row']=c.call(jobs('8101')[-1 if case=='active'else 0]);good(res['row'])
    except BaseException as e:res['error']=repr(e)
   if case in ['active','writer','active_reset_stop']:
    t=threading.Thread(target=request);t.start();threads.append(t)
    wait(n,lambda:'"event":"invoke_begin"'in n.log.read_text())
   if case in ['reset_stop','active_reset_stop']:
    def resetting():
     try:out['reset']=reset(label,'overlap')
     except BaseException as e:out['reset_error']=repr(e)
    rt=threading.Thread(target=resetting);rt.start();threads.append(rt)
    if case=='reset_stop':wait(n,lambda:ctl('/state')['phase']=='reset_cleanup')
    else:wait(n,lambda:control('/state')['resetting'])
   if case=='writer':wait(n,lambda:ctl('/state')['phase']=='db_write')
   signal(n)
   if case in ['writer','reset_stop']:
    target='"event":"rpc_stop_begin"'if case=='writer'else'"event":"stop_requested"'
    wait(n,lambda:target in n.log.read_text())
    out['no_db_close_before_release']='"event":"db_close_begin"'not in n.log.read_text()
    out['release']=ctl('/release');assert out['no_db_close_before_release']
   for t in threads:t.join(30);assert not t.is_alive()
   out['business']=res
   assert 'error'not in res and'reset_error'not in out,out
  elif case=='idle':pass
  else:raise ValueError(case)
 finally:
  if c:c.close()
  result=n.close();out['node']=result;(P/'raw_logs'/f'{label}-case.json').write_text(json.dumps(out,indent=2))
  passed=not result['reason']and result['systemd'].get('ExecMainStatus')=='0'and result['pid_exited']and result['cgroup_empty']and result['owner']and result['owner']['managed_pending']==0
  if not passed:(P/'STOP.json').write_text(json.dumps({'label':label,'reason':result,'action':'stop all regression, inspect'}))
  assert passed,result
  with(P/'PROGRESS.md').open('a')as f:f.write('\nRegression '+label+' '+case+' PASS; raw logs and counts persisted.\n')
if __name__=='__main__':main()
