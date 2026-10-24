# Step-21固定协议（正式100次批次前登记）

仅评估复用损失，不接入Copy/A/PB，也不改变WASM。固定当前TestInvoke/testdata已提交的四份WASM，六个方法；完整SHA和100行输入序列见cases.json、inputs/。compute.bigNumCal/hashCal为已有100轮WASM，normalCal为已有1000万循环，未为倍率改变循环。

每组100次连续调用，包含第一笔，无Sleep、无预热剔除；每方法三批，顺序a R0/R1、b R1/R0、c R0/R1；每组独立进程、同一个普通测试binary。先3次每组的独立smoke，再对有效方法做3次每组-race诊断，诊断时长不进入主统计。业务成功按code和实际结果内容验证，不能用Go PASS代替。

原参数规则冻结一次，fact时间为实验开始时秒时间戳；ERC721及exchange tokenId为1…100（原RandomNumberString实际从1递增，length被忽略），每组输入完全相同。SnapshotMock仍是原夹具，非真实持久账本；不同调用各自上下文，不能将mint成功解读为验证了跨交易账本授权/唯一性。原prepareContract的空contractId.Name问题保留并说明，不偷偷修补业务路径。

只增加观测：channel接收语句紧邻的单调耗时、GetInstance整体、返回前库存、每调用原始起止/结果/Gas及参数哈希。原InvokeTime计时范围不变。TestInvoke打印标签TPS(callMethod only)错误，实际分母为executionTime，统计按成功数/成功executionTime总和。失败、首样本和异常值全部保留。

为避免原close无join造成退出截断，在全部计时调用结束后等待apply/discard任务、worker barrier，再等待关闭完成；不在两次调用之间插入等待，不改池容量、shouldGrow、R1异步补池或Store执行锁。窗口外排空与额外JSON输出均记录在source.patch，不能声称与旧binary逐字相同。

保护：进程MemoryMax2GiB、RSS软限1536MiB、TasksMax256、线程软限220、RuntimeMax60s、Go测试超时45s、退出等待5s。若资源、Go race、panic、回收超时发生，停止后续性能执行并保留数据。Go race不能认证native Store并发；这些有界隔离调用仅作性能参考，不扩展并发或生产安全。

比较采用三批合计的总成功数/总成功耗时，倍率=R0 TPS/R1 TPS，并同时给出三批倍率，不平均每次倒数。分类预定义：不完整/失败组E；在0.95…1.05区间内为C（仅5%描述性容差，不是等价检验）；低于0.95且三批均小于1为D，否则标C及批间不一致；大于1.05为损失，若合计倍率达到历史参考则A，否则B。历史公式、WASM、机器未完全对齐，A仅是数值达到，并非历史条件精确复现。Gas差异单列，不隐瞒或改Gas逻辑。

若方法smoke业务失败但进程/回收正常，该方法保留E，不为失败路径给主TPS或扩大100次；其他独立方法仍可进行。已观察exchange在addWriteList分支失败，准备环境缺跨合约支持；不mock成功响应或变换成另一业务方法。
