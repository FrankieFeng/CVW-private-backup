from pathlib import Path
import csv,json,hashlib,collections,subprocess
P=Path(__file__).resolve().parents[1];OLD=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-32-all-contracts-acopy')
def read(p):return list(csv.DictReader(p.open()))
def write(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r));f=p.open('w',newline='');w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rs);f.close()
cases=json.loads((P/'inputs/cases.json').read_text());cm={c['case']:c for c in cases};vs=json.loads((P/'inputs/variants.json').read_text());inv=read(P/'CONTRACT_INVENTORY.csv');new=read(P/'PAIRED_EFFECTS.csv');old=read(OLD/'PAIRED_EFFECTS.csv');summary=read(P/'SUMMARY.csv');osum=read(OLD/'SUMMARY.csv');blocks=[json.loads(f.read_text())for f in(P/'raw_logs').glob('*-block.json')];N=collections.Counter(b['case']for b in blocks if b['phase']=='formal');pref={b['case']for b in blocks if b['phase']=='preflight'}
for r in inv:
 if r.get('case'):
  r['status']='completed'if N[r['case']]==30 else'partial'if N[r['case']]else'preflight_passed'if r['case']in pref else'pending';r['fixture_status']=r['status'];r['A_build_status']='frozen_and_preflight_validated'if r['case']in pref else r['A_build_status'];r['Copy_build_status']='preflight_passed'if r['case']in pref else r['Copy_build_status'];r['formal_blocks']=N[r['case']]
write(P/'CONTRACT_INVENTORY.csv',inv)
methods={'bigNumCal':('compute','bigNumCal'),'hashCal':('compute','hashCal'),'normalCal':('compute','normalCal'),'fact':('fact','saveAndFindByFileHash'),'erc721':('erc721','mint'),'buyNow':('exchange','buyNow')};matrix=[]
for origin,rs,sums,sha,branch in [('Step32',old,osum,'7eccc36e','experiment/step32-all-contracts-acopy-matrix'),('Step33',new,summary,json.loads((P/'audit/SOURCE_SNAPSHOT.json').read_text())['source_snapshot_commit'],'experiment/step33-full-contract-coverage')]:
 for case in sorted({r['case']for r in rs}):
  c,m=methods[case]if origin=='Step32'else(cm[case]['contract'],cm[case]['method']);effects={r['effect']:r for r in rs if r['case']==case};gr={r['group']:r for r in sums if r['case']==case and r['metric']=='invoke_ns'}
  d=dict(contract=c,method=m,source=origin,branch=branch,commit=sha,family='Step18-P0-plain',N_per_group=gr['G0']['N'],batches=gr['G0']['batches'],status='completed'if int(gr['G0']['N'])==30 else'partial',exception_rollback='not_tested',table_identity='not_tested')
  for g in ['G0','G1','G2','G3']:
   a=vs[c+'-'+g];d[g+'_wasm_sha256']=a['sha'];d[g+'_wasm_path']=a['path']
   for metric in ['median_ms','p95_ms','mean_ms']:d[g+'_invoke_'+metric]=gr[g][metric]
  for name,e in effects.items():
   for field in ['paired_saving_median_ms','ci95_low_ms','ci95_high_ms','positive_fraction','batch_medians_ms','all_batches_positive']:d[name+'_'+field]=e[field]
  eligible=[name for name in ['A','Copy','A+Copy']if float(effects[name]['ci95_low_ms'])>0 and effects[name]['all_batches_positive']=='True'];d['supported_positive']=','.join(eligible)or'insufficient_evidence';d['recommendation']='candidate_requires_node_validation'if eligible else'needs_more_evidence';matrix.append(d)
for r in inv:
 if r['status']in ['blocked','auxiliary_not_performance']:matrix.append(dict(contract=r['contract'],method=r['method'],source='inventory_only',status=r['status'],reason=r['blocking_reason']))
write(P/'FULL_CONTRACT_MATRIX.csv',matrix)
# Long table keeps source explicit; old and new samples never concatenated.
write(P/'FULL_EFFECTS_WITH_PROVENANCE.csv',[dict(source=o,source_commit='7eccc36e'if o=='Step32'else'parent7eccc36e; build3',**r)for o,rs in [('Step32',old),('Step33',new)]for r in rs])
lines=['# 新增方法完整 Invoke 结果','', '单位ms；正配对节省表示优化更快。CI为直接整区块分层bootstrap，不能把单组中位数之差当配对效应。完整结果和来源见FULL_CONTRACT_MATRIX.csv。','', '|方法|G0 Median|G1 A|G2 Copy|G3 A+Copy|A节省 [95% CI]|Copy节省 [95% CI]|A+Copy节省 [95% CI]|N/组|','|---|---:|---:|---:|---:|---|---|---|---:|']
for d in matrix:
 if d['source']!='Step33':continue
 vals=[f"{d[g+'_invoke_median_ms'] and float(d[g+'_invoke_median_ms']):.3f}"for g in ['G0','G1','G2','G3']]
 ef=[f"{float(d[e+'_paired_saving_median_ms']):.3f} [{float(d[e+'_ci95_low_ms']):.3f}, {float(d[e+'_ci95_high_ms']):.3f}]"for e in ['A','Copy','A+Copy']]
 lines.append('|'+'.'.join([d['contract'],d['method']])+'|'+'|'.join(vals+ef+[d['N_per_group']])+'|')
lines+=['','已有Step32六方法仅引用，未重跑、未混合原始统计；本表新增方法在同一冻结构建家族内比较，绝对耗时不用于跨实验批次作因果推断。','', 'raw Interaction=G0-G1-G2+G3：正值表示抵消，负值表示额外协同。不是原请求早期误写的正协同；保留公式与Step32解释一致。', '', '异常/回滚与真实Table函数身份未覆盖，不宣称全面安全或生产/E2E收益。']
(P/'RESULTS.md').write_text('\n'.join(lines)+'\n')
print('REPORT',len(matrix),'rows; completed new methods',sum(v==30 for v in N.values()),'formal blocks',sum(N.values()))
