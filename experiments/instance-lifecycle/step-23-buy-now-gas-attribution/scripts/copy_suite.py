from pathlib import Path
import json,subprocess,sys
from compare import compare
P=Path(__file__).resolve().parents[1]
complete=json.loads((P/'audit/lifecycle_complete.json').read_text());assert complete['stage_complete']
compare('v2-preflight-R1-on','v2-preflight-C1-on',require_gas=True)
for b in range(1,complete['paired_blocks']+1):
    order=['R1','C1']if b%2 else['C1','R1']
    for c in order:
        subprocess.run([sys.executable,'-B',str(P/'scripts/run.py'),f'v2-copy-b{b}-{c}',c,'--stage','copy','--block',str(b)],check=True)
    compare(f'v2-copy-b{b}-R1',f'v2-copy-b{b}-C1',require_gas=True)
(P/'audit/copy_complete.json').write_text(json.dumps(dict(paired_blocks=complete['paired_blocks'],stage_complete=True),indent=2)+'\n')
