# 历史证据恢复及独立性

本轮读原报告，同时重新读取冻结CSV和600条B5原日志，将Instance ID、sample_id、method和export_ns关联；CallMethod旧CSV由浮点转换，个别差1ns，保留这一精度限制，不把它当8ms效应。代码见scripts/history.py，结果HISTORICAL_RECOMPUTATION.csv，链接核查audit/history-raw-links.json。两个短批CSV还有2个normal-gate预检，未混入12个正式短批。

| 数据集 | 原WASM/代码 | 样本/独立批 | 顺序/状态 | 计时与可比性 |
|---|---|---|---|---|
| 旧Step21容量修复b/c/d | compute e8b1fe...；源码c6addbf，完整记录在原capacity-fix目录 | R0/R1各300，3批×100；每组独立进程 | 原池和后台供给；保留冷态；无100ms间隔 | InvokeTime日志窗口，实例可提前由池准备，非本轮同步创建全链路；有已知Store生命周期风险，不能安全照搬 |
| Step21E normal-ab | 原件e8b1fe...；507310c归档的诊断源码 | R0/R1各3，1独立进程 | ABBAAB；R0有1次业务预热；R1各独立预建bundle | 4个独立Store，编译/创建在测量前；Fresh关闭在Invoke内；额外CPU/host GC观察在B5外 |
| Step21E normal-ba | 同上 | R0/R1各3，另1独立进程 | BAABBA；同样预热 | 与normal-ab同模型，但不是本轮同Store模型 |
| Step25 normalCal | Step18同源plain及A/PB变体；be88d9a | 每条边18对/3批/9进程 | 两对/短进程，交替；只有Fresh组合，没有R0 | 原固定owner参考管理器，含每次创建/start/关闭，Module准备在外 |
| Step26 | 81e1c0a | 无新增normalCal样本 | 只复算3个其他方法的旧直接配对 | 不能算normalCal的独立重复，更不能和25累计样本数 |
| Step27 | 本轮source/binary hash见environment/MATRIX | 新样本单列 | 同Store R0/R1以及同协议Fresh组合 | 不能拼接旧批计算CI |

历史b/c/d均值R0/R1分别：Invoke82.118080/73.870941ms，差8.247139；CallMethod81.975486/73.675233ms，差8.300253；export81.739296/73.445268ms，差8.294028。它们是原多进程样本的描述性均值差，不是本轮逐对随机化效应。600条原始样本只是一份数据；Step21E报告的重新统计不是又新增600次。

原Step21E两个新短批export均值差R0−R1：ABBAAB为1.486065ms，BAABBA为3.019442ms，同方向但没有复现8ms幅度。它们是两次独立短过程，不是3个独立批，也没有足够样本证明稳定。两组Gas100000072，返回success normalCal:666，无业务参数；实际GoRuntime内部状态并不相等（R0已业务预热、R1未执行业务）。

旧原池的8ms差主要在宽export窗口，不是大部分GetInstance/Allocate；但该窗口含Guest运行时/SDK、末尾SuccessResult宿主回调、GC和调度，不是纯循环CPU。Step21E host线程CPU同向减少约4–5ms，仍不能唯一解释为频率/Guest路径/缓存。历史未可靠采集Guest GC、Windows调度和物理频率。

Step25 normalCal已有C1→A+Copy的负点估计且CI跨零，不能把相对Fresh某条边的正结果推导成相对Copy必然更快。本轮逐边新测并单列，不把25旧窗口与本轮不同Store历史直接相减。
