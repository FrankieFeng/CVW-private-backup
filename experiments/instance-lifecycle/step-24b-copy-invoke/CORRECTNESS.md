# 正确性范围

所有目标调用都是Fresh Instance；A1使用既有静态Memory Copy，不复制业务执行后的实例。没有改Gas规则或业务WASM。根结果、status/code、Gas、完整实际根RWSet、事件、初始/最终账本hash逐对严格比较，完整数据位于raw_logs/*-receipts；离线复核见CORRECTNESS.csv、scripts/check_pair.py及verification.json。

预检每个新Instance在S1实际计算全Memory SHA并与原静态Image核对；正式关闭该hash观测，全部预检单独标记、不纳入性能。初始化在每变体Store均实际执行，不伪造账本；离线还比较两组init的Gas/返回/RWSet/事件。目标每次clone相同初始化账本，固定TxID/参数/tokenId，避免把输入长度或累计账本变化当作Copy差异。

buyNow为真实根及六次VmManager子调用：identity.addWriteList、isApprovedUser两次、erc721.mint、setApprovalForAll2、transferFrom。按调用ID排序核对方法/合约/深度、Gas、返回/错误；根RWSet是真实TxSimContext最终结果。没有使用23受影响v1的中途RWMap观察器；没有把派生集合当框架完整callee RWMap。每变体独立进程的根初始/最终账本、输入/TxID都配对比较，避免因进程不同省略语义检查。

| 范围 | 状态 |
|---|---|
| 指定成功输入的业务返回、Gas、根读写集/事件、账本 | tested，逐对结果见CORRECTNESS.csv |
| 预检S1全Memory与模板一致 | tested，原sample含s1_hash |
| 原非Data字节/Copy代码与22一致 | 源码及manifest审计；没有用此替代动态状态验证 |
| Table真实函数身份 | not_tested |
| 内部Globals动态比较 | not_tested |
| 异常、Trap、OOG与全部失败分支 | not_tested |
| 每callee框架内部完整RWMap | not_tested；仅核对真实根合并RWSet与子调用Gas/结果 |
| 并发隔离、长期Store回收、真实节点 | not_tested |

保留22/23已经标注的缺口，不把无崩溃、Memory hash相等或几个成功路径当成生产启用证明。实验Runtime沿用原CallMethod错误被Gas读取覆盖的语义，同时记录call_error_observed；离线要求其为<nil>，避免被成功Code掩盖。所有scope before/after计数相等、最终登记0同样是实验生命周期检查，不证明native内部全部资源立即释放。
