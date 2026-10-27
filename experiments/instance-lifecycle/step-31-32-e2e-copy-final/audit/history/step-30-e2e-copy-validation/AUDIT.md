# Step-30：历史E2E与新实验准入审计

本文件先于任何Step30节点/客户端执行形成。本轮截至本审计只读源码、配置、已有日志；没有编译、启动节点、发送RPC或提高任何阈值。分支experiment/step30-e2e-copy-validation，父f1609b80。

## 执行范围决定

**新E2E smoke/正式采样暂不准入，G0/G1/G2均blocked。** 已找到保存的Step17/20节点与客户端，但它们没有接入Step21B之后要求的Store所有者/Finalizer回收协议；Step22/28/29的安全副本仅为有界Go测试夹具，不是可以直接替换进真实节点的已验证实现。将该协议临时搬入节点需要新的运行时集成与验证，本轮明确不临时重写运行时。因此本轮先完成可复核审计和历史原始数据复算，新增样本数0，不用旧样本冒充新三批。资源中止不是通过抬高限额或重启轮换继续采样来绕开。

## 实际资料与版本

用户所列旧路径`e20-e2e-copy-attribution/`未找到；实际目录为`CVW/experiments/instance-lifecycle/step-20-e2e-performance-attribution/`，NAMING.md记录更名。分支experiment/step20-e2e-performance-attribution、HEAD668ecb4a；Step17分支HEADb21ca6af。Step28提交29950ab与Step29 f1609b80均存在，三项正式结果/原始CSV/脚本可读取。Step20原始low-a/low-smoke客户端JSONL、四个node stdout、资源JSONL、状态、pending请求及binary均存在。精选原件逐字拷贝到raw_logs/historical-step20，来源/哈希见audit/HISTORICAL_MANIFEST.json；不复制密钥、证书或账本。

Step20没有完成三批：smoke3完整热对；low-a计划100对实际88完整热对+1条Copy未配对响应，另1个job已写管道但SDK开始/TxID/提交未知，22计划请求未发出。两次含cold/warmup合计207已保存响应；low-b/c、详细trace、默认池R1/R2及并发没有运行。失败/超时未观察到，不把pending或未发出请求算成功。

## 客户端真实边界和提交语义

`step-17-real-node/prototype/client-benchmark.go:17–24`：先构造业务kv；begin=time.Now → SDK-Go/v2 v2.4.0 `InvokeContract(contract,method,"",kv,60,true)` → 返回后time.Since(begin)。包含SDK组包/签名、RPC与同步结果等待，不含SDK构造/Python启动，也不等于driver发送管道到收到JSON的总窗。原客户端没有记录SDK内部begin/end绝对时间，仅elapsed；driver_send/receive只作为外层窗，不能冒名为SDK请求边界。

冻结SDK sdk_client.go:674–700：轮询仅在syncResult且nodeOnlyAsync=true等条件成立；配置未启用node_only_async（默认false），实际进入sendRequestSync。配置retry_limit100/retry_interval5不是本路径已证实的5ms轮询。SDK遇gRPC Unavailable可切换地址重试，但每链只有一个地址；raw没有每次transport attempt明细，不能断言绝无内部重试。

节点`.worktrees/node-step17/module/rpcserver/api_service.go:588–650`：先dispatcher.Register，再AddTx，随后等待txResultC/ctx timeout；成功返回ContractResult/TxBlockHeight。故该配置不是AddTx ACK边界，而是节点报告提交结果的同步RPC响应。能称“客户端等待节点提交结果的E2E延迟”，不能称独立验证全网最终性或精确PutBlock持久化完成时间。仍须区分同步响应的提交证据与独立账本确认/提交统计窗口，后者本次日志未充分提供。

## Step20固定条件

- 实际方法compute.bigNumCal，参数{}；逻辑WASM SHA `e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507`。这属于Step24B原件家族（bigNum100循环），不是Step18家族10000循环。G0/G1同一WASM，Copy执行另生成noData；G2同源A未可靠恢复，不能混用Step18 A变体。
- 同一个保存节点binary：`ba5cbd3b956fb24f10ac0e73aec1a21a17998709c4977cd5db7cd316141cc2b0`；客户端`8c54eab4ca354d21ddbf0129909f10cc366e1143a02266b6f6417a7f7ebafd2f`；native `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。实际文件存在性与流式SHA复核另存audit/environment-check.json；不能以文档哈希代替文件校验。
- node源351b816、CVW源快照202b666/Step17最终b21ca6a（带已有工作区patch）；详细版另为node2b1ddb17、CVWa47ae2f，不用于本次low性能。Go1.25.0、ChainMaker/SDK2.4.0。完整显式实验env见原*-command.json；未全量归档父进程环境，不声称每个系统变量相同。
- 两个独立单验证节点TBFT测试链，链ID step17、20ms出块、空seeds；RPC127.0.0.1:27801/27802、P2P127.0.0.1:28801/28802，账本为旧已停机baseline独立复制，非生产拓扑。实验请求不得转向目前其他监听端口或既有四节点。
- G0/G1皆CM_FRESH_INVOKE=1、CM_STEP17_SERIALIZE_VM=1、CM_STEP17_OBSERVE=1、GOMAXPROCS4；Copy开关0/1，CM_STEP16_SERIALIZED_MODULE置空，共享相同经校验编译artifact目录。同步fresh不启动后台grow，已执行Instance同步Close不回池。根锁并非Store安全证据。
- 单客户端顺序闭环，每请求等响应后才发下一请求，无100ms业务Sleep；每对随机先后。每endpoint每次重启1次cold+5次warmup；热样本全部保留，cold/warmup分别标记而不是从历史文件删除。SDK timeout60s/node sync timeout60s，外部客户端watchdog15s，node runtime上限120s/停止5s。

## RSS停止及资源门槛

原始low-a-status.json为RSS soft limit，low-a-resources.jsonl可复核Copy采样峰2564.707MiB、Baseline2558.711MiB。两组首个热窗分别1575.414/1572.469MiB，均增长约1GiB，不能单凭增长归因Copy模板。线程峰27，两组仅一个compute模板，未发现热调用反复生成模板。node RSS不是Go heap；旧数据未采集Go heap，必须标missing。

阈值固定：每节点MemoryMax3GiB、RSS软限2560MiB、TasksMax256、线程软限220、RuntimeMax120s、watchdog15s；不可抬限。新目标3×20对尚未启动，不能将旧3对smoke认作本轮smoke。未知资源所有权及安全协议未补齐前，也不通过“每若干请求重启”绕开内存增长结论。

## 安全边界的源码证据

旧实际节点源码与原型：runtime.go:50–57的invokeMu只包根Invoke；模板/Module/池准备在NewRuntimeInstance，发生于锁之前。vm_pool.go:1052创建单合约Store，后续Fresh复用此Store；:638–645同步NewInstance，:685–688同步Close；:713–734 CloseInstance显式关闭Instance并把WASI放freelist，不构成所有native wrapper的owner/join协议。

绑定仍注册native Finalizer：wasmer-go/store.go:33、exports.go:24、function.go:51、memory.go:26、wasi.go:285。它们不经过invokeMu，native析构可能在Go Finalizer goroutine执行；逐次Close Instance并不能证明所有导出/import/metadata析构都在同一Store所有者上。error.go:42的LockOSThread仅围绕一个C调用/last-error读取，不是整个Store生命期固定owner。该结论是未满足安全证明，不是声称本轮已经复现native race/崩溃。

Step21B CONCURRENCY_CONTRACT已不放行无同步Store创建/执行/关闭重叠。Step22/28/29以ManagedScope强引用抑制native Finalizer、固定OS owner、严格串行、同步清理并最终退出进程；每Store与WASI数量受限。已检查可恢复的node-step17/node-step19/node-step19-reuse go.mod依赖及对应VM绑定，没有找到已经集成此协议的节点binary/源码。仅单客户端仍不能排除Finalizer重叠或节点内重执行。不能降低这一门槛来完成新E2E。

## 克隆窗口适用性

Step29定位的是`source/vm/step21d_fixture_test.go:79`测试夹具`append([]byte(nil),b...)`，在根export内六次获取下游字节码。Step17/20节点不使用这个Go测试Snapshot夹具，且Step20只测无跨合约compute.bigNumCal；不能把Step29约28MiB六次clone套到Step20。实际节点ctx.GetContractBytecode→BlockchainStore取码在根/子调用准备中，可能位于客户端总窗内、VM计时之前，但现有low日志无独立clone耗时；标missing。各旧组相同加载路径，不改clone、不研究其GC机制。

Step29 fine trace有可见观测影响，不能搬入本轮主E2E。Step28/29串行测试明确不包括SDK/RPC/提交，不能以其Invoke收益代替客户端结果。

## 王浅秋历史指标

实际恢复`parallel_claim.go:134 getLastTimestamp`匹配vm_factory.go:438，跳过首条匹配日志；:179在合约/方法过滤前累加end-start，:184–187成功过滤被注释，:188只筛方法/合约，返回切片不按TxID去重。normalTPSTest:806–809取各节点条数合计/各日志耗时合计；并发入口:694–697用条数/(maxEnd-minStart)。map版:374以后另用vm_factory.go:417、按TxID覆盖且过滤成功，但分母仍在筛选前累加，不能混同。

因此历史PPT究竟调用哪一入口/哪些过滤尚未完全证实。可说明已恢复顺序“VM日志等效速率”N/ΣInvokeDuration及并发日志窗口速率两种实现，不能承诺历史具体数字已同口径。Step17 STEP17.invoke_ns还位于根锁之后，而vm_factory timer包runtime.Invoke外层（含根锁等待）；前者不能直接冒称王浅秋原计时。当前不采伪TPS，不把VM时间倒数当节点TPS。

## 数据重用和缺口

可复用旧Step20原始207响应、VM逐TxID事件、资源、停止和旧详细trace归因；本轮离线重算并明确origin_step=20。未测：新Step30客户端延迟/60对/三批、G2 E2E、逐笔SDK begin/end绝对时刻、独立账本确认时间/提交窗口TPS、Go heap、原版独立NewInstance/_start/CallMethod、当前节点clone耗时。旧S1含NewInstance+Copy，S2-S1为WASI+_start合计，不改名纯_start。旧AddTx→VM证据来自另外2026-10-19详细批次，不能拿来填Step20低日志或Step30的缺失值。

补充边界：未在本轮新启动节点，因此没有“本轮复现race、RSS超限或必然崩溃”的结论。旧RSS增长不证明20对必然超限；当前阻止smoke的首要条件是节点native生命周期所有权未准入，缩小样本本身不能补足该协议。四轮历史文件实际存在性/哈希与两个基线commit另由prerequisite-files.json和git cat-file复核。

### 本地提交到同步响应的补充调用链核验

继续沿实际源码追踪，而非按dispatcher名称推断：`module/core/common/committer.go:60`先执行store.PutBlock，失败panic；block_helper.go:1059等待CommitBlock返回，:1087发布BlockInfo。subscriber/subscriber.go:23–25将该消息转NewBlockEvent，rpcserver/tx_result_dispatcher.go:265–275遍历块内交易，:320–333按已注册TxID发送tx.Result与blockHeight；api_service.go:629接收后返回SDK。因此当前配置下成功同步响应确实在本节点PutBlock返回之后。它不能提供独立持久化/全网最终性验证或精确提交时间戳。

缺失“独立提交事件窗口TPS”不等于提交语义未知：207响应有本节点提交结果证据。客户端观察窗内这些已确认交易的响应速率可以计算；但本报告不把它冒充按PutBlock事件时间窗统计的独立节点吞吐，也不把未知pending当未提交。新增链路源码快照列入environment-check.json/evidence。
