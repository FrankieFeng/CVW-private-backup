from harness import *
label=sys.argv[1];n=c=None;out={'label':label,'passed':False};watch=None;rt=None
try:
 clone(Path('/tmp/cvw-step39c-seed-compute-A'),H);n=Node(label,'E3');c=Client(label);tx=hashlib.sha256(label.encode()).hexdigest();out['tx_id']=tx;reset={};trigger={};done=threading.Event()
 def observe():
  global rt
  try:
   deadline=time.monotonic()+20
   while time.monotonic()<deadline:
    txt=n.log.read_text()
    if any(tx in line and'"event":"invoke_begin"'in line for line in txt.splitlines()):break
    if done.wait(.001):raise RuntimeError('request ended before observed VM entry')
   else:raise RuntimeError('no observed VM entry')
   trigger['observed_vm']=True
   def do_reset():
    try:reset['response']=manager('reset',True)
    except BaseException as e:reset['error']=repr(e)
   rt=threading.Thread(target=do_reset);rt.start();deadline=time.monotonic()+8
   while time.monotonic()<deadline:
    state=manager('state')
    if state['resetting']:trigger['state']=state;break
    if done.wait(.001):raise RuntimeError('request ended before reset observation')
   else:raise RuntimeError('reset state not observed')
   subprocess.run(['systemctl','--user','kill','--signal=SIGTERM',n.unit],check=True,capture_output=True);trigger['sigterm_monotonic_s']=time.monotonic()
  except BaseException as e:trigger['error']=repr(e)
 watch=threading.Thread(target=observe);watch.start()
 result=c.batch([{'Op':'invoke','Contract':'compute','Method':'hashCal','Params':{},'TxID':tx,'Tag':'inflight','Phase':'lifecycle'}]);out['business']=result;done.set();watch.join(25)
 if rt:rt.join(20)
 out['trigger']=trigger;out['reset']=reset;assert not watch.is_alive()and(rt is None or not rt.is_alive());assert trigger.get('observed_vm')and'sigterm_monotonic_s'in trigger and'error'not in trigger,trigger;assert reset.get('response',{}).get('error')=='<nil>',reset
 out['passed']=True
finally:
 if c:c.close()
 if n:
  z=n.close();out['node']=z;o=z.get('owner')or{};safe=not z['reason']and z['systemd'].get('ExecMainStatus')=='0'and o.get('managed_pending')==0 and o.get('stores_created')==o.get('stores_closed')and o.get('instances_created')==o.get('instances_closed')and z['pid_exited']and z['cgroup_empty'];out['passed']=out['passed']and safe
  if not safe:(P/'STOP_SHARED.json').write_text(json.dumps({'label':label,'stage':'inflight','node':z},indent=2))
 (P/'raw_logs'/f'{label}-inflight.json').write_text(json.dumps(out,indent=2));assert out['passed'],label+' failed; see inflight.json'
