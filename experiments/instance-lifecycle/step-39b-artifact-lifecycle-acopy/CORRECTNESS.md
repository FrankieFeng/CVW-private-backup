# 正确性与隔离

- 预检12进程×四目标调用，所有根/子Instance初始Memory与原Image逐字节相同；正式阶段不扫描，Copy原C0未修改。
- 四组3方法正式72次调用，按同case/batch/slot比较Gas、完整Result、事件、RWSet与初始/最终账本hash，全部一致；逐层比较以CHILD_GAS_PARITY.csv为准，不将生命周期测试混入性能N。
- buyNow每笔根+6真实子调用，正式每组6笔全部为7条invoke_end；没有用Mock子返回或空方法代替。各层gas/调用顺序也逐条相同。
- 输入SHA仍每Invoke执行；补充TestStep39Reject在本轮二进制验证不同内容/版本拒绝。输入读取期间仍要求调用方不并发写入，未声称外部[]byte天然不可变。
- 同版本换码/版本升级/保留旧Runtime实际执行/Reset后新Module及Store/Stop后拒绝都通过；案例见LIFECYCLE.md。
- Stop中的buyNow收据，与pre-exchange_buyNow-G3/formal0具有相同TxID、Gas/完整Result/RWSet/初始最终账本，audit/drain-buyNow-parity.json通过。原日志中Stop requested先于root开始，最终cache close晚于root及6子执行完毕。
- Owner/wasmer-go Store/Instance/WASI/Finalizer/Compiler/Copy文件不变；只在独立实验目录加Go Artifact治理及观测/测试。native库及加载路径保持原Selector修复版。

边界：这是VM夹具，不是SDK部署/链上升级/提交确认。BlockVersion1、gasUsed0等与Step36真实节点上下文不同。未验证真实Table函数身份、全部业务异常/回滚、同Runtime并发调用、长期节点运行；原安全Owner串行协议不放宽。

原始失败保留：初次diag编译因新测试未使用变量失败，修正后另建diag-r1。一次补充测试源码复制路径错误导致diag-r2仍为旧测试版本，未用于正式性能或新增检查；修正后diag-r3/r4/r5依次用于明确标记的补充验证。没有业务失败、native崩溃、资源守卫触发或样本删除。编译时测试文本快照与SHA另存audit/frozen-tests；各二进制与命令一一保留。
