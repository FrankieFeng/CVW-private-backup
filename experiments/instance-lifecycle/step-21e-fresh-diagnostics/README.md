# Step-21E：Fresh基线、Gas与Store生命周期诊断

分支 `experiment/step21e-fresh-diagnostics`，独立worktree `.worktrees/cvw-step21e`，父Step21D `87eb925`；审计基准21B `620650d`、夹具来源21C `32d257b`。未修改生产VM，未覆盖21B/C/D，未推送。

| 问题 | 本轮结论 | 证据 |
|---|---|---|
| Store共享/回收 | 原池同合约多个Instance共享Store；无同步创建/执行/删除存在静态不安全路径。21A那次仅证明区间重叠，未抓到native race。E仍用固定OS线程owner、每Fresh独立Store/Module/WASI、显式scope清理 | [所有权审计](STORE_OWNERSHIP.md) |
| Gas差异 | 相同输入/初始账本/结果/读写集/事件仍复现：fact冷热差594，ERC721差4379；buyNow根差4379，首次来自第6次真实transferFrom。已缩到guest host边界间，JSON编码缓存是候选而非完整因果证明 | [Gas分析](GAS_ANALYSIS.md) |
| normalCal Fresh更快 | 两个反向顺序短批export均值R0/R1为77.398/75.912ms、78.270/75.251ms；小幅同方向可观测，历史约8.294ms幅度及原因尚未解释。Fresh整笔Invoke仍更慢 | [normal分析](NORMALCAL_ANALYSIS.md) |
| 约0.56秒Module成本 | D每次Fresh重建Engine/Store并编译引入；原ChainMaker按pool缓存Module。微型串行多实例与可信Serialize→独立目标Store Deserialize能力通过，实际业务缓存路径尚未认证 | [Module分析](MODULE_ANALYSIS.md) |

共12独立进程通过；[验证详情](VALIDATION.md)、[逐进程结果](processes.csv)、[原始日志](raw_logs/)、[源码diff](source.patch)、[行号索引](SOURCE_INDEX.md)、[恢复进度](PROGRESS.md)。没有以无崩溃证明安全，没有放行并发Fresh或100次。

Step22可继续小规模串行设计与功能预检；**尚不具备可信的连续负载Copy性能实验条件**。必须明确冷态复制起点并逐层保证Gas等价、选择并验证业务Module缓存/目标Store绑定、解决长期WASI回收及供给协议。native精确构建来源仍缺；normal未知影响性能归因，但不阻止有限功能诊断。原容量修复改变grow裁剪、库存和供给，不能把旧10–15倍或D重新编译结果叫原生产池性能，详见[NEXT_STEP](NEXT_STEP.md)。
