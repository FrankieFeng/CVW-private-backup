"""Audit frozen historical tables and raw block1 logs without executing guest code."""
from pathlib import Path
import csv,json
P=Path(__file__).resolve().parents[1];H=P/'audit/history'
rows=list(csv.DictReader((H/'BLOCK_SUMMARY.csv').open()))
r=[x for x in rows if x['stage']=='lifecycle'];assert len(r)==5
assert all((x['root_gas_a'],x['root_gas_b'],x['root_delta_b_minus_a'])==('12761395','12765774','4379')for x in r)
c=list(csv.DictReader((H/'COPY_PARITY.csv').open()));assert len(c)==35
assert all(x['gas_equal']=='True'and x['input_result_rw_events_equal']=='True'for x in c)
points={}
for mode in ['R0','R1']:
 es=[json.loads(l[7:])for l in(H/'raw_logs'/f'v2-lifecycle-b1-{mode}.log').read_text().splitlines()if l.startswith('STEP23 ')]
 gas=[x for x in es if x['event']=='gas'and x['tx_id']=='step21c-buy-001'and x['call_id']==6]
 points[mode]={str(x['seq']):x['gas_absolute']for x in gas if x['seq']in [36,37]}
assert points=={'R0':{'36':6378616,'37':6386180},'R1':{'36':6378616,'37':6390559}}
out=dict(historical_lifecycle_blocks=len(r),historical_copy_pairs=len(c),raw_block1_selected_points=points,only_valid_v2=True)
(P/'audit/history-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
