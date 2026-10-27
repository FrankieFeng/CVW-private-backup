# Step-24A 可恢复进度

2026-10-27 Asia/Shanghai。父ba57368，分支experiment/step24a-buy-now-gas。

当前：三块五条件的有界动态对照与复算已完成；精确内部cache根因未唯一定位，详见文末和README。以下保留原阶段进度。Step23只取有效v2，原受影响v1不纳入。本轮不研究TPS，不启用Copy，不改Gas/WASM/业务逻辑。

已找到原始WASM与已有GetGas只读探针；正在从固定hash的函数反汇编核对目标路径、JSON缓存HashTrieMap全局槽及已存在诊断导出。任何缓存解释仍待验证。

下一步：生成TRACE_PATH及可证伪预登记；布局若不能由实际assembly核对，Guest cache读取标为工具限制，不猜内存偏移。只允许固定OS owner的有界串行，每进程1根，沿用RSS1536MiB/线程220软限、2GiB/256task硬限、45/60s超时、available8GiB/swap1GiB。禁止提高阈值。

恢复先读本文件/outcome/活动unit，不重复label。每有效过程保存原命令、日志、CSV与状态。无远程push，不覆盖Step23/生产VM。

开始 preflight-R1-off，condition=R1 probe=off stage=preflight block=0；unit=step24a-preflight-R1-off，每进程最多1根。

结束 preflight-R1-off：{"label": "preflight-R1-off", "condition": "R1", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 515008, "peak_sampled_threads": 176, "wall_s": 2.0494296649994794, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 preflight-R1-on，condition=R1 probe=on stage=preflight block=0；unit=step24a-preflight-R1-on，每进程最多1根。

结束 preflight-R1-on：{"label": "preflight-R1-on", "condition": "R1", "probe": "on", "stage": "preflight", "block": 0, "passed": false, "reason": "exited", "systemd": {"MainPID": "0", "Result": "exit-code", "ExecMainStatus": "1", "ActiveState": "failed", "SubState": "failed"}, "peak_sampled_rss_kib": 503084, "peak_sampled_threads": 141, "wall_s": 2.065733678988181, "all_owned_processes_stopped": true, "root_gas": 1510719}。原日志/events/receipt/资源即时落盘；只分析失败，停止后续运行。

preflight-R1-on失败：仅内部cache读取器键布局校验，mint被探针异常中止；所有资源和owner退出正常。已保存STOP/源码。停用读取器A24_CACHE_READ=0，保留Step23 v2探针，准备独立build02与safe-*全部预检；未修改Gas/WASM或放宽任何native/资源守卫。

开始 safe-preflight-R1-on，condition=R1 probe=on stage=preflight block=0；unit=step24a-safe-preflight-R1-on，每进程最多1根。

结束 safe-preflight-R1-on：{"label": "safe-preflight-R1-on", "condition": "R1", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 495852, "peak_sampled_threads": 144, "wall_s": 1.8925681080145296, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-preflight-R1-off，condition=R1 probe=off stage=preflight block=0；unit=step24a-safe-preflight-R1-off，每进程最多1根。

结束 safe-preflight-R1-off：{"label": "safe-preflight-R1-off", "condition": "R1", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 514524, "peak_sampled_threads": 141, "wall_s": 1.9867389540013392, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-preflight-R0-off，condition=R0 probe=off stage=preflight block=0；unit=step24a-safe-preflight-R0-off，每进程最多1根。

结束 safe-preflight-R0-off：{"label": "safe-preflight-R0-off", "condition": "R0", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 485832, "peak_sampled_threads": 40, "wall_s": 1.9567463620041963, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-preflight-R0-on，condition=R0 probe=on stage=preflight block=0；unit=step24a-safe-preflight-R0-on，每进程最多1根。

结束 safe-preflight-R0-on：{"label": "safe-preflight-R0-on", "condition": "R0", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 477384, "peak_sampled_threads": 25, "wall_s": 1.9356046909815632, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-preflight-S0-off，condition=S0 probe=off stage=preflight block=0；unit=step24a-safe-preflight-S0-off，每进程最多1根。

结束 safe-preflight-S0-off：{"label": "safe-preflight-S0-off", "condition": "S0", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 513152, "peak_sampled_threads": 159, "wall_s": 1.918893861991819, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-preflight-S0-on，condition=S0 probe=on stage=preflight block=0；unit=step24a-safe-preflight-S0-on，每进程最多1根。

结束 safe-preflight-S0-on：{"label": "safe-preflight-S0-on", "condition": "S0", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 507192, "peak_sampled_threads": 176, "wall_s": 2.0511353519978, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-preflight-J-off，condition=J probe=off stage=preflight block=0；unit=step24a-safe-preflight-J-off，每进程最多1根。

结束 safe-preflight-J-off：{"label": "safe-preflight-J-off", "condition": "J", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 512980, "peak_sampled_threads": 159, "wall_s": 1.9854079740180168, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-preflight-J-on，condition=J probe=on stage=preflight block=0；unit=step24a-safe-preflight-J-on，每进程最多1根。

结束 safe-preflight-J-on：{"label": "safe-preflight-J-on", "condition": "J", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 501820, "peak_sampled_threads": 159, "wall_s": 2.0396373350231443, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-preflight-U-off，condition=U probe=off stage=preflight block=0；unit=step24a-safe-preflight-U-off，每进程最多1根。

结束 safe-preflight-U-off：{"label": "safe-preflight-U-off", "condition": "U", "probe": "off", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 509484, "peak_sampled_threads": 142, "wall_s": 2.0395331240142696, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-preflight-U-on，condition=U probe=on stage=preflight block=0；unit=step24a-safe-preflight-U-on，每进程最多1根。

结束 safe-preflight-U-on：{"label": "safe-preflight-U-on", "condition": "U", "probe": "on", "stage": "preflight", "block": 0, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 494420, "peak_sampled_threads": 144, "wall_s": 1.946808387991041, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block1-R0，condition=R0 probe=on stage=formal block=1；unit=step24a-safe-block1-R0，每进程最多1根。

结束 safe-block1-R0：{"label": "safe-block1-R0", "condition": "R0", "probe": "on", "stage": "formal", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 492016, "peak_sampled_threads": 57, "wall_s": 1.9706938849994913, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block1-R1，condition=R1 probe=on stage=formal block=1；unit=step24a-safe-block1-R1，每进程最多1根。

结束 safe-block1-R1：{"label": "safe-block1-R1", "condition": "R1", "probe": "on", "stage": "formal", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 510728, "peak_sampled_threads": 176, "wall_s": 1.9970812569954433, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block1-S0，condition=S0 probe=on stage=formal block=1；unit=step24a-safe-block1-S0，每进程最多1根。

结束 safe-block1-S0：{"label": "safe-block1-S0", "condition": "S0", "probe": "on", "stage": "formal", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 515216, "peak_sampled_threads": 142, "wall_s": 1.9519438899878878, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block1-J，condition=J probe=on stage=formal block=1；unit=step24a-safe-block1-J，每进程最多1根。

结束 safe-block1-J：{"label": "safe-block1-J", "condition": "J", "probe": "on", "stage": "formal", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 518212, "peak_sampled_threads": 141, "wall_s": 1.9751355269982014, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block1-U，condition=U probe=on stage=formal block=1；unit=step24a-safe-block1-U，每进程最多1根。

结束 safe-block1-U：{"label": "safe-block1-U", "condition": "U", "probe": "on", "stage": "formal", "block": 1, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 528524, "peak_sampled_threads": 176, "wall_s": 1.9704552490147762, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

正式块1五条件完成；逐callee业务/操作/最终RWSet/事件已compare断言通过。

开始 safe-block2-U，condition=U probe=on stage=formal block=2；unit=step24a-safe-block2-U，每进程最多1根。

结束 safe-block2-U：{"label": "safe-block2-U", "condition": "U", "probe": "on", "stage": "formal", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 508480, "peak_sampled_threads": 159, "wall_s": 2.0132632149907295, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block2-J，condition=J probe=on stage=formal block=2；unit=step24a-safe-block2-J，每进程最多1根。

结束 safe-block2-J：{"label": "safe-block2-J", "condition": "J", "probe": "on", "stage": "formal", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 517528, "peak_sampled_threads": 176, "wall_s": 2.023619802988833, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block2-S0，condition=S0 probe=on stage=formal block=2；unit=step24a-safe-block2-S0，每进程最多1根。

结束 safe-block2-S0：{"label": "safe-block2-S0", "condition": "S0", "probe": "on", "stage": "formal", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 536744, "peak_sampled_threads": 176, "wall_s": 2.035029576974921, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block2-R1，condition=R1 probe=on stage=formal block=2；unit=step24a-safe-block2-R1，每进程最多1根。

结束 safe-block2-R1：{"label": "safe-block2-R1", "condition": "R1", "probe": "on", "stage": "formal", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 521840, "peak_sampled_threads": 142, "wall_s": 2.0146006350114476, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block2-R0，condition=R0 probe=on stage=formal block=2；unit=step24a-safe-block2-R0，每进程最多1根。

结束 safe-block2-R0：{"label": "safe-block2-R0", "condition": "R0", "probe": "on", "stage": "formal", "block": 2, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 500716, "peak_sampled_threads": 40, "wall_s": 1.911541307985317, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

正式块2五条件完成；逐callee业务/操作/最终RWSet/事件已compare断言通过。

开始 safe-block3-S0，condition=S0 probe=on stage=formal block=3；unit=step24a-safe-block3-S0，每进程最多1根。

结束 safe-block3-S0：{"label": "safe-block3-S0", "condition": "S0", "probe": "on", "stage": "formal", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 534076, "peak_sampled_threads": 175, "wall_s": 1.9566531399905216, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block3-R1，condition=R1 probe=on stage=formal block=3；unit=step24a-safe-block3-R1，每进程最多1根。

结束 safe-block3-R1：{"label": "safe-block3-R1", "condition": "R1", "probe": "on", "stage": "formal", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 520168, "peak_sampled_threads": 159, "wall_s": 2.0359530259738676, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block3-J，condition=J probe=on stage=formal block=3；unit=step24a-safe-block3-J，每进程最多1根。

结束 safe-block3-J：{"label": "safe-block3-J", "condition": "J", "probe": "on", "stage": "formal", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 509592, "peak_sampled_threads": 141, "wall_s": 2.0054220790043473, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block3-R0，condition=R0 probe=on stage=formal block=3；unit=step24a-safe-block3-R0，每进程最多1根。

结束 safe-block3-R0：{"label": "safe-block3-R0", "condition": "R0", "probe": "on", "stage": "formal", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 491536, "peak_sampled_threads": 57, "wall_s": 2.0092288550222293, "all_owned_processes_stopped": true, "root_gas": 12761395}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

开始 safe-block3-U，condition=U probe=on stage=formal block=3；unit=step24a-safe-block3-U，每进程最多1根。

结束 safe-block3-U：{"label": "safe-block3-U", "condition": "U", "probe": "on", "stage": "formal", "block": 3, "passed": true, "reason": "exited", "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ActiveState": "active", "SubState": "exited"}, "peak_sampled_rss_kib": 509156, "peak_sampled_threads": 141, "wall_s": 2.1782988179766107, "all_owned_processes_stopped": true, "root_gas": 12765774}。原日志/events/receipt/资源即时落盘；下一步核对当前块，再继续已登记阶段。

正式块3五条件完成；逐callee业务/操作/最终RWSet/事件已compare断言通过。

## 阶段完成：审计、预检、动态块、复算

2026-10-27：build02 SHA303c5a7680d3cfee20bd07dc8332ed929073a3a015fe25f03374963efd916fc1，仅原Module，A24_CACHE_READ=0；probe off/on五条件配对均通过。suite三块顺序按TRACE_PATH登记完成，15笔真实root/90子调用，逐过程即时落盘，无重跑有效label。

运行命令：python3 -B scripts/run.py safe-preflight-R1-on R1 --probe on；python3 -B scripts/suite.py；python3 -B scripts/analyze.py；python3 -B scripts/verify_history.py。前置build01/build02准确argv存audit/*-command.json，逐进程完整argv/env存raw_logs/*-command.json。

结果：R0/J每块根Gas12761395；R1/S0/U每块12765774。第一处分歧call6 seq37，seq36相等；窗口增量7564/11943。root/各callee输入、透明Get/Put/Del操作、结果/事件、root最终实际RWSet与账本逐项一致。原cache reader失败未抹除，不能作为有效Gas证据；所有新进程未读取cache内部。27进程26成功1探针失败，全部退出，所有manager created=closed，owner managed/pending0。最高监控采样RSS536744KiB/176线程，阈值未提高。

交付：README.md、TRACE_PATH.md、GAS_ATTRIBUTION.md、GAS_TRACE.csv、BLOCK_SUMMARY.csv、CALLS.csv、STATE_COMPARISON.csv、PAIRED_GAS.csv、WARM_RECORDS.csv、ALL_RUNS.csv、RESOURCE_LIFECYCLE.csv、audit/verification.json、原始raw_logs、源码及scripts。当前阻塞：只读内部cache解析未建立可靠性，因而精确encoderCache/fieldCache/fmt/分配机制未唯一定位；Table身份/异常/并发/长期回收仍not_tested。

下一条安全恢复命令：python3 -B scripts/analyze.py（只复算）；不需再启动guest。后续动态诊断必须独立计划，不删除STOP或覆盖本轮label。当前准备只提交实验独立分支并同步IDE资料，不push。
