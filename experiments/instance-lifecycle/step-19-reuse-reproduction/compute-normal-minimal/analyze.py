"""Reduce saved normalCal runs without executing any nodes."""
from pathlib import Path
import base64
import collections
import csv
import hashlib
import json
import math
import re
import statistics
import subprocess
from run_low import events, invoke_logs

ROOT = Path(__file__).resolve().parent


def write(name, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (ROOT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def stats(values):
    return dict(n=len(values), mean_ms=statistics.mean(values)/1e6,
                median_ms=statistics.median(values)/1e6,
                p95_ms=sorted(values)[math.ceil(.95*len(values))-1]/1e6,
                vm_log_tps=len(values)*1e9/sum(values))


def main():
    raw = [json.loads(x) for x in (ROOT/'requests.jsonl').read_text().splitlines()]
    resources = [json.loads(x) for x in (ROOT/'resources.jsonl').read_text().splitlines()]
    commits = {(x['batch'], x['policy'], x['transaction']['transaction']['payload']['tx_id']): x['transaction']
               for x in raw if x['phase'] == 'commit-check'}
    samples, summaries, pairs, boundaries, hashes = [], [], collections.defaultdict(dict), [], []
    all_mints = [x for x in raw if x['phase'] in ['warmup', 'sample']]
    assert len(all_mints) == 60
    for r in all_mints:
        info = commits[r['batch'], r['policy'], r['response']['tx_id']]
        assert info['block_height'] > 0
        result = info['transaction']['result']
        assert result.get('code', 0) == 0
        assert base64.b64decode(result['contract_result']['result']) == b'success normalCal: 666'
    for batch, policy in [('a', 'R0'), ('a', 'R1'), ('b', 'R1'), ('b', 'R0')]:
        home = ROOT/batch/'network'/('baseline' if policy == 'R0' else 'optimized')
        original = invoke_logs(home)
        bytx = collections.defaultdict(list)
        for log in original:
            bytx[log['tx_id']].append(log)
        stdout = (home/'stdout.log').read_text()
        aux = {m[1]: (int(m[2]), int(m[3])) for m in re.finditer(
            r'REUSE_VM tx=(\w+).*?begin_ns=(\d+) end_ns=(\d+)', stdout)}
        selected = []
        for r in raw:
            if (r.get('batch'), r.get('policy'), r.get('phase')) != (batch, policy, 'sample'):
                continue
            tx = r['response']['tx_id']
            logs = bytx[tx]
            assert len(logs) == 1
            log = logs[0]
            assert log['contract'] == 'compute' and log['method'] == 'normalCal' and log['code'] == 0
            assert aux[tx] == (log['begin_ns'], log['end_ns'])
            info = commits[batch, policy, tx]
            assert info['transaction']['payload'].get('parameters', []) == []
            row = dict(batch=batch, policy=policy, index=r['index'], tx_id=tx,
                       vm_ns=log['end_ns']-log['begin_ns'], begin_ns=log['begin_ns'], end_ns=log['end_ns'],
                       gas=r['response']['contract_result']['gas_used'], client_ns=r['elapsed_ns'],
                       committed=True, source_file=log['file'], source_line=log['line'])
            samples.append(row)
            selected.append(row['vm_ns'])
            pairs[batch, r['index']][policy] = info['transaction']['result']['contract_result']
            boundaries.append(dict(batch=batch, policy=policy, tx_id=tx, original_matches_aux=True))
        assert len(selected) == 10
        ee = events(home)
        assert sum(x['event'] == 'acquire_wait' for x in ee) == 0
        creates = [x for x in ee if x['event'] == 'create']
        assert len(creates) == (6 if policy == 'R0' else 22)
        rr = [x for x in resources if (x['batch'], x['policy']) == (batch, policy)]
        start = next(x for x in rr if x['label'] == 'post-deploy')
        row = dict(batch=batch, policy=policy, **stats(selected), empty_pool_events=0,
                   blocking_wait_observed=False, creates=len(creates), replacements=len(creates)-6,
                   replacement_median_ms=statistics.median(x['elapsed_ns'] for x in creates[6:])/1e6 if policy == 'R1' else '',
                   rss_peak_mib=max(x['VmRSS'] for x in rr)/1024,
                   post_deploy_rss_growth_mib=(rr[-1]['VmRSS']-start['VmRSS'])/1024,
                   threads_peak=max(x['Threads'] for x in rr), execution_errors=0)
        summaries.append(row)
        pid = int((home/'pid').read_text())
        assert not Path(f'/proc/{pid}').exists()
        unit = f'step19-normal-min-{batch}-{policy.lower()}'
        assert subprocess.run(['systemctl', '--user', 'is-active', unit], capture_output=True, text=True).stdout.strip() != 'active'
        for f in [home/'stdout.log', home/'sdk.yml', *sorted((home/'config').rglob('*.yml')),
                  *sorted((home/'log').glob('system.log.*'))]:
            hashes.append(dict(path=str(f.relative_to(ROOT)), sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
    comparisons = []
    for batch in ['a', 'b', 'pooled_descriptive']:
        v = {p: stats([r['vm_ns'] for r in samples if r['policy'] == p and
                      (batch == 'pooled_descriptive' or r['batch'] == batch)]) for p in ['R0', 'R1']}
        a, b = v['R0'], v['R1']
        comparisons.append(dict(batch=batch, n_each=a['n'], r0_mean_ms=a['mean_ms'], r1_mean_ms=b['mean_ms'],
                                r0_vm_log_tps=a['vm_log_tps'], r1_vm_log_tps=b['vm_log_tps'],
                                ratio=a['vm_log_tps']/b['vm_log_tps'],
                                r1_tps_drop_pct=100*(1-b['vm_log_tps']/a['vm_log_tps']),
                                empty_pool_events=0, pressure='serial_200ms_plus_quiescence'))
    checks = []
    for (batch, index), modes in pairs.items():
        a, b = modes['R0'], modes['R1']
        checks.append(dict(batch=batch, index=index, result_equal=a['result'] == b['result'],
                           r0_gas=a['gas_used'], r1_gas=b['gas_used'], gas_equal=a['gas_used'] == b['gas_used'],
                           r0_events=len(a.get('contract_event', [])), r1_events=len(b.get('contract_event', [])),
                           table='not_tested', all_semantics_certified=False))
    assert all(c['result_equal'] for c in checks)
    write('samples.csv', samples)
    write('summary.csv', summaries)
    write('comparison.csv', comparisons)
    write('correctness.csv', checks)
    write('boundary_check.csv', boundaries)
    (ROOT/'artifact_hashes.json').write_text(json.dumps(hashes, indent=2)+'\n')
    print(json.dumps(comparisons, indent=2))
    print('60 successful committed calls; 40 original log samples; gas differences:', sum(not c['gas_equal'] for c in checks))


if __name__ == '__main__':
    main()
