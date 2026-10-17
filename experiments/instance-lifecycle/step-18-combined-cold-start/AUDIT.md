# Step-18 实施前审计

基线：CVW `4cdf6c51df36f3ff350baf120863edc893da7383`（step-16 实验分支），新 worktree `.worktrees/cvw-step18`，分支 `experiment/step18-combined-cold-start`。不改 main 的 VM、SDK、Go 或 native Wasmer。

|因素|可恢复实现|本轮处理|冲突/限制|
|---|---|---|---|
|A|`experiments/a_initial_memory_sweep/layout_pad_near.go`，通过可达静态数组交给原 Go 链接器重新布局，减少 `memAllocAligned` 前置释放/清零；不是仅改 memory min|恢复同类源码填充原型；读取 `runtime.firstmoduledata.end`，加上首次 arena 预留前的元数据空间，再计算 padding；诊断必须核实首次 `sysReserveAlignedSbrk` 的 bloc=4MiB、skip=0|旧 padding 1507328 仅适用对应 ERC721；新增可达数据/指针/init 会改变布局、体积、Gas，必须重新测量；不得手改 data offset|
|P|找到 `erc721-hotspot-research/pb-trim-artifacts/{original,trimmed}` 下四合约 WASM，但没有裁剪源码、补丁、构建记录；`pb-alignment-2x2/prepare.py` 仅接受现成二进制并改 memory min，不执行裁剪|P=1 的可重建流水线缺失，保留失败组；不拿历史二进制拼接新源码 A，也不用 minimal SDK 替代|只能确认历史体积变化，不能确认相同 SDK 语义、编译器、Gas 注册点或全部八合约可构建。SDK 0.1.3 的 GetBatchState 公开 API 使用 pb-go 的 BatchKey/BatchKeys，不能直接删除依赖|
|C|step-14 保守 data-section 变换，step-16 `static_init_copy.go` / `vm_pool.go` / `runtime.go` 集成|对每个最终支持的 WASM 重新生成模板、独立编译 original/nodata，再用 fresh 同步 Invoke 测试|必须先移除 active data，再在 WASI Initialize / `_start` 之前 Copy；不能复用旧二进制模板；不支持自动 start、导入 memory/global/table、passive data、DataCount/复杂 offset 等则保留失败/回退记录|

依赖顺序：原始源代码 → 可选 P（当前缺少可恢复实现）→ Go 链接器可选 A → 最终 WASM → 独立 C 变换/模板 → fresh Instance。A/P 改变静态布局及可能的 Gas；C 只在同一个逻辑 WASM 内要求 Gas 严格一致。

兼容性：guest Go 1.24.1，host Go 1.25.0，ChainMaker VM/protocol 2.4.0，packaged Wasmer 6.0.1，沿用 step-16 的 metering 配置。每个原始/去 data 模块单独进程首次编译并序列化，隔离已有首编译 Gas 异常。性能使用原版 Go，A/B1 诊断使用同版本工具链的独立插桩副本，不能混合计算绝对收益。

可复用：保守 transformer、计时边界、业务 fixtures、隔离/Table-nullness 测试、首编译隔离方法、统计工具。必须重测：所有新二进制的业务/Gas/隔离/Copy等价、A 的实际布局及 A×C 交互。旧 A 诊断收益、旧 Copy 绝对耗时、历史 PB 文件体积不能当作本轮组合收益。

Table：可复用静态 Element/Function/Code 保持证明和全表 nullness 检查；真实 Table 函数对象身份 API 不可用，仍为 not_tested。step-17 缓存回收/并发 race 未解决；本轮仅单线程 VM pilot，不证明生产安全。

搜索范围：本工作区（含隐藏文件）、`/home/frankie` 下 trim 源码/patch 名、module cache SDK 0.1.3，以及既有 PB/对齐脚本。没有发现可复建的真实合约 PB 裁剪实现。P=1 不自动删除，不宣称完成全三因素验证。

## 小样本恢复过程中的失败记录

`attempt-01-wrong-initbloc-target/` 保留第一轮全部 plain/probe 原始数据（各 480 条）。该轮把 initBloc 本身对齐4MiB，而旧 near 原型对齐的是首次 heap reserve 时的 bloc。静态区之后的运行时元数据分配会继续推进 bloc；因此这不是正确恢复的 near 优化，A=1 组不得作为有效组合结论。旧 ERC721 near 的1507328字节 padding 与当前 baseline 的 initBloc2359296 相加仅为3866624，距4MiB还有327680字节，已经说明二者不能混同。

修正仍是同一个可达数组填充方法：本固定版本试验先按五个64KiB元数据页预留，再由独立 runtime 诊断验证实际首次 reserve 的 bloc/skip/alignment。该页数不是通用启用阈值，任何新构建都必须重新校准/验证，不能只看 initial memory 页数或静态末尾地址。失败产物、样本和哈希不删除，不与修正后统计混合。

当前重建的 baseline WASM 与 step-16 保留的 WASM 哈希不同，业务 Gas 亦不同（例如 compute registry Gas 为120027，step-16样本为105920）。producers 均标记 Go1.24.1；同 Go 版本不等于相同源码/SDK产物。旧二进制缺少可反推的完整构建输入，不能用旧 Invoke 绝对耗时充当本轮 baseline，也不能把差异归因于 Copy 或单独归因于 Go 编译器。当前受控比较固定 worktree 中的合约源码与 registry、SDK依赖，并记录其哈希。
