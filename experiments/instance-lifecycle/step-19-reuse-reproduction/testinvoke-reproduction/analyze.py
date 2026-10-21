"""Analyze unchanged TestInvoke logs; never launches a runtime."""
from pathlib import Path
from collections import Counter
import csv
import json
import math
import re
import statistics

ROOT = Path(__file__).resolve().parent
TIMING = re.compile(r'invoke vm, tx id:([^,]+), contractName:([^,]*), contractMethod:([^,]+), runtimeContractResult:(\d+)\s*,startTime:(\d+), endTime:(\d+), executionTime:([\d.]+) s, callMethodTime:([\d.]+) s')


def write(name, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (ROOT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def analyze_log(label, race=False):
    txt = (ROOT/(label+'.log')).read_text()
    policy = 'R0' if 'r0' in label else 'R1'
    events = [json.loads(s[12:]) for s in txt.splitlines() if s.startswith('REUSE_EVENT ')]
    counts = Counter(x['event'] for x in events)
    times = []
    results = []
    errors = []
    for line, s in enumerate(txt.splitlines(), 1):
        m = TIMING.search(s)
        if m:
            times.append(dict(tx_id=m[1], name=m[2], method=m[3], code=int(m[4]), begin=int(m[5]), end=int(m[6]), source_line=line))
        m = re.search(r'testid = (\d+) contractResult = (.*)', s)
        if m:
            body = m[2]
            gas = re.search(r'gas_used:(\d+)', body)
            code = re.search(r'(?:^|\s)code:(\d+)', body)
            result = re.search(r'result:"([^"]*)"', body)
            results.append(dict(index=int(m[1]), code=int(code[1]) if code else 0,
                                gas=int(gas[1]) if gas else 0, result=result[1] if result else ''))
        if re.search(r'\[ERROR\]|panic:|fatal error:|WARNING: DATA RACE', s):
            errors.append(dict(label=label, line=line, text=s))
    assert len(times) == len(results) == 100
    assert [r['index'] for r in results] == list(range(100))
    sm = re.search(r'successCnt=(\d+) compileTime=([\d.eE+-]+) totalCallMethodTime=([\d.eE+-]+) TPS\(callMethod only\)=([\d.eE+-]+)', txt)
    assert sm
    records = []
    for t, r in zip(times, results):
        assert t['code'] == r['code'] == 0
        assert r['result'] == 'success bigNumCal: 607723520'
        acquisitions = [e for e in events if e['event'] == 'acquire' and not e['instance_id'] and t['begin'] <= e['unix_ns'] <= t['end']]
        assert len(acquisitions) == 1
        records.append(dict(label=label, batch=label.split('-')[0], policy=policy, race=race,
                            index=r['index'], tx_id=t['tx_id'], begin_ns=t['begin'], end_ns=t['end'],
                            invoke_ns=t['end']-t['begin'], code=r['code'], gas=r['gas'], result=r['result'],
                            contract_id_name=t['name'],
                            acquire_function_ns=acquisitions[0]['elapsed_ns'],
                            empty_pool_path=any(e['event'] == 'acquire_wait' and t['begin'] <= e['unix_ns'] <= t['end'] for e in events),
                            source_file=label+'.log', source_line=t['source_line']))
    duration = sum(r['invoke_ns'] for r in records)/1e9
    assert math.isclose(duration, float(sm[3]), abs_tol=1e-12)
    assert int(sm[1]) == 100 and math.isclose(100/duration, float(sm[4]), rel_tol=1e-12)
    resource = ROOT/(label+'-result.json')
    resource = json.loads(resource.read_text()) if resource.exists() else json.loads((ROOT/'preflight-result.json').read_text())
    ds = sorted(r['invoke_ns']/1e6 for r in records)
    summary = dict(label=label, batch=label.split('-')[0], policy=policy, race=race, calls=100, successes=int(sm[1]),
                   sum_invoke_s=duration, mean_invoke_ms=duration*10, median_invoke_ms=statistics.median(ds),
                   p95_invoke_ms=ds[94], tps=100/duration, original_printed_tps=float(sm[4]), compile_s=float(sm[2]),
                   creates_started=counts['create_begin'], creates_completed=counts['create'],
                   closes_started=counts['close_begin'], closes_completed=counts['close_done'],
                   enqueued=counts['enqueue_done'], reuse_events=counts['reuse'], discard_events=counts['drop'],
                   empty_pool_calls=counts['acquire_wait'], sum_acquire_function_ms=sum(r['acquire_function_ns'] for r in records)/1e6,
                   gas_distribution=json.dumps(dict(Counter(r['gas'] for r in records)), sort_keys=True),
                   error_lines=len(errors), peak_rss_mib=resource.get('peak_rss_mib', resource.get('resources_peak_rss_mib')),
                   peak_threads=resource.get('peak_threads', resource.get('threads_peak')),
                   reclamation_scope='log events until process exit; close() has no join; not long-run boundedness proof')
    return records, summary, errors


def main():
    samples, summaries, errors, diagnostic = [], [], [], []
    for label in ['a-r0', 'a-r1', 'b-r1', 'b-r0', 'c-r0', 'c-r1']:
        r, s, e = analyze_log(label)
        samples.extend(r)
        summaries.append(s)
        errors.extend(e)
    for label in ['preflight-r0-race', 'preflight-r1-race']:
        _, s, e = analyze_log(label, True)
        diagnostic.append(s)
        errors.extend(e)
    comparisons = []
    for batch in ['a', 'b', 'c']:
        a, b = [next(r for r in summaries if r['batch'] == batch and r['policy'] == p) for p in ['R0', 'R1']]
        comparisons.append(dict(batch=batch, calls_per_group=100, r0_tps=a['tps'], r1_tps=b['tps'],
                                r0_mean_ms=a['mean_invoke_ms'], r1_mean_ms=b['mean_invoke_ms'],
                                ratio=a['tps']/b['tps'], r1_tps_drop_pct=100*(1-b['tps']/a['tps']),
                                r0_empty_pool=a['empty_pool_calls'], r1_empty_pool=b['empty_pool_calls']))
    write('samples.csv', samples)
    write('summary.csv', summaries)
    write('batch_comparison.csv', comparisons)
    write('diagnostic_summary.csv', diagnostic)
    write('errors.csv', errors or [dict(label='all', line='', text='no matching error/race/panic lines')])
    node = Path(__file__).resolve().parent.parent/'vm-log-metric-audit/vm_log_summary.csv'
    if not node.exists():
        node = ROOT/'previous_node_vm_log_summary.csv'
    node = list(csv.DictReader(node.open()))
    node = [r for r in node if r['contract'] == 'compute' and r['method'] == 'bigNumCal']
    juxtaposition = []
    for r in node:
        juxtaposition.append(dict(environment='previous single-node paced SDK', group='single', policy=r['policy'], n=r['n'],
                                  mean_ms=r['mean_ms'], tps=r['duration_sum_vm_log_tps'],
                                  metric='factory outer Invoke window', pacing='100ms sleep after response', snapshot='real ledger'))
    for r in summaries:
        juxtaposition.append(dict(environment='original TestInvoke', group=r['batch'], policy=r['policy'], n=r['calls'],
                                  mean_ms=r['mean_invoke_ms'], tps=r['tps'], metric='inner InvokeTime executionTime',
                                  pacing='none; no warmup exclusion', snapshot='SnapshotMock; no node/commit'))
    write('node_comparison.csv', juxtaposition)
    print(json.dumps(comparisons, indent=2))
    print('Formal samples:', len(samples), 'errors:', len(errors))
    print('Gas:', {p: dict(Counter(r['gas'] for r in samples if r['policy'] == p)) for p in ['R0', 'R1']})


if __name__ == '__main__':
    main()
