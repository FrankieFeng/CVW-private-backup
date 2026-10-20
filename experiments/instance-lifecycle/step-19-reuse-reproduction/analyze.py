"""Read-only reduction of saved smoke output; no node/benchmark execution."""
from pathlib import Path
import base64, collections, csv, json, math, os, re, statistics

ROOT = Path(__file__).resolve().parent


def write(name, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with (ROOT / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def quantile(values, q):
    return sorted(values)[math.ceil(len(values) * q) - 1]


def main():
    samples, correctness, summaries, resource_summaries, event_summaries = [], [], [], [], []
    for batch, folder in [('three-contract-smoke', ROOT), ('fact-target-smoke', ROOT / 'fact-target-smoke')]:
        requests = [json.loads(line) for line in (folder / 'requests.jsonl').read_text().splitlines()]
        committed = {(row['policy'], row['transaction']['transaction']['payload']['tx_id']): row['transaction']
                     for row in requests if row['op'] == 'rwset'}
        vms, events = collections.defaultdict(list), []
        for endpoint, policy in [('baseline', 'R0'), ('optimized', 'R1')]:
            for line in (folder / 'network' / endpoint / 'stdout.log').read_text(errors='replace').splitlines():
                if line.startswith('REUSE_VM '):
                    vm = dict(re.findall(r'(\w+)=([^ ]+)', line))
                    vms[policy, vm['tx']].append(vm)
                if line.startswith('REUSE_EVENT '):
                    event = json.loads(line[len('REUSE_EVENT '):])
                    event.update(policy=policy, batch=batch)
                    events.append(event)
        groups = collections.defaultdict(list)
        paired = collections.defaultdict(dict)
        for row in requests:
            if row['phase'] != 'sample':
                continue
            tx_id = row['response']['tx_id']
            attempts = vms[row['policy'], tx_id]
            assert len(attempts) == 1, (batch, row['policy'], tx_id, attempts)
            vm = attempts[0]
            info = committed[row['policy'], tx_id]
            tx_result = info['transaction'].get('result') or {}
            assert tx_result.get('code', 0) == 0
            result = row['response'].get('contract_result') or {}
            sample = dict(batch=batch, policy=row['policy'], contract=row['contract'], method=row['method'],
                          index=row['index'], tx_id=tx_id, vm_invoke_ns=int(vm['end_ns']) - int(vm['begin_ns']),
                          client_ns=row['elapsed_ns'], block_height=info['block_height'],
                          block_timestamp=info.get('block_timestamp'), gas_reported=result.get('gas_used', 0),
                          native_meter_gas='not_collected', committed_success=True,
                          root_attempts=len(attempts), window_begin_ns=row['window_begin_ns'],
                          window_end_ns=row['window_end_ns'])
            samples.append(sample)
            groups[row['policy'], row['contract'], row['method']].append(sample)
            paired[row['contract'], row['method'], row['index']][row['policy']] = (row, info)
        for (policy, contract, method), rows in groups.items():
            window = max(row['window_end_ns'] for row in rows) - min(row['window_begin_ns'] for row in rows)
            v = [row['vm_invoke_ns'] / 1e6 for row in rows]
            c = [row['client_ns'] / 1e6 for row in rows]
            summaries.append(dict(batch=batch, policy=policy, contract=contract, method=method, n=len(rows),
                                  vm_median_ms=statistics.median(v), vm_p95_ms=quantile(v, .95),
                                  client_median_ms=statistics.median(c), client_p95_ms=quantile(c, .95),
                                  committed_successes=len(rows), success_pct=100,
                                  observed_successful_commit_rate_tps=len(rows) / (window / 1e9),
                                  rate_scope='paced single-client smoke, includes 100ms gaps; not saturation capacity',
                                  historical_tps='not_measured_formula_unknown',
                                  saturated_commit_tps='not_measured', ci95='not_estimated_single_smoke'))
        for (contract, method, index), modes in paired.items():
            a, b = modes['R0'], modes['R1']
            ar = a[0]['response'].get('contract_result') or {}
            br = b[0]['response'].get('contract_result') or {}
            def writes(info):
                return sorted((info.get('rw_set') or {}).get('tx_writes', []), key=lambda x: json.dumps(x, sort_keys=True))
            def normalized_events(result):
                return [{key: value for key, value in event.items() if key != 'tx_id'}
                        for event in result.get('contract_event', [])]
            def normalized_writes(info):
                values = json.loads(json.dumps(writes(info)))
                for value in values:
                    key = base64.b64decode(value.get('key', '')).decode(errors='replace')
                    # Preserve the raw comparison. Normalize only the known per-transaction
                    # identity in ERC721's latestTxInfo; retain BlockHeight and all state.
                    if contract == 'erc721' and key.endswith('_latestTxInfo'):
                        decoded = json.loads(base64.b64decode(value['value']))
                        decoded.pop('TxId', None)
                        value['value'] = json.dumps(decoded, sort_keys=True)
                return values
            correctness.append(dict(batch=batch, contract=contract, method=method, index=index,
                                    committed='pass', return_equal=ar.get('result') == br.get('result'),
                                    reported_gas_equal=ar.get('gas_used', 0) == br.get('gas_used', 0),
                                    writes_equal=writes(a[1]) == writes(b[1]),
                                    writes_equal_without_erc721_tx_id=normalized_writes(a[1]) == normalized_writes(b[1]),
                                    events_equal_without_tx_id=normalized_events(ar) == normalized_events(br),
                                    writes_r0=len(writes(a[1])), writes_r1=len(writes(b[1])),
                                    native_gas='not_collected', reuse_semantics='not_certified',
                                    table='not_tested', safe_for_production=False))
        for policy in ['R0', 'R1']:
            subset = [event for event in events if event['policy'] == policy]
            for contract in sorted(set(event['contract'] for event in subset)):
                ee = [event for event in subset if event['contract'] == contract]
                creates = [event['elapsed_ns'] / 1e6 for event in ee if event['event'] == 'create']
                closes = [event['elapsed_ns'] / 1e6 for event in ee if event['event'] == 'close']
                acquired = [event for event in ee if event['event'] in ['acquire', 'acquire_wait'] and event['instance_id']]
                event_summaries.append(dict(batch=batch, policy=policy, contract=contract,
                                           creates=len(creates), create_to_ready_median_ms=statistics.median(creates),
                                           create_to_ready_p95_ms=quantile(creates, .95),
                                           closes=len(closes), close_median_ms=statistics.median(closes),
                                           acquisitions=len(acquired), unique_acquired_instances=len(set(e['instance_id'] for e in acquired)),
                                           empty_queue_waits=sum(e['event'] == 'acquire_wait' for e in acquired),
                                           create_scope='all process creations, includes verification, initial grow, replacement',
                                           newinstance_only='not_separately_collected'))
            resources = [json.loads(line) for line in (folder / 'resources.jsonl').read_text().splitlines()
                         if json.loads(line)['policy'] == policy]
            first, last = resources[0], resources[-1]
            ticks = last['cpu_user_ticks'] + last['cpu_system_ticks'] - first['cpu_user_ticks'] - first['cpu_system_ticks']
            cpu_s = ticks / os.sysconf('SC_CLK_TCK')
            span_s = (last['monotonic_ns'] - first['monotonic_ns']) / 1e9
            resource_summaries.append(dict(batch=batch, policy=policy, rss_peak_mib=max(x['VmRSS'] for x in resources)/1024,
                                           rss_last_mib=last['VmRSS']/1024, vmsize_last_gib=last['VmSize']/1024**2,
                                           threads_peak=max(x['Threads'] for x in resources), threads_last=last['Threads'],
                                           cpu_seconds=cpu_s, observed_seconds=span_s,
                                           cpu_pct_one_core=cpu_s/span_s*100,
                                           cpu_scope='whole process including startup, compilation, smoke, ledger checks and idle'))
        write('events-' + batch + '.csv', events)
    write('samples.csv', samples); write('summary.csv', summaries)
    write('correctness.csv', correctness); write('instance_summary.csv', event_summaries)
    write('resource_summary.csv', resource_summaries)
    comparison = []
    historical = json.loads((ROOT / 'environment.json').read_text())['historical_tps']
    for name, (reuse, fresh) in historical.items():
        contract, method = name.split('.', 1)
        candidates = [row for row in summaries if row['contract'] == contract and row['method'] == method]
        modes = {row['policy']: row for row in candidates}
        row = dict(contract=contract, method=method, historical_reuse_tps=reuse, historical_no_reuse_tps=fresh,
                   historical_drop_pct=(reuse-fresh)/reuse*100,
                   current_r0_capacity_tps='not_measured', current_r1_capacity_tps='not_measured',
                   current_capacity_drop_pct='not_available', reproduction='not_established')
        if modes:
            a, b = modes['R0'], modes['R1']
            row.update(r0_vm_median_ms=a['vm_median_ms'], r1_vm_median_ms=b['vm_median_ms'],
                       r0_vm_p95_ms=a['vm_p95_ms'], r1_vm_p95_ms=b['vm_p95_ms'],
                       difference_of_medians_ms=b['vm_median_ms']-a['vm_median_ms'],
                       median_increase_pct=(b['vm_median_ms']/a['vm_median_ms']-1)*100,
                       n_each=a['n'], evidence='single low-load smoke, fixed R0 then R1 order; no paired-effect claim')
        comparison.append(row)
    write('historical_comparison.csv', comparison)
    gas_differences = sum(not row['reported_gas_equal'] for row in correctness)
    raw_write_differences = sum(not row['writes_equal'] for row in correctness)
    unexpected = [row for row in correctness if not all(row[key] for key in ['return_equal', 'writes_equal_without_erc721_tx_id', 'events_equal_without_tx_id'])]
    print('samples', len(samples), 'comparisons', len(correctness), 'reported Gas differences', gas_differences,
          'raw write differences', raw_write_differences, 'unexpected business differences', len(unexpected))
    assert not unexpected, unexpected


if __name__ == '__main__':
    main()
