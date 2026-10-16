from run import O,Client,record,restart,specs,modes,job
import os,time
os.environ.pop('CM_INSTANCE_LIFECYCLE_TRACE',None)
os.environ['STEP17_NODE_BINARY']=str(O/'chainmaker-race-bloom');os.environ['GORACE']='log_path='+str(O/'race-node')+' halt_on_error=1'
restart();time.sleep(1);c=Client();f=open(O/'race-node-requests.jsonl','w')
for s in specs:
 for m in modes:
  for group in range(2):record(c,[job(s,m,'race:'+s['label']+':'+str(group*4+i),800000000001+specs.index(s)*100+group*4+i) for i in range(4)],f)
c.close();f.close()
print('128 real node race-instrumented client requests completed')
