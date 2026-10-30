# 正确性

CORRECTNESS.csv：12完整四组区块，48根全部通过。G0 Fresh、G1 A、G2 Copy、G3 A+Copy，Gas/返回/RWSet/事件/初末账本严格相同。buyNow每根真实调用identity.addWriteList、identity.isApprovedUser两次、ERC721.mint、setApprovalForAll2、transferFrom；12根共72子调用，全保留每层Gas与状态，不累加嵌套累计Gas。

HISTORICAL_SEMANTIC_CHECK.csv逐个组与Step32同WASM/输入/TxID原收据比较通过，包括真实业务Gas/写集/事件/账本；仅作语义复核，不比较旧时间。A和Copy Guest原件哈希冻结，未构建新Guest/删SDK接口/改Gas规则。

Go故障与真实业务异常均检查BeforeHash==AfterHash；故障后恢复收据仍执行真实业务。关闭/取消错误不会把未提交交易写入账本。native不可安全注入的OOM/析构失败未测，仅验证Go层相应回滚边界；不能标作真实native失败已全部认证。

真实Table函数身份、所有任意输入、原池并发、在线合约升级及长期资源释放：not_tested。日志内原recipe的table字段未改成通过。本轮只证明已覆盖路径，不证明生产普遍正确。
