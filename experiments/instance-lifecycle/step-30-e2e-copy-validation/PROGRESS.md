# Step-30可恢复进度
2026-10-27，父f1609b80，独立experiment/step30-e2e-copy-validation。
当前审计：实际Step20目录为step-20-e2e-performance-attribution，旧e20-e2e-copy-attribution路径未找到。SDK边界与资源停止原始文件可恢复。
没有启动节点/客户端/编译/新请求。旧17/20保存节点未接入21B之后固定owner/managed finalizer安全协议；必须先完成安全准入，不能直接按旧成功smoke放行。
下一步：形成AUDIT.md并冻结历史证据；仅离线重算旧原始样本。所有旧文件保持不变，不push、不修改生产。

阶段1审计已完成并保存AUDIT（新执行前形成），确认为SendRequestSync/节点提交结果等待；原e20路径已更名，旧17/20binary/native/WASM文件SHA复核全部匹配。旧节点模块/Finalizer不在根锁完整所有权内，node-step17/19/19-reuse未发现ManagedOwner集成；21B边界不满足，因此阶段2/3新smoke与正式三批未启动，G0/G1/G2均blocked。没有提高RSS限或临时重写节点运行时。
离线原始证据完成：Step20两轮207响应+1未知pending，88正式完整对+1Copy未配对，3对旧smoke；全部207唯一TxID/Instance及单根VM/Gas106028核验。旧17原stdout重读5248热响应/6008根Invoke，382 TxID重执行，均workers4。不得把旧数据当Step30新样本。
交付README/AUDIT/RESULTS/TIMING_BOUNDARIES/E2E_SAMPLES/PAIRED_EFFECTS/THROUGHPUT/CORRECTNESS/RESOURCE_SUMMARY/原始历史副本及只读复算脚本均完成。新样本0、新CI/时延/TPS空值+blocked；Go heap/独立提交窗口/原factory计时缺失，没有编造。旧RSS峰2564.707MiB，按原2560MiB软限记录，不代表新20对必然超限。
verify通过：历史SHA未改变；本轮无节点unit/客户端/RPC，未触碰现有其他监听端口/节点。待办仅本地commit与IDE镜像；后续需独立完成节点owner/回收的安全适配与有界资源准入，再恢复本实验，不属于本轮临时实现。

补充审计完成：追踪CommitBlock.PutBlock→BlockInfo→EventSubscriber→TxResultDispatcher→RPC，证实同步成功返回覆盖本地PutBlock返回后的结果通知，不只是AddTx ACK。仍无逐笔提交精确时间窗，不冒称独立提交TPS。Step17原source_hashes的11个源码/依赖文件逐项匹配当前可恢复工作树，已冻结step17-snapshot-source-check.json；编译源与当前审计对象没有默默换版本。
本轮审计/历史复算已完成；新E2E因用户指定安全边界未满足而未执行，属于明确部分交付，不能称完成新性能验证。首个本地审计commit366516b7，全部历史未改。后续仅本地保存/镜像，不运行节点，不push。需要进入新E2E时应先独立交付可验证的节点生命周期适配及资源准入，而非直接修改本报告中的blocked标签。
