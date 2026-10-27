from pathlib import Path
import json,hashlib,subprocess,os,shutil,csv,importlib.util
P=Path(__file__).resolve().parents[1];S=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-18-combined-cold-start');WT=Path('/home/frankie/mygitprojects/.worktrees/cvw-step18');GO=Path('/usr/local/go-version/go1.24.1');PROBE=S/'toolchains/go1.24.1-diagnostic'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('old18',S/'pipeline.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
assert sha(GO/'src/runtime/symtab.go')==json.loads((S/'environment.json').read_text())['runtime_symtab_sha256'];sdk=Path('/home/frankie/go/pkg/mod/github.com/!t!k!o!t!k!ch/contract-sdk-go-wasm@v0.1.3')
for name,value in json.loads((S/'sdk-provenance.json').read_text())['files'].items():assert sha(sdk/name)==value,name
assert 'GetBatchState'in(sdk/'sdk/chainmaker.go').read_text()
variants={};rows=[]
for c in ['compute','fact','erc721']:
 for group,a,copy in [('G0',0,False),('G1',0,True),('G2',1,True)]:
  src=S/'artifacts'/f'{c}-a{a}p0-plain/original.wasm';expect=next(r for r in csv.DictReader((S/'variants.csv').open())if r['contract']==c and r['A']==str(a)and r['P']=='0'and r['C']==str(int(copy))and r['flavor']=='plain');assert sha(src)==expect['logical_wasm_sha256']
  dst=P/'inputs'/f'{c}-{group}.wasm'
  if not dst.exists():shutil.copyfile(src,dst)
  assert sha(dst)==sha(src);variants[c+'-'+group]={'path':str(dst),'sha':sha(dst),'copy':copy,'group':group};rows.append({'contract':c,'group':group,'sha':sha(dst),'origin':'Step18 saved plain 95903a3','layout':old.layout(dst.read_bytes())})
work=P/'guest.work';work.write_text('go 1.24.1\nuse (\n '+str(WT)+'\n '+str(P/'guest-source/exchange')+'\n '+str(P/'guest-source/identity')+'\n)\n')
# Materialize both workspace modules before the first build.
for c in ['exchange','identity']:
 dest=P/'guest-source'/c;dest.mkdir(exist_ok=True)
 names=subprocess.check_output(['git','-C',str(WT),'ls-tree','-r','--name-only','95903a3','--','chainmaker/testdata-instrument/'+c],text=True).splitlines()
 for name in names:
  if name.endswith(('.go','go.mod','go.sum')):
   data=subprocess.check_output(['git','-C',str(WT),'show','95903a3:'+name]);f=dest/Path(name).name
   if f.exists():assert f.read_bytes()==data
   else:f.write_bytes(data)
for c in ['exchange','identity']:
 dest=P/'guest-source'/c;dest.mkdir(exist_ok=True)
 files=subprocess.check_output(['git','-C',str(WT),'ls-tree','-r','--name-only','95903a3','--','chainmaker/testdata-instrument/'+c],text=True).splitlines()
 for name in files:
  if name.endswith(('.go','go.mod','go.sum')):
   data=subprocess.check_output(['git','-C',str(WT),'show','95903a3:'+name]);f=dest/Path(name).name
   if f.exists():assert f.read_bytes()==data
   else:f.write_bytes(data)
 base={}
 for flavor,tool in [('plain',GO),('probe',PROBE)]:
  for a in [0,1]:
   label=f'{c}-a{a}-{flavor}';out=P/'guest-builds'/f'{label}.wasm';log=P/'audit'/f'guest-{label}-attempt2.log';pad=dest/'layout_pad_step18.go'
   if a:
    amount=(4<<20)-base[flavor]['bloc']-5*65536;assert amount>0
    pad.write_text(f'package main\nimport "unsafe"\nvar experimentHeapLayoutPad = [{amount}]byte{{{amount}-1:1}}\nvar experimentHeapLayoutPadPtr = unsafe.Pointer(&experimentHeapLayoutPad)\nfunc init() {{ if experimentHeapLayoutPadPtr == nil {{ panic("experiment heap layout padding unavailable") }} }}\n')
    shutil.copyfile(pad,P/'audit'/f'{label}-padding.go.txt')
   try:
    if not out.exists():
     assert not log.exists(),'partial build: inspect first'
     envs={'GOROOT':str(tool),'GOTOOLCHAIN':'local','GOOS':'wasip1','GOARCH':'wasm','GOWORK':str(work),'GOPROXY':'off','GOSUMDB':'off','GOMAXPROCS':'2','GOFLAGS':''}
     cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit=step28-guest-'+label,'-p','MemoryMax=2G','-p','TasksMax=192','-p','CPUQuota=400%','-p','RuntimeMaxSec=180s','-p','KillMode=control-group','--working-directory='+str(dest)]+['--setenv='+k+'='+v for k,v in envs.items()]+[str(tool/'bin/go'),'build','-o',str(out),'.']
     (P/'audit'/f'guest-{label}-attempt2-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
     print('building',label,flush=True)
     with log.open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
     if r.returncode:raise RuntimeError(log.read_text()[-2000:])
    subprocess.run(['wasm-validate','--enable-all',str(out)],check=True,capture_output=True);info=old.layout(out.read_bytes())
    if not a:base[flavor]=info
    else:assert info['bloc']==(4<<20)-5*65536,info
    rows.append({'contract':c,'group':('G2'if a else'G0/G1')+'-'+flavor,'sha':sha(out),'origin':'95903a3 source, same Go/SDK/P0 flags; new path recorded','layout':info})
    if flavor=='plain':
     for group,copy in ([('G2',True)]if a else[('G0',False),('G1',True)]):variants[c+'-'+group]={'path':str(out),'sha':sha(out),'copy':copy,'group':group}
   finally:
    if pad.exists():pad.unlink()
(P/'inputs/variants.json').write_text(json.dumps(variants,indent=2)+'\n');(P/'audit/guest-lineage.json').write_text(json.dumps({'variants':rows,'source_commit':'95903a3','SDK_version':'0.1.3','SDK_source_matches_saved_zip':True,'B1':False,'registry_sha':sha(WT/'registry/registry.go'),'guest_go':subprocess.check_output([str(GO/'bin/go'),'version'],text=True).strip(),'compiler_sha':sha(GO/'pkg/tool/linux_amd64/compile'),'linker_sha':sha(GO/'pkg/tool/linux_amd64/link'),'probe_runtime_sha':{f:sha(PROBE/'src/runtime'/f)for f in ['proc.go','mem_sbrk.go','step18_wasm.go']}},indent=2)+'\n')
print('guest preparation complete; new exchange/identity A alignment still requires safe dynamic probe',flush=True)
