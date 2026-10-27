# Step-22：Copy方案串行性能与正确性验证

2026-10-26（Asia/Shanghai）。**已真实执行**原始随机顺序三批及单列的平衡顺序三批。既有Host区间Copy减少的主要是S0→S1静态初始化：NewInstance省掉active Data初始化，再支付Host Copy成本。未改Copy算法，未启用Arena/PB，未运行原池或节点并发压测。

在顺序平衡补充中，compute/ERC721完整串行Invoke分别节省中位数0.738/0.903ms，6/6对正向；fact一批接近零；exchange主实验第三批反向。**不能把这些短小样本写成通用稳定收益或生产收益**。原主实验完整Invoke的CI全部跨零，仍全部保留。

## 测量范围

每合约/变体一个所有者线程上的Store+Module缓存；每次新WASI、新Instance，串行创建→Copy（A1）→WASI.Initialize/_start→SetGas/真实业务→Gas/result→CallDeallocate/Instance scope同步关闭。完整Invoke包含以上每次调用路径，**不含一次性模板/编译及最终Module/Store缓存销毁**。这是Step21D基础上的新串行参考管理器dRuntime.Invoke，真实SimContext和业务WASM执行；不是生产RuntimeInstance.Invoke、原池TPS或真实节点/客户端结果。

## 原始主实验，单位ms

三个单合约各3独立进程×3配对；exchange各3个独立配对批、每变体独立进程执行1根及6个真实子调用。全部保留首个正式样本，无额外预热或Sleep。

| 合约/方法 | A0 Median | A1 Median | A0 P95 | A1 P95 | 配对节省 Median [95% CI] | 对数/独立批 |
|---|---:|---:|---:|---:|---:|---:|
| compute.bigNumCal | 5.220 | 4.922 | 6.151 | 5.403 | 0.695 [-0.254, 1.280] | 9/3 |
| fact.saveAndFindByFileHash | 5.454 | 4.843 | 5.739 | 5.610 | 0.301 [-0.056, 0.947] | 9/3 |
| erc721.mint | 5.741 | 5.225 | 6.244 | 5.488 | 0.829 [-0.170, 1.143] | 9/3 |
| exchange.buyNow | 68.782 | 63.760 | 75.288 | 82.150 | 11.528 [-15.765, 12.965] | 3/3 |

“配对节省”是每对A0−A1的中位数，**不是两组Median相减**，因此表中两者可能明显不同。P95为最近秩；N≤9时等于最大值。95%CI为先抽3个batch、再抽pair slot的10000次配对bootstrap（seed22026026）；仅作探索性区间，3批不能证明长周期稳定。

## 顺序平衡补充，独立统计，单位ms

审计发现主实验每单合约A1先7对、A0先2对；其中compute两次反向在A0先，fact/ERC不满足统一关系。不能据此认定顺序是原因。补充保持同一build4/业务/Gas/上限；每进程只2对、恰好一对A0先一对A1先，3独立批。种子只按顺序选择，不按耗时选择。原始数据未剔除、未替换、未与补充混合。

| 合约/方法 | A0 Median | A1 Median | A0 P95 | A1 P95 | 配对节省 Median [95% CI] | 对数/独立批 |
|---|---:|---:|---:|---:|---:|---:|
| compute.bigNumCal | 5.257 | 4.477 | 5.812 | 4.783 | 0.738 [0.575, 1.356] | 6/3 |
| fact.saveAndFindByFileHash | 5.476 | 4.763 | 5.753 | 4.981 | 0.719 [0.002, 1.769] | 6/3 |
| erc721.mint | 4.868 | 4.024 | 6.434 | 5.243 | 0.903 [0.568, 1.949] | 6/3 |

compute两种顺序各3对均为正向，支持Copy收益不完全由原7:2顺序失衡解释；ERC721也6/6正向。fact 5/6正向，第二批配对均值仅0.002293ms（两样本均值=中位数），不足以称稳定；主实验三个合约CI跨零的事实不因补充变更。详见balanced_*、execution_order.csv、order_sensitivity.csv。

## 正确性与安全

预检逐实例在_start前核对全Memory SHA；A0/A1业务返回、根Gas、读写集、事件、等价初始/最终账本hash全部匹配；三个单合约主实验+预检各10对，平衡补充各6对；exchange主实验+预检4对，根与六个真实callee的Gas/结果/顺序都核对。所有调用均Fresh，未复用业务Instance。非Data section原字节相同，格式验证通过。

**真实Table函数身份、内部Globals动态比较、异常/OOG全路径仍not_tested**；不把静态section保持不变认定为所有动态状态均验证。标量模块做了实际写Memory后新Instance仍全零的隔离预检；真实合约在顺序fresh实例间的S1哈希/业务结果隔离已检查，未验证并发隔离。见CORRECTNESS.md与correctness.csv。

共33个有界测试进程（含探索和所有预检/补充）正常退出；外采样+边界日志最大RSS 765.62MiB、线程176，未触发阈值。**Store缓存存活时线程随WASI创建累积**：单合约主实验结束125线程、最终owner关闭约13；exchange176→约16。只有退出进程后资源终结可确认，不认证长寿命缓存有界，不允许据此直接扩大连续100次或并发池。

## 准备与容量

| 合约 | 模板准备ms | A0 Module准备ms | A1 Module准备ms | Image MiB | 区间数 | 每次Copy Bytes |
|---|---:|---:|---:|---:|---:|---:|
| compute | 11.641 | 581.125 | 559.269 | 3.0625 | 49547 | 1167957 |
| fact | 12.498 | 623.490 | 609.636 | 3.1250 | 50467 | 1209635 |
| erc721 | 11.658 | 669.139 | 636.615 | 3.1875 | 52954 | 1273888 |
| exchange | 5.837 | 548.887 | 527.791 | 2.9375 | 46378 | 1080586 |
| identity | 11.339 | 633.794 | 624.214 | 3.1250 | 50781 | 1216964 |

模板成本含完整SHA审计；Module准备含validate/compile及持久metadata，不是单纯编译函数。两者均独立于每次Invoke，preparation.csv还记录实验双组总准备与最终cache close。Image+16×区间数只是部分Go空间下界，plan还持有noData代码，底层capacity/Module/Store/native线程成本另计。template_cost.csv给出下界，native缓存精确大小未测。原始设计的每次Store编译约0.5–0.7秒不能算入Copy收益，本轮实际每变体每合约只准备一次。

A0/A1在同进程都保留模板和两个Module；exchange分进程也准备同样两组Module。因此RSS是**双组实验配置**，不是生产Copy独占增量RSS。未隔离的native资源成本和宽CI也不足以给可靠摊销次数。

## 版本、交付和下一步

分支 `experiment/step22-serial-static-copy`，父87eb925；实验代码冻结提交 `4160b271fda1bba587dd0098d7069e9e74b5a907`；固定Go1.25.0/native6.0.1（SHA见environment）。最终测量binary `f83ff5524108f56290767d2b23426f8de4b78454f27f69b5b09db3f9ae89fbc7`。所有原WASM/hash、noData/template SHA在variants.csv；仅ERC721与Step16旧binary不同，沿用Step21D候选，本轮两组完全相同。SDK精确原二进制构建来源未重新认证。

- [RESULTS.md](RESULTS.md)：完整阶段表及exchange反向样本定位。
- [AUDIT.md](AUDIT.md)、[source.diff](source.diff)、[audit/source_hashes.json](audit/source_hashes.json)：真实函数/行号、版本和增量源。
- [CORRECTNESS.md](CORRECTNESS.md)、[correctness.csv](correctness.csv)、[balanced_correctness.csv](balanced_correctness.csv)：通过范围与not_tested。
- [samples.csv](samples.csv)、[summary.csv](summary.csv)、[paired_effects.csv](paired_effects.csv)、balanced_*：全部原始Invoke行（含init、子调用、预检），性能筛选明确保留在脚本中。
- [raw_logs](raw_logs/)、[resource_summary.csv](resource_summary.csv)、[template_cost.csv](template_cost.csv)、[environment.json](environment.json)：原命令、receipt、资源与准备成本。
- [RUNNING.md](RUNNING.md)、[PROGRESS.md](PROGRESS.md)：复现、保护、恢复与回滚。只提交独立分支，不push。

下一步应先拆分WASI/import准备窗口的波动及解释Store持有的线程生命周期，在同样有界进程中做更多独立、顺序平衡批次；Table/异常语义仍需补齐。不能把本轮成功视为默认共享Store池或生产启用许可。本轮不继续实现优化或节点实验。
