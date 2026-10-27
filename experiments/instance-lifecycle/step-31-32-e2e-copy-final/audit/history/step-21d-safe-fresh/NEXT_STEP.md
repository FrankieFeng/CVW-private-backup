# 后续准入与具体阻塞

本轮已恢复：固定实际WASM/输入/库、真实VM业务路径、串行Fresh所有权、显式清理、隔离进程保护与可恢复日志。可以在同一1–3次边界内诊断compute，以及1根buyNow的真实状态/事件。R0只能提供参考，exchange Gas已经不等价。

## 为什么没有100次

1. 每Fresh Invoke重编Module约0.56–0.63秒。100次compute即约56秒量级，还没有加入normalCal业务和关闭，超过当前45秒Go测试预算；buyNow约4.56秒/根更不合适。这是小样本成本推算，不是100次实测。
2. 最终只检查短进程；WASI/Store显式清理后RSS不立即回初值，部分线程残留归属未确定。scope登记归零是Go/C wrapper所有权证据，不是长期native资源收敛证明。
3. 源码/runner限制compute≤3、exchange=1是本轮安全门。不得通过更改标签、解除限制、提高RSS/线程/超时阈值填满100次。

## 要恢复后台Fresh供给，至少解决什么

- 固定so的精确commit、patch、Cargo.lock、features、编译器和可重建产物；当前只有6.0.1自报/头文件、hash、反汇编及0910740候选源码，不能认证完整来源。
- 去掉逐次编译造成的新成本前，审计同Engine下shared compiled Module在目标Store获得/实例化的契约。6.0.1的C API线程例子使用`wasm_module_share/obtain`，但当前Go NewInstance只认module.store；不能把任意原Module配一个新Store变量。应做新的实验绑定接口及错误/销毁审计，先验证目标Store，再重建基线。
- 若要多个所有者并行，重做按所有者隔离的清理登记、Go全局metering配置及回调路由。当前managedOwner/registry为单所有者，不能只是改GOMAXPROCS或并发调用dRuntime。
- 真正的有界后台供给需明确预留、在建、可用、借出、关闭计数，有限入队与取消、关闭join；不重新引入原apply/remove/add的重复请求和等待环。策略变更R0/R1一致，单列性能影响。
- 给native内存/线程取更长但仍有界的分级证据、线程归属及确定退出记录；先登记预算，不能根据“没崩溃”解除门槛。
- 解释buyNow R0/R1 Gas4379差异和旧块版本累计Gas规则，补充负向交易回滚/重复token/非法地址。节点ACL、真实持久数据库等另属验证范围。

## Step21C与Step22结论

Step21C：本轮首次真正完成两模式各一次的六callee成功链，已有状态、读写集、事件及Gas证据；可以沿此基线继续小样本功能调查。它不构成原池/生产吞吐复现。

Step22：当前**不具备Fresh+Copy补池性能实验条件**。先建立不把编译放大为主导成本、所有权明确且供给有界的新Fresh基线，证明资源及业务/Gas前提；再在完全相同的安全实现里只切Fresh/Fresh+Copy。模板、编译准备、复制、等待和回收分别计时，不和旧Step21修复版直接相减。

不采用一把全局锁后称原池性能，不默认独立Store可跨线程，不在本轮加入Copy、Arena Alignment或PB裁剪。现有独立进程串行参考保留为功能/生命周期对照，不因下一步优化而覆盖。
