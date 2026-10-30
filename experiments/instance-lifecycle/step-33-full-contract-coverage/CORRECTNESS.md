# 正确性与证据边界

900正式完整区块逐组对比Gas、返回、实际TxRWSet、事件、初末账本哈希；从CHAIN_CONFIG和真实init/prerequisite写集重建全账本，再复算每个target初末hash。输入逐笔匹配冻结case manifest。详见CORRECTNESS.csv、原收据和*-ledger.json。

新增30方法预检均真实执行。四组fresh实例无业务复用；所有有效sample reused=false，实例所有权与固定owner及同步关闭守卫启用。S1预检逐组与其最终WASM模板匹配，正式关闭昂贵hash计时。A不同布局的S1 hash不直接要求相等，业务/Gas/状态仍需等价。

itinerary历史与ERC721范围迭代的内存后端来自实际提交写集/账本，并保留原VM/SDK迭代执行，不是固定成功Mock。查询不意味着已验证真实链数据库。erc721.mint2按现有部分实现核对，仅写latestTxInfo，不能冒称完整mint。

identity.callerAddress=blocked：自调用触及active-contract owner守卫，未做危险动态放宽。buyNow六次真实子调用使用Step32原始证据和来源，不重跑。

未验证：真实Table函数身份、所有输入/异常和回滚路径、原池后台并发、长期native回收及真实E2E。它们保持not_tested，不能把成功路径等价推成生产安全。

失败前置记录、监控退出竞态与恢复见PROGRESS及audit，未删除失败或slow/reverse正式数据。
