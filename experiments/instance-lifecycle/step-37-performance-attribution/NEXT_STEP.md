# 下一轮最小、可证伪验证建议（本轮不执行）

1. **先补三个窄窗**：在同安全Owner路径的step35_node.go:249～264分出NewStore、WASI Finalize/GenerateImportObject、CM GetImports/intoInner；runtime:90、Invoke:184、prepare:133分别统计WASM clone和SHA。这只回答成本在哪，保留原总Invoke边界，计时开销单独评估。
2. **只验证区间粒度一个因素**：step35_static.go:205的范围计划和:249的循环，固定WASM、Fresh协议，比较原range、64B零gap合并、单span；预先固定选择，不根据性能中途改阈值。验证全Memory初态、Gas、globals/table身份、跨调用及trap。静态预测只是次数从约5万到个位/十位，不能预设变快。
3. **根据第1项决定是否摊销身份验证**：若clone/SHA足够大，再设计不可变bytecode record+版本失效测试；不直接删校验，不顺手改WASI或Copy，保留独立因果对照。
4. 统计重复单位应提高独立进程/日期/批次，而非仅增加同进程调用。先明确主要stage假设和少量主对照，再做预注册独立确认；保留37方法覆盖矩阵但不以全部方法平均收益为优化目标。确认样本量需估计批间方差，3批本身不足做可靠功效规划。
5. Renew先向老师确认实现/语义；COW先native纯功能原型。二者暂不替代已验证Fresh基线，不并入节点实验。

停止条件：正确性/Gas差异、生命周期守卫、资源增长即停止；1536MiB/原线程阈值不变。上述均是建议，没有在Step37执行，也不自动开始Step38/39。
