# Step-18：Go/WASM 冷启动组合优化 pilot

本轮只做 compute、ERC721、fact 的小样本 VM 实验。**P 裁剪源码/构建流程未恢复，P=1 的四组保留为 blocked；不能宣称完成三因素组合验证。** A 使用已有可达静态数组填充原型，由原 Go 链接器修正地址；C 使用 step-16 去 active Data + fresh Memory Copy。没有扩大到八合约或启动真实节点。

实施状态、依赖、冲突和首次失败见 [AUDIT.md](AUDIT.md)。8 组组会表见 [PPT.md](PPT.md)；结果解释见 [RESULTS.md](RESULTS.md)。所有表中的缺失/blocked/not_tested 均不是通过。

## 固定环境与构建

- CVW 实验基线 `4cdf6c51df36f3ff350baf120863edc893da7383`，分支 `experiment/step18-combined-cold-start`，worktree `/home/frankie/mygitprojects/.worktrees/cvw-step18`。
- guest Go1.24.1，host Go1.25.0；ChainMaker VM/protocol2.4.0；Wasmer6.0.1。native库 SHA-256 `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。
- `environment.json`、`resolved-modules.txt`、`artifact_hashes.json` 记录源码、依赖、产物；原始文件及所有最终 WASM 保留在 `artifacts/`。`variants.csv` 同时列 plain 性能构建和 probe 诊断构建；P=1 不填造假的产物哈希。
- A：读取 Go1.24.1 `moduledata.end`，按首次 heap arena 预留点计算填充。本次固定构建在 initBloc 后还有5个64KiB的元数据页，诊断检查首次 `sysReserveAlignedSbrk` 的 bloc=4194304、skip=0、align=4194304。不将静态区末尾对齐视为已完成 A。此页数不是通用阈值，新 WASM 必须重新校准。
- P：只有四份历史裁剪 WASM，没有可恢复源码/配方，未改变 SDK 公开 API 来冒充旧 P。历史文件哈希见 `historical-pb-artifacts.json`。
- C：最终每份 WASM 独立重算模板/范围/哈希，去除 active Data 后编译；新建 Instance → Copy → WASI Initialize → `_start`。Module、源 WASM hash、合约版本、metering配置、native库指纹共同约束模板，禁止跨二进制复用。其他节保持逐字节相同，见 `static_sections.csv`。
- 诊断只改独立的 Go1.24.1 副本，原工具链不动。`diagnostic-runtime.patch` 与 `prototype/step18_wasm.go.txt` 保存插桩。plain/probe 各自布局校准，诊断的绝对时间不能替代未插桩性能。

## 统一计时边界

调用的是 **实际 `RuntimeInstance.Invoke` + 测试 TxSimContext/SnapshotMock**。`CM_FRESH_INVOKE=1` 令 GetInstance 同步创建，关闭同步完成，不复用已执行业务 Instance；本轮无池等待、无后台 grow。Module/模板预处理在样本窗口外单独统计。

|指标|边界|
|---|---|
|S0→S1|`newInstanceFromModule` 开始，含 UUID/WASI环境取得/import准备、NewInstance、C恢复，至静态 Memory 可用；不是仅 C API NewInstance|
|`start_ns`|调用 WASI start RawFunction 前后；不含 WASI Initialize/导出查找|
|A `a_ns`|仅 probe：`_start` 调用入口至非runtime package init开始；包含Go runtime启动，不含此前 WASI Initialize；guest/host单调时钟用7次调用中最小RTT校准，记录误差|
|B1 `b1_ns`|仅 probe：Go非runtime模块的 `doInit(m.inittasks)` 循环；含新增 A 小 init，不等于PB自身耗时|
|创建至S2|同S1起点，包含 WASI Initialize、`_start`；截止start返回，早于handle关闭/最终wrapper绑定|
|创建至S3|同创建起点至Invoke内SetGas返回，含S2后的绑定/控制逻辑|
|完整 `invoke_ns`|Invoke入口前至返回后，含GetInstance同步创建、上述初始化、SetGas、CallMethod/业务/host syscall、Gas读取、defer上下文清理、CallDeallocate及Instance.Close；测试Tx/参数map准备在窗口外|

这些阶段嵌套，不相加。plain 所有性能样本均无 S2 observer。probe 在S2读取标记/校准，会污染probe S3/Invoke，分析器只从probe提取A/B1和误差；不能用probe Invoke宣称性能收益。

每合约独立进程，4个有效组合每轮随机排列、5轮预热丢弃、40轮正式记录；固定 CPU affinity、GOMAXPROCS=1、关闭自动GC、每20轮边界显式GC。每个original/nodata/diagnostic模块在单独新进程作为首个模块编译并Serialize，测量时Deserialize。只对完全相同 WASM hash 的第一版A=0产物复用已隔离编译的模块，加载器仍检查ConfigID/ArtifactSHA。避免既有首编译Gas异常，并非把不同WASM共享Module。

`summary.csv` 使用中位数、nearest-rank P95；CI为4000次循环移动块bootstrap的中位数95%区间，块长5轮。`paired_effects.csv` 用同轮时间差，负值表示更快；`interactions.csv` 的 A×C 为 `t101-t100-t001+t000`，正值表示延迟改善小于简单相加。只有一批、40个配对轮，CI仅描述本机短批不确定性，不证明跨批/跨机器稳定性。

## 重现

在原报告目录运行；先保留现有结果，重建时使用新的输出目录/新的worktree，脚本不会覆盖已有 artifact 目录。P=1 当前明确不可重建，不会静默改成P=0。

```bash
cd /home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-18-combined-cold-start
python3 pipeline.py build
python3 pipeline.py host
python3 pipeline.py compile
python3 pipeline.py run --batch pilot-plain-n40 --mode plain --n 40 --seed 181701
python3 pipeline.py run --batch pilot-probe-n40 --mode probe --n 40 --seed 181701
python3 pipeline.py validate
python3 pipeline.py template-cost
python3 analyze.py
python3 report.py
```

重现脚本依赖既有step-14/15/16资料；`S18_REPO`可指定其CVW根目录，`S18_WORKTREE`可指定新的独立实验worktree。

代码在 `prototype/`，完整分支改动见 `prototype.patch`。原 step-16 helper 已在基线提交内。构建不升级任何依赖。`attempt-01-wrong-initbloc-target/` 是保留的失败恢复尝试，不参与最终统计。

## 正确性范围与回滚

`correctness.csv` 逐组报告真实guest业务返回、排序状态写集、事件、registry/native Gas、S1 Memory、Globals、fresh Memory/Globals隔离、模板不变性。实际执行host缺失导出方法分支，以及ERC721/fact非法数字输入的guest错误分支；不覆盖compute guest错误、全部trap/OOG/host错误。C0/C1在同逻辑WASM内要求Gas完全一致；跨A二进制分别记录启动与业务Gas，不能默认新合约Gas策略已获认可。Table提供静态Function/Code/Element保持和全表nullness；真实Table函数对象身份、真实跨合约调用均为not_tested，未认证生产安全。

关闭C：`CM_STATIC_MEMORY_COPY=0`；关闭A：恢复保留的A0原始WASM并重建/加载对应Module，不能对A1模板换一个开关冒充A0。P未启用。实验不改生产main/正式节点；回滚仅停止测试进程并切回原worktree，保留数据后可由用户移除独立实验worktree。不要对已有脏main执行reset。step-17缓存回收、共享Store race和真实Table身份问题未修复，本轮结果不能作为生产启用依据。
