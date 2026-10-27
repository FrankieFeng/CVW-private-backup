"""Bounded, resumable screening. All pair contrasts measured directly, never median subtraction."""
from pathlib import Path
import json,argparse
from run import run
from check_pair import local,setup_check
P=Path(__file__).resolve().parents[1]
EDGES=[('G0','G1'),('G0','G2'),('G0','G3'),('G0','G4'),('G1','G2'),('G1','G3'),('G1','G4'),('G2','G4')]
def checked(label,c,a,b,n,phase,**kwargs):
 o=run(label,c,left=a,right=b,pairs=n,phase=phase,**kwargs);assert o['passed']
 try:local(label,n);assert setup_check(label)==1
 except Exception as e:
  (P/'STOP.json').write_text(json.dumps({'label':label,'reason':'offline semantic check: '+str(e),'stop_all':True},indent=2));raise
 (P/'raw_logs'/f'{label}-checks.json').write_text(json.dumps({'setup_semantic_equal':True,'paired_receipts_equal':n,'includes_gas':True,'table_identity':'not_tested'},indent=2)+'\n')
def preflight(c):
 for i,(a,b)in enumerate(EDGES[:4]):checked(f'pre2-{c}-{a}-{b}',c,a,b,1,'preflight',first=i%2,module_first='A1'if i%2 else'A0')
 for i,g in enumerate(['G2','G3','G4']):checked(f'pre2-{c}-{g}-copycheck',c,g,g,1,'preflight',copy_check=True,first=i%2,module_first='A1'if i%2 else'A0')
 with(P/'PROGRESS.md').open('a')as f:f.write(f'\n{c}四个G0配对及三种新WASM各自Copy off/on功能/S1/Gas/业务预检全部通过。\n')
def formal(contracts):
 for c in contracts:
  for label in [f'pre2-{c}-G0-G{i}'for i in range(1,5)]+[f'pre2-{c}-G{i}-copycheck'for i in range(2,5)]:
   assert json.loads((P/'raw_logs'/f'{label}-outcome.json').read_text())['passed'] and (P/'raw_logs'/f'{label}-checks.json').exists(),'preflight gate missing'
 for batch in range(1,4):
  order=EDGES if batch%2 else list(reversed(EDGES))
  for edge_index,(a,b)in enumerate(order):
   for cindex,c in enumerate(contracts if batch%2 else list(reversed(contracts))):
    for slot in range(3):
     first=(slot+batch+edge_index+cindex)%2
     checked(f'{c}-b{batch}-{a}-{b}-p{slot}',c,a,b,2,'formal',batch=batch,slot=slot,first=first,module_first='A1'if first else'A0')
  with(P/'PROGRESS.md').open('a')as f:f.write(f'\n正式批{batch} contracts={contracts}完成，所有8条直接对照各6对，逐过程日志/receipt/check/outcome已保存。\n')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['preflight-primary','formal-primary','preflight-normal','formal-normal']);a=ap.parse_args()
 if a.stage=='preflight-primary':
  for c in ['compute','fact','erc721']:preflight(c)
 elif a.stage=='formal-primary':formal(['compute','fact','erc721'])
 elif a.stage=='preflight-normal':preflight('normal')
 else:formal(['normal'])
