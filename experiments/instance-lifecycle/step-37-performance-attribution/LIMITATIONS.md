# 证据边界与未证明事项

1. 只有3个独立批次、每组通常12笔（alterAdminAddress3，raffle9）。同进程四笔共享条件，不能当12次独立环境重复。
2. 复现Step36 925项配对中位数/CI/正向比例完全一致；不等于原设计能推断任意节点负载。所用层级bootstrap在3clusters下覆盖率很不稳定。
3. 本轮主检验以每批配对差均值的双侧8种符号翻转、Holm整体222项。符号对称/可交换是条件假设；原组顺序平衡但非充分随机化，不能宣传为严格随机试验精确因果p。最小p0.25、Holm无显著主要表明功效不足，不证明所有效果为零。
4. 旧Step32用G0-G1-G2+G3若把“正值”称额外协同，会把成本交互符号解释反。本轮同时保存成本交互与节省协同，历史原文件不改。Step36组号G3是A-only，不能沿用旧矩阵编号。
5. Source/Owner设计和串行语义固定；没有可比的“旧共享Store”反事实，所以Store独立化的净额外成本not_measured。不能用不同版本3ms与18ms相减。
6. Store创建、WASI/import、独立export、guest Runtime A与B1、guest GC、page fault、memory.grow调用次数和字节均未独立落盘；阶段表not_measured。sim_context内计算过B5Profile并不代表该安全路径输出过这些值。
7. 外层Factory日志UnixNano有墙钟局限；内层和SDK各用单调时间。跨进程绝对时间只关联事件，不相减。NODE_STAGES是同一节点CLOCK_MONOTONIC，但事件含日志/ReadMemStats开销。
8. 主数据1728Tx对应1872根执行，root不能只取一次；根/子Invoke嵌套不可相加。buyNow真实子调用六次，但根CallMethod不是纯guest计算。
9. 未找到独立逐笔CPU频率、guest缓存命中、fault、GC证据；RSS/host Heap变化不能直接解释guest执行。正式样本进程全部正常退出、计数配平，不证明长期资源收敛和并发安全。
10. 业务正确性在原规范化规则下复算111个四组block；历史记录时间/高度被特定规范化，因此不是原始全账本字节相等。异常验证仅原35C/36已覆盖范围，Table真实身份及全部异常not_tested。
11. Step36 SHA清单中一个ignored packaged so不在Git worktree；从原Step36工作树只读找到并校验SHA，记录fallback。运行时762份maps指向另一个明确冻结的Selector修复库，不将packaged so误认为实际加载版本。
12. A的元数据5页校正来自历史同源probe，当前静态layout吻合，但本轮没有重新追踪每次guest arena调用。Copy range静态粗化仅算操作数/字节，不是新性能实验或新实现。
13. 单节点/Common/同步单客户端、Module已预热、新Instance每次创建。不能当节点最大TPS、冷Module端到端或王浅秋历史VM等效TPS；不混入Step25～32样本。
