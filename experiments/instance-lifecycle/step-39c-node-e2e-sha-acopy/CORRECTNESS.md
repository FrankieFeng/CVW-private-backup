# 正确性与资源核查

360/360正式根交易成功提交，无失败、超时或剔除样本。每方法每组30笔、3个独立批次；不能称为30个独立实验。跨组同一批/位置使用同TxID及输入，分属独立等价账本，唯一性按(run,TxID)判断，不把跨账本相同TxID误作同一笔提交。

scripts/finalize.py 对九个方法×批次四组比较，27个优化组对照全部通过：精确ContractResult（含Gas/返回值/事件）、TxID、完整读集和写集所有字段、初始业务投影及最终业务KV投影一致。仅对读写集合和KV列表排序，不删除字段、不替换历史时间。audit/strict-business-parity.json保留结果。历史parity.py还会归一化时间/TxID，其结果仅辅助；本轮主正确性依据是更严格的精确比较。

hashCal Gas=120127；bigInput.inputSize Gas=52562；buyNow Gas=12620047或12620048，随本轮tokenId长度变化，同批同位置四组完全相等，不把跨输入的1 Gas变化视为优化错误。buyNow共120笔根调用、720次正式真实下游调用；逐TxID依次为identity.addWriteList、identity.isApprovedUser两次、erc721.mint、erc721.setApprovalForAll2、erc721.transferFrom。六次子调用方法/顺序/深度/Gas/结果码跨四组也精确比较通过；嵌套Gas为累计传播计数，不相加充当总Gas。

初始六个部署账本按同源plain/A分别冻结；每组拷贝自己的等价seed，部署成本在测量外。buyNow每笔tokenId1001..1010；预热Query用9001，不提交其写集。正式每笔真实读写集可查，最终写键值由节点数据库读取核对；36次独立只读重启检查全部360笔TxID、区块高度及结果和最终业务投影。不同组的系统合约登记含不同WASM，因此不宣称整个LevelDB字节相同；也未穷举没有写入的所有业务键。

三种失败export交易均实际提交为失败、无写集，已验证业务KV投影不变，日志保留。Manager Reset/Stop、在途处理和容量拒绝见SMOKE.md。真实节点不允许同版本升级，测试证明此入口拒绝且未错误命中；这与39B内部registry同版本换码隔离证据分开报告。

107个节点进程（含部署、Smoke、正式和重启）均退出码0、Store/Instance配平、native managed_pending=0、Artifact Stop后0项0字节，无共享基础设施停止标记。RSS正式峰值1161.727MiB，全部峰值1310.508MiB，线程峰值46；未提高1536MiB/220线。RESOURCE_SUMMARY.csv的GoHeap是已有阶段事件的边界采样峰值，不是连续全局Heap最大值；RSS是监控轮询峰值。缓存热态E3通常1项，buyNow3项/14125044字节，额外不可变WASM持有有界，但不声称无内存成本或已证明长期无泄漏。

所有节点实际加载patched native SHA256=56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc；Runtime Clone、输入SHA、安全Fresh Owner、Selector补丁和Core排空均保留。node4实际编译VM源哈希与交付源逐项核对；client.go独立编译，后续管理功能变更不属于node依赖。源差异只有4个VM实验文件的观测/收集调整，详见audit/vm-relative39b.diff；Owner、Copy实现、wasmer-go及Gas未修改。
