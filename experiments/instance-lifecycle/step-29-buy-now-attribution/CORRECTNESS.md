# Step-29正确性与资源

真实WASM沿Step28已冻结Step18家族，无重编译、无B1或SDK变更；三组根与identity/ERC721依赖均使用对应G0/G1/G2构建。每个成功区块逐根、逐六callee核对Gas/返回/状态码；根完整读写集、事件、初始/最终账本核对一致；plain与trace同区块同组再次核对一致。不能以Go进程PASS代替业务核验。

模块/模板准备在Invoke之外，原计划/Module缓存和fresh规则未改。异常empty/duplicate在最终build3复核，实际错误返回、真实子调用、Gas/读写/事件一致、最终账本不提交变化；保留旧build1预检，未混主性能。派生ledger由真实RW集重放并逐阶段复核原进程snapshot SHA，不修改原始回执。

| 模式/阶段 | 有效三组区块 | 根Gas集合 |
|---|---:|---|
| plain formal | 30 | 12612158 |
| trace formal | 30 | 12612158 |

实际执行204独立Guest测试进程，全部正常退出；最大采样RSS 568.8MiB，线程177，边界Go heap objects 105.7MiB。每个正常buyNow进程created=closed=10、owner managed/pending=0、cgroup/PID均结束。轮询/边界峰值可能遗漏更短峰值，不能称精确native分配峰值。

资源阈值不变：RSS1536MiB/线程220软限，2GiB/256task硬限，Go45s/进程60s，全机available≥8GiB/swap≤1GiB。独立Store固定owner串行，逐次同步关闭，无后台池、并发Store、全局锁或守卫绕过。

未通过/未测试项：真实Table逐元素函数身份、其他异常/回滚、节点ACL/签名/共识/持久化、长期WASI线程完全回收、原池并发安全。所有这些仍not_tested；本轮不作生产安全认证。
