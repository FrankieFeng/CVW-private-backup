# Step-27：normalCal Reuse/Fresh/Copy执行差异诊断

分支`experiment/step27-normalcal-diagnostic`，父`81e1c0a`。已真实执行新增有界对照；不制作PPT，不改生产VM/Gas/合约，不push。主结论、全部Median/P95/CI/正向比例、批次/顺序和CPU/GC诊断见[NORMALCAL_ANALYSIS.md](NORMALCAL_ANALYSIS.md)。

## 结论

历史原件在同一个Store、同一个已编译Module、固定owner串行模型中，Fresh export点估计快1.293ms，但95%CI [−0.079,2.405]跨零，没有稳定复现旧8.294ms。原3批中位数均小幅同方向，但首笔normalCal与业务后复用分层不同，不能称Fresh普遍更快。完整同步Invoke中Fresh反而更慢，R0−R1=−3.978ms，CI [−4.959,−2.490]；初始化及关闭成本进入关键路径，不能把Guest窗口排序当整笔排序。

Step18家族的Reuse/Fresh export方向不同且CI跨零；Copy/A的长业务净收益也会被Guest窗口波动抵消。原件Copy相对Fresh完整Invoke节省0.405ms，CI跨零；Step18 A+Copy相对Fresh节省3.540ms、CI为正，但A+Copy相对Copy直接差−0.518ms、CI跨零，未证明进一步优于Copy。不同直接边在各自进程测量，不能相减独立Median构造因果或未测全局四组排序。

机制未唯一定位。主运行的host GC指标是外层窗口，不是Guest GC；独立诊断测量期host GC为0也出现正反方向，不能归因单一host GC。Guest运行时历史、内存/JIT布局、CPU频率和调度均仍是候选，未取得Guest栈或可靠Guest GC计数。

## 家族与无法字面满足的部分

| 家族 | 可执行组 | 原始WASM/范围 |
|---|---|---|
| original | R0、R1、C1 | 与21E/24B同compute e8b1fe...；C1用对应noData模块 |
| original | C2 | blocked：匹配原件A构建未恢复，未伪造替代 |
| step18 | R0、R1、C1、C2 | R0/R1/C1同plain P0原件；C2为同源A布局变体，hash不同 |

A改变WASM布局，所以不能声称四组字面使用同一hash。两家族从不拼接绝对耗时、Gas或CI。三个输入二进制都通过实际反汇编核实normalCal循环10000000，见audit/workload-check；没有为倍率修改负载。MATRIX记录Source SHA/代码和binary；Module/template准备原hash与计时在MODULE_PREPARATION，实际Store/Module/Instance及prior uses在TIMING。

## 执行和生命周期

先6个功能/生命周期预检，每个2对；通过后主六条family/edge分别3批×5独立进程×2对=30对，90进程/180对。对内ABBA/BAAB、跨进程首次先后交替、第二批反转edge顺序，无100ms Sleep。另6进程每个1对CPU/GC诊断，原件R0单独业务预热一次（仅诊断），不混入主性能。总102测试进程/198配对均通过，全部失败/无效准备记录保留。

R0/R1真正共享一个Store/Module：R0保留init实例；R1每次创建/执行/显式关闭后再继续；总3个WASI/Store，不增加原22/24B单Store预算。每个R0仅两次正式调用，首次此前只init，第二次此前一次normalCal；保留全部，不冒充同R0连续10次。Fresh组合每变体独占Store+Module，各init+2实例、最多6个WASI/进程。没有恢复原池grow/异步close，没有全局锁。

更完整安全论证和边界见[LIFECYCLE_AUDIT.md](LIFECYCLE_AUDIT.md)，正确性与未测范围见[CORRECTNESS.md](CORRECTNESS.md)。原managed.go、Gas getter/setter、opcode映射、Data transformer字节保持原样；source.diff只有实验准备/记录/诊断。原关闭base守卫保留，Reuse逐次profile重置，最终R0 Close单列。

## 数据字段与计时

完整Invoke继承参考管理器边界：包含同步Fresh创建、Copy、WASI/_start、SetGas/CallMethod/GetGas和每次关闭，排除一次性prepare/Module/init、外部账本clone/receipt输出及最终缓存关闭。R0 cache hit无每次创建/start/close，相应字段0；最终释放仍有记录。NewInstance不包含Copy；CallMethod包含exportFunc.Call，不能重复相加。所有同进程耗时用单调时间，不跨进程相减时钟。

主程序只在f.run外用runtime/metrics记录host GC周期、heap objects和pause histogram；它还包含上下文/receipt开销，不能定位Guest内部暂停。诊断使用RUSAGE_THREAD和MemStats、位于原B5边界外，CallMethod/Invoke包含这些探针开销，diagnostic完全单列。没有CPU栈采样/Guest栈，owner CPU加实际WASM路径是本轮执行证据，Guest GC明确不可观测。

## 历史与新数据独立性

HISTORICAL_AUDIT列出旧池b/c/d各300次、21E两个反向短批、25 Fresh组合及26只复算的来源。600旧B5重读/关联不是600次新实验；Step26没有新增normalCal样本。旧InvokeTime池路径、21E预建4个Store和本轮同Store同步创建模型不同，历史与新批不合并计算。

## 复算和恢复

```bash
cd /home/frankie/mygitprojects/.worktrees/cvw-step27/experiments/instance-lifecycle/step-27-normalcal-diagnostic
python3 -B scripts/history.py
python3 -B scripts/analyze.py
python3 -B scripts/report.py
python3 -B scripts/verify.py
```

这些只读复算，不运行Guest。动态原命令和完整env/binary保存raw_logs/*-command.json，套件scripts/suite.py用于历史复现说明，不需要再运行；先读PROGRESS和state，不重复有效label或在长时间无输出时盲目重启。原所有进程已退出，若STOP出现只分析，不清除重跑。

本机binary/native未入Git，native SHA固定dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9；其他workspace依赖沿原CVW，见go.work。新构建需独立label/新binary/provenance，不覆盖原build。代码冻结commit在MATRIX及每process provenance中，对应build2源码hash；commit归档于采样后，明确为事后逐字核验，不伪装为采样时HEAD。

回退为离开实验worktree，生产VM/服务无改动需要回滚。不删除历史、不push。当前证据不支持原池并发/生产启用，也没有要求本轮彻底解决长期Store资源问题。
