# 安全准入：接线/功能通过，正式E2E暂停

| 条件 | 状态 | 证据/限制 |
|---|---|---|
| 真节点独立Store执行 | PASS（本轮范围） | 真实SDK交易，runtime Store不等于compile Store；NewInstanceInStore；INVOCATIONS.csv |
| 缓存Module及同Engine跨Store | PASS | 六轮5次准备/62次命中，Owner内元数据准备；固定库6.0.1及加载maps |
| buyNow六真实下游 | PASS |10次成功根调用，每次6个真实child；CORRECTNESS_CHECKS.csv |
| Gas/结果/业务状态 | PASS（已覆盖路径） |Baseline/Copy同新生命周期同初始业务状态，COPY_PARITY.csv；全链哈希与Table身份不在范围内 |
| 关闭/Stop/Reset协议 | 部分PASS |真实node Stop在inflight1时等待完成后退出；实际manager接口Reset、Stop幂等通过；chain-config触发node Reset未执行 |
| Finalizer/借用所有权 | PASS于受控协议 |沿用Step34，未观测守卫失败；不是任意native故障认证 |
| 资源长期或多轮收敛 | **NOT PROVEN** |CAPI配平但RSS仍增长；六轮峰值1481.109MiB，软阈值1536MiB，线程109；Go GC回收live heap不等于RSS/native线程收敛 |

**本轮不签发正式Copy客户端E2E准入，不运行性能压测。** 这不是说所有E2E路径一定不安全，也不是确认已有native资源损坏。新Owner已真正接管有限真实节点调用；阻塞从接线/归属落实为资源收敛证据不足，及尚缺节点级Reset触发覆盖。

原配置触发保护已停止保留。小账本配置容量缩减不是提高RSS上限，不是修复native leak的证据。六轮正常退出也不能证明持续服务无累积。

原池worker并发、共享Store并发创建、异步关闭均未启用。最终实验二进制未opt-in就拒绝StartVM；不能把该managed绑定与legacy池混搭。节点只支持本次1链/1Owner、最多32外部job、固定Guest；不是生产兼容VM。
