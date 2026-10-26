# 最小验证设计和实际结果

先完成源码审计再决定运行。源码发现同Store无同步访问的明确风险路径，因此**不执行重叠场景**，不复跑Step21A STOP，不进入真实节点高并发。矩阵的缺失有明确理由，不用“未崩溃”推断线程安全。

| 场景 | 本轮状态 | 理由/结果 |
|---|---|---|
| 单Store同Instance串行3次 | 已执行，独立进程 | 最小C API guest恒返回42，3/3，exit0 |
| 单Store三个Instance串行各1次 | 已执行，另一独立进程 | 先顺序创建3个，再顺序调用，再顺序关闭，3/3返回42，exit0 |
| 单Store不同Instance创建×执行 | 跳过 | 共享StoreMut与Rc，不能通过当前API安全门 |
| 单Store创建×关闭 | 跳过 | 删除引用与创建共享Store，Close也可能执行guest |
| 同Store不同Instance并行执行/执行×关闭 | 跳过 | 同上，无同步契约 |
| 独立Store并行执行 | 未执行 | 隔离方案有价值，但本轮没有实现绑定所有者/回调/Finalizer修复；不因赶矩阵而增加无依据场景 |
| Go绑定+真实业务/WASI/Gas | 未执行新测试 | native串行样例不替代这些检查。Step21A已有24次隔离功能结果只是历史参考 |

## 实际运行方式

[scripts/serial.c](scripts/serial.c)以当前packaged `wasmer.h`编译并动态链接同一so；无Go运行时、host imports、WASI、Gas metering。两个进程各在main OS线程完成所有C API操作；native编译器内部线程不共享主线程外的Store API调用。微型WASM嵌在源码，语义为`run() -> i32.const 42`。

[scripts/run_serial.py](scripts/run_serial.py)固定两场景各3次，拒绝覆盖已有outcome/log；先校验native SHA，编译命令和输出保存[evidence/build.json](evidence/build.json)，binary SHA/ldd见[serial-artifact.json](evidence/serial-artifact.json)。二进制留本机、不作为源码交付提交。没有编译或更改生产VM。

保护沿用：MemoryMax2GiB、TasksMax256、RSS软限1536MiB、线程软限220、MemAvailable至少8GiB、SwapUsed最多1GiB；cgroup RuntimeMax45秒，内层timeout30秒，控制器50秒截止，KillMode=control-group。没有提高旧阈值，运行命令/启动状态/资源采样/退出状态逐进程落盘。超限或失败后停止后续场景，不自动重试。

## 原始记录

| 进程 | 日志 | 退出/结果 | 资源观测 |
|---|---|---|---|
| same，PID517002 | [same.log](raw_logs/same.log)、[outcome](raw_logs/same-outcome.json) | native_version6.0.1，3个42，PASS，ExecMainStatus0 | 进程很短，轮询时已退出，无有效RSS/线程样本 |
| different，PID517024 | [different.log](raw_logs/different.log)、[outcome](raw_logs/different-outcome.json) | 同上；3个实例create_done=close_done | 同上 |

`peak_sampled_rss_kib=0/peak_sampled_threads=0`表示控制器**未采中活进程**，不能称资源消耗为0或证明未超过所有软阈值。硬cgroup限制仍存在；采样保护对短瞬态有盲区，未因补资源数字重复native实验。长测试下一次应增加在进程内事件点读`/proc/self/status`及cgroup峰值，提前登记，不在业务窗内偷偷增加采样开销。

日志每个create/call/close保存CLOCK_MONOTONIC纳秒事件，顺序清楚；借用函数随exports vector统一释放，不重复删除borrowed func。两次均在Store删除前完成全部Instance/exports关闭，退出后MainPID0、unit inactive。未见trap、native崩溃、错误或超时。这不是资源长期回收、Store对象表不增长、WASI线程释放或并发安全的充分证据。

业务结果/Gas列为**不适用/未测**：这里是C API恒定返回样例，不调用ChainMaker CallMethod或计算Gas，不能填写业务成功/同Gas。没有运行Go race；即便通过也不能认证native。

恢复时只读PROGRESS、raw_logs/*-outcome.json、unit状态；当前两个进程已结束，不再运行脚本补“更多次数”。本轮原始数据只支持API串行路径工作，不支持任何新TPS数字。
