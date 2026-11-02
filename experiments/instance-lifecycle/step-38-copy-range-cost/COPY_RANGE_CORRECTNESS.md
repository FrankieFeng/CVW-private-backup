# 正确性检查

## 原生边界测试

冻结A2的TestStep38Memory在SafeFreshOwner内使用当前patched native运行；先Native原Module实例化得到完整Memory，再为每策略新建Store/NoData Instance，确认全部初始字节为零，restore后逐字节对比全部Memory。

覆盖：全零段、非零段、短/长零gap、直接相邻段、重叠、显式零覆盖、out-of-bounds实例化trap、memory.grow后的旧前缀与新零页、两个同时存活的独立实例的写隔离。grow后固定模板长度不匹配会被拒绝。OOB源plan被拒绝，native原模块确实trap；安全VM保留fallback原模块分支，不用NoData掩盖原始失败。

A3-memory追加automatic start trap与**脏目标负对照**。在未执行业务的测试实例里人为写入模板范围外的字节，再restore，脏字节仍在，证明restore不是Reset。该试验没有把非Fresh方案用于正式业务。A3只增加测试代码，运行机制与A2相同；不将A3作为新的性能版本。

结果均保存在MEMORY_CHECKS.csv和原始memory-A-r1/memory-A3-controls.log。第一次memory-A因缺少CM_STEP21A_POOL配置而在Go初始化guard处panic；原日志保留，之后只修正环境并用新label重试。

## 真实Go/WASM预检

10方法×6配置的独立预检均开E38_VERIFY_MEMORY=1：对每个根/子Instance在_start之前比较**整个初始Memory**与原source解析得到的Image，包含F0原Data初始化与C0～C4。不是只比较Hash或返回值。正式性能关闭该扫描，全部预检不纳入性能统计。

初始化、前置业务均真实执行；each target恢复等价内存账本，原始snapshot/inputs/TxID相同。所有正式成功，Gas、ContractResult（含事件）、读写集与最终账本Hash逐槽完全相同，不做性能样本筛除。buyNow使用真实identity.addWriteList/isApprovedUser×2、ERC721.mint/setApprovalForAll2/transferFrom，保留每笔六次子VM记录，没有mock成功返回。

辅助校准另复核A/B结果与状态匹配；semantic-state-check.csv额外核对ERC721 token所有权、buyNow最终owner及fact真实写入。fact冻结实现的Fact字段未导出，json.Marshal(fact)写入`{}`；后续查询返回已有私有字段生成的JSON。保留原语义，没有为加重工作负载改字段/序列化器。

## Gas/上下文边界

本轮沿用现有VM夹具：step21d_context_test.go的BlockVersion=1，RunContract输入gasUsed=0，固定公开P256测试成员/时间戳、内存账本；不是Step36真实节点的完整交易上下文或scheduler计费。比如fact本轮VM Gas154，Step36日志VM Gas272、客户端Gas285；它们不是可直接比的同一Gas边界。本轮规则源代码未改，**只声明各策略在本轮同条件下Gas一致**，不宣称与Step36绝对Gas相等。上下文差异也限制完整Invoke外推，初始化区间比较仍在各组同源条件下成立。

所有正式Instance均fresh；没有复用业务实例，Module缓存保留。资源计数配平与pending0已记录；WASI独立计数、Table真实函数身份、所有业务异常/回滚、长期并发与真实节点不在本轮覆盖范围，均不标记为全面安全认证。
