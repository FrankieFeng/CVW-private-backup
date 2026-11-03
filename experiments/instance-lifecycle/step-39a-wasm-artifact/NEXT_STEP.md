# 建议：仅优化SHA，暂不优化Runtime Clone

1. 保留原输入SHA、Template Key及Module native校验。在safe Manager纯Go层缓存拥有权快照的摘要，避免Invoke对内部快照重复SHA和prepare对同内容重复SHA。不要把metadata当作真实性校验。
2. 进入有限真实节点E2E前，补齐管理器Artifact容量、Reset/Stop清理及真实升级/同名不同内容缓存验证；继续使用既有安全Owner和1536MiB/线程守卫。不得直接把本地原型当生产实现。
3. 仅SHA的有限客户端配对优先于Clone；保留Factory和RunContract/SDK不同边界，客户端传递仍待验证。hashCal关闭新增插桩后Factory CI跨零，应保留不确定性，不以它作稳定收益承诺。
4. C/D虽然降低每次Go分配，但本轮不支持Clone的额外性能收益。不能从“少复制33.8MB”推断buyNow一定更快，也不能无证据归因cache/内存带宽。
5. 不自动进入下一阶段。若后续有限E2E确认SHA未传递到客户端，再考虑WASI Builder/Tokio的独立研究；不改当前native生命周期，不将旧共享Store时间差解释为独立Store成本。

A+Copy的Guest family/二进制不同于本轮Fresh+Copy，下一轮若纳入应独立冻结WASM，不复用本轮绝对Gas/耗时配对。论文可用的当前材料是可审计实现/安全前提、调用边界及有界探索结果；普遍性能结论还需更多独立批次、体积分布和真实节点验证。
