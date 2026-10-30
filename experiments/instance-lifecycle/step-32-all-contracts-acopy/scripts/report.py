from pathlib import Path
import csv,json,statistics as st
P=Path(__file__).resolve().parents[1];read=lambda n:list(csv.DictReader((P/n).open()))
def fmt(x):
 try:return f'{float(x):.3f}'
 except:return str(x)
def tab(rows,cols):return '| '+' | '.join(k for k,v in cols)+' |\n| '+' | '.join('---'for _ in cols)+' |\n'+'\n'.join('| '+' | '.join(str(r.get(v,''))for k,v in cols)+' |'for r in rows)+'\n'
a=json.loads((P/'analysis.json').read_text());summary=read('SUMMARY.csv');effects=read('PAIRED_EFFECTS.csv');inter=read('INTERACTION_ANALYSIS.csv');res=read('RESOURCE_SUMMARY.csv');stage=read('STAGE_EFFECTS.csv');strata=read('STRATIFIED_EFFECTS.csv');cases=['bigNumCal','hashCal','normalCal','fact','erc721','buyNow'];names={'bigNumCal':'compute.bigNumCal','hashCal':'compute.hashCal','normalCal':'compute.normalCal','fact':'fact.saveAndFindByFileHash','erc721':'erc721.mint','buyNow':'exchange.buyNow'}
get=lambda c,e:next(r for r in effects if r['case']==c and r['effect']==e)
ci=lambda r:fmt(r['paired_saving_median_ms'])+' ['+fmt(r['ci95_low_ms'])+', '+fmt(r['ci95_high_ms'])+']'
rows=[]
for c in cases:
 if not any(r['case']==c for r in effects):continue
 r=dict(method=names[c],N=get(c,'A')['N'],batches=get(c,'A')['batches'])
 for g in ['G0','G1','G2','G3']:
  z=next(x for x in summary if x['case']==c and x['group']==g and x['metric']=='invoke_ns');r[g]=fmt(z['median_ms'])+' / '+fmt(z['p95_ms'])
 for e in ['A','Copy','A+Copy','A_given_Copy','Copy_given_A']:r[e]=ci(get(c,e))
 rows.append(r)
perf=tab(rows,[('方法','method'),('N/组','N'),('批','batches'),('Fresh Median/P95','G0'),('A Median/P95','G1'),('Copy Median/P95','G2'),('A+Copy Median/P95','G3')]);eff=tab(rows,[('方法','method'),('A节省[95%CI]','A'),('Copy节省[95%CI]','Copy'),('组合节省[95%CI]','A+Copy'),('A叠加Copy','A_given_Copy'),('Copy叠加A','Copy_given_A')])
br=[]
for c in cases:
 if not any(x['case']==c for x in effects):continue
 z={'method':names[c]}
 for e in ['A','Copy','A+Copy','A_given_Copy','Copy_given_A']:
  z[e]=' / '.join(fmt(v)for v in json.loads(get(c,e)['batch_medians_ms']))
 br.append(z)
bt=tab(br,[('方法','method'),('A各批','A'),('Copy各批','Copy'),('组合各批','A+Copy'),('A叠加Copy各批','A_given_Copy'),('Copy叠加A各批','Copy_given_A')])
ir=[]
for r in inter:
 ir.append(dict(method=names[r['case']],raw=fmt(r['interaction_cost_median_ms'])+' ['+fmt(r['interaction_cost_ci95_low_ms'])+', '+fmt(r['interaction_cost_ci95_high_ms'])+']',synergy=fmt(r['synergy_saving_median_ms'])+' ['+fmt(r['synergy_ci95_low_ms'])+', '+fmt(r['synergy_ci95_high_ms'])+']',judgment='额外协同得到本批支持'if float(r['interaction_cost_ci95_high_ms'])<0 else'抵消得到本批支持'if float(r['interaction_cost_ci95_low_ms'])>0 else'CI跨零，未分辨交互'))
it=tab(ir,[('方法','method'),('原式Interaction[CI]','raw'),('额外协同收益[CI]','synergy'),('判断','judgment')])
st=[]
for c in cases:
 for e in ['Copy','A','A+Copy']:
  arr=[r for r in stage if r['case']==c and r['effect']==e]
  if not arr:continue
  z=dict(method=names[c],effect=e)
  for m in ['to_s1_ns','s1_to_s2_ns','s2_to_s3_ns','export_call_ns','close_ns']:z[m]=fmt(next(r['paired_saving_median_ms']for r in arr if r['metric']==m))
  z['invoke']=fmt(get(c,e)['paired_saving_median_ms']);st.append(z)
stt=tab(st,[('方法','method'),('效应','effect'),('S0→S1节省','to_s1_ns'),('S1→S2节省','s1_to_s2_ns'),('S2→S3节省','s2_to_s3_ns'),('export节省','export_call_ns'),('Close节省','close_ns'),('Invoke节省','invoke')])
order=[]
for c in cases:
 for e in ['A','Copy','A+Copy','A_given_Copy','Copy_given_A']:
  rs=[r for r in strata if r['case']==c and r['effect']==e and r['stratum']=='left_before_right']
  if not rs:continue
  order.append(dict(method=names[c],effect=e,groups='；'.join(r['value']+': '+fmt(r['paired_saving_median_ms'])+'ms / N'+r['N']for r in rs),direction_agree=len({float(r['paired_saving_median_ms'])>0 for r in rs})==1))
ot=tab(order,[('方法','method'),('效应','effect'),('左先执行True/False','groups'),('方向一致','direction_agree')])
judgments=[]
for c in cases:
 if not any(r['case']==c for r in effects):continue
 parts=[]
 for e in ['A','Copy','A+Copy','A_given_Copy','Copy_given_A']:
  r=get(c,e);decision='正向CI且三批正'if float(r['ci95_low_ms'])>0 and r['all_batches_positive']=='True'else'总体正向CI但批次不一致'if float(r['ci95_low_ms'])>0 else'总体负向CI'if float(r['ci95_high_ms'])<0 else'CI跨零'
  parts.append(e+'：'+decision+'，正向'+f"{100*float(r['positive_fraction']):.1f}%")
 judgments.append('- **'+names[c]+'**：'+'；'.join(parts)+'。')
text=f'''# Step32 实测结果

本轮新样本：{a['valid_formal_blocks']}有效正式四组区块、{a['formal_root_calls']}正式根调用、{a['formal_real_child_calls']}真实下游调用；每方法实际数量见表。未混入任何历史计时。所有时间单位ms，Median/P50相同；Mean及完整阶段统计见SUMMARY.csv。四组定义G0 Fresh、G1 A-only、G2 Copy-only、G3 A+Copy，勿沿用Step28编号。

## 完整Invoke

{perf}
## 直接配对效应

正值表示右侧更快。每个block内相减，再取中位数；不是独立组Median相减。CI为10,000次批次→whole-block层次bootstrap，固定种子；只有3个时间批次，多重比较未校正。正向比例、Mean、P95及相对比例见PAIRED_EFFECTS.csv。

{eff}
{chr(10).join(judgments)}

## 三批结果

{bt}
## 交互效应

{it}

必须纠正符号：原式G0−G1−G2+G3为正表示组合比加性预测更慢（抵消）；为负表示组合额外节省（协同）。文件同时保留原式和相反数synergy_saving_ms。上述均同一block四项直接运算后统计，不根据三条独立Median推算。

## 阶段归因

{stt}

Module编译/模板准备在Invoke外，另存MODULE_PREPARATION.csv。S0→S1是WASI/imports+Instance/Copy；S1→S2含WASI Initialize及_start；S2→S3包含CallMethod/Gas结算，不是CallMethod前的空白准备。export包含在CallMethod内；各阶段独立配对Median不可相加得到Invoke Median。A改变布局而非替换memclr实现，不能把整个阶段差强归因于清零。

buyNow完整执行真实六callee。BUY_NOW_WINDOWS.csv记录root export−六子Invoke之和的剩余窗口，包含桥接、字节码准备等多项；没有本轮独立测量clone/JSON/GC或纯Gas传播，不能把残余全叫子调用准备，也不能将Step29旧trace数值直接搬入。Store问题不是本轮已证实的性能归因。

## 顺序分层

{ot}

顺序、Module准备顺序和进程chunk位置有关联，分层方向不是唯一缓存/调度因果。全部不利样本保留。每批每组位置数2或3，实际顺序存command/block；没有100ms业务Sleep。每进程最多2目标调用，buyNow1目标；编译、init在外但其状态影响仍可能留在目标窗口，这是受控串行实验局限，不冒充节点池。

## 覆盖与正确性/资源

已有8类Go合约，优先完成六方法（4个root合约）；identity真实callee已覆盖，其独立方法及bigInput/itinerary/raffle扩展仍blocked，详见CONTRACT_INVENTORY。不是“8合约全部通过”。一般异常、真实Table函数身份、节点并发和长寿命回收未验证。

资源与正确性详情见CORRECTNESS.md/RESOURCE_SUMMARY.csv。出现STOP时对应配置只能分析保留现场；本报告不以缺失数字当0。当前进程outcome失败数{a['failed']}。
'''
(P/'RESULTS.md').write_text(text)
peakrss=max(float(x['peak_rss_kib'])for x in res)/1024;threads=max(int(x['peak_threads'])for x in res);heap=max(int(x['go_heap_peak_bytes'])for x in res)/1024/1024
bad=[r for r in res if r['passed']!='True' or r['instances_created']!=r['instances_closed'] or r['managed_pending']!='0' or r['pids_stopped']!='True' or r['cgroup_empty']!='True'];cc=read('CORRECTNESS.csv');gases={c:sorted({r['gas']for r in cc if r['case']==c})for c in cases};exceptions=[json.loads(f.read_text())for f in(P/'raw_logs').glob('exception-*-parity.json')]
(P/'CORRECTNESS.md').write_text(f'''# 四组正确性与资源边界

每个有效block四组Gas、返回、错误码、实际root读写集、事件、初始/最终账本hash一致；全部root账本由setup/target真实RWSet离线重建并逐阶段核对内存snapshot SHA，target-Gx-ledger.json完整保存。CORRECTNESS.csv保存每block状态，其他样本不会静默混入。

实际Gas集合：`{json.dumps(gases)}`。同家族跨A二进制虽本轮观测相等，不能推广到任意构建；Copy开启/关闭对应同逻辑WASM，S1 oracle校验仅preflight启用，正式关hash。编译/模板准备在外。

buyNow每成功root严格核对六callee的contract/method/depth/TxID/Gas/code/result；f.run使用真实合约和账本，无mock子调用返回。空参数/重复token两类失败路径四组分别实际执行，回滚最终账本等于初始，全部语义/trace一致，原始exception回执保留：{json.dumps(exceptions)}。

未测试：真实Table函数身份、一般异常/OOG全覆盖、节点共识/提交/E2E、原池并发、长期Store资源有界。不能把这些项记PASS。

## 资源

当前{len(res)}个有界独立进程，最高RSS {peakrss:.2f}MiB、host heap边界峰{heap:.2f}MiB、线程{threads}。不合格资源/退出记录{len(bad)}。每个outcome记录soft/hard保护、created/closed、in_flight、owner pending、PID/cgroup退出。

Store计数是每个cached Module所属Store scope的创建与成功关闭数：module事件数与cache_closed.store_scopes_closed核对；它不是native内部Rc引用计数或内存泄漏检测。Instance created=closed、scope回到0及进程退出证明本轮有界协议完成，不证明长寿命节点无泄漏。RSS/heap为整进程，不强分配为某个组净增量。

资源阈值保持历史非exchange768MiB/125线程、exchange1536MiB/220线程软限，hard2GiB/256tasks；没有提高上限，禁止绕过STOP。
''')
(P/'README.md').write_text(f'''# Step-32：A / Copy / A+Copy全方法四组评估

独立分支experiment/step32-all-contracts-acopy-matrix，父Step28 29950ab1。只使用既有受控串行Fresh协议，不修改生产VM、不加入B1/新Store架构、不运行节点/E2E、不推送、不制作PPT。

本轮实际完成{a['valid_formal_blocks']}正式四组block、{a['formal_root_calls']}根调用；每方法见RESULTS，不把预检/异常/下游重复算为根样本。新数据未与旧批次拼接。六重点方法均预检通过；其他候选合约及未纳入原因见CONTRACT_INVENTORY.csv。

{perf}

完整直接收益、CI、批次、顺序与阶段见[RESULTS](RESULTS.md)。交互原公式的符号与“额外收益”相反，两个方向同时保留INTERACTION_ANALYSIS.csv，不强行标所有组合有效。资源/业务/Gas与限制见CORRECTNESS.md。

## 复现和恢复

在独立worktree的本目录执行：

```bash
python3 scripts/experiment.py preflight
python3 scripts/experiment.py formal
python3 scripts/analyze.py
python3 scripts/report.py
python3 scripts/verify.py
```

有outcome/有效block时跳过，不覆盖；存在STOP或日志无outcome时先读PROGRESS和实际unit，禁止重复启动。准备WASM为同源冻结产物，不需要重编Guest；SHA见audit/variants.csv。Host完整build argv/build1-outcome/environment保留；脚本有本机绝对路径，迁移机器须登记新配置，不能直接宣称精确复现。

回退：等自有unit结束，离开本worktree即可；生产没有改动。保留所有历史与本轮数据，无远程推送。原始模块/模板/计时/回执/资源日志均在raw_logs，TIMING含初始化、预检、异常、root/child及valid_block标识。
''')
print('REPORT',a['formal_root_calls'],'roots; peak',round(peakrss,2),'MiB',threads,'threads; bad',len(bad))
extra='''
## 最终判断与后续候选

1. 六重点方法全部完成四组30区块/3批，180正式区块/720根调用；不是720个完全独立环境。bigInput.inputSize、identity.isApprovedUser独立root、itinerary.save、raffle.registerAll及额外fact.save本轮没有性能矩阵。identity仅在真实buyNow下游覆盖，不代替独立方法数据。
2. A单独：hash/fact/ERC/buyNow总体CI正且三批正；bigNum和normal CI跨零。Copy单独：bigNum/hash/ERC有正向CI且三批正；fact/normal/buyNow未确认。不同方法不合并成统一平均。
3. 组合相对Fresh：除buyNow以外五方法总体CI正且三批正。但“优于两项单独使用”的两条增量同时得到支持，只在hash/fact/ERC。本轮bigNum/normal的组合增量CI跨零，buyNow叠Copy到A为负。
4. 六方法交互CI均跨零，没有统计证据确认额外协同或抵消；buyNow的Copy_given_A负向是直接增量事实，不等于已证明统一交互机制。
5. 顺序分层反转见normal A-only与Copy-only，buyNow Copy-only及A_given_Copy；hash/fact/ERC主要效应和增量方向均较一致。只有3个时间批、顺序分层N13–17，多重比较未校正，不能称顺序无关或普遍适用。
6. 业务/Gas/完整root账本/事件及buyNow真实子调用均一致；两类buyNow失败回滚通过，没有资源/守卫/退出异常。Table身份、一般异常/OOG、长寿命回收、默认池与节点E2E仍未验证。
7. 优先后续候选为hashCal/fact/ERC721的A+Copy；bigNum/normal需要关注增量和Guest波动；buyNow优先专项复核A-only及根export残余，不推荐按本轮证据默认开启组合。这是通过节点安全准入后的候选清单，**不是E2E准入已经通过**。

## buyNow可测量的抵消窗口

BUY_NOW_PAIRED_WINDOWS.csv对相同30块直接计算。A-only→A+Copy的root export配对Mean节省为−8.558ms，六个子Invoke合计配对Mean节省+2.906ms，而root export减子Invoke总和的残余配对Mean节省−11.464ms。Mean在同集合下可相加核对；Median不可相加。说明新增耗时主要落在子Invoke外的根export残余中，不能归因于子Invoke本身变慢。

该残余包括原真实桥接、取字节码/克隆和其他host/guest工作；本轮没有细分计时，不宣称纯clone、JSON、GC或Store是根因。保留Step29作为独立历史线索，不搬其计时填补本轮窗口。
'''
with(P/'RESULTS.md').open('a')as f:f.write(extra)
with(P/'README.md').open('a')as f:f.write('\n主要判断：hash/fact/ERC的组合及增量较稳定；bigNum/normal组合对Fresh正向但增量未确认；buyNow A-only有收益、组合对Fresh未确认，Copy叠到A反向。交互CI均跨零。完整证据/限制见RESULTS。\n')
