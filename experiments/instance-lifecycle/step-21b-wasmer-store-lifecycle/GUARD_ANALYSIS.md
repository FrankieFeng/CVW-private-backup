# Step21A守卫触发归因

只读分析已有失败，**没有重新运行被STOP的场景**。完整原始现场已复制到[evidence/step21a](evidence/step21a/)，逐行结构化事件见[guard-events.json](evidence/guard-events.json)。源目录Step21A文件没有覆盖。

## 检测的实际条件

`step21a_guard.go:26–48`用每池atomic CAS将owner从0设成1(create)、2(execute)或3(close)。失败就输出owner/requested/时间戳及全Go栈，`os.Exit(86)`，不等待、不加锁串行化。它记录**区间是否相交**，不记录native地址、线程ID、读写位置、Instance身份或数据竞争检测结果。

create覆盖`newInstanceFromModule`入口直到返回（A/vm_pool.go:1290–1291），包含uuid、日志、WASI config等非Store操作；execute在GetInstance后、Gas/业务前进入（A/runtime.go:271–272），Close从CloseInstance入口包住（A/vm_pool.go:724–725）。execute leave按defer顺序先于Revert，正常同一Invoke的归还关闭不会因此与自己的execute区冲突。

## 实际事件时间线

时间均为原日志Unix纳秒，未改写为本机新运行时间；日志第1行为表头计数起点。

| 原log行 | unix_ns | 事件 |
|---:|---:|---|
| 8–23 | 1792948458979419149起 | 验证Instance `889415088d1b442486d5b85a09f85dea`创建后关闭，非业务库存 |
| 32 | 1792948458996792431 | worker创建业务候选 `d29c0f7d059147418a55c8c222772a76` |
| 43 | 1792948459000761528 | 该Instance enqueue_done，已可取走 |
| 44 | 1792948459000766887 | worker开始下一Instance `ef82a07ccbcc47918e8fc7d30b0fb401` |
| 47 | 1792948459000843135 | Invoke取得d29c… |
| 50 | 1792948459000871645 | guard：owner=1/requested=2，拒绝进入执行区 |

上表行号需以原log核对，结构化JSON保留精确log_line；create_begin到guard约0.105ms只是墙钟间距，不是native并行耗时或竞态窗口。

失败栈中goroutine22停在`step21aEnter→InvokeTime`；goroutine23在`wasi_config_new→NewWasiStateBuilder→acquireWasiEnv→newInstanceFromModule→grow→startRefreshingLoop`。`wasi_config_new`没有Store参数。该次execute被守卫阻止，不能说exportFunc.Call已和worker同时触碰Store。

## A–E逐项归因

| 类型 | 现场结论 | 证据范围 |
|---|---|---|
| A 不同Instance共享Store创建/执行区间重叠 | **命中拟执行入口与另一创建区间** | d29c…已借出，ef82…正创建；同一pool使用p.store；尚未进入实际业务native执行 |
| B 同一Instance访问重叠 | **未发现** | 两个UUID不同；guard本身未按Instance检测，不能泛化为全面排除B |
| C Instance关闭时仍有在途调用 | **未发现本次证据** | 业务调用尚未开始，未见该业务Instance关闭；源码另有风险不等于现场发生 |
| D Store/WASI已释放仍访问 | **未发现本次证据** | pool未进入close；不能从verify关闭推出业务Store已释放 |
| E 仅区间重叠，未发现对象冲突证据 | **本次观测的上限** | 没有同时native读写地址或内存破坏记录；实际结果是安全预防性中止 |

A与E在这里不是互斥：A描述拓扑和生命周期区间，E限制对具体native冲突的推论。结合本轮6.0.1/实际so审计可知，**若继续不受约束地重叠，存在共享可变Store/Rc的不安全访问路径**；这属于静态发现，不能倒写成那次守卫已抓到native race。

## 保守性与盲区

守卫把纯日志、构建WASI config等也纳入create，因此可能在尚无Store访问的时刻报警，确实保守。它没有持久OS线程所有者，也不覆盖binding Finalizer、WASI cap丢弃后GC删除、module/store删除及所有外部API入口，不能“未报警=安全”。只缩小守卫区间或禁用它不能解决本轮发现的Rc/StoreMut约束。

[outcome.json](evidence/step21a/preflight-bigNumCal-original-r0-a-outcome.json)为store_guard_stopped、0业务返回，记录峰值约207.44MiB/23线程。其systemd字段却保存inactive/success/ExecMainStatus0，与源码os.Exit86不能等同；运行器原来在后续状态采样可能丢失失败状态。本轮**只报告源码定义的退出码86与实测日志命中**，不把86标为该旧进程已可靠采集的退出状态。没有恢复当时OS收尾/Finalizer，不能称正常排空。
