# Step-18 当前实施审计（PB恢复后）

最初工作区审计和P blocked状态保留在 `initial-pilot/AUDIT.md`；**历史会话中已找回原SDK补丁与构建命令，P=1当前不再blocked。** 详细证据在 [recovered-pb/RECOVERY.md](recovered-pb/RECOVERY.md)，SDK改动未替换为其他实现。

|方向|恢复/实现状态|已验证范围|依赖与潜在冲突|
|---|---|---|---|
|A|恢复既有可达静态数组padding原型；Go链接器完整修正地址引用；不是单改initial memory|对每个最终P0/P1和plain/probe重新计算padding；三合约所有A1首次arena预留bloc=4MiB、对齐距离0|P改变静态末尾和对齐距离，旧padding不能直接复用；A增加initial memory/模板，新增init使native启动计量+16。首次误把initBloc本身对齐的失败尝试完整保留|
|P|从2026-09历史会话原补丁恢复SDK0.1.3私有副本；删除GetBatchState接口/实现及PB import|现有8合约均构建成功且无相关直接引用；三合约8组执行与错误路径复核；编译依赖不含pb-go/gogo-protobuf|缩减SDK公开API，不能无条件启用；改变WASM函数、Table、data布局与native启动计量；未验证所有SDK/反射行为。历史trimmed WASM是诊断构建，不能和新plain构建混比|
|C|沿用step-16，移除active Data后NewInstance，再在WASI/_start之前Host Copy|三合约最终AP各版本分别重算模板/哈希；C0/C1 S1/Globals、业务、Gas、fresh隔离一致|原始Data不重复初始化；Go自动_start是导出函数，不是自动start section。自动start/imported memory/passive data/DataCount/复杂offset仍保守拒绝/回退；P/C在S1有收益重叠|

兼容版本：guest Go1.24.1、host Go1.25.0、ChainMaker VM/protocol2.4.0、packaged Wasmer6.0.1。原Go、原SDK module cache和生产main不改。诊断是独立同版本Go副本，不进入性能结论。每个WASM单独新进程首次编译/Serialize，加载核对WASM hash、配置及产物hash；不跨不同二进制复用模板。

流水线：原始源代码 → 可选恢复的P → 每个P版本可选A源码padding/Go链接 → 最终WASM → 可选C数据剥离/模板 → fresh实例。A在源码/链接阶段完成，未采用手改WASM data offset的布局变换。

复用：旧保守transformer、step-16同步fresh Invoke/关闭路径、fixture、Table-nullness/隔离检查、完全相同P0 WASM/配置的隔离编译产物。重测：三合约完整8组40次同批配对、A/B1独立诊断、P1正确性、最终AP模板和Gas、预计算成本。未拼接旧4组样本或历史/tmp汇总。旧原始JSONL当前未找回，只恢复了历史汇总输出。

不能生产启用：SDK API缩减、Table真实函数身份、真实跨合约及全部OOG/trap未覆盖；step-17缓存退休/回收、fresh reset/close生命周期及共享Store race仍未修复。本次是串行VM/mock上下文，非真实节点、非升级/缓存失效/并发认证。全部safe字段为not_certified。
