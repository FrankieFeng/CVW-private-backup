# Step-26 增量收益复算结果

**全部来自Step25已有有效配对，新增运行0、编译0、独立新批次0。** 这是对原始证据的审计确认，不是一次新的时间维度重复验证。主矩阵只用Step18同源plain家族，不混入Step24B原件数据。

编号：G1=Copy（oldG1），G2=A+Copy（oldG2），G3=A+B1+Copy（oldG4）。正值=左Invoke−右Invoke。原始日志保留oldG4，CSV同时列出原编号。

## 完整Invoke直接配对

| 方法 | 对照 | 左Median/P95 ms | 右Median/P95 ms | 配对节省Median [95%CI] ms | 正向 | 原对数/批/进程 |
|---|---|---:|---:|---:|---:|---:|
| compute.bigNumCal（10000轮） | G1→G2 | 18.163/19.632 | 17.402/18.545 | 0.711 [0.303, 1.366] | 13/18 | 18/3/9 |
| compute.bigNumCal（10000轮） | G1→G3 | 19.174/21.104 | 16.924/18.589 | 1.799 [1.240, 2.439] | 17/18 | 18/3/9 |
| compute.bigNumCal（10000轮） | G2→G3 | 18.594/20.275 | 17.624/19.460 | 1.090 [0.228, 1.383] | 15/18 | 18/3/9 |
| erc721.mint | G1→G2 | 4.722/5.786 | 3.733/4.425 | 0.966 [0.521, 1.139] | 18/18 | 18/3/9 |
| erc721.mint | G1→G3 | 4.202/5.127 | 3.240/3.721 | 1.089 [0.777, 1.448] | 18/18 | 18/3/9 |
| erc721.mint | G2→G3 | 3.685/4.224 | 3.182/3.627 | 0.498 [0.214, 0.530] | 17/18 | 18/3/9 |
| fact.saveAndFindByFileHash | G1→G2 | 4.430/4.978 | 3.347/4.836 | 0.957 [0.458, 1.342] | 17/18 | 18/3/9 |
| fact.saveAndFindByFileHash | G1→G3 | 4.208/5.046 | 3.140/3.670 | 1.128 [0.919, 1.739] | 18/18 | 18/3/9 |
| fact.saveAndFindByFileHash | G2→G3 | 3.537/4.097 | 3.109/3.709 | 0.328 [0.068, 0.592] | 14/18 | 18/3/9 |

所有9项总体CI在零以上、各自原3批配对中位数为正。这支持原有三个批次和平衡调用协议下的增量收益，不是长期、顺序无关或真实节点收益认证。不同对照各有自己的进程和左右样本，绝对中位数不能跨行直接相减、相加或串接成“总收益”。

CI沿用预先登记的层次bootstrap：先抽3个batch，再在该batch抽process，将每process的2对作为整体保留，10000次、seed250027；P95与区间端点用线性分位数。18对不是18个完全独立进程。多重比较未校正，3批对环境长期波动覆盖有限。

## 批次分层

| 方法 | 对照 | 原批次 | N/进程 | 节省Median [95%CI] ms | 正向 |
|---|---|---:|---:|---:|---:|
| compute.bigNumCal（10000轮） | G1→G2 | 1 | 6/3 | 0.711 [0.510, 1.849] | 6/6 |
| compute.bigNumCal（10000轮） | G1→G2 | 2 | 6/3 | 1.013 [-0.063, 2.508] | 4/6 |
| compute.bigNumCal（10000轮） | G1→G2 | 3 | 6/3 | 0.591 [-0.264, 0.709] | 3/6 |
| compute.bigNumCal（10000轮） | G1→G3 | 1 | 6/3 | 1.593 [0.405, 2.193] | 5/6 |
| compute.bigNumCal（10000轮） | G1→G3 | 2 | 6/3 | 2.067 [1.385, 3.530] | 6/6 |
| compute.bigNumCal（10000轮） | G1→G3 | 3 | 6/3 | 1.904 [1.800, 1.904] | 6/6 |
| compute.bigNumCal（10000轮） | G2→G3 | 1 | 6/3 | 0.812 [-0.822, 1.888] | 4/6 |
| compute.bigNumCal（10000轮） | G2→G3 | 2 | 6/3 | 1.007 [-0.057, 1.573] | 5/6 |
| compute.bigNumCal（10000轮） | G2→G3 | 3 | 6/3 | 1.356 [1.055, 1.562] | 6/6 |
| erc721.mint | G1→G2 | 1 | 6/3 | 1.139 [1.139, 1.194] | 6/6 |
| erc721.mint | G1→G2 | 2 | 6/3 | 0.913 [0.743, 0.913] | 6/6 |
| erc721.mint | G1→G2 | 3 | 6/3 | 0.802 [0.233, 1.351] | 6/6 |
| erc721.mint | G1→G3 | 1 | 6/3 | 1.393 [0.846, 1.690] | 6/6 |
| erc721.mint | G1→G3 | 2 | 6/3 | 1.111 [0.836, 1.389] | 6/6 |
| erc721.mint | G1→G3 | 3 | 6/3 | 0.777 [0.665, 0.914] | 6/6 |
| erc721.mint | G2→G3 | 1 | 6/3 | 0.503 [0.366, 0.543] | 5/6 |
| erc721.mint | G2→G3 | 2 | 6/3 | 0.530 [0.496, 0.652] | 6/6 |
| erc721.mint | G2→G3 | 3 | 6/3 | 0.258 [0.175, 0.648] | 6/6 |
| fact.saveAndFindByFileHash | G1→G2 | 1 | 6/3 | 0.992 [-0.277, 1.290] | 5/6 |
| fact.saveAndFindByFileHash | G1→G2 | 2 | 6/3 | 1.090 [0.625, 1.446] | 6/6 |
| fact.saveAndFindByFileHash | G1→G2 | 3 | 6/3 | 0.922 [0.613, 1.147] | 6/6 |
| fact.saveAndFindByFileHash | G1→G3 | 1 | 6/3 | 1.058 [0.927, 1.337] | 6/6 |
| fact.saveAndFindByFileHash | G1→G3 | 2 | 6/3 | 1.537 [0.794, 1.762] | 6/6 |
| fact.saveAndFindByFileHash | G1→G3 | 3 | 6/3 | 1.068 [0.819, 1.459] | 6/6 |
| fact.saveAndFindByFileHash | G2→G3 | 1 | 6/3 | 0.270 [-0.548, 0.487] | 4/6 |
| fact.saveAndFindByFileHash | G2→G3 | 2 | 6/3 | 0.301 [0.281, 0.603] | 6/6 |
| fact.saveAndFindByFileHash | G2→G3 | 3 | 6/3 | 0.565 [0.260, 0.705] | 4/6 |

批内区间仅有3个process簇，非常探索性；批次中位数为正不等于每个批内CI均排除零。

## 运行与Module准备顺序

| 方法 | 对照 | 因素 | 实际先执行/准备的组 | N/进程 | 节省Median [95%CI] ms |
|---|---|---|---|---:|---:|
| compute.bigNumCal（10000轮） | G1→G2 | first | G1 | 9/9 | 0.715 [-0.786, 1.813] |
| compute.bigNumCal（10000轮） | G1→G2 | first | G2 | 9/9 | 0.660 [-0.360, 2.991] |
| compute.bigNumCal（10000轮） | G1→G2 | module_first | G1 | 6/3 | 1.589 [0.220, 2.508] |
| compute.bigNumCal（10000轮） | G1→G2 | module_first | G2 | 12/6 | 0.601 [0.150, 0.838] |
| compute.bigNumCal（10000轮） | G1→G3 | first | G1 | 9/9 | 2.202 [1.415, 2.439] |
| compute.bigNumCal（10000轮） | G1→G3 | first | G3 | 9/9 | 1.605 [1.120, 2.484] |
| compute.bigNumCal（10000轮） | G1→G3 | module_first | G1 | 6/3 | 2.075 [1.904, 2.193] |
| compute.bigNumCal（10000轮） | G1→G3 | module_first | G3 | 12/6 | 1.533 [1.102, 2.588] |
| compute.bigNumCal（10000轮） | G2→G3 | first | G2 | 9/9 | 0.570 [-0.538, 2.139] |
| compute.bigNumCal（10000轮） | G2→G3 | first | G3 | 9/9 | 1.537 [0.619, 1.989] |
| compute.bigNumCal（10000轮） | G2→G3 | module_first | G2 | 12/6 | 1.356 [1.007, 1.395] |
| compute.bigNumCal（10000轮） | G2→G3 | module_first | G3 | 6/3 | 0.399 [-0.822, 1.573] |
| erc721.mint | G1→G2 | first | G1 | 9/9 | 0.951 [0.297, 1.010] |
| erc721.mint | G1→G2 | first | G2 | 9/9 | 1.239 [0.234, 1.438] |
| erc721.mint | G1→G2 | module_first | G1 | 6/3 | 0.924 [0.761, 1.194] |
| erc721.mint | G1→G2 | module_first | G2 | 12/6 | 0.995 [0.297, 1.139] |
| erc721.mint | G1→G3 | first | G1 | 9/9 | 0.761 [0.536, 1.496] |
| erc721.mint | G1→G3 | first | G3 | 9/9 | 1.131 [1.005, 1.448] |
| erc721.mint | G1→G3 | module_first | G1 | 6/3 | 1.257 [0.914, 1.393] |
| erc721.mint | G1→G3 | module_first | G3 | 12/6 | 0.975 [0.777, 1.496] |
| erc721.mint | G2→G3 | first | G2 | 9/9 | 0.489 [0.301, 1.017] |
| erc721.mint | G2→G3 | first | G3 | 9/9 | 0.535 [0.182, 0.618] |
| erc721.mint | G2→G3 | module_first | G2 | 12/6 | 0.498 [0.214, 0.562] |
| erc721.mint | G2→G3 | module_first | G3 | 6/3 | 0.503 [0.496, 0.648] |
| fact.saveAndFindByFileHash | G1→G2 | first | G1 | 9/9 | 1.250 [0.412, 1.790] |
| fact.saveAndFindByFileHash | G1→G2 | first | G2 | 9/9 | 0.790 [0.367, 1.220] |
| fact.saveAndFindByFileHash | G1→G2 | module_first | G1 | 12/6 | 1.206 [0.838, 1.342] |
| fact.saveAndFindByFileHash | G1→G2 | module_first | G2 | 6/3 | 0.548 [-0.277, 1.049] |
| fact.saveAndFindByFileHash | G1→G3 | first | G1 | 9/9 | 1.154 [0.871, 1.739] |
| fact.saveAndFindByFileHash | G1→G3 | first | G3 | 9/9 | 1.101 [0.700, 1.784] |
| fact.saveAndFindByFileHash | G1→G3 | module_first | G1 | 12/6 | 1.058 [0.911, 1.308] |
| fact.saveAndFindByFileHash | G1→G3 | module_first | G3 | 6/3 | 1.186 [0.927, 1.762] |
| fact.saveAndFindByFileHash | G2→G3 | first | G2 | 9/9 | 0.315 [-0.045, 0.592] |
| fact.saveAndFindByFileHash | G2→G3 | first | G3 | 9/9 | 0.342 [0.180, 0.819] |
| fact.saveAndFindByFileHash | G2→G3 | module_first | G2 | 6/3 | 0.281 [0.260, 0.360] |
| fact.saveAndFindByFileHash | G2→G3 | module_first | G3 | 12/6 | 0.351 [-0.180, 0.705] |

每process两对交替，所以执行先后各9对；Module准备/真实init先后受原调度影响，是3/6或6/3个process（6/12或12/6对），不能写成完全平衡。

- compute的A增量：左右先执行的分层CI均跨零，Module准备先后中位数约1.589/0.601ms；不能据总体CI宣称不受顺序影响。
- compute的B1增量：A+Copy先执行及完整组合先准备的部分分层CI跨零。
- fact的A增量：A+Copy先准备分层CI跨零；B1增量中A+Copy先执行和完整组合先准备的分层CI跨零。
- ERC721三个对照的所有已采样顺序分层CI均为正；三合约完整组合相对Copy的分层CI也均为正。这是原小样本中的更强一致性，不证明任何运行顺序下都成立。
- 共7/36个顺序分层CI跨零。分层差异本身不等于已完成正式的顺序交互因果检验，不通过独立Median差推断具体机制。

## 阶段记录

| 方法 | 对照 | NewInstance节省 | Copy节省 | S0→S1节省 | S1→S2节省 | S2→S3节省 | export.Call节省 | Invoke节省（ms） |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| compute.bigNumCal（10000轮） | G1→G2 | -0.002 | -0.048 | 0.031 | 0.786 | 0.026 | 0.061 | 0.711 |
| compute.bigNumCal（10000轮） | G1→G3 | 0.010 | 0.296 | 0.322 | 0.969 | 0.539 | 0.516 | 1.799 |
| compute.bigNumCal（10000轮） | G2→G3 | 0.021 | 0.261 | 0.202 | 0.082 | 0.569 | 0.610 | 1.090 |
| erc721.mint | G1→G2 | 0.008 | 0.024 | 0.163 | 0.744 | 0.007 | -0.012 | 0.966 |
| erc721.mint | G1→G3 | 0.020 | 0.242 | 0.301 | 0.800 | -0.034 | -0.016 | 1.089 |
| erc721.mint | G2→G3 | 0.023 | 0.194 | 0.248 | 0.090 | -0.003 | 0.000 | 0.498 |
| fact.saveAndFindByFileHash | G1→G2 | -0.003 | -0.017 | -0.061 | 0.765 | 0.070 | 0.049 | 0.957 |
| fact.saveAndFindByFileHash | G1→G3 | 0.021 | 0.262 | 0.338 | 0.863 | 0.024 | 0.005 | 1.128 |
| fact.saveAndFindByFileHash | G2→G3 | 0.026 | 0.277 | 0.241 | 0.090 | -0.034 | -0.016 | 0.328 |

这里只给直接差的阶段中位数，不横向相加重建总中位数。start、CallMethod和Close全部原记录在TIMING/STAGE_EFFECTS。

S0是Invoke入口（Module/模板已准备），S1是NewInstance+Copy完成，S2是WASI.Initialize/_start及start wrapper关闭后，S3是业务/GetGas/结果处理完成且Instance关闭前。完整Invoke到每次清理defer结束，包含创建/start/业务/同步关闭。NewInstance不含随后Copy；Copy包含原校验、Memory lookup和区间copy；S0→S1还包含WASI/imports准备。模板/Module准备、真实init、账本clone/receipt写盘、末尾持久Module/Store关闭都在外，MODULE_PREPARATION单列。Module prepare还含配置/验证/Store/metadata，并不是纯编译器CPU时间。

A增量主要落在S1→S2约0.74–0.79ms；B1在A+Copy基础上的增量包含更少Copy/S0→S1及部分启动时间。compute还有Guest export窗口差异，不能全归因初始化。当前plain没有Guest A/B1细分计时，不把整个_start解释为某一个具体缓存或清零函数。NoData只替代active Data初始化，未执行原始Data后重复Copy。

## 资源与范围

复核原81正式+15预检进程均created=closed、managed/pending=0、PID/cgroup退出；原所选进程观测峰RSS 418.39MiB、Go heap Alloc 66.73MiB、线程109，未触发资源保护。本轮没有产生新的VM资源样本，RESOURCE_SUMMARY明确标为旧数据。每个进程有两个独占Store，RSS不能分解为某一组的精确成本。

## 判断与下一步

在这组原有Step18样本中，A+Copy优于Copy，B1在A+Copy之上有正增量，完整组合优于Copy。顺序分层限制和构建来源限制仍然存在，不把复算写成新增独立验证。

若优先保持SDK公共接口，A+Copy更适合优先继续：三个原批总体收益为正，API未被本优化删减。完整组合在这里更快，但B1删除GetBatchState，仅能保留为受限合约的实验分支候选。原Step24B家族匹配A/B1仍blocked，先恢复其计费/构建链再验证，不能把本家族的数值当成原件或节点收益。

Table真实函数身份、异常/OOG/回滚、真实跨合约、长期Store回收及原池并发未验证。这些结果足以选择下一轮隔离串行候选，不足以生产启用或开展原池并发节点压测。本轮无PPT、无新增机制、无生产修改。
