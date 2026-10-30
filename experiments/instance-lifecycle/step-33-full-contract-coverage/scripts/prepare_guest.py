from pathlib import Path
import subprocess,json,hashlib,shutil,csv,importlib.util,os
P=Path(__file__).resolve().parents[1];ROOT=Path('/home/frankie/mygitprojects');WT=ROOT/'.worktrees/cvw-step18';S18=ROOT/'CVW/experiments/instance-lifecycle/step-18-combined-cold-start';S32=ROOT/'.worktrees/cvw-step32/experiments/instance-lifecycle/step-32-all-contracts-acopy';GO=Path('/usr/local/go-version/go1.24.1');PROBE=S18/'toolchains/go1.24.1-diagnostic';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('old18',S18/'pipeline.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
variants={};rows=[];oldv=json.loads((S32/'inputs/variants.json').read_text())
for c in ['compute','fact','erc721','identity','exchange']:
 for g in ['G0','G1','G2','G3']:
  a=oldv[c+'-'+g];data=Path(a['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==a['sha'];dst=P/'inputs'/f'{c}-{g}.wasm'
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  variants[c+'-'+g]=dict(a,path=str(dst))
for c in ['bigInput','itinerary','raffle']:
 dest=P/'guest-source'/c;dest.mkdir(exist_ok=True)
 for n in subprocess.check_output(['git','-C',str(WT),'ls-tree','-r','--name-only','95903a3','--','chainmaker/testdata-instrument/'+c],text=True).splitlines():
  if n.endswith(('.go','go.mod','go.sum')):
   f=dest/Path(n).name;data=subprocess.check_output(['git','-C',str(WT),'show','95903a3:'+n])
   if f.exists():assert f.read_bytes()==data
   else:f.write_bytes(data)
work=P/'guest.work';work.write_text('go 1.24.1\nuse (\n'+str(WT)+'\n'+'\n'.join(str(P/'guest-source'/c)for c in ['bigInput','itinerary','raffle'])+'\n)\n')
for c in ['bigInput','itinerary','raffle']:
 dest=P/'guest-source'/c;base={}
 for flavor,tool in [('plain',GO),('probe',PROBE)]:
  for a in [0,1]:
   label=f'{c}-a{a}-{flavor}';out=P/'guest-builds'/f'{label}.wasm';log=P/'audit'/f'guest-{label}.log';pad=dest/'layout_pad_step18.go'
   if a:
    amount=(4<<20)-base[flavor]['bloc']-5*65536;assert amount>0
    pad.write_text(f'package main\nimport "unsafe"\nvar experimentHeapLayoutPad = [{amount}]byte{{{amount}-1:1}}\nvar experimentHeapLayoutPadPtr = unsafe.Pointer(&experimentHeapLayoutPad)\nfunc init() {{ if experimentHeapLayoutPadPtr == nil {{ panic("experiment heap layout padding unavailable") }} }}\n');shutil.copyfile(pad,P/'audit'/f'{label}-padding.go.txt')
   try:
    if not out.exists():
     assert not log.exists(),'inspect partial build first'
     env={'GOROOT':str(tool),'GOTOOLCHAIN':'local','GOOS':'wasip1','GOARCH':'wasm','GOWORK':str(work),'GOPROXY':'off','GOSUMDB':'off','GOMAXPROCS':'2','GOFLAGS':''}
     cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit=step33-guest-'+label,'-p','MemoryMax=2G','-p','TasksMax=192','-p','CPUQuota=400%','-p','RuntimeMaxSec=180s','-p','KillMode=control-group','--working-directory='+str(dest)]+['--setenv='+k+'='+v for k,v in env.items()]+[str(tool/'bin/go'),'build','-o',str(out),'.'];(P/'audit'/f'guest-{label}-command.json').write_text(json.dumps(cmd,indent=2));print('BUILD',label,flush=True)
     with log.open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
     if r.returncode:raise RuntimeError(log.read_text()[-1600:])
    subprocess.run(['wasm-validate','--enable-all',str(out)],capture_output=True,check=True);info=old.layout(out.read_bytes())
    if not a:base[flavor]=info
    else:assert info['bloc']==(4<<20)-5*65536
    rows.append(dict(contract=c,A=a,flavor=flavor,sha=sha(out),path=str(out),source='95903a3',layout=info))
    if flavor=='plain':
     for g,copy in ([('G0',False),('G2',True)]if not a else[('G1',False),('G3',True)]):variants[c+'-'+g]=dict(path=str(out),sha=sha(out),copy=copy,group=g)
   finally:
    if pad.exists():pad.unlink()
(P/'inputs/variants.json').write_text(json.dumps(variants,indent=2));(P/'audit/guest-lineage.json').write_text(json.dumps({'new_builds':rows,'source_commit':'95903a3','guest_go':'1.24.1','B1':False,'registry_sha':sha(WT/'registry/registry.go')},indent=2));print('GUEST READY',flush=True)
