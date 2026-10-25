"""Rebuild per-attempt CSV and explicit unrun matrix. Never launches a test."""
from pathlib import Path
import json,csv,sys,itertools
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from run import reduce_attempt

def write(name,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (ROOT/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

outcomes=[json.loads(f.read_text()) for f in sorted((ROOT/'raw_logs').glob('*-outcome.json'))]
for o in outcomes:reduce_attempt(o['label'],o)
actual=[json.loads(f.read_text()) for f in sorted((ROOT/'raw_logs').glob('*-summary.json'))]
planned=[]
for method,pool,policy,batch in itertools.product(['bigNumCal','normalCal'],['original','capacity'],['R0','R1'],['a','b','c']):
    label=f'formal-{method}-{pool}-{policy.lower()}-{batch}';r=next((x for x in actual if x['label']==label),None)
    planned.append(r or dict(label=label,pool=pool,policy=policy,phase='formal',method=method,requested=100,observed=0,success=0,primary_accepted=False,status='not_run_safety_stop',invoke_mean_ms='',invoke_p50_ms='',invoke_p95_ms='',callmethod_mean_ms='',b5_export_mean_ms='',vm_log_tps_diagnostic_only=''))
write('formal_matrix.csv',planned);write('summary.csv',actual+[r for r in planned if r['status']=='not_run_safety_stop'])
checks=[]
for method,pool in itertools.product(['bigNumCal','normalCal'],['original','capacity']):
    sets={}
    for policy in ['R0','R1']:
        f=ROOT/'raw_logs'/f'isolated-{method}-{pool}-{policy.lower()}-a-samples.csv'
        if f.exists():sets[policy]=list(csv.DictReader(f.open()))
    if set(sets)!={'R0','R1'}:continue
    for a,b in zip(sets['R0'],sets['R1']):
        checks.append(dict(method=method,pool=pool,index=a['index'],input_equal=a['input_sha256']==b['input_sha256'],result_equal=a['result']==b['result'],gas_equal=a['gas']==b['gas'],r0_gas=a['gas'],r1_gas=b['gas'],scope='isolated functional diagnostic; not main performance'))
write('correctness.csv',checks)
assert len(actual)==9 and sum(int(x['observed']) for x in actual)==24
assert all(r['input_equal'] and r['result_equal'] and r['gas_equal'] for r in checks)
assert len(checks)==12
(ROOT/'verification.json').write_text(json.dumps(dict(actual_processes=9,isolated_processes=8,isolated_guest_successes=24,failed_as_is_pool_preflight=1,formal_processes=0,formal_calls=0,formal_planned_processes=24,all_owned_processes_stopped=all(o['all_owned_processes_stopped'] for o in outcomes),normalcal_new_sample_size_per_isolated_condition=3,no_capacity_effect_quantified=True,native_data_race_proven=False,guard_region_overlap_observed=True,stack_preserved=True),indent=2)+'\n')
print('saved 9 actual attempts + 24 unrun formal conditions; primary sample count 0')
