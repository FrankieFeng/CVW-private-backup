import sys,json,subprocess,shutil,hashlib,difflib
from pathlib import Path
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r));import pipeline as p
root=r/'recovered-pb';sdk=root/'sdk';wt=p.WT
# Dedicated workspace pins the original module graph and only replaces SDK.
w=json.loads(subprocess.check_output([str(p.GO/'bin/go'),'work','edit','-json'],cwd=wt,env=p.guestenv(p.GO),text=True))
work=root/'go.work';work.write_text('go 1.24.1\nuse (\n'+''.join(' '+str((wt/entry['DiskPath']).resolve())+'\n' for entry in w['Use'])+')\nreplace github.com/TKOTKCh/contract-sdk-go-wasm => '+str(sdk)+'\n')
original=Path('/home/frankie/go/pkg/mod/github.com/!t!k!o!t!k!ch/contract-sdk-go-wasm@v0.1.3/sdk/chainmaker.go')
(root/'sdk.diff').write_text(''.join(difflib.unified_diff(original.read_text().splitlines(True),(sdk/'sdk/chainmaker.go').read_text().splitlines(True),fromfile='sdk-original/sdk/chainmaker.go',tofile='sdk-trimmed/sdk/chainmaker.go')))
old=json.loads((r/'manifest.json').read_text());manifest=list(old);vrows=[];layouts=[]
for contract in p.CONTRACTS:
 source=wt/'chainmaker/testdata-instrument'/contract;pad=source/'layout_pad_step18.go';base={}
 try:
  for a in (0,1):
   for flavor,goroot in [('plain',p.GO),('probe',p.PROBE)]:
    label=f'{contract}-a{a}p1-{flavor}';dest=r/'artifacts'/label;dest.mkdir(exist_ok=False)
    if a:
     amount=(4<<20)-base[flavor]['bloc']-5*65536;assert amount>0
     pad.write_text(f'package main\nimport "unsafe"\nvar experimentHeapLayoutPad = [{amount}]byte{{{amount}-1:1}}\nvar experimentHeapLayoutPadPtr = unsafe.Pointer(&experimentHeapLayoutPad)\nfunc init() {{ if experimentHeapLayoutPadPtr == nil {{ panic("experiment heap layout padding unavailable") }} }}\n')
     shutil.copyfile(pad,r/'prototype'/f'{contract}_{flavor}_p1_layout_pad.go.txt')
    e=p.guestenv(goroot);e['GOWORK']=str(work)
    print('P BUILD',label,flush=True)
    p.invoke([goroot/'bin/go','build','-o',dest/'original.wasm','.'],source,e,r/'build-logs'/f'{label}.log')
    blob=(dest/'original.wasm').read_bytes();info=p.layout(blob)
    if not a:base[flavor]=info
    if a:assert info['bloc']==(4<<20)-5*65536,info
    layouts.append(dict(info,label=label,contract=contract,A=a,P=1,flavor=flavor,padding_bytes=amount if a else 0))
    stripped,image,ranges,n,gs,ts,diag,diagnodata=p.old.transform(blob);diag,table=p.s16.diagnostic(diag);diagnodata,table2=p.s16.diagnostic(diagnodata);assert table==table2
    files=dict(original=blob,nodata=stripped,image=image,diagnostic=diag,diagnostic_nodata=diagnodata);paths={}
    for key,data in files.items():
     path=dest/(key+('.bin' if key=='image' else '.wasm'));path.write_bytes(data);paths[key]=str(path)
     if key!='image':subprocess.run(['wasm-validate','--enable-all',str(path)],check=True)
    (dest/'table_expected.json').write_text(json.dumps(table))
    s=next(s for s in old if s['label']==f'{contract}-a0p0-plain');row={k:s[k] for k in ['method','params','expected','business_scope','real']}
    row.update(label=label,status='supported',contract=contract,A=a,P=1,flavor=flavor,paths=paths,ranges=ranges,globals=gs,tables=ts,image_sha256=p.sha(image),module_end=info['module_end']);manifest.append(row)
    for c in (0,1):vrows.append(dict(contract=contract,A=a,P=1,C=c,flavor=flavor,status='built_recovered_original_patch',label=label,logical_wasm_sha256=p.sha(blob),execution_wasm_sha256=p.sha(stripped if c else blob),template_sha256=p.sha(image) if c else '',wasm_bytes=len(blob),execution_wasm_bytes=len(stripped if c else blob),template_bytes=len(image) if c else 0,copy_bytes=sum(b-a for a,b in ranges) if c else 0,copy_ranges=len(ranges) if c else 0,**{k:info[k] for k in ['module_end','bloc','initial_pages']},padding_bytes=amount if a else 0))
 finally:
  if pad.exists():pad.unlink()
(r/'manifest-full.json').write_text(json.dumps(manifest,indent=2)+'\n');p.csvwrite(root/'built_variants.csv',vrows);p.csvwrite(root/'layout.csv',layouts)
# Check build and dependency compatibility for all eight, without running nodes.
checks=[]
for contract in ['compute','erc721','fact','bigInput','exchange','identity','itinerary','raffle']:
 source=wt/'chainmaker/testdata-instrument'/contract;e=p.guestenv(p.GO);e['GOWORK']=str(work)
 p.invoke([p.GO/'bin/go','build','-o',root/(contract+'-p1-smoke.wasm'),'.'],source,e,root/(contract+'-build.log'))
 deps=subprocess.check_output([str(p.GO/'bin/go'),'list','-deps','.'],cwd=source,env=e,text=True)
 (root/(contract+'-deps.txt')).write_text(deps)
 checks.append(dict(contract=contract,build='pass',uses_removed_API=any('GetBatchState' in f.read_text() or 'BatchKey' in f.read_text() for f in source.glob('*.go')),pb_compiled=any('chainmaker.org/chainmaker/pb-go' in d or 'gogo/protobuf' in d for d in deps.splitlines()),wasm_sha256=p.sha((root/(contract+'-p1-smoke.wasm')).read_bytes())))
p.csvwrite(root/'eight_contract_build_checks.csv',checks)
