# Step-19：ERC721同WASM最小差异验证

2026-10-20。只运行ERC721.mint；没有运行其他合约、重新编译运行时或加入Copy/A/P/Renew。**候选WASM低负载两批结果为1.17倍、1.51倍，合并描述为1.33倍，没有复现历史约13.09倍的差距。较高压力未运行：共享Store并发安全条件未通过。**这不能证明提高压力后也不存在大幅差距。

## 结果

主指标来自实际`vm_factory.go` INFO日志的原始起止纳秒。日志TPS定义为`N / Σ((end_ns-begin_ns)/1e9)`，不是成功提交TPS。历史公式仍未获得原脚本确认；本轮按用户指定公式计算，不宣称历史已确认采用此公式。

| 压力档 | R0平均Invoke(ms) | R1平均Invoke(ms) | R0日志TPS | R1日志TPS | 性能比R0/R1 | 池等待 |
|---|---:|---:|---:|---:|---:|---|
| 低负载a，先R0后R1，N=10/组 | 0.5692 | 0.6662 | 1756.86 | 1501.07 | 1.170 | 未走空池阻塞分支 |
| 低负载b，先R1后R0，N=10/组 | 0.4755 | 0.7198 | 2103.01 | 1389.26 | 1.514 | 未走空池阻塞分支 |
| 两批合并描述，N=20/组 | 0.5224 | 0.6930 | 1914.41 | 1443.01 | 1.327 | 未走空池阻塞分支 |
| 较高压力 | 未测 | 未测 | 未测 | 未测 | 未测 | Store安全检查未通过 |

合并值按全部样本的`N/Σtime`计算，没有平均两批TPS。合并R1日志TPS比R0低24.62%。样本小，未报告置信区间、稳定性或生产吞吐收益。

| 批次/模式 | N | Median(ms) | P95(ms) | 总创建数 | 其中替补创建数 | 替补创建Median/P95(ms) | RSS采样峰值(MiB) | 部署后RSS增量(MiB) | 线程采样峰值 |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| a/R0 | 10 | 0.5100 | 1.0736 | 6 | 0 | 不适用 | 632.94 | 100.63 | 95 |
| a/R1 | 10 | 0.6481 | 0.8018 | 22 | 16 | 4.5014 / 6.8192 | 695.49 | 173.97 | 95 |
| b/R1 | 10 | 0.6829 | 1.0469 | 22 | 16 | 4.2126 / 6.7503 | 700.75 | 174.04 | 95 |
| b/R0 | 10 | 0.4739 | 0.5266 | 6 | 0 | 不适用 | 634.27 | 100.67 | 95 |

P95采用nearest-rank；每组仅10条，P95即该组最大值。资源指标来自离散采样，不是连续峰值；RSS增量为部署后到最后一次采样，不是单Instance大小。替补创建统计覆盖部署init+5次预热+10次测量，共16次，不能与只含10次mint的Invoke耗时逐项配对。

## 固定对象与版本

- WASM：`chainmaker-test-toolkit-master/chainmaker-performance-test/contract/claim_demo/erc721-go.wasm`，5,178,387 Bytes。
- SHA256：`a692e438748bc0989095ac5eceda75d1eb106b61fcc29a34567bd465da2baeba`。这是恢复的候选，**没有证明就是历史PPT所用二进制**。
- VM运行时源版本：`eac4f2942151dc346dace728f1f9e7651c83615f`；记录工作树分支：`experiment/step19-erc721-minimal`。
- node源版本：`552df3f464d8e113dbca03c5da385c4ff1afd0b0`；节点SHA256：`3b48ebad57c36c08a135fb3640607fd30382861716917fd2bb90033d17d7fc18`。
- 客户端SDK-Go/v2 v2.4.0；客户端SHA256：`a7d394281451e7cb005b35d508eae7301e525cf91d32905167db33a08d3cc223`。宿主Go1.25.0；本轮没有重建合约，也未恢复候选的完整构建来源。
- 两组加载相同packaged Wasmer6.0.1，库SHA256：`dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。
- 当前共同运行时已有WASI freelist及先Close、再发送替补信号的资源处理；没有在本轮新增。它与历史运行时是否相同未知，因此不是历史二进制的严格重演。

每个模式使用独立空账本，单验证节点TBFT，block interval=20ms、GOMAXPROCS=4、默认池initial=5/max=10及后台grow。节点配置除模式、隔离路径/端口外保持一致。没有使用同步fresh或根VM串行锁。

部署参数为空。固定15个mint输入见`inputs.json`，两模式及两批使用相同顺序：

- `to=8acfaca5eeec9f6f7c23c4ffac969b86f27799b0`
- `metadata=http://chainmaker.org.cn/`
- `tokenId=111111111111111111111112 + i`，i=0…14，十进制字符串，每个账本内唯一。按恢复脚本的大整数递增规则生成，不使用随机碰撞输入。

前5次预热，后10次进入主指标；部署、预热、查询及非mint调用全部排除。每个已保存请求TxID必须对应且仅对应一条成功mint INFO日志。60次mint全部查询到已提交交易及写集；40条测量日志的原始起止与`REUSE_VM`辅助输出逐条一致，见`boundary_check.csv`。纳秒相减避免六位小数executionTime的舍入误差。

## 调用边界与低负载控制

源码均位于独立工作树`/home/frankie/mygitprojects/.worktrees/cvw-step19-reuse/chainmaker/chainmaker-vm-wasmer/`：

- `vm/v2@v2.4.0/vm_factory.go:432–439`：原始计时包围`runtimeInstance.Invoke`；辅助打印发生在endTime采集之后。
- `vm-wasmer/v2@v2.4.0/runtime.go:87–94`：从池GetInstance，defer归还；SetGas和CallMethod仍在Invoke内。
- `vm-wasmer/v2@v2.4.0/vm_pool.go:628–665`：优先非阻塞取池，失败才发送apply并阻塞等实例。`acquire_wait`在阻塞路径返回后记录；本轮无该事件，所有请求均完成，因此未观察到该阻塞分支。CSV中的blocking wait=0表达此含义，不代表GetInstance函数没有执行成本。
- `vm_pool.go:669–685`：R0归还实例；R1异步Close后remove/add；原始后台队列机制保留。R0仍保留原错误丢弃策略。
- `vm_pool.go:1242–1324`：创建包含imports、NewInstance、WASI Initialize及`_start`。这些工作提前在后台完成时，不在当前mint的Invoke窗口内。

每次最多一个业务请求在途，最小200ms起点间隔；发下一笔前，外部检查已知create/close/enqueue生命周期事件均完成，最多等2秒。**这属于明确的低负载条件，不是通过全局锁修改实例池。**它只约束已观测的显式生命周期工作，未证明所有finalizer或任意Store并发安全。

初始6次创建=1次部署验证+5次池预填。R1另有16次替补，R0没有替补。Invoke没有等待池，R1每次约4–7ms的替补成本主要在后台，没有作为同步创建成本进入约0.7ms的mint窗口。因此不能用创建耗时倒数推算节点TPS，也不能把这些成本加到不匹配的Invoke中位数上。

INFO日志、现有生命周期埋点和辅助打印两组完全相同；其绝对开销未校准。当前与旧Step-19相比还改变了WASM、输入、日志级别和低负载节奏，不能把两轮差值完全归因于候选WASM。

## 正确性与Gas

`correctness.csv`含两批20组同序号测量输入的比较：

- 返回值相同；事件除交易ID外相同。
- 原始写集不完全相同。仅从ERC721 `_latestTxInfo` JSON中去除`TxId`后相同；保留BlockHeight和其他字段，未泛化删除业务字段。
- 每组R1返回Gas比R0多**4379**：对应16604→20983、16605→20984、16613→20992。两批均如此。
- 这证明报告Gas不同，未证明具体省略了哪个执行子路径。不能把时间差全部解释为实例创建或宣称R0正确性等价。
- Table、跨合约、所有异常语义未测试；`certified_safe=False`。R0仅供隔离性能参考。

## 压力档停止原因

不是以“低负载已成功”放行并发。当前实际库及Go调用链的证据见父目录`four-node-tps-preflight/README.md`及保存的反汇编：`wasm_instance_new`对Store引用做非原子incq，`wasm_instance_delete`做非原子decq；实例创建还修改Store对象容器。Go层NewInstance/Close缺少覆盖这些访问的统一所有权或同步。R1各次归还会启动独立Close goroutine，后台grow与业务还共享同池Store。

提高请求压力将允许业务、关闭及创建重叠；当前不能排除竞争。没有靠增加全局锁改变原始行为，也没有运行高负载碰碰运气。低负载本身也不构成完整并发安全证明。本轮资源未触发阈值、没有执行错误，但R1部署后RSS增加约174MiB，短测未证明长期有界。

容器保护：单节点逐次运行，MemoryMax=2GiB、TasksMax=256、RuntimeMax=90s、TimeoutStop=5s；软阈值RSS<1536MiB、部署后RSS增加<256MiB、线程<220、单请求15s、补池2s。全部四个节点及客户端已停止，未替换正式节点或生产代码。

## 对五个问题的回答

1. **候选WASM是否放大差距？**本轮合并约1.33倍，与旧约1.35倍接近；两批为1.17和1.51倍，没有接近历史4077.5/311.4≈13.09倍。跨轮控制不同，不能据此证明WASM完全无影响。
2. **压力是否进一步扩大？**未测，安全检查未通过。
3. **是否看到空池或争用？**未观察到空池阻塞；未收集能归因到Store/CPU争用的证据，不能宣称不存在争用。
4. **能否断言当前环境不能复现？**只能说此次同候选WASM低负载未复现；较高压力未知。
5. **最小额外证据？**先明确实际Store跨线程所有权及资源回收边界，随后在两组共同且披露的安全条件下做同候选WASM的短时压力档，逐交易对齐Invoke、空池/等待及补池时间线；若要归因历史13倍，还需历史实际ERC721哈希与负载档。不能用加全局锁后的结果冒充原池并发结果。本轮不实施修复或继续扩展。

## 文件、复核与回滚

`samples.csv`逐交易原始日志来源及耗时；`summary.csv`四个条件分位数/创建/资源；`comparison.csv`主表；`correctness.csv`状态与Gas；`requests.jsonl`原始SDK及提交写集；`resources.jsonl`RSS/虚拟地址/线程/CPU ticks采样；`boundary_check.csv`原始日志交叉核对；`environment.json`版本；`artifact_hashes.json`配置/输入/二进制/日志哈希。虚拟地址空间及CPU ticks仅保留原始数据，未声称是RSS或CPU利用率。

原始节点材料保留于本目录`{a,b}/network/{baseline,optimized}/`，包括stdout、system.log、配置、账本、启动/停止/cgroup记录；未清理、覆盖旧产物。这里的baseline/optimized目录名沿用旧客户端协议，实际仅表示R0/R1，**不含任何Copy优化**。证书、账本及二进制不纳入报告提交。

只读复核保存数据（不启动节点）：

```bash
python3 -B CVW/experiments/instance-lifecycle/step-19-reuse-reproduction/erc721-minimal-difference/analyze.py
```

`run_low.py`是本轮有限低负载执行器，遇到已有requests或stdout会拒绝覆盖。它依赖保存的隔离配置及客户端，并非可直接切换为压力的工具。复跑必须另建输出和空账本、修正隔离路径/端口并保留现有结果，不能直接删除本目录重试。

回滚无需恢复生产：四个`step19-erc-min-*`单元已停止，生产配置、二进制及脏工作区未覆盖。弃用本实验分支即可；保留原始结果，不执行reset/clean或删除历史账本。
