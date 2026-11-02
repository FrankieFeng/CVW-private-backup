# Step-37：全合约性能归因与源码机制分析

已完成只读审计和独立复算。基线CVW abc2ce35、节点c28bfa8，独立分支experiment/step37-performance-attribution。没有节点、编译、性能实验、新Copy/A实现或PPT；历史样本保持不变。

## 数据审计结果（A）

8业务合约、37方法、111个四组匹配block（同batch+slot），444正式窗口、1728交易、1872根执行。8779项SHA校验通过，其中一个Git忽略packaged so只在原Step36工作树存在，已只读取回校验，不将其误认为实际加载库。独立从raw case/日志复核1728逐笔时长、阶段、TxID及提交receipt，111个四组Gas/返回/读写集/事件/已写键状态按原规范化规则一致。原始无效raffle仍保留、不混入主数据。

925项原配对CI/中位节省/正向比例独立复算，最大数值差0。新增五项对照与直接两因素交互、三批/顺序及TPS分析。原报告不改。完整37行见ALL_METHODS.md，完整字段见CSV。

## 统计结论（B）

原探索性Copy正向CI方法：erc721_symbol, compute_hashCal, fact_saveAndFindByFileHash；反向CI方法：erc721_mint。其余CI跨零，不等于没有效果。

以3批为独立单位作双侧符号翻转，五种主对照+交互共222项Holm校正：原始p最低0.25，校正后全部不显著。只有3批，可交换/符号对称亦是条件假设，因此既不能确认普遍受益，也不能确认普遍退化；原局部信号保留为探索性。

## 必答问题

1. **哪些真正受益于Copy？（B）** 按原探索性CI是上述3方法；按本轮保守聚类+Holm标准，没有方法达到确认性统计门槛。不能把“不足以确认”改写为所有方法无效。
2. **哪些Copy增加成本？（B）** ERC721.mint E2E三批负向、原CI全负；但Owner窗口反向情况不同，不能认定restore自身导致额外E2E成本。其他反向中位数亦全部保留。
3. **A改变什么？（A/C）** Go1.24.1同源全局padding重新链接，将init_bloc置59页，针对4MiB arena对齐gap的memFree/memclr路径；不提前执行Runtime，不是128页配置，也不裁剪PB。具体本轮分配调用计数未测。
4. **为何A+Copy不一定更好？（A/B/C）** _start改善同时伴随不同准备/执行/提交窗口；A增加初始Memory/模板容量，却仅增加几百B文件/Copy数据。不能用WASM大幅变大作解释。直接交互/阶段证明非简单加性，尚无唯一负收益机制。
5. **哪些瓶颈已不只在初始化？（A/B）** bigNumCal、normalCal、buyNow、callerAddress的CallMethod占Owner中位比率过半。buyNow的CallMethod含子初始化，不能一概说初始化不重要；Store/WASI分窗缺失仍待测。
6. **Store独立化净成本？** not_measured。所有组相同Store协议，没有同条件共享Store对照或独立NewStore窗，不能用历史批次相减。
7. **Copy明显多余工作？（A/C）** restore约5万区间循环、混合区间内约0.31～0.36MB零字节；更小字节与更少循环有取舍。另有runtime整WASM副本和Invoke/prepare重复SHA，但不在restore内；源码能证明存在，未证明是性能主因。
8. **Renew值得做核心方向？（D）** 值得先定义/调研，尚无完整Instance Renew实现证据。Memory.Reset和Manager.Reset均不等价Fresh；不能直接恢复执行过的Instance来绕过问题。
9. **最值得研究三个问题？** 区间粒度/额外零gap复制的权衡；热路径不可变字节码验证/缓存成本；独立Store下WASI/import准备的可测成本。COW/全状态Renew暂非最小主线。
10. **下一轮具体函数/假设？** step35_static.prepareStaticMemory/restore验证合并区间假设；step35_node.runtime/Invoke/prepare分离clone/SHA再考虑摊销；NewStore/Finalize/GenerateImportObject/GetImports分离计时。只建议，不在本轮修改。

## 交付导航

- METHOD_CLASSIFICATION.csv、ALL_METHODS.md：37方法、四组P50/P95/Mean/TPS及原CI/校正分类。
- PAIRED_EFFECTS.csv：五对照、相对节省=逐对百分比中位数、CI、正向率、三批及TPS。
- BATCH_ANALYSIS.csv、INTERACTION_ANALYSIS.csv：批次/顺序与交互，正saving_synergy才表示协同。
- SOURCE_TRACE.md、COPY_MECHANISM.md、A_MECHANISM.md、GO_RUNTIME_ANALYSIS.md：实际调用链与机制。
- E2E_ATTRIBUTION.md、CASE_STUDIES.md、STAGE_BREAKDOWN.csv、BUY_NOW_PHASES.csv：阶段、负向案例和六子调用。
- STATIC_LAYOUT.csv、COPY_RANGE_SCENARIOS.csv：冻结布局及只算操作量的候选方案，不是基准结果。
- OPTIMIZATION_CANDIDATES.md、RENEW_RESEARCH.md、LIMITATIONS.md、NEXT_STEP.md：建议与证据空缺。

复算：`python3 scripts/analyze.py` → `python3 scripts/layout.py` → `python3 scripts/verify_records.py` → `python3 scripts/report.py` → `python3 scripts/supplement.py` → `python3 scripts/validate.py`。仅写Step37派生数据；需要本机原Step36未入Git的packaged so作清单校验，无需启动native。

A=源码/观测直接证明，B=数据支持机制未唯一，C=源码合理假设，D=未验证研究设想。没有任何静态字节量被换算为未测毫秒。

研究建议：优先验证可解释、可普遍复用的初始化机制，不追求所有方法平均数都变好。本轮结束于报告，不自动启动Step38/39。

统计与假设细节见STATISTICAL_METHODS.md；运行说明见RUNNING.md。
