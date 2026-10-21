# Step-19：原始TestInvoke入口的reuse/no_reuse对照

2026-10-21。**已完成compute.bigNumCal的3个独立批次，每批R0/R1各100次调用，600/600成功。连续无间隔的TestInvoke中，R1每批100次均走空池等待，R0每批仅首次等待；VM日志TPS相差10.4–12.2倍。**这解释了当前工程为何可以在不同负载方式下出现远大于低负载节点日志的差距，但不是历史四节点实验的严格复现。

未加入Copy/A/PB/Renew、根VM锁、同步fresh或额外预填池；没有改原始TestInvoke/InvokeTime计时边界。所有测试进程已停止。普通版结束时回收未完成，native Store并发安全仍未获证明，**停止扩展ERC721**，不做生产安全认证或实际节点吞吐结论。

## 三批正式结果

| 批次/顺序 | 每组成功/调用数 | R0平均Invoke(ms) | R1平均Invoke(ms) | R0 TPS | R1 TPS | R0/R1 | R1下降 | 创建完成数R0/R1 | 空池等待次数R0/R1 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| a：R0→R1 | 100/100 | 0.266620 | 3.251027 | 3750.66 | 307.60 | 12.19倍 | 91.80% | 6 / 101 | 1 / 100 |
| b：R1→R0 | 100/100 | 0.269778 | 2.807141 | 3706.75 | 356.23 | 10.41倍 | 90.39% | 6 / 101 | 1 / 100 |
| c：R0→R1 | 100/100 | 0.304064 | 3.235688 | 3288.78 | 309.05 | 10.64倍 | 90.60% | 6 / 101 | 1 / 100 |

六组返回均为`success bigNumCal: 607723520`，报告Gas分布均为`{105920:100}`，未匹配到错误、panic或race日志。R0在本方法Gas一致不代表其他合约复用安全。每组100次是在**同一个进程和池内连续调用**，不是100次独立实验；真正独立的对照批次为3个。没有用600条当作600个独立重复，没有估计95% CI。

P50/P95、编译耗时、采样RSS/线程、创建开始/结束、关闭开始/结束分别见summary.csv。单组编译约0.47–0.52s，在InvokeTime分母外。创建完成数包含验证实例及后台创建，不是纯wasm_instance_new耗时。

## 与先前节点日志并列

同一compute WASM SHA256=`e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507`，bigNumCal为100轮版本；未重编合约，未证明其为王浅秋历史部署二进制。

| 环境 | 样本 | R0平均(ms) | R1平均(ms) | R0 VM日志TPS | R1 VM日志TPS | 差距 |
|---|---|---:|---:|---:|---:|---|
| 先前单节点SDK低负载 | 每模式20条，单批 | 0.364369 | 0.378341 | 2744.48 | 2643.12 | 1.038倍 |
| 原始TestInvoke a | 每模式100次 | 0.266620 | 3.251027 | 3750.66 | 307.60 | 12.19倍 |
| 原始TestInvoke b | 每模式100次 | 0.269778 | 2.807141 | 3706.75 | 356.23 | 10.41倍 |
| 原始TestInvoke c | 每模式100次 | 0.304064 | 3.235688 | 3288.78 | 309.05 | 10.64倍 |
| 王浅秋历史bigNumCal参考 | 精确批次/公式未恢复 | 不换算 | 不换算 | 295.8 | 210.4 | 1.406倍 |

这些TPS均不能解释为实际成功提交TPS。历史ERC721的13倍是另一个合约，**不能拿本轮compute的约10倍宣称ERC721历史已复现**。

两种当前环境的区别：

- 节点：真实单节点账本、SDK/网络/共识；业务Invoke从默认已预填池取实例，每次响应后等100ms。该轮排除3次预热，未观察到空池等待；读取vm_factory外层Invoke窗口。
- TestInvoke：直接构造RuntimeInstance、SnapshotMock、模拟上下文，无真实账本、节点、RPC或提交；池验证后业务队列为空，由首次GetInstance触发grow。100次连续执行，无额外间隔、预热或剔除首样本；读取内层InvokeTime窗口。
- 两环境的上下文、日志、边界和压力均不完全相同，不能只用两者的TPS差认定单一原因。

## 本次直接支持的解释

每批R0只有第一笔等待，之后使用池中已有实例；R1每次丢弃，连续请求使补池成为同步等待。acquire_effects.csv按**同批耗时总和**比较，GetInstance整个函数的额外耗时约对应Invoke总增量的95.3%–96.7%。该函数含分支、日志及观测，不是纯channel阻塞探针；此比例是关联分解，不能宣称全部为Memcpy、纯创建或CPU争用成本。

这给出了当前连续调用条件下的直接证据：**创建虽在后台，供给不足时其延迟通过GetInstance等待进入InvokeTime。**它与先前低负载无等待的结果相容。没有对历史机器、WASM、并发配置和计数公式做因果推断。

## 原始入口和计时审计

GitHub主分支经`git ls-remote`确认是`c3e8f2cc1479a11450d61e342a93c3b2416b7cff`：

https://github.com/wqqkakuiii/CVW/tree/c3e8f2cc1479a11450d61e342a93c3b2416b7cff

实际源码commit为`9caf9d2da13eef64363ad39e84a3a19eb2957bbf`，工作分支`experiment/step19-testinvoke-reproduction`；运行时主体沿用eac4f29。environment.json逐文件保存GitHub/实际源码哈希；source-vs-github.patch覆盖本轮实际编译的chainmaker源码差异，包括vm依赖里的辅助日志。

| 对象 | 实际位置，路径以VM module为基准 | 审计结论 |
|---|---|---|
| TestInvoke | runtime_test.go:369–370 | 与GitHub文件逐字相同，调用runInvokeWithConfig |
| 100次循环 | runtime_test.go:373–432 | 参数需显式传100；默认值仅1。每次建立新TxSimContext，成功才累加executionTime；无预热剔除 |
| 标签错误 | runtime_test.go:414–415、432 | 注释和TPS(callMethod only)误导；实际累加第五个返回值executionTime，不是第六个callMethodTime |
| InvokeTime | runtime.go:213、222–250 | 元数据读取后采startTime，最外层defer采endTime；后注册的defer（归还、上下文移除、instance_compare）先执行，包含在分母内。没有移动原有采样位置 |
| GetInstance/SetGas/CallMethod/Gas | runtime.go:260以后 | 均在该窗口内；结尾Debug打印位于采endTime之后；CallMethod仅是嵌套子窗口 |
| newVmPool | vm_pool.go:789、1033–1077 | 验证/编译、创建并关闭一个验证实例，再启动worker；业务队列仍空，currentSize=0。没有调用节点manager的预填5步骤 |
| 初次取实例 | vm_pool.go:628–665、1089–1096、1179–1196 | 空池发送apply、阻塞接收；worker一次grow5，逐个创建入池，与继续执行可能重叠 |
| R0/R1 | instance_lifecycle_trace.go:13–19；vm_pool.go:669–684 | GitHub原版if true强制丢弃；实际分支以显式环境变量R0/R1替代，R0仍保留shouldDiscard错误策略 |
| 回收 | vm_pool.go:1116–1134、1344–1346 | close仅关闭信号channel，没有join或完成通知；TestInvoke返回不保证worker已退出 |

GitHub原版本身已有WASI freelist及先Close再remove/add，本轮未新增该资源策略。实际分支新增生命周期及B5观测；开销未校准，R0/R1完全相同。未改Opcode/Gas表、Memory配置、合约和业务输入。

另有原始夹具细节：prepareContract读取未赋值的包级ContractName，导致contractId.Name为空，而Tx payload的contractName是compute；日志实际显示空名。为保留入口未修补。SnapshotMock没有真实持久账本，不能宣称验证了节点状态提交。

## 安全检查及扩展停止

先分别运行R0/R1各100次`-race`诊断，与600次普通版性能数据严格分开；未报告Go race，采样未触发限额。**Go race不覆盖native Store并发，诊断成功不是native安全证明。**

每组单独进程、MemoryMax=2GiB、TasksMax=256、RuntimeMax=90s、TimeoutStop=5s、测试超时60s；软阈值RSS=1536MiB、线程=220，出现race或限额即终止。普通版R0采样RSS峰值259–280MiB，R1为654–657MiB；线程最高94，全部正常退出，没有观察到资源耗尽。这只证明短时有界进程未触发阈值。

普通版进程退出时，R0创建完成6，但关闭完成只记录1/3/1；R1每批创建开始102、完成101，关闭完成101/100/100，有创建在途。原始close未等待，所以记录截断不能直接认定运行时泄漏，也不能当作回收通过。-race运行因退出等待不同，能记录更多清理，不能拿它替代普通版回收证据。

基于这些回收缺口及先前native Store非原子引用/容器修改证据，按任务要求**不扩展ERC721，不运行长期/节点压力，不以Go race通过放行生产**。要补齐需要设计并验证Store所有权、在途创建/关闭和shutdown等待；本轮没有暗加全局锁或改同步fresh。

## 复现命令及材料

本地发现的原包装器`chainmaker/cmd/run_testinvoke/*.go:691–709`会执行以下go test入口；未找到本轮用户消息之外的逐字“王浅秋100次命令”，所以按该包装器透传标志恢复。为排除go test缓存，实际先编译一次普通测试binary，再每组独立执行，等价的直接入口是：

```bash
cd chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0
CM_REUSE_EXPERIMENT=R0 GOMAXPROCS=4 \
go test -count=1 -run '^TestInvoke$' -v . -args \
  -invoke_contract_name compute -invoke_contract_method bigNumCal \
  -invoke_contract_type go -invoke_test_time 100
```

R1只切换环境变量。不要原样无保护启动；实际systemd/cgroup、binary和完整标志见每组`*-command.json`及run_guarded.py。三批顺序a R0/R1、b R1/R0、c R0/R1。

构建使用已安装Go1.25.0，显式GOROOT=/usr/local/go、GOTOOLCHAIN=local、GOPROXY=off及保存的go.work。第一次尝试GOWORK=off因缺少旧crypto/sys缓存失败，保存于build-race.log；没有下载、升级或替换依赖，随后用当前工程workspace成功，完整模块图见modules.jsonl。不要把该失败当作性能样本。

WASM、native、普通和race测试binary的SHA256均在environment.json；native沿用packaged Wasmer6.0.1。Go/OS/CPU、源码commit、R0/R1配置、参数、运行命令、原始日志、600条samples.csv、每批summary.csv及公式都已保存。复算：`python3 -B analyze.py`，不会启动测试。summary.csv中的TPS与原始TestInvoke打印值逐组核对一致，公式为`成功数/成功InvokeTime总和`。

材料包`testinvoke-minimal-repro.tar.gz`仅使用白名单打包，不含密钥、证书、账本、SDK配置、测试binary或so。原始runtime_test.go含其他不相关方法的内嵌PEM测试夹具，因此包内不分发完整文件；仅给入口非敏感摘录及完整文件哈希，从固定GitHub commit取得未改原文件。source-vs-github.patch不修改runtime_test.go。未向任何人发送材料。

所有owned单元已停止，生产主分支和已有Step-19数据未覆盖。结果保存在新目录；回滚仅弃用实验分支，不对旧工作区reset/clean。
