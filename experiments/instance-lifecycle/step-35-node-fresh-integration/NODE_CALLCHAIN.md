# 真实节点调用链

```text
Blockchain.initVM
  -> NewInstancesManager(chain) [source/vm/vm_instances_manager.go]
  -> StartVM [检查缺失opt-in/config/R1/唯一Owner的初始化错误]
Scheduler.runVM -> VmManagerImpl.RunContract
  -> invokeUserContractByRuntime -> NewRuntimeInstance [source/vm/vm_instances_manager.go:53]
  -> nodeFreshRuntime.Invoke [source/vm/step35_node.go:177]
  -> Step34 SafeFreshOwner.Do
       -> nodeFreshManager.prepare [source/vm/step35_node.go:121]
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

Reset/Close接口 -> source/vm/step35_node.go:116 -> Owner.Reset，拒绝新根job、排空、关闭缓存、后续重新编译。该最小版合约级Reset也清空整个有限缓存，未实现细粒度回收。Reset从active Owner调用会拒绝，避免等待自己。

节点停止：ChainMakerServer.Stop -> Blockchain.Stop -> VmManager.Stop -> source/vm/vm_instances_manager.go:221 -> Owner.Stop排空 -> cache scopes -> Owner root -> EndOwner -> 原节点继续Stop store。StopVM不提前返回超时给Blockchain；外部systemd TimeoutStopSec=10s保留整进程硬终止上界，不能安全中断任意native函数。原节点的其他模块停止顺序未重写。

真实在途证据：node-small-inflight-node.log 中invoke_begin -> stop_requested(inflight=1) -> module_prepared -> invoke_end -> cache_closed -> owner_closed -> ChainMaker exit。Stop在编译/创建窗口已开始；未观测到提前释放后使用。
