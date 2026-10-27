# 新数据前预登记

首先历史原件e8b1fe...做R0/R1同一Store/Module；若ABBA功能/关闭/owner/资源预检通过，再执行3独立批×5进程×2对=30对。R1/Copy使用同一原件、各模块同协议Fresh，另外直接对比。原件的C2匹配A构建仍blocked，不造替代品。

Step18家族另列四组：R0/R1/Copy基于同一plain p0原件；C2基于同源A布局变体，hash不同，不称字面同一WASM。对R0-R1、R1-C1、R1-C2、C1-C2分别执行3批×5进程×2对。所有结果按family/edge拆分，不把历史和新数据或两家族合并。

R0/R1同Store设置：只编译一次Module，所有WASI/import/Instance由固定owner串行操作，R0保留init实例，R1执行两次各新建/同步关闭，共3个WASI Instance/Store；没有新并发。每process R0仅2次正式复用调用，记录prior uses，保留第一次正式冷业务；不声称同一R0跑10次。对内次序ABBA/BAAB，5进程首次先后3/2，下一批翻转；Module准备顺序随slot+batch交替（共享对照只有一个Module，准备先后不适用）。各角色共享同一init账本副本，R0 guest状态不清，R1/C完全fresh。

Fresh Copy对照每角色独立Module/Store，对称真实init+2调用，各Store3个WASI/进程总6，不放宽24B预算。三个模块不同时放入一个进程，四组结果为各自直接边，不通过边的Median相减构造未测因果排序。

主计时继承25/22：NewInstance不含Copy，S1含Copy，S2含WASI/_start，S3含业务与Gas，Full Invoke含每次同步Close。R0就绪读取无NewInstance/start/Copy，最终保留Instance关闭单列，不平均摊入每笔。复用profile每次重置，保留原close baseline，原native关闭守卫不变。StoreID/ModuleID、source SHA、InstanceID、prior uses每次落盘，R0/R1要求前两者相同。

主运行使用runtime/metrics在目标调用外记录host GC cycles/heap objects/暂停histogram；其计数窗口还含外层RunContract及receipt处理，非Guest GC/精确export GC。ReadMemStats与owner线程RUSAGE只在单列diagnostic进程围住export，GC/CPU观察开销不混入主性能；原B5紧贴Call的计时保留。Guest GC无可靠导出，标not_observed，不猜偏移。CPU线程计时不等于指令数或CPU频率，也不提供Guest函数栈。

诊断：主功能通过且资源正常后，原件R0/R1各批1个独立1对diagnostic进程，R0预热1次原业务（仅诊断、单列、不入测量）；Step18 C1/C2各批1对diagnostic。按相反先后交替。无需native信号采样/pprof，采用线程CPU和原WASM执行路径证据；未获取CPU调用栈需明确说明。

RSS768MiB/线程125软限，2GiB/256task硬限，Go45s/process60s，available8GiB/swap1GiB；所有创建执行关闭同owner，无后台grow/异步close、无全局锁、无Guard豁免。任一资源/生命周期/语义异常保留STOP，停止对应配置，不凑数量。

主要效应left−right，Invoke/export各自逐对统计；batch→process聚类bootstrap10000次，seed270027，保留每process2对整体，线性P95；保留所有冷/热/反向样本。每个主edge30对/3批/15进程，非30完全独立；diagnostic、预检、历史数据不混入。多重比较未校正，顺序分层另列。
