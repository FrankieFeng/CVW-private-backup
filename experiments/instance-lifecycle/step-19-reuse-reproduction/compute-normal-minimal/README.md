# compute.normalCal：补充R0/R1低负载测量

2026-10-20。此前normalCal未采集，并非无法测试。本轮实际启动隔离节点完成两批同WASM对照，没有Copy/A/P/Renew、同步fresh或根VM串行锁。生产代码未修改，四个实验节点均已停止。

## 结果

主指标为vm_factory.go原始INFO的RuntimeInstance.Invoke起止纳秒，日志TPS=`N/ΣInvokeTime`，不是成功提交TPS。部署、预热及查询排除；逐TxID核对仅一条成功normalCal日志。40条测量起止均与辅助REUSE_VM一致。全部60次业务调用（含预热）查询到成功提交，返回`success normalCal: 666`。

| 条件 | N/模式 | R0平均Invoke(ms) | R1平均Invoke(ms) | R0日志TPS | R1日志TPS | R1日志TPS下降 | 空池等待 |
|---|---:|---:|---:|---:|---:|---:|---|
| a：先R0后R1 | 10 | 70.1090 | 70.0870 | 14.2635 | 14.2680 | -0.03% | 未观察到 |
| b：先R1后R0 | 10 | 71.0979 | 68.9938 | 14.0651 | 14.4941 | -3.05% | 未观察到 |
| 合并描述 | 20 | 70.6034 | 69.5404 | 14.1636 | 14.3801 | -1.53% | 未观察到 |

合并R0 Median/P95为70.5874/74.5054ms，R1为68.8037/72.5493ms。P95 nearest-rank；两批小样本，无置信区间和稳定性结论。未观察到复用优势，不能将约1.5%的反向差异宣称为不复用优化。

与用户提供历史normalCal 408.7/264.3（下降35.33%）不一致。本轮数值不能直接替代历史环境，也没有确认历史统计公式与本轮完全相同。相比此前bigNumCal的约0.37ms，这是不同方法，不能混用。

## 固定对象与输入

- 使用我们此前Step-19的同一compute原始WASM：`../step-16-chainmaker-copy/artifacts/compute/original.wasm`（以instance-lifecycle目录为基准），SHA256 `e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507`。没有改用恢复的toolkit候选，也没有重新编译。原始路径见environment.json。
- normalCal输入为空，两模式每次相同。现存compute源码该方法有10,000,000次循环；本轮所有调用返回Gas为100000180。没有验证历史实际执行循环数或用Gas倒推历史版本。这个WASM中bigNumCal曾被改为100轮，不能据此将normalCal也当成100轮。
- node二进制SHA256 `3b48ebad57c36c08a135fb3640607fd30382861716917fd2bb90033d17d7fc18`，VM源码基准`eac4f2942151dc346dace728f1f9e7651c83615f`，node源码`552df3f464d8e113dbca03c5da385c4ff1afd0b0`；客户端SDK-Go/v2 v2.4.0。版本、输入和二进制哈希核对见environment.json。运行时沿用既有WASI freelist及Close后补池逻辑，与历史是否相同未知。
- 原库packaged Wasmer6.0.1、宿主Go1.25.0；无版本升级。

## 运行与安全边界

复用`erc721-minimal-difference/run_low.py`的有界串行框架，只改输出、方法、WASM、空输入和隔离网络配置；脚本完整保存于run_low.py。每个模式独立空账本，单验证节点TBFT、block interval=20ms、初始池5/max10、GOMAXPROCS=4，同一二进制通过`CM_REUSE_EXPERIMENT=R0/R1`切换复用。

每批每模式5次预热+10次测量。最多一个业务请求在途，最小200ms起点间隔；下一笔前等待已观测创建/关闭/入池完成，补池超时2s。没有通过全局锁修改池行为。此控制不构成任意Store并发安全认证，不运行压力档。

MemoryMax=2GiB、TasksMax=256、RuntimeMax=90s、TimeoutStop=5s；软阈值RSS<1536MiB、部署后增加<256MiB、线程<220、单请求15s。全部运行未触发阈值，执行错误0，未走GetInstance空池阻塞分支。

R0每批创建6个（验证1+预填5）；R1每批22个（另有部署init+15业务对应16次替补）。R1替补创建Median分别4.3375/5.0679ms，主要在后台。RSS采样峰值R0为575.68/563.87MiB，R1为651.52/650.83MiB；部署后增长R0约98MiB，R1约170MiB。线程采样峰值最高97。短测不能证明内存长期有界，资源原始数据见resources.jsonl。

原始计时边界位于独立工作树的`chainmaker/chainmaker-vm-wasmer/vm/v2@v2.4.0/vm_factory.go:432–440`。包括GetInstance/潜在等待、SetGas、业务及归还；不包含提前完成的实例创建和_start，异步Close/grow不保证在窗口内。后台创建不能重复加到Invoke中位数。

## 正确性与局限

20组测量输入配对返回相同、报告Gas均为100000180、无事件；所有60次调用（含预热）均验证了提交结果。没有为本轮独立实现Table/全部异常/跨合约或fresh内存隔离验证，correctness.csv明确不认证全部语义。R0仅作隔离性能参考，不推广为生产正确方案。历史WASM/机器/负载/统计公式未完全对齐，不能归因历史差距。

## 原始资料、复核、回滚

`samples.csv`40条测量及原始日志位置；`summary.csv`四个条件；`comparison.csv`合并；`correctness.csv`返回/Gas；`boundary_check.csv`计时交叉核对；`requests.jsonl`原始SDK及提交查询；`resources.jsonl`资源采样；`artifact_hashes.json`配置、原始日志哈希；`environment.json`环境；`{a,b}/network/{baseline,optimized}/`保存原始配置、日志及账本。baseline/optimized只是旧客户端命名，实际为R0/R1。

只复核已有数据，不启动节点：

```bash
python3 -B CVW/experiments/instance-lifecycle/step-19-reuse-reproduction/compute-normal-minimal/analyze.py
```

run_low.py检测已有requests/stdout会拒绝覆盖；复跑需另建隔离配置和空账本，不能删除本轮资料重用目录。所有`step19-normal-min-*`进程已停止；回滚只需弃用实验分支。证书、账本和二进制不纳入报告提交，生产配置与已有脏工作区不变。
