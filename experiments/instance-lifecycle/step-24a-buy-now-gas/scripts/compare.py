from pathlib import Path
import hashlib,json,sys
P=Path(__file__).resolve().parents[1]
TX=json.loads((P/'inputs/business.json').read_text())['root_tx_id']
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(label):
 o=json.loads((P/'raw_logs'/f'{label}-outcome.json').read_text());assert o['passed'],label
 events=[json.loads(l)for l in(P/'raw_logs'/f'{label}-events.jsonl').read_text().splitlines()]
 calls=[e['record']for e in events if e['event']=='call_record'and e['record']['tx_id']==TX];calls.sort(key=lambda c:c['call_id']);assert [c['call_id']for c in calls]==list(range(7))
 for c in calls:assert c['actual_result'].get('code',0)==0 and c['call_error_observed']=='<nil>'
 return dict(label=label,outcome=o,events=events,calls=calls,gas=[e for e in events if e['event']=='gas'and e['tx_id']==TX],bridge=[e for e in events if e['event']=='bridge_gas'and e['tx_id']==TX],receipt=json.loads((P/'raw_logs'/f'{label}-receipts/target.json').read_text()))
def semantics(c,with_state=True):
 r=dict(c['actual_result']);r.pop('gas_used',None)
 return dict(call_id=c['call_id'],parent_call_id=c['parent_call_id'],caller=c['caller'],contract=c['contract'],method=c['method'],depth=c['depth'],tx_id=c['tx_id'],actual_parameters=c['actual_parameters'],state_before=c['state_observation_before']if with_state else None,state_after=c['state_observation_after']if with_state else None,own_state_operations=c['own_state_operations']if with_state else None,actual_result_without_gas=r,initial_ledger_sha=c['initial_ledger_sha'])
def shape(e):return tuple(e[k]for k in ['call_id','seq','phase','host','when','detail'])
def gas_compare(a,b):
 aa=a['gas'];bb=b['gas']
 if not aa or not bb:return dict(status='not_applicable_probe_off',all_equal=None,first=None)
 prev=None
 for i,(x,y)in enumerate(zip(aa,bb)):
  if shape(x)!=shape(y):return dict(status='host_path_or_log_diff',all_equal=False,first=dict(index=i,a=x,b=y),previous=prev)
  if x['gas_absolute']!=y['gas_absolute']:
   return dict(status='gas_counter_diff',all_equal=False,first=dict(index=i,a=x,b=y,delta_b_minus_a=y['gas_absolute']-x['gas_absolute']),previous=prev)
  prev=dict(a=x,b=y)
 if len(aa)!=len(bb):return dict(status='trace_length_diff',all_equal=False,first=dict(a_count=len(aa),b_count=len(bb)))
 return dict(status='equal',all_equal=True,first=None,points=len(aa))
def compare(a_label,b_label,require_gas=False):
 a=load(a_label);b=load(b_label);rows=[]
 for x,y in zip(a['calls'],b['calls']):
  observe_both=a['outcome']['probe']=='on'and b['outcome']['probe']=='on'
  same=semantics(x,observe_both)==semantics(y,observe_both)
  assert same,(a_label,b_label,x['call_id'],'business/RW/events/inputs differ')
  gas_equal=x['gas_in_cumulative']==y['gas_in_cumulative']and x['gas_out_cumulative']==y['gas_out_cumulative']
  if require_gas:assert gas_equal,(a_label,b_label,x['call_id'],'Gas differs')
  rows.append(dict(call_id=x['call_id'],contract=x['contract'],method=x['method'],gas_in_a=x['gas_in_cumulative'],gas_in_b=y['gas_in_cumulative'],gas_out_a=x['gas_out_cumulative'],gas_out_b=y['gas_out_cumulative'],local_delta_a=x['gas_out_cumulative']-x['gas_in_cumulative'],local_delta_b=y['gas_out_cumulative']-y['gas_in_cumulative'],gas_equal=gas_equal,semantic_equal=same,state_before_sha=digest(x['state_observation_before']),state_after_sha=digest(x['state_observation_after']),events_sha=digest(x['actual_result'].get('contract_event',[]))))
 for k in ['business_input','before_hash','after_hash','status','actual_rwset']:assert a['receipt'][k]==b['receipt'][k],k
 trace=gas_compare(a,b)
 if require_gas and a['gas']and b['gas']:assert trace['all_equal'],trace
 bridge_fields=['bridge_seq','when','is_len','parent_remaining_readonly','gas_argument_or_return_cumulative','callee_result_gas_cumulative','callee_code','callee_result']
 bridge_equal=None
 if a['bridge']and b['bridge']:
  bridge_equal=[{k:e.get(k)for k in bridge_fields}for e in a['bridge']]==[{k:e.get(k)for k in bridge_fields}for e in b['bridge']]
  if require_gas:assert bridge_equal,'bridge counter differs'
 report=dict(labels=[a_label,b_label],require_gas=require_gas,root_delta_b_minus_a=b['calls'][0]['gas_out_cumulative']-a['calls'][0]['gas_out_cumulative'],all_business_equal=True,all_call_gas_equal=all(r['gas_equal']for r in rows),bridge_counters_equal=bridge_equal,calls=rows,trace=trace)
 (P/'audit'/f'compare-{a_label}-{b_label}.json').write_text(json.dumps(report,indent=2)+'\n')
 first=trace.get('first')or{}
 print(json.dumps(dict(labels=report['labels'],root_delta=report['root_delta_b_minus_a'],business_equal=True,gas_equal=report['all_call_gas_equal'],trace=trace['status'],first_call_id=first.get('a',{}).get('call_id'),first_phase=first.get('a',{}).get('phase'),first_host=first.get('a',{}).get('host'))),flush=True)
 return report
if __name__=='__main__':compare(sys.argv[1],sys.argv[2],'--require-gas'in sys.argv[3:])
