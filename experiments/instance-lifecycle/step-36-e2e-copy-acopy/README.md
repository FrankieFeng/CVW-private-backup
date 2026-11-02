# Step-36：安全Fresh / Copy / A+Copy / A-only真实节点E2E

已完成8个独立部署Go/WASM业务合约、37个业务方法的四组对照。每方法3个独立批次，共444个正式窗口、1728次有效提交；一般每组12次，identity.alterAdminAddress每组3次、raffle.raffle每组9次。无生产代码覆盖、无并发压测、无远程推送。

G0 Fresh；G1 Copy；G2 A+Copy；G3 A-only。同源Step18/33家族，无B1。原始样本、失败窗口和反向收益均保留。测量SDK同步提交响应，而非仅AddTx ACK；提交结果用链上RWSet查询与重启后读回复核。

- G0→G1：37方法中，CI全正3项，全负1项；三批配对中位数均正4项。
- G1→G2：37方法中，CI全正1项，全负1项；三批配对中位数均正6项。
- G0→G2：37方法中，CI全正3项，全负1项；三批配对中位数均正6项。
- G0→G3：37方法中，CI全正2项，全负1项；三批配对中位数均正6项。

结论：VM内部初始化收益不能自动推出客户端收益。本轮多数方法E2E CI跨零，少数出现正/负信号；A+Copy没有得到普遍稳定优于Copy的证据。具体方法、P50/P95和TPS见E2E_RESULTS.md与TPS_RESULTS.md。单客户端TPS不代表节点最大吞吐。

RSS观测峰值1075.84MiB、OS线程峰值45，原1536MiB守卫保留。148次重启及36次真实失败/回滚检查通过。不能据此认证所有异常路径、Table身份或原池并发。

复算：`python3 scripts/analyze.py`，随后`python3 scripts/report.py`。脚本只读原始JSON/日志并重建本目录派生CSV/报告，不启动节点。执行实验入口scripts/experiment.py，专项raffle脚本retry_raffle.py，重启验证postcheck_all.py；均有已完成结果检查，禁止无理由重跑。

只有3个独立批次；一般每组12次，alterAdminAddress每组3次，raffle每组9次。95%CI采用批次/槽位两层成对bootstrap 10,000次；3个批次不足以稳定估计总体尾部或消除环境/顺序混杂。37方法、多对照未作多重比较校正，因此局部CI为探索性信号，不是普遍收益证明。四组顺序平衡但三个批次无法覆盖四个位置的全部排列。

详见EXPERIMENT_DESIGN.md、SDK_TIMING_CODE.md、TPS_MEASUREMENT.md、SAFETY_GATE.md、CORRECTNESS.md。
