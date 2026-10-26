# 源码证据索引

本目录source/vm是独立实验副本，行号不可混用生产工作区。

| 文件/函数 | 作用 |
|---|---|
| source/vm/step23_checks_test.go:11 TestStep23BuyNow | 三次真实init+一根实际buyNow；同输入/账本/调用图和业务断言 |
| source/vm/step21d_runtime_test.go:226 dRuntime.Invoke | 保留原SetGas、CallMethod、GetGas、结算；增加逐call标识及只读观察 |
| source/vm/step23_probe.go:50 eRawGas | 固定hash/slot、地址边界、只读registry Remain |
| source/vm/step23_probe.go:70 eGas | 当前调用各已采样host/业务边界 |
| source/vm/step23_probe.go:80 eVerifyGas | 与原真正Getter返回核对，不新增guest Getter |
| source/vm/step23_diagnostics.go:60 a23RW | 只读可见累计RW映射，禁止中途GetTxRWSet |
| source/vm/step23_diagnostics.go:70 a23Enter | caller/深度/序号/参数及状态入口 |
| source/vm/step23_diagnostics.go:95 a23BeforeSet | 记录旧计数并标明非本次计费，不转换越限初值 |
| source/vm/step23_diagnostics.go:133 a23Bridge | 原WACSI/SetGas周围的父子Gas传播观察 |
| source/vm/step23_diagnostics.go:153 a23Finish | 返回值/Gas/事件/可见RW结果，无已销毁memory读取 |
| source/vm/vm_bridge.go:178 | 原syscall前后观察；日志边界85/110 |
| source/vm/vm_bridge.go:393 callContractCore | 原跨调用Getter、WACSI与SetGas，未变其算法 |
| source/vm/step22_runtime_test.go:79 e22Prepare | 一次模板+两变体Module/Store准备及缓存 |
| source/vm/step22_runtime_test.go:122 makeE22 | 新WASI/Instance、A1恢复后才进入_start，原Memory页数 |
| source/vm/step22_runtime_test.go:216 closeE22 | 同owner scope显式销毁、原Fresh基线及新增own-scope严格计数 |
| source/vm/step22_static_test.go:85 prepareStaticMemory | 原active data按顺序叠加，移除Data section、合并copy ranges |
| source/vm/step22_static_test.go:235 restore | 原Host区间copy，Module指针/config/key检查，无Data重复初始化 |
| source/vm/wasmer-go/managed.go:151 ManagedLiveCount | 只读自身scope live登记数；旧owner/in-flight/native守卫保留 |
| source/vm/step21d_compile.go:11 dCompile | 原Gas映射与Validate/Compile，逐字节相同 |

外部运行依赖来自固定Step21C工作树，原文件已冻结在audit/runtime_reference：tx_sim_context.go:709 GetTxRWSet会释放迭代器；:864 GetTxRWMapByContractName只合并新映射；:934 CallContract真实进入VmManager。wasi.go:525 WacsiImpl.CallContract；:583加原基础费；:600前后真实调用与累计返回合并；:543非isLen只读结果缓存。vm_interface.go:28基础费常量100000。原vm_factory.go也已冻结，未改其边界。

source.diff相对Step22实际执行源（不仅Git快照），包含探针移植、R0 scope登记适配和新诊断。差异列表见audit/source_changes.json；Step22忽略掉的6个占位Go文件按旧hash恢复并在本轮提交。所有实际guest源hash与build02一致已核对。
