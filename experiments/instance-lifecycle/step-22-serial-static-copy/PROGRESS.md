# Step-22 可恢复进度

2026-10-26，Asia/Shanghai。实验：Copy方案串行性能与正确性验证。

当前阶段：已完成实测、分析与归档。主结果/平衡补充分表，限制见README/CORRECTNESS。旧阶段记录按时间保留。

## 固定范围

A0原版Fresh与A1同逻辑WASM的noData+预计算静态区间Copy。只启用既有Copy（本轮不加Arena/PB）；不使用原后台实例池，不并发访问Store，不更新版本，不修改生产VM，不push。

计划先bigNumCal/fact，小样本安全/结果/Gas/写集/事件预检通过后做三独立配对批；再评估ERC721/exchange。Module/模板一次准备和每调用分开。若Module缓存不能满足同线程所有权，记录限制，不共享未知native对象。

每进程/批次保存命令、原日志、资源、CSV和outcome。中断恢复先读本文件、state.json、outcome及活动unit，不覆盖/重复有效批次。

## 已执行

- git worktree list、实验目录清单、free -h、systemctl用户实验unit清单。
- 读取Step21B README（不放行共享Store无同步）和Step21D README（固定OS线程、native scope、独立进程结束）。

## 当前阻碍

Step21D现有Fresh每次编译，尚不适合作为Copy微小收益的稳态比较。需审查能否在同一OS线程、同一Store上串行缓存Module并逐次创建/关闭新Instance；任何native引用和清理必须归所有者。

## 下一步

读取Step21D独立模块/所有权实现以及Step16/18模板生成与恢复代码，记录POOL/所有权模型及准备成本边界。

## 串行模型登记与独立分支

审计完成，选择每对照/合约独占Store+Module的串行缓存模型；metadata缓存持久化、WASI逐次新建、不复用业务Instance。详细audit/module-model.md。独立worktree .worktrees/cvw-step22，父87eb925，实验模块只复制D/source/vm，不改生产VM。先标量所有权预检，再真实1对，再3批最多3对；不自动提高资源阈值。下一步实现统一计时与准备缓存。

即将执行 lifecycle-probe；原始命令已保存，unit=step22-lifecycle-probe，pairs=1。

完成 lifecycle-probe：{"label": "lifecycle-probe", "contract": "probe", "phase": "probe", "pairs": 1, "seed": 2200, "passed": true, "reason": "exited", "peak_rss_kib": 42988, "peak_threads": 5, "wall_s": 0.03924144900520332, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 compute-preflight；原始命令已保存，unit=step22-compute-preflight，pairs=1。

完成 compute-preflight：{"label": "compute-preflight", "contract": "compute", "phase": "preflight", "pairs": 1, "seed": 2201, "passed": true, "reason": "exited", "peak_rss_kib": 367792, "peak_threads": 40, "wall_s": 1.2499471670016646, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 fact-preflight；原始命令已保存，unit=step22-fact-preflight，pairs=1。

完成 fact-preflight：{"label": "fact-preflight", "contract": "fact", "phase": "preflight", "pairs": 1, "seed": 2202, "passed": true, "reason": "exited", "peak_rss_kib": 392308, "peak_threads": 40, "wall_s": 1.2884764769987669, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

## 缓存预检完成与测量版本冻结

标量Module缓存/三个Fresh Instance生命周期通过；build3 bigNum/fact各1对S1 Memory/业务/Gas/读写集/事件一致。现冻结build4（只补正式准备总成本和exchange可独立进程配对接口）；新版本先复核预检再测量。exchange每进程只测一个变体、一根业务，避免同进程两套调用链增加WASI线程；仍需跨进程完整结果/Gas/状态比较，未比较前不认证。所有初次和失败构建/预检保留，不混入正式数据。

即将执行 v4-lifecycle；原始命令已保存，unit=step22-v4-lifecycle，pairs=1。

完成 v4-lifecycle：{"label": "v4-lifecycle", "contract": "probe", "phase": "probe", "pairs": 1, "seed": 2200, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 38716, "peak_threads": 5, "wall_s": 0.03673174302093685, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 v4-preflight-compute；原始命令已保存，unit=step22-v4-preflight-compute，pairs=1。

完成 v4-preflight-compute：{"label": "v4-preflight-compute", "contract": "compute", "phase": "preflight", "pairs": 1, "seed": 2201, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 361620, "peak_threads": 23, "wall_s": 1.2593003019865137, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 v4-preflight-fact；原始命令已保存，unit=step22-v4-preflight-fact，pairs=1。

完成 v4-preflight-fact：{"label": "v4-preflight-fact", "contract": "fact", "phase": "preflight", "pairs": 1, "seed": 2201, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 392332, "peak_threads": 41, "wall_s": 1.3324041970190592, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 compute-batch-1；原始命令已保存，unit=step22-compute-batch-1，pairs=3。

完成 compute-batch-1：{"label": "compute-batch-1", "contract": "compute", "phase": "formal", "pairs": 3, "seed": 22001, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 372716, "peak_threads": 91, "wall_s": 1.296472675021505, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 compute-batch-2；原始命令已保存，unit=step22-compute-batch-2，pairs=3。

完成 compute-batch-2：{"label": "compute-batch-2", "contract": "compute", "phase": "formal", "pairs": 3, "seed": 22002, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 377032, "peak_threads": 82, "wall_s": 1.231975577014964, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 compute-batch-3；原始命令已保存，unit=step22-compute-batch-3，pairs=3。

完成 compute-batch-3：{"label": "compute-batch-3", "contract": "compute", "phase": "formal", "pairs": 3, "seed": 22003, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 372124, "peak_threads": 91, "wall_s": 1.278758480999386, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 fact-batch-1；原始命令已保存，unit=step22-fact-batch-1，pairs=3。

完成 fact-batch-1：{"label": "fact-batch-1", "contract": "fact", "phase": "formal", "pairs": 3, "seed": 22001, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 399600, "peak_threads": 108, "wall_s": 1.318019157013623, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 fact-batch-2；原始命令已保存，unit=step22-fact-batch-2，pairs=3。

完成 fact-batch-2：{"label": "fact-batch-2", "contract": "fact", "phase": "formal", "pairs": 3, "seed": 22002, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 416892, "peak_threads": 107, "wall_s": 1.3786236890009604, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 fact-batch-3；原始命令已保存，unit=step22-fact-batch-3，pairs=3。

完成 fact-batch-3：{"label": "fact-batch-3", "contract": "fact", "phase": "formal", "pairs": 3, "seed": 22003, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 407524, "peak_threads": 125, "wall_s": 1.3750976330193225, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 v4-preflight-erc721；原始命令已保存，unit=step22-v4-preflight-erc721，pairs=1。

完成 v4-preflight-erc721：{"label": "v4-preflight-erc721", "contract": "erc721", "phase": "preflight", "pairs": 1, "seed": 2201, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 387856, "peak_threads": 23, "wall_s": 1.40553037400241, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 erc721-batch-1；原始命令已保存，unit=step22-erc721-batch-1，pairs=3。

完成 erc721-batch-1：{"label": "erc721-batch-1", "contract": "erc721", "phase": "formal", "pairs": 3, "seed": 22001, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 409528, "peak_threads": 91, "wall_s": 1.4082256430119742, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 erc721-batch-2；原始命令已保存，unit=step22-erc721-batch-2，pairs=3。

完成 erc721-batch-2：{"label": "erc721-batch-2", "contract": "erc721", "phase": "formal", "pairs": 3, "seed": 22002, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 392188, "peak_threads": 92, "wall_s": 1.4391914590087254, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 erc721-batch-3；原始命令已保存，unit=step22-erc721-batch-3，pairs=3。

完成 erc721-batch-3：{"label": "erc721-batch-3", "contract": "erc721", "phase": "formal", "pairs": 3, "seed": 22003, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 408184, "peak_threads": 57, "wall_s": 1.426872394979, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 exchange-preflight-A0；原始命令已保存，unit=step22-exchange-preflight-A0，pairs=1。

完成 exchange-preflight-A0：{"label": "exchange-preflight-A0", "contract": "exchange", "phase": "preflight", "pairs": 1, "seed": 2201, "single": "A0", "passed": true, "reason": "exited", "peak_rss_kib": 755268, "peak_threads": 158, "wall_s": 3.8014253269939218, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 exchange-preflight-A1；原始命令已保存，unit=step22-exchange-preflight-A1，pairs=1。

完成 exchange-preflight-A1：{"label": "exchange-preflight-A1", "contract": "exchange", "phase": "preflight", "pairs": 1, "seed": 2201, "single": "A1", "passed": true, "reason": "exited", "peak_rss_kib": 755616, "peak_threads": 142, "wall_s": 3.9282388639985584, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 exchange-batch-1-A0；原始命令已保存，unit=step22-exchange-batch-1-A0，pairs=1。

完成 exchange-batch-1-A0：{"label": "exchange-batch-1-A0", "contract": "exchange", "phase": "formal", "pairs": 1, "seed": 22001, "single": "A0", "passed": true, "reason": "exited", "peak_rss_kib": 751016, "peak_threads": 142, "wall_s": 3.836007678997703, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 exchange-batch-1-A1；原始命令已保存，unit=step22-exchange-batch-1-A1，pairs=1。

完成 exchange-batch-1-A1：{"label": "exchange-batch-1-A1", "contract": "exchange", "phase": "formal", "pairs": 1, "seed": 22001, "single": "A1", "passed": true, "reason": "exited", "peak_rss_kib": 777488, "peak_threads": 159, "wall_s": 3.8825091980106663, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 exchange-batch-2-A1；原始命令已保存，unit=step22-exchange-batch-2-A1，pairs=1。

完成 exchange-batch-2-A1：{"label": "exchange-batch-2-A1", "contract": "exchange", "phase": "formal", "pairs": 1, "seed": 22002, "single": "A1", "passed": true, "reason": "exited", "peak_rss_kib": 762592, "peak_threads": 176, "wall_s": 3.9237182770157233, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 exchange-batch-2-A0；原始命令已保存，unit=step22-exchange-batch-2-A0，pairs=1。

完成 exchange-batch-2-A0：{"label": "exchange-batch-2-A0", "contract": "exchange", "phase": "formal", "pairs": 1, "seed": 22002, "single": "A0", "passed": true, "reason": "exited", "peak_rss_kib": 736984, "peak_threads": 176, "wall_s": 3.8547536480182316, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 exchange-batch-3-A0；原始命令已保存，unit=step22-exchange-batch-3-A0，pairs=1。

完成 exchange-batch-3-A0：{"label": "exchange-batch-3-A0", "contract": "exchange", "phase": "formal", "pairs": 1, "seed": 22003, "single": "A0", "passed": true, "reason": "exited", "peak_rss_kib": 763928, "peak_threads": 176, "wall_s": 3.873115552996751, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 exchange-batch-3-A1；原始命令已保存，unit=step22-exchange-batch-3-A1，pairs=1。

完成 exchange-batch-3-A1：{"label": "exchange-batch-3-A1", "contract": "exchange", "phase": "formal", "pairs": 1, "seed": 22003, "single": "A1", "passed": true, "reason": "exited", "peak_rss_kib": 779536, "peak_threads": 166, "wall_s": 3.801613065006677, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。


## 阶段完成记录（2026-10-26）

1. 审计完成：Step16 prepareStaticMemory/restore仅格式化复制；Step18沿用相同pool路径，但本轮不取A/P变体。Step21D owner/ManagedScope及原Gas映射未变。
2. 预检完成：最终build4标量缓存生命周期；compute/fact/ERC各1对S1全Memory哈希；exchange分进程各1根，真实3初始化+根及6子调用。所有receipt等价。
3. 正式完成：compute/fact/ERC各3个独立进程、每进程3对；exchange3个独立配对批、每条件1进程1根。未运行更多/原后台池/节点/并发实验。
4. 数据分析完成：scripts/analyze.py生成summary、逐对差、按批汇总、correctness、resource_summary等；配对bootstrap三批后重采样slots，10000次，seed22026026。

所有24个测试进程（含探索预检）正常退出；未触发资源guard，最大合并峰值约765.62MiB/176线程。观察到Store存活时每新WASI调用后线程数增多：单合约最后125、exchange176，缓存关闭后约13/16；不认定长期资源已受控，因此停止扩大样本。当前无Step22活动unit。

完整Invoke的95%CI均跨零。S1静态初始化有正向证据；不能将本轮小样本写成稳定生产收益。exchange第三批完整Invoke反向，已保留。

当前阻碍：Table真实函数身份、内部Globals动态比较、异常/OOG路径未验证；精确native构建来源与长寿命Store资源有界性未闭合。

下一条待执行：完成README/AUDIT/CORRECTNESS/运行说明和独立分支提交；不再启动实验。恢复先读本记录及outcome，不重复已有有效批次。


## 新发现：顺序敏感性补充登记（不改主实验）

主实验每单合约A1先7对、A0先2对，compute完整Invoke反向恰好出现在A0先两对；fact/ERC不符合这一统一关系，不能以顺序解释所有反向。此新混杂值得最小补充，撤销“只归档、不再测试”的下一步，单列顺序平衡补充，不替换/合并主结果。

保持build4/Gas/输入/资源阈值，compute/fact/ERC各3独立进程×2对（每进程5个实例，少于已通过的7个）。每批恰好一对A1先、一对A0先，seed22003/22004/22003；种子只按已知顺序选择，不按耗时。保持单进程预算不增加，exchange不补跑。输出balanced_*独立表格，不能选择性丢弃主实验反向样本。

下一条命令：python3 -B scripts/balanced_suite.py。任何guard失败立即停止。数据每进程仍自动保存。

即将执行 compute-balanced-batch-1；原始命令已保存，unit=step22-compute-balanced-batch-1，pairs=2。

完成 compute-balanced-batch-1：{"label": "compute-balanced-batch-1", "contract": "compute", "phase": "formal", "pairs": 2, "seed": 22003, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 357712, "peak_threads": 40, "wall_s": 1.1113864250073675, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 compute-balanced-batch-2；原始命令已保存，unit=step22-compute-balanced-batch-2，pairs=2。

完成 compute-balanced-batch-2：{"label": "compute-balanced-batch-2", "contract": "compute", "phase": "formal", "pairs": 2, "seed": 22004, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 354304, "peak_threads": 80, "wall_s": 1.1480331339989789, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 compute-balanced-batch-3；原始命令已保存，unit=step22-compute-balanced-batch-3，pairs=2。

完成 compute-balanced-batch-3：{"label": "compute-balanced-batch-3", "contract": "compute", "phase": "formal", "pairs": 2, "seed": 22003, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 358380, "peak_threads": 57, "wall_s": 1.1885299990244675, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 fact-balanced-batch-1；原始命令已保存，unit=step22-fact-balanced-batch-1，pairs=2。

完成 fact-balanced-batch-1：{"label": "fact-balanced-batch-1", "contract": "fact", "phase": "formal", "pairs": 2, "seed": 22003, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 381072, "peak_threads": 59, "wall_s": 1.3259820599923842, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 fact-balanced-batch-2；原始命令已保存，unit=step22-fact-balanced-batch-2，pairs=2。

完成 fact-balanced-batch-2：{"label": "fact-balanced-batch-2", "contract": "fact", "phase": "formal", "pairs": 2, "seed": 22004, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 394956, "peak_threads": 74, "wall_s": 1.4088612889754586, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 fact-balanced-batch-3；原始命令已保存，unit=step22-fact-balanced-batch-3，pairs=2。

完成 fact-balanced-batch-3：{"label": "fact-balanced-batch-3", "contract": "fact", "phase": "formal", "pairs": 2, "seed": 22003, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 387892, "peak_threads": 72, "wall_s": 1.2760316469939426, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 erc721-balanced-batch-1；原始命令已保存，unit=step22-erc721-balanced-batch-1，pairs=2。

完成 erc721-balanced-batch-1：{"label": "erc721-balanced-batch-1", "contract": "erc721", "phase": "formal", "pairs": 2, "seed": 22003, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 405320, "peak_threads": 57, "wall_s": 1.4283973400015384, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 erc721-balanced-batch-2；原始命令已保存，unit=step22-erc721-balanced-batch-2，pairs=2。

完成 erc721-balanced-batch-2：{"label": "erc721-balanced-batch-2", "contract": "erc721", "phase": "formal", "pairs": 2, "seed": 22004, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 406260, "peak_threads": 23, "wall_s": 1.4470790409832262, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。

即将执行 erc721-balanced-batch-3；原始命令已保存，unit=step22-erc721-balanced-batch-3，pairs=2。

完成 erc721-balanced-batch-3：{"label": "erc721-balanced-batch-3", "contract": "erc721", "phase": "formal", "pairs": 2, "seed": 22003, "single": "", "passed": true, "reason": "exited", "peak_rss_kib": 405612, "peak_threads": 91, "wall_s": 1.4513848459755536, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "all_owned_processes_stopped": true}；日志/资源/receipt已落盘。下一步读取outcome后按登记阶段继续。


## 最终数据分析与归档完成

平衡补充9个进程全部通过：各单合约3批×2对，每批两种先后各1对，build4不变。总33个测试进程无残留、所有正式进程使用同一冻结binary；audit/final-health.json验证完成。没有WSL重启或资源阈值触发。

结果：平衡组compute/erc721分别6/6正向，配对Median节省0.7384055/0.9031495ms；fact5/6正向、第二批近零。主实验完整Invoke CI全部跨零，exchange第三批反向15.764944ms；全部保留。主实验/平衡补充不混合。阶段和正确性原始数据、prepare/module/cache成本、source.diff、原始日志/receipt、版本/哈希与not_tested边界全部写入。

审计修正：仅compute负向与A0先共现，fact/ERC不满足；发现并明确纠正此前概括，未认定顺序为统一原因。

当前仍阻碍生产/扩大：Store长寿命线程/RSS有界性、native精确构建来源、Table真实身份和异常路径。未加Copy以外优化，未执行默认池/并发/节点实验。

下一步只在独立Step22分支提交本目录、同步CVW可见镜像；不推送、不启动更多测试。完成后读取README/RUNNING复现，已有label不可覆盖。

实验源与脚本冻结提交：4160b271fda1bba587dd0098d7069e9e74b5a907。仅本分支；仓库未配置作者，采用每条commit命令的Codex <codex@local>身份，未改全局Git配置。下一步提交结果/报告，不push。
