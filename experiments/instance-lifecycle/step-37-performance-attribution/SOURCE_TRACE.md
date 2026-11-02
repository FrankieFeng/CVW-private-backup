# 真实调用链与证据路径

证据等级：A=源码与对应观测直接证明；B=数据支持、机制不唯一；C=源码推测待测；D=研究假设。源码索引/hash见audit/SOURCE_INDEX.csv。下面路径别名均是**本机实际文件目录**，不代表新编译版本：

- `V`=/home/frankie/mygitprojects/.worktrees/cvw-step36/experiments/instance-lifecycle/step-36-e2e-copy-acopy/source/vm
- `N`=/home/frankie/mygitprojects/.worktrees/node-step36
- `F`=/home/frankie/mygitprojects/.worktrees/cvw-step21c/chainmaker/chainmaker-vm-wasmer/vm/v2@v2.4.0/vm_factory.go（node buildinfo实际local replace）
- `R`=/home/frankie/mygitprojects/.worktrees/native-step35b（24b6afd798cafb01d86d1e2d5d5a7ccb0cc503fe，实际Selector补丁源码）
- `G`=/usr/local/go-version/go1.24.1/src/runtime（Guest；host二进制为Go1.25.0）
- `S36`=/home/frankie/mygitprojects/.worktrees/cvw-step36/experiments/instance-lifecycle/step-36-e2e-copy-acopy

## SDK至VM和提交

| 次序 | 文件/函数/行 | 实际行为 | 等级 |
|---|---|---|---|
| 1 | S36/source/client.go:63/69/87/89，serial loop | 已在窗口前准备参数/TxID，SDK InvokeContract(timeout60,true)前后time.Now，Sub保留单调时钟 | A |
| 2 | /home/frankie/go/pkg/mod/chainmaker.org/chainmaker/sdk-go/v2@v2.4.0/sdk_user_contract.go:168 InvokeContract；sdk_client.go:666；conn_pool.go:117 | 同步SendRequestSync，不是仅发异步ACK | A |
| 3 | N/module/rpcserver/api_service.go:147 SendRequestSync，:596 dealTransact，:606 Register，:617 AddTx，:643 select | 注册TxID后投递交易，等待提交结果通道 | A |
| 4 | N/module/core/common/scheduler/run_vm.go:169 runVM2300、:258 RunContract（按区块版本选相应入口） | 调度与合约/字节码准备；具体交易版本以实际记录为准，不能仅凭文件断言每笔走2300 | A/C |
| 5 | F:393 NewRuntimeInstance，:432开始，:433 RuntimeInstance.Invoke，:436结束 | runtime对象建立在外层Invoke计时之前；原日志使用UnixNano墙钟 | A |
| 6 | V/vm_instances_manager.go:56 NewRuntimeInstance，:67 safe.runtime | **安全Fresh分支绕过旧getVmPool/GetInstance/grow**。不能把Step36当旧池等待实验 | A |
| 7 | V/step35_node.go:90 runtime，:94 append(raw...) | 每runtime对象私有WASM副本，在外层Invoke之前。源码证明复制存在，未独立打点 | A/C |
| 8 | V/step35_node.go:181 Invoke，:184校验，:190 owner.Do | 比较nodeSHA(raw)、nodeSHA(r.raw)，排队进入Owner | A |
| 9 | V/step34_owner.go:58 loop，:59 LockOSThread，:105 Do | 单native Owner；同Owner子调用直接执行fn，避免自己排队死锁。安全协议，不是100ms间隔 | A |
| 10 | V/step35_node.go:199 invoke，:204 begin，:223 prepare | Owner内计时开始后查Module缓存 | A |
| 11 | V/step35_node.go:125 prepare，:133 key，:155 prepareStaticMemory，:165 dCompile | key含chain/name/version/原WASM SHA/native-Gas-编译配置/Copy；命中复用Module/模板，不复用Instance | A |
| 12 | V/step21d_compile.go:dCompile（最后60行）；V/wasmer-go/store.go:26 | 缓存项首次创建Engine/编译Store/Module；新Instance使用同Engine的**另一真Store** | A |
| 13 | V/step35_node.go:230 ManagedOpen，:248 NewStore、:249 Finalize、:253 GenerateImportObject、:258 GetImports | 先Store/WASI/Imports，再实例化；不是Copy后才创建WASI | A |
| 14 | V/wasmer-go/instance.go:33 NewInstanceInStore、:48 wasm_instance_new | imports.intoInner(module)，显式传目标store.Inner；并建Exports wrapper | A |
| 15 | V/step35_node.go:263实例化计时、:272 restore、:277 S1 | Copy在native实例化后；NoData模块使原active Data初始化被移除，而非先完整原Data再追加Copy | A |
| 16 | V/step35_node.go:278 Initialize、:286 start.Call、:293 S2 | 模板为_start前静态字节，Go Runtime仍完整启动 | A |
| 17 | V/step35_node.go:303 setGasByExport、:306 NewSimContext、:316 CallMethod | 新业务上下文/Memory/host绑定。V/sim_context.go:136分配、:160写入参数、:188 guest export | A |
| 18 | V/vm_bridge.go:385 WaciInstance.CallContract，:396 wacsi.CallContract | 真正子合约执行再次进入Manager/Owner；buyNow顺序六个子Invoke嵌套于根CallMethod | A |
| 19 | V/step35_node.go:234 deferred cleanup，:236 CallDeallocate、:240 scope.Close，:217 invoke_ns | 同步逆序释放Instance/WASI/import/Store；Module缓存scope长期保留。Close包含在Owner Invoke内 | A |
| 20 | N/module/core/common/committer.go:61 PutBlock → block_helper.go:1087 PublishSafe(BlockInfo) | Common写入结束后公布区块结果；不是vm返回即同步SDK成功 | A |
| 21 | N/module/rpcserver/tx_result_dispatcher.go:264 start、:274、:320 trySendTxResult | 按TxID通知SDK等待者，携带高度与结果 | A |
| 22 | S36/scripts/case_run.py:21 committed，:25查询，:27 CR匹配；postcheck.py:5 | 窗口外查询RWSet/实际状态，batch3账本重启后再核对 | A |

## 计时包含什么

Owner Invoke含prepare命中时的SHA/日志、fresh Store/WASI/import、新实例、Copy、Initialize/_start、Gas/CallMethod/同步关闭；不包含runtime(raw...)复制和进入Owner前的两次整WASM SHA/队列。Factory Invoke包含后两者，但不含runtime对象建立；E2E包含SDK/RPC/调度/字节码读取/全部根执行/PutBlock/通知等。

NewInstance_ns不仅是纯wasm_instance_new，还含imports.intoInner、错误包装、Exports构造；Copy_ns也包含模板身份校验、Memory导出获取、Data视图、循环复制。Store和WASI/import未拆分，不能从相邻嵌套窗口中凭空给各自成本。S1→S2可用同一次s2_ns-s1_ns准确得到；start_ns只包start.Call，二者不同。B5Profile虽然在sim_context.go写入，但安全路径未输出其字段，Step36没有exportFunc.Call独立原始值。

## 生命周期和缓存边界

V/wasmer-go/managed.go:51 managedSetFinalizer、:75 ManagedScope.Close在Owner同步处理；instance.go:154 Close、store.go:62 Close幂等/清native引用。V/step35_node.go:96 clear逆序关闭缓存，:120 reset调用Owner.Reset；Owner:139 Reset、:178 Stop按既有协议排空。Step37未运行任何生命周期测试，也未把35C已有验证扩大成所有并发场景安全。

## 为什么有些TxID有两次根执行（A/B/C）

A：原始日志精确计数144笔各2次，分别为erc721.accountTokens、itinerary.queryHistory、itinerary.saveAndQueryHistory，每方法48笔；没有把它们去重成一次VM时间。

A：冻结Guest源码`audit/frozen_guest_source/erc721-erc721.go:1191`使用NewIteratorPrefixWithKeyField；`itinerary-itinerary.go:257/:430`使用NewHistoryKvIterForKey。host `V/vm_bridge.go:317/:320/:333`把这些调用标记ExecOrderTxTypeIterator。节点`N/module/snapshot/snapshot_impl.go:427`在首轮applySpecialTx=false时加入specialTxTable，`N/module/core/common/scheduler/scheduler.go:181/240`处理special队列，`:779 simulateSpecialTxs`、`:798`再次executeTx、`:801`以applySpecialTx=true应用结果。

B/C：这是与三类方法精确对应的源码重执行机制，且与观测两次吻合；每笔日志未独立保存specialTxType或调度原因码，不能把所有两次执行不加限定地归因于这唯一原因，更不能声称因跨线程资源竞争重试。将来只需补调度原因/attempt ID即可确认，无需重跑全矩阵。

```mermaid
flowchart LR
  SDK[SDK同步Invoke] --> RPC[注册TxID并AddTx]
  RPC --> Schedule[调度 / special重执行]
  Schedule --> Manager[NewRuntimeInstance 私有bytecode]
  Manager --> Owner[Owner 验证与Module缓存]
  Owner --> Fresh[独立Store / WASI / Imports / NewInstance]
  Fresh --> Copy[可选NoData模板restore]
  Copy --> Run[_start / CallMethod / 子调用]
  Run --> Close[同步Close]
  Close --> Commit[PutBlock / BlockInfo]
  Commit --> Return[TxID通知 / SDK返回]
```
