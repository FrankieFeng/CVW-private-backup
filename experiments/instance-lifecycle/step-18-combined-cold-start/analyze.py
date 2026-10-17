"""Paired pilot analysis. Negative delta means faster; blocked cells stay visible."""
import csv,json,statistics,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(os.environ.get('S18_REPO','/home/frankie/mygitprojects/CVW'))/'experiments/instance-lifecycle/step-15-copy-attribution'))
from common import csvwrite,stats

def readrows(path):
 return [json.loads(line) for line in path.read_text().splitlines()]
def ci(values):return stats(values,seed=18018,block=5,reps=4000)
def same(a,b,keys):return all(a.get(k)==b.get(k) for k in keys)
def main():
 raw=[]
 for folder in sorted(ROOT.glob('pilot-*')):
  if not (folder/'run.json').exists():continue
  for path in sorted(folder.glob('*.jsonl')):
   for row in readrows(path):
    if row['kind']=='sample':row['batch']=folder.name;row['invoke_minus_s3_ns']=row['invoke_ns']-row['s3_ns'];raw.append(row)
 csvwrite(ROOT/'samples.csv',raw)
 plain=[r for r in raw if r['mode']=='plain'];probe=[r for r in raw if r['mode']=='probe']
 summary=[];effects=[];interactions=[];correctness=[];ppt=[];error_rows=[]
 variants=list(csv.DictReader((ROOT/'variants.csv').open()))
 measures=['s1_ns','start_ns','s2_ns','s3_ns','invoke_ns','copy_ns','invoke_minus_s3_ns']
 keys=['result','result_code','message','registry_gas','native_business_gas','native_init_and_setgas_gas','writes_sha256','events','special','cross_calls']
 semantic=['result','result_code','message','writes_sha256','events','special','cross_calls']
 for contract in ['compute','erc721','fact']:
  data={};diag={}
  for r in plain:
   if r['contract']==contract:data[r['sample'],r['A'],r['C']]=r
  for r in probe:
   if r['contract']==contract:diag[r['sample'],r['A'],r['C']]=r
  rounds=sorted({key[0] for key in data});assert len(data)==4*len(rounds)
  assert len({r['instance_id'] for r in plain if r['contract']==contract})==len(data)
  vchecks=[]
  for p in (ROOT/'validation').glob(contract+'-checks.jsonl'):vchecks+=readrows(p)
  tchecks=[]
  for p in (ROOT/'validation').glob(contract+'-a*p0-plain.jsonl'):tchecks+=readrows(p)
  for a in (0,1):
   for p in (0,1):
    for c in (0,1):
     variant=f'{a}{p}{c}'
     if p:
      summary.append(dict(contract=contract,A=a,P=p,C=c,scope='plain_VM_Invoke',metric='invoke_ns',n=0,status='blocked_missing_pb_source'))
      correctness.append(dict(contract=contract,A=a,P=p,C=c,status='blocked_missing_pb_source',safe='no',business='not_tested',gas='not_tested',table='not_tested',cross_contract='not_tested'))
      ppt.append(dict(contract=contract,variant=variant,status='blocked',n=0))
      continue
     rows=[data[i,a,c] for i in rounds]
     partner=[data[i,a,1-c] for i in rounds]
     copy_equal=all(same(r,q,keys) for r,q in zip(rows,partner))
     business=all(r['result_code']==0 and r['expected_output'] for r in rows)
     sem_equal=all(same(r,data[i,0,0],semantic) for i,r in zip(rounds,rows))
     checks=next((v for v in vchecks if v['A']==a and v['C']==c),{})
     stage=next((v for v in tchecks if v['label']==f'{contract}-a{a}p0-plain' and v['enabled']==bool(c)),{})
     table_checks=stage.get('stages',[])
     statics=bool(table_checks) and all(s.get('table_nullness_mismatches')==0 for s in table_checks)
     s1=checks.get('s1_checks',0)>0 and checks.get('s1_mismatches')==0
     peer=checks.get('fresh_memory_isolation',False) and stage.get('fresh_memory_globals_isolation',False)
     globals_ok=all(s.get('globals_table_size_equal') for s in table_checks if s['stage']=='S1') if table_checks else False
     peer_check=next((v for v in vchecks if v['A']==a and v['C']==1-c),{})
     ex_equal=bool(checks) and bool(peer_check) and same(checks['exception'],peer_check['exception'],[k for k in keys if k!='native_init_and_setgas_gas'])
     guest=checks.get('guest_error');guest_peer=peer_check.get('guest_error')
     guest_ok=bool(guest and guest_peer) and guest['result_code']!=0 and same(guest,guest_peer,[k for k in keys if k!='native_init_and_setgas_gas'])
     error_rows.append(dict(contract=contract,A=a,P=0,C=c,case='missing_export_host_dispatch',code=checks.get('exception',{}).get('result_code'),message=checks.get('exception',{}).get('message'),copy_equal=ex_equal,status='observed; host logs error but API returns code0; not a guest error validation'))
     error_rows.append(dict(contract=contract,A=a,P=0,C=c,case='invalid_numeric_input_guest',status='tested_pass' if guest_ok else 'not_tested' if not guest else 'failed',code=guest.get('result_code') if guest else None,message=guest.get('message') if guest else None,copy_equal=guest_ok if guest else 'not_tested'))
     gas_base=sorted({r['registry_gas'] for r in rows})
     native_base=sorted({r['native_business_gas'] for r in rows})
     startup_base=sorted({r['native_init_and_setgas_gas'] for r in rows})
     logical_gas_same=all(rows[j]['registry_gas']==data[i,0,0]['registry_gas'] and rows[j]['native_business_gas']==data[i,0,0]['native_business_gas'] for j,i in enumerate(rounds))
     tested=business and sem_equal and copy_equal and s1 and peer and globals_ok and statics and checks.get('template_immutable',False) and ex_equal and (guest_ok or contract=='compute')
     correctness.append(dict(contract=contract,A=a,P=0,C=c,status='tested_scope_pass' if tested else 'failed_or_incomplete',safe='not_certified',business_success=business,business_writes_events_equal_to_base=sem_equal,copy_same_logical_wasm_gas_results_equal=copy_equal,S1_memory=s1,globals_equal=globals_ok,fresh_memory_globals_isolation=peer,template_immutable=checks.get('template_immutable','not_tested'),table_nullness=statics,table_element_mapping='static_sections_preserved',table_function_identity='not_tested',cross_contract='not_tested',exception_copy_equal=ex_equal,exception_scope='host missing export; guest invalid numeric input for ERC721/fact',guest_error='tested_pass' if guest_ok else 'not_tested' if not guest else 'failed',exception_code=checks.get('exception',{}).get('result_code','missing'),exception_message=checks.get('exception',{}).get('message','missing'),registry_gas=gas_base,native_business_gas=native_base,native_init_and_setgas_gas=startup_base,cross_A_business_gas_equal=logical_gas_same,gas_acceptability='not_certified_for_new_binary',all_traps_OOG='not_tested'))
     for metric in measures:summary.append(dict(contract=contract,A=a,P=0,C=c,scope='plain_VM_Invoke',metric=metric,status='measured' if tested else 'unusable_or_incomplete',**ci([r[metric] for r in rows])))
     for metric in ['a_ns','b1_ns','clock_uncertainty_ns']:
      vs=[diag[i,a,c][metric] for i in rounds if (i,a,c) in diag]
      if vs:summary.append(dict(contract=contract,A=a,P=0,C=c,scope='instrumented_guest_diagnostic_only',metric=metric,status='diagnostic',**ci(vs)))
     deltas=[data[i,a,c]['invoke_ns']-data[i,0,0]['invoke_ns'] for i in rounds]
     st=ci([r['invoke_ns'] for r in rows]);d=ci(deltas)
     ppt.append(dict(contract=contract,variant=variant,status='measured' if tested else 'incomplete',median_ms=st['median_ns']/1e6,p95_ms=st['p95_ns']/1e6,paired_saving_ms=-d['median_ns']/1e6,saving_ci_low_ms=-d['ci95_high_ns']/1e6,saving_ci_high_ms=-d['ci95_low_ns']/1e6,n=len(rows)))
  contrasts={'A_only':[(1,0,1),(0,0,-1)],'C_only':[(0,1,1),(0,0,-1)],'A_plus_C':[(1,1,1),(0,0,-1)],'A_on_C':[(1,1,1),(0,1,-1)],'C_on_A':[(1,1,1),(1,0,-1)]}
  for name,terms in contrasts.items():
   for metric in measures:
    delta=[sum(sign*data[i,a,c][metric] for a,c,sign in terms) for i in rounds]
    effects.append(dict(contract=contract,contrast=name,metric=metric,sign='optimized_minus_reference; negative=faster',scope='plain_VM_Invoke',**ci(delta)))
  for name in ['P_only','A_plus_P','P_plus_C','A_plus_P_plus_C']:
   effects.append(dict(contract=contract,contrast=name,metric='invoke_ns',n=0,status='blocked_missing_pb_source'))
  for metric in measures:
   delta=[data[i,1,1][metric]-data[i,1,0][metric]-data[i,0,1][metric]+data[i,0,0][metric] for i in rounds]
   interactions.append(dict(contract=contract,interaction='A_x_C_at_P0',metric=metric,formula='t101-t100-t001+t000',sign='positive=antagonistic relative to additive latency changes',**ci(delta)))
  for name in ['A_x_P','P_x_C','A_x_P_x_C']:interactions.append(dict(contract=contract,interaction=name,n=0,status='blocked_missing_pb_source'))
 csvwrite(ROOT/'summary.csv',summary);csvwrite(ROOT/'paired_effects.csv',effects);csvwrite(ROOT/'interactions.csv',interactions);csvwrite(ROOT/'correctness.csv',correctness);csvwrite(ROOT/'ppt_data.csv',ppt)
 csvwrite(ROOT/'error_paths.csv',error_rows)
 lines=['# 三合约 pilot：完整 VM Invoke（ms）','','单线程 VM + mock TxSimContext，包含同步 fresh 创建、业务和关闭；不是节点延迟。40 次/有效组，单批探索性结果。P=1 缺可恢复源码。','', '| A | P | C | compute Median / P95 | ERC721 Median / P95 | fact Median / P95 |','|---|---|---|---|---|---|']
 for a in (0,1):
  for p in (0,1):
   for c in (0,1):
    cells=[]
    for contract in ['compute','erc721','fact']:
     r=next(v for v in ppt if v['contract']==contract and v['variant']==f'{a}{p}{c}')
     cells.append('blocked（PB 源码缺失）' if p else f"{r['median_ms']:.3f} / {r['p95_ms']:.3f}"+('（未通过）' if r['status']!='measured' else ''))
    lines.append('| '+' | '.join(map(str,[a,p,c]+cells))+' |')
 (ROOT/'PPT.md').write_text('\n'.join(lines)+'\n')
 costs=[]
 for path in (ROOT/'template-cost').glob('*.jsonl'):
  rs=readrows(path);v=[r['precompute_ns'] for r in rs if r['kind']=='template_sample'];memory=next(r for r in rs if r['kind']=='template_memory')
  costs.append(dict(label=path.stem,**ci(v),**{k:v for k,v in memory.items() if k not in ['kind','label']}))
 csvwrite(ROOT/'template_cost.csv',costs)
 print('plain',len(plain),'probe',len(probe),'correctness',[(r['contract'],r['A'],r['C'],r['status']) for r in correctness if r['P']==0])
if __name__=='__main__':main()
