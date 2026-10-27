# 同Store串行对照与计时审计

## 可执行安全边界

Step21B未放行共享Store的无同步创建/执行/关闭；它允许完整单一所有者串行操作。Step21D把Go native Finalizer改为强引用ManagedScope，由LockOSThread owner显式逆序清理；原GetGas/SetGas同scope回调可嵌套至两层，其余重入拒绝。Step22/24B把Store+Module缓存到进程内、WASI/Instance逐次Fresh同步关闭，预算为每Store真实init+2正式实例，长Store线程问题未解决。

本轮同Store R0/R1没有恢复原池、worker、shouldGrow、异步关闭，也没用全局锁：同一个已编译Module和同一个Store，native lazy metadata先物化到持久scope；一个R0 init实例保留，R1两次各新WASI/imports/Instance、同步关闭后才继续。总共3个WASI Instance/Store，没有扩大原已测预算。R0/R1用完全相同的code/Module/Store/配置，不把不同Store结果冒充纯Reuse因果。

所有应用层Wasmer C API操作归同一OS owner，激活正确scope；finalizer不在GC线程删除native对象。未改managed.go、Gas getter/setter、opcode映射、Data transformer及原close守卫。预检ABBA确认R1创建/关闭两次后R0仍执行正常、Gas/结果一致；raw StoreID/ModuleID完全相同，R0 ID不变，R1 ID新建。原构建来源与native内部线程生命周期限制仍保留，不认证无限安全。

Fresh Copy对照所需原Module/noData Module不同，各有独占Store，统一固定owner/同步生命周期和对称init。每Store至多3个WASI，进程总6；它们不是共享同一个Module的Reuse对照，也不声称跨模块能保留相同Store。A会改变静态布局及WASM，所以C2不能字面使用同一个hash。

## 范围与两家族

- 历史原件e8b1fe...：新测R0/R1和R1/C1。匹配原件的A构建未恢复，C2为blocked。
- Step18 plain P0：新测R0/R1、R1/C1、R1/C2、C1/C2。R0/R1/C1原始逻辑WASM相同，C1执行对应noData；C2使用原有同源A布局变体，不加入PB/B1。逻辑hash不同，单列MATRIX。
- 三份实际normalCal反汇编均核实10000000循环，见audit/workload-check。相同返回666不能证明工作量，证据来自二进制。
- 原件Gas100000072，Step18家族Gas100000019；每家族内各模式均一致，不能混合绝对Gas或时间。

每批每edge10对来自5进程各2对；同一R0只跑两次正式normalCal，而不是连续10次。第一次目标调用以前执行过init但没有normalCal，第二次以前执行过一次normalCal，分别记录uses_before=1/2。保留全部首个调用，既不清R0内部状态，也不把15个“业务后复用”样本写成30个长期热态样本。另3个原件diagnostic进程将R0预热一次业务，单列，不混入主性能。

## 调用与计时

`dRuntime.Invoke → cache lookup / makeE22 → NewInstance → [restore] → WASI.Initialize → _start → SetGas → CallMethod → GetGas/result → [Fresh close] → deferred return`

R0 cache hit不再创建/启动；逐次重置profile，NewInstance/Copy/start/Close均0，S1/S2作为就绪读取，不沿用init旧时间。原native关闭base仍保存到最终关闭，守卫未改。R0最终保留实例close与持久Module/Store关闭分别记录RETAINED_CLOSE和MODULE_PREPARATION，未把它们均摊或藏入每次调用。

完整Invoke含Fresh创建、Copy、start、业务、Gas和每次显式关闭；模板、Module prepare、真实init、账本clone、root receipt输出和最终缓存关闭在外。Module prepare含配置、验证、Store、编译和metadata，不是纯编译器时间。NewInstance本身不包含随后Copy。S0→S1还含WASI/imports；S1→S2含Initialize/start；CallMethod包含exportFunc.Call，二者不能重复加总。

export计时保留原B5紧贴Call的time.Now单调边界；Getrusage/MemStats只在独立diagnostic中位于该边界之外，CallMethod及完整Invoke会包含诊断开销，所以diagnostic绝不进入主性能CI。

## GC/CPU观测的含义

主运行在f.run前后调用runtime/metrics，记录host GC cycles、heap objects和pause histogram。该窗口还含RunContract上下文与receipt序列化，不能定位到export，更不能当Guest GC。暂停只给histogram累计增量的区间界限，非精确PauseTotal；单次GC可能有两次暂停，暂停事件数不是GC次数。

diagnostic从MemStats得到host NumGC/PauseTotal增量，从RUSAGE_THREAD得到owner线程CPU；两个B5时钟极小开销在CPU包围范围内，不声称和精确wall边界逐指令一致。未使用信号CPU栈采样，采用线程CPU及实际WASM路径作为替代证据；没有Guest函数栈、Guest GC计数、CPU频率或Windows调度轨迹。CPU差可来自执行路径、频率、内存/系统成本，不等于指令数变化；wall−ownerCPU也不是纯调度等待，因为其他native线程未纳入。

## 停止与退出

软限768MiB/125线程、硬限2GiB/256tasks，45s Go/60s进程，global available8GiB/swap1GiB，未提高。已知WASI线程在Store存活期间随Fresh创建增加，所以短进程隔离、没有把同Store延长到10次。每次后重新核对native live计数；最终created=closed、owner managed/pending0、PID/cgroup退出。作用域关闭返回不等于证明所有native线程当场join；进程退出才是有界隔离终点。
