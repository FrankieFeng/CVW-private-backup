from pathlib import Path
import csv,json
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
E=read('PAIRED_EFFECTS.csv');B=read('BATCH_EFFECTS.csv');O=read('ORDER_SENSITIVITY.csv');S=read('STAGE_EFFECTS.csv');V=json.loads((P/'verification.json').read_text());N={'compute':'compute.bigNumCal（10000轮）','fact':'fact.saveAndFindByFileHash','erc721':'erc721.mint'}
f=lambda x:f'{float(x):.3f}'
text='''# Step-26 增量收益复算结果

**全部来自Step25已有有效配对，新增运行0、编译0、独立新批次0。** 这是对原始证据的审计确认，不是一次新的时间维度重复验证。主矩阵只用Step18同源plain家族，不混入Step24B原件数据。

编号：G1=Copy（oldG1），G2=A+Copy（oldG2），G3=A+B1+Copy（oldG4）。正值=左Invoke−右Invoke。原始日志保留oldG4，CSV同时列出原编号。

## 完整Invoke直接配对

| 方法 | 对照 | 左Median/P95 ms | 右Median/P95 ms | 配对节省Median [95%CI] ms | 正向 | 原对数/批/进程 |
|---|---|---:|---:|---:|---:|---:|
'''
for e in E:text+=f"| {N[e['case']]} | {e['left']}→{e['right']} | {f(e['left_median_ms'])}/{f(e['left_p95_ms'])} | {f(e['right_median_ms'])}/{f(e['right_p95_ms'])} | {f(e['paired_saving_median_ms'])} [{f(e['ci95_low_ms'])}, {f(e['ci95_high_ms'])}] | {e['positive_pairs']}/18 | 18/3/9 |\n"
text+='''
所有9项总体CI在零以上、各自原3批配对中位数为正。这支持原有三个批次和平衡调用协议下的增量收益，不是长期、顺序无关或真实节点收益认证。不同对照各有自己的进程和左右样本，绝对中位数不能跨行直接相减、相加或串接成“总收益”。

CI沿用预先登记的层次bootstrap：先抽3个batch，再在该batch抽process，将每process的2对作为整体保留，10000次、seed250027；P95与区间端点用线性分位数。18对不是18个完全独立进程。多重比较未校正，3批对环境长期波动覆盖有限。

## 批次分层

| 方法 | 对照 | 原批次 | N/进程 | 节省Median [95%CI] ms | 正向 |
|---|---|---:|---:|---:|---:|
'''
for e in B:text+=f"| {N[e['case']]} | {e['left']}→{e['right']} | {e['batch']} | 6/3 | {f(e['saving_median_ms'])} [{f(e['ci95_low_ms'])}, {f(e['ci95_high_ms'])}] | {e['positive_pairs']}/6 |\n"
text+='''
批内区间仅有3个process簇，非常探索性；批次中位数为正不等于每个批内CI均排除零。

## 运行与Module准备顺序

| 方法 | 对照 | 因素 | 实际先执行/准备的组 | N/进程 | 节省Median [95%CI] ms |
|---|---|---|---|---:|---:|
'''
for e in O:text+=f"| {N[e['case']]} | {e['left']}→{e['right']} | {e['factor']} | {e['actual_first_group']} | {e['pairs']}/{e['processes']} | {f(e['paired_saving_median_ms'])} [{f(e['ci95_low_ms'])}, {f(e['ci95_high_ms'])}] |\n"
text+='''
每process两对交替，所以执行先后各9对；Module准备/真实init先后受原调度影响，是3/6或6/3个process（6/12或12/6对），不能写成完全平衡。

- compute的A增量：左右先执行的分层CI均跨零，Module准备先后中位数约1.589/0.601ms；不能据总体CI宣称不受顺序影响。
- compute的B1增量：A+Copy先执行及完整组合先准备的部分分层CI跨零。
- fact的A增量：A+Copy先准备分层CI跨零；B1增量中A+Copy先执行和完整组合先准备的分层CI跨零。
- ERC721三个对照的所有已采样顺序分层CI均为正；三合约完整组合相对Copy的分层CI也均为正。这是原小样本中的更强一致性，不证明任何运行顺序下都成立。
- 共7/36个顺序分层CI跨零。分层差异本身不等于已完成正式的顺序交互因果检验，不通过独立Median差推断具体机制。

## 阶段记录

| 方法 | 对照 | NewInstance节省 | Copy节省 | S0→S1节省 | S1→S2节省 | S2→S3节省 | export.Call节省 | Invoke节省（ms） |
|---|---|---:|---:|---:|---:|---:|---:|---:|
'''
for e in E:
 def stage(k):return f(next(s['paired_saving_median_ms']for s in S if(s['case'],s['left'],s['right'],s['metric'])==(e['case'],e['left'],e['right'],k)))
 text+='| '+N[e['case']]+' | '+e['left']+'→'+e['right']+' | '+' | '.join(stage(k)for k in ['newinstance_ns','copy_ns','s0_s1_ns','s1_s2_ns','s2_s3_ns','export_call_ns','invoke_ns'])+' |\n'
text+='''
这里只给直接差的阶段中位数，不横向相加重建总中位数。start、CallMethod和Close全部原记录在TIMING/STAGE_EFFECTS。

S0是Invoke入口（Module/模板已准备），S1是NewInstance+Copy完成，S2是WASI.Initialize/_start及start wrapper关闭后，S3是业务/GetGas/结果处理完成且Instance关闭前。完整Invoke到每次清理defer结束，包含创建/start/业务/同步关闭。NewInstance不含随后Copy；Copy包含原校验、Memory lookup和区间copy；S0→S1还包含WASI/imports准备。模板/Module准备、真实init、账本clone/receipt写盘、末尾持久Module/Store关闭都在外，MODULE_PREPARATION单列。Module prepare还含配置/验证/Store/metadata，并不是纯编译器CPU时间。

A增量主要落在S1→S2约0.74–0.79ms；B1在A+Copy基础上的增量包含更少Copy/S0→S1及部分启动时间。compute还有Guest export窗口差异，不能全归因初始化。当前plain没有Guest A/B1细分计时，不把整个_start解释为某一个具体缓存或清零函数。NoData只替代active Data初始化，未执行原始Data后重复Copy。
'''
text+=f"\n## 资源与范围\n\n复核原81正式+15预检进程均created=closed、managed/pending=0、PID/cgroup退出；原所选进程观测峰RSS {V['max_original_rss_mib']:.2f}MiB、Go heap Alloc {V['max_original_go_heap_alloc_mib']:.2f}MiB、线程{V['max_original_threads']}，未触发资源保护。本轮没有产生新的VM资源样本，RESOURCE_SUMMARY明确标为旧数据。每个进程有两个独占Store，RSS不能分解为某一组的精确成本。\n"
text+='''
## 判断与下一步

在这组原有Step18样本中，A+Copy优于Copy，B1在A+Copy之上有正增量，完整组合优于Copy。顺序分层限制和构建来源限制仍然存在，不把复算写成新增独立验证。

若优先保持SDK公共接口，A+Copy更适合优先继续：三个原批总体收益为正，API未被本优化删减。完整组合在这里更快，但B1删除GetBatchState，仅能保留为受限合约的实验分支候选。原Step24B家族匹配A/B1仍blocked，先恢复其计费/构建链再验证，不能把本家族的数值当成原件或节点收益。

Table真实函数身份、异常/OOG/回滚、真实跨合约、长期Store回收及原池并发未验证。这些结果足以选择下一轮隔离串行候选，不足以生产启用或开展原池并发节点压测。本轮无PPT、无新增机制、无生产修改。
'''
(P/'RESULTS.md').write_text(text)
