# Step-21异常与未完成项

## 1. 正式首批R1：业务100/100成功，窗口外维护排空失败

原始日志：raw_logs/compute-bigNumCal-a-r1.log。全部100次InvokeTime已返回，code=0，结果`success bigNumCal: 607723520`，Gas均105920。随后两次`step21 maintenance drain timeout`分别来自显式排空及defer退出检查，不是两个独立实验失败。Go日志明确`--- FAIL: TestInvoke`；后续所有正式组停止。

最后的生命周期计数：

| 事件 | 数量 |
|---|---:|
| create_begin / create完成 | 112 / 112 |
| close_begin / close_done | 101 / 101 |
| enqueue_before / enqueue_done | 111 / 110 |
| 业务借出 / 丢弃 | 100 / 100 |
| 队列容量 | 10 |

创建含1个验证实例。扣除验证和100次业务关闭后，仍有11个实例；其中10个已在队列，最后1个创建完成后记录`enqueue_before queue_len=10`，未记录`enqueue_done`。源码的下一步正是`p.instances <- instance`。业务循环已经结束，没有继续取实例的消费者，worker因此无法完成这次入池；尚有维护任务也不能完成。外层close信号无法打断该阻塞发送。

关联源码（以实验VM module为根）：vm_pool.go的GetInstance空池apply、RevertInstance异步remove/add、startRefreshingLoop的apply→shouldGrow→grow(5)和add→grow(1)、grow的无取消阻塞发送。初步机制是需求触发grow与逐次discard补充可以叠加；库存/待补容量没有统一预留。源码与日志共同支持满队列阻塞；没有采集Go goroutine栈，未进一步复现每种调度顺序或量化每个signal来源。

本轮增加的任务计数/barrier只在所有计时调用之后等待既有工作完成，没有新增补池请求、改变容量或给Store加锁。它使原来测试进程快速退出可能掩盖的维护问题显现。不能声称未经等待的旧TestInvoke已经完成安全回收，也不能据此否定旧记录中的每次业务耗时。

R1采样RSS峰值711.98MiB、线程195，未触发1536MiB/220软限；本次停止原因是维护超时，不能写成OOM或线程阈值。所有自启进程已停止，未留驻测试binary。

## 2. systemd最后状态的陷阱

原始outcome中的ExecMainStatus=0与Go FAIL不一致。失败unit使用--collect后被移除，最后一次show可能只返回未加载unit的默认值（inactive/dead、ControlGroup空）。该值不是可信的实际成功退出码。分析以Go FAIL与closed事件缺失判定失败；per_run_summary保留原观测并标注可靠性。驱动exit=2是安全检查的退出码，不是原Go测试binary的可信退出码。

## 3. exchange.buyNow：环境夹具失败，不能计性能成功

两模式smoke各3次，全部code=1，Gas=331，message为`contract message:[buyNow] addWriteList failed `，没有buyNow success；Go测试本身仍可显示PASS，因为原入口没有对业务失败Fatal。

WASM加载、实例创建和_start成功，不代表buyNow成功。原SnapshotMock没有预部署identity/ERC721，也没有真实跨合约账本。原协议ParametersValueMaxLength在该测试入口未按节点配置初始化（protocol变量零值，vm/wasi.go及wacsi_with_gas.go检查参数长度）；也缺少合约元数据/初始状态。原日志没有给出host失败详情，尚未独立区分这些前置限制各自的贡献。不能把它解释成合约算法错误，也不补mock成功响应后宣称真实跨合约性能。

保持E类、主TPS缺失，不对失败路径重复100次或拿Gas331路径与历史成功路径比较。

## 4. 原TestInvoke输入、状态和Gas限制

- 原参数只在循环前生成一次，tokenId实际从1生成但随后会重复。Step-21通过原测试入口的可选输入文件钩子提供1…100，两个模式逐条哈希一致；没有改WASM或计算循环。fact使用按原规则生成一次并冻结的时间，避免两进程参数不同。
- SnapshotMock不是持久账本，每次建立新的TxSimContext；因此唯一TokenID只证明本轮输入规则，不代表验证了真实账本中的跨交易NFT唯一性、授权和初始化。
- prepareContract使用未赋值的包级ContractName，实际contractId.Name为空，Tx payload名是目标合约。保留原夹具行为，不能伪装成真实节点上下文。
- 非race smoke的ERC721：R0 Gas为14469一次、10090两次，R1均14469；fact R0为1585一次、991两次，R1均1585。Go状态复用/Gas路径不等价的风险已实际出现；本轮不改Gas，仅将R0作性能参考。详细race样本另列，不混入主实验。

## 5. 分类与缺失

六个主比较均为E：bigNumCal只有一批已返回的调用且R1退出未通过；其余四个可行方法仅smoke/race，未启动正式组；exchange业务smoke失败。planned_matrix.csv保留36个计划条件，未运行项实际调用数为0、TPS与延迟留空。不能称其余方法“倍率低于历史”或“不复用更快”，因为尚无有效正式数据。

## 6. 后续最小工作，未在本轮实施

先在独立安全补丁中统一grow容量预留/待补计数，避免apply和discard补池叠加越界；入池发送需有退出/取消机制，关闭需处理在途创建和维护任务。不能仅增大队列、跳过排空或强制复用以凑满次数。再检查共享Store的创建/执行/关闭所有权及native引用风险。修复后的两模式必须用同一补丁，作为明确标注的新补充实验，不能替换本轮原策略记录。

补齐exchange需真实可验证的跨合约状态夹具、参数限制和执行链，同时保持原业务路径；这也应独立说明。当前不启动节点、不做Copy或Step-20归因。
