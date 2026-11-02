# Copy真实机制与可证明的成本

路径别名与绝对目录见SOURCE_TRACE.md。当前版本是Host区间Copy，不是native memcpy新ABI或COW。

## 模板如何生成（A）

`V/step35_static.go:85 prepareStaticMemory`解析原WASM：`:134`按Memory Section initial pages分配零Image；Data Section按原顺序`:201 copy`叠加，重叠保留最后写入；`:208`排序，`:209`合并重叠/相邻，`:220`只删除**整段最终全零的合并区间**。混合区间中的零字节保留。`:230 NoData=out`移除Section11，其余Section保留。Key绑定合约名、版本、源SHA、配置。拒绝automatic start、passive/DataCount/复杂offset等语义；prepare失败会fallback。111个正式四组block中没有Copy fallback，见audit/record-verification.json。

`V/step35_node.go:125 prepare`缓存，首次按最终WASM重新生成并编译NoData；命中不再生成Image或重新编译。模板是_start前静态内存，不包含执行过的Go heap、mutable global或table快照。全Image占initial pages×64KiB，只读保存在Go plan中；Memory fresh、Instance fresh、globals/table由native正常新建。主计时前Query已加载模块，首次准备总成本单列MODULE_PREPARATION.csv；template-only与compile-only未可靠分离。

## 每次执行（A）

`restore:235`核对module指针/配置/短Key，`:241`GetMemory，`:245`Memory.Data取得借用slice视图，`:249`循环copy。memory.go:105使用reflect.SliceHeader引用native线性内存，**不分配第二个等长目标字节数组**。GetMemory/Exports/宿主包装仍可能创建小对象；其分配量未单独记录。

native baseline在`R/lib/vm/src/instance/mod.rs:1490 initialize_memories`逐DataInitializer取得Memory、算offset、做越界检查，然后`memory.rs:766 initialize_memory_with_data`→`:774 copy_from_slice`。Copy版本用NoData绕过此active Data循环，在fresh零内存上恢复最终Image区间；所以不是把同一批原Data复制两遍。native创建零Memory、WASI环境、imports、globals、table、Instance分配等并未跳过。

## 冻结WASM静态复核（A）

STATIC_LAYOUT.csv逐合同、plain/A列出初始页、模板容量、Data payload、并集、区间数、复制零字节、源/派生NoData/Image SHA。脚本只读字节，没有输出新WASM或运行native。

本轮Copy仍有约46,181～54,041个区间，实际复制约1.07～1.27MB，混合区间中的零字节约0.31～0.36MB。不能把此实现讲成一次大块Image Copy，也不能认为所有零字节都已剔除。多数原segment仍是单独的非相邻区间；收益可能来自省掉native逐segment路径和更直接的目标访问，但未做指令/干预实验，唯一机制仍属C。

## 最接近的可验证改进点（C/D）

**减少区间遍历次数与最小字节量是两种目标，不能自动等同。** COPY_RANGE_SCENARIOS.csv只计算静态操作量。compute plain：49,443区间/1,154,947B；允许覆盖≤64B的已知零gap后为13区间/2,026,437B；覆盖全部span为1区间/2,028,831B。这不是性能结果，增加约0.87MB字节可能换取更少loop/边界检查，也可能触碰更多页；须未来独立验证。

在fresh零目标且完整Image准确的约束下复制gap零字节保持初始语义；不能将该方案用于已执行业务Memory。纯零区间跳过依赖fresh零Memory，不能推广到Renew。只读源模板可共享，但guest写入页、全局、table身份、WASI与hostctx必须私有。

热路径额外整WASM SHA存在于Invoke与prepare，raw副本在runtime创建时存在；它们不是restore内的重复payload复制，不能统一叫Copy成本。未独立计时，不能把现有负收益归因于它们。

补充边界：native原始Data循环在一次wasm_instance_new内部执行，不能宣称Copy减少了约5万次cgo调用。本轮Host Copy也有约5万次Go内存copy，两个循环的固定/内存成本需要独立干预才能比较。A的纯零padding大部分不在copy范围，见STATIC_LAYOUT，不能将初始页数增长直接当作每笔Copy字节增长。
