"""Freeze the prespecified existing paired records. Never execute or compile guest code."""
from pathlib import Path
import json,csv,hashlib,shutil,subprocess
P=Path(__file__).resolve().parents[1];B=P.parent/'step-25-ab-copy-screening';OLD_EDGES={('G1','G2'),('G2','G4'),('G1','G4')};CASES={'compute','fact','erc721'}
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
origin=json.loads((B/'audit/ARTIFACT_HASHES.json').read_text());frozen=subprocess.check_output(['git','-C',str(P.parents[2]),'show','be88d9a:experiments/instance-lifecycle/step-25-ab-copy-screening/audit/ARTIFACT_HASHES.json']);assert frozen==(B/'audit/ARTIFACT_HASHES.json').read_bytes()
archive=[]
def freeze(src,dst):
 rel=str(src.relative_to(B));assert sha(src)==origin[rel],rel
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==src.read_bytes(),'existing frozen file differs'
 else:shutil.copyfile(src,dst)
 archive.append({'origin':'be88d9a','origin_path':rel,'copied_path':str(dst.relative_to(P)),'sha256':sha(dst)})
inv=[];selected=[]
for f in sorted((B/'raw_logs').glob('*-outcome.json')):
 o=json.loads(f.read_text());label=o['label'];formal=o['contract']in CASES and o['phase']=='formal'and(o['left'],o['right'])in OLD_EDGES
 pre=o['contract']in CASES and label in [f"pre2-{o['contract']}-{x}"for x in ['G0-G1','G0-G2','G0-G4','G2-copycheck','G4-copycheck']]
 inv.append({'label':label,'phase':o['phase'],'case':o['contract'],'old_left':o['left'],'old_right':o['right'],'passed':o['passed'],'included':formal or pre,'reason':'requested direct edge'if formal else'relevant functional/Copy precheck'if pre else'outside prespecified Step26 comparisons; retained in immutable Step25 commit'})
 if not(formal or pre):continue
 selected.append(label)
 for src in sorted((B/'raw_logs').glob(label+'*')):
  if src.is_dir():
   for ff in src.rglob('*'):
    if ff.is_file():freeze(ff,P/'raw_logs'/ff.relative_to(B/'raw_logs'))
  elif src.name==label+'.log'or src.name.startswith(label+'-'):freeze(src,P/'raw_logs'/src.name)
rows=list(csv.DictReader((B/'MATRIX.csv').open()));wanted=[]
for r in rows:
 if r['family']!='step18'or r['case']not in CASES or r['group']not in ['G1','G2','G4']:continue
 r=dict(r);r['step25_group']=r['group'];r['group']={'G1':'G1','G2':'G2','G4':'G3'}[r['group']];r['origin_commit']='be88d9a';r['newly_built']=False;wanted.append(r)
 freeze(B/'inputs'/f"{r['contract']}-{r['step25_group']}.wasm",P/'inputs'/f"{r['contract']}-{r['group']}.wasm")
for rel in ['PAIRED_EFFECTS.csv','ORDER_SENSITIVITY.csv','BATCH_EFFECTS.csv','STAGE_EFFECTS.csv','environment.json','go.work','source/vm/step25_test.go','source/vm/step22_runtime_test.go','source/vm/step21d_runtime_test.go','source/vm/step22_static_test.go','source/vm/sim_context.go','source/vm/step21d_compile.go','source/vm/wasmer-go/managed.go','scripts/run.py']:
 freeze(B/rel,P/'audit/original_step25'/rel)
for c in ['compute','fact','erc721']:
 freeze(B/'inputs'/f'{c}-step24b-original.wasm',P/'inputs'/f'{c}-step24b-original.wasm')
for name,data in [('MATRIX.csv',wanted),('audit/ALL_STEP25_RUNS.csv',inv),('audit/ORIGIN_FILES.csv',archive)]:
 with(P/name).open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(P/'audit/selection.json').write_text(json.dumps({'source_commit':'be88d9a','selected_processes':len(selected),'formal_processes':81,'preflight_processes':15,'source_all_processes':len(inv),'source_failed_processes':sum(not x['passed']for x in inv),'rule':'prespecified cases/edges/phases only; no time/result filtering','new_guest_runs':0,'new_compilations':0,'mapping':{'Step26 G1':'Step25 G1','Step26 G2':'Step25 G2','Step26 G3':'Step25 G4'}},indent=2)+'\n')
print('froze',len(archive),'files;',len(selected),'original processes; no guest executed')
