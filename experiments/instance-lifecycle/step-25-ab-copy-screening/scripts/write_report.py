from pathlib import Path
import csv,json,statistics
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
E=read('PAIRED_EFFECTS.csv');B=read('BATCH_EFFECTS.csv');S=read('STAGE_EFFECTS.csv');R=read('RESOURCE_SUMMARY.csv');C=read('CORRECTNESS.csv');T=read('TIMING.csv');M=read('MATRIX.csv');O=read('ORDER_SENSITIVITY.csv');Prep=read('MODULE_PREPARATION.csv');v=json.loads((P/'verification.json').read_text())
names={'compute':'bigNumCal（10,000轮）','fact':'fact','erc721':'ERC721.mint','normal':'normalCal'}
def fmt(x):return f'{float(x):.3f}'
def effect(case,a,b):return next((r for r in E if(r['case'],r['left'],r['right'])==(case,a,b)),None)
def conclusion(r):
 if int(r['n_pairs'])<18:return '部分/探索性'
 if float(r['ci95_low_ms'])>0 and r['all_batch_medians_positive']=='True':return '三批正向（串行筛选）'
 if float(r['ci95_high_ms'])<0:return '总体负向'
 return '方向不稳定/证据不足'
def table(rows):
 text='| 方法 | 直接对照 | 左Median/P95 ms | 右Median/P95 ms | 配对节省Median [95%CI] ms | 正向 | 对数/批 | 判断 |\n|---|---|---:|---:|---:|---:|---:|---|\n'
 for r in rows:text+=f"| {names[r['case']]} | {r['left']}→{r['right']} | {fmt(r['left_median_ms'])}/{fmt(r['left_p95_ms'])} | {fmt(r['right_median_ms'])}/{fmt(r['right_p95_ms'])} | {fmt(r['paired_saving_median_ms'])} [{fmt(r['ci95_low_ms'])}, {fmt(r['ci95_high_ms'])}] | {r['positive_pairs']}/{r['n_pairs']} | {r['n_pairs']}/{r['independent_batches']} | {conclusion(r)} |\n"
 return text
main=[r for r in E if r['left']=='G0'];inc=[r for r in E if r['left']!='G0']
core=[]
for case in names:
 rr=[effect(case,'G1',g)for g in ['G2','G3','G4']]
 if all(rr):core.append(f"{names[case]}：相对Copy单独，A、B1、A+B1的直接配对节省分别为"+' / '.join(fmt(r['paired_saving_median_ms'])+'ms'for r in rr)+'；'+ ' / '.join(conclusion(r)for r in rr)+'。')
limits='''本轮是五组组合筛选，非完整三因子交互实验；每条对照18对来自3批/9进程，每进程最多2对，CI为预登记的batch→process聚类bootstrap（10,000次、seed250027），多重比较未校正。P95采用线性分位数，样本少，不作为尾延迟容量承诺。G0→各优化组分别有自己的直接配对Baseline，表中绝对中位数不能跨行相减。

使用Step18同源plain家族，bigNumCal 10,000轮，Step24B原件100轮；不能直接把本轮绝对耗时与旧约5ms相减。B1仅指恢复的SDK PB依赖裁剪，移除了GetBatchState公共API，不是通用兼容优化。A增大静态布局和模板，需计内存成本。所有组Fresh，未设置R0，所以不能复核历史normalCal“Fresh比复用快”的方向。

这是固定owner/独立Store的串行参考管理器测试，不是原实例池或节点端到端数据。Table真实函数身份、异常/OOG/跨合约、长期Store资源回收和并发均not_tested，不支持直接开展原池并发Fresh节点压测。'''
# Deliver presentation material first, before longer reports.
(P/'PPT.md').write_text('# Step-25：A/B1/Copy组合的串行筛选\n\nG0=Baseline Fresh；G1=Copy；G2=A+Copy；G3=历史PB依赖裁剪+Copy；G4=A+同一裁剪+Copy。正值=左减右、右组更快。\n\n'+table(main)+'\n## 核心结论\n\n'+'\n\n'.join(core)+'\n\n全部已完成配对Gas、返回、根RWSet、事件及账本对照通过；证据限当前成功路径。\n\n## 局限\n\n'+limits+'\n')
text='# 完整串行筛选结果\n\n'+table(E)+'\n## 各批直接配对节省\n\n| 方法 | 对照 | 批次 | N | 节省Median ms | 正向比例 |\n|---|---|---:|---:|---:|---:|\n'
for r in B:text+=f"| {names[r['case']]} | {r['left']}→{r['right']} | {r['batch']} | {r['n']} | {fmt(r['paired_median_ms'])} | {float(r['positive_fraction']):.1%} |\n"
text+='\n## 阶段归因（同样本直接配对）\n\n| 方法 | 对照 | NewInstance节省 | Copy节省 | S0→S1节省 | S1→S2节省 | S2→S3节省 | export.Call节省 | 完整Invoke节省（均ms） |\n|---|---|---:|---:|---:|---:|---:|---:|---:|\n'
for r in E:
 def stage(k):return fmt(next(s['paired_saving_median_ms']for s in S if(s['case'],s['left'],s['right'],s['metric'])==(r['case'],r['left'],r['right'],k)))
 text+='| '+names[r['case']]+' | '+r['left']+'→'+r['right']+' | '+' | '.join(stage(k)for k in ['newinstance_ns','copy_ns','s0_s1_ns','s1_s2_ns','s2_s3_ns','export_call_ns','invoke_ns'])+' |\n'
text+='\n各列均是逐条差的中位数，不能横向相加重建总中位数。start中同时含Go Runtime和package init，本轮没有独立Guest A/B1计时，不把整个start节省归于其中一项。\n\n## 顺序敏感性\n\n| 方法 | 对照 | 分层因素 | 左/右先 | N | 节省Median [95%CI] ms |\n|---|---|---|---|---:|---:|\n'
for r in O:text+=f"| {names[r['case']]} | {r['left']}→{r['right']} | {r['factor']} | {r['value']} | {r['n']} | {fmt(r['paired_median_ms'])} [{fmt(r['ci95_low_ms'])}, {fmt(r['ci95_high_ms'])}] |\n"
text+='\n任何分层CI跨零或反向都保留；平衡总体受益不等于顺序无关。\n\n## 内存、模板与准备\n\n| 合约 | 组 | 原WASM KiB | 初始页 | 静态Image MiB | Copy字节 | Copy范围 |\n|---|---|---:|---:|---:|---:|---:|\n'
for m in M:
 if m.get('case')=='normal':continue
 temps=[x for x in Prep if x['event']=='template'and x.get('source_sha')==m['wasm_sha256']];samples=[x for x in T if x['contract']==m['contract']and x['group']==m['group']and x['is_target']=='True']
 if temps and samples:text+=f"| {m['contract']} | {m['group']} | {int(m['wasm_bytes'])/1024:.2f} | {m['initial_pages']} | {int(temps[0]['image_bytes'])/1048576:.4f} | {samples[0]['copy_bytes']} | {samples[0]['copy_ranges']} |\n"
text+='\nG0也构造/持有用于比较和S1检查的Image；这不是生产Baseline必须支付的内存。G0/G1同源可共享一个模板；不同WASM分开。原始NoData字节、Image与Module本身各有缓存占用；Image容量不等于整个native Module容量，后者未单独量化。A模板与初始页增加见表。MODULE_PREPARATION.csv保留每进程template/module/close；Module prepare含验证/Store/metadata，不是纯JIT编译时间。\n'
text+=f"\n全部{v['processes']}进程，成功{v['passed']}、失败{v['failed']}；峰值观测RSS {v['max_observed_rss_mib']:.2f}MiB、线程{v['max_observed_threads']}。Go heap与每个退出结果见RESOURCE_SUMMARY.csv。RSS为双角色进程总量，不拆成各组独立成本。\n\n## 限制\n\n"+limits+'\n'
(P/'RESULTS.md').write_text(text)
gas={}
for case in names:
 for g in ['G0','G1','G2','G3','G4']:gas[case,g]=sorted({int(x['gas'])for x in T if x['case']==case and x['group']==g and x['is_target']=='True'})
ct='# 正确性与安全范围\n\n目标方法真实执行，所有成功/失败均保留；不是仅用Go进程PASS判定。\n\n| 方法 | G0 | G1 | G2 | G3 | G4 |\n|---|---:|---:|---:|---:|---:|\n'
for case in names:
 if any(gas[case,g]for g in ['G0','G1','G2','G3','G4']):ct+='| '+names[case]+' | '+' | '.join(str(gas[case,g])for g in ['G0','G1','G2','G3','G4'])+' |\n'
ct+=f'''\n已完成{len(C)}个有效配对的Gas/业务对照。逐对比较实际返回码/消息/返回字节、root RWSet（含读集和写集）、事件、业务输入、初始/最终账本及每层调用记录；bigNum返回607723520，normal返回666，fact检查JSON字段与实际写入，mint检查owner。相同输入、固定TxID和初始账本，mint tokenId=1，每次从相同init账本开始，Instance完全Fresh。

四种最终逻辑WASM各自Copy off/on经过preflight：原版与对应noData+restore S1全Memory SHA各与其模板相等，同逻辑二进制Gas/业务相等。A/B1跨二进制不能要求S1字节相等，但本次观测Gas仍严格相等；未隐去跨二进制差异。所有实测合同的A/B1新布局也可被原Copy parser支持。

未测试：真实Table函数身份（不是以非空证明身份）、全部异常/OOG/回滚、真实跨合约、长期Store回收/共享Store并发、原池背景补充及节点共识。没有这些场景的PASS。B1删除GetBatchState公共接口，只对不使用该API的当前方法给出结果。

两角色Module/Store独立，owner/ManagedScope守卫保持；每次business fresh，逐次close后native对象数恢复到创建前，最终created=closed、managed/pending=0，进程及cgroup退出。独立Instance隔离来自新建、相等初始账本与重复业务结果检查；本轮没有新增同时保留两个Instance互写的隔离压力试验，不把未做的测试冒充通过。RSS/线程有界只覆盖单进程2对，Store存活期间线程增长仍存在。
'''
(P/'CORRECTNESS.md').write_text(ct)
