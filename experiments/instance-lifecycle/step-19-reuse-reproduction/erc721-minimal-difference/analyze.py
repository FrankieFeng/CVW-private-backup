"""Reduce saved candidate-ERC721 runs. No node execution."""
from pathlib import Path
import base64, collections, csv, hashlib, json, math, statistics
from run_low import invoke_logs, events

ROOT=Path(__file__).resolve().parent


def write(name,rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def p95(values):return sorted(values)[math.ceil(.95*len(values))-1]


def main():
    raw=[json.loads(x) for x in (ROOT/'requests.jsonl').read_text().splitlines()]
    resources=[json.loads(x) for x in (ROOT/'resources.jsonl').read_text().splitlines()]
    inputs=json.loads((ROOT/'inputs.json').read_text())
    commits={(x['batch'],x['policy'],x['transaction']['transaction']['payload']['tx_id']):x['transaction']
             for x in raw if x['phase']=='commit-check'}
    samples=[];summaries=[];checks=[];paired=collections.defaultdict(dict)
    for batch,policy in [('a','R0'),('a','R1'),('b','R1'),('b','R0')]:
        home=ROOT/batch/'network'/('baseline' if policy=='R0' else 'optimized')
        logs=invoke_logs(home);bytx=collections.defaultdict(list)
        for x in logs:bytx[x['tx_id']].append(x)
        ee=events(home);begins=[e for e in ee if e['event']=='create_begin'];costs=[e for e in ee if e['event']=='create']
        assert len(begins)==len(costs)
        newcost={b['instance_id']:c['elapsed_ns'] for b,c in zip(begins,costs)}
        replacements=costs[6:];create_ns=[x['elapsed_ns'] for x in replacements]
        rr=[x for x in resources if x['batch']==batch and x['policy']==policy]
        start=next(x for x in rr if x['label']=='post-deploy');last=rr[-1]
        acquire_costs=[e['elapsed_ns'] for e in ee if e['event']=='acquire' and not e['instance_id']]
        selected=[]
        for row in raw:
            if row['batch']!=batch or row['policy']!=policy or row['phase']!='sample':continue
            tx=row['response']['tx_id'];matches=bytx[tx];assert len(matches)==1
            log=matches[0];assert log['method']=='mint' and log['code']==0 and log['end_ns']>log['begin_ns']
            info=commits[batch,policy,tx];payload=info['transaction']['payload']
            actual={p['key']:base64.b64decode(p.get('value','')).decode() for p in payload.get('parameters',[])}
            assert all(actual.get(k)==v for k,v in inputs[row['index']].items())
            acquired=[e for e in ee if e['event']=='acquire' and e['instance_id'] and log['begin_ns']<=e['unix_ns']<=log['end_ns']]
            assert len(acquired)==1
            sample=dict(batch=batch,pressure='low_serial_quiescent',policy=policy,index=row['index'],tx_id=tx,
                        instance_id=acquired[0]['instance_id'],vm_begin_ns=log['begin_ns'],vm_end_ns=log['end_ns'],
                        vm_ns=log['end_ns']-log['begin_ns'],client_ns=row['elapsed_ns'],
                        gas_reported=row['response'].get('contract_result',{}).get('gas_used',0),
                        block_height=info['block_height'],committed_success=True,
                        source_file=log['file'],source_line=log['line'],getinstance_blocking_wait_ns=0)
            samples.append(sample);selected.append(sample)
            paired[batch,row['index']][policy]=(row,info)
        durations=[x['vm_ns'] for x in selected];assert len(durations)==10
        summaries.append(dict(batch=batch,pressure='low_serial_quiescent',policy=policy,n=len(durations),
                              mean_invoke_ms=statistics.mean(durations)/1e6,median_invoke_ms=statistics.median(durations)/1e6,
                              p95_invoke_ms=p95(durations)/1e6,vm_log_tps=len(durations)*1e9/sum(durations),
                              empty_pool_events=sum(e['event']=='acquire_wait' for e in ee),
                              getinstance_blocking_wait_ns=0,
                              acquire_function_median_ms=statistics.median(acquire_costs)/1e6,
                              acquire_scope='all 16 borrows, includes instrumentation; not pure channel wait',
                              total_creates=len(costs),verification_and_initial_creates=6,replacement_creates=len(replacements),
                              replacement_median_ms=statistics.median(create_ns)/1e6 if create_ns else '',
                              replacement_p95_ms=p95(create_ns)/1e6 if create_ns else '',
                              rss_peak_mib=max(x['VmRSS'] for x in rr)/1024,
                              post_deploy_rss_growth_mib=(last['VmRSS']-start['VmRSS'])/1024,
                              threads_peak=max(x['Threads'] for x in rr),errors=0,
                              reported_gas_values=json.dumps(dict(collections.Counter(x['gas_reported'] for x in selected))),
                              evidence='10 samples per independent batch; swapped order; no CI claim',
                              concurrency_safety='only externally quiescent serial path; pressure gate not passed'))
    for (batch,index),modes in paired.items():
        (a,ai),(b,bi)=modes['R0'],modes['R1']
        ar=a['response'].get('contract_result',{});br=b['response'].get('contract_result',{})
        def writes(info,normalize):
            result=json.loads(json.dumps(info.get('rw_set',{}).get('tx_writes',[])))
            for x in result:
                key=base64.b64decode(x.get('key','')).decode(errors='replace')
                if normalize and key.endswith('_latestTxInfo'):
                    value=json.loads(base64.b64decode(x['value']));value.pop('TxId',None)
                    x['value']=json.dumps(value,sort_keys=True)
            return sorted(result,key=lambda x:json.dumps(x,sort_keys=True))
        def event(result):return [{k:v for k,v in x.items() if k!='tx_id'} for x in result.get('contract_event',[])]
        checks.append(dict(batch=batch,index=index,return_equal=ar.get('result')==br.get('result'),
                           raw_writes_equal=writes(ai,False)==writes(bi,False),
                           writes_equal_except_transaction_id=writes(ai,True)==writes(bi,True),
                           events_equal_except_transaction_id=event(ar)==event(br),
                           r0_gas=ar.get('gas_used',0),r1_gas=br.get('gas_used',0),
                           gas_equal=ar.get('gas_used',0)==br.get('gas_used',0),
                           certified_safe=False,table='not_tested'))
    comparisons=[]
    for batch in ['a','b','pooled_descriptive']:
        modes={}
        for policy in ['R0','R1']:
            ds=[x['vm_ns'] for x in samples if x['policy']==policy and (batch=='pooled_descriptive' or x['batch']==batch)]
            modes[policy]=dict(n=len(ds),mean=statistics.mean(ds)/1e6,tps=len(ds)*1e9/sum(ds))
        a,b=modes['R0'],modes['R1']
        comparisons.append(dict(pressure='low_serial_quiescent',batch=batch,n_each=a['n'],
                                r0_mean_ms=a['mean'],r1_mean_ms=b['mean'],r0_vm_log_tps=a['tps'],r1_vm_log_tps=b['tps'],
                                r0_over_r1_tps_ratio=a['tps']/b['tps'],r1_tps_drop_pct=(1-b['tps']/a['tps'])*100,
                                empty_pool_events=0,blocking_pool_wait_ms=0,
                                scope='candidate WASM, original factory INFO, serial low-load; R0 Gas differs'))
    comparisons.append(dict(pressure='higher_load',batch='not_run',n_each=0,r0_mean_ms='',r1_mean_ms='',
                            r0_vm_log_tps='',r1_vm_log_tps='',r0_over_r1_tps_ratio='',
                            empty_pool_events='',blocking_pool_wait_ms='',
                            scope='blocked: concurrent shared Store access and native retention not controlled; no global lock added'))
    write('samples.csv',samples);write('summary.csv',summaries);write('comparison.csv',comparisons);write('correctness.csv',checks)
    bad=[x for x in checks if not (x['return_equal'] and x['writes_equal_except_transaction_id'] and x['events_equal_except_transaction_id'])]
    print('original factory samples',len(samples),'paired state checks',len(checks),'unexpected state/result differences',len(bad),
          'reported Gas differences',sum(not x['gas_equal'] for x in checks))
    for x in comparisons:print(x['batch'],x['r0_mean_ms'],x['r1_mean_ms'],x['r0_over_r1_tps_ratio'])
    assert not bad,bad


if __name__=='__main__':main()
