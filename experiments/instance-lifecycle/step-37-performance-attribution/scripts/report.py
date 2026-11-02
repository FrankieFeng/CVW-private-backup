"""Generate Step37 analysis reports only. Reads Step36 and Step37, no benchmarks."""
from pathlib import Path
import csv,json,statistics as st,collections
P=Path(__file__).resolve().parents[1];S=P.parent/'step-36-e2e-copy-acopy';csv.field_size_limit(32*1024*1024)
def read(n):return list(csv.DictReader((P/n).open()))
def save(n,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def doc(n,s):(P/n).write_text(s.strip()+'\n')
def f(v):return f'{float(v):.3f}'
E=read('PAIRED_EFFECTS.csv');G=read('GROUP_STATISTICS.csv');T=read('RECOMPUTED_TRANSACTIONS.csv');C=read('METHOD_CLASSIFICATION.csv');I=read('INTERACTION_ANALYSIS.csv');L=read('STATIC_LAYOUT.csv');J=json.loads((P/'audit/reanalysis.json').read_text());sel=read('CASE_SELECTION.csv');lookup={(e['case'],e['left'],e['right'],e['metric']):e for e in E};stats={(x['case'],x['group'],x['metric']):x for x in G}
def effect(c,l,r,m='e2e_ms'):return lookup[c,l,r,m]
def desc(e):return f"{f(e['paired_saving_median'])} [{f(e['ci95_low'])}, {f(e['ci95_high'])}]"
for c in C:
 name=c['case']
 for g in ['G0','G1','G2','G3']:
  z=stats[name,g,'e2e_ms']
  for k in ['mean','p50','p95']:c[g+'_'+k+'_ms']=z[k]
  c[g+'_pooled_tps']=effect(name,'G0','G1')['left_pooled_tps']if g=='G0'else effect(name,'G0',g)['right_pooled_tps']
save('METHOD_CLASSIFICATION.csv',C)
rows=['| 方法 | N/组 | Fresh→Copy节省 | Fresh→A-only节省 | Fresh→A+Copy节省 | A叠加Copy节省 |','|---|---:|---:|---:|---:|---:|']
for x in C:
 c=x['case'];rows.append('| '+c.replace('_','.',1)+' | '+x['N_per_group']+' | '+' | '.join(desc(effect(c,l,r))for l,r in [('G0','G1'),('G0','G3'),('G0','G2'),('G1','G2')])+' |')
header='所有“节省”定义左组耗时−右组耗时，正值更快。下表ms，[ ]为未经多重校正的探索性95%层级bootstrap CI；表头是优化方向，不是反向减法。全部Holm结果均不显著，不能据此说无效。'
doc('ALL_METHODS.md','# 37方法完整对照\n\n'+header+'\n\n'+'\n'.join(rows)+'\n\nPAIRED_EFFECTS.csv还含A-only→A+Copy、Mean/P50/P95、逐对相对改善%、正向比例、批次/顺序、TPS。INTERACTION_ANALYSIS.csv保留每block直接交互，未使用独立中位数相减。')
# Per-case measured stage table, all group columns required.
ph=read('STAGE_BREAKDOWN.csv');staged={}
for c in [x['case']for x in C]:
 a=['| 阶段（ms，中位数） | Fresh | Copy | A-only | A+Copy |','|---|---:|---:|---:|---:|']
 for name in ['Store preparation','WASI/import preparation','NewInstance','Copy','_start','S0_to_S1','S1_to_S2','S2_to_S3','CallMethod','exportFunc.Call','Close','Owner Invoke','Factory Invoke','VM external remainder','SDK E2E']:
  vals=[]
  for g in ['G0','G1','G3','G2']:
   r=next(x for x in ph if x['case']==c and x['group']==g and x['phase']==name);vals.append(f(r['p50_ms'])if r['p50_ms']!='not_measured'else'not_measured')
  a.append('| '+name+' | '+' | '.join(vals)+' |')
 staged[c]='\n'.join(a)
caseids=list(dict.fromkeys(['compute_bigNumCal','compute_hashCal','compute_normalCal','fact_saveAndFindByFileHash','erc721_mint','exchange_buyNow']+[x['case']for x in sel if x['case']!='none']))
mechanisms={
 'compute_bigNumCal':('大整数计算；CallMethod包含guest math/big与参数/host辅助，不能把全部当初始化','本轮无Reuse组，不能用它判断历史Reuse/Fresh异常'),
 'compute_hashCal':('hash业务与runtime准备共同构成；固定同源输入，没有修改循环来增收益','E2E局部正向只是未经多重校正的信号'),
 'compute_normalCal':('长计算窗口；CallMethod占Owner Invoke约92%，初始化只占其中一部分','本轮没有独立exportFunc.Call落盘，也没有Reuse组，不能宣称再现或推翻Step27 guest差异'),
 'fact_saveAndFindByFileHash':('真实保存和查询；host状态调用嵌在CallMethod','读写/编码的独立成本未记录，不据整体时间认定PB/JSON根因'),
 'erc721_mint':('真实状态更新与事件；Copy的VM变化和E2E方向可能不同','负向E2E三批信号保留；未证实Copy引起缓存变坏/GC或提交等待增加'),
 'exchange_buyNow':('根CallMethod包含identity三次、ERC721三次真实下游及其Fresh生命周期','7实例不重叠初始化窗口可相加，7个完整Invoke不可相加；Step29夹具clone结果不能直接当本轮真实节点根因'),
 'identity_addWriteList':('独立白名单业务读写，A-only局部有利，组合未必进一步有利','不能由此得出所有identity方法都适合A-only'),
 'identity_alterAdminAddress':('改管理员后当前签名者权限变化，每批只有1次合法目标调用','N=3；宽CI典型低功效，不是最有代表性的稳定无效结果'),
 'erc721_symbol':('读取真实symbol，本轮仍用InvokeContract提交而非Query-only计时','短业务可见初始化占比，但节点前后窗口与调度波动仍在')}
parts=['# 典型方法：数据自动筛选与源码约束\n\nCASE_SELECTION.csv保存筛选条件。Copy受益/退化等标签均为未经校正探索性CI分类。没有任何方法满足“A+Copy对其余三组全部CI全正”，因此该类别明确none，不强行挑赢家。所有结论分A/B/C/D。']
for c in caseids:
 a=[x for x in T if x['case']==c and x['group']=='G0'];share=st.median(float(x['callmethod_ms'])/float(x['vm_inner_ms'])for x in a);source=mechanisms.get(c,('见冻结业务源码和源码调用链；保留全部真实业务','缺少针对该方法的guest内部观测，无法唯一归因'))
 table=['| 直接对照 | E2E节省 ms [95%CI] | Owner Invoke节省 | _start节省 | TPS增量 |','|---|---:|---:|---:|---:|']
 for l,r in [('G0','G1'),('G0','G3'),('G0','G2'),('G1','G2'),('G3','G2')]:
  e=effect(c,l,r);table.append('| '+l+'→'+r+' | '+desc(e)+' | '+desc(effect(c,l,r,'vm_inner_ms'))+' | '+desc(effect(c,l,r,'start_ms'))+' | '+f(e['tps_gain'])+' |')
 parts.append('\n## '+c.replace('_','.',1)+'\n\n'+staged[c]+'\n\n'+'\n'.join(table)+f'\n\n1. **主要耗时（A/B）**：{source[0]}。Fresh CallMethod/Owner Invoke逐交易比率中位{share*100:.1f}%；这是窗口占比，不是某一guest函数的CPU占比。\n2. **Copy节省什么（A/B）**：对同一block直接比较S0→S1、Owner和E2E，表列测得的效应；移除Data Section、恢复约5万范围已由源码/静态产物确认。\n3. **Copy新增成本（A/C）**：restore计时包含身份检查、Memory获取及范围循环；它不是纯memcpy。模板一次性容量/构建另计，不算每笔重复准备。\n4. **A改变什么（A/C）**：同源padding使init_bloc目标59页，关联arena gap路径；没有跳过_start、改Guest业务或修改Gas。实际Store/WASI时间未分离。\n5. **组合解释（B/C）**：表中G1→G2与G3→G2为直接配对；可测_start收益不保证总窗口收益。交互见INTERACTION_ANALYSIS，不由两个Median相加。\n6. **直接证据（A/B）**：原始TxID、阶段和四组Gas/状态核对均保存；样本与批次差异在BATCH_ANALYSIS。Holm222项校正无显著，不能宣称已确定该方法受益。\n7. **未证实解释（C/D）**：{source[1]}。缓存/页fault、guestGC、hash/clone、WASI分配都需额外独立观测。')
doc('CASE_STUDIES.md','\n'.join(parts))
# E2E attribution all methods: compare measured effects, never invent missing stage.
a=['| 方法 | Copy Owner节省 | Copy E2E节省 | A+Copy Owner节省 | A+Copy E2E节省 | Fresh CallMethod/Owner % |','|---|---:|---:|---:|---:|---:|'];heavy=[]
for z in C:
 c=z['case'];rs=[x for x in T if x['case']==c and x['group']=='G0'];share=st.median(float(x['callmethod_ms'])/float(x['vm_inner_ms'])for x in rs)
 if share>=.5:heavy.append((c,share))
 a.append('| '+c.replace('_','.',1)+' | '+' | '.join(desc(effect(c,'G0',g,m))for g in ['G1','G2']for m in ['vm_inner_ms','e2e_ms'])+' | '+f(share*100)+' |')
doc('E2E_ATTRIBUTION.md','# VM收益与客户端收益\n\n'+'\n'.join(a)+'\n\n## 分解表\n\n'+staged['compute_hashCal']+'\n\n全部37方法×4组×阶段在STAGE_BREAKDOWN.csv；典型方法逐表在CASE_STUDIES.md。Store、WASI/import及VM外残余一律not_measured，不用相邻嵌套阶段的Median相减填表。S1→S2由同一次已记录s2_ns−s1_ns得到，不等同start_ns。\n\n**A**：1728交易对应1872根Invoke，144笔各2次（accountTokens、queryHistory、saveAndQueryHistory）；每笔VM成本取全部根执行。buyNow每笔根/子共7个Instance，root已含子Invoke，不将完整窗口重复累计。\n\n**B**：Copy的Owner Invoke探索性CI全正6/37，客户端3/37；A叠加Copy的_start CI全正37/37，Owner9/37，客户端1/37。不能把这种数量差当成精确“收益传递率”。每方法配对效应和CI才是实际可比较结果。\n\n**A/B**：Fresh CallMethod超过一半Owner时间的方法为'+', '.join(c.replace('_','.',1)+f'({v*100:.1f}%)'for c,v in heavy)+'。对这些方法，单独优化根实例初始化可消除的总耗时有限；buyNow的CallMethod内部还包含六次下游实例化，不能称其完全没有初始化瓶颈。\n\n**C**：“VM省1ms，其他串行窗口不变时E2E也省1ms”只是条件恒等，不是本轮估计系数。节点调度/PutBlock等可能波动；既有NODE_STAGES.csv提供同节点单调RPC/PutBlock窗，但没有消除批次/顺序混杂。E2E/VM配对中位数不能相除冒充因果传递比例。\n\n**A/B**：TPS为每批已确认提交数/首SDK开始至末同步返回的真实窗口。P50比较不是窗口均值，少数慢样本与循环开销会改变TPS；同一窗口TPS与实际总时长恒等不矛盾。比如mint的Copy Owner配对中位更快而E2E及TPS较差，定位到“VM之外或未细分部分抵消”的观察，不能唯一归到共识/GC。\n\n**C/D**：WASI/import是否新瓶颈、Copy是否改变后续内存访问局部性、资源状态是否导致反向效果，尚无独立证据。Store独立化是四组共同条件，没有净额外成本对照。资源按进程关联RESOURCE_ANALYSIS.csv；3批运行顺序与环境混杂不能由相关性排除。')
# Phase data for real buyNow, sum only disjoint initialization intervals.
vm=list(csv.DictReader((S/'VM_EVENTS.csv').open()));buy=[]
for t in T:
 if t['case']!='exchange_buyNow':continue
 ev=[e for e in vm if e['run']==t['run']and e['tx_id']==t['tx_id']];assert len(ev)==7
 row={k:t[k]for k in ['run','case','group','batch','slot','tx_id']};row['instances']=len(ev)
 for name,k in [('all7_newinstance_ms','newinstance_ns'),('all7_copy_ms','copy_ns'),('all7_start_ms','start_ns'),('all7_close_ms','close_ns')]:row[name]=sum(float(e[k]or 0)for e in ev)/1e6
 row['root_invoke_ms']=t['vm_inner_ms'];row['root_callmethod_ms']=t['callmethod_ms'];buy.append(row)
save('BUY_NOW_PHASES.csv',buy)
positive=[x['case']for x in C if x['copy_exploratory_class']=='CI_positive'];negative=[x['case']for x in C if x['copy_exploratory_class']=='CI_negative'];apos=[x['case']for x in C if x['A_exploratory_class']=='CI_positive']
readme=f'''# Step-37：全合约性能归因与源码机制分析

已完成只读审计和独立复算。基线CVW abc2ce35、节点c28bfa8，独立分支experiment/step37-performance-attribution。没有节点、编译、性能实验、新Copy/A实现或PPT；历史样本保持不变。

## 数据审计结果（A）

8业务合约、37方法、111个四组匹配block（同batch+slot），444正式窗口、1728交易、1872根执行。8779项SHA校验通过，其中一个Git忽略packaged so只在原Step36工作树存在，已只读取回校验，不将其误认为实际加载库。独立从raw case/日志复核1728逐笔时长、阶段、TxID及提交receipt，111个四组Gas/返回/读写集/事件/已写键状态按原规范化规则一致。原始无效raffle仍保留、不混入主数据。

925项原配对CI/中位节省/正向比例独立复算，最大数值差0。新增五项对照与直接两因素交互、三批/顺序及TPS分析。原报告不改。完整37行见ALL_METHODS.md，完整字段见CSV。

## 统计结论（B）

原探索性Copy正向CI方法：{', '.join(positive)}；反向CI方法：{', '.join(negative)}。其余CI跨零，不等于没有效果。

以3批为独立单位作双侧符号翻转，五种主对照+交互共222项Holm校正：原始p最低0.25，校正后全部不显著。只有3批，可交换/符号对称亦是条件假设，因此既不能确认普遍受益，也不能确认普遍退化；原局部信号保留为探索性。

## 必答问题

1. **哪些真正受益于Copy？（B）** 按原探索性CI是上述3方法；按本轮保守聚类+Holm标准，没有方法达到确认性统计门槛。不能把“不足以确认”改写为所有方法无效。
2. **哪些Copy增加成本？（B）** ERC721.mint E2E三批负向、原CI全负；但Owner窗口反向情况不同，不能认定restore自身导致额外E2E成本。其他反向中位数亦全部保留。
3. **A改变什么？（A/C）** Go1.24.1同源全局padding重新链接，将init_bloc置59页，针对4MiB arena对齐gap的memFree/memclr路径；不提前执行Runtime，不是128页配置，也不裁剪PB。具体本轮分配调用计数未测。
4. **为何A+Copy不一定更好？（A/B/C）** _start改善同时伴随不同准备/执行/提交窗口；A增加初始Memory/模板容量，却仅增加几百B文件/Copy数据。不能用WASM大幅变大作解释。直接交互/阶段证明非简单加性，尚无唯一负收益机制。
5. **哪些瓶颈已不只在初始化？（A/B）** bigNumCal、normalCal、buyNow、callerAddress的CallMethod占Owner中位比率过半。buyNow的CallMethod含子初始化，不能一概说初始化不重要；Store/WASI分窗缺失仍待测。
6. **Store独立化净成本？** not_measured。所有组相同Store协议，没有同条件共享Store对照或独立NewStore窗，不能用历史批次相减。
7. **Copy明显多余工作？（A/C）** restore约5万区间循环、混合区间内约0.31～0.36MB零字节；更小字节与更少循环有取舍。另有runtime整WASM副本和Invoke/prepare重复SHA，但不在restore内；源码能证明存在，未证明是性能主因。
8. **Renew值得做核心方向？（D）** 值得先定义/调研，尚无完整Instance Renew实现证据。Memory.Reset和Manager.Reset均不等价Fresh；不能直接恢复执行过的Instance来绕过问题。
9. **最值得研究三个问题？** 区间粒度/额外零gap复制的权衡；热路径不可变字节码验证/缓存成本；独立Store下WASI/import准备的可测成本。COW/全状态Renew暂非最小主线。
10. **下一轮具体函数/假设？** step35_static.prepareStaticMemory/restore验证合并区间假设；step35_node.runtime/Invoke/prepare分离clone/SHA再考虑摊销；NewStore/Finalize/GenerateImportObject/GetImports分离计时。只建议，不在本轮修改。

## 交付导航

- METHOD_CLASSIFICATION.csv、ALL_METHODS.md：37方法、四组P50/P95/Mean/TPS及原CI/校正分类。
- PAIRED_EFFECTS.csv：五对照、相对节省=逐对百分比中位数、CI、正向率、三批及TPS。
- BATCH_ANALYSIS.csv、INTERACTION_ANALYSIS.csv：批次/顺序与交互，正saving_synergy才表示协同。
- SOURCE_TRACE.md、COPY_MECHANISM.md、A_MECHANISM.md、GO_RUNTIME_ANALYSIS.md：实际调用链与机制。
- E2E_ATTRIBUTION.md、CASE_STUDIES.md、STAGE_BREAKDOWN.csv、BUY_NOW_PHASES.csv：阶段、负向案例和六子调用。
- STATIC_LAYOUT.csv、COPY_RANGE_SCENARIOS.csv：冻结布局及只算操作量的候选方案，不是基准结果。
- OPTIMIZATION_CANDIDATES.md、RENEW_RESEARCH.md、LIMITATIONS.md、NEXT_STEP.md：建议与证据空缺。

复算：`python3 scripts/analyze.py` → `python3 scripts/layout.py` → `python3 scripts/verify_records.py` → `python3 scripts/report.py` → `python3 scripts/supplement.py` → `python3 scripts/validate.py`。仅写Step37派生数据；需要本机原Step36未入Git的packaged so作清单校验，无需启动native。

A=源码/观测直接证明，B=数据支持机制未唯一，C=源码合理假设，D=未验证研究设想。没有任何静态字节量被换算为未测毫秒。

研究建议：优先验证可解释、可普遍复用的初始化机制，不追求所有方法平均数都变好。本轮结束于报告，不自动启动Step38/39。
'''
doc('README.md',readme)
print('reports written; cases',len(caseids),'methods',len(C),'buyNow rows',len(buy))
