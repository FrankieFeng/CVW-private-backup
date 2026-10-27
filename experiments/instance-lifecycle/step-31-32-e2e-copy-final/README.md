# Step-31/32：真实节点安全准入与Copy E2E收尾

**本轮结论C：真实节点安全门槛未通过，Step32未启动。** 新节点/SDK请求/E2E配对/完成轮次均0；没有把历史样本或本轮小WAT测试冒充真实E2E。

已实际复验两个既有有界生命周期检查并通过，确认测试协议可复用的一部分；但真实节点Store/Module锁前准备、native Finalizer、Reset/Stop与在途排空仍缺完整owner适配，不能直接搬测试manager进节点。首次配置拒绝保留，不隐去。VM/绑定/SDK/Gas代码改动0，没有生产修改、推送、PPT、新优化或clone内部研究。

先读[SAFETY_GATE](SAFETY_GATE.md)，再读[AUDIT](AUDIT.md)、[RESULTS](RESULTS.md)、[计时边界](TIMING_BOUNDARIES.md)、[正确性](CORRECTNESS.md)。E2E_SAMPLES只有表头，PAIRED_EFFECTS和THROUGHPUT为明确not_run占位、缺失指标空值；RESOURCE_SUMMARY只含3个protocol/config进程，不能解读为节点资源。

分支experiment/step31-32-e2e-copy-final，父bb2772d9；源码/历史快照及hash见audit。脚本归档既有检查命令、失败及资源监视，**最终gate失败后不应继续运行检查或节点**。离线复算仅：

```bash
python3 -B scripts/archive_and_report.py
python3 -B scripts/verify.py
```

复算在原独立worktree中运行；IDE镜像用于阅读。所有原始probe日志、命令、outcome、资源、配置纠正与停止记录保留，source/SDK版本未改，历史原始数据未覆盖。旧Step20实际路径为step-20-e2e-performance-attribution，不是原e20路径。

可以结束当前研究阶段并开始总结：支持局部VM初始化收益与有限语义证据，真实客户端收益尚未确认；无需把clone内部机制、A/B1、COW或原池高并发继续扩为当前结题条件。下一项工作应单列节点生命周期适配及回收验证，完成后最多两轮E2E。回退无需改生产；本轮所有自有进程已退出，不停止任何其他现有节点。
