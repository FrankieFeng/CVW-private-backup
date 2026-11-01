# 正确性及未完成项

## 已通过

- 同一个Go测试二进制，原始库、重建未修复库、补丁库的Step34Serial：compute.bigNumCal Gas均120027，buyNow Gas均12612158；输入、初始/最终账本hash、返回、完整读写集、事件及各层调用Gas逐字段相等。
- buyNow真实6子调用：identity.addWriteList、identity.isApprovedUser两次、erc721.mint、erc721.setApprovalForAll2、erc721.transferFrom。未使用固定返回或模拟子合约。
- 两组真实节点各2轮compute+buyNow，业务成功且取得提交交易及rwset。compute Gas120135、buyNow12620048，两组逐轮一致。节点与原型上下文不同，**不把两类Gas相减判断回归**。
- 节点事件/结果/Gas、提交读写集规范化后相等。规范化仅去除TxID及业务latestTxInfo中的TxId/BlockHeight等交易元数据；原始值全部保留。不宣称两个独立节点原始全账本hash完全一致，未额外导出全账本。
- Step34Owner在两组均通过：缓存Module跨独立Store、幂等关闭、取消/故障路径及Reset/Stop；其历史测试包含GC用于验证Finalizer，不作为线程修复手段。本轮节点资源准入未调用/gc或/scavenge。
- 两组节点Manager ResetAllPool空闲/在途compute/在途buyNow通过，期间新请求成功排队执行；节点Owner最终配平并退出。

具体字段复核见 `audit/correctness-details.json`、`audit/node-call-details.json`，复算脚本遇到任何不一致将失败。

## 异常与缺口

| 项目 | 实际状态 |
|---|---|
| 补丁组在途Reset+SIGTERM | **失败**：VM stop_finished、Owner Store2/2 Instance1/1后，historydb CommitBlock后台写入已关闭LevelDB panic，进程exit2 |
| 未修复组相同Stop | 此次exit0；客户端也丢失RPC响应，不能称交易确认成功 |
| 新库导致panic的因果 | 未证实；堆栈属于ChainMaker账本Store，不能与Wasmer native Store混同 |
| 重启/重复buyNow失败回滚 | 未修复组在补丁异常结果返回前已启动，正常完成；失败交易已提交、ownerOf前后不变。补丁组因停止条件未启动，**not_tested** |
| 补丁组完整异常回滚与重启矩阵 | 未完成，不能用Owner单测代替真实节点级覆盖 |
| 真实Table函数身份 / 网络共享Runtime长寿命 | not_tested，不能标通过 |
| 长时间资源与并发压力 | 未执行，不作推断 |

没有更改Gas规则或合约业务来使结果相等。因安全停止而缺失的验证保留为缺失，不能作为优化负收益或业务失败证据。
