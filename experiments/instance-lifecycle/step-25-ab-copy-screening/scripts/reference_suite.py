from pathlib import Path
import json
from run import run
from check_pair import local,setup_check
P=Path(__file__).resolve().parents[1]
def check(label,c,phase,n,batch=0,slot=0):
 o=run(label,c,pairs=n,phase=phase,batch=batch,slot=slot,first=(batch+slot)%2,module_first='A1'if(batch+slot)%2 else'A0',family='step24b');assert o['passed']
 try:local(label,n);assert setup_check(label)==1
 except Exception as e:(P/'STOP.json').write_text(json.dumps({'label':label,'reason':str(e)}));raise
 (P/'raw_logs'/f'{label}-checks.json').write_text(json.dumps({'paired_receipts_equal':n,'family':'step24b','gas_equal':True})+'\n')
for c in ['compute','fact','erc721']:check('ref-pre-'+c,c,'reference-preflight',1)
for b in range(1,4):
 for c in ['compute','fact','erc721']if b%2 else['erc721','fact','compute']:
  for slot in range(3):check(f'ref-{c}-b{b}-p{slot}',c,'reference',2,b,slot)
 with(P/'PROGRESS.md').open('a')as f:f.write(f'\n原Step24B WASM参考批{b}全部3方法G0/G1每组6对完成；与主矩阵分开。\n')
