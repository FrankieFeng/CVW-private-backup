"""Step-18 pilot. No PB replacement is invented when its source is missing."""
import argparse,csv,hashlib,importlib.util,json,os,platform,shutil,struct,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CVW=Path(os.environ.get('S18_REPO','/home/frankie/mygitprojects/CVW')); HOME=CVW.parent; WT=Path(os.environ.get('S18_WORKTREE',str(HOME/'.worktrees/cvw-step18')))
VM=WT/'chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'
GO=Path('/usr/local/go-version/go1.24.1'); PROBE=ROOT/'toolchains/go1.24.1-diagnostic'
EXPERIMENTS=CVW/'experiments/instance-lifecycle'
sys.path.insert(0,str(EXPERIMENTS/'step-15-copy-attribution'))
from common import csvwrite,load14
old=load14()
spec=importlib.util.spec_from_file_location('step16_setup',EXPERIMENTS/'step-16-chainmaker-copy/setup.py')
s16=importlib.util.module_from_spec(spec);spec.loader.exec_module(s16)
sha=lambda b:hashlib.sha256(b).hexdigest()
CONTRACTS=['compute','erc721','fact']
def invoke(cmd,cwd,env,log):
 with Path(log).open('w') as f:
  code=subprocess.run([str(x) for x in cmd],cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
 if code: raise RuntimeError(f'exit {code}: {log}\n'+Path(log).read_text(errors='replace')[-3000:])
def guestenv(goroot):
 e=os.environ.copy();e.update(GOROOT=str(goroot),GOTOOLCHAIN='local',GOOS='wasip1',GOARCH='wasm',GOWORK=str(WT/'go.work'),GOMAXPROCS='2');return e
def layout(blob):
 # Go 1.24.1 wasm has no DWARF. Recover moduledata using pcHeader pointer,
 # then validate all relevant field bounds and linker's initial-page formula.
 # moduledata offsets are pinned to the saved runtime/symtab.go hash.
 parts=list(old.sections(blob));r=old.Reader(next(p for k,p,_ in parts if k==5));assert r.uleb()==1;flags=r.uleb();pages=r.uleb()
 image=bytearray(pages*65536)
 for k,p,_ in parts:
  if k==11:
   for seg in old.parse_active_data(p):image[seg.offset:seg.offset+len(seg.data)]=seg.data
 magic=bytes.fromhex('f1ffffff00000108');candidates=[];start=0
 while True:
  header=image.find(magic,start)
  if header<0:break
  start=header+1;pos=0
  while True:
   pos=image.find(struct.pack('<Q',header),pos+1)
   if pos<0:break
   if pos%8 or pos+35*8>len(image):continue
   fields=struct.unpack_from('<35Q',image,pos);end=fields[34]
   if 0<fields[24]<=fields[25]<=fields[26]<=fields[27]<=fields[28]<=fields[29]<=fields[30]<=fields[31]<=end<len(image) and (end+(1<<20))//65536==pages:
    candidates.append(dict(moduledata_address=pos,module_end=end,bloc=(end+65535)&~65535,initial_pages=pages))
 assert len(candidates)==1,candidates
 return candidates[0]
def probe_toolchain():
 if not PROBE.exists():
  PROBE.parent.mkdir(exist_ok=True)
  shutil.copytree(GO,PROBE)
 p=PROBE/'src/runtime/proc.go';text=(GO/'src/runtime/proc.go').read_text()
 before='\tfor m := &firstmoduledata; m != nil; m = m.next {\n\t\tdoInit(m.inittasks)\n\t}'
 after='\tstep18Times[0] = nanotime()\n'+before+'\n\tstep18Times[1] = nanotime()'
 assert text.count(before)==1;p.write_text(text.replace(before,after))
 (PROBE/'src/runtime/step18_wasm.go').write_text('''//go:build wasip1 && wasm
package runtime
var step18Times [2]int64
var step18Reserve [3]int64
//go:wasmexport Step18Read
func Step18Read(index int32) int64 {
 if index == 2 { return nanotime() }
 if index == 3 { return int64(firstmoduledata.end) }
 if index >= 4 && index <= 6 { return step18Reserve[index-4] }
 if index < 0 || index > 1 { return -1 }
 return step18Times[index]
}
''')
 p2=PROBE/'src/runtime/mem_sbrk.go';text=(GO/'src/runtime/mem_sbrk.go').read_text();before='func sysReserveAlignedSbrk(size, align uintptr) (unsafe.Pointer, uintptr) {\n\tlock(&memlock)'
 assert text.count(before)==1
 text=text.replace(before,before+'\n\tif step18Reserve[0] == 0 { step18Reserve = [3]int64{int64(bloc), int64(alignUp(bloc, align)-bloc), int64(align)} }');p2.write_text(text)
 patch=''.join(subprocess.run(['diff','-u',str(GO/'src/runtime'/name),str(PROBE/'src/runtime'/name)],capture_output=True,text=True).stdout for name in ['proc.go','mem_sbrk.go'])
 (ROOT/'diagnostic-runtime.patch').write_text(patch)
 shutil.copyfile(PROBE/'src/runtime/step18_wasm.go',ROOT/'prototype/step18_wasm.go.txt')
def build():
 (ROOT/'prototype').mkdir(exist_ok=True);(ROOT/'build-logs').mkdir(exist_ok=True);(ROOT/'artifacts').mkdir(exist_ok=True)
 probe_toolchain();prior=json.loads((EXPERIMENTS/'step-16-chainmaker-copy/manifest.json').read_text());manifest=[];variants=[];layouts=[]
 for contract in CONTRACTS:
  source=WT/'chainmaker/testdata-instrument'/contract
  pad=source/'layout_pad_step18.go'
  if pad.exists():raise RuntimeError('existing generated pad; inspect before rebuilding')
  baseline_layout={}
  try:
   for a in (0,1):
    for flavor,goroot in [('plain',GO),('probe',PROBE)]:
     if a:
      # Restore the old near prototype's target: first heap reservation bloc,
      # not initBloc. The known bootstrap metadata uses five 64KiB pages in
      # these pinned builds; probe measurements below MUST verify this.
      amount=(4<<20)-baseline_layout[flavor]['bloc']-5*65536;assert amount>0
      pad.write_text(f'''package main
import "unsafe"
var experimentHeapLayoutPad = [{amount}]byte{{{amount}-1:1}}
var experimentHeapLayoutPadPtr = unsafe.Pointer(&experimentHeapLayoutPad)
func init() {{ if experimentHeapLayoutPadPtr == nil {{ panic("experiment heap layout padding unavailable") }} }}
''')
      shutil.copyfile(pad,ROOT/'prototype'/f'{contract}_{flavor}_layout_pad.go.txt')
     label=f'{contract}-a{a}p0-{flavor}';dest=ROOT/'artifacts'/label;dest.mkdir(exist_ok=False)
     original=dest/'original.wasm'
     invoke([goroot/'bin/go','build','-o',original,'.'],source,guestenv(goroot),ROOT/'build-logs'/f'{label}.log')
     blob=original.read_bytes();info=layout(blob)
     if not a:baseline_layout[flavor]=info
     info.update(label=label,contract=contract,A=a,P=0,flavor=flavor,padding_bytes=amount if a else 0)
     # Explicitly fail rather than silently label a layout which missed the target.
     if a and info['bloc']!=(4<<20)-5*65536:raise RuntimeError(f'A initial target missed: {info}')
     layouts.append(info)
     stripped,image,ranges,n,gs,ts,diag,diagnodata=old.transform(blob)
     diag,table=s16.diagnostic(diag);diagnodata,table2=s16.diagnostic(diagnodata);assert table==table2
     files=dict(original=blob,nodata=stripped,image=image,diagnostic=diag,diagnostic_nodata=diagnodata)
     paths={}
     for key,data in files.items():
      path=dest/(key+('.bin' if key=='image' else '.wasm'));path.write_bytes(data);paths[key]=str(path)
      if key!='image':subprocess.run(['wasm-validate','--enable-all',str(path)],check=True)
     (dest/'table_expected.json').write_text(json.dumps(table))
     s=next(s for s in prior if s['label']==contract)
     row={k:s[k] for k in ['method','params','expected','business_scope','real']}
     row.update(label=label,status='supported',contract=contract,A=a,P=0,flavor=flavor,paths=paths,ranges=ranges,globals=gs,tables=ts,image_sha256=sha(image),module_end=info['module_end'])
     manifest.append(row)
     for c in (0,1):variants.append(dict(contract=contract,A=a,P=0,C=c,flavor=flavor,status='built',label=label,logical_wasm_sha256=sha(blob),execution_wasm_sha256=sha(stripped if c else blob),template_sha256=sha(image) if c else '',wasm_bytes=len(blob),execution_wasm_bytes=len(stripped if c else blob),template_bytes=len(image) if c else 0,copy_bytes=sum(b-a for a,b in ranges) if c else 0,copy_ranges=len(ranges) if c else 0,**{k:info[k] for k in ['module_end','bloc','initial_pages','padding_bytes']}))
  finally:
   if pad.exists():pad.unlink()
  for a in (0,1):
   for c in (0,1):variants.append(dict(contract=contract,A=a,P=1,C=c,flavor='plain',status='blocked_missing_pb_source',reason='historical trimmed WASM has no recoverable trim source/recipe; cannot compose source-level A or verify SDK/Gas provenance'))
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');csvwrite(ROOT/'variants.csv',variants);csvwrite(ROOT/'layout.csv',layouts)
 env=dict(baseline_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=WT,text=True).strip(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=WT,text=True).strip(),host=platform.platform(),cpu=Path('/proc/cpuinfo').read_text().split('model name')[1].splitlines()[0],guest_go=subprocess.check_output([str(GO/'bin/go'),'version'],text=True).strip(),host_go=subprocess.check_output(['/usr/local/go/bin/go','version'],text=True).strip(),wasmer_library_sha256=sha((VM/'wasmer-go/packaged/lib/linux-amd64/libwasmer.so').read_bytes()),runtime_symtab_sha256=sha((GO/'src/runtime/symtab.go').read_bytes()),guest_sources={str(p.relative_to(WT)):sha(p.read_bytes()) for c in CONTRACTS for p in (WT/'chainmaker/testdata-instrument'/c).glob('*.go')},registry_sha256=sha((WT/'registry/registry.go').read_bytes()))
 (ROOT/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
 print('built',len(manifest),'logical builds; P=1 explicitly blocked',flush=True)
def hostenv(label):
 e=os.environ.copy();e.update(GOROOT='/usr/local/go',GOTOOLCHAIN='local',GOMAXPROCS='1',CM_INSTANCE_LIFECYCLE_TRACE='0',S15_MANIFEST=str(ROOT/'manifest.json'),S15_CONTRACT=label,S16_ARTIFACTS=str(ROOT/'artifacts'));return e
def host():
 for name in ['step18_test.go']:
  shutil.copyfile(ROOT/'prototype'/name,VM/name)
 # Minimal experimental timing additions, generated only in the new worktree.
 p=VM/'static_init_copy.go';txt=p.read_text()
 if 'StartMonoNS' not in txt:
  needle='S1NS, S2NS, S3NS, CopyNS';assert txt.count(needle)==1;txt=txt.replace(needle,'StartNS, StartMonoNS, S1NS, S2NS, S3NS, CopyNS');txt=txt.replace('"bytes"','"bytes"\n "golang.org/x/sys/unix"');txt+='\nfunc step18MonoNow() int64 { var ts unix.Timespec; if e:=unix.ClockGettime(unix.CLOCK_MONOTONIC,&ts); e!=nil {panic(e)}; return ts.Nano() }\n';p.write_text(txt)
 p=VM/'vm_pool.go';txt=p.read_text()
 if 'beginStart := time.Now()' not in txt:
  needle='\t\t_, startErr = start.Call()';assert txt.count(needle)==1;txt=txt.replace(needle,'\t\tbeginStart := time.Now()\n\t\tif os.Getenv("S18_DIAG") == "1" { profile.StartMonoNS = step18MonoNow() }\n'+needle+'\n\t\tprofile.StartNS = time.Since(beginStart).Nanoseconds()');p.write_text(txt)
 subprocess.run(['/usr/local/go/bin/gofmt','-w',str(VM/'static_init_copy.go'),str(VM/'vm_pool.go'),str(VM/'step18_test.go')],check=True)
 invoke(['/usr/local/go/bin/go','test','-tags','step16','-c','-o',ROOT/'step18.test','.'],VM,hostenv(''),ROOT/'build-logs/host.log')
 for name in ['static_init_copy.go','vm_pool.go']:
  shutil.copyfile(VM/name,ROOT/'prototype'/name)
 (ROOT/'prototype.patch').write_text(subprocess.check_output(['git','diff','--','chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'],cwd=WT,text=True))
def execute(test,label,out,extra=None):
 e=hostenv(label);e.update(extra or {});e['S16_OUT']=str(out.with_suffix('.jsonl'))
 invoke(['taskset','-c',str(min(os.sched_getaffinity(0))),'/usr/bin/time','-v','-o',out.with_suffix('.resources.txt'),ROOT/'step18.test','-test.run=^'+test+'$','-test.v','-test.timeout=10m'],VM,e,out.with_suffix('.log'))
def compile_all():
 dest=ROOT/'prepare-logs';dest.mkdir(exist_ok=True)
 for s in json.loads((ROOT/'manifest.json').read_text()):
  for key in ['original','nodata','diagnostic','diagnostic_nodata']:
   if (ROOT/'artifacts'/s['label']/(key+'.module')).exists():continue
   prior=ROOT/'attempt-01-wrong-initbloc-target/artifacts'/s['label']/(key+'.module')
   if prior.exists() and json.loads(prior.with_suffix('.module.json').read_text())['WasmSHA']==sha(Path(s['paths'][key]).read_bytes()):
    # Exact-binary reuse only. The loader independently rechecks ConfigID and
    # ArtifactSHA; it will fail rather than accept an incompatible cache.
    shutil.copyfile(prior,ROOT/'artifacts'/s['label']/(key+'.module'));shutil.copyfile(prior.with_suffix('.module.json'),ROOT/'artifacts'/s['label']/(key+'.module.json'))
    print('reuse exact validated first-compile artifact',s['label'],key,flush=True);continue
   print('isolated first compile',s['label'],key,flush=True)
   execute('TestStep16CompileProbe',s['label'],dest/(s['label']+'-'+key),dict(S16_KEY=key))
def run(batch,n,seed,mode):
 dest=ROOT/batch;dest.mkdir(exist_ok=False)
 for contract in CONTRACTS:
  print('run',mode,contract,n,flush=True)
  execute('TestStep18Pilot',contract,dest/contract,dict(S18_CONTRACT=contract,S18_MODE=mode,S18_DIAG='1' if mode=='probe' else '0',S16_N=str(n),S16_SEED=str(seed)))
 (dest/'run.json').write_text(json.dumps(dict(n=n,seed=seed,mode=mode,cpu_affinity=min(os.sched_getaffinity(0)),warmup_rounds=5,GC='disabled during samples; explicit GC every 20 complete paired rounds',binary_sha256=sha((ROOT/'step18.test').read_bytes()),scope='single-thread actual RuntimeInstance.Invoke; test TxSimContext; not real node'),indent=2))
def validate():
 dest=ROOT/'validation';dest.mkdir(exist_ok=True)
 def run_if_needed(test,label,path,extra=None):
  if path.with_suffix('.log').exists() and path.with_suffix('.log').read_text(errors='replace').rstrip().endswith('PASS'):return
  if path.with_suffix('.log').exists():
   failed=dest/'failed-harness';failed.mkdir(exist_ok=True)
   for suffix in ['.log','.jsonl','.resources.txt']:
    old=path.with_suffix(suffix)
    if old.exists():old.rename(failed/old.name)
  execute(test,label,path,extra)
 for s in json.loads((ROOT/'manifest.json').read_text()):
  if s['flavor']=='plain':run_if_needed('TestStep16Validation',s['label'],dest/s['label'])
 for contract in CONTRACTS:run_if_needed('TestStep18Checks',contract,dest/(contract+'-checks'),dict(S18_CONTRACT=contract))
 run_if_needed('TestStep16SafetyAndTableSynthetic','compute-a0p0-plain',dest/'synthetic')
 run_if_needed('TestStep16UnsupportedAndFallback','compute-a0p0-plain',dest/'fallback')
def template_cost():
 dest=ROOT/'template-cost';dest.mkdir(exist_ok=False)
 for s in json.loads((ROOT/'manifest.json').read_text()):
  if s['flavor']=='plain':execute('TestStep16TemplateCost',s['label'],dest/s['label'])
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['build','host','compile','run','validate','template-cost']);ap.add_argument('--batch',default='pilot-plain-n40');ap.add_argument('--n',type=int,default=40);ap.add_argument('--seed',type=int,default=181701);ap.add_argument('--mode',choices=['plain','probe'],default='plain');a=ap.parse_args()
 if a.stage=='build':build()
 elif a.stage=='host':host()
 elif a.stage=='compile':compile_all()
 elif a.stage=='validate':validate()
 elif a.stage=='template-cost':template_cost()
 else:run(a.batch,a.n,a.seed,a.mode)
