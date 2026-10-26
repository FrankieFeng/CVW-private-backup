"""Render Step23 from saved raw evidence, with no guest or performance experiment."""
from pathlib import Path
import csv,json,re
from compare import P,load
v=json.loads((P/'verification.json').read_text());env=json.loads((P/'environment.json').read_text())
r0=load('v2-lifecycle-b1-R0');r1=load('v2-lifecycle-b1-R1');cc=load('v2-copy-b1-C1')
table='| 子调用序号 | 下游方法 | Gas入参（两组相同） | R0累计返回 | R1累计返回 | R0本地增量 | R1本地增量 | R0/R1此前使用次数 |\n|---:|---|---:|---:|---:|---:|---:|---|\n'
for a,b in zip(r0['calls'][1:],r1['calls'][1:]):
 table+=f"| {a['call_id']} | {a['contract']}.{a['method']} | {a['gas_in_cumulative']} | {a['gas_out_cumulative']} | {b['gas_out_cumulative']} | {a['gas_out_cumulative']-a['gas_in_cumulative']} | {b['gas_out_cumulative']-b['gas_in_cumulative']} | {a['instance_uses_before']}/{b['instance_uses_before']} |\n"
parity='| 调用 | Fresh Baseline累计Gas | Fresh+Copy累计Gas | 五块结果 |\n|---|---:|---:|---|\n'
for a,b in zip(r1['calls'],cc['calls']):parity+=f"| {a['call_id']} {a['contract']}.{a['method']} | {a['gas_out_cumulative']} | {b['gas_out_cumulative']} | 相等 |\n"
readme=f'''# Step-23：buyNow Gas差异归因与Copy正确性复核

2026-10-26启动，2026-10-27收尾（Asia/Shanghai）。独立分支 `experiment/step23-buy-now-gas-attribution`，父Step22 `394d291`；历史只读核对Step21E `507310c`。**已实际执行**六个探针开/关预检、五个生命周期配对块、五个Fresh/Copy配对块；最终有效v2共26个有界独立进程（另有26个受影响v1过程完整保留且不纳入结论），每进程三次真实init及一次根buyNow/六个真实callee。未启动原后台池、并发、节点或TPS测试，未改生产VM/Gas规则，未推送。

## 六个问题的答案

1. **历史比较条件**：21E buyNow是R0从init开始保留每合约Instance，对R1每次子调用Fresh；每进程只有一次目标根调用。第六callee的R0 ERC721已执行init、mint、approval，不是“两个根调用冷/热”。21E独立fact/ERC重复调用是另一条件。
2. **独立复现**：本轮五块都得到根Gas R0 **12761395**、R1 **12765774**，差 **4379**。真实初始账本、输入/TxID、结果、读写集和事件相同。新R1按Store缓存Module，仍能复现，说明每次重新编译并不是出现这项Gas差异的必要条件。
3. **首次当前调用Gas分歧**：五块都是第六次子调用 `erc721.transferFrom`，深度1。R0为同一ERC721 Instance ID2、此前使用3次；R1为新ID10、此前使用0次。前五callee入参/累计返回相同。
4. **最早计量阶段**：本次SetGas重置后的所有已采样计数，在该callee `DeleteState.after`仍为6378616；下一个 `log_message.before`为R0 **6386180**、R1 **6390559**。差值已在这两个已采样ChainMaker host边界之间产生；然后经原WACSI返回值、父SetGas和最终Getter传播至根。不是根最后结算时凭空产生。
5. **Copy正确性**：第二阶段完成后另跑五块Fresh Baseline vs Fresh+Copy。根Gas均 **12765774**；**35对根/子调用**的输入、Gas、返回/错误、观测业务状态操作/派生集合、事件及根最终账本均相同。每块147个计数边界和36个桥接快照均逐值相同。没有以Memory hash替代Gas验证。
6. **已证实与缺口**：已证实具体条件、首差窗口和向上传播；**尚未定位到某个具体guest函数/指令/缓存**。JSON编码器缓存只是历史源码支持的候选，不是本轮已证实原因；未以耗时或4379差值反推Go机制。真实Table函数身份、异常/OOG、长期资源边界仍not_tested。

注意：进入SetGas前，R0保留旧计数，Fresh观测初值9223372036854775807，早已存在生命周期状态差异。此旧值不是本次已收费Gas。两侧在原SetGas后都恢复相同的当前调用预算；“首差第六次”专指**本次预算重置后的已采样Gas轨迹**，不是声称所有Runtime状态此前相同。

## 条件与执行

R0：每合约一个已真实init的Instance/WASI bundle持续使用；不清guest缓存、不为追平Gas做重置。R1：同样缓存Store+Module，每次新WASI/Instance。C1：R1生命周期，原Step22 noData+静态区间Copy；恢复发生在WASI.Initialize/_start之前。原active Data初始化已移除，不是原版初始化后追加复制。

三组使用相同build03 binary、三个原WASM、参数、公开测试成员、BlockVersion1/ETHEREUM配置、原Gas映射。固定根TxID `step21c-buy-001`、tokenId1、from/to/metadata；真实init顺序identity→ERC721→exchange，初始/最终账本与21E原receipt严格匹配。每条件分别运行独立进程/等价账本；原始Fixture不伪造callee成功返回。

Store/Module每合约/变体只准备一次（共六个预备Module、实际使用三个），实际Store/Module ID证明没有逐子调用重编译。模板/准备成本另记preparation.csv，不用这些重构成本解释Gas或计算TPS。R0/R1块顺序交替；前三块差异稳定且资源正常，按保存extension_gate扩到五。之后才运行独立Copy五块，顺序交替。

## 实际六个下游结果

下表五个生命周期块完全一致，仍逐块保留在BLOCK_SUMMARY、GAS_TRACE和原日志中；不是把五块压成单样本。

{table}
“本地增量”=累计返回−Gas入参，仅是原API边界增量，根仍包含嵌套执行；**不能把累计子Gas相加**。完整向上传播见GAS_ATTRIBUTION.md和GAS_PROPAGATION.csv。

## Fresh/Copy独立复核

{parity}
S1全Memory hash在每个新建Instance上实际核对原Image；Copy源码和Gas配置未变。Bytecode/Table/Element/Global section保持不变不等于真实Table函数身份已验证。读写观测用真实Get/Put/Del透明转发，逐call记录实际请求/返回；框架内部每callee完整RWMap未读取，明确not_tested。根最终RWSet为原TxSimContext实际结果。此结论只覆盖指定成功路径，不能扩展到所有输入/异常或生产启用。

## 资源与局限

最终有效v2的26进程全部退出，260个含init Invoke均实际成功；目标业务为26根+156个callee。原Getter与只读registry在既有Getter处核对，三模式probe on/off的最终Gas和业务相同；诊断有明显日志开销，不用于性能结论。

外部采样+边界日志峰值 **{v['peak_rss_mib']:.2f}MiB / {v['peak_threads']}线程**，未提高1536MiB/220软限，硬限2GiB/256任务/60秒，Go45秒。Scope登记最终0、所有进程退出、WSL boot ID未变。Store长寿命WASI线程增长与精确native构建来源问题未解决，本轮有限进程不能认证长期有界或默认池安全。

Step21E与22虽然业务输入及初始账本相同，根TxID不同，不能直接减绝对Gas。本轮统一21E TxID后恢复了21E绝对值；未做TxID单因素干预，不能把原1520差额全部断言为TxID成本。

## 观测器修正与数据排除

最初v1使用GetTxRWMapByContractName，深审发现mergeTxReadSet(dst,src)/mergeTxWriteSet会写内部dst，并非只读。该26进程的源码、原CSV/报告已冻结audit/affected_observer_v1，原日志/命令/receipt均保留，ALL_RUNS标记不可作最终只读结论。

修正v2不再调用任何中途RWMap/GetTxRWSet接口，只透明转发原Get/Put/Del一次并复制观察值，不清缓存、不改Gas。**v2重新完成全部六个on/off预检、五个生命周期块及五个Copy块**；不是仅靠旧数据继续声称通过。最终表/验证只使用v2标签/build03；总计实际执行52个有界进程。受影响v1不得合并扩大样本数。

## 交付与复算

- [HISTORICAL_AUDIT.md](HISTORICAL_AUDIT.md)：原始证据、条件对照及冷/热/复用区分。
- [GAS_ATTRIBUTION.md](GAS_ATTRIBUTION.md)：首差窗口、父子Gas传播和未定位项。
- [GAS_TRACE.csv](GAS_TRACE.csv)、[CALLS.csv](CALLS.csv)、[BRIDGE_GAS.csv](BRIDGE_GAS.csv)：逐计数点、逐调用和桥接观察，包含TxID、序号/深度/Instance、输入/状态摘要。
- [STATE_COMPARISON.csv](STATE_COMPARISON.csv)、[COPY_PARITY.csv](COPY_PARITY.csv)、[BLOCK_SUMMARY.csv](BLOCK_SUMMARY.csv)：逐块/逐层业务与Gas比较，not_tested明确保留。
- [BUSINESS_STATE_OPS.csv](BUSINESS_STATE_OPS.csv)、[BUSINESS_RWSETS.csv](BUSINESS_RWSETS.csv)、[STATE_OBSERVER_COVERAGE.csv](STATE_OBSERVER_COVERAGE.csv)：实际业务Get/Put/Del及派生集合，逐项核对原Host调用恰好转发一次；框架内部callee完整RWSet不冒充已测。
- [raw_logs](raw_logs/)、[audit](audit/)、[source.diff](source.diff)、[SOURCE_INDEX.md](SOURCE_INDEX.md)、[ENVIRONMENT.md](ENVIRONMENT.md)：原命令、真实receipt、slot/源码/binary哈希、回收与引用行号。
- [SAFETY_AND_LIMITS.md](SAFETY_AND_LIMITS.md)、[RUNNING.md](RUNNING.md)、[PROGRESS.md](PROGRESS.md)：安全边界、运行/恢复/回滚；所有旧数据保留。

只复算：`python3 -B scripts/analyze.py`、`python3 -B scripts/write_report.py`。源码冻结提交 `{env.get('source_commit','pending')}`。后续若要追到具体Go函数，需另设计函数级无Gas扰动观测或受控干预；本轮不再扩展新机制/负载。
'''
(P/'README.md').write_text(readme)
gas='''# Gas首差与传播：已定位到窗口，尚未定位具体函数

所有五块有相同整数结果，首次分歧原事件完整保存在audit/first_divergences.json；GAS_TRACE可按run_label + tx_id + call_sequence + point_sequence复算。没有以exportFunc.Call耗时推导Gas。

## 调用与状态

外部→exchange.buyNow（深度0、根序号0），依次六个真实VmManager下游（深度1）：identity.addWriteList、两次isApprovedUser、ERC721.mint、setApprovalForAll2、transferFrom。R0三个Instance分别ID1 identity、ID2 ERC721、ID3 exchange，从真实init一直保留；R1/C1初始化各一个，业务根ID4，六个callee为ID5–10。新建模式的uses_before全部0。

R0根在本轮只init过，没有预热第二根buyNow；ERC721到第6callee已走init/mint/approval。冷/热是具体执行历史描述，不是对reuse/fresh的同义替换。新模型把R1的Store/Module也缓存，在同Store上连续创建不同Fresh Instance后依然复现差值；不能把历史“每调用编译”当必要根因。仍未单独隔离Instance私有guest状态与其WASI bundle状态。

## 最早当前调用计数差

| 观测边界 | R0 | R1 | 解释 |
|---|---:|---:|---|
| root原SetGas后已用Gas | 0 | 0 | 旧Instance Gas与Fresh初值差异已由原SetGas覆盖 |
| 第6子调用Gas入参/SetGas后 | 6374268 | 6374268 | 更早调用没有把差额带入 |
| transferFrom DeleteState.after，seq36 | 6378616 | 6378616 | 最后相同的计费点 |
| 下一log_message.before，seq37 | 6386180 | 6390559 | 首个已采样不同点，差4379 |
| 该窗口增量 | 7564 | 11943 | 由同一个上一点逐条相减，非不同批次 |
| callee最终GetGas累计已用 | 6386947 | 6391326 | 后续各增加767，差值不再扩大 |
| callee本地边界增量 | 12679 | 17058 | 累计返回−相同入参 |

seq37的相同文本为`setTokenLatestTxInfo to {"TxId":"step21c-buy-001",...}`。它在日志宿主实际处理前已经携带不同计数。先前观测业务状态操作、输入、全部已采样ChainMaker host调用形状和前五callee计数均相同。

这是**两个已采样ChainMaker host边界之间的guest执行窗口**，包括未细分的Go runtime行为；WASI imports没有逐项采样，不能据此排除未观测WASI行为或声称逐guest指令路径完全一致。源码参考`setTokenLatestTxInfo`包含构造对象、json.Marshal、格式化与日志；WASM含encoding/json相关函数。这只支持JSON缓存候选，没有逐函数/指令Gas和受控干预，不能把4379完整归给某个编码器、GC、分配或缓存。

## 传播到父与最终Gas

| 阶段 | R0 | R1 |
|---|---:|---:|
| root第6次before_wacsi已用 | 6274268 | 6274268 |
| 原跨合约基础费 | 100000 | 100000 |
| 传给子调用的累计Gas | 6374268 | 6374268 |
| 子返回累计Gas | 6386947 | 6391326 |
| WACSI返回gas | 12761215 | 12765594 |
| 原parent SetGas后已用 | 12761215 | 12765594 |
| root最后GetGas/ContractResult | 12761395 | 12765774 |

本fixture为BlockVersion1，保留既有`WacsiImpl.CallContract`：先`gasUsed += CallContractGasOnce`，子调用接收此累计值，返回后`gasUsed += result.GasUsed`。因此本实现的WACSI值为6374268+子累计返回；不能把子结果误当“纯本地Gas”。这里只复核现存公式和相同计量边界，**不据此认证收费公式全局正确，也没有改它**。

`after_wacsi`时父registry仍是调用前相同值6274268，但WACSI返回已含差额；原`setGasByExport`之后父计数才带上4379差额。root之后均再增加180，故根差完整由该callee带回，末尾Getter/结算没有新增差额。36个桥接快照（12次core调用×3阶段）及每次原Getter读数核对支持这一定位。

为什么是12次core却只有6个callee：每个SDK跨调用的is_len=true会真实执行一次子合约；is_len=false只读取缓存结果。原wasi.go有明确分支，实际dRuntime Invoke记录始终为根+6，不把取结果当额外业务执行。

当前Gas是runtime原GetGas的registry Remain：`runtimeGasLimit - Remain`，不是native fuel、指令数、CPU周期或时间。GasOut是业务后、CallDeallocate/销毁前的原Getter结算值；关闭阶段不读取已销毁memory，也不重定义原Gas范围。

## Copy单独判断

五块Fresh/Copy根/六子返回相等，各147个原gas点及36桥接快照相等；同WASM/source SHA、原Gas规则和等状态输入，无模块升级或SDK替换。35对CALL/STATE复核与Memory hash独立进行，所以不是通过hash推断Gas。R0热态少4379不构成Cold Copy必须追平的目标。

未验证的Table函数身份、内部Globals全量动态比较、异常/OOG/回滚、真实节点及长期Store并发/回收仍not_tested。根因只定位到上述窗口，不能用假设替代尚缺证据。
'''
(P/'GAS_ATTRIBUTION.md').write_text(gas)
environment=f'''# Step-23 环境与版本

- 2026-10-26开始，2026-10-27收尾，Asia/Shanghai。独立worktree /home/frankie/mygitprojects/.worktrees/cvw-step23；父394d2914289caace077349dd99677f430005ab6c，历史507310cb391de666cfadf5d3712dcebee13de885；源码冻结提交{env.get('source_commit','pending')}。
- 分支experiment/step23-buy-now-gas-attribution。生产工作区原在step-21b-wasmer-store-lifecycle/620650d，已有脏文件保留；本轮仅新增Step23实验及IDE镜像。
- Host Go1.25.0，GOMAXPROCS2/GOGC100，Go test -p2 -c，GOPROXY=off/GOTOOLCHAIN=local；当前WSL/CPU信息与完整source hashes见environment.json。
- 有效v2 build03 binary SHA `{env['binary_sha']}`，所有有效v2的26个进程相同，v1 build02另保留。build01因遗漏占位Go包而编译失败，未执行guest；修复只恢复Step22实际source_hashes绑定的6个原Go文件。
- native6.0.1 SHA `{env['settings']['native_sha']}`；实际动态加载路径audit/ldd.txt；未编译或修改runtime。精确native构建源码映射仍未认证。
- 原dCompile/opcode/fn Gas映射原字节与Step22相同，max_pages512，原module metering初始1e19、runtimeGasLimit2^31−1。E23不是Gas规则开关。
- 固定三个原WASM SHA在inputs/manifest.json，GetGas槽在inputs/gas-slots.json。source与noData/template hash及Module缓存key在MODULES/preparation.csv，每进程六Module仅准备一次，实际使用三个，不逐子调用编译。
- inputs/business.json冻结root TxID、参数、初始/最终ledger hash和init顺序。BlockVersion1、ETHEREUM地址、固定公开P256公钥与逻辑member、内存账本/真实TxSimContext；不是生产ACL/节点共识验证。
- 原来WASM的精确SDK/compiler构建来源未重新认证；本轮没有重编译或改SDK，A0/A1使用完全相同逻辑source artifact，C1仅按既有方案移除active data。
- 五生命周期块：R0→R1、R1→R0、R0→R1、R1→R0、R0→R1；每条件独立进程1根。五Copy块同样交替R1/C1。每模式probe off/on各一个预检。共26进程、有效260含init Invoke，另保留受影响v1的260调用，非100次/轮，更非TPS实验。
- 上限MemoryMax2GiB/RSS软1536MiB，TasksMax256/线程软220，Go45秒/进程60秒，全机available8GiB/swapUsed1GiB；未提高。合并峰值{v['peak_rss_mib']:.2f}MiB/{v['peak_threads']}线程。所有进程退出、owner最终登记0、WSL boot ID未变。
- 完整原始执行命令、环境、binary SHA在每个raw_logs/*-command.json；有效v2构建命令在audit/build03-command.json（v1 build02另保留）。scope、Store与Module实际ID在CALLS及原事件中。每进程本地单调时钟只用于事件排序，不跨进程相减；不以诊断时延作性能主张。
'''
(P/'ENVIRONMENT.md').write_text(environment)
index='''# 源码证据索引

本目录source/vm是独立实验副本，行号不可混用生产工作区。v1误用RWMap采样已废弃，最终v2使用透明转发状态观察。

| 文件/函数 | 作用 |
|---|---|
| source/vm/step23_checks_test.go:11 TestStep23BuyNow | 三次真实init+一根实际buyNow；同输入/账本/调用图和业务断言 |
| source/vm/step21d_runtime_test.go:226 dRuntime.Invoke | 保留原SetGas、CallMethod、GetGas、结算；增加逐call标识及只读观察 |
| source/vm/step23_probe.go:50 eRawGas | 固定hash/slot、地址边界、只读registry Remain |
| source/vm/step23_probe.go:70 eGas | 当前调用各已采样host/业务边界 |
| source/vm/step23_probe.go:80 eVerifyGas | 与原真正Getter返回核对，不新增guest Getter |
| source/vm/step23_diagnostics.go:60 a23RW | 只序列化自身状态操作前缀，不访问内部事务映射 |
| source/vm/step23_diagnostics.go:70 a23Enter | caller/深度/序号/参数及状态入口 |
| source/vm/step23_diagnostics.go:95 a23BeforeSet | 记录旧计数并标明非本次计费，不转换越限初值 |
| source/vm/step23_diagnostics.go:133 a23Bridge | 原WACSI/SetGas周围的父子Gas传播观察 |
| source/vm/step23_diagnostics.go:153 a23Finish | 返回值/Gas/事件/状态操作结果，无已销毁memory读取 |
| source/vm/vm_bridge.go:178 | 原syscall前后观察；日志边界85/110 |
| source/vm/vm_bridge.go:393 callContractCore | 原跨调用Getter、WACSI与SetGas，未变其算法 |
| source/vm/step22_runtime_test.go:79 e22Prepare | 一次模板+两变体Module/Store准备及缓存 |
| source/vm/step22_runtime_test.go:122 makeE22 | 新WASI/Instance、A1恢复后才进入_start，原Memory页数 |
| source/vm/step22_runtime_test.go:216 closeE22 | 同owner scope显式销毁、原Fresh基线及新增own-scope严格计数 |
| source/vm/step22_static_test.go:85 prepareStaticMemory | 原active data按顺序叠加，移除Data section、合并copy ranges |
| source/vm/step22_static_test.go:235 restore | 原Host区间copy，Module指针/config/key检查，无Data重复初始化 |
| source/vm/wasmer-go/managed.go:151 ManagedLiveCount | 只读自身scope live登记数；旧owner/in-flight/native守卫保留 |
| source/vm/step21d_compile.go:11 dCompile | 原Gas映射与Validate/Compile，逐字节相同 |

外部运行依赖来自固定Step21C工作树，原文件已冻结在audit/runtime_reference：tx_sim_context.go:709 GetTxRWSet会释放迭代器；:864 GetTxRWMapByContractName会写内部映射（最终v2不使用）；:934 CallContract真实进入VmManager。wasi.go:525 WacsiImpl.CallContract；:583加原基础费；:600前后真实调用与累计返回合并；:543非isLen只读结果缓存。vm_interface.go:28基础费常量100000。原vm_factory.go也已冻结，未改其边界。

source.diff相对Step22实际执行源（不仅Git快照），包含探针移植、R0 scope登记适配和新诊断。差异列表见audit/source_changes.json；Step22忽略掉的6个占位Go文件按旧hash恢复并在本轮提交。所有有效v2 guest源hash与build03一致已核对。
'''
for relative,name in [('step23_checks_test.go','TestStep23BuyNow'),('step21d_runtime_test.go','dRuntime.Invoke'),('step23_probe.go','eRawGas'),('step23_probe.go','eGas'),('step23_probe.go','eVerifyGas'),('step23_diagnostics.go','a23RW'),('step23_diagnostics.go','a23Enter'),('step23_diagnostics.go','a23BeforeSet'),('step23_diagnostics.go','a23Bridge'),('step23_diagnostics.go','a23Finish')]:
    token='func '+name if name!='dRuntime.Invoke'else'func (r *dRuntime) Invoke'
    f=P/'source/vm'/relative
    number=next(i for i,s in enumerate(f.read_text().splitlines(),1)if s.startswith(token+'('))
    path='source/vm/'+relative
    index=re.sub(re.escape(path)+r':\d+ '+re.escape(name),f'{path}:{number} {name}',index)
index+='\n最终状态观察源source/vm/step23_state_observer.go：Get/Put/Del只委托原接口一次，复制输入/返回到自身记录；无额外ctx.Get、无RWMap/GetTxRWSet调用。state_observation_before/after是观察器业务操作前缀，不是内部map；完整callee框架RWSet明确not_tested。读写合并函数副作用证据在audit/runtime_reference/sim_context_rwset_cache.go:36/46。v1全部标记affected，最终仅v2。\n'
(P/'SOURCE_INDEX.md').write_text(index)
print('rendered reports from actual five-block evidence, no new execution')
