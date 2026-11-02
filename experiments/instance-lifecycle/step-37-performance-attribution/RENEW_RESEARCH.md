# Renew：存在什么，不存在什么

证据等级沿用SOURCE_TRACE.md；以下为静态检索，本轮未运行Reset/Renew。

## 找到的实际接口（A）

1. `V/wasmer-go/memory.go:139 Memory.Reset` → `R/lib/c-api/src/wasm_c_api/externals/memory.rs:108 wasm_memory_reset` → native memory.reset。`R/lib/vm/src/memory.rs:140 WasmMmap.reset`仅将self.size.0置零；不能据此证明恢复到模块初始Memory，亦没有Data、globals、table、WASI或Gas重建。更广泛size/current_length一致性未经本轮动态核实，不能当可靠Renew。
2. `V/step35_node.go:120 reset` → `SafeFreshOwner.Reset:139` → clear缓存、等待任务；这是Manager生命周期重置，不是把已执行业务Instance恢复初态。旧vm_pool.reset也属于池管理，不能等同guest语义恢复。
3. 对实际native lib和冻结VM的Go/Rust代码搜索`Renew/renew`：只发现`R/lib/wasix/src/fs/fd.rs:140 renew`和epoll_wait相关join重订阅，**不是Instance Renew API**。CVW旧VM和本地陈航VM也未找到可核实的完整Instance Renew公共实现。检索范围/原输出保存在audit/renew-search.txt；不是声称全球没有该方案。
4. `R/lib/c-api/src/wasm_c_api/externals/memory.rs:40 wasm_memory_copy`直接`Box::new(memory.clone())`，注释明确shallow copy。不能用它证明独立Memory或COW。`R/lib/vm/src/mmap.rs:361 Mmap.copy`实际新建Private映射再copy_from_slice；仅有MAP_PRIVATE或“COW”注释也不证明已实现模板文件的惰性共享。

## 两种可能的研究含义（D）

- **资源Renew**：每笔仍是新Instance/独立Store，仅复用经过验证的编译结果、只读镜像或无状态宿主描述，或重建新的native对象图。与当前Fresh原则可兼容。
- **完整状态重建**：保留执行过的Instance，试图恢复所有可观察状态。是否允许应由研究定义确认；不能先假定它等价Fresh，也不能先假定老师说的Renew就是这种方式。

后一条至少需要Memory大小/字节、mutable globals、table元素及函数身份、被动段drop状态、Go heap/allocator/goroutine/TLS、计费状态、WASI文件/随机/时钟/任务/Selector、hostctx和跨合约回调全部恢复或重建。Step23历史Reuse/Fresh Gas差异只能说明需要语义验证，不能自动套成本轮Renew根因。

## 向老师确认的最小问题

1. Renew的原始论文/代码/commit是什么，API名字和native版本是什么？
2. 重建的是Memory映射、Store对象、Instance，还是全部运行时状态？是否允许保留已执行业务Instance？
3. 等价边界是_start前、_start后还是业务调用前？Gas/Go全局和WASI状态怎样定义？
4. 是否支持memory.grow、table/被动段、跨合约、trap/rollback、取消及重复调用？
5. 是否有新对象身份与资源所有权证明，而非只比较Memory字节？

## 建议

值得作为受控支线调研，暂不作为下一轮唯一核心。先明确Renew定义和现有实现；目前缺少可直接复用的全状态恢复协议。更接近现有证据、改动较小的主线是区间粒度/模板表示与热路径验证开销。任何Renew未来先做正确性和Gas反例测试，不立即以TPS为目标。
