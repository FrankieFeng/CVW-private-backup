# Step-23 可恢复进度

2026-10-26 Asia/Shanghai。分支experiment/step23-buy-now-gas-attribution，父394d291。

当前：最终v2实测与分析完成；受影响v1独立隔离。只剩本地提交/镜像，不运行更多guest。主结果见README与verification.json，不测TPS。

已读：Step21E 507310c原Gas报告/源码/receipt/trace；Step22 394d291源码及真实跨合约数据。已创建独立worktree，不改生产VM/历史目录，不push。

初步条件：21E buyNow是R0从真实init后复用同合约Instance对比R1逐子调用Fresh，并非两次root冷热对比；R0的ERC721第6子调用已执行过mint/approval。21E与22相同业务参数及初始账本，但root TxID分别step21c-buy-001与step22-exchange-000，不应直接比较绝对Gas。

待做：冻结历史证据和条件表；在Step22串行缓存Module路径移植21E只读Gas探针，保留守卫，逐过程最多三初始化+一根六callee。R0保留原guest历史，R1 Fresh，Copy单列；每条件独立进程。

资源边界沿用RSS1536MiB/线程220软限，MemoryMax2GiB/TasksMax256/Go45s/进程60s，全机available8GiB/swap1GiB。禁止增大每进程root数。

下一步：静态审计Gas传播与RWSet获取是否只读，再实现夹具。每进程命令/outcome/原日志即时保存；失败即STOP，不重复已完成label。恢复先读取本文件、state和活动unit。不要自动改代理/WSL/IDE。

构建build01未执行guest：Step22 Git快照遗漏packaged/lib中6个占位Go文件。已从原执行worktree按Step22 audit/source_hashes逐件核对恢复，记录audit/restored_packaging.json；不更新依赖，不改历史文件。准备build02。

开始 preflight-R0-off，condition=R0 probe=off stage=preflight block=0；unit=step23-preflight-R0-off，每进程最多1根。

结束 preflight-R0-off：{"label": "preflight-R0-off", "condition": "R0", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 745348, "peak_sampled_threads": 57, "wall_s": 4.017206246004207, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 preflight-R0-on，condition=R0 probe=on stage=preflight block=0；unit=step23-preflight-R0-on，每进程最多1根。

结束 preflight-R0-on：{"label": "preflight-R0-on", "condition": "R0", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 715592, "peak_sampled_threads": 57, "wall_s": 3.954709971003467, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 preflight-R1-off，condition=R1 probe=off stage=preflight block=0；unit=step23-preflight-R1-off，每进程最多1根。

结束 preflight-R1-off：{"label": "preflight-R1-off", "condition": "R1", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 764556, "peak_sampled_threads": 159, "wall_s": 4.0508037870167755, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 preflight-R1-on，condition=R1 probe=on stage=preflight block=0；unit=step23-preflight-R1-on，每进程最多1根。

结束 preflight-R1-on：{"label": "preflight-R1-on", "condition": "R1", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 770704, "peak_sampled_threads": 176, "wall_s": 4.097546250006417, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 preflight-C1-off，condition=C1 probe=off stage=preflight block=0；unit=step23-preflight-C1-off，每进程最多1根。

结束 preflight-C1-off：{"label": "preflight-C1-off", "condition": "C1", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 748520, "peak_sampled_threads": 172, "wall_s": 4.062724608986173, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 preflight-C1-on，condition=C1 probe=on stage=preflight block=0；unit=step23-preflight-C1-on，每进程最多1根。

结束 preflight-C1-on：{"label": "preflight-C1-on", "condition": "C1", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 767348, "peak_sampled_threads": 142, "wall_s": 3.99500487500336, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 lifecycle-b1-R0，condition=R0 probe=on stage=lifecycle block=1；unit=step23-lifecycle-b1-R0，每进程最多1根。

结束 lifecycle-b1-R0：{"label": "lifecycle-b1-R0", "condition": "R0", "probe": "on", "stage": "lifecycle", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 739732, "peak_sampled_threads": 57, "wall_s": 4.017103224992752, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 lifecycle-b1-R1，condition=R1 probe=on stage=lifecycle block=1；unit=step23-lifecycle-b1-R1，每进程最多1根。

结束 lifecycle-b1-R1：{"label": "lifecycle-b1-R1", "condition": "R1", "probe": "on", "stage": "lifecycle", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 763904, "peak_sampled_threads": 159, "wall_s": 3.9590450690011494, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 lifecycle-b2-R1，condition=R1 probe=on stage=lifecycle block=2；unit=step23-lifecycle-b2-R1，每进程最多1根。

结束 lifecycle-b2-R1：{"label": "lifecycle-b2-R1", "condition": "R1", "probe": "on", "stage": "lifecycle", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 755984, "peak_sampled_threads": 145, "wall_s": 3.992865584004903, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 lifecycle-b2-R0，condition=R0 probe=on stage=lifecycle block=2；unit=step23-lifecycle-b2-R0，每进程最多1根。

结束 lifecycle-b2-R0：{"label": "lifecycle-b2-R0", "condition": "R0", "probe": "on", "stage": "lifecycle", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 736300, "peak_sampled_threads": 57, "wall_s": 4.057515583990607, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 lifecycle-b3-R0，condition=R0 probe=on stage=lifecycle block=3；unit=step23-lifecycle-b3-R0，每进程最多1根。

结束 lifecycle-b3-R0：{"label": "lifecycle-b3-R0", "condition": "R0", "probe": "on", "stage": "lifecycle", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 724272, "peak_sampled_threads": 57, "wall_s": 3.9952279980061576, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 lifecycle-b3-R1，condition=R1 probe=on stage=lifecycle block=3；unit=step23-lifecycle-b3-R1，每进程最多1根。

结束 lifecycle-b3-R1：{"label": "lifecycle-b3-R1", "condition": "R1", "probe": "on", "stage": "lifecycle", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 770604, "peak_sampled_threads": 176, "wall_s": 4.178502449009102, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

三独立生命周期配对块已核对，扩展gate：{"initial_pairs": 3, "stable_nonzero_difference": true, "signatures": [[4379, "gas_counter_diff", 6, 37, "host", "log_message"], [4379, "gas_counter_diff", 6, 37, "host", "log_message"], [4379, "gas_counter_diff", 6, 37, "host", "log_message"]], "next": "extend to 5 separate-process blocks"}。

开始 lifecycle-b4-R1，condition=R1 probe=on stage=lifecycle block=4；unit=step23-lifecycle-b4-R1，每进程最多1根。

结束 lifecycle-b4-R1：{"label": "lifecycle-b4-R1", "condition": "R1", "probe": "on", "stage": "lifecycle", "block": 4, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 760832, "peak_sampled_threads": 176, "wall_s": 4.120330465986626, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 lifecycle-b4-R0，condition=R0 probe=on stage=lifecycle block=4；unit=step23-lifecycle-b4-R0，每进程最多1根。

结束 lifecycle-b4-R0：{"label": "lifecycle-b4-R0", "condition": "R0", "probe": "on", "stage": "lifecycle", "block": 4, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 721524, "peak_sampled_threads": 57, "wall_s": 3.98146439701668, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 lifecycle-b5-R0，condition=R0 probe=on stage=lifecycle block=5；unit=step23-lifecycle-b5-R0，每进程最多1根。

结束 lifecycle-b5-R0：{"label": "lifecycle-b5-R0", "condition": "R0", "probe": "on", "stage": "lifecycle", "block": 5, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 735844, "peak_sampled_threads": 57, "wall_s": 4.193433252017712, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 lifecycle-b5-R1，condition=R1 probe=on stage=lifecycle block=5；unit=step23-lifecycle-b5-R1，每进程最多1根。

结束 lifecycle-b5-R1：{"label": "lifecycle-b5-R1", "condition": "R1", "probe": "on", "stage": "lifecycle", "block": 5, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 753400, "peak_sampled_threads": 145, "wall_s": 4.095780325005762, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 copy-b1-R1，condition=R1 probe=on stage=copy block=1；unit=step23-copy-b1-R1，每进程最多1根。

结束 copy-b1-R1：{"label": "copy-b1-R1", "condition": "R1", "probe": "on", "stage": "copy", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 768768, "peak_sampled_threads": 176, "wall_s": 4.088458993006498, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 copy-b1-C1，condition=C1 probe=on stage=copy block=1；unit=step23-copy-b1-C1，每进程最多1根。

结束 copy-b1-C1：{"label": "copy-b1-C1", "condition": "C1", "probe": "on", "stage": "copy", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 764204, "peak_sampled_threads": 176, "wall_s": 4.0661844839924015, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 copy-b2-C1，condition=C1 probe=on stage=copy block=2；unit=step23-copy-b2-C1，每进程最多1根。

结束 copy-b2-C1：{"label": "copy-b2-C1", "condition": "C1", "probe": "on", "stage": "copy", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 760780, "peak_sampled_threads": 159, "wall_s": 4.01481819601031, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 copy-b2-R1，condition=R1 probe=on stage=copy block=2；unit=step23-copy-b2-R1，每进程最多1根。

结束 copy-b2-R1：{"label": "copy-b2-R1", "condition": "R1", "probe": "on", "stage": "copy", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 768360, "peak_sampled_threads": 159, "wall_s": 4.190013926010579, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 copy-b3-R1，condition=R1 probe=on stage=copy block=3；unit=step23-copy-b3-R1，每进程最多1根。

结束 copy-b3-R1：{"label": "copy-b3-R1", "condition": "R1", "probe": "on", "stage": "copy", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 765992, "peak_sampled_threads": 159, "wall_s": 4.041746164992219, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 copy-b3-C1，condition=C1 probe=on stage=copy block=3；unit=step23-copy-b3-C1，每进程最多1根。

结束 copy-b3-C1：{"label": "copy-b3-C1", "condition": "C1", "probe": "on", "stage": "copy", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 747668, "peak_sampled_threads": 142, "wall_s": 4.160091333993478, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 copy-b4-C1，condition=C1 probe=on stage=copy block=4；unit=step23-copy-b4-C1，每进程最多1根。

结束 copy-b4-C1：{"label": "copy-b4-C1", "condition": "C1", "probe": "on", "stage": "copy", "block": 4, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 768752, "peak_sampled_threads": 176, "wall_s": 4.069140645995503, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 copy-b4-R1，condition=R1 probe=on stage=copy block=4；unit=step23-copy-b4-R1，每进程最多1根。

结束 copy-b4-R1：{"label": "copy-b4-R1", "condition": "R1", "probe": "on", "stage": "copy", "block": 4, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 764984, "peak_sampled_threads": 176, "wall_s": 4.077264277002541, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 copy-b5-R1，condition=R1 probe=on stage=copy block=5；unit=step23-copy-b5-R1，每进程最多1根。

结束 copy-b5-R1：{"label": "copy-b5-R1", "condition": "R1", "probe": "on", "stage": "copy", "block": 5, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 756428, "peak_sampled_threads": 144, "wall_s": 3.963769640016835, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 copy-b5-C1，condition=C1 probe=on stage=copy block=5；unit=step23-copy-b5-C1，每进程最多1根。

结束 copy-b5-C1：{"label": "copy-b5-C1", "condition": "C1", "probe": "on", "stage": "copy", "block": 5, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 751456, "peak_sampled_threads": 142, "wall_s": 4.062808986986056, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

## 2026-10-27 观测器v1拒绝与修正
底层mergeTxReadSet(dst,src)/mergeTxWriteSet会写dst；原GetTxRWMapByContractName采样不能标成readonly。26进程原数据完整保留，源/原CSV/报告已冻结audit/affected_observer_v1并标记不可作最终只读结论。不再运行v1。将仅以透明Get/Put/Del转发记录替代，不读/合并事务内部映射；先静态核查和off/on预检，再另用v2标签重新验证。

开始 v2-preflight-R0-off，condition=R0 probe=off stage=preflight block=0；unit=step23-v2-preflight-R0-off，每进程最多1根。

结束 v2-preflight-R0-off：{"label": "v2-preflight-R0-off", "condition": "R0", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 707320, "peak_sampled_threads": 57, "wall_s": 3.850979241018649, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-preflight-R0-on，condition=R0 probe=on stage=preflight block=0；unit=step23-v2-preflight-R0-on，每进程最多1根。

结束 v2-preflight-R0-on：{"label": "v2-preflight-R0-on", "condition": "R0", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 721992, "peak_sampled_threads": 57, "wall_s": 3.884001313999761, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-preflight-R1-off，condition=R1 probe=off stage=preflight block=0；unit=step23-v2-preflight-R1-off，每进程最多1根。

结束 v2-preflight-R1-off：{"label": "v2-preflight-R1-off", "condition": "R1", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 765948, "peak_sampled_threads": 176, "wall_s": 3.768727510003373, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-preflight-R1-on，condition=R1 probe=on stage=preflight block=0；unit=step23-v2-preflight-R1-on，每进程最多1根。

结束 v2-preflight-R1-on：{"label": "v2-preflight-R1-on", "condition": "R1", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 762920, "peak_sampled_threads": 176, "wall_s": 4.007023782003671, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-preflight-C1-off，condition=C1 probe=off stage=preflight block=0；unit=step23-v2-preflight-C1-off，每进程最多1根。

结束 v2-preflight-C1-off：{"label": "v2-preflight-C1-off", "condition": "C1", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 750948, "peak_sampled_threads": 160, "wall_s": 3.8850502979767043, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-preflight-C1-on，condition=C1 probe=on stage=preflight block=0；unit=step23-v2-preflight-C1-on，每进程最多1根。

结束 v2-preflight-C1-on：{"label": "v2-preflight-C1-on", "condition": "C1", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 767488, "peak_sampled_threads": 159, "wall_s": 3.8251036790024955, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-lifecycle-b1-R0，condition=R0 probe=on stage=lifecycle block=1；unit=step23-v2-lifecycle-b1-R0，每进程最多1根。

结束 v2-lifecycle-b1-R0：{"label": "v2-lifecycle-b1-R0", "condition": "R0", "probe": "on", "stage": "lifecycle", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 733952, "peak_sampled_threads": 57, "wall_s": 3.9069872940017376, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-lifecycle-b1-R1，condition=R1 probe=on stage=lifecycle block=1；unit=step23-v2-lifecycle-b1-R1，每进程最多1根。

结束 v2-lifecycle-b1-R1：{"label": "v2-lifecycle-b1-R1", "condition": "R1", "probe": "on", "stage": "lifecycle", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 759212, "peak_sampled_threads": 176, "wall_s": 3.9392833420133684, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-lifecycle-b2-R1，condition=R1 probe=on stage=lifecycle block=2；unit=step23-v2-lifecycle-b2-R1，每进程最多1根。

结束 v2-lifecycle-b2-R1：{"label": "v2-lifecycle-b2-R1", "condition": "R1", "probe": "on", "stage": "lifecycle", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 762884, "peak_sampled_threads": 171, "wall_s": 3.99374170898227, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-lifecycle-b2-R0，condition=R0 probe=on stage=lifecycle block=2；unit=step23-v2-lifecycle-b2-R0，每进程最多1根。

结束 v2-lifecycle-b2-R0：{"label": "v2-lifecycle-b2-R0", "condition": "R0", "probe": "on", "stage": "lifecycle", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 731380, "peak_sampled_threads": 57, "wall_s": 3.9454786329879425, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-lifecycle-b3-R0，condition=R0 probe=on stage=lifecycle block=3；unit=step23-v2-lifecycle-b3-R0，每进程最多1根。

结束 v2-lifecycle-b3-R0：{"label": "v2-lifecycle-b3-R0", "condition": "R0", "probe": "on", "stage": "lifecycle", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 742796, "peak_sampled_threads": 57, "wall_s": 3.807747105980525, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-lifecycle-b3-R1，condition=R1 probe=on stage=lifecycle block=3；unit=step23-v2-lifecycle-b3-R1，每进程最多1根。

结束 v2-lifecycle-b3-R1：{"label": "v2-lifecycle-b3-R1", "condition": "R1", "probe": "on", "stage": "lifecycle", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 767408, "peak_sampled_threads": 163, "wall_s": 3.893674965016544, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

三独立生命周期配对块已核对，扩展gate：{"initial_pairs": 3, "stable_nonzero_difference": true, "signatures": [[4379, "gas_counter_diff", 6, 37, "host", "log_message"], [4379, "gas_counter_diff", 6, 37, "host", "log_message"], [4379, "gas_counter_diff", 6, 37, "host", "log_message"]], "next": "extend to 5 separate-process blocks"}。

开始 v2-lifecycle-b4-R1，condition=R1 probe=on stage=lifecycle block=4；unit=step23-v2-lifecycle-b4-R1，每进程最多1根。

结束 v2-lifecycle-b4-R1：{"label": "v2-lifecycle-b4-R1", "condition": "R1", "probe": "on", "stage": "lifecycle", "block": 4, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 751800, "peak_sampled_threads": 159, "wall_s": 3.9166779200022575, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-lifecycle-b4-R0，condition=R0 probe=on stage=lifecycle block=4；unit=step23-v2-lifecycle-b4-R0，每进程最多1根。

结束 v2-lifecycle-b4-R0：{"label": "v2-lifecycle-b4-R0", "condition": "R0", "probe": "on", "stage": "lifecycle", "block": 4, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 715512, "peak_sampled_threads": 57, "wall_s": 3.877254772000015, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-lifecycle-b5-R0，condition=R0 probe=on stage=lifecycle block=5；unit=step23-v2-lifecycle-b5-R0，每进程最多1根。

结束 v2-lifecycle-b5-R0：{"label": "v2-lifecycle-b5-R0", "condition": "R0", "probe": "on", "stage": "lifecycle", "block": 5, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 734548, "peak_sampled_threads": 57, "wall_s": 3.9393111869867425, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-lifecycle-b5-R1，condition=R1 probe=on stage=lifecycle block=5；unit=step23-v2-lifecycle-b5-R1，每进程最多1根。

结束 v2-lifecycle-b5-R1：{"label": "v2-lifecycle-b5-R1", "condition": "R1", "probe": "on", "stage": "lifecycle", "block": 5, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 755380, "peak_sampled_threads": 175, "wall_s": 4.178439350012923, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-copy-b1-R1，condition=R1 probe=on stage=copy block=1；unit=step23-v2-copy-b1-R1，每进程最多1根。

结束 v2-copy-b1-R1：{"label": "v2-copy-b1-R1", "condition": "R1", "probe": "on", "stage": "copy", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 759848, "peak_sampled_threads": 166, "wall_s": 3.823200012993766, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-copy-b1-C1，condition=C1 probe=on stage=copy block=1；unit=step23-v2-copy-b1-C1，每进程最多1根。

结束 v2-copy-b1-C1：{"label": "v2-copy-b1-C1", "condition": "C1", "probe": "on", "stage": "copy", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 737716, "peak_sampled_threads": 176, "wall_s": 4.007549954985734, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-copy-b2-C1，condition=C1 probe=on stage=copy block=2；unit=step23-v2-copy-b2-C1，每进程最多1根。

结束 v2-copy-b2-C1：{"label": "v2-copy-b2-C1", "condition": "C1", "probe": "on", "stage": "copy", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 746712, "peak_sampled_threads": 159, "wall_s": 4.051348400011193, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-copy-b2-R1，condition=R1 probe=on stage=copy block=2；unit=step23-v2-copy-b2-R1，每进程最多1根。

结束 v2-copy-b2-R1：{"label": "v2-copy-b2-R1", "condition": "R1", "probe": "on", "stage": "copy", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 743364, "peak_sampled_threads": 144, "wall_s": 4.2679676249972545, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-copy-b3-R1，condition=R1 probe=on stage=copy block=3；unit=step23-v2-copy-b3-R1，每进程最多1根。

结束 v2-copy-b3-R1：{"label": "v2-copy-b3-R1", "condition": "R1", "probe": "on", "stage": "copy", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 759532, "peak_sampled_threads": 159, "wall_s": 4.159325561020523, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-copy-b3-C1，condition=C1 probe=on stage=copy block=3；unit=step23-v2-copy-b3-C1，每进程最多1根。

结束 v2-copy-b3-C1：{"label": "v2-copy-b3-C1", "condition": "C1", "probe": "on", "stage": "copy", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 766244, "peak_sampled_threads": 176, "wall_s": 4.2705690400034655, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-copy-b4-C1，condition=C1 probe=on stage=copy block=4；unit=step23-v2-copy-b4-C1，每进程最多1根。

结束 v2-copy-b4-C1：{"label": "v2-copy-b4-C1", "condition": "C1", "probe": "on", "stage": "copy", "block": 4, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 775456, "peak_sampled_threads": 165, "wall_s": 4.182728412997676, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-copy-b4-R1，condition=R1 probe=on stage=copy block=4；unit=step23-v2-copy-b4-R1，每进程最多1根。

结束 v2-copy-b4-R1：{"label": "v2-copy-b4-R1", "condition": "R1", "probe": "on", "stage": "copy", "block": 4, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 766812, "peak_sampled_threads": 159, "wall_s": 4.182565019000322, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-copy-b5-R1，condition=R1 probe=on stage=copy block=5；unit=step23-v2-copy-b5-R1，每进程最多1根。

结束 v2-copy-b5-R1：{"label": "v2-copy-b5-R1", "condition": "R1", "probe": "on", "stage": "copy", "block": 5, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 768628, "peak_sampled_threads": 144, "wall_s": 4.382238199003041, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 v2-copy-b5-C1，condition=C1 probe=on stage=copy block=5；unit=step23-v2-copy-b5-C1，每进程最多1根。

结束 v2-copy-b5-C1：{"label": "v2-copy-b5-C1", "condition": "C1", "probe": "on", "stage": "copy", "block": 5, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 768604, "peak_sampled_threads": 159, "wall_s": 4.344880917982664, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。


## 2026-10-27 最终v2完成（不使用v1作为最终证据）

v2 build03重新完成6个probe off/on、5个R0/R1块、5个Fresh/Copy块。累计本轮52进程均退出，26个v1因RWMap采样副作用被隔离保存，26个v2构成最终证据；ALL_RUNS.csv明确资格，不合并扩大N。没有提高资源阈值，WSL boot ID未变，无Step23活动unit。

v2五块root R0=12761395/R1=12765774，首差仍第6 transferFrom seq36 DeleteState.after共同6378616→seq37 log_message.before 6386180/6390559，差4379。Fresh/Copy5块35对call、每块147计数点+36桥接快照相同。具体guest缓存原因未定位，不写JSON缓存为确定因果。

最终状态观察不读内部map，原Get/Put/Del透明转发、真实返回/error不改；观测覆盖计数逐项与全部GetStateLen/PutState/DeleteState host调用核对一次。所有业务操作/输入/结果/事件、最终root真实RWSet与账本比较通过。完整callee框架内部RWMap/Table身份/异常仍not_tested。

已产出mandatory CSV、额外业务操作/派生集/覆盖表、source.diff、历史条件、源码行号、版本/回收/运行说明。每原始命令/outcome/receipt均保留。构建build01缺失占位包与脚本小错也如实登记；build02受影响、build03才是有效v2。实际Go源hash均与build03一致，Gas配置和Copy代码原字节未变，native guards前缀未改。

下一条待执行：只提交本实验分支和同步IDE镜像；不再执行guest或push。恢复先读本段、state和ALL_RUNS，旧label不重复跑。

最终v2源码/脚本冻结提交 54e7b45149d2e57ee9190f5295d0ecc9a559bd6d；仅新Step23目录，未推送。准备提交报告/数据/受影响v1档案。

交付核对通过：分析脚本/CSV/范围标签、源码和binary哈希、52进程退出及已记录的历史receipt匹配均检查。最终有效26个v2、旧26个v1完整隔离，不合并。下一步仅本地数据提交和逐文件镜像校验，无待运行实验。
