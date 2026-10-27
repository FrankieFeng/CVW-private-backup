from pathlib import Path
import csv,json,statistics
P=Path(__file__).resolve().parents[1]
def rows(name):return list(csv.DictReader((P/name).open()))
E=rows('PAIRED_EFFECTS.csv');S=rows('SUMMARY.csv');B=rows('BATCH_EFFECTS.csv');R=rows('RESOURCE_SUMMARY.csv');T=rows('TIMING.csv');M=rows('MODULE_PREPARATION.csv');D=rows('BUY_NOW_DECOMPOSITION.csv');V=json.loads((P/'verification.json').read_text())
name={'compute':'compute.bigNumCal','fact':'fact.saveAndFindByFileHash','erc721':'erc721.mint','exchange':'exchange.buyNow'}
def effect(c,k):return next(r for r in E if r['contract']==c and r['metric']==k)
def summary(c,v,k):return next(r for r in S if r['contract']==c and r['variant']==v and r['metric']==k)
def f(x):return f'{float(x):.3f}'
def etable(cs,k):
 s='| 合约 | 对数/独立批 | A0 Median/P95 ms | A1 Median/P95 ms | 配对节省Median [95%CI] ms | 正向比例 |\n|---|---:|---:|---:|---:|---:|\n'
 for c in cs:
  e=effect(c,k);a=summary(c,'A0',k);b=summary(c,'A1',k)
  s+=f"| {name[c]} | {e['valid_pairs']}/{e['independent_batches']} | {f(a['median_ms'])}/{f(a['p95_ms'])} | {f(b['median_ms'])}/{f(b['p95_ms'])} | {f(e['saving_median_ms'])} [{f(e['ci95_low_ms'])}, {f(e['ci95_high_ms'])}] | {e['positive_pairs']}/{e['valid_pairs']} ({float(e['positive_fraction'])*100:.1f}%) |\n"
 return s
core=['compute','fact','erc721'];body='''# Step-24B 结果：有界串行完整Invoke

2026-10-27 Asia/Shanghai。先审计、预登记、预检及先导，再完成135个单合约正式进程（每合约45进程、3批各15进程×2对），另3预检及8个buyNow进程。不是同Store连续30对；线程累积限制下没有扩大单进程预算。A0/A1只比较Baseline Fresh与静态Memory Copy，没有A段/PB等优化。

## 完整Invoke主结果

'''+etable(core,'invoke_ns')+'''
三个合约各批完整Invoke配对节省中位数均为正，整体95%聚类bootstrap区间均在零以上：**本轮条件支持静态初始化收益传递到完整Invoke**。这不是每次都更快；270个单合约正式配对有49对反向，全部保留，未剔除异常值。不能扩大为所有合约、长寿命Store或真实节点稳定收益。

配对节省是逐对A0−A1的中位数，不是两组Median相减。P95最近秩；每合约90对、45进程聚类、仅3批，置信区间是固定本机/本时段有界进程模型下的探索性估计，不认证长期稳定性。预检、init、Module/模板准备与最终缓存关闭不计入表中Invoke；每次Instance/WASI关闭计入。详见AUDIT.md。

## 初始化收益及阶段传递

纯静态初始化窗口NewInstance+Copy：

'''+etable(core,'static_init_ns')+'''
这里每条样本先求newinstance_ns+copy_ns再配对，不把不同中位数混加。Invoke级S0→S1还包含WASI/imports准备，因此不等于纯Data初始化；S0=Invoke入口，S1=NewInstance/Copy后，S2=WASI.Initialize/_start后，S3=业务/Gas结果后关闭前。全部阶段有嵌套，不可把CallMethod再次加到S2→S3。TIMING.csv资源值为每根调用返回后的实际RSS/线程边界，子行仅引用所属根边界；没有声称获得每callee瞬时资源。

| 合约 | 阶段 | 配对节省Median [95%CI] ms |
|---|---|---:|
'''
for c in core:
 for k,title in [('newinstance_ns','NewInstance'),('copy_ns','Copy（A0为0，故节省为负成本）'),('wasi_imports_ns','WASI/imports'),('s0_s1_ns','S0→S1'),('s1_s2_ns','S1→S2'),('s2_s3_ns','S2→S3'),('callmethod_ns','CallMethod'),('close_ns','Close')]:
  e=effect(c,k);body+=f"| {name[c]} | {title} | {f(e['saving_median_ms'])} [{f(e['ci95_low_ms'])}, {f(e['ci95_high_ms'])}] |\n"
body+='''
主要可解释节省位于NewInstance静态Data初始化；A1另支付Host区间Copy成本，净初始化省约0.68–0.75ms。A1在Copy timer后还有Ranges字节计数记账循环，该观测开销计入S0→S1/Invoke，未算入pure static_init；本轮按22原样保留。后续准备/执行/关闭存在噪声，不能用各阶段中位数相加解释整笔中位数。对阶段均值可作线性核算，但本轮不把其他窗口偶发差异归因于Copy。

## 每批与顺序

| 合约 | 批次 | 有效对 | Invoke节省Median ms | 正向比例 |
|---|---:|---:|---:|---:|
'''
for c in core:
 for r in B:
  if r['contract']==c and r['metric']=='invoke_ns':body+=f"| {name[c]} | {r['batch']} | {r['n']} | {f(r['saving_median_ms'])} | {float(r['positive_fraction'])*100:.1f}% |\n"
body+='''
### 顺序分层（补充离线分析）

| 合约 | 配对中先运行 | n | Invoke节省Median [95%CI] ms | 正向比例 |
|---|---|---:|---:|---:|
'''
for r in rows('ORDER_SENSITIVITY.csv'):
 if r['contract'] in core and r['factor']=='first':
  body+=f"| {name[r['contract']]} | {r['value']} | {r['n']} | {f(r['invoke_saving_median_ms'])} [{f(r['ci95_low_ms'])}, {f(r['ci95_high_ms'])}] | {float(r['positive_fraction'])*100:.1f}% |\n"
body+='''
收益幅度明显依赖先后顺序，不能把平衡设计下总体中位数解释为顺序无关常数；尤其fact在A0先分层的95%CI为[-0.113,0.488]ms，跨零；不能称该顺序已确认收益。这是事后分层，未用于挑选/剔除样本或触发继续运行。完整Invoke的强结论限于预登记的平衡顺序总体。

每个单合约进程两配对恰好一对A0先/一对A1先，整体45对/顺序。Module准备顺序也按进程交替（45进程不能完全二等分，23/22），未根据耗时选种子/样本。ORDER_SENSITIVITY.csv同时保存两种因素；有顺序/时期敏感性但未删样本。统计固定seed240027，10000次先抽batch再抽process的配对bootstrap，同进程两对整体保留；没有把180条单独Invoke当独立配对。

## buyNow扩展：根与六callee

'''+etable(['exchange'],'invoke_ns')+'''
只有3独立对，3/3为正时bootstrap区间正值很大程度受小样本支持集限制；**不能据此声称buyNow稳定收益**。三组正式Full Invoke节省为6.628、28.385、2.698ms；正式样本未重复22的A1慢15.765ms，但宿主准备/启动波动仍明显。

| 批次/阶段 | 根Full Invoke节省 ms | 全7调用纯静态初始化节省 ms | 六callee WASI/imports节省 ms | 全7 _start节省 ms |
|---|---:|---:|---:|---:|
'''
for r in D:body+=f"| {r['phase']} {r['batch']} | {f(r['full_invoke_saving_ms'])} | {f(r['all7_static_init_saving_ms'])} | {f(r['six_child_wasi_imports_saving_ms'])} | {f(r['all7_start_saving_ms'])} |\n"
body+='''
预检反向1.351ms仍保留，其六callee准备A1多5.9995ms；该过程含S1全Memory SHA，不混入正式性能。正式第2批A0六callee准备反而多11.344ms，连同启动/其他窗口导致更大正向值；不能把28.385ms全部认作Copy。实际六子调用逐窗口见BUY_NOW_STAGE_EFFECTS.csv；BUY_NOW_DECOMPOSITION.csv只加互不嵌套的创建/start/close子阶段，不把根与子Invoke重复相加。未测每窗口owner线程CPU/调度/分配器因果，不宣称准备波动一定由调度造成。

旧22第三批两原log重算Full Invoke A0−A1=-15.764944ms，六callee WASI/imports=-19.732278ms（audit/historical-buyNow-recompute.json），说明历史反向确实主要发生在准备窗口。新样本出现不同方向的大准备差；证据支持它能掩盖或放大Copy净收益，尚不能证明某一反向机制稳定存在。

## Module/模板成本与复制量

| 合约 | 模板准备Median ms | A0 Module准备Median ms | A1 Module准备Median ms | 每次Copy Bytes |
|---|---:|---:|---:|---:|
'''
for c in ['compute','fact','erc721','exchange','identity']:
 sel=[r for r in M if r['phase']=='formal'and r.get('contract')==c]
 temp=[int(r['prepare_ns'])/1e6 for r in sel if r['event']=='template'];a=[int(r['module_prepare_ns'])/1e6 for r in sel if r['event']=='module'and r['variant']=='A0'];b=[int(r['module_prepare_ns'])/1e6 for r in sel if r['event']=='module'and r['variant']=='A1'];bs=sorted(set(int(r['copy_bytes'])for r in T if r['phase']=='formal'and r['contract']==c and r['variant']=='A1'))
 body+=f"| {c} | {f(statistics.median(temp))} | {f(statistics.median(a))} | {f(statistics.median(b))} | {','.join(map(str,bs))} |\n"
body+='''
Module准备含config/Engine/Store/Validate/compile及metadata，不是纯编译器函数；各缓存只准备一次，无不对称逐调用编译。每个独立进程重建缓存的真实总成本全数保存在MODULE_PREPARATION.csv；本轮Invoke收益不含这些一次性成本，不能用于估计进程级端到端收益/摊销或原生产池性能。

## 正确性、资源与可推广性

'''+f"共{V['processes']}个测试进程正常退出，{V['semantic_pair_checks']}对成功路径语义检查相同（含预检），最终native包装登记0，所有PID/cgroup结束。单合约正式90对/合约与buyNow3对，全部Fresh，Gas/返回/根读写集/事件/初始最终账本一致。最高RSS采样/边界{max(float(r['peak_rss_mib'])for r in R):.2f}MiB，线程{max(int(r['peak_threads'])for r in R)}；无STOP、阈值未放宽。\n"+'''
Store期内线程仍随WASI累积，单合约边界通常57→74→91→108，进程最终释放；没有解决长期Store生命周期。真实Table函数身份、动态Globals、异常/OOG、完整callee内部RWMap、并发和真实节点继续not_tested。原始记录与计时范围见CORRECTNESS.md、RESOURCE_SUMMARY.csv、raw_logs和AUDIT.md。

本结果足以支持进一步设计**有界、隔离的节点功能验证**，但不足以直接启动真实节点并发Fresh性能实验或生产启用。必须先补Table/异常语义、长期WASI/Store供给与回收协议和节点路径等价性；不能把进程隔离下的90对写成同Store连续90对或默认池TPS。精确native构建来源仍未闭合。本轮不部署节点、不新增优化、不push。
'''
(P/'RESULTS.md').write_text(body)
readme='''# Step-24B：Copy完整Invoke收益确认

2026-10-27。分支experiment/step24b-copy-invoke，父Step23 ba57368，Copy/计时基于Step22 394d291。独立worktree .worktrees/cvw-step24b，未修改生产VM、Gas规则、Copy算法或生命周期guard，未覆盖22/23，未push。

**本轮三个单合约的初始化净节省传递到完整Invoke；buyNow只得到小样本且强波动结果，不能泛化稳定收益。**

'''+etable(core,'invoke_ns')+'''
每合约3批×30对，但每批由15个独立进程各2对构成，Module/Store在该进程缓存。不是同Store连续30/90对；不提高单Store预算，以隔离已知WASI线程累积。相比22还补齐两组对称真实init、固定TxID/tokenId、平衡Module准备顺序；因此不把不同版本绝对耗时直接作因果相减。

## 六个问题

1. **节省阶段**：主要在NewInstance的静态Data初始化，支付Copy后净省约0.68–0.75ms；S0→S1含WASI/imports，分表报告。
2. **完整Invoke稳定性**：本轮三个合约各批中位数为正，平衡顺序总体95%聚类区间在零以上；约80–83%配对正向。顺序分层幅度明显不同，仍有反向样本，不宣称顺序无关或长期/节点稳定。
3. **哪些受益**：bigNumCal、fact、ERC721在平衡顺序总体均受益；fact的A0先分层CI跨零，收益并非顺序无关。buyNow数据不足作稳定判断，不因3/3正向宣称普遍收益。
4. **buyNow反向**：正式3对未复现原15.765ms反向，节省2.698–28.385ms；预检保留1.351ms反向。子调用准备波动能掩盖或放大收益，未证明由Copy导致。
5. **语义**：146个有界进程、277个配对语义核对通过；Gas/返回/根RWSet/事件/账本一致，buyNow均真实六callee。Table身份/异常等仍not_tested。
6. **真实节点**：尚不足以直接进入并发Fresh节点性能验证；先解决长期Store线程/回收与Table/异常安全门槛，可据此设计有限节点功能预检。

[RESULTS](RESULTS.md)含完整阶段、CI、每批、准备成本和buyNow分析；[AUDIT](AUDIT.md)给出模型/计时；[CORRECTNESS](CORRECTNESS.md)界定成功路径；[PROGRESS](PROGRESS.md)、[RUNNING](RUNNING.md)用于恢复/复算。

交付数据：TIMING.csv、PAIRED_EFFECTS.csv、PAIRED_SAMPLES.csv、RESOURCE_SUMMARY.csv、MODULE_PREPARATION.csv、BUY_NOW_STAGE_EFFECTS.csv及raw_logs。源码差异source.diff仅实验测试入口，全部原始失败/异常保留；scripts/analyze.py和write_report.py离线复算，不运行guest。
'''
(P/'README.md').write_text(readme)
print('README.md / RESULTS.md written from final CSV')
