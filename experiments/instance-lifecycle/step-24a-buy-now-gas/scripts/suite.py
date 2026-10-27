"""Registered sequence; one bounded process at a time; never bypass a new failure."""
from pathlib import Path
import subprocess,sys
from compare import compare
P=Path(__file__).resolve().parents[1]
def run(label,mode,stage,block,probe):
 subprocess.run([sys.executable,'-B',str(P/'scripts/run.py'),label,mode,'--stage',stage,'--block',str(block),'--probe',probe],check=True)
for mode in ['R1','R0','S0','J','U']:
 for probe in ['off','on']:run(f'safe-preflight-{mode}-{probe}',mode,'preflight',0,probe)
 compare(f'safe-preflight-{mode}-off',f'safe-preflight-{mode}-on',require_gas=True)
for block,order in enumerate([['R0','R1','S0','J','U'],['U','J','S0','R1','R0'],['S0','R1','J','R0','U']],1):
 for mode in order:run(f'safe-block{block}-{mode}',mode,'formal',block,'on')
 for mode in ['R0','S0','J','U']:compare(f'safe-block{block}-R1',f'safe-block{block}-{mode}')
 with(P/'PROGRESS.md').open('a')as f:f.write(f'\n正式块{block}五条件完成；逐callee业务/操作/最终RWSet/事件已compare断言通过。\n')
