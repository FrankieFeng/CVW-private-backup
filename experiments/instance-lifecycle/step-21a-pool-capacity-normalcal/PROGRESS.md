# Step-21A 可恢复进度

实验：Step-21A-实例池容量修复与normalCal归因。2026-10-26，Asia/Shanghai。

## 四阶段

- 审计：进行中。已确认原Step21源码dc4d63b、容量修复c6addbf；初始资源空闲，未启动新测试。
- 预检：未开始。
- 正式实验：未开始。计划bigNumCal/normalCal，100次/组，最多3批；原策略若阻塞则停止相关后续组，保留栈和已返回样本。
- 结果分析：未开始。

## 已运行命令

- `git -C CVW worktree list`
- `git -C .worktrees/cvw-step21-fixed show --format=fuller --stat c6addbf`
- `free -h`、`systemctl --user list-units 'step21*' --no-legend`

## 结果文件

本文件先于新构建/测试创建；后续每进程保存命令JSON、原始日志、资源采样、CSV和outcome，再更新本文件。不覆盖Step19/21历史数据。

## 当前阻塞项

尚需复核Store安全与原阻塞退出路径、normalCal可用细分观测；不预设可以开始性能测试。

## 下一条待执行命令

`git -C .worktrees/cvw-step21-fixed diff dc4d63b c6addbf -- chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/vm_pool.go`

## 恢复规则

会话中断后先读本文件和raw_logs/*-outcome.json；有活动unit时先查PID/状态，不重启同标签。有效进程不重复。失败、超时、资源保护停止必须保留现场。未承诺防止stream disconnected；不改Clash、代理或VS Code配置。

## 审计阶段完成

- 准确diff已保存audit/capacity-fix.patch，结论见POOL_DIFF.md。容量补丁可能影响稳态供给，不仅退出。
- 独立分支experiment/step21a-pool-normalcal，worktree .worktrees/cvw-step21a，父c6addbf。
- 发现潜在同Store生命周期重叠：先加共同fail-fast守卫，既不等待也不串行化；检测即保存栈并停止相关正式矩阵。
- 下一步：构建守卫诊断；先单实例、每次调用后排空的功能预检（单列，非原负载性能），再原始TestInvoke小样本，安全通过才允许100次正式批。

## 预检构建完成

- 共同源码3c01a4b，binary与完整差异见environment.json、audit/step21a-source.patch。原始/修复模式仅grow容量分支不同，原InvokeTime时间戳位置未动。
- 执行计划已固化scripts/suite.py；所有守卫和仪表两组一致。每进程后立即更新summary.csv、raw_logs/*samples.csv和PROGRESS。
- next: `python3 -B scripts/suite.py`。不启动并发或节点。

### 2026-10-26 01:14:11

即将执行：`python3 -B scripts/run.py --pool original --policy R0 --method bigNumCal --phase isolated --n 3`；原始命令见raw_logs/isolated-bigNumCal-original-r0-a-command.json。

下一条待执行：先检查systemctl --user show step21a-isolated-bignumcal-original-r0-a；不可重复启动

### 2026-10-26 01:14:11

已落盘isolated-bigNumCal-original-r0-a：{"label": "isolated-bigNumCal-original-r0-a", "pool": "original", "policy": "R0", "phase": "isolated", "method": "bigNumCal", "requested": 3, "observed": 3, "success": 3, "gas_distribution": "{\"105920\": 3}", "guard_overlap": false, "execution_ok": true, "primary_accepted": false, "status": "passed", "peak_rss_mib": 218.40234375, "peak_threads": 24, "enqueue_unfinished": 0, "created": 2, "closed": 2, "invoke_mean_ms": 0.5476553333333334, "invoke_p50_ms": 0.473896, "invoke_p95_ms": 0.763012, "callmethod_mean_ms": 0.45472399999999996, "callmethod_p50_ms": 0.413675, "callmethod_p95_ms": 0.612987, "channel_mean_ms": 0.0, "channel_p50_ms": 0.0, "channel_p95_ms": 0.0, "b5_export_mean_ms": 0.333751, "b5_export_p50_ms": 0.320626, "b5_export_p95_ms": 0.412227, "vm_log_tps_diagnostic_only": 1825.965966429007}；CSV已更新。

下一条待执行：python3 -B scripts/suite.py (会跳过已有完成结果)

### 2026-10-26 01:14:12

即将执行：`python3 -B scripts/run.py --pool original --policy R1 --method bigNumCal --phase isolated --n 3`；原始命令见raw_logs/isolated-bigNumCal-original-r1-a-command.json。

下一条待执行：先检查systemctl --user show step21a-isolated-bignumcal-original-r1-a；不可重复启动

### 2026-10-26 01:14:12

已落盘isolated-bigNumCal-original-r1-a：{"label": "isolated-bigNumCal-original-r1-a", "pool": "original", "policy": "R1", "phase": "isolated", "method": "bigNumCal", "requested": 3, "observed": 3, "success": 3, "gas_distribution": "{\"105920\": 3}", "guard_overlap": false, "execution_ok": true, "primary_accepted": false, "status": "passed", "peak_rss_mib": 215.328125, "peak_threads": 24, "enqueue_unfinished": 0, "created": 5, "closed": 5, "invoke_mean_ms": 0.47682, "invoke_p50_ms": 0.517537, "invoke_p95_ms": 0.650752, "callmethod_mean_ms": 0.38301366666666664, "callmethod_p50_ms": 0.379706, "callmethod_p95_ms": 0.55468, "channel_mean_ms": 0.0, "channel_p50_ms": 0.0, "channel_p95_ms": 0.0, "b5_export_mean_ms": 0.25927133333333335, "b5_export_p50_ms": 0.198916, "b5_export_p95_ms": 0.418346, "vm_log_tps_diagnostic_only": 2097.2274652908854}；CSV已更新。

下一条待执行：python3 -B scripts/suite.py (会跳过已有完成结果)

### 2026-10-26 01:14:12

即将执行：`python3 -B scripts/run.py --pool capacity --policy R0 --method bigNumCal --phase isolated --n 3`；原始命令见raw_logs/isolated-bigNumCal-capacity-r0-a-command.json。

下一条待执行：先检查systemctl --user show step21a-isolated-bignumcal-capacity-r0-a；不可重复启动

### 2026-10-26 01:14:13

已落盘isolated-bigNumCal-capacity-r0-a：{"label": "isolated-bigNumCal-capacity-r0-a", "pool": "capacity", "policy": "R0", "phase": "isolated", "method": "bigNumCal", "requested": 3, "observed": 3, "success": 3, "gas_distribution": "{\"105920\": 3}", "guard_overlap": false, "execution_ok": true, "primary_accepted": false, "status": "passed", "peak_rss_mib": 258.1328125, "peak_threads": 25, "enqueue_unfinished": 0, "created": 2, "closed": 2, "invoke_mean_ms": 0.3628986666666667, "invoke_p50_ms": 0.263421, "invoke_p95_ms": 0.602844, "callmethod_mean_ms": 0.3013416666666667, "callmethod_p50_ms": 0.228283, "callmethod_p95_ms": 0.480555, "channel_mean_ms": 0.0, "channel_p50_ms": 0.0, "channel_p95_ms": 0.0, "b5_export_mean_ms": 0.20477166666666666, "b5_export_p50_ms": 0.182258, "b5_export_p95_ms": 0.279939, "vm_log_tps_diagnostic_only": 2755.5901739328515}；CSV已更新。

下一条待执行：python3 -B scripts/suite.py (会跳过已有完成结果)

### 2026-10-26 01:14:13

即将执行：`python3 -B scripts/run.py --pool capacity --policy R1 --method bigNumCal --phase isolated --n 3`；原始命令见raw_logs/isolated-bigNumCal-capacity-r1-a-command.json。

下一条待执行：先检查systemctl --user show step21a-isolated-bignumcal-capacity-r1-a；不可重复启动

### 2026-10-26 01:14:14

已落盘isolated-bigNumCal-capacity-r1-a：{"label": "isolated-bigNumCal-capacity-r1-a", "pool": "capacity", "policy": "R1", "phase": "isolated", "method": "bigNumCal", "requested": 3, "observed": 3, "success": 3, "gas_distribution": "{\"105920\": 3}", "guard_overlap": false, "execution_ok": true, "primary_accepted": false, "status": "passed", "peak_rss_mib": 253.6484375, "peak_threads": 24, "enqueue_unfinished": 0, "created": 5, "closed": 5, "invoke_mean_ms": 0.3921946666666667, "invoke_p50_ms": 0.356506, "invoke_p95_ms": 0.490611, "callmethod_mean_ms": 0.308681, "callmethod_p50_ms": 0.298808, "callmethod_p95_ms": 0.37013, "channel_mean_ms": 0.0, "channel_p50_ms": 0.0, "channel_p95_ms": 0.0, "b5_export_mean_ms": 0.20778833333333332, "b5_export_p50_ms": 0.192672, "b5_export_p95_ms": 0.250434, "vm_log_tps_diagnostic_only": 2549.754203694764}；CSV已更新。

下一条待执行：python3 -B scripts/suite.py (会跳过已有完成结果)

### 2026-10-26 01:14:14

即将执行：`python3 -B scripts/run.py --pool original --policy R0 --method normalCal --phase isolated --n 3`；原始命令见raw_logs/isolated-normalCal-original-r0-a-command.json。

下一条待执行：先检查systemctl --user show step21a-isolated-normalcal-original-r0-a；不可重复启动

### 2026-10-26 01:14:15

已落盘isolated-normalCal-original-r0-a：{"label": "isolated-normalCal-original-r0-a", "pool": "original", "policy": "R0", "phase": "isolated", "method": "normalCal", "requested": 3, "observed": 3, "success": 3, "gas_distribution": "{\"100000072\": 3}", "guard_overlap": false, "execution_ok": true, "primary_accepted": false, "status": "passed", "peak_rss_mib": 256.69921875, "peak_threads": 24, "enqueue_unfinished": 0, "created": 2, "closed": 2, "invoke_mean_ms": 72.91165066666667, "invoke_p50_ms": 73.651724, "invoke_p95_ms": 74.130694, "callmethod_mean_ms": 72.790581, "callmethod_p50_ms": 73.444207, "callmethod_p95_ms": 74.04406, "channel_mean_ms": 0.0, "channel_p50_ms": 0.0, "channel_p95_ms": 0.0, "b5_export_mean_ms": 72.55816833333333, "b5_export_p50_ms": 73.115022, "b5_export_p95_ms": 73.865922, "vm_log_tps_diagnostic_only": 13.715229196658063}；CSV已更新。

下一条待执行：python3 -B scripts/suite.py (会跳过已有完成结果)

### 2026-10-26 01:14:15

即将执行：`python3 -B scripts/run.py --pool original --policy R1 --method normalCal --phase isolated --n 3`；原始命令见raw_logs/isolated-normalCal-original-r1-a-command.json。

下一条待执行：先检查systemctl --user show step21a-isolated-normalcal-original-r1-a；不可重复启动

### 2026-10-26 01:14:16

已落盘isolated-normalCal-original-r1-a：{"label": "isolated-normalCal-original-r1-a", "pool": "original", "policy": "R1", "phase": "isolated", "method": "normalCal", "requested": 3, "observed": 3, "success": 3, "gas_distribution": "{\"100000072\": 3}", "guard_overlap": false, "execution_ok": true, "primary_accepted": false, "status": "passed", "peak_rss_mib": 259.48828125, "peak_threads": 24, "enqueue_unfinished": 0, "created": 5, "closed": 5, "invoke_mean_ms": 78.76274, "invoke_p50_ms": 80.249218, "invoke_p95_ms": 80.977834, "callmethod_mean_ms": 78.63697366666666, "callmethod_p50_ms": 80.094798, "callmethod_p95_ms": 80.909721, "channel_mean_ms": 0.0, "channel_p50_ms": 0.0, "channel_p95_ms": 0.0, "b5_export_mean_ms": 78.43448333333333, "b5_export_p50_ms": 79.806464, "b5_export_p95_ms": 80.766091, "vm_log_tps_diagnostic_only": 12.696358709714772}；CSV已更新。

下一条待执行：python3 -B scripts/suite.py (会跳过已有完成结果)

### 2026-10-26 01:14:16

即将执行：`python3 -B scripts/run.py --pool capacity --policy R0 --method normalCal --phase isolated --n 3`；原始命令见raw_logs/isolated-normalCal-capacity-r0-a-command.json。

下一条待执行：先检查systemctl --user show step21a-isolated-normalcal-capacity-r0-a；不可重复启动

### 2026-10-26 01:14:17

已落盘isolated-normalCal-capacity-r0-a：{"label": "isolated-normalCal-capacity-r0-a", "pool": "capacity", "policy": "R0", "phase": "isolated", "method": "normalCal", "requested": 3, "observed": 3, "success": 3, "gas_distribution": "{\"100000072\": 3}", "guard_overlap": false, "execution_ok": true, "primary_accepted": false, "status": "passed", "peak_rss_mib": 257.69140625, "peak_threads": 24, "enqueue_unfinished": 0, "created": 2, "closed": 2, "invoke_mean_ms": 75.15324033333333, "invoke_p50_ms": 75.932883, "invoke_p95_ms": 78.344838, "callmethod_mean_ms": 75.060828, "callmethod_p50_ms": 75.854187, "callmethod_p95_ms": 78.276421, "channel_mean_ms": 0.0, "channel_p50_ms": 0.0, "channel_p95_ms": 0.0, "b5_export_mean_ms": 74.89198666666667, "b5_export_p50_ms": 75.693163, "b5_export_p95_ms": 78.140374, "vm_log_tps_diagnostic_only": 13.306146156368214}；CSV已更新。

下一条待执行：python3 -B scripts/suite.py (会跳过已有完成结果)

### 2026-10-26 01:14:17

即将执行：`python3 -B scripts/run.py --pool capacity --policy R1 --method normalCal --phase isolated --n 3`；原始命令见raw_logs/isolated-normalCal-capacity-r1-a-command.json。

下一条待执行：先检查systemctl --user show step21a-isolated-normalcal-capacity-r1-a；不可重复启动

### 2026-10-26 01:14:18

已落盘isolated-normalCal-capacity-r1-a：{"label": "isolated-normalCal-capacity-r1-a", "pool": "capacity", "policy": "R1", "phase": "isolated", "method": "normalCal", "requested": 3, "observed": 3, "success": 3, "gas_distribution": "{\"100000072\": 3}", "guard_overlap": false, "execution_ok": true, "primary_accepted": false, "status": "passed", "peak_rss_mib": 259.29296875, "peak_threads": 24, "enqueue_unfinished": 0, "created": 5, "closed": 5, "invoke_mean_ms": 75.197076, "invoke_p50_ms": 74.752849, "invoke_p95_ms": 77.06594, "callmethod_mean_ms": 75.04280166666666, "callmethod_p50_ms": 74.578642, "callmethod_p95_ms": 76.936706, "channel_mean_ms": 0.0, "channel_p50_ms": 0.0, "channel_p95_ms": 0.0, "b5_export_mean_ms": 74.856276, "b5_export_p50_ms": 74.377573, "b5_export_p95_ms": 76.777879, "vm_log_tps_diagnostic_only": 13.29838942141846}；CSV已更新。

下一条待执行：python3 -B scripts/suite.py (会跳过已有完成结果)

### 2026-10-26 01:14:18

即将执行：`python3 -B scripts/run.py --pool original --policy R0 --method bigNumCal --phase preflight --n 3`；原始命令见raw_logs/preflight-bigNumCal-original-r0-a-command.json。

下一条待执行：先检查systemctl --user show step21a-preflight-bignumcal-original-r0-a；不可重复启动

### 2026-10-26 01:14:19

已落盘preflight-bigNumCal-original-r0-a：{"label": "preflight-bigNumCal-original-r0-a", "pool": "original", "policy": "R0", "phase": "preflight", "method": "bigNumCal", "requested": 3, "observed": 0, "success": 0, "gas_distribution": "{}", "guard_overlap": true, "execution_ok": false, "primary_accepted": false, "status": "store_guard_stopped", "peak_rss_mib": 207.44140625, "peak_threads": 23, "enqueue_unfinished": 0, "created": 2, "closed": 1, "invoke_mean_ms": "", "invoke_p50_ms": "", "invoke_p95_ms": "", "callmethod_mean_ms": "", "callmethod_p50_ms": "", "callmethod_p95_ms": "", "channel_mean_ms": "", "channel_p50_ms": "", "channel_p95_ms": "", "b5_export_mean_ms": "", "b5_export_p50_ms": "", "b5_export_p95_ms": "", "vm_log_tps_diagnostic_only": ""}；CSV已更新。

下一条待执行：仅分析现有raw_logs及STOP.json；禁止继续正式矩阵

## 预检阶段完成，正式阶段按安全要求停止

- 已真实执行8个隔离功能进程：2方法×2池模式×R0/R1，各3次，共24次业务成功。每进程CSV和原日志均已在完成后保存。该诊断初始库存1、每调用后维护排空，不能作为原连续负载吞吐对照。
- 恢复原始空池TestInvoke路径的第一个预检preflight-bigNumCal-original-r0-a触发守卫，requested=execute/owner=create；栈已保存在对应.log。没有返回业务样本，没有启动正式100次或重复触发。
- 守卫检测的是保守的生命周期区间，栈采样时worker在wasi_config_new；这不等于已证实两次具体Store原生访问重叠，更不能写成已复现native数据竞争。由于现有Store所有权保障未建立，按预先登记安全条件停止，未用全局锁继续采数。
- formal 24个计划条件（2方法×2池×2模式×3批）均未运行；主性能样本0，不补造。
- 所有9个自启测试进程已停止；8个诊断正常排空，第9个为守卫退出，不能标正常回收。
- 下一条待执行：`python3 -B scripts/analyze.py`，仅分析和报告，不再启动测试。

## 分析阶段完成

- NORMALCAL_ANALYSIS.md：原600条细分，8.300ms CallMethod差异中的8.294ms在exportFunc.Call；本轮24次实际功能样本不构成原连续负载重复证据。
- README.md：五项最终问题、部分完成范围与停止原因。summary.csv保留9次实际尝试并显式列24个未执行正式组；formal_matrix.csv、correctness.csv、verification.json已保存。
- 已执行只读分析命令：`python3 -B scripts/audit_history.py`、`python3 -B scripts/extract_current_normalcal.py`、`python3 -B scripts/analyze.py`、`python3 -B scripts/report.py`。
- 所有实验unit已退出；未触发RSS/线程限额，守卫为安全停止。未修改网络/代理/VSCode。
- 下一步：保存独立分支提交（不push）；禁止自动续跑STOP矩阵。恢复时只读本文件、STOP.json及分支HEAD。

## 最终一致性检查

- 9个实际进程、24次功能成功、24个正式组均0次主样本；所有owned unit的MainPID为0/非active。
- 全部脚本语法检查通过，audit/final-check.json已保存。
- 即将仅在experiment/step21a-pool-normalcal提交本实验资料；没有push，PROGRESS/STOP是后续恢复入口。
