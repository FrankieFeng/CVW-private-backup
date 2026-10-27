# 构建来源审计与恢复结论

## 恢复结果

**Step24B原件的匹配A/B1构建尚未可靠恢复，blocked；Step18同源的现有产物、原补丁和构建脚本可以恢复并核对哈希。本轮没有重新构建，因此不声称已完成逐字可重建验证。** 不把两个家族的时间或Gas拼接比较。

| 层次 | 固定版本/代码 | 本轮核查 |
|---|---|---|
| 原Copy | Step22 `394d291` | 原Data解析/restore、Gas映射、Managed owner等源码与Step25字节一致，原核查记录保存在audit/step25/audit/step22-identity.json |
| 原串行路径 | Step24B `570b06a` | 固定owner、每逻辑变体独占Store+Module，Module metadata持久scope；每Invoke fresh、同步关闭；每process最多2对 |
| A/PB布局家族 | Step18 `95903a3` | 原始plain WASM的SHA匹配Step25保存的MATRIX；wasm-validate通过；A/P0/P1各自布局独立校准，未交换padding |
| 实际采集代码与数据 | Step25 source `501200f`，data `be88d9a` | binary `b72ea6f87d2014356c01b4bb4e6d42f0a212c19e00d7d6ef310b1de7c80f8dd5`，相同配置和host Go1.25.0；Guest记录Go1.24.1；ChainMaker/protocol2.4.0；native6.0.1 SHA固定于原environment |
| Step26 | 基于`be88d9a`的独立分支 | 只读提取/复算，新增编译0、新Guest运行0；不是新采样批次 |

`audit/original_step25/environment.json`、`go.work`、`scripts/run.py`和八份核心Go源码冻结原实现；`MATRIX.csv`保存本轮G1/G2/G3对应的原WASM、执行noData、模板hash、cache key和SDK差异。原始command中的旧路径指向原worktree，作为历史证据保留，不伪装成本轮运行命令。

## 三种机制到底是什么

**A**：源码级可达静态padding数组、unsafe指针及init引用，由Go链接器重新排布并修正地址。旧脚本按各自P版本的module_end/bloc计算padding，目标为首次arena预留达到4MiB对齐，而不是把initBloc本身盲目对齐。增加Memory声明初始页和模板容量。它不修改Go Runtime清零算法，不是Step10的单纯initial memory=128页方案。证据为`audit/step25/audit/step18/pipeline.py`及P1独立layout表。

**B1**：本轮只能指历史恢复的PB依赖裁剪补丁。它删除SDK0.1.3中PB import、`SimContext.GetBatchState`公共接口、`SimContextImpl.GetBatchState`实现和`batchKeysLimit`，不是保留全部SDK API的透明优化，也不是所有B1优化的统称。旧恢复证据、会话摘录定位及完整diff在`audit/step25/audit/step18/recovered-pb/`。它改变WASM函数、Data和Table布局；A必须对P1重算。本轮使用已分别校准的现有plain产物，没有重写SDK或临时调整工作量。

**Copy**：`prepareStaticMemory`解析最终WASM active Data，生成S1 image、非零有效覆盖区间并移除原active Data初始化；相应noData Module编译一次并归属独立Store。新Instance创建后，在WASI.Initialize/_start之前`staticMemoryPlan.restore`执行Host区间copy。没有先完成原Data再重复复制。key绑定contract/version、最终WASM SHA和配置，module指针也核对；不同WASM不共用模板。非Data section保留，真实Table函数身份仍not_tested。

配置在同一Step25宿主代码上可组合，证据是实际三条直接对照及预检，不是源码相近就推断兼容。本轮新G3=旧G4；旧G3“B1+Copy”不属于本轮主比较，原负向结果仍保留于Step25和ALL_STEP25_RUNS清单。

## 为什么不能把Step24B原件视为已恢复

1. 原件WASM及SHA可恢复，但没有找到已验证的、与这些原件相同计费/构建链对应的A/B1变体。Step25的这些单元原本就标记blocked。
2. 当前build.sh指向Go1.24.1，只说明一个通用命令；没有将原件的源文件、SDK/标准库状态、工作区replace/overlay、插桩器版本/黑名单/参数及构建flags完整绑定到这些SHA。当前源码不能代替历史编译时源码。
3. `testdata-instrument.zip`实际存在，但compute/erc721/fact的WASM SHA分别为`0734282a...`、`29cfe272...`、`dc3609ef...`，均不匹配24B原件。zip中compute源码循环10000，不是原件100。逐项大小/全SHA与zip SHA见`audit/lineage-findings.json`。
4. 仓库有instrumenter/instrumenter-go源代码和旧Windows路径日志，它们可以修改AST并插入ConsumeGas；没有证据把某一套输入/输出/黑名单和原件建立唯一对应。工具存在不等于原件构建已恢复。本轮没有运行它们，也没用它们制造“历史”产物。
5. 原件与Step18二进制size/hash/布局及Gas不同，不能仅凭Go版本号相同认定同源。没有通过把10000改成100、替换SDK或复制旧padding强行对齐。

这不是宣称永远无法恢复；只是截至本轮仍缺证据。下一步所需最小资料：原件实际Go源码和所有生成文件、原SDK/标准库或其改动hash、插桩器版本与黑名单/参数、go.work/replace及完整build命令/flags。先重建可核对的G0来源（若路径/build ID导致hash差异需逐项解释），再构建A/B1，并在原件相同输入下核对业务、计费路径与布局。不能在没有这条链时称原件组合恢复成功。

## 两家族已证实的差异

`BINARY_LINEAGE.csv`给出实际文件大小、Memory声明初始页和完整SHA；`audit/step24b-bigNumCal.txt`与`step18-bigNumCal.txt`来自实际WASM反汇编。

- 原24B `main.bigNumCal`循环比较为100，Step18为10000；返回值相同不表示工作量相同。当前Step18源码也为10000，但结论以反汇编为依据。
- 在Step25两家族参考中，三个方法的业务参数、固定TxID、初始/最终账本、根RWSet及Gas外返回值均相同，仍有不同Gas：compute 120027 vs105920，fact154 vs1585，ERC721235 vs15981（Step18 vs原件）。所以不能把全部家族差异归为请求参数不一致。
- 历史24B ERC的15677与Step25原件参考15981之间有固定TxID格式差异；这项跨轮差别不能用来证明Copy改变Gas。本轮不使用这类跨轮差作组合效应。
- 是否由标准库/SDK插桩覆盖、具体函数路径或其他构建差异导致跨家族Gas不同，仍未唯一定位；不同Gas本身不是某个具体机制的证明。

相同业务输出/账本并不能补齐源代码、SDK或计费构建的来源缺口。本轮只对Step18同源家族内的直接增量作性能与正确性判断。

## API兼容性与下一步

GetBatchState用户代码不能直接用该删API SDK构建；SDK接口方法集合/反射和间接依赖行为也未通用验证。三个目标方法通过不能推导通用兼容。不自动启用B1，不把它作为生产SDK替换方案。完整组合可作明确白名单合约的隔离研究候选；保留原SDK API的A+Copy更适合作为优先继续路线，但仍需补原件匹配构建及未测安全项。
