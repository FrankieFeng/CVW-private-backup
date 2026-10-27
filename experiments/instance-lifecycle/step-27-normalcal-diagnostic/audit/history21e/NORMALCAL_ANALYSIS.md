# normalCal：导出窗口小幅同方向复现，机制未解释

历史约8.294ms差异已经从600条原始B5逐次重算；本轮两个反向顺序短批里Fresh导出窗口均较快，但仅1.486/3.019ms。不能宣称稳定复现历史8ms，更不能把Fresh实例供给或总Invoke说成更快。

## 历史数据复核

有效b/c/d各100次/模式，重读6个原始log与samples.csv，按sample原始行向前寻找对应B5，并严格核对Instance ID与CallMethod纳秒数。原始日志已冻结[audit/history-source](audit/history-source/)，manifest保存来源与hash；逐笔输出[audit/history-normal-samples.csv](audit/history-normal-samples.csv)。

| 旧容量修复版均值（ms） | R0，300次 | R1，300次 | R0−R1 |
|---|---:|---:|---:|
| Invoke | 82.118 | 73.871 | 8.247 |
| CallMethod | 81.975 | 73.675 | 8.300 |
| exportFunc.Call | 81.739 | 73.445 | 8.294 |

这证明历史差异落在exportFunc.Call的宽窗口，非大部分GetInstance/allocate耗时。但该窗口含guest循环、runtime/SDK、SuccessResult宿主回调以及调度/GC；不是纯循环CPU时间。旧负载存在后台创建/关闭区间交叠，当前不安全条件不能原样恢复重跑。

## 本轮受控小样本

同compute WASM SHA `e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507`、无业务参数、固定TxID、Gas均100000072、返回success normalCal:666。实际反汇编含10000000循环与相关Gas扣减；常量返回自身不能证明循环工作量。未修改WASM或Gas。

先完成两个bundle的AB预检，再每独立进程预建R0一个和R1三个bundle；创建/编译全部在测量前，最大同时4个独立Store，单OS线程串行执行。R0预热1次不入统计，Fresh无业务预热；测量顺序ABBAAB与BAABBA，A=R0、B=R1，各3次。R0运行时历史与Fresh初态刻意不同，不能称全部内部状态相同。所有正常日志设置一致，Gas密集探针关闭，未在调用间强制GC。

| 批次 | 模式 | n | Invoke ms | CallMethod ms | export ms | owner线程CPU ms | export窗口host GC次数合计 |
|---|---|---:|---:|---:|---:|---:|---:|
| ABBAAB | R0 | 3 | 77.925 | 77.692 | 77.398 | 76.029 | 0 |
| ABBAAB | R1 | 3 | 81.161 | 76.324 | 75.912 | 71.119 | 2 |
| BAABBA | R0 | 3 | 78.807 | 78.606 | 78.270 | 74.826 | 2 |
| BAABBA | R1 | 3 | 80.643 | 75.808 | 75.251 | 70.802 | 0 |

来源：[normal_samples.csv](normal_samples.csv)、[normal_summary.csv](normal_summary.csv)、[export_profiles.csv](export_profiles.csv)、[两批receipt/资源日志](raw_logs/)。Invoke仍包含R1关闭，故R1整笔更慢；CallMethod与export嵌套，不相加。资源峰值AB/BA约737.01/750.85MiB、74线程，预建多个WASI带来的资源布局不同于原池。

## 能排除和不能解释的部分

- 新小样本同方向出现在两种相反顺序；未发现参数、WASM、Gas或host syscall数量改变。并非仅一次先后顺序造成的观测。样本小且共享同一机器时段，不能据此做统计稳定性认证。
- CPU时使用固定owner `getrusage(RUSAGE_THREAD)`；两批R1平均CPU亦较少（约4.91/4.02ms）。因此新差异不能全由该线程的off-CPU等待解释；仍不区分CPU频率、原生代码/内存布局、guest runtime状态、采样粒度、host回调工作。
- `runtime.ReadMemStats`只测**host Go**，host GC出现模式随批次改变；第一批R0无GC、第二批R1无GC，仍同方向。没有证据将差异归咎于host GC，更不能把host NumGC当guest GC。
- 原有B5 export计时边界仍紧贴exportFunc.Call；额外线程CPU/host统计包在其外，因此CallMethod含观测开销。本轮eMeasure export_ns与B5仅有边界开销差，未把ReadMemStats停顿算入原B5 export。本轮表使用eMeasure紧贴Call的外层时钟，包含两次原B5计时边界的极小开销；原B5字段仍在内层计算，本实验Runtime没有另输出该字段，不宣称逐条量化两时钟之差。详细探针实现见step21e_probe.go与sim_context.go。
- guest包含runtime.gcStart符号，但无ReadMemStats业务导出/DWARF，GC次数/暂停未测；没有向WASM加探针或推测固定偏移读取guest GC。WSL的物理频率、温度和宿主Windows调度也未观测。

结论是**导出调用窗口的小幅同方向现象可在本次有限串行样本观察到，历史约8ms幅度及具体机制尚未稳定解释**。进一步定位需要可审计的guest runtime观测或同编译代码/同资源布局的串行对照，先在同样小预算下设计，不能跳到100次或不安全后台补池。这个未知阻止声称执行阶段收益来自Copy/实例化优化；它不阻止小规模Fresh/Copy的功能与Gas一致性检查。
