# Step-33 全合约覆盖结果

独立分支 experiment/step33-full-contract-coverage，源码快照 131915d666a4a233a0ff3307d8b055ed88871244，父7eccc36e。正式执行build3，与快照Go源码逐文件hash一致。只运行串行Fresh VM，没有原池并发、真实节点E2E、B1或远程推送。

识别 8 个独立部署业务合约家族：bigInput, compute, erc721, exchange, fact, identity, itinerary, raffle。扫描路径、所有WASM候选和辅助/源码样例分别登记，副本或构建变体不重复计作独立合约。没有把仅有WASM文件当成真实节点已部署证明。

本轮新增 30/30 个方法完成3批×10四组区块，共 900 区块、3600 次正式目标Invoke、1920 个独立测试进程。另保留Step32六方法，不重跑、不合并统计。八合约全部至少一个业务方法完成四组对照；总计36个业务方法完成，identity.callerAddress一个业务入口blocked。不是所有公开probe和所有输入路径均已认证。

已归档失败预检 1 个进程：accountTokens 原后端缺 SelectObject，VM返回nil pointer；实现真实账本范围迭代后重试通过。未计入正式统计。另有一次监控读取/proc与进程正常退出竞态，从既有PASS日志/收据/空cgroup恢复，未重复执行。

## 数据与复算

- RESULTS.md：30方法四组Invoke与直接效应；FULL_CONTRACT_MATRIX.csv：Step32+Step33完整矩阵（保留source/branch/commit/WASM SHA）；SUMMARY/BATCH_SUMMARY/STRATIFIED_EFFECTS：总体、逐批和顺序。
- TIMING.csv：包含init/setup/target原始计时，主统计仅phase=formal、valid_block=True、depth=0、tx_id=step33-<case>-fixed。每组N30，不能把init/setup也算正式样本。
- PAIRED_EFFECTS.csv：五个直接效应；INTERACTION_ANALYSIS.csv：原符号交互。置信区间未作多重比较校正，30方法/同合约多入口非独立合约重复，结论为筛选性证据。
- INPUT_MANIFEST、inputs/*-case.json：冻结输入与真实前置调用；CORRECTNESS.csv及每区块收据/重建账本；MODULE_PREPARATION：模板/编译独立成本。

## 收益判断

“跨批正向”指直接节省95% CI下界>0且三批中位效应均正，非生产安全或普遍阈值。

- A-only 相对Fresh跨批正向：bigInput_inputSize,bigInput_inputSizeMulti,identity_addWriteList,identity_alterAdminAddress,identity_removeWriteList,identity_isApprovedUser,identity_address,itinerary_save,itinerary_queryHistory,itinerary_saveAndQueryHistory,raffle_registerAll,raffle_query,raffle_raffle,raffle_registRaffle,fact_save,fact_findByFileHash,erc721_balanceOf,erc721_ownerOf,erc721_getApproved,erc721_tokenURI,erc721_tokenMetadata,erc721_accountTokens,erc721_tokenLatestTxInfo,erc721_name,erc721_symbol,erc721_setApprovalForAll2,erc721_approve,erc721_transferFrom,erc721_mint2。
- Copy-only 相对Fresh跨批正向：identity_alterAdminAddress,identity_address,raffle_registerAll,raffle_query,raffle_raffle,erc721_ownerOf,erc721_accountTokens,erc721_name,erc721_symbol,erc721_setApprovalForAll2,erc721_approve,erc721_transferFrom,erc721_mint2。
- A+Copy 相对Fresh跨批正向：bigInput_inputSize,bigInput_inputSizeMulti,bigInput_ioHeavy,identity_addWriteList,identity_alterAdminAddress,identity_removeWriteList,identity_isApprovedUser,identity_address,itinerary_save,itinerary_queryHistory,itinerary_saveAndQueryHistory,raffle_registerAll,raffle_query,raffle_raffle,raffle_registRaffle,fact_save,fact_findByFileHash,erc721_balanceOf,erc721_ownerOf,erc721_getApproved,erc721_tokenURI,erc721_tokenMetadata,erc721_accountTokens,erc721_tokenLatestTxInfo,erc721_name,erc721_symbol,erc721_setApprovalForAll2,erc721_approve,erc721_transferFrom,erc721_mint2。
- A+Copy 相对两种单项的直接增量也均跨批正向：bigInput_inputSize,identity_isApprovedUser,identity_address,itinerary_save,itinerary_saveAndQueryHistory,raffle_registerAll,raffle_raffle,fact_findByFileHash,erc721_getApproved,erc721_accountTokens,erc721_name,erc721_symbol,erc721_setApprovalForAll2,erc721_approve,erc721_mint2。
- raw交互CI全正（抵消）：erc721_ownerOf；raw交互CI全负（额外协同）：无。未跨零也需结合批次，不把CI跨零称确定机制。
- 先后分层中至少一个中位效应不正：bigInput_inputSizeMulti.Copy,bigInput_ioHeavy.A,bigInput_ioHeavy.Copy,erc721_balanceOf.Copy_given_A,identity_removeWriteList.Copy,itinerary_queryHistory.Copy,itinerary_queryHistory.Copy_given_A；详细方向和N见STRATIFIED_EFFECTS，不能仅总体结果忽视顺序。

独立合约层面覆盖8/8足以形成当前冻结工作负载的阶段性全合约矩阵；不代表所有输入、所有业务方法、真实数据库、并发或端到端普遍受益。后续E2E优先选择跨批与顺序均支持、正确性一致的方法，仍必须经过独立Store生命周期准入。Step32已有buyNow结论按原来源引用，不用本轮其他方法填补其不稳定收益。

## 资源与局限

已通过进程观测最大RSS 529.3 MiB，线程109。RSS为25ms采样与边界峰值；Go heap为目标边界runtime/metrics采样，不是native内存或全程精确峰值。所有正式进程必须PID结束、cgroup空、manager创建/关闭相等、in-flight=0、managed pending=0，详见RESOURCE_SUMMARY。进程退出是本轮有界回收边界，不证明长期Store复用或原池安全。

Table真实函数身份、通用异常/回滚：not_tested。init/setup与各组目标真实执行业务，四组Gas、返回、读写集、事件和最终账本一致；此范围之外不标pass。identity.callerAddress守卫限制没有绕过。无固定子调用返回值。

## 运行与回滚

先读取PROGRESS.md、state.json与已有systemd unit，不能重复启动活动实验。实际工作树 .worktrees/cvw-step33；同环境复算：

```sh
python3 scripts/analyze.py
python3 scripts/stage_report.py
python3 scripts/finalize_docs.py
python3 scripts/recommend.py
```

有界运行脚本scripts/experiment.py alignment/preflight/formal均使用已保存清单；formal会跳过有效已完成区块，不能把再次运行的skip当新实验。新独立实验须另建目录/标签和重新登记二进制。build脚本要求本地固定native（SHA在environment.json），不打包替换未知so。

未修改生产VM；回退仅停止state.json所列step33自有unit并检查cgroup，保留本分支/worktree和数据即可，切勿删除既有历史目录或reset主工作区。报告与delivery副本不等于在主分支合并。


补充：原始主数据为raw_logs/标签日志、command/outcome/收据；source/vm/default.log*保留logger辅助输出及复制的旧片段，不用于本轮筛选统计。预检含build2与后端补齐后的build3，所有正式调用统一build3；各进程二进制SHA见command.json。可用python3 scripts/recompute.py一键复算全部派生表，旧来源保持只读。

归档未包含可执行.test与native so；本地工作树保留它们。重建时须使用固定SHA native库、现有Go1.24.1诊断工具链和Step21C/18依赖工作树，不能自动替换库。build.py使用新的build标签以避免覆盖历史；run.py支持E33_BINARY_LABEL指定新构建，旧有效标签会跳过，新的独立复现须登记新目录/标签与输入路径。完整环境还包括audit/EXTERNAL_MODULE_SOURCE.json中Step21C核心依赖提交32d257b62cbaedbefd6112ddf1badb4aee2b413f。
