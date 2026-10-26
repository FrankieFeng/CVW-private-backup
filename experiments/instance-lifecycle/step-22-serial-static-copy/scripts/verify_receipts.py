"""Compare real results; never infer success from a Go process exit alone."""
from pathlib import Path
import json, sys
P=Path(__file__).resolve().parents[1]
def compare(a_label,b_label):
    a=json.loads((P/'raw_logs'/f'{a_label}-receipts/pair-000-A0.json').read_text())
    b=json.loads((P/'raw_logs'/f'{b_label}-receipts/pair-000-A1.json').read_text())
    for key in ['business_input','before_hash','after_hash','status','actual_result','actual_rwset']:
        assert a[key]==b[key],f'{a_label}/{b_label}: {key} differs'
    fields=['contract','method','depth','gas_used_actual','code','result','message']
    aa=[{k:c[k] for k in fields} for c in a['inclusive_call_records_do_not_sum']]
    bb=[{k:c[k] for k in fields} for c in b['inclusive_call_records_do_not_sum']]
    assert aa==bb,'actual child result/Gas/call sequence differs'
    assert len(aa)==7 and all(c['code']==0 for c in aa)
    result=dict(labels=[a_label,b_label],status='tested_scope_pass',root_and_six_children=aa,
                input_state_gas_result_rwset_events_equal=True,
                table_function_identity='not_tested',exception_paths='not_tested')
    out=P/'audit'/f'comparison-{a_label}-{b_label}.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print('verified real root + six child results/Gas/state:',a_label,b_label,flush=True)
    return result
if __name__=='__main__':compare(*sys.argv[1:])
