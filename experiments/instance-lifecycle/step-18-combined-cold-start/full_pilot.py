"""Eight-cell pilot using the historically recovered SDK patch; no node run."""
import argparse,json,os,shutil,subprocess
from pathlib import Path
import pipeline as p
ROOT=p.ROOT;MAN=ROOT/'manifest-full.json';DEST=ROOT/'full-pilot';BIN=ROOT/'step18.test'
def extra():return dict(S15_MANIFEST=str(MAN))
def prepare():
 out=ROOT/'prepare-logs'
 for s in json.loads(MAN.read_text()):
  if s['P']!=1:continue
  for key in ['original','nodata']+(['diagnostic','diagnostic_nodata'] if s['flavor']=='plain' else []):
   target=ROOT/'artifacts'/s['label']/(key+'.module')
   if target.exists():continue
   print('first compile recovered',s['label'],key,flush=True)
   p.execute('TestStep16CompileProbe',s['label'],out/(s['label']+'-'+key),dict(extra(),S16_KEY=key))
def run(mode,n,seed):
 dest=DEST/mode;dest.mkdir(parents=True,exist_ok=False)
 for c in p.CONTRACTS:
  print('full matrix',mode,c,n,flush=True)
  p.execute('TestStep18Pilot',c,dest/c,dict(extra(),S18_CONTRACT=c,S18_MODE=mode,S18_FULL='1',S18_DIAG='1' if mode=='probe' else '0',S16_N=str(n),S16_SEED=str(seed)))
 (dest/'run.json').write_text(json.dumps(dict(n=n,seed=seed,mode=mode,paired_cells=8,warmup_rounds=5,cpu_affinity=min(os.sched_getaffinity(0)),binary_sha256=p.sha(BIN.read_bytes()),scope='actual RuntimeInstance.Invoke; mock TxSimContext; synchronous fresh creation and close; not live node'),indent=2)+'\n')
 shutil.copyfile(BIN,ROOT/'binaries'/f'full-{mode}.test')
def validate():
 dest=DEST/'validation';dest.mkdir(exist_ok=True)
 for s in json.loads(MAN.read_text()):
  if s['P']==1 and s['flavor']=='plain':p.execute('TestStep16Validation',s['label'],dest/s['label'],extra())
 for pv in [0,1]:
  for c in p.CONTRACTS:p.execute('TestStep18Checks',c,dest/(c+f'-p{pv}-checks'),dict(extra(),S18_CONTRACT=c,S18_P=str(pv)))
 costs=DEST/'template-cost';costs.mkdir(exist_ok=True)
 for s in json.loads(MAN.read_text()):
  if s['flavor']=='plain':p.execute('TestStep16TemplateCost',s['label'],costs/s['label'],extra())
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','run','validate']);ap.add_argument('--mode',default='plain',choices=['plain','probe']);ap.add_argument('--n',type=int,default=40);ap.add_argument('--seed',type=int,default=181802);a=ap.parse_args()
 if a.stage=='prepare':prepare()
 elif a.stage=='validate':validate()
 else:run(a.mode,a.n,a.seed)
