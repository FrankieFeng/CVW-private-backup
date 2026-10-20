# exchange.buyNow快速补测：安全预检停止

2026-10-20。本轮只检查成功路径和运行条件，未启动节点、未发送交易、未产生R0/R1性能样本。表中此前的881.2/57.7为用户提供的历史参考，不是当前测量。

已找到toolkit的exchange、identity、ERC721候选WASM，路径、大小与哈希见manifest.json；准备成功buyNow必须真实部署这三个合约。原参数规则位于parallel/Init.go:214–217；tokenId必须递增且账本内唯一。

阻碍不是缺少WASM，而是同一根交易内的Store并发：

1. CVW/chainmaker/testdata/exchange/exchange.go:48、57、65先后调用identity三次，:77、88、101先后调用ERC721三次。此为现存源码流程，尚未通过本轮运行确认候选二进制完整行为。
2. 实验实际运行时.worktrees/cvw-step19-reuse/.../runtime.go:79–89对子调用仍GetInstance、defer RevertInstance。
3. vm_pool.go:669–680在R1归还时启动异步Close、remove/add。下一次同合约子调用不等待该操作结束，可能同时访问同池Store。
4. 同池Store对应vm_pool.go:1033、1050；wasmer-go/instance.go:28–45及137–145未提供覆盖创建/关闭的统一Store同步。实际native库非原子Store引用及对象容器证据已保存在父目录four-node-tps-preflight。

因此“客户端逐笔发送并在交易之间等待补池结束”不足以规避buyNow内部的重叠，不能照搬此前mint的外部quiescence控制。未声称已经复现race或每次调用必然崩溃。

遵守此前“Store风险未控制不运行不安全测试、不得增加全局锁改变实例池行为”的要求，本轮停止。没有将Step-16的外部响应mock、提前返回的错误路径或历史数值作为本轮节点成功路径数据。

最小解锁条件：在独立安全补丁中明确同Store的创建、执行、关闭所有权与同步，涵盖连续子调用、后台worker及finalizer，验证重入与生命周期后，两组使用同一补丁再测。此操作会改变当前并发实现，必须披露；本轮未擅自实施。性能统计应只筛选根exchange.buyNow的原始Invoke窗口，不重复累加嵌套子调用。

当前R0/R1日志TPS均未测得，不是0。为了明天汇报，主实测表应删除exchange行，历史数据可以单列为参考；不能填入未经测量的数字。
