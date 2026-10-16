#!/usr/bin/env python3
from pathlib import Path
import os,sys,subprocess,json,signal,time
O=Path(__file__).resolve().parent
LIB='/home/frankie/mygitprojects/.worktrees/cvw-step17/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib/linux-amd64'
if sys.argv[1]=='start':
 for mode in sys.argv[2:] or ['baseline','optimized']:
  home=O/'network'/mode; pidfile=home/'pid'
  if pidfile.exists():
   try:
    pid=int(pidfile.read_text())
    if Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z':raise RuntimeError(f'{mode} already running')
   except (ProcessLookupError,FileNotFoundError):pass
  env=dict(os.environ,CM_STATIC_MEMORY_COPY=os.environ.get('CM_STATIC_MEMORY_COPY_OVERRIDE','1' if mode=='optimized' else '0'),CM_FRESH_INVOKE='1',CM_STEP17_SERIALIZE_VM='1',CM_STEP17_OBSERVE='1',CM_STEP17_ARTIFACT_DIR=str(O/'compiled'),LD_LIBRARY_PATH=LIB,GOMAXPROCS='4')
  env.pop('CM_STEP16_SERIALIZED_MODULE',None)
  log=open(home/'stdout.log','ab',buffering=0)
  p=subprocess.Popen([os.environ.get('STEP17_NODE_BINARY',str(O/'chainmaker')),'start','-c',str(home/'config/wx-org1.chainmaker.org'/os.environ.get('STEP17_CONFIG_NAME','chainmaker.yml'))],cwd=home,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  pidfile.write_text(str(p.pid));print(mode,p.pid)
elif sys.argv[1]=='stop':
 for mode in sys.argv[2:] or ['baseline','optimized']:
  f=O/'network'/mode/'pid'
  if not f.exists():continue
  pid=int(f.read_text())
  try:
   # Check ownership: never kill an unrelated process after PID reuse.
   if str(O/'chainmaker').encode() in Path(f'/proc/{pid}/cmdline').read_bytes():os.kill(pid,signal.SIGTERM)
  except (ProcessLookupError,FileNotFoundError):pass
