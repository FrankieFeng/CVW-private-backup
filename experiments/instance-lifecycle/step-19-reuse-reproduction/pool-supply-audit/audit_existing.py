"""Audit already-saved logs only. Does not launch nodes or invoke contracts."""
from pathlib import Path
import collections, csv, json, statistics

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent


def write(name, rows):
    with (OUT / name).open('w', newline='') as stream:
        fields = list(dict.fromkeys(key for row in rows for key in row))
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def main():
    inventory, replacements, windows, idle = [], [], [], []
    samples = list(csv.DictReader((ROOT / 'samples.csv').open()))
    for batch, folder in [('three-contract-smoke', ROOT), ('fact-target-smoke', ROOT / 'fact-target-smoke')]:
        events = []
        for endpoint, policy in [('baseline', 'R0'), ('optimized', 'R1')]:
            for line in (folder / 'network' / endpoint / 'stdout.log').read_text().splitlines():
                if line.startswith('REUSE_EVENT '):
                    events.append(dict(json.loads(line[12:]), policy=policy))
        resources = [json.loads(line) for line in (folder / 'resources.jsonl').read_text().splitlines()]
        for policy in ['R0', 'R1']:
            pe = [event for event in events if event['policy'] == policy]
            for contract in sorted(set(event['contract'] for event in pe)):
                ce = [event for event in pe if event['contract'] == contract]
                begins = [event for event in ce if event['event'] == 'create_begin']
                acquired = [event for event in ce if event['event'] in ['acquire', 'acquire_wait'] and event['instance_id']]
                dropped = [event for event in ce if event['event'] == 'drop']
                closed = {event['instance_id']: event for event in ce if event['event'] == 'close_done'}
                enqueued = {event['instance_id']: event for event in ce if event['event'] == 'enqueue_done'}
                # One verification instance + five manager initial-grows, verified against queue events.
                assert len(begins) >= 6
                assert begins[0]['instance_id'] in closed and begins[0]['instance_id'] not in enqueued
                assert all(event['instance_id'] in enqueued for event in begins[1:6])
                after_initial = begins[6:]
                assert len(after_initial) == len(dropped)
                for i, (drop, begin) in enumerate(zip(dropped, after_initial)):
                    close = closed[drop['instance_id']]
                    enqueue = enqueued[begin['instance_id']]
                    assert drop['unix_ns'] <= close['unix_ns'] <= begin['unix_ns'] <= enqueue['unix_ns']
                    # Verify that no second discard was pending: FIFO association is unambiguous here.
                    if i + 1 < len(dropped):
                        assert enqueue['unix_ns'] < dropped[i+1]['unix_ns']
                    replacements.append(dict(batch=batch, policy=policy, contract=contract,
                                             dropped_instance=drop['instance_id'], new_instance=begin['instance_id'],
                                             association='single-outstanding-per-pool FIFO verified in existing smoke',
                                             drop_to_closed_ms=(close['unix_ns']-drop['unix_ns'])/1e6,
                                             closed_to_create_ms=(begin['unix_ns']-close['unix_ns'])/1e6,
                                             create_to_enqueue_ms=(enqueue['unix_ns']-begin['unix_ns'])/1e6,
                                             drop_to_enqueue_ms=(enqueue['unix_ns']-drop['unix_ns'])/1e6))
                inventory.append(dict(batch=batch, policy=policy, contract=contract,
                                      verification_creates=1, initial_grow_creates=5,
                                      replacement_creates=len(after_initial), total_creates=len(begins),
                                      borrowed=len(acquired), unique_borrowed=len(set(x['instance_id'] for x in acquired)),
                                      discarded=len(dropped), closed=len(closed), enqueued=len(enqueued),
                                      wait_events=sum(event['event']=='acquire_wait' for event in acquired),
                                      min_queue_at_borrow=min(event['queue_len'] for event in acquired),
                                      max_queue_at_borrow=max(event['queue_len'] for event in acquired)))
            pr = [row for row in resources if row['policy'] == policy]
            offset = pr[0]['unix_ns'] - pr[0]['monotonic_ns']
            ss = [row for row in samples if row['batch']==batch and row['policy']==policy]
            groups = collections.defaultdict(list)
            for row in ss:
                groups[row['contract'], row['method']].append(row)
            for (contract, method), rows in groups.items():
                begin = min(int(row['window_begin_ns']) for row in rows)
                end = max(int(row['window_end_ns']) for row in rows)
                span = (end-begin)/1e9
                during = [event for event in pe if event['contract']==contract+'_1.0.0'
                          and begin+offset <= event['unix_ns'] <= end+offset]
                creates = [event for event in during if event['event']=='create']
                enqueues = [event for event in during if event['event']=='enqueue_done']
                lo = max((row for row in pr if row['monotonic_ns']<=begin),key=lambda x:x['monotonic_ns'])
                hi = min((row for row in pr if row['monotonic_ns']>=end),key=lambda x:x['monotonic_ns'])
                windows.append(dict(batch=batch, policy=policy, contract=contract, method=method,
                                    n=len(rows), window_seconds=span, created=len(creates), enqueued=len(enqueues),
                                    observed_enqueue_per_second=len(enqueues)/span,
                                    create_function_wall_ms=sum(row['elapsed_ns'] for row in creates)/1e6,
                                    create_function_wall_pct=sum(row['elapsed_ns'] for row in creates)/(end-begin)*100,
                                    rss_delta_mib=(hi['VmRSS']-lo['VmRSS'])/1024,
                                    virtual_delta_gib=(hi['VmSize']-lo['VmSize'])/1024**2,
                                    cpu_ticks_delta=hi['cpu_user_ticks']+hi['cpu_system_ticks']-lo['cpu_user_ticks']-lo['cpu_system_ticks'],
                                    threads_begin=lo['Threads'], threads_end=hi['Threads'],
                                    boundary_before_gap_ms=(begin-lo['monotonic_ns'])/1e6,
                                    boundary_after_gap_ms=(hi['monotonic_ns']-end)/1e6,
                                    limits='paced window; wall busy is not CPU; whole-process RSS includes business/host/ledger/allocator; not capacity'))
            ri = [row for row in pr if row['label']=='before-idle' or row['label']=='idle']
            a,b = ri[0],ri[-1]
            idle.append(dict(batch=batch,policy=policy,seconds=(b['monotonic_ns']-a['monotonic_ns'])/1e9,
                             rss_begin_mib=a['VmRSS']/1024,rss_end_mib=b['VmRSS']/1024,
                             virtual_begin_gib=a['VmSize']/1024**2,virtual_end_gib=b['VmSize']/1024**2,
                             threads_begin=a['Threads'],threads_end=b['Threads']))
    write('inventory.csv', inventory); write('replacement_pairs.csv', replacements)
    write('sample_windows.csv', windows); write('idle_resources.csv', idle)
    summary=[]
    for (batch,contract), rows in __import__('itertools').groupby(sorted(replacements,key=lambda x:(x['batch'],x['contract'])),key=lambda x:(x['batch'],x['contract'])):
        rows=list(rows)
        result=dict(batch=batch,contract=contract,n=len(rows))
        for metric in ['drop_to_closed_ms','closed_to_create_ms','create_to_enqueue_ms','drop_to_enqueue_ms']:
            result[metric+'_median']=statistics.median(row[metric] for row in rows)
        summary.append(result)
    write('replacement_summary.csv',summary)
    print('audited', len(inventory), 'pool/policy records;',len(replacements),'replacements;',len(windows),'existing sample windows; no new execution')


if __name__=='__main__':
    main()
