"""Read-only reduction of saved data; no benchmarks. stdlib, seed-fixed cluster bootstrap."""
from pathlib import Path
from collections import defaultdict
import csv,json,math,random,statistics as st
P=Path(__file__).resolve().parents[1]
SEED=22026026
REPS=10000
def write(name,rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with(P/name).open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def quantile(xs,p):
    v=sorted(xs);q=(len(v)-1)*p;i=int(q)
    return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(q-i)
def stat(xs):
    return dict(n=len(xs),mean_ms=st.mean(xs),median_ms=st.median(xs),p95_ms=sorted(xs)[math.ceil(.95*len(xs))-1])
def boot(groups,func):
    # Resample independent batches, then paired sample slots within each selected batch.
    rng=random.Random(SEED);bs=[];groups=list(groups)
    for _ in range(REPS):
        vals=[]
        for g in rng.choices(groups,k=len(groups)):
            vals.extend(rng.choices(g,k=len(g)))
        bs.append(func(vals))
    return quantile(bs,.025),quantile(bs,.975)
raw=list(csv.DictReader((P/'samples.csv').open()))
formal=[r for r in raw if r['phase']=='formal' and '-balanced-' not in r['label'] and r['passed_process']=='True' and not r['tx_id'].startswith('step22-init-')]
for r in formal:
    for k in list(r):
        if k.endswith('_ns')or k in ['depth','gas','code','instance_id','copy_bytes','copy_ranges','managed_before','managed_after']:
            r[k]=int(r[k])
    assert r['code']==0 and r['call_error_observed']=='<nil>'
    assert r['managed_before']==r['managed_after']
    r['batch']=int(r['label'].split('-batch-')[1].split('-')[0])
    r['static_init_ns']=r['newinstance_ns']+r['copy_ns']
    r['other_to_s1_ns']=r['to_s1_ns']-r['static_init_ns']
roots=[r for r in formal if r['depth']==0]
metrics=['newinstance_ns','copy_ns','static_init_ns','wasi_imports_ns','other_to_s1_ns','to_s1_ns','wasi_initialize_ns','start_ns','to_s2_ns','callmethod_ns','to_s3_ns','close_ns','invoke_ns']
summary=[];effects=[];paired=[];batches=[];overview=[]
for c in ['compute','fact','erc721','exchange']:
    rs=[r for r in roots if r['condition_contract']==c]
    for v in ['A0','A1']:
        vs=[r for r in rs if r['variant']==v]
        assert len(vs)==(3 if c=='exchange' else 9)
        for metric in metrics:
            groups=[[r[metric]/1e6 for r in vs if r['batch']==b]for b in [1,2,3]]
            lo,hi=boot(groups,st.median)
            summary.append(dict(contract=c,variant=v,metric=metric[:-3],independent_batches=3,**stat([r[metric]/1e6 for r in vs]),median_ci95_low_ms=lo,median_ci95_high_ms=hi))
        for b in [1,2,3]:
            vr=[r for r in vs if r['batch']==b]
            batches.append(dict(contract=c,variant=v,batch=b,**stat([r['invoke_ns']/1e6 for r in vr]),gas_values=json.dumps(sorted({r['gas']for r in vr})),all_business_pass=True))
    slots=sorted({(r['batch'],r['tx_id'])for r in rs})
    pairs=[]
    for b,tx in slots:
        ps={r['variant']:r for r in rs if r['batch']==b and r['tx_id']==tx}
        assert set(ps)=={'A0','A1'}
        assert ps['A0']['gas']==ps['A1']['gas']
        pairs.append(ps)
        for metric in metrics:
            paired.append(dict(contract=c,batch=b,tx_id=tx,metric=metric[:-3],baseline_ms=ps['A0'][metric]/1e6,copy_ms=ps['A1'][metric]/1e6,saving_ms=(ps['A0'][metric]-ps['A1'][metric])/1e6))
    for metric in metrics:
        gs=[[(p['A0'][metric]-p['A1'][metric])/1e6 for p in pairs if p['A0']['batch']==b]for b in [1,2,3]]
        values=sum(gs,[]);lo,hi=boot(gs,st.median);ml,mh=boot(gs,st.mean)
        denom=st.median(p['A0'][metric]/1e6 for p in pairs)
        effects.append(dict(contract=c,metric=metric[:-3],n_pairs=len(values),independent_batches=3,median_saving_ms=st.median(values),mean_saving_ms=st.mean(values),median_ci95_low_ms=lo,median_ci95_high_ms=hi,mean_ci95_low_ms=ml,mean_ci95_high_ms=mh,median_saving_pct_of_baseline_median=(100*st.median(values)/denom if denom else ''),positive_pairs=sum(v>0 for v in values),positive_batch_medians=sum(st.median(g)>0 for g in gs),batch_median_savings_ms=json.dumps([st.median(g)for g in gs]),ci_method='hierarchical paired bootstrap: resample 3 batches, then slots; seed 22026026; B=10000'))
    one={x['variant']:x for x in summary if x['contract']==c and x['metric']=='invoke'}
    e=next(x for x in effects if x['contract']==c and x['metric']=='invoke')
    overview.append(dict(contract=c,baseline_median_ms=one['A0']['median_ms'],copy_median_ms=one['A1']['median_ms'],baseline_p95_ms=one['A0']['p95_ms'],copy_p95_ms=one['A1']['p95_ms'],**{k:e[k]for k in ['n_pairs','independent_batches','median_saving_ms','median_saving_pct_of_baseline_median','median_ci95_low_ms','median_ci95_high_ms','positive_pairs','positive_batch_medians','batch_median_savings_ms']}))
write('summary.csv',summary);write('paired_samples.csv',paired);write('paired_effects.csv',effects);write('batch_summary.csv',batches);write('ppt_table.csv',overview)

# Child time is already inside root CallMethod and Invoke; do not add inclusive Invoke times.
totals=[]
for b in [1,2,3]:
    for v in ['A0','A1']:
        rs=[r for r in formal if r['condition_contract']=='exchange' and r['batch']==b and r['variant']==v]
        assert len(rs)==7
        root=next(r for r in rs if r['depth']==0)
        totals.append(dict(batch=b,variant=v,instance_count=len(rs),root_invoke_ms=root['invoke_ns']/1e6,
            all_7_instances_static_ms=sum(r['static_init_ns']for r in rs)/1e6,
            all_7_start_ms=sum(r['start_ns']for r in rs)/1e6,
            all_7_close_ms=sum(r['close_ns']for r in rs)/1e6,
            root_callmethod_inclusive_ms=root['callmethod_ns']/1e6,
            child_6_invoke_ms=sum(r['invoke_ns']for r in rs if r['depth']>0)/1e6,
            child_6_creation_to_s2_ms=sum(r['to_s2_ns']for r in rs if r['depth']>0)/1e6))
write('exchange_transaction_stages.csv',totals)

# Actual receipt equality checks, independently recomputed from disk.
checks=[]
from verify_receipts import compare
compare('exchange-preflight-A0','exchange-preflight-A1')
for b in [1,2,3]:compare(f'exchange-batch-{b}-A0',f'exchange-batch-{b}-A1')
for c in ['compute','fact','erc721']:
    checked=0
    for label in [f'v4-preflight-{c}']+[f'{c}-batch-{b}'for b in [1,2,3]]:
        for a in (P/'raw_logs'/f'{label}-receipts').glob('pair-*-A0.json'):
            aa=json.loads(a.read_text());bb=json.loads(a.with_name(a.name.replace('A0','A1')).read_text())
            for k in ['business_input','before_hash','after_hash','status','actual_result','actual_rwset']:assert aa[k]==bb[k],(label,k)
            assert aa['status']==0 and aa['actual_result'].get('code',0)==0
            checked+=1
    checks.append(dict(contract=c,equivalent_receipt_pairs=checked))
checks.append(dict(contract='exchange',equivalent_receipt_pairs=4))
for ck in checks:
    c=ck['contract'];label=f'v4-preflight-{c}'if c!='exchange' else'exchange-preflight-'
    ss=[r for r in raw if r['label'].startswith(label)and r['s1_hash']]
    assert len(ss)==(14 if c=='exchange' else 2)
    assert all(r['managed_before']==r['managed_after']and r['code']=='0'for r in ss)
    gs=defaultdict(set)
    for r in ss:gs[r['contract']].add(r['s1_hash'])
    assert all(len(h)==1 for h in gs.values())
    ck.update(status='tested_scope_pass',s1_memory='tested_pass: full memory SHA equals expected template before _start',return_gas_rwset_events='tested_pass',fresh_business_instances='tested_pass; no reuse',isolation='tested_pass in sequential scope: real S1 hash plus scalar mutate/new-zero',table_function_identity='not_tested',internal_globals='not_tested dynamically; original non-Data sections preserved',exceptions='not_tested',cross_contract='tested_pass real 6 children'if c=='exchange'else'not_tested',long_running_memory_bound='not_tested',production_safe='not_certified')
write('correctness.csv',checks)

# Merge external sampling with synchronous boundary snapshots (external sampling misses short peaks).
resources=[]
for out in sorted((P/'raw_logs').glob('*-outcome.json')):
    o=json.loads(out.read_text());events=[]
    for line in (P/'raw_logs'/f"{o['label']}.log").read_text().splitlines():
        if line.startswith('STEP21C '):events.append(json.loads(line[8:]))
    owner=next((e for e in events if e.get('event')=='owner_closed'),{})
    resources.append(dict(label=o['label'],contract=o['contract'],phase=o['phase'],passed=o['passed'],
        peak_rss_kib=max([o['peak_rss_kib']]+[e.get('VmRSS',0)for e in events]),peak_threads=max([o['peak_threads']]+[e.get('Threads',0)for e in events]),
        after_owner_rss_kib=owner.get('VmRSS',''),after_owner_threads=owner.get('Threads',''),managed_after=owner.get('managed_objects',''),
        all_owned_processes_stopped=o['all_owned_processes_stopped']))
write('resource_summary.csv',resources)

report=dict(bootstrap_seed=SEED,bootstrap_replicates=REPS,small_sample_warning='Only 3 independent batches; P95 nearest rank = max for N<=9; bootstrap CI exploratory.',overview=overview)
(P/'analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
