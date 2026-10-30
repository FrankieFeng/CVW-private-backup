# 四组正确性与资源边界

每个有效block四组Gas、返回、错误码、实际root读写集、事件、初始/最终账本hash一致；全部root账本由setup/target真实RWSet离线重建并逐阶段核对内存snapshot SHA，target-Gx-ledger.json完整保存。CORRECTNESS.csv保存每block状态，其他样本不会静默混入。

实际Gas集合：`{"bigNumCal": ["120027"], "hashCal": ["120019"], "normalCal": ["100000019"], "fact": ["154"], "erc721": ["235"], "buyNow": ["12612158"]}`。同家族跨A二进制虽本轮观测相等，不能推广到任意构建；Copy开启/关闭对应同逻辑WASM，S1 oracle校验仅preflight启用，正式关hash。编译/模板准备在外。

buyNow每成功root严格核对六callee的contract/method/depth/TxID/Gas/code/result；f.run使用真实合约和账本，无mock子调用返回。空参数/重复token两类失败路径四组分别实际执行，回滚最终账本等于初始，全部语义/trace一致，原始exception回执保留：[{"gas": 142, "calls": 1, "gas_result_rwset_events": true, "initial_final_ledger": true, "exception": true}, {"gas": 3002833, "calls": 5, "gas_result_rwset_events": true, "initial_final_ledger": true, "exception": true}]。

未测试：真实Table函数身份、一般异常/OOG全覆盖、节点共识/提交/E2E、原池并发、长期Store资源有界。不能把这些项记PASS。

## 资源

当前442个有界独立进程，最高RSS 571.01MiB、host heap边界峰105.96MiB、线程177。不合格资源/退出记录0。每个outcome记录soft/hard保护、created/closed、in_flight、owner pending、PID/cgroup退出。

Store计数是每个cached Module所属Store scope的创建与成功关闭数：module事件数与cache_closed.store_scopes_closed核对；它不是native内部Rc引用计数或内存泄漏检测。Instance created=closed、scope回到0及进程退出证明本轮有界协议完成，不证明长寿命节点无泄漏。RSS/heap为整进程，不强分配为某个组净增量。

资源阈值保持历史非exchange768MiB/125线程、exchange1536MiB/220线程软限，hard2GiB/256tasks；没有提高上限，禁止绕过STOP。
