# 正确性和失败保留

37业务方法×4配置，均通过独立功能预检和3批正式执行；1728正式调用全部同步成功，并由GetTxWithRWSetByTxId确认相同TxID、高度、ContractResult。149份配对核对文件（含预检）均通过。四组逐槽Gas、返回值、排序读写集、事件及已写键的实际状态回读一致。TxID/区块高度等元数据按配对标签规范化；历史查询记录时间仅在识别的HistoryValue结构中规范化，规则见scripts/parity.py。

不能将“已写键最终状态一致”扩大为全账本字节哈希一致。每个配置的batch3账本独立重启，148/148次重新查询交易、高度和状态通过。36次真实错误提交/回滚检查通过：每合约每配置无效export，以及raffle空名单真实Guest错误；无写集，已知状态投影不变。其余业务特定异常分支、真实Table函数身份均not_tested，不标记为全面安全认证。

buyNow使用真实identity/ERC721/exchange，48笔正式根调用各保留六次子调用，无固定返回值。根Gas同槽四组相同；不同token/槽可为12,620,047或12,620,048，未强制跨输入相等。compute.bigNumCal根Gas120,135，fact.saveAndFindByFileHash285，均四组一致。

原raffle4次计划超过三人名单，第三次后为空，第四次真实Guest ExitCode2。整个原窗口排除，原case/client/node日志完整保留；新revision用相同Alice/Bob/Carol名单执行3次，预期Carol/Alice/Bob，独立3批，每组9次。未添加人口或改算法。失败不是资源异常，节点正常退出。最早node编译GetState符号错误及node2基础设施预检亦保留，不算正式样本。

异常测试和重启验证在主采样后单列；不宣称所有方法异常分支已在主实验前覆盖。
