# Step-35 可恢复进度：已交付，E2E准入暂停

- 审计完成：真实节点入口/停止链、版本、native哈希、原生产工作区状态已保存。
- 源码完成：Step34 Owner接入非测试InstancesManager；缓存Module、独立Store、WASI、真实根/子调用、同步关闭、Reset/Stop路由、fail-closed准入。
- 有界验证完成：7个实际Manager夹具进程（6种配置+最终回归），准入测试；真实节点已完成四方法、六次子调用、同账本重启、失败提交零写集、inflight1 Stop、6轮有限请求。原始失败全部保留。
- 资源门槛未通过：原配置触发1536MiB停止，小账本6轮峰值1481.109MiB/109线程，GC后heap下降但RSS/线程未证实收敛；不扩大、不启动E2E性能实验。
- 正式Copy性能对照：未执行。节点级链配置触发Reset：未执行（实际manager Reset接口测试通过）。
- 当前无运行中的本实验节点、客户端或native测试；仅最初启动失败的systemd状态保留，MainPID=0。
- 下一条可执行命令（只复算）：`python3 scripts/analyze.py`。后续动态任务需先针对资源收敛制定有界诊断，见NEXT_STEP.md，不能自动续跑压测。
- 主分支原HEAD/已有修改保持，历史目录未改。不推送。

## 执行日志（保留早期状态与当时下一步）

# Step-35 progress

1. Audit: started. Base 9845db98, independent worktree cvw-step35. Existing CVW changes preserved.
2. Implementation: pending.
3. Node smoke: not started.
4. Gate: not admitted.

Next: implement actual InstancesManager adapter reusing SafeFreshOwner. No old grow/async close.

Adapter preflight compute/exchange/fact passed. fact resource monitor hit /proc exit race after PASS; preserved raw log and marked resource peak missing. Added ProcessLookupError handling; no native failure observed. Next continue remaining preflights, then node.

First node startup refused at package init due missing CM_STEP21A_POOL; raw stack preserved. Added existing capacity/guard/observe flags; all guards remain on. No native job/ledger created by refused startup.

Node node-baseline-configured finished; action=deploy; outcome={"label": "node-baseline-configured", "reason": "resource_guard", "peak_rss_kib": 1585572, "peak_threads": 33, "stop_s": 0.017405816999598756, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 6, "instances_created": 6, "managed_objects": 0, "managed_pending": 0, "stores_closed": 11, "stores_created": 11}, "pid_exited": true, "cgroup_empty": true}

## NODE RESOURCE STOP
After five real deployments, before first business request completed, monitor observed 1,585,572 KiB RSS > 1,572,864 KiB soft limit; sent SIGTERM. Owner drained: Store 11/11, Instance 6/6, pending0; node exit0 and cgroup empty. No threshold increase or E2E run. Client monitor print hit None response after stop; raw response already persisted. Analyze retained resource trace/config before any further request.

## Small-ledger controlled smoke
Static storage path store/v2@v2.4.0/statedb/bloom/bloom.go:173 -> bloom/filter.go -> bits-and-blooms.NewWithEstimates allocates ~1.116GiB for original n=1e9,p=.01. Declared fresh independent ledger config reduces only n to1e5, keeps enabled/p=.01, all original RSS/thread/native/Gas/Guest guards. Failed original ledger and logs retained. This does not establish root cause of all RSS growth. Next: baseline small-ledger bounded smoke.

Node node-small-baseline finished; action=deploy; outcome={"label": "node-small-baseline", "reason": "", "peak_rss_kib": 1265920, "peak_threads": 65, "stop_s": 0.05101381100030267, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 22, "instances_created": 22, "managed_objects": 0, "managed_pending": 0, "stores_closed": 27, "stores_created": 27}, "pid_exited": true, "cgroup_empty": true}

Code review before further smoke: StopVM previously passed a 10s context to Owner.Stop. To prevent returning a timeout to Blockchain.Stop then closing the chain DB under an active guest, it now waits for Owner drain; external systemd TimeoutStopSec=10s remains fail-closed process bound. No native cancellation is claimed. Rebuild node4/vm3; earlier node2 logs retained separately.

Node node-small-restart-converge finished; action=converge; outcome={"label": "node-small-restart-converge", "reason": "", "peak_rss_kib": 1161228, "peak_threads": 55, "stop_s": 0.05212327799927152, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 29, "instances_created": 29, "managed_objects": 0, "managed_pending": 0, "stores_closed": 34, "stores_created": 34}, "pid_exited": true, "cgroup_empty": true}

Node node-small-copy finished; action=deploy; outcome={"label": "node-small-copy", "reason": "", "peak_rss_kib": 1320836, "peak_threads": 65, "stop_s": 0.04219832499984477, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 22, "instances_created": 22, "managed_objects": 0, "managed_pending": 0, "stores_closed": 27, "stores_created": 27}, "pid_exited": true, "cgroup_empty": true}

Node node-small-inflight finished; action=inflight; outcome={"label": "node-small-inflight", "reason": "", "peak_rss_kib": 681008, "peak_threads": 26, "stop_s": 0.012557762000142247, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 1, "instances_created": 1, "managed_objects": 0, "managed_pending": 0, "stores_closed": 2, "stores_created": 2}, "owned_pids": [29514], "pid_exited": true, "cgroup_empty": true}

Node node-small-six-waves finished; action=converge; outcome={"label": "node-small-six-waves", "reason": "", "peak_rss_kib": 1516656, "peak_threads": 109, "stop_s": 0.05503333799970278, "systemd": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "inactive"}, "owner": {"event": "owner_closed", "instances_closed": 67, "instances_created": 67, "managed_objects": 0, "managed_pending": 0, "stores_closed": 72, "stores_created": 72}, "owned_pids": [30552], "pid_exited": true, "cgroup_empty": true}

Final review: managed experiment bindings cannot safely fall through to the old pool when opt-in is absent. Constructor now fails closed for CM_SAFE_FRESH_NODE!=1; original production rollback is original binary/config, not flag-off into legacy workers. This only changes disabled-mode admission. Build node6/vm5, admission and one actual manager lifecycle regression; no more node load.
