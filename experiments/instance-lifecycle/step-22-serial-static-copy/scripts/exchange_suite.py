"""Three split-process pairs, guarded by real cross-contract preflight equivalence."""
from pathlib import Path
import subprocess,sys
from verify_receipts import compare
P=Path(__file__).resolve().parents[1]
compare('exchange-preflight-A0','exchange-preflight-A1')
for batch in range(1,4):
    order=['A0','A1'] if batch%2 else ['A1','A0']
    for v in order:
        subprocess.run([sys.executable,'-B',str(P/'scripts/run.py'),f'exchange-batch-{batch}-{v}',
                        'exchange','--pairs','1','--phase','formal','--single',v,'--seed',str(22000+batch)],check=True)
    compare(f'exchange-batch-{batch}-A0',f'exchange-batch-{batch}-A1')
