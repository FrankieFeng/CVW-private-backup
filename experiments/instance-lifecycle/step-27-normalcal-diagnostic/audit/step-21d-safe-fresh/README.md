# Step21D：安全Fresh Instance生命周期基线

2026-10-26，Asia/Shanghai。分支`experiment/step21d-safe-fresh`，父提交Step21B `620650d`；选择使用Step21C `32d257b`夹具，不合并其整个分支。**已建立并实测一个有界的串行参考实现；尚未放行100次、并发补池或Copy。**

## 最终六问

| 问题 | 答案 |
|---|---|
| Store所有权与回收模型？ | 采用B的串行版本：每次R1 Invoke全新Store、在该Store编译的Module、同Store host imports/WASI/Instance。全部由固定OS线程创建、执行、显式销毁。绑定的自动native Finalizer改为有界强引用scope清理，最终独立进程退出/join提供残留native资源的隔离终点。 |
| 允许哪些并发？ | **没有放行应用层Wasmer C API并发创建/执行/关闭**。允许同一所有者上的串行操作、独立Store的同步父子调用；同Store重入只限原GetGas/SetGas且最多两层。不同Store不自动等于当前Go绑定可多线程运行。 |
| 真正执行了什么？ | 最终同一build12：bigNumCal、normalCal各R0/R1连续3次，全部真实返回/Gas通过；buyNow各模式1根，均实际完成六个callee、状态及事件断言。另验证跨线程拒绝、创建失败回滚、关闭报错后继续回收。 |
| 能安全运行100次Fresh吗？ | **本轮不具备准入条件，也没有执行**。逐次编译约0.56–0.63秒，100次已经超出45秒测试预算；buyNow每根约4.56秒。长期RSS/线程回收及native精确构建来源仍未闭合。源码及运行器目前限制compute≤3、exchange=1。 |
| 对计时和供给有什么影响？ | 取消原后台池，需求到达后同步创建，库存/排队0；编译、WASI、start与R1显式关闭进入Invoke，GetInstance channel阻塞不存在。它是新参考基线，不能称原实例池性能；旧容量补丁也不再是当前控制策略。 |
| 可以继续21C/22吗？ | **可以在此边界内继续21C小样本真实功能诊断；不能进入原池100次或Step22补池性能测试**。先解决可控构建、跨Store编译模块复用/所有者并行、长期资源及Gas差异，再登记新实验。 |

## 最终验证结果

| 方法 | R0/R1目标调用数 | 实际结果 | R0/R1 Gas |
|---|---:|---|---|
| compute.bigNumCal | 3 / 3 | success bigNumCal: 607723520 | 105920 / 105920 |
| compute.normalCal | 3 / 3 | success normalCal: 666 | 100000072 / 100000072 |
| exchange.buyNow | 1 / 1 | buyNow success；每根7个真实Invoke、子深度1 | **12761395 / 12765774，不等价** |

最终7个进程（6个业务条件+1个所有权/错误处理预检）均exit0；14个目标根调用、含初始化/子调用共32个真实VM调用。Fresh compute各创建/关闭3个bundle；Fresh exchange包含3个init和根+6子，共10个；R0 exchange3个bundle复用，仅作参考。所有进程在途0、清理登记0、创建数=关闭数，已停止。

事件和外部采样合并的最终峰值约681.24MiB/57线程，低于1536MiB/220软限；硬限2GiB/256任务/60秒，Go timeout45秒，未提高。样本短，**不认证长期内存有界或每次native线程已全部join**。scope清理返回与进程最终退出分开记录。

全开发过程23个测试进程，17通过、6失败，全部留档；失败包含夹具配置/断言/准备错误，不隐藏为通过。主表只使用`final-*`同版本结果，早期逐调用强制GC的诊断不混入。细节见[验证报告](VALIDATION.md)。

## 文件与恢复

- [DESIGN.md](DESIGN.md)、[OWNERSHIP.md](OWNERSHIP.md)：方案选择、对象/线程/回收边界及源码行号。
- [VALIDATION.md](VALIDATION.md)：真实业务、六callee、失败记录、安全门及未测项。
- [PERFORMANCE.md](PERFORMANCE.md)：新旧计时/供给机制比较，小样本耗时，禁止跨版本倍率推断。
- [NEXT_STEP.md](NEXT_STEP.md)、[PROGRESS.md](PROGRESS.md)：阻塞项、后续步骤和恢复入口。
- [source.patch](source.patch)、[source/vm](source/vm/)：相对21C的实验源码差异和可构建复制模块；生产VM路径没有改动。
- [summary.csv](summary.csv)、[samples.csv](samples.csv)、[correctness.csv](correctness.csv)、[lifecycle_events.csv](lifecycle_events.csv)、[all_processes.csv](all_processes.csv)：仅分析已有日志即可重建。
- [environment.json](environment.json)、[audit](audit/)、[raw_logs](raw_logs/)：版本、原始命令、失败/成功日志、receipt、资源、退出状态。旧B/C原件保持原样。

恢复后先读PROGRESS与已有outcome，确认unit状态；只读复算`python3 -B scripts/analyze.py`。不要重启已有标签，不自动放宽次数。构建不运行guest；本地环境恢复说明见[REPRODUCE.md](REPRODUCE.md)。没有push，没有Copy/Arena/PB，没有修改代理、WSL、VS Code或生产生命周期/Gas。
