"""Read retained raw records, not Markdown conclusions. No benchmark execution."""
from pathlib import Path
from collections import defaultdict
import re,json,csv,statistics
ROOT=Path(__file__).resolve().parent.parent
OLD=ROOT.parent/'step-21-instance-reuse-loss/capacity-fix-20261024-01'
fields=['total_ns','internal_total_ns','runtime_ns','prepare_ns','dispatch_pre_ns','allocate_ns','copy_lookup_ns','export_call_ns','dispatch_post_ns','syscall_ns','syscall_count']
rows=[];overlaps=[]
for batch in ['b','c','d']:
 for policy in ['R0','R1']:
    path=OLD/'raw_logs'/f'compute-normalCal-{batch}-{policy.lower()}.log'
    events=[];profiles=[];calls=[]
    for line,s in enumerate(path.read_text().splitlines(),1):
        if s.startswith('REUSE_EVENT '):events.append(dict(json.loads(s[12:]),line=line))
        if s.startswith('STEP21 '):
            r=json.loads(s[7:])
            if r['event']=='sample':calls.append(dict(r,line=line))
        if 'b5_profile sample_id=' in s:
            d=dict(re.findall(r'(\w+)=([^\s]*)',s));profiles.append(dict(d,line=line))
    assert len(calls)==len(profiles)==100
    for call,prof in zip(calls,profiles):
        row=dict(batch=batch,policy=policy,index=call['index'],gas=call['gas'],code=call['code'],invoke_ns=call['end_ns']-call['begin_ns'],callmethod_ns=round(call['callmethod_s']*1e9),source=str(path),source_line=prof['line'])
        row.update({f:int(prof[f]) for f in fields});rows.append(row)
    starts=[r for r in events if r['event']=='create_begin'];ends=[r for r in events if r['event']=='create'];assert len(starts)==len(ends)
    creates=list(zip(starts,ends))
    bs={};cl={}
    for e in events:
        if e['event']=='business_before':bs[e['instance_id']]=e
        elif e['event']=='close_begin':cl[e['instance_id']]=e
        elif e['event']=='business_return':
            b=bs.pop(e['instance_id'])
            for start,end in creates:
                if start['unix_ns']<e['unix_ns'] and end['unix_ns']>b['unix_ns']:
                    overlaps.append(dict(batch=batch,policy=policy,kind='recorded_create_vs_business',business_instance=e['instance_id'],other_instance=start['instance_id'],business_start_line=b['line'],business_end_line=e['line'],other_start_line=start['line'],other_end_line=end['line'],source=str(path)))
        elif e['event']=='close_done':
            start=cl.pop(e['instance_id'])
            # Close overlap is reduced separately from all business intervals below.
    bstarts=[x for x in events if x['event']=='business_before'];bends=[x for x in events if x['event']=='business_return'];cstarts=[x for x in events if x['event']=='close_begin'];cends=[x for x in events if x['event']=='close_done']
    closeend={x['instance_id']:x for x in cends}
    for b,e in zip(bstarts,bends):
        assert b['instance_id']==e['instance_id']
        for start in cstarts:
            end=closeend[start['instance_id']]
            if start['unix_ns']<e['unix_ns'] and end['unix_ns']>b['unix_ns']:
                overlaps.append(dict(batch=batch,policy=policy,kind='recorded_close_vs_business',business_instance=e['instance_id'],other_instance=start['instance_id'],business_start_line=b['line'],business_end_line=e['line'],other_start_line=start['line'],other_end_line=end['line'],source=str(path)))
def write(name,values):
 with (ROOT/'audit'/name).open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in values for k in r)));w.writeheader();w.writerows(values)
write('previous_normalcal_components.csv',rows);write('previous_recorded_overlaps.csv',overlaps)
means={p:{f:statistics.mean(r[f] for r in rows if r['policy']==p)/1e6 for f in ['invoke_ns','callmethod_ns']+fields if f!='syscall_count'} for p in ['R0','R1']}
result=dict(scope='previous accepted normalCal b/c/d, raw B5 per-call records',n_each=300,means_ms=means,export_delta_ms=means['R0']['export_call_ns']-means['R1']['export_call_ns'],callmethod_delta_ms=means['R0']['callmethod_ns']-means['R1']['callmethod_ns'],overlap_counts={p:{k:sum(x['policy']==p and x['kind']==k for x in overlaps) for k in ['recorded_create_vs_business','recorded_close_vs_business']} for p in ['R0','R1']},limitations='timestamps are recorded wall intervals; conservative region overlap is not proof of actual native data race; normalCal a invalid clock pair excluded completely')
(ROOT/'audit/history-observations.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
