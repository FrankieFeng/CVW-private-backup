# Step-24B：Copy完整Invoke收益确认

2026-10-27。分支experiment/step24b-copy-invoke，父Step23 ba57368，Copy/计时基于Step22 394d291。独立worktree .worktrees/cvw-step24b，未修改生产VM、Gas规则、Copy算法或生命周期guard，未覆盖22/23，未push。

**本轮三个单合约的初始化净节省传递到完整Invoke；buyNow只得到小样本且强波动结果，不能泛化稳定收益。**

| 合约 | 对数/独立批 | A0 Median/P95 ms | A1 Median/P95 ms | 配对节省Median [95%CI] ms | 正向比例 |
|---|---:|---:|---:|---:|---:|
| compute.bigNumCal | 90/3 | 5.020/6.758 | 4.290/5.981 | 0.670 [0.468, 1.014] | 74/90 (82.2%) |
| fact.saveAndFindByFileHash | 90/3 | 5.178/6.895 | 4.590/5.962 | 0.750 [0.654, 0.967] | 72/90 (80.0%) |
| erc721.mint | 90/3 | 5.360/7.474 | 4.692/6.241 | 0.711 [0.485, 0.957] | 75/90 (83.3%) |

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
