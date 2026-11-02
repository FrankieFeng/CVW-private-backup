# 候选优化：不实施、不预报收益

下表全部是C（源码支持成本存在）或D（机制/收益待验证），不将静态操作量换算成毫秒。

| 方向与当前证据 | 对应函数 | 原理/目标窗口 | 正确性及Fresh约束 | 最小后续验证 | Wasmer6.0.1适配判断 |
|---|---|---|---|---|---|
| 1 区间粗化/分组复制（C/D）；当前约5万次copy | step35_static.go prepareStaticMemory/restore:85/235 | 将短零gap一并复制，减loop/检查，作用Copy与实例准备 | 只准fresh已零目标；最终Image不变、越界/start语义不变；不能套已执行业务Memory | 固定同WASM/Owner，比较原range/≤64B合并/单span；记录真实bytes、页fault、NewInstance+Copy、Gas/状态 | 可先host原型，无native ABI变动；本轮COPY_RANGE_SCENARIOS仅静态算量 |
| 2 模板紧凑存储、去掉不复制的尾部/零区间（C/D） | plan.Image/Ranges、restore长度校验 | 存offset+紧凑payload，避免每缓存项保留整个initial Memory；作用一次准备/容量 | 长度校验改为Memory声明独立字段；保持原段覆盖顺序，不能丢零覆盖；源只读/目标私有 | 原/紧凑Image的逐字节初态、hash、overlap/zero/OOB测试；单独报告准备成本与热路径 | host可行，但可能增加slice定位/小copy，不能只按更小容量断言更快 |
| 3 热路径字节码身份与缓存验证摊销（C/D） | step35_node.go runtime:90、Invoke:184、prepare:133 | 当前每runtime复制整WASM，Invoke哈希两遍、prepare再哈希；改为可信不可变code-record token仍完整失效校验，目标Factory/Owner外和内 | 不准直接删SHA；版本更新/同名不同字节/可变[]byte会导致错误复用；子调用亦需正确绑定 | 只加copy/hash计时及分配计数，冻结热输入/升级输入反例；再做一项干预而非同时改多处 | Go层可探索，必须保留不可变性及缓存失效证明；文件A增量仅几百B不能解释A负收益 |
| 4 按页初始化/只读模板+file-backed COW（D） | native instance/mod.rs initialize_memories:1490，memory.rs，mmap.rs:361 | 缓存最终初态页，fresh私有映射共享只读来源，写时分离；作用native准备/内存带宽 | 映射基址、guard pages、grow、traps、table/globals仍私有；先验证段OOB，不改变初始化异常时机 | 纯native小模块、重叠/零洞/写后隔离/grow/OOB/trap；页fault+RSS与CPU，不先上节点 | 无现成Go/C API接入；wasm_memory_copy是浅复制，Mmap.copy仍实拷贝，需native改造，优先级低于1/3 |
| 5 Data Segment惰性初始化（D） | initialize_memories、initialize_memory_with_data:766 | 将完整初态映射为按页按需触碰，降低未读取页成本 | WASM普通load/store不经过host；需页fault映射支持，不可按业务手工省段；启动前OOB仍需校验 | 页级纯native原型，对未读/跨页/全读/首次写分别对照，并检查trap顺序 | 当前C API无惰性Data接口，难度较高；并非简单关闭Data Section |
| 6 WASI/import描述复用（C/D） | step35_node.go Finalize/GenerateImportObject:250/254；vm_bridge.go GetImports:585 | 缓存不可变签名/命名描述，目标Store仍新建native imports与WASI；目标S0→S1 | 不能跨Store共享Function句柄/hostctx/FD或WASI任务；Selector析构修复必须保留 | 首先分离Store/WASI/import/intoInner计时与对象计数；再单独优化无状态描述 | 可做Go层描述缓存；native Function/Env共享不直接可用，资源成本尚未单独量化 |
| 7 有界资源预分配（D） | NewStore/NewInstanceInStore、ManagedScope | 预分配未执行业务的Store/Memory可能平滑等待；不复用已执行Instance | 重新引入后台同Store/析构并发风险；当前Owner串行协议不可绕过，Store不能重置当Fresh | 先单Owner同步创建/领用/关闭身份与配平；无后台并发，再单独算准备成本 | Store/Memory有API，但Module/Imports所有权与时间窗口转移必须说明；不优先恢复旧池 |
| 8 条件选择A/Copy（B/D） | 构建配置、缓存key、prepare | 按可解释布局特征选择，不对37个单方法样本事后过拟合 | 同一二进制正确性/Gas记录，选择策略在独立样本前冻结；不是修改工作负载凑收益 | 以初始布局/区间数等预注册阈值，留出合约验证；先证明stage规律 | 现有开关可实现，但本轮三批不够可靠训练策略 |
| 9 Renew/状态重建（D） | Memory.Reset、Owner.Reset；见RENEW_RESEARCH | 根据明确定义重建状态或复用无状态资源 | 不能将Memory.Reset=Fresh；globals/table/Go/WASI/Gas全部语义边界需证明 | 先取得老师定义/代码，再做Gas、隔离、grow、跨调用、trap反例 | 没有找到完整现成Renew实例接口；不直接合并未知方案 |

优先顺序：1（区间粒度权衡）、3（热路径身份/缓存成本先计时）、6（Store/WASI/import分窗）作为三项可证伪研究；2可并行作为容量问题。COW/Renew暂不承诺比Copy更好，也不自动开始实现。
