# Step-19 默认实例池供给与资源有界性审计

2026-10-20。仅重新读取保存的源码、日志、CSV；没有启动节点、执行合约、重新编译或修改生产代码。结论是**当前不能原样开展并发阶梯负载**，先完成Store访问与资源回收的安全门槛。R0仅为隔离性能参考，不是正确性基线。

## 1. 创建worker、容量与等待

审计源码为`.worktrees/cvw-step19-reuse`，运行源提交`eac4f29`，后续`68ccd5a`仅精简manifest和记录版本。

| 路径 | 行号（vm_pool.go，除特别注明） | 行为 |
|---|---|---|
| 首次加载 | vm_instances_manager.go:107–113 | newVmPool验证一次；manager同步grow5，然后缓存pool |
| 初始验证 | 1064–1074 | 创建1个完整实例，关闭；启动每池一个刷新goroutine |
| 默认队列 | 25–44、1053 | channel容量10，初始/最小5，增长步长5；不是10个创建worker |
| GetInstance | 628–665 | 先非阻塞接收；为空则新goroutine发送apply，调用者等待队列；无context取消/超时分支 |
| R1丢弃 | 669–680 | 每次业务结束另启goroutine，Close→remove信号→add信号，两个控制通道均无缓冲 |
| R0归还 | 681–683 | 正常实例直接回队列，错误仍按shouldDiscard丢弃 |
| 补池 | 1081–1151、1179–1196 | 每合约一个刷新loop；接到add后grow1；grow内部逐个同步创建、入队；不同合约池可并行 |
| 扩容 | 1158–1176 | currentSize<5直接grow5；否则currentSize+5<=10且apply计数>100或平均等待>10ms |
| 定时器 | 27、1098 | 12小时只是定时检查；每次discard后的grow1立即触发，不等12小时 |
| 平均等待 | 1329–1335 | 累计阻塞时间/全部acquire数，毫秒整数；正在等待但尚未取得实例者还没有计入 |

`currentSize`不是可用队列长度：借出不减，remove信号才减，且可能尚未处理。等待apply发送的goroutine也没有数量上界。扩容阈值不能代替及时的背压/超时。

单合约R1的可用量关系为 `Q(t)=Q0+成功入队数−成功借出数`；R0还要加业务实例归还数。瞬态累计需求超出Q0与入队之和，或持续需求速率大于实际供给，都会产生等待。突发即使长期平均负载不高也会耗尽5个预建实例。

需求应按该节点、该合约的实际VM attempts及跨调用计算，不能直接用成功提交TPS替代：提案/验证重执行、失败调用、跨合约都可能额外取实例。不同合约池的速率也不能直接合并成一个串行worker速率。

可能降低供给的路径：单worker创建和_start成本、CPU竞争、WASI/import准备、关闭及信号调度滞后、队列发送阻塞、资源增长导致分配/缺页成本变化。当前只确认这些路径存在，未证明哪一项主导历史TPS损失。

## 2. 18与113个实例的数量守恒

| 三合约批次 | R0 | R1 |
|---|---:|---:|
| verification | 3 | 3 |
| 初始grow | 15 | 15 |
| init_contract后的替补 | 0 | 3 |
| 92笔业务后的替补 | 0 | 92 |
| 总创建 | 18 | 113 |
| 实际关闭（不含进程退出） | 3 | 98 |
| 总入队 | 15 | 110 |
| 总借出 | 95 | 95 |
| 空池等待事件 | 0 | 0 |

92笔=compute两方法各23笔+ERC721 23笔+fact.save 23笔。R0每合约轮转5个预建实例；R1每次取得不同实例。没有证据显示该批次执行了额外grow5。三合约借出后的queue_len快照始终为4；R1替补入队恢复5。

fact目标方法补测单独一批：R0创建6、关闭1，R1创建30、关闭25；24次借出为init_contract一次+23次业务。不能把该批混进18/113。

## 3. 从已有日志测到的供给时序

`replacement_pairs.csv`按池关联drop→close_done→下一次create_begin→enqueue_done。脚本检查每次替补完成早于该池下一次drop，因此这批单在途日志里的FIFO关联无歧义；不假定高负载也能这样关联。

| 合约（首批R1） | 替补数，含init | drop至入队Median ms | close_done至create_begin Median ms |
|---|---:|---:|---:|
| compute | 47 | 4.746 | 0.015 |
| ERC721 | 24 | 4.836 | 0.014 |
| fact.save | 24 | 4.874 | 0.014 |

这只是低负载时关闭/调度没有积压的证据，不排除高负载形成close/remove/add积压。上述复合窗口不等于纯wasm_instance_new，不取其倒数推断TPS。

按每方法20笔采样的同一墙钟窗口统计：

| 首批R1方法 | 窗口秒 | 成功入池数 | 实际入池/秒 | 创建函数墙钟占比 |
|---|---:|---:|---:|---:|
| compute.bigNumCal | 2.550 | 20 | 7.84 | 3.68% |
| compute.hashCal | 2.572 | 20 | 7.78 | 3.94% |
| erc721.mint | 2.502 | 20 | 7.99 | 3.98% |
| fact.save | 2.532 | 20 | 7.90 | 3.73% |

供给受人为100ms请求间隔限制。墙钟占比是创建函数elapsed之和/窗口，并非CPU利用率、也不含所有关闭/控制循环工作。这些数字不能当作最大创建能力或节点TPS。原始窗口和边界差见sample_windows.csv。

低负载下Invoke小差异的解释已经足够明确：每次借出时仍有库存，下一请求来前替补已完成；Invoke只支付取用、业务和归还/调度开销。后台创建/_start不会完整串行加入该次Invoke。仍可能发生资源争用，不能把小差异全部指定为goroutine启动成本。

## 4. 资源有界性：目前没有通过

同一20笔采样窗口的整进程资源变化（包含业务、host、分配器和同期节点工作，未分离native/Go）：

| 方法 | R0新建数 | R0 RSS增长 MiB | R1新建数 | R1 RSS增长 MiB | R1虚拟地址增长 GiB |
|---|---:|---:|---:|---:|---:|
| compute.bigNumCal | 0 | 141.73 | 20 | 224.99 | 120.13 |
| compute.hashCal | 0 | 141.39 | 20 | 227.21 | 120.19 |
| erc721.mint | 0 | 147.57 | 20 | 228.18 | 120.13 |
| fact.save | 0 | 143.21 | 20 | 224.45 | 120.13 |

R1窗口约11.2–11.4MiB RSS增长/业务调用，是**混合路径的观测比值，不是单实例分配量**。R0无新建也增长约7MiB/调用，足以否定“全部RSS增长来自创建”的归因。不同进程的差额也不能直接认定为native Memory成本。

末尾5秒空闲：R0 RSS1848.57→1848.72MiB，R1 2230.33→2232.51MiB；VA分别维持120.39/690.45GiB，Threads均265不变。VA不是物理占用；5秒未回落不能独立证明永久泄漏。线程在该短批次未持续增长，不代表长期回收已验证。

已检查Go释放链：vm_pool.go:695的CloseInstance执行CallDeallocate→Instance.Close→releaseWasiEnv；sim_context.go:202的Deallocate主要清理合约参数，并不证明整个线性内存、Store对象或OS映射释放；wasmer-go/instance.go:137关闭exports/imports并调用C.wasm_instance_delete。Store/Module在pool关闭时才释放。

WASI freelist只保护可回收env切片，cap10不限制累计创建数、在途env或已遗留的native线程。当前原始日志没有Finalize/freelist计数（INFO未输出），所以不能计算实际命中率或证明所有线程属于WASI。

本地Rust源码`wasmer_chainmaker` HEAD `7c14de7f8`提供风险线索：

- lib/c-api/src/wasm_c_api/store.rs:8 是Rc<UnsafeCell<Store>>，没有自动跨线程互斥保证。
- lib/vm/src/store.rs:48保存memories/functions/instances等Vec，271–274插入对象时push；StoreHandle clone只复制句柄。
- lib/c-api/src/wasm_c_api/instance.rs:108接收Box并在函数结束drop。**空函数体不是“不执行析构”**；但丢弃包装句柄也不能证明Store拥有的底层对象释放。
- Go Instance.Close中第二次Exports.Close需核查幂等性；本地Rust vec删除take会清空data/size，不能据Go重复调用直接断言double-free。

这些Rust文件没有证明与实际packaged6.0.1 so逐字同源，不能直接把其行为确认为当前RSS增长根因。缺少：smaps映射分类、Go heap/GC计数、native Store对象计数及释放计数、WASI实际新建计数。

## 5. 并发与生命周期阻碍，及最小修复方案（未实现）

| 阻碍 | 证据/风险 | 最小下一步 |
|---|---|---|
| 共享Store并发 | 业务、后台create和async close使用同池Store；无完整Store锁；Go race不覆盖native | 先匹配so源码/线程契约；若不安全，在独立分支对同Store全部native访问建立一致所有权/同步，不仅锁root Invoke |
| 锁方案可能死锁 | 持Store锁等待GetInstance会阻止补池获得锁；跨合约可能形成A→B/B→A锁环 | GetInstance等待、channel发送不得持Store执行锁；单合约起步，设计重入/跨调用锁顺序并验证；所有R0/R1用相同安全策略，注明偏离历史 |
| 关闭不等于回收 | Close调用次数正常但RSS/VA不回落，R0同样增长 | 分离Go heap、Store对象、映射、WASI资源；验证无在途引用时释放Module/Store；不能靠强制GC或轮换Store掩盖后宣称历史复现 |
| pool close/reset | 刷新loop按currentSize等待队列，但R1在途实例关闭后只发remove，不回队列 | 退休标记+活跃/关闭中/创建中计数；等待在loop外或仍处理完成信号，最后释放资源；取消等待者 |
| 容量/控制队列 | currentSize包含尚未remove对象，不含pending add承诺；grow1没有统一预留容量，grow入队可阻塞刷新loop | 明确available/in_use/closing/creating/pending，原子预留容量与有界信号队列；验证满队列及退出路径 |
| 创建错误 | grow忽略newInstanceFromModule错误后解引用；验证实例也先使用再检查 | 创建失败不入队、不增加库存，传播给等待者；清理部分WASI/import资源 |
| Go计数器竞争 | newInstanceTime为全局float64，多个合约worker可同时+= | 删除诊断全局累加或改安全计数；用实例/池局部指标 |
| R0 Gas | fact目标方法18/20组差异，1707 vs1113 | 原样记录，只作隔离性能参考，不认证生产正确性 |

两项具体反例是源码推演，不声称已在本批复现：

1. currentSize=5、队列4、有一个R1实例在途。loop进入close排空4个后仍等第5个；在途结束后Close并等待remove，而loop正等队列，两者不能互相推进。reset有类似风险。
2. 已扩到10后，5个remove先被处理，留下currentSize=5和5个pending add。若apply计数此时满足阈值，grow5把计数加到10，随后pending add继续grow1，可超出名义10；满队列发送又可能卡住控制loop。单看channel容量不构成完整资源上界。

本轮仅提交修复方案，未修改运行时。后续同步/回收修复须单独记录补丁和测试，不能将修复后的吞吐标为未经改变的历史实现。

## 6. 历史cmc口径

当前源码：parallel_request.go:81是异步SendTxRequest(...,false)，parallel_dispatch.go:277以e==nil计成功；parallel_statistician.go:238按RPC成功数/发送窗口计算TPS。返回成功不直接证明业务提交成功。

同文件154行CTps按每节点区块TxCount/elapsedSeconds，364行不逐笔筛除业务失败；printDetails在parallel_main.go:260按发送结束墙钟设置统计跨度。`cmc parallel analyse`另按(start,end]区块范围、秒级区块时间统计（parallel_analyse.go:135–169），也不是相同时间口径。全局statisticianTxBlock:321对订阅事件直接累计；若订阅四节点，不应未经区块/TxID去重便把全局累计当唯一链TPS。

现存cmc二进制哈希/buildinfo在上级目录。未找到给定历史295.8/210.4等五组数据对应的原始命令、输出和统计脚本，也没有证实历史二进制对应当前源码。历史PPT里的进程隔离结果不能代用。

需要王浅秋提供：node/VM/native/cmc版本和patch、完整cmc命令（线程/loop/限速/only-send/订阅节点）、TPS字段和起止定义、四节点机器分布及配置、原始WASM哈希/输入/账本状态、原始cmc与节点日志、Gas失败/重试记录、WASI freelist与进程隔离状态。

## 7. 最小阶梯设计：当前blocked，不执行

先过第5节Store同步和回收门槛，再用单验证节点、单合约、同WASM及输入、默认池运行R1；R0仅在隔离账本作参考。先compute.bigNumCal或ERC721之一，不同时装载三合约，先不使用存在Gas分歧的fact目标方法解释性能。

见staircase.csv：20/40/80/160笔每秒，每阶32笔，最大在途2/2/4/8，总创建预算48/进程。每阶独立进程和空账本、3次warmup、预建队列恢复5后发送；固定开放式节奏，不因上一响应慢而无限降速，也不在迟到后补发突发。记录计划/实际发送率、排队及被在途上限拒发的数量。允许提前结束，未达到计划负载不能声称该阶无瓶颈。

这些0.2–1.6秒发送窗只用于**短阶跃/转折探测**，不是稳定TPS或P95/P99认证。32次足以超过初始5个库存，仍需看窗口末库存是否持续下降；初始库存补贴、瞬时突发与持续供给不足分别标记。若没有转折，仅报告“所测负载未触及”，不自动扩时/加并发。可单列8笔微突发验证等待路径，但不能用它证明持续吞吐瓶颈。

保护：独立cgroup（若权限支持）memory.max=2GiB、pids.max=256；监督器100ms采样，RSS>=1.5GiB、就绪后增量>=256MiB、MemAvailable<4GiB、线程>=220、创建数>48、等待者>8、单次池等待>500ms、任意trap/进程异常或业务失败，立即停止发送并排空至多5秒。随后仅终止该实验拥有的进程组；保存原始失败样本。硬限制/监督器无法生效则不启动。阈值是拟定保护参数，不是测得的正常范围。

创建预算也包含verification、预建、init和重执行；停止时未提交交易标pending，不删去。强制退出只用于资源保护，不算资源回收验证。达到阈值时该阶是资源中止结果，不可用于稳定吞吐宣传。修复前的当前保留成本可能触发这些保护，不能放宽保护去追历史数字。

## 8. 必需埋点和判据

- 每池：create开始/成功/失败、S1/WASI/_start、enqueue前后、acquire开始/取得/等待/超时；记录parent drop ID关联替补，worker忙碌/空闲、pending close/remove/add、available/in_use/creating/closing、队列长度和零库存持续时间。
- 每交易：TxID、root/child、VM attempt、方法、实例ID、Invoke起止/取池等待、成功或失败、Gas；统计每笔成功提交对应的总attempt及创建数，不能只看请求数。
- 提交：唯一TxID+区块高度+业务状态，客户端submit/commit/失败/超时；成功提交TPS按同一时间窗，发送结束后单列排空和滞后提交。客户端延迟和VM/池等待不互相替代。
- 资源：CPU user/system、RSS/VA及smaps_rollup、线程/goroutine、Go heap/GC、Store/Module/WASI计数；计数必须安全，禁止热路径Memory SHA。
- 时间：进程内monotonic；不同节点不直接减未校准时间戳。现有队列值只是事件快照，既有elapsed acquire不能分离纯channel等待；未来需独立等待起止。已有create事件没有父drop ID，在高并发不可沿用本次FIFO推断。

确认“补池瓶颈”需要同一阶先看到Q耗尽/等待增长，创建worker持续忙或close/control积压，实际借出需求超过入队供给，同时成功提交率平台化、客户端和VM池等待上升。若worker空闲却等待长，应查信号/扩容/锁而不是memcpy；若队列充足却TPS下降，应查业务、调度、共识、提交与资源争用。

历史损失**可能**来自创建及补池，但本轮低负载既不能证实也不能否定。只有上述时序与成功提交证据、加上历史负载/版本对齐，才能区分补池供给不足、线程/内存问题、重复执行和统计口径差异。

## 交付与复核

`python3 -B audit_existing.py`只读取上级已保存日志并重建本目录CSV，不启动节点。inventory.csv、replacement_pairs.csv/replacement_summary.csv、sample_windows.csv、idle_resources.csv保留统计依据。没有修改原始samples.csv、日志或旧报告；没有开展新性能实验。
