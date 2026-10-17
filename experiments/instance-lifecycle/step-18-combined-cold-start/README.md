# Step-18：Go/WASM冷启动完整8组pilot

**已从历史会话恢复原PB裁剪补丁，补齐compute/ERC721/fact全部8组。** 本批三项组合比C单独开启进一步降低完整VM Invoke中位数；compute的P95未全面胜出，仍需独立批次确认。此前P blocked判断已修正，初始报告与样本完整保留。

- [恢复证据与SDK语义变化](recovered-pb/RECOVERY.md)
- [当前实施审计](AUDIT.md)
- [完整结果、CI、交互与内存分析](RESULTS.md)
- [8组PPT对照表](PPT.md)

`samples.csv`有960条plain和960条独立probe，三合约每组40次。`summary.csv`、`paired_effects.csv`、`interactions.csv`、`variants.csv`、`correctness.csv`为当前完整矩阵；所有原始JSONL在`full-pilot/`。`initial-pilot/`保存原4组/blocked报告，`pilot-plain-n40/`和`pilot-probe-n40/`仍是原4组数据；`attempt-01-wrong-initbloc-target/`保留失败的首次A恢复，均不混入新批。

## 固定构建

独立worktree `/home/frankie/mygitprojects/.worktrees/cvw-step18`，分支 `experiment/step18-combined-cold-start`；基础提交4cdf6c51df36f3ff350baf120863edc893da7383，初始报告提交d9a117b。当前提交见branch.json。

guest Go1.24.1、host Go1.25.0、VM/protocol2.4.0、Wasmer6.0.1不变；native SHA256为dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9。SDK是在0.1.3源码私有副本上应用原历史API删除补丁，原module cache不变。所有最终原始WASM、nodata、模板在artifacts，各自按最终WASM/配置关联，无跨二进制模板复用。

A通过可达数组交给Go链接器布局，不手改WASM偏移；每个P版本重新校准首次heap arena位置。P删除GetBatchState API，非透明裁剪；仅限不依赖该API/相关反射行为且已验证的构建。C使用新Instance的初始零memory，去active Data后直接拷贝必要范围，发生在WASI Initialize/_start之前。不做S2 Snapshot，不复用已执行业务Instance。

## 计时和统计

实际RuntimeInstance.Invoke + 测试TxSimContext/SnapshotMock。CM_FRESH_INVOKE=1使GetInstance同步新建、Revert同步关闭，无后台grow/池等待。完整Invoke含NewInstance、WASI Initialize、_start、SetGas、CallMethod/业务/host syscall、Gas读取、上下文清理、CallDeallocate和Instance.Close；测试Tx和参数构造、Module/模板预处理在窗口外。

S1从newInstanceFromModule入口到静态memory就绪，含UUID/import/WASI环境准备和Copy；S2同起点至_start返回；S3同起点至SetGas返回。start_ns仅RawFunction.Call。阶段嵌套，不能相加。A/B1来自独立probe的host/guest单调时钟标记，记录校准误差；probe S2 observer影响S3/Invoke，正式结论只用plain。

每合约单进程、8个实验池共存、每轮8组随机排列、5轮预热、40轮采样、固定CPU affinity与GOMAXPROCS1、关闭自动GC并在20轮边界GC。每个original/nodata单独首编译/Serialize，测量进程Deserialize，隔离已有首编译Gas异常。相同P0源hash/配置的旧隔离产物可复用，加载器仍核对来源及产物。

Median、nearest-rank P95；CI为4000次循环移动块bootstrap中位数区间，块长5轮。配对差在同轮计算；负值更快。二阶/三阶交互同轮先作有限差分再统计，不由不同组中位数相加。只有一个完整矩阵批次，不宣称跨批稳定或节点收益。

## 重新构建和运行

现有结果不覆盖；使用新的输出目录和独立worktree。S18_REPO指向保留step-14/15/16资料的原CVW，S18_WORKTREE可指定新的实验worktree。SDK副本和diff已持久化，不依赖原/tmp目录或再读取会话。

```bash
python3 pipeline.py build                 # 构建P0；已有artifact时拒绝覆盖
python3 recovered-pb/restore.py           # SDK私有副本应用已恢复原补丁
python3 recovered-pb/build.py             # P1、每P校准A、每最终WASM重算C
python3 pipeline.py host
python3 full_pilot.py prepare             # P1逐模块独立首编译
python3 full_pilot.py run --mode probe --n 40 --seed 181802
python3 full_pilot.py run --mode plain --n 40 --seed 181802
python3 full_pilot.py validate
python3 analyze_full.py
python3 publish_full.py
```

SDK source在recovered-pb/sdk，Go诊断patch和prototype在根目录；原始Go工具链不修改。旧analyze.py/report.py是初始4组分析器，当前完整结果请使用analyze_full.py/publish_full.py。重现编译阶段的SDK公共API变更必须保留审计，不得换成其他实现来冒充P。

## 正确性和回退

correctness.csv逐组给出S1 Memory、Globals、业务输出/写集/事件、同逻辑WASM的Gas、模板不变性和fresh隔离。Table静态节保持并检查全表nullness；真实函数身份仍not_tested。ERC721/fact实际执行非法数字输入的guest错误；compute guest异常、真实跨合约和全部trap/OOG未覆盖。8目标合约P1构建成功不等于8合约业务安全通过。全部safe=not_certified。

新进程/重建池时CM_STATIC_MEMORY_COPY=0并加载对应original模块可关闭C。A/P关闭必须选择保留的A0/P0 WASM重建Module，不能给其他二进制套旧模板。完整回退选择000原始WASM、关闭C并停止实验进程；生产main/正式节点从未修改，不对脏main做reset。step-17缓存退休/回收、race、真实Table身份问题未解决，当前不能生产启用。
