# 四节点真实TPS：启动前安全检查未通过

2026-10-20。三项当前TPS均为**未测得**，不是0 TPS。本轮未启动ChainMaker节点、部署合约或发送交易；未编译、修改运行时或加入任何优化。没有复用此前低负载Invoke数据充当TPS。

| 方法 | 历史R0/R1 TPS（用户参考） | 当前R0 | 当前R1 | 当前下降比例 |
|---|---|---|---|---|
| compute.normalCal | 408.7 / 264.3 | 未测 | 未测 | 无法计算 |
| erc721.mint | 4077.5 / 311.4 | 未测 | 未测 | 无法计算 |
| fact.saveAndFindByFileHash | 2959.1 / 380.3 | 未测 | 未测 | 无法计算 |

## 已确认可复用的环境

- 找到`chainmaker-go/build/release/chainmaker-v2.4.0_alpha-wx-org{1,2,3,4}.chainmaker.org`四份发布目录、节点配置、证书及共识配置；配置中的链为chain1、四节点、block_interval=200ms、block_tx_capacity=1000。
- 原`start_four_node.sh`依赖工作目录，`stop_four_node.sh`还可清理旧数据，未直接调用它们；隔离测试必须复制配置/证书、修改路径及端口，不启动原账本。
- 四份发布库与CVW当前packaged库SHA完全相同：`dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。各节点配置、binary和native哈希保存在preflight.json。默认ldd也指向CVW packaged路径。
- `systemd-run --user`接受MemoryMax=2G、TasksMax=256、RuntimeMaxSec=5s，使用`/usr/bin/true`检查成功退出。仅验证可创建带限制的临时服务，没有做耗尽压力验证，更不是节点性能测试。资源隔离可以准备，不是此次唯一阻碍。

## 阻碍从“源码可能不同”推进到了实际二进制证据

对上面实际加载的so执行只读objdump，而非从其他Wasmer源码版本推测：

| ELF虚拟地址 | 指令/路径 | 含义与界限 |
|---|---|---|
| wasm_instance_new + 0x1b12，即0x461062 | `incq (%r14)` | Store引用的非原子递增，没有lock前缀 |
| wasm_instance_delete + 0x11，即0x4618c1 | `decq (%r14)` | Store引用的非原子递减；0x4618e5还递减弱引用 |
| 0x45f683 | 调用InternalStoreHandle::new(0x3ea240) | 实例创建会修改Store拥有的对象容器 |
| 0x3ea24f、0x3ea26d、0x3ea27d–0x3ea286 | 读Vec长度、可能扩容、写元素/长度 | 该容器插入路径自身没有互斥保证 |

保留完整的instance-new.asm.txt、instance-delete.asm.txt和store-object-insert.asm.txt。库中其他Arc计数有lock指令，**没有声称整个库不存在原子操作**。这些静态证据说明相关操作需要调用方正确同步；本轮没有复现崩溃或生成race堆栈，也不声称每次并发调用必然出错。

实际Go调用链没有提供这层统一同步：

- `.worktrees/cvw-step19-reuse/.../vm_pool.go:673–679`每次R1归还都启动独立goroutine执行Close，多个Close可以同时操作同池Store；后台grow也使用同池Module/Store。
- `wasmer-go/instance.go:28–46`直接用module.store调用wasm_instance_new，137–145直接删除实例，没有Store互斥。
- `wasmer-go/store.go:18–20`不含同步字段。
- `wasmer-go/error.go:41–43`的LockOSThread只固定当前goroutine所在线程，不串行化多个goroutine。
- `wasmer-go/module.go:65–78`的锁只保护NewModule，不保护实例创建、调用或关闭；function.go里的锁仅保护host函数注册表。

因此允许发生同一共享引用计数/Store对象的并发访问。进程内存上限、线程上限和故障后终止可以隔离进程资源，不能消除这条竞争路径，也不能保证TPS/状态结果有效。此前没有崩溃或某个样本成功，不能作为放行依据。

## 按本次安全要求停止

本轮要求“不得为了跑出TPS而跳过安全检查”，且禁止加入Step-17根VM串行保护。当前R0/R1原始并发路径不满足最小条件，故在启动节点交易前停止，未通过扩大并发尝试碰运气。

这不是“历史cmc命令找不到所以不测试”：历史数值只作参考，新统一四节点测试可以使用明确的新统计口径。此次直接阻碍是实际native库与Go调用链的Store同步缺口，加上此前尚未完成的资源回收验证。

## 得到有效TPS前需要完成的最小安全工作

1. 明确并验证同一Store所有native访问的所有权/互斥，覆盖NewInstance、WASI/import、Call、Close、exports/finalizer；不能只保护创建worker或只给引用计数换原子，Store容器仍有修改。
2. 不持Store执行锁等待GetInstance或向池channel发送，防止后台补池被阻塞；处理回调重入和跨调用锁顺序。保留默认队列与后台grow，不使用同步fresh替代。
3. 完成关闭/退休与在途实例回收的有界验证，再使用已验证可用的资源限制做短时交易试运行。

这些是安全修复，会改变原始并发实现；必须独立补丁、两组完全相同、明确披露后再测试，不能悄悄添加并宣称只有复用开关不同于未修复的历史程序。本轮没有实施这些修复。

解锁后才进入本次三方法真实TPS流程：隔离四节点、同WASM/输入/配置，部署初始化预热在统计窗外；短批无100ms等待，逐级增加，交换R0/R1顺序。以唯一TxID、成功业务状态、四节点确认的提交记录及相同墙钟窗口计算实际成功提交TPS；发送/提交/失败/超时/排空单列，客户端与VM延迟仅作辅助。R0 Gas不同仅作性能参考，状态分歧或资源异常立即停止。

## 结果文件

preflight.json保存此次新检查；tps_summary.csv三行均明确not_run_preflight_blocked，没有伪造原始交易数据、成功率、延迟或零TPS。本轮所有检查已结束，无ChainMaker实验进程需要回退。生产分支、原四节点配置和账本均未修改。
