"""Within-round factorial confirmation of frozen step-18 artifacts."""
from pathlib import Path
import csv, hashlib, itertools, json, math, random, re, statistics, sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
sys.path.insert(0, str(ROOT.parents[0]/'step-15-copy-attribution'))
from common import stats
CELLS = list(itertools.product(range(2), repeat=3))
CONTRACTS = ['compute','erc721','fact']

def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]

def write(name, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)

def simple(v):
    return dict(n=len(v),median_ns=statistics.median(v),p95_ns=sorted(v)[math.ceil(.95*len(v))-1])

def ci(v):
    return stats(v,seed=181950,block=10,reps=4000)

def main():
    specs = json.loads((ROOT/'manifest-full.json').read_text())
    audit = {s['label']:s for s in json.loads((OUT/'audit.json').read_text())['variant_checks']}
    summary, effects, interactions, correctness, samples, resources, ppt, modules = [], [], [], [], [], [], [], []
    contrast = dict(AC_vs_C=((1,0,1),(0,0,1)), APC_vs_AC=((1,1,1),(1,0,1)),
                    APC_vs_C=((1,1,1),(0,0,1)), PC_vs_C=((0,1,1),(0,0,1)),
                    P_vs_000=((0,1,0),(0,0,0)), A_vs_000=((1,0,0),(0,0,0)),
                    AP_vs_A=((1,1,0),(1,0,0)))
    semantic = ['result','result_code','message','writes_sha256','events','special','cross_calls']
    gas = ['registry_gas','native_business_gas','native_init_and_setgas_gas']
    def equal(a,b,keys): return all(a.get(k)==b.get(k) for k in keys)
    for batch in ['confirm-a','probe-a','confirm-b','probe-b','confirm-c']:
        plain = batch.startswith('confirm')
        flavor = 'plain' if plain else 'probe'
        for contract in CONTRACTS:
            rows = read(OUT/batch/(contract+'.jsonl'))
            raw = [r for r in rows if r['kind']=='sample']
            assert len(raw)==1200
            by = {(r['sample'],r['A'],r['P'],r['C']):r for r in raw}
            assert len(by)==1200 and len({r['instance_id'] for r in raw})==1200
            for r in rows:
                if r['kind']=='module':
                    label=f'{contract}-a{r["A"]}p{r["P"]}-{flavor}'
                    assert r['source_sha256']==audit[label]['wasm_sha']
                    assert r['template_sha256']==audit[label]['image_sha']
                    assert r['config_id']==audit[label]['config']
                    modules.append(dict(batch=batch,**r))
            for r in raw:
                assert r['result_code']==0 and r['expected_output']
                assert equal(r,by[r['sample'],0,0,0],semantic)
                assert equal(r,by[r['sample'],r['A'],r['P'],1-r['C']],semantic+gas)
                if not plain and r['A']==1:
                    assert r['first_reserve_bloc']==4194304 and r['first_alignment_skip_bytes']==0
                samples.append(dict(batch=batch,**r))
            metrics = ['s1_ns','start_ns','s2_ns','s3_ns','invoke_ns','copy_ns'] if plain else ['a_ns','b1_ns','clock_uncertainty_ns']
            for cell in CELLS:
                rs = [by[(i,)+cell] for i in range(150)]
                for metric in metrics:
                    summary.append(dict(batch=batch,contract=contract,A=cell[0],P=cell[1],C=cell[2],
                                        scope='plain_VM_Invoke' if plain else 'diagnostic_only',metric=metric,
                                        **simple([r[metric] for r in rs])))
                if plain:
                    st = simple([r['invoke_ns'] for r in rs])
                    ppt.append(dict(batch=batch,contract=contract,A=cell[0],P=cell[1],C=cell[2],
                                    median_ms=st['median_ns']/1e6,p95_ms=st['p95_ns']/1e6,n=150,
                                    evidence='three_independent_batches_tested_scope',
                                    compatibility='removed_GetBatchState_API' if cell[1] else 'original_SDK_API',
                                    safety='not_certified'))
                    correctness.append(dict(batch=batch,contract=contract,A=cell[0],P=cell[1],C=cell[2],n=150,
                                            business_results_writes_events='pass',copy_same_binary_gas='pass',fresh_unique_ids='pass',
                                            registry_gas=sorted({r['registry_gas'] for r in rs}),
                                            native_business_gas=sorted({r['native_business_gas'] for r in rs}),
                                            native_init_and_setgas_gas=sorted({r['native_init_and_setgas_gas'] for r in rs}),
                                            cross_binary_gas_acceptability='not_certified',table_identity='not_tested',
                                            cross_contract='not_tested',api='incompatible_for_GetBatchState_users' if cell[1] else 'original_API'))
            contrast_metrics = ['invoke_ns','start_ns','s1_ns','copy_ns'] if plain else ['a_ns','b1_ns']
            for name,(opt,ref) in contrast.items():
                for metric in contrast_metrics:
                    v=[by[(i,)+opt][metric]-by[(i,)+ref][metric] for i in range(150)]
                    row=dict(batch=batch,contract=contract,contrast=name,metric=metric,
                             sign='optimized_minus_reference_negative_faster',**ci(v))
                    if plain:
                        a=[by[(i,)+opt][metric] for i in range(150)]
                        b=[by[(i,)+ref][metric] for i in range(150)]
                        row['p95_change_ns']=simple(a)['p95_ns']-simple(b)['p95_ns']
                    effects.append(row)
            # Interactions are finite differences computed in each round, never medians subtracted.
            interaction_metrics=['invoke_ns','start_ns','s1_ns','copy_ns'] if plain else ['a_ns','b1_ns']
            for axis0,axis1,other,name in [(0,1,2,'A_x_P'),(1,2,0,'P_x_C'),(0,2,1,'A_x_C')]:
                for fixed in [0,1]:
                    terms=[]
                    for u,v in itertools.product([0,1],repeat=2):
                        cell=[0,0,0];cell[axis0]=u;cell[axis1]=v;cell[other]=fixed
                        terms.append((tuple(cell),1 if u==v else -1))
                    for metric in interaction_metrics:
                        d=[sum(sign*by[(i,)+cell][metric] for cell,sign in terms) for i in range(150)]
                        interactions.append(dict(batch=batch,contract=contract,interaction=name+'_other'+str(fixed),
                                                 metric=metric,sign='positive_antagonism_negative_synergy',**ci(d)))
            text=(OUT/batch/(contract+'.resources.txt')).read_text()
            resources.append(dict(batch=batch,contract=contract,n_per_cell=150,pools=8,
                                  peak_rss_kib=int(re.search(r'Maximum resident set size \(kbytes\): (\d+)',text)[1]),
                                  scope='whole_eight_pool_worker_not_per_combination_RSS'))
            print('analyzed',batch,contract,flush=True)
    for name,data in [('samples.csv',samples),('summary.csv',summary),('paired_effects.csv',effects),
                      ('interactions.csv',interactions),('correctness.csv',correctness),('rss.csv',resources),
                      ('ppt_data.csv',ppt),('modules.csv',modules)]:write(name,data)
    # Recheck original safety fixtures with the identical binary; keep not_tested explicit.
    checks=[]
    for path in (OUT/'validation').glob('*-checks.jsonl'):
        for r in read(path):
            assert r['s1_checks']>0 and r['s1_mismatches']==0 and r['fresh_memory_isolation'] and r['template_immutable']
            checks.append(r)
    assert len(checks)==24
    check_index={(r['contract'],r['A'],r['P'],r['C']):r for r in checks}
    for r in checks:
        peer=check_index[r['contract'],r['A'],r['P'],1-r['C']]
        assert equal(r['success'],peer['success'],semantic+gas)
        assert equal(r['exception'],peer['exception'],semantic+['registry_gas','native_business_gas'])
        if r['contract']!='compute':
            assert r['guest_error']['result_code']!=0
            assert equal(r['guest_error'],peer['guest_error'],semantic+['registry_gas','native_business_gas'])
    write('validation_checks.csv',checks)
    for path in (OUT/'validation').glob('*-plain.jsonl'):
        for r in read(path):
            assert r['fresh_memory_globals_isolation']
            assert all(s['table_nullness_mismatches']==0 for s in r['stages'])
            assert all(s['globals_table_size_equal'] for s in r['stages'] if s['stage']=='S1')
            assert all(s['s1_memory_equal'] for s in r['stages'] if s['stage']=='S1')
    print('all 18000 samples qualified in selected scope; 24 safety checks passed',flush=True)

if __name__=='__main__': main()
