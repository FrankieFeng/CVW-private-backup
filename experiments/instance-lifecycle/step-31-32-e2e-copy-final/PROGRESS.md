# Step-31/32可恢复进度
父bb2772d9，分支experiment/step31-32-e2e-copy-final。
阶段一：最小安全审计。仅核对历史源码与已有协议，不新优化、无clone内部研究。准备重跑既有两个有界生命周期probe（非节点/非E2E）：TestStep22ModuleLifecycle；TestStep21DOwnerFailure。保留managed owner/close/资源守卫，独立进程，仅scalar3 fresh或1个WASI错误回收。
有限候选：现有根锁不覆盖finalizer；直接复制managed.go不建立owner路径；现有dManager依赖测试fixture且没有真实节点入口/退出适配。审计真实StartVM/NewRuntimeInstance/Reset/Stop全链，若仍需未经验证的节点运行时适配即门槛失败，停止而不继续改VM。
没有启动节点/RPC/E2E，第二阶段未准入。中断先读本文件与raw outcome及systemctl，不重复完成probe。

启动既有protocol probe TestStep22ModuleLifecycle；命令已保存，未启动节点。

完成probe TestStep22ModuleLifecycle：passed=False，PID/cgroup清空=True；不代表真实节点已准入。

启动既有protocol probe TestStep22ModuleLifecycle；命令已保存，未启动节点。

完成probe TestStep22ModuleLifecycle：passed=True，PID/cgroup清空=True；不代表真实节点已准入。

启动既有protocol probe TestStep21DOwnerFailure；命令已保存，未启动节点。

完成probe TestStep21DOwnerFailure：passed=True，PID/cgroup清空=True；不代表真实节点已准入。

阶段一动态检查已执行：首个进程因漏CM_REUSE_EXPERIMENT在package init失败，无测试体/Store创建，原日志/STOP保留。补齐R1、capacity和STORE_GUARD=1后独立重试，既有ModuleLifecycle及OwnerFailure均通过。没有关闭任何生命周期守卫、没调限、没改VM。两有效进程managed/pending0，PID/cgroup结束；资源峰52.71MiB/23线程。Go heap缺失如实标记。
有限适配审计完成：真实node NewRuntimeInstance在根锁前创建pool；StartVM/StopVM均空，CloseAllPool/Reset没有fixed owner与在途join；managed测试管理器有fixture依赖、进程终结与Store/WASI预算，不能直接当节点插件。缺可验证的节点全生命周期适配/长寿命资源约束。
SAFETY_GATE.md已落盘，最终NOT_PASSED。按用户要求即刻停止进一步动态测试及VM代码改动，Step32两轮均not_run，新E2E配对0。接下来仅离线审计/报告/CSV/本地版本保存，不再运行任何native probe或客户端。

收尾交付完成：README/SAFETY_GATE/AUDIT/RESULTS/TIMING_BOUNDARIES/E2E_SAMPLES/PAIRED_EFFECTS/THROUGHPUT/CORRECTNESS/RESOURCE_SUMMARY、原始probe日志/命令/outcome/资源、历史源码/原始数据引用manifest、离线复算与verify全部保存。最终C；新E2E0请求/0对/0轮。历史数据没有拼接进本轮。配置失败的systemd unit保留failed状态，但MainPID0、无cgroup；verify按“无活进程”验证，不清除失败记录来伪装通过。
两个协议检查通过只属于小进程；节点full owner/Reset/Stop排空和长寿命native/WASI回收仍未满足，门槛已失败，不再修改VM/执行更多检查。仅stage31代码/日志/文档交付，无生产改动、无新优化、无clone机制研究、无PPT、无push。
现在可以阶段性总结：若干串行VM初始化收益已有证据；真实客户端端到端收益尚未确认，本轮因安全准入阻塞而非负收益。后续最小任务限定节点生命周期适配包及其回收/业务预检，其他机制研究不作为本阶段总结前置。
下一条仅本地commit与IDE镜像；复核只运行archive_and_report.py、verify.py（不运行lifecycle_checks）。
