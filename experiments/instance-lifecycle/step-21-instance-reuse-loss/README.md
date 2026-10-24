# Step-21-多合约Instance复用性能损失复现

2026-10-24。**已完成六方法的输入/加载小样本检查；五方法通过业务检查，exchange失败。正式套件在首批compute.bigNumCal R1出现维护排空超时后停止，未完成六方法各3批。**六个正式比较均保留为E，不以历史或smoke数字填补缺失。

## 实际执行与结果

| 方法 | 历史倍率 | 小样本R0/R1业务成功 | 正式进展 | 主分类 |
|---|---:|---|---|---|
| compute.bigNumCal | 1.41 | 3/3、3/3 | a批各100次业务成功；R1排空失败，后续停止 | E |
| compute.hashCal | 2.78 | 3/3、3/3 | 未开始正式组 | E |
| compute.normalCal | 1.55 | 3/3、3/3 | 未开始正式组 | E |
| erc721.mint | 13.09 | 3/3、3/3 | 未开始正式组 | E |
| fact.saveAndFindByFileHash | 7.78 | 3/3、3/3 | 未开始正式组 | E |
| exchange.buyNow | 15.27 | 0/3、0/3 | addWriteList失败，未扩大调用 | E |

记录24个实际条件进程：12个smoke（36次）、10个race-smoke（30次）、2个正式条件（200次），共266次调用，260次预期业务成功、6次exchange失败。诊断样本不混入主统计；100次调用是一个进程/池内的序列，不能当成100次独立实验。

仅首批已返回调用的**诊断值**如下，不认证为完整正式对照或三批可重复结论：

| compute.bigNumCal，100次/组 | R0 | R1 |
|---|---:|---:|
| Mean InvokeTime，ms | 0.309588 | 3.746388 |
| P50 / P95，ms | 0.251409 / 0.424505 | 3.554173 / 5.054063 |
| 成功数 | 100 | 100 |
| 成功数/成功InvokeTime总和，等效TPS | 3230.10 | 266.92 |
| GetInstance平均观测窗口，ms | 0.045134 | 3.373651 |
| 紧贴channel接收的平均耗时，ms | 0.040507 | 3.320474 |
| 空池分支次数 | 1 | 100 |
| Gas | 105920×100 | 105920×100 |
| 创建开始/完成数 | 6 / 6 | 112 / 112 |
| 关闭完成数 | 6 | 101 |
| 入池开始/完成数 | 5 / 5 | 111 / 110 |
| 退出检查 | 通过 | **维护排空超时** |

诊断倍率12.101倍、等效TPS下降91.74%，大于历史bigNumCal的1.41；但因R1维护失败且缺少3个有效独立批次，**不能标为A类正式结论**。baseline_comparison.csv将这些数字放diagnostic列，正式TPS留空。

R1在输出原末尾TPS汇总之前已因排空超时失败，诊断TPS由100条返回的executionTime按原成功数/总时长公式重建；没有将Go FAIL说成成功完成的原汇总。

同批100次总Invoke增量343.680ms，channel接收窗口增量327.997ms，约95.44%。这是同一批时间总和的分解，未通过两个中位数相减。它支持本例供给等待占主要增量，不证明六种合约都如此；CallMethod包括分配/参数/导出调用，不等于纯业务函数。

该例CallMethod均值R0/R1为0.228/0.306ms，远小于约3.437ms的Invoke增量；但供给包括创建、WASI/_start和调度，不能据此认定静态Data初始化本身占95%。

## 为什么停止

R1在业务结束后库存达到容量10，worker又创建了一个实例并停在无消费者的入池发送：有enqueue_before、无enqueue_done。112创建减101关闭=11个未关闭实例；其中10个在队列，1个等待入池。任务排空超时使Go FAIL，后续所有正式组未启动。RSS峰值约712MiB、线程195，未越过1536MiB/220阈值，不能称为OOM。

详见ANOMALIES.md。没有扩大队列、跳过检查、增加全局Store锁或修改业务量继续采集。全部自启进程已停止；旧Step-19/19A/20数据与生产源码未覆盖。

## 设计与计时

优先保留原`runtime_test.go:TestInvoke → newVmPool → InvokeTime`入口，显式传方法/名称/100次数。源码基于474da33；实际编译源码077a8cb，完整最小差异source.patch。R0/R1使用同一个普通测试binary，仅CM_REUSE_EXPERIMENT切换生命周期：R0归还池，R1关闭并异步remove/add补池。池初始空、min5/max10/grow5、不预建，不加Sleep或剔除首调用。3批顺序已预定义于PROTOCOL.md，但未执行完。

`TPS(callMethod only)`标签不准确：主分母是完整InvokeTime.executionTime，包括GetInstance/等待、SetGas、CallMethod、Gas读取与defer归还；编译/池验证在窗外。原InvokeTime源文件和开始/结束位置未改变。新增channel计时紧贴`instance = <-p.instances`前后，用time.Now/time.Since；非空分支未执行阻塞接收，记0。GetInstance为返回前观测窗口，观测输出开销未校准，不能当作无扰动计时。

输入沿原规则生成后冻结，见inputs/及SHA；ERC721 tokenId 1…100逐次唯一，fact时间固定，两个模式逐条输入哈希相同。参数哈希采于调用后，包含SimContext加入的context pointer/空bytecode字段；当前相应索引仍完全一致。保留原SnapshotMock和空contractId.Name夹具，不能宣称真实链上状态正确性。

窗口外增加维护任务追踪、worker barrier及关闭完成检查，目的为检测退出截断；不在两次Invoke之间等待，不改变补池策略或Store执行所有权。这与旧快速退出的TestInvoke有已披露差异。源码改动和普通/race构建哈希见ENVIRONMENT.md，额外JSON观测对两组相同但开销未独立校准。

## 正确性、安全与分类

每笔必须同时核对code及预期结果：compute三个确定输出，mint success，fact JSON字段与输入一致，buyNow success；Go PASS不代替业务成功。R1正式100个业务Instance ID均不同；R0有100次reuse、无drop，R1有100次drop、无reuse。Gas逐笔保存，不改Gas逻辑。

ERC721/fact的smoke已出现复用Gas降低；R0只能作性能参考。Table、真实账本持久化/授权、跨合约成功链、native Store并发安全均未认证。Go race小样本没报告竞争，不等于native安全。严格资源、超时和进程退出保护见PROTOCOL.md及每次命令。

分类规则在正式运行前登记。未完成/不安全组为E，未测不归为B/C/D，也不为了提高倍率改WASM、参数量或选择有利数据。

## 对研究问题的回答

1. 六方法的有效三批倍率尚不能给出；只有bigNumCal的首批诊断倍率12.10，其余不能用smoke替代正式统计。
2. 没有完成可接受的A类正式结果。诊断bigNumCal数值达到历史，但退出失败使其仍为E。
3. 其他方法是未完成，不是已证实没达到；exchange为原测试环境前置条件不足，不能比较失败路径。
4. 当前bigNumCal约95.4%的额外时间对应channel接收窗口，主要证据是供给等待；不能泛化所有合约或归因纯业务。
5. 尚无足够正式数据判C或D，不能预先宣称normalCal损失小或R1更快。
6. 数据支持本例Fresh供给延迟值得研究，同时暴露控制/退出缺陷；不足以证明六方法普遍创建瓶颈，也不能跳过安全修复直接推广优化。
7. 后续Copy适合先验证短业务、等待占比高且结果/Gas可对齐的条件。具体合约排序需修复后完成主矩阵；目前不依据历史倍率给新合约承诺收益。本轮未做Copy或Step-20端到端归因。

## 文件和复核

- baseline_comparison.csv：六方法、历史参考、E类原因和独立诊断列。
- per_run_summary.csv：24个实际条件与34个未运行正式条件；未运行调用数0、性能留空。
- planned_matrix.csv：全部36个正式计划条件，没有删除失败/未运行组。
- samples.csv、correctness.csv：266次输入哈希、结果、Gas、逐调用计时及两模式检查。
- creation_samples.csv、lifecycle_events.csv、diagnostic_effects.csv：创建、库存、关闭、等待和退场证据。
- raw_logs/：全部原始日志、systemd命令、资源、结果；失败日志保留。
- scripts/：运行器、套件控制、完整分析脚本；environment.json、ENVIRONMENT.md、cases.json、source.patch：版本、输入、构建与差异。

只读复核（不会启动测试）：

```bash
python3 -B CVW/experiments/instance-lifecycle/step-21-instance-reuse-loss/scripts/analyze.py
```

原执行示例：`scripts/run.py --case compute-bigNumCal --batch a --policy R0 --n 100`；所有实际完整命令见raw_logs/*-command.json。当前有退出缺陷，禁止直接通过更换标签重跑扩量；脚本拒绝覆盖已有结果。回滚仅停止/弃用本实验分支与binary，不reset/clean生产脏工作区，不删除旧实验数据。
