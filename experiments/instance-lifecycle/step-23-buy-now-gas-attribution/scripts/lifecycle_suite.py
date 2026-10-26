"""Preflight gate, three independent pairs, extend to five only if stable and safe."""
from pathlib import Path
import json,subprocess,sys
from compare import compare
P=Path(__file__).resolve().parents[1]
for c in ['R0','R1','C1']:compare(f'v2-preflight-{c}-off',f'v2-preflight-{c}-on',require_gas=True)
compare('v2-preflight-R0-on','v2-preflight-R1-on')
compare('v2-preflight-R1-on','v2-preflight-C1-on',require_gas=True)
def run(b):
 order=['R0','R1']if b%2 else['R1','R0']
 for c in order:subprocess.run([sys.executable,'-B',str(P/'scripts/run.py'),f'v2-lifecycle-b{b}-{c}',c,'--stage','lifecycle','--block',str(b)],check=True)
 return compare(f'v2-lifecycle-b{b}-R0',f'v2-lifecycle-b{b}-R1')
results=[run(b)for b in [1,2,3]]
def signature(r):
 t=r['trace'];first=t.get('first')or{};v=first.get('a',{})
 return r['root_delta_b_minus_a'],t['status'],v.get('call_id'),v.get('seq'),v.get('phase'),v.get('host')
stable=len({signature(r)for r in results})==1 and results[0]['root_delta_b_minus_a']!=0
gate=dict(initial_pairs=3,stable_nonzero_difference=stable,signatures=[signature(r)for r in results],next='extend to 5 separate-process blocks'if stable else'no extension; analyze existing 3')
(P/'audit/extension_gate.json').write_text(json.dumps(gate,indent=2)+'\n')
with(P/'PROGRESS.md').open('a')as f:f.write('\n三独立生命周期配对块已核对，扩展gate：'+json.dumps(gate,ensure_ascii=False)+'。\n')
if stable:
 for b in [4,5]:results.append(run(b))
(P/'audit/lifecycle_complete.json').write_text(json.dumps(dict(paired_blocks=len(results),stage_complete=True),indent=2)+'\n')
