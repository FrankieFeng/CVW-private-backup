# 哪些阻碍真正影响Step22

| 项目 | 当前状态 | 对下一步的影响/最小动作 |
|---|---|---|
| 共享Store并发所有权 | 原池静态危险路径明确；E单owner规避；不同Store并行未认证 | 禁止恢复原无同步创建/执行/关闭。继续单owner小样本可以；并行供给须另审Go全局配置/host/WASI与释放协议 |
| Cold Fresh与Copy Gas | 等账本Gas仍受guest执行历史影响；差值边界明确，精确缓存原因未闭合 | **功能门槛**：声明复制的是哪个初始化点；逐层对冷Fresh比较Gas/返回/RWSet/事件/深度。不要拿热R0 Gas作为Fresh目标，也不调整Gas规则 |
| Module与目标Store | API微型能力通过；原路径本来缓存Module；D每笔重新编译 | **性能门槛**：选一个能够实际运行的同Store串行缓存或独立Store可信Deserialize业务模型，验证WASI/host/metering等价，拆分一次性/每次成本。此轮没有实现优化 |
| 长期资源及关闭 | 小样本scope归零，进程/cgroup收尾；内部WASI线程长期收敛未证明 | **连续100次门槛**：先设计低预算分级资源验收/超时，不抬现有限额；仍不能跑100次或自动并行扩容 |
| Native精确来源 | so固定hash/6.0.1和候选源码已冻结，缺完整构建映射 | 固定二进制有界功能诊断可继续；不得声称通用并发契约/可重建认证，需要取得构建记录或可审计等价库 |
| normal执行差异 | 新短批同方向1.5–3ms，历史8ms不稳定解释；CPU与host GC已记录，guestGC未测 | 阻止将执行窗口收益归因于Copy；不阻止功能验证。先设计可审计guest runtime或同代码布局的短诊断，不能靠重复次数弥补缺证据 |

## 容量修复与性能机制

21B的[POOL_LIFECYCLE](../step-21b-wasmer-store-lifecycle/POOL_LIFECYCLE.md)逐行审计：容量补丁在grow按max−currentSize裁剪所有来源的请求，currentSize包含借出/待remove对象，不能等同队列库存。apply空池请求与R1 remove/add没有去重票据；裁剪可能减少创建/提前返回，改变库存、等待和后台工作量。它避免一类容量溢出，但不修Store并发、Finalizer或关闭等待环。

补丁没有直接改Invoke/CallMethod计时边界，却能通过供给和CPU/资源竞争间接改变时延，不能认为稳态供给未变。E无原池GetInstance通道或异步grow，正常测量从最多3个预建Fresh bundle获取，通道阻塞0表示机制不存在；不是证明原GetInstance等待消失。D按需编译的约0.56秒也不是原池实例化成本。三个实现版本应分列，未建立可以量化换算的关系。

可继续Step21C真实跨合约**有限串行**功能诊断，本轮两个buyNow已实际各执行六callee；不能把这一成功扩大为长期生产许可。Step22本轮仅交付前置诊断及边界，未执行Copy。
