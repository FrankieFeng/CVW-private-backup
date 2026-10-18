# Step-19：客户端收益未显现的最小链路验证

2026-10-19，Asia/Shanghai。结论：compute 的 VM 节省保留，但本轮客户端改善不显著；已把主要波动定位到 AddTx 返回后、进入 VM 之前的窗口。不能认定 Copy 导致排队变慢，也未证实“提前执行结束被同一次提交时刻完全吸收”。

## 范围和隔离

- 复用 step-17 Copy，不引入优化机制，不改 Go/ChainMaker/Wasmer 版本。
- CVW 独立 worktree `.worktrees/cvw-step19`，基线 `b21ca6a`；node 独立 worktree `.worktrees/node-step19`，基线 `351b816`。两个仓库分支均为 `experiment/step19-client-latency`。
- 新增有限打点，开关 `CM_STEP19_TRACE=1`，只记录前缀 `1919` 的实验 TxId；源码快照在 `prototype/`，完整补丁在 `vm.patch`、`node.patch`。
- 从已停机 step-17 baseline 账本复制两个独立 data 目录，没有硬链接或共享可写账本，不启动或写入旧节点。RPC 27401/27402，P2P 28401/28402，空 seeds；仍为两个隔离单验证节点 TBFT 链。
- 仅 `compute.bigNumCal`，无业务状态写入；结果应为 `success bigNumCal: 607723520`，Gas 106028。
- `CM_FRESH_INVOKE=1`、`CM_STEP17_SERIALIZE_VM=1`、`GOMAXPROCS=4`，默认 GC。每次同步创建新实例、启动、业务、关闭；Module/template 热缓存。复用 step-17 已校验的编译 artifact，沿用首编译 Gas 异常隔离方法。
- 每轮一个常驻客户端，最多一个在途请求，30 对随机先后，seed 191901/191902；每端点先 1 个冷调用及 5 个成功预热。第二轮交换两个物理端点的 Copy 开关，重启进程清空缓存后重新预热。两轮分开统计。
- 共 120 条热调用、20 条预热、4 条冷调用；没有失败或删样。本轮节点均已停止。未测 TPS/P99，不能外推多客户端或全部 8 合约。

## 时间点与计时边界

所有进程在同一 Linux host/time namespace，用 `CLOCK_MONOTONIC`，不以跨进程的 Go `time.Time` 私有单调偏移相减。boot ID、namespace、配置及二进制 SHA 见 `environment.json`。

```text
client_begin
  → rpc_enter
  → addtx_begin → addtx_end
  → vm_enter → vm_lock_acquired
  → instance_ready → vm_end
  → putblock_returned → commit_common_return
  → committed_event_received → sync_result_received → rpc_return
  → client_end
```

- 客户端 elapsed：SDK InvokeContract 前至返回，含签名/RPC/同步结果。
- `invoke_ns`：沿用 step-17，从根锁获得后开始，到业务与关闭完成；不含锁等待。`vm_span_ns` 另从获锁打点到最终 VM 打点，包含额外观测开销。
- `instance_ready` 在 GetInstance 返回后，此时已经完成 WASI/_start；不是 S1。S1/S2 沿用 step-17 的实例局部 profile。
- `vm_entry_to_lock_ns` 包含第一条 trace 输出和宿主调用开销，属于入口到获锁的观测区间，不能当作纯锁竞争时间。热样本最大 0.084 ms。
- `putblock_returned` 在 `store.PutBlock` 返回及 ledger cache 更新之后；不等于测得 fsync 完成，也不涵盖所有共识网络动作。
- `commit_common_return` 是 common CommitBlock 返回前；dispatcher 收到提交区块事件后发同步结果。VM 后至 PutBlock 窗口包含尚未细分的共识/验证/持久化工作，不能命名为纯数据库耗时。
- 每笔请求检查阶段顺序和完整性。9 个相邻窗口之和与 client monotonic 总时间逐笔精确相等。SDK elapsed 与该总时间最多相差 16.204 微秒，由边界处额外取时等造成，两个字段均保留。
- 未独立校准 trace 的观测扰动；日志写入会增加开销。因此只作同版本、同打点的最小诊断，不替代 step-17 正式延迟。

## 性能结果

单位 ms，Median / P95。每格 n=30，冷调用和预热单列，不混入统计。

| 批次 | 指标 | Baseline | Copy |
|---|---|---:|---:|
| A | VM Invoke | 4.686 / 5.267 | 4.083 / 5.172 |
| A | 客户端 | 35.793 / 47.690 | 36.767 / 45.664 |
| B，角色交换 | VM Invoke | 3.910 / 6.173 | 3.374 / 4.491 |
| B，角色交换 | 客户端 | 29.150 / 48.993 | 34.494 / 41.275 |

正数表示配对节省 `Baseline_i−Copy_i`；它不等于两个总体 Median 之差。

| 批次 | VM 配对节省 Median [95% CI] | 客户端配对节省 Median [95% CI] |
|---|---:|---:|
| A | 0.670 [0.367, 0.916] | −2.034 [−5.183, 4.046] |
| B | 0.465 [0.340, 0.782] | −3.719 [−6.721, 1.905] |

P95 nearest rank。CI 为本轮探索性 circular moving-block bootstrap，block=5 对、4000 次、seed=191903，取中位估计量的百分位区间；未做多重检验校正。30 对样本不足以作稳定 P95/P99 或总体分布结论。客户端两轮 CI 均跨零，不能声称显著退化或改善。

关键窗口中位数如下，不能将这些中位数直接相加：

| 窗口 | A Baseline / Copy | B Baseline / Copy |
|---|---:|---:|
| 客户端开始至 RPC 入口 | 0.368 / 0.355 | 0.359 / 0.368 |
| RPC 校验/注册至 AddTx 前 | 0.184 / 0.194 | 0.181 / 0.176 |
| AddTx 调用 | 0.055 / 0.054 | 0.051 / 0.048 |
| AddTx 返回至 VM 入口 | 19.019 / 21.561 | 13.786 / 18.995 |
| VM 入口至获锁，含打点开销 | 0.038 / 0.039 | 0.034 / 0.035 |
| VM 结束至 PutBlock 返回 | 9.652 / 9.921 | 10.450 / 9.523 |
| PutBlock 返回至 RPC 返回 | 0.180 / 0.189 | 0.178 / 0.166 |
| RPC 返回至客户端结束 | 0.248 / 0.246 | 0.239 / 0.235 |

为解释抵消关系，用逐交易相邻窗口的**平均配对节省**做可加性核算：

| 批次 | 获锁前全部窗口 | 获锁至 VM 结束 | VM 后至客户端结束 | 客户端总时间 |
|---|---:|---:|---:|---:|
| A | −1.657 | +0.640 | −0.356 | −1.373 |
| B | −2.572 | +0.674 | +1.271 | −0.626 |

上表四列使用同一 monotonic 总窗口；未四舍五入前逐笔及均值都严格相加。A/B 的“获锁前”差异主要在 AddTx 返回至 VM 入口。这是本轮样本的时间预算定位，不是“Copy 使调度变慢”的因果证明。

## 能确认什么

1. VM 内部 Copy 收益再次出现，而不是只加速后台补充实例。
2. 本轮所有 144 次调用均只有一个 VM attempt，未发现重执行；所有实例 ID 唯一。单客户端入口到获锁区间远小于主等待区间，因此锁竞争/重执行不是这批样本的主要解释。
3. 大量时间消耗在 VM 前的 AddTx→VM 窗口及 VM 后的提交路径，VM 前窗口在配对间的变化足以抵消约 0.5–0.7 ms 的执行节省。
4. 没有证据证明每次 VM 提前结束都被固定提交时刻吸收：B 批 VM 后窗口反而更快，A 批基本不变。这一假设仍未证实。
5. 两个独立链的出块相位、闭环请求到达时刻和调度状态并未对齐。随机配对和端点交换不能完全消除它们。不能将本轮 Copy 侧更长的 VM 前等待解释为优化引入的排队开销，也不能推广到历史所有合约。

后续若继续，只需对同一 compute 使用固定外部到达节奏、随机切换模式/匹配出块相位，再在 AddTx→VM 中补 proposer 取交易和调度入队时间。当前无需启动 8 合约大规模实验，也没有足够证据为了客户端收益继续修改 Wasmer。

## 验证、复查与回退

`correctness.csv` 的 60 对检查通过：实际结果与预期一致、Gas=106028、两模式相等、fresh ID 不重复、每 Tx 单次执行、所有 trace 完整且时间预算精确。未新增 Table、整节点 race 或生产安全认证；step-17 已知限制仍然适用。

只读重算：

```bash
cd /home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-19-client-latency-trace
python3 analyze.py
```

`run.py` 拒绝覆盖 requests.jsonl，启动前检查端口空闲，finally 只停止其自己启动的 Popen 对象。再次运行需复制运行脚本到新的结果目录，复制已停机账本与配置并重写绝对路径；不要删除或覆盖本轮数据。

构建原型（仅实验 worktree）：

```bash
cd /home/frankie/mygitprojects/.worktrees/node-step19
GOMAXPROCS=2 GOFLAGS=-mod=readonly GOTOOLCHAIN=local /usr/local/go/bin/go build -p 2 -o /ABS/NEW_OUTPUT/chainmaker ./main
GOMAXPROCS=2 GOFLAGS=-mod=readonly GOTOOLCHAIN=local /usr/local/go/bin/go build -p 2 -o /ABS/NEW_OUTPUT/client /ABS/OUTPUT/client.go
```

无生产部署。回退无需改任何生产文件：停用实验二进制，取消 CM_STEP19_TRACE 即关闭新增打点；Copy 仍遵循原 pool 构造开关。节点已停止。保留分支与补丁即可复查，无需 git restore 或清理历史产物。正式生产缓存回收、race 和 Table 限制未因本轮测量而修复。

交付：requests.jsonl 原始客户端、network/*/stdout-{a,b}.log 原始节点、trace_events.csv 全事件、samples.csv 全阶段、summary.csv、paired_effects.csv、mean_accounting.csv、correctness.csv、environment.json、源码快照及补丁。
