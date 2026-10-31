from pathlib import Path
import json,csv,subprocess,hashlib
P=Path(__file__).resolve().parents[1];R=Path('/home/frankie/mygitprojects');V=P/'source/vm'
def put(n,s):(P/n).write_text(s.strip()+'\n')
def line(f,pattern):return next(i for i,s in enumerate((V/f).read_text().splitlines(),1)if pattern in s)
def ref(f,p):return f'source/vm/{f}:{line(f,p)}'
entry=ref('vm_instances_manager.go','func (m *InstancesManager) NewRuntimeInstance');prep=ref('step35_node.go','func (m *nodeFreshManager) prepare');invoke=ref('step35_node.go','func (r *nodeFreshRuntime) Invoke');inner=ref('step35_node.go','func (r *nodeFreshRuntime) invoke');stop=ref('vm_instances_manager.go','func (m *InstancesManager) StopVM');reset=ref('step35_node.go','func (m *nodeFreshManager) reset')
put('README.md',f'''# Step-35：真实节点 Fresh 生命周期接入与 Smoke Test

**已实现并实测真实节点接入；E2E 安全准入暂不签发。** 阻塞收敛为资源问题：六轮请求后 C API 句柄配平，但 RSS/线程尚未证实收敛。没有启动正式性能对照。

基线 Step-34 `9845db9841bc963634c8f7d28d644e8756d5ac22`；工作树 `/home/frankie/mygitprojects/.worktrees/cvw-step35`，分支 `experiment/step35-node-fresh-integration`。节点工作树 `/home/frankie/mygitprojects/.worktrees/node-step35`，节点适配提交 `4dd3ae3`（父 `351b816e`）。本目录 source/vm 是实际编入节点的非测试 VM，实现入口 {entry}。

已验证：五合约真实部署/初始化，compute.bigNumCal、fact.saveAndFindByFileHash、erc721.mint、exchange.buyNow 真实交易；buyNow 完整六次下游；Module 命中；独立 runtime Store；同步关闭；节点正常关闭/同账本重启；重复 buyNow 失败零写集；真实在途 Stop。Baseline/Copy 独立账本的 Gas、结果、业务读写集、事件和最终业务账本一致（限定元数据归一化，见 CORRECTNESS.md）。

| 记录 | 业务/生命周期 | RSS 峰值 MiB | 线程峰值 | Store CAPI创建/关闭 | Instance CAPI创建/关闭 |
|---|---|---:|---:|---:|---:|
| 原继承配置 | 五部署后触发资源停止 | 1548.410 | 33 | 11/11 | 6/6 |
| 小账本 Baseline | 四业务+查询+重复失败 | 1236.250 | 65 | 27/27 | 22/22 |
| 同账本重启 | 两轮四业务+检查 | 1134.012 | 55 | 34/34 | 29/29 |
| 小账本 Copy | 同 Baseline 业务序列 | 1289.879 | 65 | 27/27 | 22/22 |
| 真实在途 Stop | 进入 VM 后 SIGTERM | 665.047 | 26 | 2/2 | 1/1 |
| 六轮有限请求 | 24笔目标业务+检查 | 1481.109 | 109 | 72/72 | 67/67 |

这是功能 Smoke Test；表中不是性能基准，批次规模、冷热和代码诊断版本不同，不计算 Copy 时延收益。

原继承配置启用 `keys_capacity=1e9` Bloom，按源码分配约1.116GiB位图。触发1536MiB软阈值后立即保留并停止；另建空账本，仅把 Bloom 容量改为1e5，仍启用、同误判率，未提高资源限制。原配置、账本及失败数据不覆盖。小账本减少了大块基础内存，不证明其他资源增长已解决。

六轮末：Go heap 从930.9MiB附近降至521.6MiB，NumGC从8增至9；RSS仍约1473MiB、线程未呈稳定平台。CAPI计数不是Rust最终Drop或物理内存释放计数。**不能凭句柄配平或正常退出宣称长生命周期资源安全。**

运行/复算见 scripts/、SMOKE_TEST.md。Node6为最终编译产物；实际节点日志分别关联node2/node4/node5（命令JSON保存精确SHA）；node6仅增加缺失opt-in时拒绝旧池的准入分支，正常opt-in路径不变。所有二进制保留在本地 binaries/ 并记录哈希，不入Git。测试网络配置/测试凭据在 `/tmp/cvw-step35-*`，不打包私钥。

回滚：停止本实验unit并检查PID/cgroup为空，恢复原节点二进制、库路径和原测试配置。**不能**在本实验 managed 绑定二进制里只关 `CM_SAFE_FRESH_NODE` 再走旧后台池：该组合现在直接拒绝启动。关闭Copy仅设 `CM_STATIC_MEMORY_COPY=0`，仍为安全Fresh路径。未改生产代码、原CVW已有修改及历史实验；不推送远程。
''')
put('NODE_CALLCHAIN.md',f'''# 真实节点调用链

```text
Blockchain.initVM
  -> NewInstancesManager(chain) [source/vm/vm_instances_manager.go]
  -> StartVM [检查缺失opt-in/config/R1/唯一Owner的初始化错误]
Scheduler.runVM -> VmManagerImpl.RunContract
  -> invokeUserContractByRuntime -> NewRuntimeInstance [{entry}]
  -> nodeFreshRuntime.Invoke [{invoke}]
  -> Step34 SafeFreshOwner.Do
       -> nodeFreshManager.prepare [{prep}]
       -> 独立Store -> WASI+host imports -> NewInstanceInStore
       -> 可选restore -> WASI.Initialize -> _start
       -> SetGas -> SimContext.CallMethod -> GetGas
       -> removeCtxPointer -> CallDeallocate -> scope.Close
  -> 原Scheduler追加RWSet/Event Gas -> 提交/SDK同步响应
```

NewRuntimeInstance仅复制/冻结合约标识与原字节码，不在请求goroutine进行native操作。第一次Module编译/模板准备在Owner内、Invoke内发生；单独有prepare_ns。后续命中缓存不重复编译。原节点NewRuntimeInstance的准备计时位置与之不同，冷调用不可直接拿历史VM时延比较。模块编译未包含在每次warm操作中。

旧 `getVmPool -> newVmPool -> grow/GetInstance -> RevertInstance` 不参与opt-in路径；旧源码保留只作参考。无后台补池、WASI freelist或异步Instance关闭。

子调用：SimContext -> WaciInstance.CallContractLen/CallContract (`source/vm/vm_bridge.go`) -> 既有Wacsi.CallContract -> TxSimContext.CallContract -> VmManager.RunContract -> 同一NewRuntimeInstance入口。回调仍在Owner OS线程，Do内联，父实例保持活跃，子实例使用另外的Store/作用域；子关闭后再恢复父scope和Gas上下文。不是用TxDepth判断是否持有Owner。

Gas getter/setter仍使用runtime.go中的既有导出函数，未改Opcode/fnmap。父Guest内的同scope重入只允许Step34已验证的GetGas/SetGas；任意同Store重入仍拒绝。子调用累计Gas不能相加。

Reset/Close接口 -> {reset} -> Owner.Reset，拒绝新根job、排空、关闭缓存、后续重新编译。该最小版合约级Reset也清空整个有限缓存，未实现细粒度回收。Reset从active Owner调用会拒绝，避免等待自己。

节点停止：ChainMakerServer.Stop -> Blockchain.Stop -> VmManager.Stop -> {stop} -> Owner.Stop排空 -> cache scopes -> Owner root -> EndOwner -> 原节点继续Stop store。StopVM不提前返回超时给Blockchain；外部systemd TimeoutStopSec=10s保留整进程硬终止上界，不能安全中断任意native函数。原节点的其他模块停止顺序未重写。

真实在途证据：node-small-inflight-node.log 中invoke_begin -> stop_requested(inflight=1) -> module_prepared -> invoke_end -> cache_closed -> owner_closed -> ChainMaker exit。Stop在编译/创建窗口已开始；未观测到提前释放后使用。
''')
put('INTEGRATION.md',f'''# 实现及版本

实际代码是本目录source/vm（不是只编入go test的另一个假入口）。节点go.mod将vm-wasmer替换到该目录，将core vm替换为Step21C已核查版本；差异仅两条replace，完整node go.mod/go.sum及diff在audit/。节点其余基线为351b816e，适配提交4dd3ae3。

- `vm_instances_manager.go`：NewInstancesManager创建唯一SafeFreshOwner；NewRuntimeInstance分流到非测试adapter；Close/Reset路由到Owner；StartVM传播配置错误；StopVM等待真实排空。
- `step35_node.go`：新增真实节点adapter和缓存，不复制另一套Owner。
- `step35_tid.go`：仅用于沿用Step34 Owner线程识别。
- `step35_static.go`：由Step34 `step22_static_test.go`提升到非测试文件，SHA-256完全相同，见audit/static-template-rename.json。
- `step34_owner.go`、managed绑定、dCompile Gas表、SimContext及Guest与Step34保持；本轮不改native ABI、Gas规则、A实现或Copy算法。
- `step35_node_test.go`：实际InstancesManager接口的串行夹具测试、Reset后重执行、真实错误回滚、Stop等待/幂等、失配准入测试。其底层业务调用使用真实WASM，非模拟子合约返回值。

缓存：chain/name/version/WASM SHA256/config identity/copy开关为Key；不以名称单独索引。config包含已固定native/compiler/Gas/最大页数等身份，本轮runner核对实际so SHA并保存加载maps。缓存最多8项、Owner最多32个外部job/进程，子调用内联不扣另一个外部job。拒绝多链多Owner同时运行；这是有限实验准入原型，不是长驻生产调度器。

Copy：prepareStaticMemory解析最终原WASM生成Image/Ranges/NoData；缓存Module使用NoData；runtime NewInstanceInStore后restore，然后WASI.Initialize/_start。未知/不支持模块记录fallback并用原模块标准初始化。本轮不引入A版本。Copy关闭也保留完全相同Fresh/Owner模型。

每个缓存record保留自己的Config/Engine及compile Store。runtime Store通过wasm_store_new使用该Engine；缓存Module跨该Engine的真正独立Store实例化，沿用Step34验证的ABI；不用wasm_store_clone。不宣称所有合约共享同一个Engine。

准备失败在缓存scope内回滚；实例创建、WASI/start失败在runtime scope内回滚；执行错误保留Code1和既有Gas；显式Close由managed scope幂等执行。完整失败注入属于Step34历史覆盖，本轮新增的实际节点只覆盖成功和业务失败，不把native OOM/析构失败标通过。

后期修正：StopVM取消了会提前返回节点shutdown链的10s上下文，改为等待排空，硬超时交给外部整进程保护；最后增加未opt-in的fail-closed启动拒绝，避免managed绑定落回旧worker路径。每个构建命令、源码哈希、二进制SHA在audit/*outcome.json；node2/4/5实际调用记录分别保留，node6/vm5为最后构建，不混作同版本性能数据。
''')
put('OWNERSHIP.md','''# 所有权与释放协议

| 资源 | 创建/使用者 | 存活范围 | 释放 |
|---|---|---|---|
| SafeFreshOwner及队列 | InstancesManager创建，独立OS线程 | 有限节点进程 | Stop拒绝新job并WaitGroup排空，关闭root，归还owner lease |
| Config/Engine | Owner的缓存record scope | Module缓存期 | 最后一次在途使用结束，逆序Close |
| compile Store及Module | Owner.prepare/dCompile | 相同Key缓存命中 | Reset/Stop同Owner关闭；不由请求goroutine析构 |
| 模板Image/Ranges/NoData | Owner.prepare，只读Go数据 | 同一最终WASM+配置缓存 | 同record释放；不跨二进制复用 |
| runtime Store | 每次invoke中的wasm_store_new | 单次Fresh调用 | Instance/Imports/WASI释放后，scope逆序删除 |
| WASI/imports/host functions | runtime Store所有者线程 | 单次调用 | managed runtime scope逆序Close，host函数登记一起移除 |
| exports/functions/memory | 对应Instance借用；不出Owner | 单次调用/子调用 | wrapper幂等Close；关闭后借用守卫拒绝 |
| 父子Instance | 同Owner线程、不同Store/scope | 父保持active；每个child独立Fresh | child返回并关闭，然后父恢复；最后父关闭 |
| Go TxSimContext/参数/结果 | 既有节点请求/调度器 | Invoke同步返回之前 | Owner不因客户端deadline提前把仍执行的TxContext交还；结果只含Go值 |

Step34 managed强引用登记替代native Go Finalizer，显式Close与scope清理不会重复native析构。没有将Go mutex当成native安全证据；OS线程所有者、Store作用域和不出Owner的借用协议共同约束。没有修改native版本。

StopVM必须在Owner执行/回调/作用域结束之后返回给节点，防止原Blockchain.Stop随后关闭账本资源。无法抢占卡住的native调用时由外部保护终止整个测试进程；这不是任意取消/崩溃恢复的生产证明。

所有计数只统计C API new/delete成功调用。Rc最后一个引用何时Drop、native allocator何时释放物理页、WASI线程/任务是否完全收敛，不能从这些计数单独证明。本轮资源收敛门槛因此保留未通过。
''')
put('SMOKE_TEST.md','''# 执行与结果

6种配置、7个实际InstancesManager夹具进程通过（包含最终compute生命周期回归）：compute(0/1 Copy)、fact(0)、ERC721(0)、exchange(0/1)。每个测试执行真实初始化、目标、等价账本Reset后重执行、missing方法失败、在途Go job Stop等待和重复Stop。fact首次monitor在进程退出时读/proc发生ProcessLookupError，测试原日志PASS但资源峰值标未记录，未重跑覆盖原始结果。准入测试覆盖缺失config、R0和最后缺失opt-in的拒绝（最终日志见admission-final2.log）。

真实节点：1节点TBFT，隔离链step35，RPC 127.0.0.1:27535/P2P 28535；同一测试网络开发凭据，非生产账本。SDK v2.4.0同步响应后另GetTxWithRWSetByTxId确认上链；query不计提交交易。日志Op=rwset为原始提交结果及写集。

- node-baseline-first：漏传继承的CM_STEP21A_POOL，包初始化拒绝，无native执行。
- node-baseline-configured：继承Bloom容量1e9，5笔部署已提交；第一个bigNumCal进入并完成VM，但客户端连接因资源SIGTERM关闭，未认定该业务提交成功。峰值1548.410MiB超过1536MiB软阈值；node exit0、owner配平。
- node-small-baseline：新空账本，仅Bloom容量1e5；5部署+四目标业务+ownerOf两次+重复buyNow失败。所有已取到TxInfo的交易确认，重复失败零写集。
- node-small-restart-converge：同账本正常重启，两轮连续四业务、唯一token3001/3002及3011/3012；4次owner查询和重复失败检查。
- node-small-copy：另一个等价空账本、同小账本配置、Copy=1，重复Baseline完整序列。18条对照检查（含部署RW/业务结果RW及最终业务账本）通过。
- node-small-inflight：同账本重启，观察到真实invoke_begin后SIGTERM；StopVM入口inflight=1，等invoke_end和同步Close后释放缓存；客户端未收到成功响应，不算成功提交。不是人为Sleep或持有业务锁制造等待。
- node-small-six-waves：6轮四目标业务，共24笔成功提交目标交易；owner查询两次和duplicate失败。5个Module准备、62次命中，67次Instance new/delete，72次Store new/delete，停止时pending0。RSS/线程增长尚未证实收敛，停止扩大。

脚本无100ms业务Sleep；25ms资源轮询和RPC启动探测间隔是监控/就绪检测，非请求之间等待。单客户端顺序请求；节点自身共识/调度路径保留，所有Wasmer操作进同一个Owner。不是原池高并发测试。

已执行命令存 raw_logs/*command.json、audit/*command.json。示例（不应在本轮资源门槛未通过时自动续跑）：
```bash
python3 scripts/build.py <新构建名> node
STEP35_HOME=/tmp/cvw-step35-small-ledger python3 scripts/node_smoke.py <新日志标签> repeat 0
python3 scripts/analyze.py
```
setup.py及small_ledger.py拒绝覆盖已有账本。source客户端为Step17同源SDK入口；client编译单独记录。运行时凭据在/tmp，不进入Git。

未执行：正式E2E性能对照、节点级chain-config触发Reset、任意native OOM/析构故障、长期运行、并发Owner/原池、真实Table函数身份、生产崩溃恢复。不得把这些记为通过。
''')
put('CORRECTNESS.md','''# 正确性与Gas

真实节点Baseline/Copy同源Step34/Step18 P0 A0 WASM，输入顺序和业务状态等价，独立初始账本。同一链配置、发送者测试证书、SDK与Gas规则；实际构建哈希见命令JSON。节点不与旧串行实验绝对Gas基线强行合并。

| 目标 | Baseline客户端Gas | Copy客户端Gas | 返回/状态检查 |
|---|---:|---:|---|
| compute.bigNumCal |120135|120135|success bigNumCal: 607723520|
| fact.saveAndFindByFileHash |285|285|fileHash/fileName/time JSON，存证写集与事件一致|
| erc721.mint |412|412|mint success，ownerOf(1001)=from，5条写集一致|
| exchange.buyNow |12620047|12620047|buyNow success，六真实下游，ownerOf(1002)=to，11条写集、3事件一致|
| duplicate buyNow |3004775|3004775|客户端状态4，失败提交交易写集0，未把失败算成功|

VM内Gas与客户端最终Gas是两个边界：原Scheduler在RunContract之后追加RWSet/Event Gas（node/module/core/common/scheduler/run_vm.go:272,287）。不把嵌套子调用累计Gas相加。本轮未改Gas逻辑。

COPY_PARITY.csv及scripts/analyze.py复算同输入业务返回、Gas、已提交Guest命名空间读写集和事件。NFT latestTxInfo只归一化TxId/BlockHeight；事件只移除交易关联tx_id，不删除业务event_data。原始未归一化数据始终保留。Native部署管理命名空间和独立链区块哈希不强求相等。最终账本检查是从所有已记录提交写集重放得到的Guest业务子集，另有真实ownerOf查询；不冒充全链所有键完整导出。

成功buyNow共10次根调用，每次均在相同TxID下真实进入identity.addWriteList、两次isApprovedUser、erc721.mint、setApprovalForAll2、transferFrom。原始node log和CORRECTNESS_CHECKS.csv保留检查；失败重复交易在mint处提前失败，不虚构后两次调用。

复用模式未启用，R0拒绝；没有与历史Reuse Gas差异混合。未测Table函数身份、全部异常/回滚路径、真实节点合约升级/链配置Reset及任意native失败。本轮覆盖的业务回滚为重复token和夹具missing方法，不能扩展为所有异常均已验证。
''')
put('SAFETY_GATE.md','''# 安全准入：接线/功能通过，正式E2E暂停

| 条件 | 状态 | 证据/限制 |
|---|---|---|
| 真节点独立Store执行 | PASS（本轮范围） | 真实SDK交易，runtime Store不等于compile Store；NewInstanceInStore；INVOCATIONS.csv |
| 缓存Module及同Engine跨Store | PASS | 六轮5次准备/62次命中，Owner内元数据准备；固定库6.0.1及加载maps |
| buyNow六真实下游 | PASS |10次成功根调用，每次6个真实child；CORRECTNESS_CHECKS.csv |
| Gas/结果/业务状态 | PASS（已覆盖路径） |Baseline/Copy同新生命周期同初始业务状态，COPY_PARITY.csv；全链哈希与Table身份不在范围内 |
| 关闭/Stop/Reset协议 | 部分PASS |真实node Stop在inflight1时等待完成后退出；实际manager接口Reset、Stop幂等通过；chain-config触发node Reset未执行 |
| Finalizer/借用所有权 | PASS于受控协议 |沿用Step34，未观测守卫失败；不是任意native故障认证 |
| 资源长期或多轮收敛 | **NOT PROVEN** |CAPI配平但RSS仍增长；六轮峰值1481.109MiB，软阈值1536MiB，线程109；Go GC回收live heap不等于RSS/native线程收敛 |

**本轮不签发正式Copy客户端E2E准入，不运行性能压测。** 这不是说所有E2E路径一定不安全，也不是确认已有native资源损坏。新Owner已真正接管有限真实节点调用；阻塞从接线/归属落实为资源收敛证据不足，及尚缺节点级Reset触发覆盖。

原配置触发保护已停止保留。小账本配置容量缩减不是提高RSS上限，不是修复native leak的证据。六轮正常退出也不能证明持续服务无累积。

原池worker并发、共享Store并发创建、异步关闭均未启用。最终实验二进制未opt-in就拒绝StartVM；不能把该managed绑定与legacy池混搭。节点只支持本次1链/1Owner、最多32外部job、固定Guest；不是生产兼容VM。
''')
put('NEXT_STEP.md','''# 最小后续工作

当前不启动Step-36性能实验；先补资源准入证据，避免继续扩大算法研究。

1. 对已记录的Go heap/HeapSys/GC、RSS与线程做有限归属验证：同一Owner下，在业务完成屏障后执行缓存Reset，记录native CAPI计数、host函数注册、线程名/TID、smaps；必要的Go GC只放独立诊断，不能把诊断运行当性能。查清RSS保留页与WASI/native线程回收是否有持续累积；不提高1536MiB/220线程上限，不通过Sleep或频繁重启掩盖增长。
2. 用节点实际manager的Reset入口验证在途排空/缓存失效，并与Stop相同记录。这不要求实现生产在线升级；固定部署下也应确认节点接口接线，不以旧resetC通道推断。
3. 若上述准入补齐，Step-36只做同小账本配置、同新Owner的Baseline Fresh/Copy SDK同步响应对照：优先单方法fact或compute，1合约缓存，2轮各10对；每节点包括部署/验证总外部job<32，不能默默重置预算。SDK开始→同步响应；提交另查TxID。固定输入/唯一状态键；交替组顺序；冷编译/模板记录单列；RSS/线程、Gas/状态/失败率每轮核对。新生命周期配置不同于原生产/Step17，不宣称生产普遍收益。

本轮无性能结论，不再改A/B1/Copy机制。原生产VM和历史成果可直接保留用于研究总结；剩余资源问题是准入问题，不否定已有串行初始化收益。
''')
# Reproducible immutable environment/hash records.
env=json.loads((P/'audit/environment.json').read_text());env['node_adapter_commit']=subprocess.check_output(['git','-C',str(R/'.worktrees/node-step35'),'rev-parse','HEAD'],text=True).strip();(P/'audit/environment.json').write_text(json.dumps(env,indent=2))
(P/'audit/final-source-shas.json').write_text(json.dumps({str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in(P/'source').rglob('*.go')},indent=2))
put('.gitignore','binaries/\n**/*.so\n**/*.test\n**/__pycache__/\n*.pyc\n')
print('reports written')
