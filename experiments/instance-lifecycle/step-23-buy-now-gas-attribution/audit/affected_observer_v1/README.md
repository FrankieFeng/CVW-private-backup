# Step-23：buyNow Gas差异归因与Copy正确性复核

2026-10-26启动，2026-10-27收尾（Asia/Shanghai）。独立分支 `experiment/step23-buy-now-gas-attribution`，父Step22 `394d291`；历史只读核对Step21E `507310c`。**已实际执行**六个探针开/关预检、五个生命周期配对块、五个Fresh/Copy配对块；共26个有界独立进程，每进程三次真实init及一次根buyNow/六个真实callee。未启动原后台池、并发、节点或TPS测试，未改生产VM/Gas规则，未推送。

## 六个问题的答案

1. **历史比较条件**：21E buyNow是R0从init开始保留每合约Instance，对R1每次子调用Fresh；每进程只有一次目标根调用。第六callee的R0 ERC721已执行init、mint、approval，不是“两个根调用冷/热”。21E独立fact/ERC重复调用是另一条件。
2. **独立复现**：本轮五块都得到根Gas R0 **12761395**、R1 **12765774**，差 **4379**。真实初始账本、输入/TxID、结果、读写集和事件相同。新R1按Store缓存Module，仍能复现，说明每次重新编译并不是出现这项Gas差异的必要条件。
3. **首次当前调用Gas分歧**：五块都是第六次子调用 `erc721.transferFrom`，深度1。R0为同一ERC721 Instance ID2、此前使用3次；R1为新ID10、此前使用0次。前五callee入参/累计返回相同。
4. **最早计量阶段**：本次SetGas重置后的所有已采样计数，在该callee `DeleteState.after`仍为6378616；下一个 `log_message.before`为R0 **6386180**、R1 **6390559**。差值已在这两个已采样ChainMaker host边界之间产生；然后经原WACSI返回值、父SetGas和最终Getter传播至根。不是根最后结算时凭空产生。
5. **Copy正确性**：第二阶段完成后另跑五块Fresh Baseline vs Fresh+Copy。根Gas均 **12765774**；**35对根/子调用**的输入、Gas、返回/错误、可见读写集、事件及根最终账本均相同。每块147个计数边界和36个桥接快照均逐值相同。没有以Memory hash替代Gas验证。
6. **已证实与缺口**：已证实具体条件、首差窗口和向上传播；**尚未定位到某个具体guest函数/指令/缓存**。JSON编码器缓存只是历史源码支持的候选，不是本轮已证实原因；未以耗时或4379差值反推Go机制。真实Table函数身份、异常/OOG、长期资源边界仍not_tested。

注意：进入SetGas前，R0保留旧计数，Fresh观测初值9223372036854775807，早已存在生命周期状态差异。此旧值不是本次已收费Gas。两侧在原SetGas后都恢复相同的当前调用预算；“首差第六次”专指**本次预算重置后的已采样Gas轨迹**，不是声称所有Runtime状态此前相同。

## 条件与执行

R0：每合约一个已真实init的Instance/WASI bundle持续使用；不清guest缓存、不为追平Gas做重置。R1：同样缓存Store+Module，每次新WASI/Instance。C1：R1生命周期，原Step22 noData+静态区间Copy；恢复发生在WASI.Initialize/_start之前。原active Data初始化已移除，不是原版初始化后追加复制。

三组使用相同build02 binary、三个原WASM、参数、公开测试成员、BlockVersion1/ETHEREUM配置、原Gas映射。固定根TxID `step21c-buy-001`、tokenId1、from/to/metadata；真实init顺序identity→ERC721→exchange，初始/最终账本与21E原receipt严格匹配。每条件分别运行独立进程/等价账本；原始Fixture不伪造callee成功返回。

Store/Module每合约/变体只准备一次（共六个预备Module、实际使用三个），实际Store/Module ID证明没有逐子调用重编译。模板/准备成本另记preparation.csv，不用这些重构成本解释Gas或计算TPS。R0/R1块顺序交替；前三块差异稳定且资源正常，按保存extension_gate扩到五。之后才运行独立Copy五块，顺序交替。

## 实际六个下游结果

下表五个生命周期块完全一致，仍逐块保留在BLOCK_SUMMARY、GAS_TRACE和原日志中；不是把五块压成单样本。

| 子调用序号 | 下游方法 | Gas入参（两组相同） | R0累计返回 | R1累计返回 | R0本地增量 | R1本地增量 | R0/R1此前使用次数 |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | identity.addWriteList | 100276 | 101804 | 101804 | 1528 | 1528 | 1/0 |
| 2 | identity.isApprovedUser | 302309 | 302538 | 302538 | 229 | 229 | 2/0 |
| 3 | identity.isApprovedUser | 705088 | 705317 | 705317 | 229 | 229 | 3/0 |
| 4 | erc721.mint | 1510668 | 1525965 | 1525965 | 15297 | 15297 | 1/0 |
| 5 | erc721.setApprovalForAll2 | 3136862 | 3137143 | 3137143 | 281 | 281 | 2/0 |
| 6 | erc721.transferFrom | 6374268 | 6386947 | 6391326 | 12679 | 17058 | 3/0 |

“本地增量”=累计返回−Gas入参，仅是原API边界增量，根仍包含嵌套执行；**不能把累计子Gas相加**。完整向上传播见GAS_ATTRIBUTION.md和GAS_PROPAGATION.csv。

## Fresh/Copy独立复核

| 调用 | Fresh Baseline累计Gas | Fresh+Copy累计Gas | 五块结果 |
|---|---:|---:|---|
| 0 exchange.buyNow | 12765774 | 12765774 | 相等 |
| 1 identity.addWriteList | 101804 | 101804 | 相等 |
| 2 identity.isApprovedUser | 302538 | 302538 | 相等 |
| 3 identity.isApprovedUser | 705317 | 705317 | 相等 |
| 4 erc721.mint | 1525965 | 1525965 | 相等 |
| 5 erc721.setApprovalForAll2 | 3137143 | 3137143 | 相等 |
| 6 erc721.transferFrom | 6391326 | 6391326 | 相等 |

S1全Memory hash在每个新建Instance上实际核对原Image；Copy源码和Gas配置未变。Bytecode/Table/Element/Global section保持不变不等于真实Table函数身份已验证。读写观测使用当前深度可见的累计映射，不伪称callee独占写集；最终root RWSet为原TxSimContext实际结果。此结论只覆盖指定成功路径，不能扩展到所有输入/异常或生产启用。

## 资源与局限

26进程全部退出，260个含init Invoke均实际成功；目标业务为26根+156个callee。原Getter与只读registry在既有Getter处核对，三模式probe on/off的最终Gas和业务相同；诊断有明显日志开销，不用于性能结论。

外部采样+边界日志峰值 **763.61MiB / 177线程**，未提高1536MiB/220软限，硬限2GiB/256任务/60秒，Go45秒。Scope登记最终0、所有进程退出、WSL boot ID未变。Store长寿命WASI线程增长与精确native构建来源问题未解决，本轮有限进程不能认证长期有界或默认池安全。

Step21E与22虽然业务输入及初始账本相同，根TxID不同，不能直接减绝对Gas。本轮统一21E TxID后恢复了21E绝对值；未做TxID单因素干预，不能把原1520差额全部断言为TxID成本。

## 交付与复算

- [HISTORICAL_AUDIT.md](HISTORICAL_AUDIT.md)：原始证据、条件对照及冷/热/复用区分。
- [GAS_ATTRIBUTION.md](GAS_ATTRIBUTION.md)：首差窗口、父子Gas传播和未定位项。
- [GAS_TRACE.csv](GAS_TRACE.csv)、[CALLS.csv](CALLS.csv)、[BRIDGE_GAS.csv](BRIDGE_GAS.csv)：逐计数点、逐调用和桥接观察，包含TxID、序号/深度/Instance、输入/状态摘要。
- [STATE_COMPARISON.csv](STATE_COMPARISON.csv)、[COPY_PARITY.csv](COPY_PARITY.csv)、[BLOCK_SUMMARY.csv](BLOCK_SUMMARY.csv)：逐块/逐层业务与Gas比较，not_tested明确保留。
- [raw_logs](raw_logs/)、[audit](audit/)、[source.diff](source.diff)、[SOURCE_INDEX.md](SOURCE_INDEX.md)、[ENVIRONMENT.md](ENVIRONMENT.md)：原命令、真实receipt、slot/源码/binary哈希、回收与引用行号。
- [SAFETY_AND_LIMITS.md](SAFETY_AND_LIMITS.md)、[RUNNING.md](RUNNING.md)、[PROGRESS.md](PROGRESS.md)：安全边界、运行/恢复/回滚；所有旧数据保留。

只复算：`python3 -B scripts/analyze.py`、`python3 -B scripts/write_report.py`。源码冻结提交 `pending`。后续若要追到具体Go函数，需另设计函数级无Gas扰动观测或受控干预；本轮不再扩展新机制/负载。
