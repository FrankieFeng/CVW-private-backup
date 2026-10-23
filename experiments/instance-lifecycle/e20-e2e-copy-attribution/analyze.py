"""Read-only reductions of saved E20 and historical logs; no runtime execution."""
from pathlib import Path
from collections import Counter, defaultdict
import base64
import csv
import json
import math
import os
import statistics

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent


def write(name, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (ROOT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def stats(values):
    return dict(n=len(values), mean_ms=statistics.mean(values)/1e6,
                p50_ms=statistics.median(values)/1e6,
                p95_ms=sorted(values)[math.ceil(.95*len(values))-1]/1e6)


def observations(path):
    vms, pools, traces = [], [], []
    for number, line in enumerate(path.read_text(errors='replace').splitlines(), 1):
        if line.startswith('STEP17 '):
            r = json.loads(line[7:])
            r.update(source_file=str(path), source_line=number)
            (vms if r['kind'] == 'invoke' else pools).append(r)
        elif line.startswith('STEP19 '):
            r = json.loads(line[7:])
            r.update(source_file=str(path), source_line=number)
            traces.append(r)
    return vms, pools, traces


def historical():
    old = BASE/'step-17-real-node'
    index = defaultdict(list)
    for mode in ['baseline', 'optimized']:
        v, _, _ = observations(old/'network'/mode/'stdout.log')
        for r in v:
            index[mode, r['tx_id'], r['contract']].append(r)
    joins = []
    for r in csv.DictReader((old/'samples.csv').open()):
        if r['phase'] != 'warm':
            continue
        vm = index[r['mode'], r['tx_id'], r['contract']]
        assert len(vm) == int(r['vm_attempts']) > 0
        joins.append(dict(batch=r['batch'], workers=r['workers'], contract=r['contract'], mode=r['mode'],
                          tx_id=r['tx_id'], attempts=len(vm), sum_root_invoke_ns=sum(x['invoke_ns'] for x in vm),
                          last_root_invoke_ns=vm[-1]['invoke_ns'], client_ns=r['client_ns']))
    write('historical_tx_join.csv', joins)
    c = Counter((r['batch'], r['workers'], r['contract'], r['attempts']) for r in joins)
    write('historical_attempt_counts.csv', [dict(batch=b, workers=w, contract=k, root_attempts_per_tx=a, tx_count=n)
                                          for (b, w, k, a), n in sorted(c.items())])


def new_replay():
    samples, all_vm, pools, correctness, orphan, resources = [], [], [], [], [], []
    failures = []
    for request_file in sorted(ROOT.glob('low-*-requests.jsonl')):
        label = request_file.name.removesuffix('-requests.jsonl')
        requests = [json.loads(x) for x in request_file.read_text().splitlines()]
        vm_index = defaultdict(list)
        for endpoint in ['baseline', 'optimized']:
            v, p, _ = observations(ROOT/'network'/endpoint/(label+'.log'))
            for r in v:
                r.update(label=label, endpoint=endpoint)
                all_vm.append(r)
                vm_index[endpoint, r['tx_id']].append(r)
            for r in p:
                r.update(label=label, endpoint=endpoint)
                pools.append(r)
                assert r['fresh'] is True
                assert r['source_sha'] == 'e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507'
        seen = set()
        for r in requests:
            resp = r.get('response') or {}
            cr = resp.get('contract_result') or {}
            tx = resp.get('tx_id')
            vm = vm_index[r['endpoint'], tx]
            assert vm, (label, tx)
            assert all(x['method'] == 'bigNumCal' and x['contract'] == 'compute' for x in vm)
            seen.add((r['endpoint'], tx))
            ok = not r.get('error') and resp.get('code', 0) == cr.get('code', 0) == 0
            ok = ok and base64.b64decode(cr.get('result', '')) == b'success bigNumCal: 607723520'
            ok = ok and cr.get('gas_used') == 106028 and resp.get('tx_block_height', 0) > 0
            assert ok, r
            assert all(x['optimized'] == (r['mode'] == 'optimized') and x['code'] == 0 and x['gas'] == cr['gas_used'] for x in vm)
            last = vm[-1]
            row = dict(label=label, phase=r['phase'], pair=r['pair'], mode=r['mode'], endpoint=r['endpoint'], tx_id=tx,
                       client_ns=r['elapsed_ns'], vm_attempts=len(vm), total_root_invoke_ns=sum(x['invoke_ns'] for x in vm),
                       last_root_invoke_ns=last['invoke_ns'], s1_ns=last['s1_ns'], s2_ns=last['s2_ns'], s3_ns=last['s3_ns'],
                       copy_ns=last['copy_ns'], wasi_and_start_ns=last['s2_ns']-last['s1_ns'],
                       gas=cr['gas_used'], code=cr.get('code', 0), block_height=resp['tx_block_height'],
                       instance_id=last['instance_id'], result=cr['result'],
                       driver_send_mono_ns=r['driver_send_mono_ns'], driver_receive_mono_ns=r['driver_receive_mono_ns'],
                       run_status='smoke_complete' if label == 'low-smoke' else 'resource_censored_incomplete_batch')
            # A descriptive remainder, not a measurement of any one stage.
            row['client_minus_root_vm_ns'] = row['client_ns']-row['total_root_invoke_ns']
            samples.append(row)
        for key, vm in vm_index.items():
            if key not in seen:
                for r in vm:
                    orphan.append(dict(label=label, endpoint=key[0], tx_id=key[1], invoke_ns=r['invoke_ns'],
                                       client_response='not_recorded_before_resource_stop',
                                       business_code=r['code'], committed_status='unknown'))
        rr = [json.loads(x) for x in (ROOT/(label+'-resources.jsonl')).read_text().splitlines()]
        for mode in ['baseline', 'optimized']:
            a = [r for r in rr if r['endpoint'] == mode]
            warm = [r for r in a if r['phase'] == 'warm']
            first, last = (warm[0], warm[-1]) if warm else (a[0], a[-1])
            resources.append(dict(label=label, endpoint=mode, rss_peak_mib=max(x['VmRSS'] for x in a)/1024,
                                  rss_first_warm_mib=first['VmRSS']/1024, rss_last_mib=last['VmRSS']/1024,
                                  vmsize_peak_mib=max(x['VmSize'] for x in a)/1024,
                                  threads_peak=max(x['Threads'] for x in a),
                                  sampled_window_s=(last['mono_ns']-first['mono_ns'])/1e9,
                                  cpu_ticks_delta=last['cpu_ticks']-first['cpu_ticks'],
                                  clock_ticks_per_s=os.sysconf('SC_CLK_TCK'),
                                  cpu_logical_core_percent=(last['cpu_ticks']-first['cpu_ticks'])/os.sysconf('SC_CLK_TCK')/((last['mono_ns']-first['mono_ns'])/1e9)*100,
                                  cpu_scope='sampled warm span; process CPU includes execution/commit/background, not per-VM attribution'))
    assert len(set((r['label'], r['endpoint'], r['instance_id']) for r in all_vm)) == len(all_vm)
    summaries = []
    paired = defaultdict(dict)
    for r in samples:
        if r['phase'] == 'warm':
            paired[r['label'], r['pair']][r['mode']] = r
    for label in sorted({r['label'] for r in samples}):
        for mode in ['baseline', 'optimized']:
            a = [r for r in samples if r['label'] == label and r['mode'] == mode and r['phase'] == 'warm']
            for metric in ['client_ns', 'total_root_invoke_ns', 'last_root_invoke_ns', 's1_ns', 's2_ns', 's3_ns', 'copy_ns', 'client_minus_root_vm_ns']:
                summaries.append(dict(label=label, mode=mode, metric=metric, **stats([r[metric] for r in a]),
                                      validity='descriptive_only; resource-censored' if label != 'low-smoke' else 'small_smoke'))
    effects, accounting, rates, matched_summary = [], [], [], []
    for label in sorted({r['label'] for r in samples}):
        complete = [(pair, g['baseline'], g['optimized']) for (l, pair), g in sorted(paired.items())
                    if l == label and set(g) == {'baseline', 'optimized'}]
        for pair, b, o in complete:
            correctness.append(dict(label=label, pair=pair, result_equal=b['result'] == o['result'], gas_equal=b['gas'] == o['gas'],
                                    baseline_attempts=b['vm_attempts'], copy_attempts=o['vm_attempts'],
                                    unique_fresh_ids=True, committed_response=True, table='not_retested', production_safe=False))
        for mode, offset in [('baseline', 1), ('optimized', 2)]:
            for metric in ['client_ns', 'total_root_invoke_ns', 's1_ns', 'copy_ns']:
                matched_summary.append(dict(label=label, mode=mode, metric=metric,
                                            **stats([g[offset][metric] for g in complete]),
                                            selection='complete pairs only; unmatched responses retained in samples.csv'))
        for metric in ['client_ns', 'total_root_invoke_ns', 's1_ns', 'client_minus_root_vm_ns']:
            values = [b[metric]-o[metric] for _, b, o in complete]
            effects.append(dict(label=label, metric=metric, sign='baseline_minus_copy', **stats(values),
                                uncertainty='no CI; small smoke or resource-censored partial batch'))
            accounting.append(dict(label=label, metric=metric, matched_pairs=len(complete), mean_saved_ns=statistics.mean(values)))
        a = next(r['mean_saved_ns'] for r in accounting if r['label'] == label and r['metric'] == 'client_ns')
        b = sum(r['mean_saved_ns'] for r in accounting if r['label'] == label and r['metric'] in ['total_root_invoke_ns', 'client_minus_root_vm_ns'])
        assert abs(a-b) < 1e-6
        for mode in ['baseline', 'optimized']:
            a = [r for r in samples if r['label'] == label and r['mode'] == mode and r['phase'] == 'warm']
            span = (max(r['driver_receive_mono_ns'] for r in a)-min(r['driver_send_mono_ns'] for r in a))/1e9
            rates.append(dict(label=label, mode=mode, completed_responses=len(a), driver_observed_window_s=span,
                              client_completed_per_s=len(a)/span,
                              vm_log_equivalent_tps=sum(r['vm_attempts'] for r in a)/(sum(r['total_root_invoke_ns'] for r in a)/1e9),
                              committed_response_count=len({r['tx_id'] for r in a}),
                              unique_ledger_window_tps='',
                              committed_tps_status='not_measured: no independent ledger-window scan; response heights only',
                              scope='two isolated endpoints interleaved; not saturation throughput'))
    write('samples.csv', samples)
    write('vm_invocations.csv', all_vm)
    write('cache_events.csv', pools)
    write('summary.csv', summaries)
    write('paired_effects.csv', effects)
    write('matched_summary.csv', matched_summary)
    write('mean_accounting.csv', accounting)
    write('correctness.csv', correctness)
    write('resource_summary.csv', resources)
    write('rate_definitions.csv', rates)
    write('orphan_vm_invocations.csv', orphan or [dict(status='none')])
    print('New saved responses:', len(samples), 'matched hot pairs:', len(correctness), 'unjoined VM events:', len(orphan))
    print('New effects:', effects)


def historical_node_stages():
    old = BASE/'step-19-client-latency-trace'
    requests = [json.loads(x) for x in (old/'requests.jsonl').read_text().splitlines()]
    events = defaultdict(lambda: defaultdict(list))
    for batch in ['a', 'b']:
        for endpoint in ['baseline', 'optimized']:
            _, _, traces = observations(old/'network'/endpoint/f'stdout-{batch}.log')
            for e in traces:
                events[e['tx_id']][e['stage']].append(e['mono_ns'])
    result = []
    partitions = [('rpc_before_addtx_ns', 'rpc_enter', 'addtx_begin'), ('addtx_ns', 'addtx_begin', 'addtx_end'),
                  ('queue_to_vm_ns', 'addtx_end', 'vm_enter'), ('entry_to_lock_ns', 'vm_enter', 'vm_lock_acquired'),
                  ('vm_span_ns', 'vm_lock_acquired', 'vm_end'), ('vm_to_putblock_ns', 'vm_end', 'putblock_returned'),
                  ('putblock_to_rpc_return_ns', 'putblock_returned', 'rpc_return')]
    for r in requests:
        tx = r['response']['tx_id']
        e = events[tx]
        assert all(len(e[s]) == 1 for _, a, b in partitions for s in [a, b])
        row = dict(batch=r['batch'], phase=r['phase'], pair=r['pair'], mode=r['mode'], tx_id=tx, client_elapsed_ns=r['elapsed_ns'])
        for key, a, b in partitions:
            row[key] = e[b][0]-e[a][0]  # same node process CLOCK_MONOTONIC
            assert row[key] >= 0
        row['node_rpc_ns'] = e['rpc_return'][0]-e['rpc_enter'][0]
        row['outside_node_rpc_residual_ns'] = r['elapsed_ns']-row['node_rpc_ns']  # durations, never timestamps
        assert row['outside_node_rpc_residual_ns'] >= 0
        assert sum(row[k] for k, _, _ in partitions) == row['node_rpc_ns']
        result.append(row)
    write('historical_same_process_stages.csv', result)
    accounting = []
    for batch in ['a', 'b']:
        a = {(r['pair'], r['mode']): r for r in result if r['batch'] == batch and r['phase'] == 'warm'}
        for key in ['client_elapsed_ns', 'outside_node_rpc_residual_ns']+[k for k, _, _ in partitions]:
            diffs = [a[i, 'baseline'][key]-a[i, 'optimized'][key] for i in range(30)]
            accounting.append(dict(batch=batch, metric=key, pairs=30, sign='baseline_minus_copy', mean_saved_ns=statistics.mean(diffs)))
        total = next(r['mean_saved_ns'] for r in accounting if r['batch'] == batch and r['metric'] == 'client_elapsed_ns')
        stage_total = sum(r['mean_saved_ns'] for r in accounting if r['batch'] == batch and r['metric'] != 'client_elapsed_ns')
        assert abs(total-stage_total) < 1e-6
    write('historical_stage_accounting.csv', accounting)
    print('Historical diagnostic stages rechecked:', len(result), 'transactions; no cross-process timestamp subtraction')


if __name__ == '__main__':
    historical()
    new_replay()
    historical_node_stages()
