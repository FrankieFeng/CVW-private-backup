"""Join same-host CLOCK_MONOTONIC traces; no benchmarks are run here."""
from pathlib import Path
from collections import defaultdict
import base64, csv, hashlib, json, math, random, statistics

ROOT = Path(__file__).resolve().parent

def write(name, rows):
    with (ROOT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def stats(a):
    n = len(a)
    rng = random.Random(191903)
    chunks = [(a + a)[i:i+5] for i in range(n)]
    boot = []
    for _ in range(4000):
        draw = [x for c in rng.choices(chunks, k=math.ceil(n/5)) for x in c][:n]
        boot.append(statistics.median(draw))
    boot.sort()
    return dict(n=n, median_ns=statistics.median(a), p95_ns=sorted(a)[math.ceil(.95*n)-1],
                mean_ns=statistics.mean(a), ci95_low_ns=boot[int(.025*3999)],
                ci95_high_ns=boot[int(.975*3999)], block_pairs=5, bootstrap_reps=4000)

def main():
    requests = [json.loads(line) for line in (ROOT / 'requests.jsonl').read_text().splitlines()]
    events, vms, all_events = defaultdict(lambda: defaultdict(list)), defaultdict(list), []
    for batch in ['a', 'b']:
        for endpoint in ['baseline', 'optimized']:
            for line in (ROOT / 'network' / endpoint / f'stdout-{batch}.log').read_text().splitlines():
                if line.startswith('STEP19 '):
                    row = json.loads(line[7:])
                    row.update(batch=batch, endpoint=endpoint)
                    events[row['tx_id']][row['stage']].append(row['mono_ns'])
                    all_events.append(row)
                elif line.startswith('STEP17 '):
                    row = json.loads(line[7:])
                    if row['kind'] == 'invoke':
                        vms[row['tx_id']].append(row)
    samples, checks = [], []
    partition = ['client_pre_rpc_ns', 'rpc_validation_registration_ns', 'addtx_ns',
                 'after_addtx_to_vm_ns', 'vm_entry_to_lock_ns', 'vm_span_ns',
                 'vm_end_to_putblock_ns', 'putblock_to_rpc_return_ns', 'rpc_to_client_ns']
    for row in requests:
        response = row.get('response') or {}
        tx = response.get('tx_id')
        assert tx, row
        trace = events[tx]
        assert len(vms[tx]) == 1, (tx, 'multiple/missing VM attempts')
        vm = vms[tx][0]
        t = {}
        for stage in ['rpc_enter', 'addtx_begin', 'addtx_end', 'vm_enter', 'vm_lock_acquired',
                      'vm_end', 'putblock_returned', 'commit_common_return',
                      'committed_event_received', 'sync_result_received', 'rpc_return']:
            assert len(trace[stage]) == 1, (tx, stage, trace[stage])
            t[stage] = trace[stage][0]
        sample = dict(batch=row['batch'], phase=row['phase'], pair=row['pair'], mode=row['mode'],
                      endpoint=row['endpoint'], tx_id=tx, instance_id=vm['instance_id'], vm_attempts=1,
                      client_elapsed_ns=row['elapsed_ns'],
                      client_mono_ns=row['client_end_mono_ns']-row['client_begin_mono_ns'],
                      invoke_ns=vm['invoke_ns'], s1_ns=vm['s1_ns'], s2_ns=vm['s2_ns'],
                      copy_ns=vm['copy_ns'], gas=vm['gas'], result_sha=vm['result_sha'])
        points = [row['client_begin_mono_ns'], t['rpc_enter'], t['addtx_begin'], t['addtx_end'],
                  t['vm_enter'], t['vm_lock_acquired'], t['vm_end'], t['putblock_returned'],
                  t['rpc_return'], row['client_end_mono_ns']]
        for key, a, b in zip(partition, points, points[1:]):
            sample[key] = b - a
            assert b >= a, (tx, key, b-a)
        assert sum(sample[key] for key in partition) == sample['client_mono_ns']
        sample['rpc_to_vm_ns'] = t['vm_enter'] - t['rpc_enter']
        sample['post_vm_to_client_ns'] = row['client_end_mono_ns']-t['vm_end']
        assert t['putblock_returned'] <= t['commit_common_return'] <= t['committed_event_received'] <= t['sync_result_received'] <= t['rpc_return']
        cr = response.get('contract_result') or {}
        assert not row.get('error') and response.get('code', 0) == cr.get('code', 0) == vm['code'] == 0
        result = base64.b64decode(cr['result'])
        assert result == b'success bigNumCal: 607723520'
        assert hashlib.sha256(result).hexdigest() == vm['result_sha']
        assert cr['gas_used'] == vm['gas'] == 106028
        assert vm['optimized'] == (row['mode'] == 'optimized')
        samples.append(sample)
    assert len({s['instance_id'] for s in samples}) == len(samples)
    write('trace_events.csv', all_events)
    write('samples.csv', samples)
    summary, effects, accounting = [], [], []
    metrics = ['client_elapsed_ns', 'client_mono_ns', 'invoke_ns', 's1_ns', 'rpc_to_vm_ns',
               'post_vm_to_client_ns'] + partition
    for batch in ['a', 'b']:
        g = [s for s in samples if s['batch'] == batch and s['phase'] == 'warm']
        b = {s['pair']:s for s in g if s['mode'] == 'baseline'}
        o = {s['pair']:s for s in g if s['mode'] == 'optimized'}
        assert set(b) == set(o) == set(range(30))
        for i in sorted(b):
            assert b[i]['gas'] == o[i]['gas'] and b[i]['result_sha'] == o[i]['result_sha']
            checks.append(dict(batch=batch, pair=i, result_gas_equal=True, fresh_ids_distinct=True,
                               exactly_one_vm_attempt=True, trace_complete=True, accounting_exact=True))
        for metric in metrics:
            for mode in ['baseline', 'optimized']:
                values = [s[metric] for s in sorted(g, key=lambda s:s['pair']) if s['mode'] == mode]
                summary.append(dict(batch=batch, mode=mode, metric=metric, **stats(values)))
            # Positive means time saved by Copy, consistent throughout this experiment.
            delta = [b[i][metric]-o[i][metric] for i in sorted(b)]
            effects.append(dict(batch=batch, metric=metric, sign='baseline_minus_optimized', **stats(delta)))
        total_mean = statistics.mean(b[i]['client_mono_ns']-o[i]['client_mono_ns'] for i in b)
        for metric in partition:
            value = statistics.mean(b[i][metric]-o[i][metric] for i in b)
            accounting.append(dict(batch=batch, metric=metric, mean_saved_ns=value,
                                   total_client_mean_saved_ns=total_mean))
        assert abs(sum(r['mean_saved_ns'] for r in accounting if r['batch']==batch)-total_mean)<1e-6
    write('summary.csv', summary)
    write('paired_effects.csv', effects)
    write('mean_accounting.csv', accounting)
    write('correctness.csv', checks)
    for row in effects:
        if row['metric'] in ['client_elapsed_ns', 'invoke_ns', 'rpc_to_vm_ns', 'post_vm_to_client_ns']:
            print(row['batch'], row['metric'], 'saved median/CI ms',
                  *[round(row[k]/1e6, 6) for k in ['median_ns', 'ci95_low_ns', 'ci95_high_ns']])

if __name__ == '__main__':
    main()
