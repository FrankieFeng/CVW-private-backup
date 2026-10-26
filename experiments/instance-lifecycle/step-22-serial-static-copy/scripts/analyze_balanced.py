"""Keep the post-audit balanced-order supplement separate from primary results."""
from pathlib import Path
from collections import defaultdict
import csv,json,statistics as st
import analyze as a
P=a.P
raw=list(csv.DictReader((P/'samples.csv').open()))
rs=[r for r in raw if '-balanced-'in r['label']and r['method']!='init_contract'and r['depth']=='0']
for r in rs:
    assert r['passed_process']=='True'and r['code']=='0'and r['call_error_observed']=='<nil>'
    assert r['managed_before']==r['managed_after']
    r['batch']=int(r['label'].split('-batch-')[1]);r['static_init_ns']=int(r['newinstance_ns'])+int(r['copy_ns']);r['other_to_s1_ns']=int(r['to_s1_ns'])-r['static_init_ns']
    for k in a.metrics:r[k]=int(r[k])
summary=[];effects=[];paired=[];overview=[];checks=[];orders=[]
for c in ['compute','fact','erc721']:
    cs=[r for r in rs if r['contract']==c];assert len(cs)==12
    pairs=[]
    for b in [1,2,3]:
        bs=[r for r in cs if r['batch']==b];firsts=[]
        for tx in sorted({r['tx_id']for r in bs}):
            slot=[r for r in bs if r['tx_id']==tx];firsts.append(slot[0]['variant']);ps={r['variant']:r for r in slot}
            assert len(ps)==2 and ps['A0']['gas']==ps['A1']['gas']
            pairs.append(ps)
            orders.append(dict(series='balanced_supplement',contract=c,batch=b,tx_id=tx,first_variant=slot[0]['variant'],invoke_saving_ms=(ps['A0']['invoke_ns']-ps['A1']['invoke_ns'])/1e6))
            for k in a.metrics:paired.append(dict(contract=c,batch=b,tx_id=tx,metric=k[:-3],saving_ms=(ps['A0'][k]-ps['A1'][k])/1e6,baseline_ms=ps['A0'][k]/1e6,copy_ms=ps['A1'][k]/1e6))
            receipt=P/'raw_logs'/f'{c}-balanced-batch-{b}-receipts'
            i=int(tx.rsplit('-',1)[1]);aa=json.loads((receipt/f'pair-{i:03d}-A0.json').read_text());bb=json.loads((receipt/f'pair-{i:03d}-A1.json').read_text())
            for key in ['business_input','before_hash','after_hash','status','actual_result','actual_rwset']:assert aa[key]==bb[key],(c,b,tx,key)
        assert sorted(firsts)==['A0','A1'],'unbalanced order; supplement invalid'
    for v in ['A0','A1']:
        vr=[r for r in cs if r['variant']==v]
        for k in a.metrics:
            gs=[[r[k]/1e6 for r in vr if r['batch']==b]for b in [1,2,3]];lo,hi=a.boot(gs,st.median)
            summary.append(dict(contract=c,variant=v,metric=k[:-3],independent_batches=3,**a.stat(sum(gs,[])),median_ci95_low_ms=lo,median_ci95_high_ms=hi))
    for k in a.metrics:
        gs=[[(p['A0'][k]-p['A1'][k])/1e6 for p in pairs if p['A0']['batch']==b]for b in [1,2,3]]
        lo,hi=a.boot(gs,st.median);ml,mh=a.boot(gs,st.mean)
        effects.append(dict(contract=c,metric=k[:-3],n_pairs=6,independent_batches=3,median_saving_ms=st.median(sum(gs,[])),mean_saving_ms=st.mean(sum(gs,[])),median_ci95_low_ms=lo,median_ci95_high_ms=hi,mean_ci95_low_ms=ml,mean_ci95_high_ms=mh,positive_pairs=sum(x>0 for x in sum(gs,[])),batch_median_savings_ms=json.dumps([st.median(g)for g in gs])))
    sm={r['variant']:r for r in summary if r['contract']==c and r['metric']=='invoke'};eff=next(r for r in effects if r['contract']==c and r['metric']=='invoke')
    overview.append(dict(contract=c,baseline_median_ms=sm['A0']['median_ms'],copy_median_ms=sm['A1']['median_ms'],baseline_p95_ms=sm['A0']['p95_ms'],copy_p95_ms=sm['A1']['p95_ms'],**{k:eff[k]for k in ['n_pairs','independent_batches','median_saving_ms','median_ci95_low_ms','median_ci95_high_ms','positive_pairs','batch_median_savings_ms']}))
    checks.append(dict(contract=c,receipt_pairs=6,status='tested_scope_pass',gas_result_input_initial_final_state_rwset_events_equal=True,both_orders_present_each_batch=True,table_function_identity='not_tested',exception_paths='not_tested',s1_hash='same build preflight only; not repeated inside performance timing'))
for c in ['compute','fact','erc721']:
    cs=[r for r in raw if r['contract']==c and r['label'].startswith(c+'-batch-')and r['depth']=='0'and r['method']!='init_contract']
    for label,tx in sorted({(r['label'],r['tx_id'])for r in cs}):
        slot=[r for r in cs if r['label']==label and r['tx_id']==tx];ps={r['variant']:r for r in slot}
        orders.append(dict(series='primary_randomized',contract=c,batch=int(label.rsplit('-',1)[1]),tx_id=tx,first_variant=slot[0]['variant'],invoke_saving_ms=(int(ps['A0']['invoke_ns'])-int(ps['A1']['invoke_ns']))/1e6))
a.write('balanced_summary.csv',summary);a.write('balanced_paired_effects.csv',effects);a.write('balanced_paired_samples.csv',paired);a.write('balanced_correctness.csv',checks);a.write('balanced_ppt_table.csv',overview);a.write('execution_order.csv',orders)
sens=[]
for series in ['primary_randomized','balanced_supplement']:
    for c in ['compute','fact','erc721']:
        for first in ['A0','A1']:
            xs=[r['invoke_saving_ms']for r in orders if r['series']==series and r['contract']==c and r['first_variant']==first]
            sens.append(dict(series=series,contract=c,first_variant=first,n_pairs=len(xs),median_paired_saving_ms=st.median(xs),mean_paired_saving_ms=st.mean(xs)))
a.write('order_sensitivity.csv',sens)
(P/'balanced_analysis.json').write_text(json.dumps(dict(overview=overview,ci_method='same hierarchical paired bootstrap as primary',separate_supplement=True),indent=2)+'\n')
print('BALANCED',json.dumps(overview,indent=2))
