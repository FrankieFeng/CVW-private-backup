# Step-23 可恢复进度

2026-10-26 Asia/Shanghai。分支experiment/step23-buy-now-gas-attribution，父394d291。

当前：历史审计中，尚未执行本轮guest。只做buyNow Gas归因与Copy同状态等价复核，不测TPS。

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
