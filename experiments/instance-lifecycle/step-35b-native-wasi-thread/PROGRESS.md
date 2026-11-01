# Step-35B progress

Baseline b00f3bad. Audit started; production CVW and native sources unchanged. Candidate local fork origin/chainmaker/v6.0.1@091074013fa056df0c6502262eae425927272e10 has Waker token0 / close token1 mismatch. Next: isolate source worktree, reproduce thread identity, check locked build. One fix only, no E2E load.

Original-library trace: selector thread id17/TID192059 created during wasi_env_new; symbolized creation frame Selector::new. Four-env run has four distinct selector TIDs lacking EXIT. FD/wake trace: close writes eventfd12 under Store deletion via Selector::shutdown, but epoll fd10 registration data=0; candidate source close condition Token1. Closure path exists, notification token mismatched. Native baseline build continues with rustc1.81/locked deps, hard1536MiB/one build job.

Native baseline dependencies compiled with rustc1.81, locked versions. C-API build script refused custom output directory name target-step35b (expects target or target triple). No Rust source fixed/changed: added target symlink to same existing artifact directory and resumed with standard target name. Initial failure log retained.

Rebuilt native baseline succeeded (Rust1.81, fixed Cargo.lock, normal target alias). Original library preserved; rebuilt baseline copied with SHA. Applied single Token0→Token1 constructor edit only; no Gas/compiler/ABI/WASI ownership changes. Next: rebuild patched + baseline C comparison.

C comparison passed: rebuilt baseline 4 WASI leaves 4 identified Selector workers after 3s, patched leaves none. Single patched returns to main thread; wake token mismatch fixed. Go binaries built; private old-ELF Rc probe removed before building, not used for new library. Next Owner and real-node bounded lifecycle smoke; no GC/scavenge resource remedy.

启动 baseline-owner，unit=step35b-proto-baseline-owner，pairs=one split block chunk, max2 targets；命令已保存。

结束 baseline-owner：passed=True，reason=exited，peak_threads=5，RSS_KiB=45404，PID/cgroup结束=True。

启动 patched-owner，unit=step35b-proto-patched-owner，pairs=one split block chunk, max2 targets；命令已保存。

结束 patched-owner：passed=True，reason=exited，peak_threads=5，RSS_KiB=44960，PID/cgroup结束=True。

启动 baseline-compute，unit=step35b-proto-baseline-compute，pairs=one split block chunk, max2 targets；命令已保存。

结束 baseline-compute：passed=True，reason=exited，peak_threads=24，RSS_KiB=276032，PID/cgroup结束=True。

启动 patched-compute，unit=step35b-proto-patched-compute，pairs=one split block chunk, max2 targets；命令已保存。

结束 patched-compute：passed=True，reason=exited，peak_threads=23，RSS_KiB=274912，PID/cgroup结束=True。

启动 baseline-exchange，unit=step35b-proto-baseline-exchange，pairs=one split block chunk, max2 targets；命令已保存。

结束 baseline-exchange：passed=True，reason=exited，peak_threads=47，RSS_KiB=532840，PID/cgroup结束=True。

启动 patched-exchange，unit=step35b-proto-patched-exchange，pairs=one split block chunk, max2 targets；命令已保存。

结束 patched-exchange：passed=True，reason=exited，peak_threads=40，RSS_KiB=516128，PID/cgroup结束=True。

Bounded diagnostic completed: {"label": "baseline-node", "mode": "resource", "outcome": {"label": "baseline-node", "reason": "", "peak_rss_kib": 1205580, "peak_threads": 58, "stop_s": 0.042238943999109324, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 16, "instances_created": 16, "managed_objects": 0, "managed_pending": 0, "stores_closed": 20, "stores_created": 20}, "owned_pids": [204606], "pid_exited": true, "cgroup_empty": true}}

Bounded diagnostic completed: {"label": "patched-node", "mode": "resource", "outcome": {"label": "patched-node", "reason": "", "peak_rss_kib": 1184648, "peak_threads": 45, "stop_s": 0.04972112199902767, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 16, "instances_created": 16, "managed_objects": 0, "managed_pending": 0, "stores_closed": 20, "stores_created": 20}, "owned_pids": [205178], "pid_exited": true, "cgroup_empty": true}}

Bounded diagnostic completed: {"label": "baseline-inflight", "mode": "inflight", "outcome": {"label": "baseline-inflight", "reason": "", "peak_rss_kib": 1175368, "peak_threads": 49, "stop_s": 0.04140612199989846, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 10, "instances_created": 10, "managed_objects": 0, "managed_pending": 0, "stores_closed": 16, "stores_created": 16}, "owned_pids": [205861], "pid_exited": true, "cgroup_empty": true}}

Bounded diagnostic completed: {"label": "patched-inflight", "mode": "inflight", "outcome": {"label": "patched-inflight", "reason": "", "peak_rss_kib": 1206016, "peak_threads": 44, "stop_s": 0.05053108200081624, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 10, "instances_created": 10, "managed_objects": 0, "managed_pending": 0, "stores_closed": 16, "stores_created": 16}, "owned_pids": [206416], "pid_exited": true, "cgroup_empty": true}}

启动 original-compute，unit=step35b-proto-original-compute，pairs=one split block chunk, max2 targets；命令已保存。

结束 original-compute：passed=True，reason=exited，peak_threads=24，RSS_KiB=270272，PID/cgroup结束=True。

启动 original-exchange，unit=step35b-proto-original-exchange，pairs=one split block chunk, max2 targets；命令已保存。

结束 original-exchange：passed=True，reason=exited，peak_threads=47，RSS_KiB=515540，PID/cgroup结束=True。

Bounded diagnostic completed: {"label": "baseline-stop", "mode": "stop-race", "outcome": {"label": "baseline-stop", "reason": "", "peak_rss_kib": 686208, "peak_threads": 26, "stop_s": 0.009284191997721791, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 1, "instances_created": 1, "managed_objects": 0, "managed_pending": 0, "stores_closed": 2, "stores_created": 2}, "owned_pids": [207354], "pid_exited": true, "cgroup_empty": true}}

Bounded diagnostic completed: {"label": "patched-stop", "mode": "stop-race", "outcome": {"label": "patched-stop", "reason": "node_failed", "peak_rss_kib": 684524, "peak_threads": 25, "stop_s": 0.017340106998744886, "systemd": {"MainPID": "0", "Result": "exit-code", "ExecMainStatus": "2", "ControlGroup": "", "ActiveState": "failed"}, "owner": {"event": "owner_closed", "instances_closed": 1, "instances_created": 1, "managed_objects": 0, "managed_pending": 0, "stores_closed": 2, "stores_created": 2}, "owned_pids": [207634], "pid_exited": true, "cgroup_empty": true}}

STOP: patched-stop combined in-flight Reset+SIGTERM reached stop_finished, stores2/2 instances1/1 pending0; then ChainMaker historydb CommitBlock writer panicked leveldb:closed (exit2). Node/cgroup exited. Baseline-stop exited0 but client also lost RPC response. No claim native patch caused panic. Further patched restart/rollback stopped; baseline restart had already started independently and finished, logs retained. Do not run any more dynamic tests without separately resolving node ledger stop/drain. Next: read-only analysis, reports, commits only.

Read-only reconstruction finished: scripts/analyze.py checked prototype original/rebuilt/patched exact parity and four matched node receipts; native patch committed24b6afd79, node adapter72e077a. Reports and CSV written, raw logs unchanged. No further dynamic tests; pending final integrity/staging/experiment commit.

Final state: no running experiment node; failed patched-stop unit MainPID0/cgroup empty retained. RPC27535 closed. All required reports and raw-log tables present. Production dirty status/HEAD and original native source/so unchanged. Deliver reports in CVW experiment directory; executable/native binaries remain ignored in isolated worktree. Dynamic verification halted as specified; next permitted work is separate ledger shutdown audit, not automatic retry.
