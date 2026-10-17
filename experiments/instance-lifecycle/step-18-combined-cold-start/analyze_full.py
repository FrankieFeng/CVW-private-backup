"""Full 2x2x2 within-round comparisons; previous four-cell pilot stays separate."""
import csv,json,sys,math,statistics,itertools
from pathlib import Path
import pipeline as p
R=p.ROOT;D=R/'full-pilot'
sys.path.insert(0,str(p.EXPERIMENTS/'step-15-copy-attribution'))
from common import csvwrite,stats
cells=list(itertools.product(range(2),repeat=3))
def load(path):return [json.loads(l) for l in path.read_text().splitlines()]
def stat(v):return stats(v,seed=181802,block=5,reps=4000)
def same(a,b,keys):return all(a.get(k)==b.get(k) for k in keys)
def main():
 raw=[]
 for mode in ['plain','probe']:
  for path in (D/mode).glob('*.jsonl'):
   for r in load(path):
    if r['kind']=='sample':r['batch']='full-'+mode;r['invoke_minus_s3_ns']=r['invoke_ns']-r['s3_ns'];raw.append(r)
 csvwrite(D/'samples.csv',raw)
 summary=[];effects=[];interactions=[];correctness=[];sections=[];ppt=[];errors=[]
 metrics=['s1_ns','start_ns','s2_ns','s3_ns','invoke_ns','copy_ns','invoke_minus_s3_ns']
 semantic=['result','result_code','message','writes_sha256','events','special','cross_calls']
 gas=['registry_gas','native_business_gas','native_init_and_setgas_gas']
 manifest=json.loads((R/'manifest-full.json').read_text())
 for contract in p.CONTRACTS:
  by={};diag={}
  for r in raw:
   if r['contract']==contract:(by if r['mode']=='plain' else diag)[r['sample'],r['A'],r['P'],r['C']]=r
  rounds=sorted({k[0] for k in by});assert len(by)==8*len(rounds)==320
  assert len({v['instance_id'] for v in by.values()})==len(by)
  checks=[v for path in (D/'validation').glob(contract+'-p*-checks.jsonl') for v in load(path)]
  stages=[]
  for root in [R/'validation',D/'validation']:
   for path in root.glob(contract+'-a*p*-plain.jsonl'):stages+=load(path)
  for a,pv,c in cells:
   rs=[by[i,a,pv,c] for i in rounds]
   label=f'{contract}-a{a}p{pv}-plain';s=next(v for v in manifest if v['label']==label)
   # Check preserved sections separately for each final logical binary.
   x={k:b for k,b,_ in p.old.sections(Path(s['paths']['original']).read_bytes())};y={k:b for k,b,_ in p.old.sections(Path(s['paths']['nodata']).read_bytes())};assert {k:b for k,b in x.items() if k!=11}==y
   if c==0:
    for k,name in [(3,'Function'),(4,'Table'),(6,'Global'),(9,'Element'),(10,'Code')]:sections.append(dict(label=label,section=name,original_sha256=p.sha(x[k]),nodata_sha256=p.sha(y[k]),equal=True))
   ck=next(v for v in checks if (v['A'],v['P'],v['C'])==(a,pv,c));peer=next(v for v in checks if (v['A'],v['P'],v['C'])==(a,pv,1-c))
   stage=next(v for v in stages if v['label']==label and v['enabled']==bool(c));ss=stage['stages']
   functional=all(r['result_code']==0 and r['expected_output'] and same(r,by[i,0,0,0],semantic) for i,r in zip(rounds,rs))
   copy_equal=all(same(r,by[i,a,pv,1-c],semantic+gas) for i,r in zip(rounds,rs))
   s1=ck['s1_checks']>0 and ck['s1_mismatches']==0 and all(v['s1_memory_equal'] for v in ss if v['stage']=='S1')
   globals_equal=all(v['globals_table_size_equal'] for v in ss if v['stage']=='S1')
   isolated=ck['fresh_memory_isolation'] and stage['fresh_memory_globals_isolation'];table_null=all(v['table_nullness_mismatches']==0 for v in ss)
   guest=ck.get('guest_error');gp=peer.get('guest_error');guest_ok=bool(guest and gp) and guest['result_code']!=0 and same(guest,gp,semantic+['registry_gas','native_business_gas'])
   host_equal=same(ck['exception'],peer['exception'],semantic+['registry_gas','native_business_gas'])
   base_check=next(v for v in checks if (v['A'],v['P'],v['C'])==(0,0,0))
   guest_semantic=bool(guest and base_check.get('guest_error')) and same(guest,base_check['guest_error'],semantic)
   if guest: guest_ok=guest_ok and guest_semantic
   tested=functional and copy_equal and s1 and globals_equal and isolated and table_null and ck['template_immutable'] and host_equal and (guest_ok or contract=='compute')
   correction=dict(contract=contract,A=a,P=pv,C=c,status='tested_scope_pass' if tested else 'unusable_or_incomplete',safe='not_certified',business_results_writes_events_equal_to_000=functional,copy_same_binary_gas_equal=copy_equal,S1_memory=s1,globals_equal=globals_equal,fresh_memory_globals_isolation=isolated,template_immutable=ck['template_immutable'],table_nullness=table_null,table_static_mapping='preserved within each final logical WASM',table_function_identity='not_tested',cross_contract='not_tested',guest_error='tested_pass' if guest_ok else 'not_tested',guest_error_result_equal_to_000=guest_semantic if guest else 'not_tested',host_missing_export='same API code0/empty result; error logged; not guest failure proof',all_OOG_traps='not_tested',registry_gas=sorted({v['registry_gas'] for v in rs}),native_business_gas=sorted({v['native_business_gas'] for v in rs}),native_init_and_setgas_gas=sorted({v['native_init_and_setgas_gas'] for v in rs}),cross_binary_gas_acceptability='not_certified')
   correctness.append(correction)
   errors.append(dict(contract=contract,A=a,P=pv,C=c,guest_error_code=guest.get('result_code') if guest else None,guest_error_message=guest.get('message') if guest else None,guest_error_copy_equal=guest_ok if guest else 'not_tested',host_missing_export_code=ck['exception']['result_code'],host_missing_export_copy_equal=host_equal))
   for metric in metrics:summary.append(dict(contract=contract,A=a,P=pv,C=c,scope='plain_VM_Invoke',metric=metric,status='measured' if tested else 'unusable_or_incomplete',**stat([v[metric] for v in rs])))
   for metric in ['a_ns','b1_ns','clock_uncertainty_ns']:
    vs=[diag[i,a,pv,c][metric] for i in rounds];summary.append(dict(contract=contract,A=a,P=pv,C=c,scope='instrumented_diagnostic_only',metric=metric,status='diagnostic',**stat(vs)))
   d=[by[i,a,pv,c]['invoke_ns']-by[i,0,0,0]['invoke_ns'] for i in rounds];st=stat([v['invoke_ns'] for v in rs]);ds=stat(d)
   ppt.append(dict(contract=contract,A=a,P=pv,C=c,status='measured' if tested else 'unusable',median_ms=st['median_ns']/1e6,p95_ms=st['p95_ns']/1e6,paired_saving_ms=-ds['median_ns']/1e6,saving_ci_low_ms=-ds['ci95_high_ns']/1e6,saving_ci_high_ms=-ds['ci95_low_ns']/1e6,n=len(rs)))
  contrasts={''.join(map(str,cell))+'_vs_000':(cell,(0,0,0)) for cell in cells if cell!=(0,0,0)}
  contrasts.update(A_on_C=((1,0,1),(0,0,1)),P_on_C=((0,1,1),(0,0,1)),AP_on_C=((1,1,1),(0,0,1)),P_on_AC=((1,1,1),(1,0,1)),A_on_PC=((1,1,1),(0,1,1)),C_on_AP=((1,1,1),(1,1,0)))
  for name,(opt,ref) in contrasts.items():
   for metric in metrics:
    d=[by[(i,)+opt][metric]-by[(i,)+ref][metric] for i in rounds];effects.append(dict(contract=contract,contrast=name,metric=metric,sign='optimized-minus-reference; negative=faster',**stat(d)))
  def interaction(name,terms):
   for metric in metrics:interactions.append(dict(contract=contract,interaction=name,metric=metric,sign='positive=antagonistic latency interaction',**stat([sum(sign*by[(i,)+cell][metric] for cell,sign in terms) for i in rounds])))
  for axis0,axis1,other,name in [(0,1,2,'A_x_P'),(0,2,1,'A_x_C'),(1,2,0,'P_x_C')]:
   for fixed in [0,1]:
    terms=[]
    for b0,b1 in itertools.product(range(2),repeat=2):
     cell=[0,0,0];cell[axis0]=b0;cell[axis1]=b1;cell[other]=fixed;terms.append((tuple(cell),1 if b0==b1 else -1))
    interaction(name+'_other'+str(fixed),terms)
  interaction('A_x_P_x_C',[(cell,(-1)**(3-sum(cell))) for cell in cells])
 for name,rs in [('summary',summary),('paired_effects',effects),('interactions',interactions),('correctness',correctness),('static_sections',sections),('ppt_data',ppt),('error_paths',errors)]:csvwrite(D/(name+'.csv'),rs)
 variants=[v for v in csv.DictReader((R/'variants.csv').open()) if v['P']=='0']+list(csv.DictReader((R/'recovered-pb/built_variants.csv').open()));csvwrite(D/'variants.csv',variants)
 costs=[]
 for root in [D/'template-cost']:
  for path in root.glob('*.jsonl'):
   rs=load(path);sample=[v['precompute_ns'] for v in rs if v['kind']=='template_sample'];mem=next(v for v in rs if v['kind']=='template_memory');costs.append(dict(label=path.stem,**stat(sample),**{k:v for k,v in mem.items() if k not in ['kind','label']}))
 csvwrite(D/'template_cost.csv',costs)
 lines=['# 完整8组消融：三合约pilot','','单批每组40次；单线程真实VM Invoke + mock TxSimContext，包含同步fresh创建、业务及关闭。数字为Median / P95，单位ms。','', '|A|P|C|compute|ERC721|fact|','|---|---|---|---|---|---|']
 for cell in cells:
  vals=[next(v for v in ppt if v['contract']==c and (v['A'],v['P'],v['C'])==cell) for c in p.CONTRACTS];lines.append('|'+ '|'.join([str(b) for b in cell]+[f"{v['median_ms']:.3f} / {v['p95_ms']:.3f}"+('（不可用）' if v['status']!='measured' else '') for v in vals])+'|')
 lines+=['','P为恢复的历史GetBatchState API删除补丁，仅适用于不使用该API的合约。所有组尚未认证生产安全；Table真实函数身份、跨合约和全部OOG/trap未验证。旧4组pilot与本批不混合统计。']
 (D/'PPT.md').write_text('\n'.join(lines)+'\n')
 print('full matrix samples',len(raw),'tested scopes',sum(v['status']=='tested_scope_pass' for v in correctness),'/',len(correctness),flush=True)
if __name__=='__main__':main()
