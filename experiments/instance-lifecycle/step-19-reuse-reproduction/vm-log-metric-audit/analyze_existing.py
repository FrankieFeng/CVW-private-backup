"""Apply recovered log formulas to saved data. Never executes a benchmark."""
from pathlib import Path
import collections, csv, hashlib, json, math, re, statistics

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
PROJECT = ROOT.parents[3]
TOOL = PROJECT / 'chainmaker-test-toolkit-master/chainmaker-performance-test'
OLD = re.compile(r'tx id:([a-f0-9]+),\s*contractName:([^,]+),\s*contractMethod:([^,]+),\s*'
                 r'runtime type:(\w+),\s*runtimeContractResult:(\d+)\s*,\s*'
                 r'startTime:(\d+),\s*endTime:(\d+),\s*executionTime:([\d.]+) s')


def write(name, rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/name).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def calc(rows):
    total=sum(r['end']-r['begin'] for r in rows)
    span=max(r['end'] for r in rows)-min(r['begin'] for r in rows)
    return dict(n=len(rows),sum_execution_ns=total,mean_ms=total/len(rows)/1e6,
                duration_sum_vm_log_tps=len(rows)*1e9/total,
                first_to_last_ns=span,span_vm_event_rate=len(rows)*1e9/span)


def main():
    raw={};all_raw={};provenance=[]
    for batch,folder in [('three-contract-smoke',ROOT),('fact-target-smoke',ROOT/'fact-target-smoke')]:
        for policy,endpoint in [('R0','baseline'),('R1','optimized')]:
            path=folder/'network'/endpoint/'stdout.log';rows=[]
            for number,line in enumerate(path.read_text().splitlines(),1):
                if not line.startswith('REUSE_VM '):continue
                d=dict(re.findall(r'(\w+)=([^ ]+)',line))
                row=dict(tx_id=d['tx'],contract=d['contract'],method=d['method'],
                         begin=int(d['begin_ns']),end=int(d['end_ns']),code=int(d['code']),
                         raw_file=str(path),raw_line=number)
                raw[batch,policy,d['tx']]=row;rows.append(row)
            all_raw[batch,policy]=rows
            provenance.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),kind='step19_raw'))
    selected=collections.defaultdict(list);boundary=[]
    for sample in csv.DictReader((ROOT/'samples.csv').open()):
        row=raw[sample['batch'],sample['policy'],sample['tx_id']]
        assert row['end']-row['begin']==int(sample['vm_invoke_ns'])
        assert row['code']==0
        selected[sample['batch'],sample['policy'],sample['contract'],sample['method']].append(row)
        boundary.append(dict(batch=sample['batch'],policy=sample['policy'],tx_id=sample['tx_id'],
                             raw_begin_ns=row['begin'],raw_end_ns=row['end'],csv_duration_ns=sample['vm_invoke_ns'],
                             exact_duration_match=True,raw_file=row['raw_file'],raw_line=row['raw_line']))
    summary=[]
    for (batch,policy,contract,method),rows in selected.items():
        result=dict(batch=batch,policy=policy,contract=contract,method=method,**calc(rows))
        duration=[r['end']-r['begin'] for r in rows]
        result.update(median_ms=statistics.median(duration)/1e6,
                      p95_ms=sorted(duration)[math.ceil(.95*len(duration))-1]/1e6,
                      source_formula='normalTPSTest lines805-809 N/sum(end-start)',
                      selection='20 saved business samples; warmup/deploy excluded explicitly',
                      metric_status='adopted_by_user_as_current_protocol_not_claimed_exact_PPT_formula',
                      ppt_version_match='not_confirmed',actual_commit_tps='different_metric')
        summary.append(result)
    compare=[]
    history=[('compute','normalCal',408.7,264.3),('compute','bigNumCal',295.8,210.4),
             ('compute','hashCal',769.6,277),('erc721','mint',4077.5,311.4),
             ('fact','saveAndFindByFileHash',2959.1,380.3),('exchange','buyNow',881.2,57.7)]
    for contract,method,a,b in history:
        modes={r['policy']:r for r in summary if r['contract']==contract and r['method']==method}
        row=dict(contract=contract,method=method,historical_r0=a,historical_r1=b,
                 historical_drop_pct=(1-b/a)*100,source='user supplied PPT reference; exact code version/entry unresolved')
        if modes:
            aa,bb=modes['R0'],modes['R1'];u,v=aa['duration_sum_vm_log_tps'],bb['duration_sum_vm_log_tps']
            row.update(current_r0_sum_metric=u,current_r1_sum_metric=v,current_drop_pct=(1-v/u)*100,n_each=aa['n'],
                       comparison='adopted N/sum protocol; historical figures are references, exact formula-version equivalence not claimed')
        else:row.update(current_r0_sum_metric='',current_r1_sum_metric='',current_drop_pct='',n_each=0,comparison='method not sampled; do not substitute another method')
        compare.append(row)
    # Literal selection replay, adapting only the input transport from REUSE_VM timestamps.
    replay=[]
    for (batch,policy),rows in all_raw.items():
        after_skip=rows[1:]
        total=sum(r['end']-r['begin'] for r in after_skip)
        for contract,method in sorted(set((r['contract'],r['method']) for r in after_skip if r['method']!='init_contract')):
            matching=[r for r in after_skip if (r['contract'],r['method'])==(contract,method)]
            replay.append(dict(batch=batch,policy=policy,contract=contract,method=method,
                               count_after_first_record_skip=len(matching),all_record_denominator_ns=total,
                               literal_selection_sum_metric=len(matching)*1e9/total,
                               warning='denominator includes other methods before filter; transport adapted, original INFO suppressed; not clean sample summary'))
    old_inventory=[]
    for path in sorted((TOOL/'log/experimentlog').glob('system.log.*')):
        rows=[];count=0;too_long=False
        for line in path.read_text(errors='replace').splitlines():
            if len(line.encode())>=65536:too_long=True;break
            if 'vm_factory.go:438' not in line:continue
            m=OLD.search(line)
            if not m:continue
            count+=1
            if count==1:continue
            rows.append(dict(tx_id=m[1],contract=m[2],method=m[3],code=int(m[5]),begin=int(m[6]),end=int(m[7])))
        if not rows:continue
        for contract,method in sorted(set((r['contract'],r['method']) for r in rows)):
            selected_rows=[r for r in rows if (r['contract'],r['method'])==(contract,method)]
            item=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),contract=contract,method=method,
                      original_first_match_skipped=True,matched_before_skip=count,failed=sum(r['code']!=0 for r in selected_rows),
                      mode='reuse policy unknown',ppt_reference_match='not_established',scanner_token_limit_reached=too_long,**calc(selected_rows))
            all_total=sum(r['end']-r['begin'] for r in rows)
            item.update(literal_denominator_all_methods_ns=all_total,literal_normal_tps=len(selected_rows)*1e9/all_total)
            old_inventory.append(item)
    write('boundary_check.csv',boundary);write('vm_log_summary.csv',summary)
    write('historical_comparison.csv',compare);write('literal_selection_replay.csv',replay)
    write('legacy_log_inventory.csv',old_inventory)
    for path in [TOOL/'parallel/parallel_claim.go',TOOL/'parallel/process_pressure.go',TOOL/'config/const_config.yml']:
        provenance.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),kind='recovered_calculator_or_config_no_git_metadata'))
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print('verified',len(boundary),'exact timestamp durations;',len(summary),'sample groups;',len(old_inventory),'legacy log/method groups; no new execution')


if __name__=='__main__':main()
