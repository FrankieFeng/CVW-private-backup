# Step-19：找回VM日志统计代码并纠正历史指标对齐

2026-10-20。本轮只读检索源码/历史日志，对已有Step-19时间戳重新统计，没有启动节点、发送交易或编译；没有修改vm_factory计时边界或引入Copy/A/P。

**后续用户确认：按合理理解统一计算，不必等待PPT公式。现采用N/ΣInvoke耗时作为本轮协议，完整规则见METRIC.md。下文关于历史入口未知的说明仅作为溯源限制，不再是计算或后续推进的前置条件；并发安全门槛仍保留。**

## 1. 本次纠正

用户已向王浅秋确认历史PPT指标来自vm_factory的Invoke执行时间日志。此前将实际成功提交TPS作为唯一主对照不符合该研究指标；此前“没有找到日志统计代码”的结论也不完整：漏查了`chainmaker-test-toolkit-master/chainmaker-performance-test`。现已找到解析/计算代码和部分历史原始日志。

**已确认本地代码公式；尚未确认给定9月PPT每一行使用的确切脚本版本和入口。** 此目录没有Git元数据，不能虚构commit或把当前文件mtime当历史运行版本。代码SHA和原始文件路径保存在provenance.json。

## 2. 找到两个不同入口，不能合称一种公式

文件：`/home/frankie/mygitprojects/chainmaker-test-toolkit-master/chainmaker-performance-test/parallel/parallel_claim.go`。

### 顺序入口 normalTPSTest

730行定义函数，764行读取各节点日志，794–795行累加节点条数及总执行时间，805–809行实际计算：

```
N = sum_over_nodes(number of selected VM log records)
T_sum = sum_over_nodes(sum(endTime - startTime)) / 1e9
VM_log_TPS_sum = N / T_sum
```

这是平均Invoke时长的倒数（样本选择一致时），不是Median的倒数，也不是逐条倒数后平均。它忽略两次Invoke窗口之间的空闲，不能解释为成功提交吞吐。

### 并发入口 ClaimTPSCTPSWithSub

553行定义，646行使用同一解析器，678–679行累加条数/总时间，但最终693–697行使用：

```
VM_log_event_rate_span = sum_over_nodes(N_node) /
    ((max_over_nodes(endTime) - min_over_nodes(startTime)) / 1e9)
```

该入口虽收集totalExecutionTime，却没有用它作为最终分母。它包含首尾之间的空闲；四节点同一交易执行事件会分别计数，也未做唯一TxID提交去重。

`parallel/process_pressure.go:37–40`按ThreadNum>0选择并发入口，否则选择顺序入口；`parallel/Init.go:293`还先按客户端数整除配置thread_num。当前const_config.yml为compute.normalCal、loop_num10、sleep_time10、thread_num4，**不是已证实的历史1000笔配置**。`ClaimPressureTest:828`中的sleep是可配置参数，历史是否为0不能从当前文件推断。

因此“来自VM日志”仍不足以确定两个公式中的哪一个。已经发出对确切公式/入口及过滤规则的补充确认请求；在答复或PPT对应原始产物到位前，以下结果明确标记为**按找回的顺序入口公式计算**，不宣称已逐项复现PPT口径。

## 3. 原始解析规则和局限

`getLastTimestamp`（133–216行）是两个现用入口调用的版本：

- 160行硬编码匹配`vm_factory.go:438`，不是按函数名自动定位。
- 165–167行无条件跳过每份文件的第一条匹配记录，假定它是安装合约；没有显式按init_contract识别。
- 179行先将每条匹配记录的end-start加入分母，然后184行才筛contract/method；混合方法日志会出现分子/分母样本不一致。
- 失败结果过滤在181–183行被注释，失败调用也可进入分子；列表版本没有TxID去重或批次时间过滤。
- getLastTimestampMap（374行）是另一个版本：固定417行，失败过滤开启、按TxID保留最后一条；但所查两个入口并未调用它。不能混用规则。

后续不应静默修正历史规则：保留原脚本输出供复现，同时另列按明确批次/方法/成功条件筛选的干净指标。若分母受其他方法污染，原样结果应标有局限。

已找到历史log目录下的6–8月汇总和7–9月system.log快照。6月23日汇总明确记录顺序执行、1600条VM记录、总执行时间0.48269665秒、TPS3314.711，而首尾墙钟约222秒；这是本地历史确实使用过耗时总和口径的直接证据。它不是给定9月769.6/277.0等PPT行，不能替代。

9月1日与9月4日三个system.log快照都有compute.normalCal记录；已登记在legacy_log_inventory.csv，**reuse策略、WASM哈希和PPT行对应均未知**，不能将它们自行配成reuse/no_reuse。原工具只复制最后结束节点的日志快照（682–683/798–799行），一份快照不能恢复完整四节点聚合。

## 4. Step-19计时边界核对

原CVW `chainmaker/chainmaker-vm-wasmer/vm/v2@v2.4.0/vm_factory.go:432–437`与实验worktree同路径432–437行逐句相同：

```
startTime := time.Now().UnixNano()
runtimeContractResult, specialTxType := runtimeInstance.Invoke(...)
endTime := time.Now().UnixNano()
executionTime := float64(endTime-startTime) / 1e9
```

Step-19仅在endTime已取得之后增加REUSE_VM输出。boundary_check.csv逐条核对200条保存样本，CSV时长全部与该原始纳秒差完全一致；无取整，均为一个root attempt。

但**记录格式不相同**：原INFO日志在本轮ERROR级别配置下没有输出，保留的是同起止值的REUSE_VM行；新增输出使原INFO调用行号变为439。将旧解析器不加适配直接用于本轮日志会匹配不到，不能把它解释成0 TPS。本轮解析器只适配输入传输字段，不移动计时边界或伪造旧格式原始日志。

窗口包括GetInstance及其可能的等待、SetGas、业务、defer归还/发起异步关闭；不包括先前NewRuntimeInstance/pool预建，也不等待全部异步Close/grow完成。原始区间边界相同，不等于程序无观测开销：Step-19在Invoke内部增加的轻量事件输出没有独立校准。

## 5. 按确认的本地顺序入口公式重算现有样本

以下每格20条，显式排除部署和3次预热；是公式级应用于已定义样本集，**不是原脚本对混合整份日志的原样输出**。原样筛选的适配重放另见literal_selection_replay.csv，其中保留分母包含其他方法的局限。

| 方法 | 历史PPT R0/R1（用户参考） | Step-19 R0 | Step-19 R1 | 本轮指标下降 |
|---|---|---:|---:|---:|
| compute.normalCal | 408.7 / 264.3 | 未采集 | 未采集 | 缺失 |
| compute.bigNumCal | 295.8 / 210.4 | 2744.48 | 2643.12 | 3.69% |
| compute.hashCal | 769.6 / 277.0 | 3308.11 | 2902.20 | 12.27% |
| erc721.mint | 4077.5 / 311.4 | 1908.10 | 1416.27 | 25.78% |
| fact.saveAndFindByFileHash | 2959.1 / 380.3 | 2368.38 | 1758.42 | 25.75% |
| exchange.buyNow | 881.2 / 57.7 | 未采集 | 未采集 | 缺失 |

本轮是N/Σ耗时指标，不是提交TPS，也不是此前Median倒数。fact的R0 Gas有18/20组从1707降为1113，R1为1707；该行不能作为语义等价性能认证。

同一组20条记录若换成并发入口首尾跨度公式，所有方法仅约7.9–8.2事件/秒，受100ms间隔及客户端等待主导。这证明公式入口必须核实，不能任选一种去解释PPT。

## 6. 为什么历史倍数差距与本轮小差距可以同时出现

已证实：本轮预建库存5，借出后仍有4个；零空池等待；R1单次替补约4.75–4.87ms，下一请求约100ms后才来。执行成本在后台，不完整进入Invoke，因此无论看Mean或Median，两组差距都可能较小。

合理但未验证的历史解释：高压下实际VM attempts的需求超过补池供给，GetInstance阻塞进入同一个Invoke窗口；后台创建/关闭争用CPU、内存、Store资源，也可增加窗口内耗时。即便公式是N/Σ，它仍会把这些等待和争用计入平均执行时间，因此可能出现很大差距。仅“关闭复用”不保证每条Invoke同步加上完整创建成本，差距取决于当时库存和压力。

尚未证实：历史PPT大差距主要由补池不足造成。历史队列等待、创建利用率、close/control积压、重复执行、资源状态及完整脚本入口未对齐；不能只因数字接近某个创建耗时就指定原因。

其他差异：本轮单验证节点/单同步客户端/100ms间隔/20条，历史参考为四节点较大批量；历史并发参数、发送模式、原始WASM SHA与fixture未知。本轮使用Step-16保存的compute WASM，bigNumCal为100轮，不能从当前源码10000轮反推历史产物；normalCal没有采样，不能用bigNumCal替代。ERC721和fact输入固定且逐笔唯一key，历史同类参数未知。当前环境有WASI freelist，历史是否相同未知；RSS/VA短批次持续增长，线程短时稳定，历史资源状态不能倒推。

## 7. 后续负载对照：目标已纠正，执行仍受安全门槛约束

主指标改为经PPT入口确认的VM日志指标，固定原vm_factory起止位置；同时报告另一个入口公式以暴露口径差异，实际成功提交TPS作为辅助，不再作为唯一主对照。

准备reuse/no_reuse两组同WASM/SHA/输入/节点配置/负载、四节点隔离账本，先短时无100ms间隔加压，记录每个节点完整VM事件及pool acquire等待、enqueue、create/close、root attempts、资源与Gas。部署/init/预热明确排除；并行保留原解析规则和按批次筛选规则，四节点按同样方式合并；交换顺序并独立批次。短批通过后再扩大每节点1000笔。

本轮没有执行，因为前置审计已在实际so发现Store引用非原子增减/对象容器修改与Go异步close/create缺少统一同步，资源回收仍未通过。主指标变更不消除这一安全条件。不使用根VM串行保护、同步fresh或更改计时边界强行得到数字；也没有新增优化。安全修复完成并披露其差异前，只推进日志审计。

还需确认：PPT使用normalTPSTest还是并发入口/其他版本，是否按成功过滤、每节点首条如何跳过、完整四节点原始日志/脚本版本及WASM输入。已找到的代码能支持本目录重算，不能替代缺失的PPT版本溯源。

## 交付与复核

`python3 -B analyze_existing.py`只重算已保存日志。输出vm_log_summary.csv、historical_comparison.csv、boundary_check.csv、literal_selection_replay.csv、legacy_log_inventory.csv、provenance.json。原日志、原samples、运行时和旧报告未覆盖。本报告补充并纠正此前对“日志计算工具未找到”的判断。
