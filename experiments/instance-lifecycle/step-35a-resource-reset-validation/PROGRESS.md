# Step-35A：已完成有界诊断，Step-36不准入

1. 历史复算完成：复用Step35六轮24笔交易；原逐轮RSS/线程同步证据缺失项显式标注。
2. 源码/析构审计完成：CAPI计数、固定ELF最后strong分支、WASI/Imports、Module缓存、allocator及Selector关闭路径已区分。
3. 动态验证完成：4个有界节点进程、30个同步资源快照、9次真实Manager Reset、14笔新成功提交业务；1笔Stop期间请求未确认提交，未算成功。原资源阈值未改。
4. 修正完成：Stop等待在途Reset结束，另覆盖先Stop后Reset拒绝；真实节点重叠退出正常，Store66/66、Instance51/51配平。
5. Native对照完成：Store-only无线程残留；WASI-only每次多1个epoll线程，单次残留持续10秒。固定so未改，后台线程回收仍有明确缺陷。
6. 结论：RSS并非整体泄漏；线程不收敛，禁止正式Copy E2E。native Selector/WASI修复需另行恢复准确构建与验证，不无限扩大本轮。
7. 当前没有运行中的本实验节点、客户端、native进程或systemd unit。
8. 下一条可执行命令（仅复算）：`python3 scripts/analyze.py`；业务核对：`python3 scripts/verify_business.py`。不自动启动新负载。

## 阶段执行记录（保留）

# Step-35A progress

Audit started from c48cf907. No new node requests yet. Four stages: historical resource reanalysis; native/Reset source audit; bounded diagnostics; admission report.
Next: reanalyse old six waves and instrument read-only diagnostics + actual Manager Reset control.

Bounded diagnostic completed: {"label": "resource1", "mode": "resource", "outcome": {"label": "resource1", "reason": "", "peak_rss_kib": 1148560, "peak_threads": 56, "stop_s": 0.028973578999284655, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 16, "instances_created": 16, "managed_objects": 0, "managed_pending": 0, "stores_closed": 20, "stores_created": 20}, "owned_pids": [135784], "pid_exited": true, "cgroup_empty": true}}

Bounded diagnostic completed: {"label": "reset1", "mode": "inflight", "outcome": {"label": "reset1", "reason": "", "peak_rss_kib": 1190624, "peak_threads": 47, "stop_s": 0.0416279709970695, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 10, "instances_created": 10, "managed_objects": 0, "managed_pending": 0, "stores_closed": 16, "stores_created": 16}, "owned_pids": [136861], "pid_exited": true, "cgroup_empty": true}}

Historical reanalysis completed without rerunning 24 transactions. resource1: 2 new compute/buyNow waves, idle1s, actual Manager Reset twice, final separate GC/scavenge diagnosis; native/WASI/Imports counters balanced. reset1: idle + in-flight compute and buyNow Reset; submissions during Reset completed afterward; bounded stop succeeded. Source review adds exact-ELF read-only last-Rc diagnostic (not ABI change or Store isolation proof) and Go thread-create profile count. Next: one short natural resource window + Stop/Reset race, no threshold changes.

Bounded diagnostic completed: {"label": "resource2", "mode": "resource", "outcome": {"label": "resource2", "reason": "", "peak_rss_kib": 1243820, "peak_threads": 50, "stop_s": 0.025409617999684997, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 24, "instances_created": 24, "managed_objects": 0, "managed_pending": 0, "stores_closed": 28, "stores_created": 28}, "owned_pids": [139230], "pid_exited": true, "cgroup_empty": true}}

Bounded diagnostic completed: {"label": "stop-reset-race", "mode": "stop-race", "outcome": {"label": "stop-reset-race", "reason": "", "peak_rss_kib": 675108, "peak_threads": 26, "stop_s": 0.009681689996796194, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 1, "instances_created": 1, "managed_objects": 0, "managed_pending": 0, "stores_closed": 2, "stores_created": 2}, "owned_pids": [141058], "pid_exited": true, "cgroup_empty": true}}

All dynamic checks finished; no additional load. resource2 exposed exact per-WASI epoll growth, C Store-only vs WASI-only control reproduced without Go/Guest/node; 1 residual epoll thread still alive after10s. Native ABI/library unchanged. Stop/Reset fixed branch and both unit orderings passed; actual node stop-race drained. Next: reports and commit; E2E blocked by native WASI thread reclamation, not an RSS-only guess.
