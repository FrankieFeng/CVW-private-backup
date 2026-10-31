# 所有权与释放协议

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
