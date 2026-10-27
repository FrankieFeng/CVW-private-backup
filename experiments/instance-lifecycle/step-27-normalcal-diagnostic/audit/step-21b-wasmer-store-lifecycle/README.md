# Step-21B：Wasmer Store并发安全与实例池生命周期验证

2026-10-26，Asia/Shanghai。分支 `step-21b-wasmer-store-lifecycle`。源码审计、失败现场分析、最小串行验证和后续方案已完成；**默认共享Store池尚不能放行连续负载性能复验或Step-22**。本轮没有修改生产VM，没有加入Copy、Arena Alignment、PB裁剪，没有推送。

## 最终五问

| 问题 | 本轮结论 |
|---|---|
| 多个Instance是否共享Store？ | **是，每个合约池一个Store**。`newVmPool`创建并持有，所有池内实例、host imports、WASI从同一`p.store`派生。不同合约池通常各有自己的Store。 |
| 同Store创建A、执行B、关闭C哪些可以并发？ | 本实现**不能允许无同步的这些组合**。6.0.1 C API通过`Rc<UnsafeCell<Store>>`取得StoreMut，实际so调用/删除有非原子引用计数；不同Instance仍有共享对象。创建×执行、执行×执行、创建×关闭、执行×关闭、关闭×关闭均不放行。生命周期完整、同一所有者线程串行操作可作最小验证。独立Store方案仍需实现与审计。 |
| Step21A守卫发现了什么？ | **不同Instance的创建/拟执行区间重叠**。进入执行区前已退出，worker采样在`wasi_config_new`，没有证实同时native Store访问、同Instance重入、在途关闭或已释放资源访问。属于A的生命周期重叠及E的证据边界，不能写native race已复现。 |
| 容量修复改变供给吗？ | **改变**。`grow`统一裁剪`max-currentSize`，影响运行期apply/add/refresh/reset；不是仅修退出。创建worker数量仍一个，稳态供给调度可能改变，影响幅度未测定。 |
| 如何继续21/22？ | 先锁定native构建来源，修复生命周期退场协议；并行供给实验优先评估**独立Store所有者/独立进程**，所有操作及销毁归所有者，WASI不得跨Store回收。新旧性能机制无法完全保持时，必须登记为新基线，不能称原池性能。当前没有证据支持原共享Store无同步方案安全延续。 |

这里的“不放行”来自源码和实际二进制结构证据，不是把“共享Store”本身视为错误。构建来源缺口也意味着不能把本地候选源码声称为so的逐字构建源。详见[并发约束](CONCURRENCY_CONTRACT.md)。

## 交付与验证

- [STORE_OWNERSHIP.md](STORE_OWNERSHIP.md)：对象图、持有关系、native共享、Finalizer。
- [POOL_LIFECYCLE.md](POOL_LIFECYCLE.md)：时序图、单worker边界、信号和关闭死锁路径、容量diff。
- [CONCURRENCY_CONTRACT.md](CONCURRENCY_CONTRACT.md)：版本、证据类别、逐组合判定和来源缺口。
- [GUARD_ANALYSIS.md](GUARD_ANALYSIS.md)：真实时间戳、实例ID、栈、A–E归因及守卫盲区。
- [VALIDATION.md](VALIDATION.md)：仅执行两个串行C API进程，各3次结果42、exit0；其余场景跳过。未认证业务Gas/WASI/Go绑定。资源采样没赶上短进程，不能把0样本当0消耗。
- [NEXT_STEP.md](NEXT_STEP.md)：进入Step22的阻塞项与不损失供给并行度的候选方案。
- [PROGRESS.md](PROGRESS.md)：恢复入口；[evidence](evidence/)为源码快照、哈希、反汇编和历史现场，[raw_logs](raw_logs/)为本轮独立进程日志/命令/退出状态。

读过的历史资料包括Step19主报告、原TestInvoke复现（Step19A对应资料实际位于`step-19-reuse-reproduction/testinvoke-reproduction`）、pool-supply及historical-entry审计、Step21主/容量补充报告、Step21A四份报告/进度/失败栈。本轮依照实际目录命名，不另造Step19A目录。历史TPS不重新认证，八份报告并不构成可立即启动的性能环境。

主工作区启动时已有生产源码及其他实验脏文件，原样保留。本分支只归档本目录；`evidence/current`冻结的是本次实际读到的源码，`evidence/step21a`冻结的是历史实际编译版本，两者行号不能混用。
