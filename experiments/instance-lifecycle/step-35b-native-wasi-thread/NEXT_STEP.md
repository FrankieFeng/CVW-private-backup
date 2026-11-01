# 最小下一步与阶段边界

1. 保留native单行补丁。将它作为独立基础设施修复，不与Copy加速收益混算；不要将本轮Smoke时长当性能数字。
2. 单独处理ChainMaker节点停止准入：明确停止接纳请求、排空VM与区块/HistoryDB提交任务、最后关闭账本DB的顺序。仅Owner排空不能代替整个节点写入排空。原始Store/v2的Close有waitG，WriteKvDb也有局部waitGroup；仍需确认真实在途调用与这些等待的覆盖关系，不能凭已有panic直接断言某一WaitGroup一定漏计。
3. 最小验证保持1个已进入VM请求，触发受控Reset/Stop，保存提交与DB关闭阶段记录；要求无write-after-close、正常有界退出，之后再做补丁组重启及重复buyNow回滚。此工作不在Step35B继续扩展，当前STOP保持。
4. 满足以上条件才进入有限G0/G1客户端E2E。保留同一补丁native、同一Gas/Guest，缓存key记录native SHA；不要与旧库历史样本拼成直接配对。

native修复仍需后续常规边界测试：共享Runtime网络对象最后所有者释放、未使用/失败初始化、I/O活跃时关闭、长期有限循环。它们是覆盖限制，不是本轮已观测损坏。

本轮已完成一次根因定位、一种最小修复、一组补丁前后有界对照。未升级Wasmer/重构Runtime，无进一步修复计划自动执行。
