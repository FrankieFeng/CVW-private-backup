# Step-22 正确性范围

所有结果限定为tested_scope_pass，不认证production_safe。

| 项目 | 实际证据 | 状态/限制 |
|---|---|---|
| WASM格式 | 原版与noData均走ValidateModule/NewModule | tested_pass |
| S1 Memory | 最终build4预检，在_start前全Memory SHA与预计算Image相等 | tested_pass，正式性能不做hash |
| Fresh与隔离 | 每次新Instance/WASI；used保护；标量写Memory→下一实例仍零；真实合约下一fresh S1 hash无前次业务修改 | tested_pass仅串行范围，无并发隔离认证 |
| 返回/Gas | compute固定计算结果、fact JSON、mint结果及owner、buyNow结果及最终owner；同输入逐对比较 | tested_pass |
| 读写/事件 | 同一初始账本clone、相同TxID/参数、实际RWSet/ContractEvent、before/after ledger hash | tested_pass，不是相同失败返回 |
| exchange | 真registry/bytecode/TxSimContext，六个真实callee全成功，逐callee结果/Gas/调用顺序 | tested_pass指定成功路径 |
| Globals | 原Global section原字节保留、Go启动/业务实际成功 | 内部mutable globals逐元素动态等价not_tested |
| Table | 原Table/Element section逐字节保留、真实Go间接调用实际执行 | 真实Table各元素函数身份not_tested；未将nullness当身份 |
| 异常/回滚/OOG | 没有专门guest错误/越界/OOG业务样本 | not_tested，不能用成功路径推出异常等价 |
| 模板只读 | restore只有Image读取，初始Image hash已记录；真实fresh实例S1一致 | 运行末全Image再次hash not_tested，不认证并发只读机制 |
| 回收 | 同owner显式Close，每实例ManagedCount回到起点，缓存尾部计数0，所有进程已退出 | tested_pass注册边界；native长期有界not_tested |

主实验+正确性预检：compute/fact/ERC各10对；顺序平衡补充各6对；exchange合计4对。所有同配对根Gas相等；成功路径Gas：compute105920，fact1585，ERC mint15449，exchange根12767294。真实exchange各子Gas以audit/comparison-*.json为准，不拿其他版本的业务参数/Gas相减。

业务状态来自Step21D真实fixture：固定公开测试公钥/逻辑member provider、BlockVersion1/ETHEREUM地址类型；不是完整节点ACL/共识/数据库认证。初始化真实执行，样本间回到同一post-init账本；ERC每配对tokenId规则唯一，A0/A1使用同一个tokenId且分别恢复账本，因此不把重复mint失败当成功。

代码保留既有CallMethod错误被GetGas错误覆盖的runtime行为，但单独记录call_error_observed；正式样本全部<nil>。此事实不免除异常路径未覆盖的限制。无Gas逻辑更改，无跨不同逻辑WASM强求Gas相等。
