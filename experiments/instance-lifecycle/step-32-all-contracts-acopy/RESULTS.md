# Step32 实测结果

本轮新样本：180有效正式四组区块、720正式根调用、720真实下游调用；每方法实际数量见表。未混入任何历史计时。所有时间单位ms，Median/P50相同；Mean及完整阶段统计见SUMMARY.csv。四组定义G0 Fresh、G1 A-only、G2 Copy-only、G3 A+Copy，勿沿用Step28编号。

## 完整Invoke

| 方法 | N/组 | 批 | Fresh Median/P95 | A Median/P95 | Copy Median/P95 | A+Copy Median/P95 |
| --- | --- | --- | --- | --- | --- | --- |
| compute.bigNumCal | 30 | 3 | 17.991 / 19.778 | 16.912 / 20.470 | 17.135 / 19.825 | 16.509 / 18.711 |
| compute.hashCal | 30 | 3 | 8.047 / 9.751 | 6.951 / 7.913 | 7.445 / 8.234 | 6.613 / 7.520 |
| compute.normalCal | 30 | 3 | 78.309 / 83.434 | 78.407 / 84.054 | 78.298 / 82.461 | 76.478 / 81.995 |
| fact.saveAndFindByFileHash | 30 | 3 | 4.412 / 5.040 | 3.760 / 5.025 | 4.107 / 5.335 | 3.191 / 3.775 |
| erc721.mint | 30 | 3 | 4.539 / 5.777 | 3.910 / 4.940 | 4.057 / 5.018 | 3.348 / 4.117 |
| exchange.buyNow | 30 | 3 | 61.002 / 76.370 | 48.430 / 66.044 | 63.142 / 75.945 | 57.004 / 68.097 |

## 直接配对效应

正值表示右侧更快。每个block内相减，再取中位数；不是独立组Median相减。CI为10,000次批次→whole-block层次bootstrap，固定种子；只有3个时间批次，多重比较未校正。正向比例、Mean、P95及相对比例见PAIRED_EFFECTS.csv。

| 方法 | A节省[95%CI] | Copy节省[95%CI] | 组合节省[95%CI] | A叠加Copy | Copy叠加A |
| --- | --- | --- | --- | --- | --- |
| compute.bigNumCal | 0.790 [-0.308, 1.172] | 0.605 [0.157, 1.447] | 1.342 [0.256, 1.733] | 0.475 [-0.283, 1.319] | 0.508 [-0.074, 1.424] |
| compute.hashCal | 0.966 [0.565, 1.465] | 0.534 [0.285, 1.024] | 1.466 [1.093, 1.892] | 0.905 [0.387, 1.148] | 0.210 [0.068, 0.731] |
| compute.normalCal | 0.183 [-2.085, 1.942] | 0.323 [-1.270, 2.827] | 2.421 [0.894, 3.718] | 1.780 [-0.207, 3.526] | 0.939 [-0.453, 5.225] |
| fact.saveAndFindByFileHash | 0.718 [0.490, 0.849] | 0.212 [-0.072, 0.664] | 1.243 [1.076, 1.378] | 0.962 [0.622, 1.347] | 0.587 [0.301, 0.885] |
| erc721.mint | 0.591 [0.238, 1.003] | 0.455 [0.110, 0.750] | 1.235 [0.958, 1.493] | 0.739 [0.488, 1.041] | 0.482 [0.300, 0.830] |
| exchange.buyNow | 11.722 [2.942, 22.338] | -0.967 [-10.124, 9.506] | 1.884 [-5.484, 11.465] | 6.987 [-2.957, 10.775] | -8.000 [-14.796, -1.980] |

- **compute.bigNumCal**：A：CI跨零，正向66.7%；Copy：正向CI且三批正，正向76.7%；A+Copy：正向CI且三批正，正向80.0%；A_given_Copy：CI跨零，正向70.0%；Copy_given_A：CI跨零，正向66.7%。
- **compute.hashCal**：A：正向CI且三批正，正向93.3%；Copy：正向CI且三批正，正向83.3%；A+Copy：正向CI且三批正，正向96.7%；A_given_Copy：正向CI且三批正，正向86.7%；Copy_given_A：正向CI且三批正，正向76.7%。
- **compute.normalCal**：A：CI跨零，正向53.3%；Copy：CI跨零，正向50.0%；A+Copy：正向CI且三批正，正向76.7%；A_given_Copy：CI跨零，正向63.3%；Copy_given_A：CI跨零，正向66.7%。
- **fact.saveAndFindByFileHash**：A：正向CI且三批正，正向76.7%；Copy：CI跨零，正向63.3%；A+Copy：正向CI且三批正，正向100.0%；A_given_Copy：正向CI且三批正，正向90.0%；Copy_given_A：正向CI且三批正，正向93.3%。
- **erc721.mint**：A：正向CI且三批正，正向96.7%；Copy：正向CI且三批正，正向70.0%；A+Copy：正向CI且三批正，正向100.0%；A_given_Copy：正向CI且三批正，正向93.3%；Copy_given_A：正向CI且三批正，正向90.0%。
- **exchange.buyNow**：A：正向CI且三批正，正向83.3%；Copy：CI跨零，正向46.7%；A+Copy：CI跨零，正向53.3%；A_given_Copy：CI跨零，正向60.0%；Copy_given_A：总体负向CI，正向23.3%。

## 三批结果

| 方法 | A各批 | Copy各批 | 组合各批 | A叠加Copy各批 | Copy叠加A各批 |
| --- | --- | --- | --- | --- | --- |
| compute.bigNumCal | 0.699 / 0.382 / 0.809 | 1.447 / 0.682 / 0.250 | 0.491 / 1.342 / 1.626 | -0.196 / 0.475 / 1.220 | 0.373 / 1.420 / 0.333 |
| compute.hashCal | 1.150 / 1.140 / 0.755 | 0.883 / 0.631 / 0.468 | 1.515 / 1.411 / 1.371 | 0.388 / 1.007 / 0.959 | 0.103 / 0.200 / 0.664 |
| compute.normalCal | 0.745 / 0.451 / -1.821 | 0.844 / -0.221 / 0.926 | 3.087 / 1.797 / 1.432 | 1.946 / 2.294 / 1.643 | 3.460 / 0.314 / 0.275 |
| fact.saveAndFindByFileHash | 0.673 / 0.753 / 0.713 | 0.100 / 0.085 / 0.556 | 1.280 / 1.242 / 1.105 | 1.210 / 1.111 / 0.752 | 0.720 / 0.537 / 0.775 |
| erc721.mint | 0.767 / 0.475 / 0.323 | 0.496 / 0.553 / 0.312 | 1.125 / 1.326 / 1.349 | 0.697 / 0.844 / 0.786 | 0.334 / 0.526 / 0.701 |
| exchange.buyNow | 8.773 / 18.659 / 10.571 | -8.961 / 6.675 / 4.229 | -3.877 / 9.000 / 3.552 | 9.860 / 7.605 / -0.863 | -14.726 / -5.785 / -7.289 |

## 交互效应

| 方法 | 原式Interaction[CI] | 额外协同收益[CI] | 判断 |
| --- | --- | --- | --- |
| compute.bigNumCal | 0.142 [-0.903, 0.627] | -0.142 [-0.627, 0.903] | CI跨零，未分辨交互 |
| compute.hashCal | 0.218 [-0.214, 0.982] | -0.218 [-0.982, 0.214] | CI跨零，未分辨交互 |
| compute.normalCal | -1.937 [-3.902, 0.325] | 1.937 [-0.325, 3.902] | CI跨零，未分辨交互 |
| fact.saveAndFindByFileHash | -0.219 [-1.847, 0.282] | 0.219 [-0.282, 1.847] | CI跨零，未分辨交互 |
| erc721.mint | 0.026 [-0.802, 0.524] | -0.026 [-0.524, 0.802] | CI跨零，未分辨交互 |
| exchange.buyNow | 10.839 [-6.347, 18.064] | -10.839 [-18.064, 6.347] | CI跨零，未分辨交互 |


必须纠正符号：原式G0−G1−G2+G3为正表示组合比加性预测更慢（抵消）；为负表示组合额外节省（协同）。文件同时保留原式和相反数synergy_saving_ms。上述均同一block四项直接运算后统计，不根据三条独立Median推算。

## 阶段归因

| 方法 | 效应 | S0→S1节省 | S1→S2节省 | S2→S3节省 | export节省 | Close节省 | Invoke节省 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| compute.bigNumCal | Copy | 0.499 | -0.041 | 0.205 | 0.144 | -0.002 | 0.605 |
| compute.bigNumCal | A | -0.135 | 0.766 | 0.152 | 0.058 | -0.005 | 0.790 |
| compute.bigNumCal | A+Copy | 0.399 | 0.728 | -0.127 | -0.124 | -0.001 | 1.342 |
| compute.hashCal | Copy | 0.591 | 0.038 | 0.015 | -0.015 | 0.001 | 0.534 |
| compute.hashCal | A | 0.103 | 0.827 | -0.005 | -0.022 | -0.000 | 0.966 |
| compute.hashCal | A+Copy | 0.474 | 0.843 | 0.036 | 0.041 | 0.001 | 1.466 |
| compute.normalCal | Copy | 0.515 | 0.003 | -0.476 | -0.453 | 0.002 | 0.323 |
| compute.normalCal | A | 0.094 | 0.772 | -1.132 | -1.037 | 0.003 | 0.183 |
| compute.normalCal | A+Copy | 0.406 | 0.743 | 0.441 | 0.515 | 0.001 | 2.421 |
| fact.saveAndFindByFileHash | Copy | 0.422 | 0.008 | -0.016 | -0.024 | 0.001 | 0.212 |
| fact.saveAndFindByFileHash | A | -0.088 | 0.789 | 0.016 | 0.002 | 0.002 | 0.718 |
| fact.saveAndFindByFileHash | A+Copy | 0.443 | 0.794 | -0.007 | -0.017 | 0.002 | 1.243 |
| erc721.mint | Copy | 0.465 | -0.016 | 0.015 | 0.001 | 0.003 | 0.455 |
| erc721.mint | A | -0.037 | 0.711 | -0.002 | -0.001 | -0.000 | 0.591 |
| erc721.mint | A+Copy | 0.415 | 0.692 | 0.044 | 0.009 | 0.002 | 1.235 |
| exchange.buyNow | Copy | 0.160 | -0.021 | -2.914 | -3.007 | 0.002 | -0.967 |
| exchange.buyNow | A | 0.229 | 0.906 | 10.821 | 10.805 | 0.001 | 11.722 |
| exchange.buyNow | A+Copy | 0.206 | 0.917 | 0.848 | 0.825 | 0.002 | 1.884 |


Module编译/模板准备在Invoke外，另存MODULE_PREPARATION.csv。S0→S1是WASI/imports+Instance/Copy；S1→S2含WASI Initialize及_start；S2→S3包含CallMethod/Gas结算，不是CallMethod前的空白准备。export包含在CallMethod内；各阶段独立配对Median不可相加得到Invoke Median。A改变布局而非替换memclr实现，不能把整个阶段差强归因于清零。

buyNow完整执行真实六callee。BUY_NOW_WINDOWS.csv记录root export−六子Invoke之和的剩余窗口，包含桥接、字节码准备等多项；没有本轮独立测量clone/JSON/GC或纯Gas传播，不能把残余全叫子调用准备，也不能将Step29旧trace数值直接搬入。Store问题不是本轮已证实的性能归因。

## 顺序分层

| 方法 | 效应 | 左先执行True/False | 方向一致 |
| --- | --- | --- | --- |
| compute.bigNumCal | A | False: 0.790ms / N14；True: 0.775ms / N16 | True |
| compute.bigNumCal | Copy | False: 0.791ms / N14；True: 0.471ms / N16 | True |
| compute.bigNumCal | A+Copy | False: 1.365ms / N15；True: 1.319ms / N15 | True |
| compute.bigNumCal | A_given_Copy | False: 0.572ms / N16；True: 0.420ms / N14 | True |
| compute.bigNumCal | Copy_given_A | False: 0.145ms / N15；True: 0.520ms / N15 | True |
| compute.hashCal | A | False: 1.103ms / N16；True: 0.862ms / N14 | True |
| compute.hashCal | Copy | False: 0.521ms / N15；True: 0.741ms / N15 | True |
| compute.hashCal | A+Copy | False: 1.450ms / N15；True: 1.506ms / N15 | True |
| compute.hashCal | A_given_Copy | False: 1.074ms / N15；True: 0.818ms / N15 | True |
| compute.hashCal | Copy_given_A | False: 0.219ms / N13；True: 0.201ms / N17 | True |
| compute.normalCal | A | False: 1.861ms / N13；True: -1.302ms / N17 | False |
| compute.normalCal | Copy | False: -0.127ms / N13；True: 0.774ms / N17 | False |
| compute.normalCal | A+Copy | False: 2.823ms / N14；True: 1.201ms / N16 | True |
| compute.normalCal | A_given_Copy | False: 1.260ms / N16；True: 2.767ms / N14 | True |
| compute.normalCal | Copy_given_A | False: 2.758ms / N14；True: 0.243ms / N16 | True |
| fact.saveAndFindByFileHash | A | False: 0.715ms / N14；True: 0.718ms / N16 | True |
| fact.saveAndFindByFileHash | Copy | False: 0.152ms / N15；True: 0.283ms / N15 | True |
| fact.saveAndFindByFileHash | A+Copy | False: 1.184ms / N16；True: 1.256ms / N14 | True |
| fact.saveAndFindByFileHash | A_given_Copy | False: 0.882ms / N16；True: 1.057ms / N14 | True |
| fact.saveAndFindByFileHash | Copy_given_A | False: 0.358ms / N15；True: 0.815ms / N15 | True |
| erc721.mint | A | False: 0.754ms / N17；True: 0.385ms / N13 | True |
| erc721.mint | Copy | False: 0.686ms / N16；True: 0.329ms / N14 | True |
| erc721.mint | A+Copy | False: 1.225ms / N15；True: 1.245ms / N15 | True |
| erc721.mint | A_given_Copy | False: 0.532ms / N13；True: 0.851ms / N17 | True |
| erc721.mint | Copy_given_A | False: 0.569ms / N15；True: 0.458ms / N15 | True |
| exchange.buyNow | A | False: 5.608ms / N14；True: 17.251ms / N16 | True |
| exchange.buyNow | Copy | False: -6.018ms / N17；True: 5.800ms / N13 | False |
| exchange.buyNow | A+Copy | False: 0.926ms / N17；True: 2.843ms / N13 | True |
| exchange.buyNow | A_given_Copy | False: -0.863ms / N14；True: 9.233ms / N16 | False |
| exchange.buyNow | Copy_given_A | False: -11.738ms / N15；True: -6.079ms / N15 | True |


顺序、Module准备顺序和进程chunk位置有关联，分层方向不是唯一缓存/调度因果。全部不利样本保留。每批每组位置数2或3，实际顺序存command/block；没有100ms业务Sleep。每进程最多2目标调用，buyNow1目标；编译、init在外但其状态影响仍可能留在目标窗口，这是受控串行实验局限，不冒充节点池。

## 覆盖与正确性/资源

已有8类Go合约，优先完成六方法（4个root合约）；identity真实callee已覆盖，其独立方法及bigInput/itinerary/raffle扩展仍blocked，详见CONTRACT_INVENTORY。不是“8合约全部通过”。一般异常、真实Table函数身份、节点并发和长寿命回收未验证。

资源与正确性详情见CORRECTNESS.md/RESOURCE_SUMMARY.csv。出现STOP时对应配置只能分析保留现场；本报告不以缺失数字当0。当前进程outcome失败数0。

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
