from report import *
mat=[r for r in matrix if r['source']in['Step32','Step33']];out=[]
for d in mat:
 stable_names=[e for e in ['A','Copy','A+Copy','A_given_Copy','Copy_given_A']if float(d[e+'_ci95_low_ms'])>0 and d[e+'_all_batches_positive']=='True']
 if 'A+Copy'in stable_names and 'A_given_Copy'in stable_names and 'Copy_given_A'in stable_names:choice='A+Copy candidate; direct increment over both supported'
 elif 'A'in stable_names and float(d['Copy_given_A_ci95_high_ms'])<0:choice='A-only candidate; adding Copy worsened measured Invoke'
 elif 'A'in stable_names and 'Copy_given_A'not in stable_names:choice='A-only is a supported simpler candidate; A+Copy extra increment unconfirmed'
 elif 'Copy'in stable_names and 'A_given_Copy'not in stable_names:choice='Copy-only supported; A increment unconfirmed'
 elif 'A+Copy'in stable_names:choice='A+Copy vs Fresh supported; superiority to single options unconfirmed'
 else:choice='needs targeted diagnosis'
 out.append(dict(contract=d['contract'],method=d['method'],source=d['source'],commit=d['commit'],N_per_group=d['N_per_group'],supported_effects=','.join(stable_names),candidate=choice,production_safe='not_certified',e2e_benefit='not_tested_here'))
write(P/'METHOD_RECOMMENDATIONS.csv',out)
cs=[]
for c in sorted({r['contract']for r in out}):
 rs=[r for r in out if r['contract']==c];cs.append(dict(contract=c,methods_completed=len(rs),source_steps=','.join(sorted({r['source']for r in rs})),A_supported=sum('A'in r['supported_effects'].split(',')for r in rs),Copy_supported=sum('Copy'in r['supported_effects'].split(',')for r in rs),ACopy_supported=sum('A+Copy'in r['supported_effects'].split(',')for r in rs),dual_increment_supported=sum(r['candidate'].startswith('A+Copy candidate;')for r in rs),blocked_business_methods='callerAddress'if c=='identity'else'',scope='counts of method-specific evidence; not pooled statistics'))
write(P/'CONTRACT_RECOMMENDATIONS.csv',cs)
with(P/'RESULTS.md').open('a')as f:
 f.write('\n## 合约层面矩阵与后续选择\n\n|合约|已完成业务方法|A跨批正向|Copy跨批正向|A+Copy跨批正向|A+Copy相对两单项增量均支持|\n|---|---:|---:|---:|---:|---:|\n')
 for r in cs:f.write('|'+r['contract']+'|'+'|'.join(str(r[k])for k in ['methods_completed','A_supported','Copy_supported','ACopy_supported','dual_increment_supported'])+'|\n')
 f.write('\n以上是保留各自来源的证据计数，不把Step32/33样本拼接。详见METHOD_RECOMMENDATIONS.csv。组合相对Fresh有效并不等于优于A-only：新增仅15/30方法的两个增量都获跨批支持；结合Step32为18/36。Step32 buyNow添加Copy到A反而慢8.000ms（直接配对95% CI −14.796至−1.980ms），优先A-only候选，组合仍需专项分析。bigNumCal现有Copy收益确认、A叠加增量不足；不能强称A+Copy最优。\n\nE2E候选优先取独立增量均支持且顺序分层一致的代表入口，如identity.address、itinerary.save、raffle.registerAll、ERC721.accountTokens；它们仍需真实节点生命周期安全准入与端到端新证据。本轮不启动节点。\n')
print('recommendations',len(out),'method rows',len(cs),'contracts')
st=read(P/'STAGE_ATTRIBUTION.csv');sm={(r['case'],r['effect']):r for r in st};ranges={e:{m:[min(float(r[m])for r in st if r['effect']==e),max(float(r[m])for r in st if r['effect']==e)]for m in ['s0_s1_mean_saving_ms','s1_s2_mean_saving_ms']}for e in ['A','Copy']};inter=[]
for c in cm:
 a,co,ac=[sm[(c,e)]for e in ['A','Copy','A+Copy']];d=dict(case=c,N=a['N'])
 for m in ['invoke_mean_saving_ms','s0_s1_mean_saving_ms','s1_s2_mean_saving_ms','s2_s3_mean_saving_ms','close_mean_saving_ms','unattributed_mean_saving_ms']:d['interaction_'+m]=float(a[m])+float(co[m])-float(ac[m])
 inter.append(d)
write(P/'STAGE_INTERACTION_MEANS.csv',inter)
with(P/'RESULTS.md').open('a')as f:
 f.write('\n## 阶段与资源判断\n\n新增30方法中，A-only有29、Copy-only有13、A+Copy有30个入口满足CI下界>0且三批中位效应均正。A叠加Copy的直接增量30/30支持，Copy叠加A仅15/30支持；不能将整体改善等同于组合总是优于两种单项。\n\n同区块均值分解显示A主要集中S1→S2，Copy主要集中S0→S1（STAGE_ATTRIBUTION.csv保留逐方法完整结果），不能把这解释成未观测的GC/cache/native机制。ownerOf的交互均值0.318ms，其中S0→S1约0.236ms、S1→S2约0.049ms，来自同30区块的线性分解；这只定位窗口，不证明具体宿主操作根因。\n\nTEMPLATE_CAPACITY.csv记录每个实际最终WASM的Image字节与Ranges；不包含native编译Module、NoData/Go容器的全部容量，不能把Image大小当总RSS。A使Image变大这一点直接可核实，进程RSS不足以单独归因给A。资源峰值529.3MiB、109线程，Go heap边界采样峰值61.1MiB；正式9360 Instance和3600 Store scope创建/关闭平衡、in-flight及managed pending归零。没有观察到本轮守卫/回收异常，但这不是长期/native全资源安全证明。\n')
