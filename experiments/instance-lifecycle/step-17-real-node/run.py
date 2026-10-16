#!/usr/bin/env python3
from pathlib import Path
import os,sys,json,subprocess,time,random,socket,argparse
O=Path(__file__).resolve().parent; specs=json.loads((O.parent/'step-16-chainmaker-copy/manifest.json').read_text()); modes=['baseline','optimized']
class Client:
 def __init__(self):
  env=dict(os.environ,STEP17_ROOT=str(O),STEP17_ADMIN='/home/frankie/mygitprojects/chainmaker-go/build/crypto-config/wx-org1.chainmaker.org/user/admin1/admin1')
  self.p=subprocess.Popen([str(O/'client')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=open(O/'client.stderr','a'),text=True,env=env,cwd=O)
 def call(self,jobs):
  self.p.stdin.write(json.dumps(jobs)+'\n');self.p.stdin.flush()
  while True:
   s=self.p.stdout.readline()
   if not s:raise RuntimeError('client exited')
   if s.startswith('RESULT '):return json.loads(s[7:])
 def close(self):self.p.stdin.close();self.p.wait(timeout=10)
def record(c,jobs,f):
 rows=c.call(jobs)
 for r in rows:f.write(json.dumps(r)+'\n');f.flush()
 return rows
def snapshot(label):
 rows=[]
 for mode in modes:
  home=O/'network'/mode;pid=int((home/'pid').read_text());status={}
  for line in Path(f'/proc/{pid}/status').read_text().splitlines():
   if line.split(':')[0] in ['VmRSS','VmSize','Threads']:status[line.split(':')[0]]=line.split(':')[1].strip()
  pools=[]
  for line in (home/'stdout.log').read_text(errors='replace').splitlines():
   if line.startswith('STEP17 '):
    row=json.loads(line[7:]);
    if row['kind']=='pool':pools.append(row)
  # Current process pools only (offset from start of each batch tracked below).
  rows.append(dict(label=label,mode=mode,pid=pid,proc=status,pool_events_total=len(pools)))
 with open(O/'memory.jsonl','a') as f:
  for r in rows:f.write(json.dumps(r)+'\n')
def wait_nodes():
 for port in [27301,27302]:
  deadline=time.time()+45
  while True:
   try:
    with socket.create_connection(('127.0.0.1',port),1):break
   except OSError:
    if time.time()>deadline:raise
    time.sleep(.25)
def restart():
 subprocess.run([sys.executable,str(O/'nodes.py'),'stop'],check=True)
 for mode in modes:
  pid=int((O/'network'/mode/'pid').read_text());deadline=time.time()+20
  while Path(f'/proc/{pid}/stat').exists() and Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z' and time.time()<deadline:time.sleep(.1)
 subprocess.run([sys.executable,str(O/'nodes.py'),'start'],check=True);wait_nodes()
def job(s,mode,tag,idx):
 p=dict(s['params']);name=s['label']
 if name in ['erc721','exchange']:p['tokenId']=str(idx)
 if name=='fact':p['file_hash']='s17'+str(idx)
 if name=='itinerary':p['phone']=str(13800000000+idx)
 return dict(Mode=mode,Op='invoke',Contract=name,Method=s['method'],Params=p,Tag=tag)
def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=['deploy','bench','correct']);a.add_argument('--batch',default='a');a.add_argument('--n',type=int,default=100);a.add_argument('--workers',type=int,default=1);args=a.parse_args()
 if args.action=='bench':restart()
 wait_nodes();c=Client();f=open(O/(args.action+'-'+args.batch+'-w'+str(args.workers)+'.jsonl'),'a');rng=random.Random(17001+sum(map(ord,args.batch))+args.workers)
 if args.action=='deploy':
  for s in specs:
   for mode in modes:print(record(c,[dict(Mode=mode,Op='deploy',Contract=s['label'],Path=s['paths']['original'],Tag='deploy')],f)[0].get('error','sent'),s['label'],mode,flush=True)
   snapshot('deployed-'+s['label'])
 elif args.action=='bench':
  snapshot(args.batch+'-empty')
  for s in specs:
   # One first access is a cold module/template cache sample, never in warm summaries.
   for mode in modes:record(c,[job(s,mode,f'{args.batch}:cold:{s["label"]}',int(time.time_ns()%1000000000))],f)
   snapshot(args.batch+'-cold-'+s['label'])
   for i in range(5):
    for mode in modes:record(c,[job(s,mode,f'{args.batch}:warmup:{i}',int(time.time_ns()%1000000000))],f)
   for start in range(0,args.n,args.workers):
    order=modes[:];rng.shuffle(order)
    base=100000000000+sum(map(ord,args.batch))*1000000+args.workers*100000+specs.index(s)*10000+start
    for mode in order:
     jobs=[job(s,mode,f'{args.batch}:w{args.workers}:{s["label"]}:{i}',base+i) for i in range(start,min(args.n,start+args.workers))]
     record(c,jobs,f)
   print(args.batch,args.workers,s['label'],'done',flush=True);snapshot(args.batch+'-warm-'+s['label'])
 else:
  for s in specs:
   for mode in modes:record(c,[dict(Mode=mode,Op='invoke',Contract=s['label'],Method='__missing_step17',Params={},Tag='exception:'+s['label'])],f)
  # Persisted state after real exchange invocation and independent mint.
 c.close();f.close()
if __name__=='__main__':main()
