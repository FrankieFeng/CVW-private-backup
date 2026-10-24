"""Reduce every saved Step-21 attempt, including failures and stopped runs."""
from pathlib import Path
from collections import Counter, defaultdict
import base64
import csv
import json
import math
import statistics
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'scripts'))
from run import semantic_success


def write(name, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (ROOT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def ms_stats(values, prefix):
    if not values:
        return {prefix+'_mean_ms': '', prefix+'_p50_ms': '', prefix+'_p95_ms': ''}
    return {prefix+'_mean_ms': statistics.mean(values)/1e6,
            prefix+'_p50_ms': statistics.median(values)/1e6,
            prefix+'_p95_ms': sorted(values)[math.ceil(.95*len(values))-1]/1e6}


def main():
    cases = {x['case']:x for x in json.loads((ROOT/'cases.json').read_text())}
    inputs = {c:json.loads(Path(x['inputs_file']).read_text()) for c,x in cases.items()}
    summaries, samples, errors, creation_rows, lifecycle, checks = [], [], [], [], [], []
    for f in sorted((ROOT/'raw_logs').glob('*-outcome.json')):
        outcome = json.loads(f.read_text())
        label = outcome['label']
        text = (ROOT/'raw_logs'/(label+'.log')).read_text(errors='replace')
        events, reuse = [], []
        for line, s in enumerate(text.splitlines(), 1):
            if s.startswith('STEP21 '):
                r = json.loads(s[7:]);r['line']=line;events.append(r)
            elif s.startswith('REUSE_EVENT '):
                r = json.loads(s[12:]);r['line']=line;reuse.append(r)
                lifecycle.append(dict(label=label, **r))
            if any(x in s for x in ['[ERROR]', 'WARNING: DATA RACE', 'panic:', 'fatal error:', 'timeout', '--- FAIL:', '\nFAIL']):
                errors.append(dict(label=label, line=line, type='log', message=s))
        calls = [r for r in events if r['event']=='sample']
        acquisitions = [r for r in events if r['event']=='acquire']
        assert len(calls) == outcome['observed_calls']
        formal = outcome['batch'] in ['a','b','c']
        rows = []
        for r in calls:
            ns = r['end_ns']-r['begin_ns']
            assert math.isclose(ns/1e9, r['invoke_s'], abs_tol=1e-12)
            g = [e for e in acquisitions if r['begin_ns']<=e['unix_ns']<=r['end_ns']]
            assert len(g)==1,(label,r['index'])
            g=g[0]
            valid = semantic_success(cases[outcome['case']],r,inputs[outcome['case']][r['index']])
            row=dict(case=outcome['case'],label=label,batch=outcome['batch'],policy=outcome['policy'],
                     phase='formal' if formal else 'race_diagnostic' if outcome['race'] else 'smoke',
                     index=r['index'],code=r['code'],business_success=valid,gas=r['gas'],
                     invoke_ns=ns,callmethod_ns=r['callmethod_s']*1e9,
                     getinstance_ns=g['getinstance_ns'],channel_receive_ns=g['channel_receive_ns'],
                     empty_branch=g['empty_branch'],queue_at_return=g['queue_after_receive'],
                     instance_id=g['instance_id'],input_sha256=r['input_sha256'],
                     result_text=base64.b64decode(r.get('result') or '').decode(errors='replace'),
                     error=r.get('message',''),source_file=str((ROOT/'raw_logs'/(label+'.log')).resolve()),source_line=r['line'])
            rows.append(row);samples.append(row)
            if not valid:errors.append(dict(label=label,line=r['line'],type='business_failure',message=r.get('message','unexpected output')))
        validrows=[r for r in rows if r['business_success']]
        cnt=Counter(r['event'] for r in reuse)
        starts=[r for r in reuse if r['event']=='create_begin'];ends=[r for r in reuse if r['event']=='create']
        for a,b in zip(starts,ends):
            creation_rows.append(dict(label=label,case=outcome['case'],policy=outcome['policy'],
                                      instance_id=a['instance_id'],create_ready_ns=b['elapsed_ns'],
                                      completed_before_last_invoke_end=bool(calls) and b['unix_ns']<=calls[-1]['end_ns'],
                                      verification_instance=a==starts[0]))
        summary=dict(case=outcome['case'],label=label,batch=outcome['batch'],policy=outcome['policy'],
                     phase='formal' if formal else 'race_diagnostic' if outcome['race'] else 'smoke',
                     requested=outcome['requested'],actual_calls=len(rows),successes=len(validrows),failures=len(rows)-len(validrows),
                     raw_code_zero=outcome['raw_code_zero'],
                     vm_log_equivalent_tps=len(validrows)/(sum(r['invoke_ns'] for r in validrows)/1e9) if validrows else '',
                     formal_accepted=bool(formal and outcome['execution_safe_observed'] and len(validrows)==100),
                     lifecycle_observed_ok=outcome['execution_safe_observed'],
                     go_test_pass='--- PASS: TestInvoke' in text,
                     go_test_fail='--- FAIL: TestInvoke' in text,
                     gas_distribution=json.dumps(dict(Counter(r['gas'] for r in rows)),sort_keys=True),
                     empty_branch_count=sum(r['empty_branch'] for r in rows),
                     business_instance_count=len({r['instance_id'] for r in rows}),
                     create_started=cnt['create_begin'],create_completed=cnt['create'],
                     close_started=cnt['close_begin'],close_completed=cnt['close_done'],
                     enqueue_started=cnt['enqueue_before'],enqueue_completed=cnt['enqueue_done'],
                     uncompleted_enqueue=cnt['enqueue_before']-cnt['enqueue_done'],
                     reuse_events=cnt['reuse'],discard_events=cnt['drop'],
                     rss_sample_peak_mib=outcome['rss_sample_peak_mib'],threads_sample_peak=outcome['threads_sample_peak'],
                     cpu_cgroup_ns=outcome['systemd'].get('CPUUsageNSec',''),
                     systemd_status_reliability='unit may have been collected: use Go log and lifecycle flags' if outcome['systemd'].get('ActiveState')=='inactive' else 'captured before stop',
                     worker_closed=outcome['lifecycle_closed'])
        for key,field in [('invoke_ns','invoke'),('callmethod_ns','callmethod'),('getinstance_ns','getinstance'),('channel_receive_ns','channel_receive')]:
            summary.update(ms_stats([r[key] for r in rows],field))
        summary.update(ms_stats([r['elapsed_ns'] for r in ends],'create_ready'))
        resources=[json.loads(s) for s in (ROOT/'raw_logs'/(label+'-resources.jsonl')).read_text().splitlines()]
        if resources:
            summary.update(rss_first_mib=resources[0].get('VmRSS',0)/1024,rss_last_mib=resources[-1].get('VmRSS',0)/1024,
                           threads_first=resources[0].get('Threads',''),threads_last=resources[-1].get('Threads',''),
                           vm_size_peak_mib=max(r.get('VmSize',0) for r in resources)/1024)
        summaries.append(summary)
        if outcome['batch'] in ['a','b','c']:
            assert cnt['reuse']==(len(rows) if outcome['policy']=='R0' else 0)
            assert cnt['drop']==(len(rows) if outcome['policy']=='R1' else 0)
            if outcome['policy']=='R1':assert len({r['instance_id'] for r in rows})==len(rows)
    paired=defaultdict(dict)
    for r in samples:paired[r['case'],r['batch'],r['index']][r['policy']]=r
    for (case,batch,i),g in paired.items():
        if set(g)!={'R0','R1'}:continue
        a,b=g['R0'],g['R1']
        checks.append(dict(case=case,batch=batch,index=i,input_hash_equal=a['input_sha256']==b['input_sha256'],
                           result_equal=a['result_text']==b['result_text'],gas_equal=a['gas']==b['gas'],
                           r0_gas=a['gas'],r1_gas=b['gas'],both_business_success=a['business_success'] and b['business_success']))
    assert all(r['input_hash_equal'] for r in checks),'R0/R1 post-call parameter hashes differ'
    comparison=[];effects=[]
    for name,case in cases.items():
        group=[r for r in summaries if r['case']==name and r['phase']=='formal']
        batches=[]
        for batch in ['a','b','c']:
            a=next((r for r in group if r['batch']==batch and r['policy']=='R0'),None)
            b=next((r for r in group if r['batch']==batch and r['policy']=='R1'),None)
            if a and b:
                ratio=a['vm_log_equivalent_tps']/b['vm_log_equivalent_tps'] if b['vm_log_equivalent_tps'] else ''
                accepted=a['formal_accepted'] and b['formal_accepted']
                batches.append((batch,ratio,accepted))
                ar=[r for r in samples if r['label']==a['label']];br=[r for r in samples if r['label']==b['label']]
                dt=sum(r['invoke_ns'] for r in br)-sum(r['invoke_ns'] for r in ar)
                dw=sum(r['channel_receive_ns'] for r in br)-sum(r['channel_receive_ns'] for r in ar)
                effects.append(dict(case=name,batch=batch,accepted=accepted,ratio=ratio,
                                    invoke_sum_increase_ms=dt/1e6,channel_sum_increase_ms=dw/1e6,
                                    channel_fraction_of_increase=dw/dt if dt else '',
                                    status='formal' if accepted else 'diagnostic_only_failed_shutdown'))
        ok=sum(x[2] for x in batches)==3
        totals={}
        for p in ['R0','R1']:
            r=[r for r in samples if r['case']==name and r['phase']=='formal' and r['policy']==p and r['business_success']]
            totals[p]=len(r)/(sum(x['invoke_ns'] for x in r)/1e9) if r else None
        ratio=totals['R0']/totals['R1'] if totals['R0'] and totals['R1'] else None
        classification='E'
        if ok:
            if .95<=ratio<=1.05:classification='C'
            elif ratio<.95:classification='D' if all(x[1]<1 for x in batches) else 'C'
            else:classification='A' if ratio>=case['historical_ratio'] else 'B'
        pre=[r for r in summaries if r['case']==name and r['phase']=='smoke']
        comparison.append(dict(method=case['contract']+'.'+case['method'],historical_r0_tps=case['historical_r0'],historical_r1_tps=case['historical_r1'],historical_ratio=case['historical_ratio'],
                               classification=classification,valid_independent_batch_pairs=sum(x[2] for x in batches),
                               r0_tps=totals['R0'] if ok else '',r1_tps=totals['R1'] if ok else '',ratio=ratio if ok else '',
                               loss_pct=(1-1/ratio)*100 if ok else '',
                               diagnostic_r0_tps=totals['R0'] if not ok else '',diagnostic_r1_tps=totals['R1'] if not ok else '',
                               diagnostic_ratio=ratio if not ok else '',
                               diagnostic_loss_pct=(1-1/ratio)*100 if ratio and not ok else '',
                               r0_smoke_success=next((str(r['successes'])+'/'+str(r['actual_calls']) for r in pre if r['policy']=='R0'),''),
                               r1_smoke_success=next((str(r['successes'])+'/'+str(r['actual_calls']) for r in pre if r['policy']=='R1'),''),
                               reason=('R1 post-window maintenance drain timed out after 100 successful calls; no 3 valid pairs' if group else 'formal not started: suite stopped at first R1 drain failure') if name!='exchange-buyNow' else 'addWriteList failure in original mock environment; no successful cross-contract path',
                               wasm_sha256=case['wasm_sha256']))
    planned=[]
    for name in cases:
        for batch in ['a','b','c']:
            for policy in ['R0','R1']:
                r=next((r for r in summaries if r['case']==name and r['batch']==batch and r['policy']==policy),None)
                state='completed' if r and r['formal_accepted'] else 'completed_calls_failed_shutdown' if r else 'not_run'
                reason='exchange business preflight failed' if name=='exchange-buyNow' else 'global suite stop after first R1 shutdown failure'
                planned.append(dict(case=name,batch=batch,policy=policy,planned_calls=100,actual_calls=r['actual_calls'] if r else 0,
                                    state=state,accepted=bool(r and r['formal_accepted']),reason='' if r and r['formal_accepted'] else reason))
                if not r:
                    summaries.append(dict(case=name,label=f'{name}-{batch}-{policy.lower()}',batch=batch,policy=policy,
                                          phase='formal',requested=100,actual_calls=0,successes=0,failures=0,
                                          vm_log_equivalent_tps='',formal_accepted=False,lifecycle_observed_ok='',
                                          state='not_run',not_run_reason=reason))
    write('per_run_summary.csv',summaries)
    write('baseline_comparison.csv',comparison)
    write('samples.csv',samples)
    write('correctness.csv',checks)
    write('creation_samples.csv',creation_rows)
    write('lifecycle_events.csv',lifecycle)
    write('diagnostic_effects.csv',effects)
    write('errors.csv',errors or [dict(type='none')])
    write('planned_matrix.csv',planned)
    print('observed runs',len(summaries)-sum(r.get('state')=='not_run' for r in summaries),'calls',len(samples),'business failures',sum(not r['business_success'] for r in samples))
    print(json.dumps(comparison,indent=2))


if __name__=='__main__':main()
