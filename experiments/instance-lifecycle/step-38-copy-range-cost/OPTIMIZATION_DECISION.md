# 决策：保留C0，不因区间数量少就接入E2E

**已测量**：C0 restore在本轮约0.76～0.90ms（各方法P50）；B的循环子窗约0.69～0.99ms。该循环是Copy内部主要成本，不是可忽略的metadata lookup。但这没有证明5万个循环本身占全部成本，也没有证明减少次数一定更快。

**已测量/源码**：compute C0为49,443 ranges/1,154,947B；C2为13 ranges/2,026,437B，增加871,490B零间隙。C1是45,678/1,192,828B，C3是3/2,027,330B，C4是1/2,028,831B。实际减少循环和增加字节之间的权衡存在；当前没有恢复阶段跨合同稳定胜者。

**阶段与完整Invoke**：某些完整Invoke改善没有对应restore改善，另有buyNow span反向；都不作挑选性宣传。先维持C0的较小复制量，不把C3在单个方法的局部正CI当成通用优化。

**下一轮优先级**：

1. runtime私有整WASM复制、Invoke两次SHA、prepare一次SHA/key是直接可测的更大热路径成本。先验证不可变code-record/版本失效/输入防篡改，再考虑摊销；本轮没有删校验。
2. WASI builder/Finalize/imports比NewStore明显更大。native builder里创建多线程Tokio Runtime不是“缓存一个签名”就能消掉。只读程序名/参数/schema/函数类型描述可研究；WASI Env、native Function/Import、host context、Memory不能直接跨Store共享。缓存Module/Engine是已验证现有做法，不是本轮新优化。
3. 若继续Copy研究，应先补**同字节数、改变分块数量**的正交控制，并记录页fault/CPU等以区分复制实现和访问行为。不能仅凭本轮字节量增加就声称带宽或缓存是唯一根因。

**不批准本轮新范围策略替换Step36默认Copy或启动全量E2E**。这是收益证据不足及扰动问题，不是发现了新的Fresh Owner安全失败。可以保留合并方案为实验参数，未来独立确认后再决定。
