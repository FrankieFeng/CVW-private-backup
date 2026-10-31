# 正确性与Gas

真实节点Baseline/Copy同源Step34/Step18 P0 A0 WASM，输入顺序和业务状态等价，独立初始账本。同一链配置、发送者测试证书、SDK与Gas规则；实际构建哈希见命令JSON。节点不与旧串行实验绝对Gas基线强行合并。

| 目标 | Baseline客户端Gas | Copy客户端Gas | 返回/状态检查 |
|---|---:|---:|---|
| compute.bigNumCal |120135|120135|success bigNumCal: 607723520|
| fact.saveAndFindByFileHash |285|285|fileHash/fileName/time JSON，存证写集与事件一致|
| erc721.mint |412|412|mint success，ownerOf(1001)=from，5条写集一致|
| exchange.buyNow |12620047|12620047|buyNow success，六真实下游，ownerOf(1002)=to，11条写集、3事件一致|
| duplicate buyNow |3004775|3004775|客户端状态4，失败提交交易写集0，未把失败算成功|

VM内Gas与客户端最终Gas是两个边界：原Scheduler在RunContract之后追加RWSet/Event Gas（node/module/core/common/scheduler/run_vm.go:272,287）。不把嵌套子调用累计Gas相加。本轮未改Gas逻辑。

COPY_PARITY.csv及scripts/analyze.py复算同输入业务返回、Gas、已提交Guest命名空间读写集和事件。NFT latestTxInfo只归一化TxId/BlockHeight；事件只移除交易关联tx_id，不删除业务event_data。原始未归一化数据始终保留。Native部署管理命名空间和独立链区块哈希不强求相等。最终账本检查是从所有已记录提交写集重放得到的Guest业务子集，另有真实ownerOf查询；不冒充全链所有键完整导出。

成功buyNow共10次根调用，每次均在相同TxID下真实进入identity.addWriteList、两次isApprovedUser、erc721.mint、setApprovalForAll2、transferFrom。原始node log和CORRECTNESS_CHECKS.csv保留检查；失败重复交易在mint处提前失败，不虚构后两次调用。

复用模式未启用，R0拒绝；没有与历史Reuse Gas差异混合。未测Table函数身份、全部异常/回滚路径、真实节点合约升级/链配置Reset及任意native失败。本轮覆盖的业务回滚为重复token和夹具missing方法，不能扩展为所有异常均已验证。
