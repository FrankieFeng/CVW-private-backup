# normalCal：较小的Guest窗口倾向仍可见，8ms及机制未确认

本轮**真实新增**102个有界独立进程，180个正式直接配对（360次目标调用），另有12个预检配对和6个独立诊断配对。全部进程成功退出，无生命周期/资源保护失败；首次build1为unused import编译失败，未执行Guest，原记录保留。主性能和诊断分别统计，历史数据不混入CI。

## 直接回答

1. 历史原件、同Store/同Module的R0/R1：Fresh export窗口点估计快1.293ms，三批中位数0.780/1.357/1.285ms均同方向，但总体95%CI [−0.079, 2.405]跨零。**没有稳定复现历史8.294ms，也不能据此确认Fresh必然更快。**
2. Step18家族的同Store/同ModuleR0/R1：export点估计反向1.428ms（Fresh更慢），CI跨零，第三批反转；它是独立家族，不能与原件混合或据此指定哪个二进制差异是原因。
3. 完整Invoke与export排序并不一致：原件R0比Fresh快3.978ms，95%CI排除零。Fresh需要同步支付创建/WASI/start/关闭，R0已初始化且不逐次关闭；原池提前供给的历史Invoke窗口不能与此直接比绝对值。Step18完整Invoke也支持R0快。
4. 原件Copy相对Fresh的完整Invoke节省0.405ms，CI跨零；Step18 Copy节省1.487ms也跨零。Step18 A+Copy相对Fresh节省3.540ms、CI为正，但相对Copy的直接增量为−0.518ms、CI跨零。不能拿两条独立Median差推出A必然优于Copy。
5. 主调用先后和复用历史影响观察：原件R0第一笔normalCal（此前仅init）对比Fresh，export节省2.141ms；R0第二笔（此前已有1次normalCal）为−0.444ms、CI跨零。pair slot也耦合时间位置、对内顺序和Fresh实例序号，不能唯一认定Go缓存或“预热”因果。
6. 主运行host GC外层计数与Guest GC不同；12条测量期CPU诊断中host GC/pause增量均0，export/CPU差仍有正反方向，不能把现象唯一归因host GC。Guest GC、CPU频率、JIT/内存布局及Windows/内核调度未定位。
7. 两家族内所有组Gas/返回/根RWSet/事件/账本均一致；原件100000072、Step18 100000019，分开报告。Copy成功路径与S1预检通过；A使用不同WASM，原件C2仍blocked，Table/异常/跨合约/长期回收未测试。

## 两个家族与四组的边界

原件R0/R1/C1使用相同原始compute SHA e8b1fe...，C1执行对应noData；原件匹配A构建未恢复，不能生成其C2。完整四组只在Step18家族单列，R0/R1/C1同原件，C2是既有A布局产物（不同hash）。三份实际WASM normalCal反汇编都核实10000000循环，没有改业务或Gas。没有字面“同一WASM但又加A”的虚构承诺。

R0/R1每个进程真正共用一个Store和一个已编译Module；Source/Store/Module ID、Instance ID和prior uses均原样记录。R0保留init实例，R1逐次新建、同步关闭，总共3个WASI/Store。每批10对由5进程各2对组成，不能说同一个R0连跑10次；每个R0只有两次正式业务，第一笔不能当长期业务热态。R0最终Close单列，不摊到每次Reuse；其Close=0不是未释放，而是没有逐次关闭。

## 新主数据：直接配对统计

正值=左−右、右侧更快。每条主edge30对/3批/15进程；Invoke与export嵌套，不能加列。95%CI为batch→process聚类bootstrap，10000次、seed270027、每process2对整体抽样；P95线性分位数。非30完全独立实验，多重比较未校正。

| 家族 | 对照 | 窗口 | 左Median/P95 ms | 右Median/P95 ms | 配对节省Median [95%CI] ms | 正向/30 |
|---|---|---|---:|---:|---:|---:|
| original | R0→R1 | export_call_ns | 74.208/82.517 | 73.598/80.398 | 1.293 [-0.079, 2.405] | 19 |
| original | R0→R1 | invoke_ns | 74.507/82.726 | 79.127/84.872 | -3.978 [-4.959, -2.490] | 3 |
| original | R1→C1 | export_call_ns | 74.369/78.314 | 74.721/80.110 | -0.419 [-1.624, 0.190] | 11 |
| original | R1→C1 | invoke_ns | 79.395/84.552 | 79.539/85.044 | 0.405 [-1.008, 1.214] | 16 |
| step18 | C1→C2 | export_call_ns | 73.536/86.765 | 75.569/83.959 | -0.987 [-3.875, 1.749] | 12 |
| step18 | C1→C2 | invoke_ns | 78.934/94.023 | 80.189/88.147 | -0.518 [-3.299, 1.656] | 13 |
| step18 | R0→R1 | export_call_ns | 72.164/86.609 | 74.569/82.833 | -1.428 [-2.917, 2.330] | 13 |
| step18 | R0→R1 | invoke_ns | 72.373/86.902 | 79.175/87.739 | -5.774 [-6.627, -1.624] | 2 |
| step18 | R1→C1 | export_call_ns | 75.052/80.904 | 74.780/80.394 | 0.519 [-1.458, 1.811] | 17 |
| step18 | R1→C1 | invoke_ns | 81.453/87.588 | 79.713/85.458 | 1.487 [-0.688, 3.096] | 19 |
| step18 | R1→C2 | export_call_ns | 77.105/82.613 | 74.757/82.954 | 1.432 [0.219, 4.441] | 21 |
| step18 | R1→C2 | invoke_ns | 82.246/89.357 | 78.854/86.822 | 3.540 [1.480, 4.568] | 23 |

这些边在不同独立进程中测量，尤其R0/R1共享Store而Fresh组合是各自Module/Store；不能把某条边的R1边际中位数挪给另一条边，也不能构造未直接测的全局四组排序。

## 批次分层

| 家族 | 对照 | 窗口 | 批次 | N | 直接差Median ms | 正向 |
|---|---|---|---:|---:|---:|---:|
| original | R0→R1 | export_call_ns | 1 | 10 | 0.780 | 6 |
| original | R0→R1 | export_call_ns | 2 | 10 | 1.357 | 7 |
| original | R0→R1 | export_call_ns | 3 | 10 | 1.285 | 6 |
| original | R0→R1 | invoke_ns | 1 | 10 | -4.358 | 1 |
| original | R0→R1 | invoke_ns | 2 | 10 | -3.347 | 2 |
| original | R0→R1 | invoke_ns | 3 | 10 | -3.638 | 0 |
| original | R1→C1 | export_call_ns | 1 | 10 | -0.520 | 4 |
| original | R1→C1 | export_call_ns | 2 | 10 | -0.958 | 3 |
| original | R1→C1 | export_call_ns | 3 | 10 | -0.164 | 4 |
| original | R1→C1 | invoke_ns | 1 | 10 | -0.353 | 5 |
| original | R1→C1 | invoke_ns | 2 | 10 | 0.212 | 5 |
| original | R1→C1 | invoke_ns | 3 | 10 | 0.931 | 6 |
| step18 | C1→C2 | export_call_ns | 1 | 10 | -0.160 | 4 |
| step18 | C1→C2 | export_call_ns | 2 | 10 | -0.757 | 5 |
| step18 | C1→C2 | export_call_ns | 3 | 10 | -2.224 | 3 |
| step18 | C1→C2 | invoke_ns | 1 | 10 | 0.507 | 5 |
| step18 | C1→C2 | invoke_ns | 2 | 10 | 0.206 | 5 |
| step18 | C1→C2 | invoke_ns | 3 | 10 | -1.176 | 3 |
| step18 | R0→R1 | export_call_ns | 1 | 10 | -2.545 | 3 |
| step18 | R0→R1 | export_call_ns | 2 | 10 | -1.648 | 3 |
| step18 | R0→R1 | export_call_ns | 3 | 10 | 2.635 | 7 |
| step18 | R0→R1 | invoke_ns | 1 | 10 | -6.576 | 0 |
| step18 | R0→R1 | invoke_ns | 2 | 10 | -6.109 | 0 |
| step18 | R0→R1 | invoke_ns | 3 | 10 | -1.624 | 2 |
| step18 | R1→C1 | export_call_ns | 1 | 10 | 0.066 | 5 |
| step18 | R1→C1 | export_call_ns | 2 | 10 | 1.811 | 7 |
| step18 | R1→C1 | export_call_ns | 3 | 10 | -0.304 | 5 |
| step18 | R1→C1 | invoke_ns | 1 | 10 | 0.995 | 6 |
| step18 | R1→C1 | invoke_ns | 2 | 10 | 2.744 | 8 |
| step18 | R1→C1 | invoke_ns | 3 | 10 | -0.146 | 5 |
| step18 | R1→C2 | export_call_ns | 1 | 10 | 0.411 | 6 |
| step18 | R1→C2 | export_call_ns | 2 | 10 | 3.492 | 7 |
| step18 | R1→C2 | export_call_ns | 3 | 10 | 2.290 | 8 |
| step18 | R1→C2 | invoke_ns | 1 | 10 | 2.835 | 7 |
| step18 | R1→C2 | invoke_ns | 2 | 10 | 3.633 | 7 |
| step18 | R1→C2 | invoke_ns | 3 | 10 | 4.001 | 9 |

## 顺序与复用历史

| 家族 | 对照 | 窗口 | 因素/值 | N | 差Median [95%CI] ms |
|---|---|---|---|---:|---:|
| original | R0→R1 | export | first=A0 | 15 | 1.153 [-1.384, 2.532] |
| original | R0→R1 | export | first=A1 | 15 | 1.312 [-0.030, 2.984] |
| original | R0→R1 | export | pair=0 | 15 | 2.141 [0.286, 3.778] |
| original | R0→R1 | export | pair=1 | 15 | -0.444 [-1.384, 1.906] |
| original | R1→C1 | export | first=A0 | 15 | -0.214 [-1.374, 1.879] |
| original | R1→C1 | export | first=A1 | 15 | -0.524 [-4.358, 0.633] |
| original | R1→C1 | export | module_first=A0 | 12 | -0.414 [-8.546, -0.115] |
| original | R1→C1 | export | module_first=A1 | 18 | -0.525 [-1.713, 0.411] |
| original | R1→C1 | export | pair=0 | 15 | -1.002 [-4.358, 1.553] |
| original | R1→C1 | export | pair=1 | 15 | -0.305 [-1.374, 1.879] |
| step18 | C1→C2 | export | first=A0 | 15 | -3.995 [-5.744, -0.163] |
| step18 | C1→C2 | export | first=A1 | 15 | 1.871 [-1.039, 5.207] |
| step18 | C1→C2 | export | module_first=A0 | 18 | -0.726 [-4.771, 2.499] |
| step18 | C1→C2 | export | module_first=A1 | 12 | -0.987 [-2.372, -0.219] |
| step18 | C1→C2 | export | pair=0 | 15 | -0.934 [-3.995, 2.764] |
| step18 | C1→C2 | export | pair=1 | 15 | -2.504 [-4.975, 2.499] |
| step18 | R0→R1 | export | first=A0 | 15 | -1.638 [-3.571, 2.330] |
| step18 | R0→R1 | export | first=A1 | 15 | 0.714 [-3.624, 2.941] |
| step18 | R0→R1 | export | pair=0 | 15 | -2.173 [-3.738, 1.730] |
| step18 | R0→R1 | export | pair=1 | 15 | 1.218 [-2.123, 2.941] |
| step18 | R1→C1 | export | first=A0 | 15 | 0.189 [-2.386, 1.914] |
| step18 | R1→C1 | export | first=A1 | 15 | 1.425 [-2.757, 3.310] |
| step18 | R1→C1 | export | module_first=A0 | 18 | -0.055 [-2.119, 1.811] |
| step18 | R1→C1 | export | module_first=A1 | 12 | 0.867 [-2.374, 3.097] |
| step18 | R1→C1 | export | pair=0 | 15 | 0.189 [-2.119, 3.851] |
| step18 | R1→C1 | export | pair=1 | 15 | 0.608 [-3.255, 1.707] |
| step18 | R1→C2 | export | first=A0 | 15 | 0.469 [-2.252, 3.596] |
| step18 | R1→C2 | export | first=A1 | 15 | 3.347 [0.209, 8.234] |
| step18 | R1→C2 | export | module_first=A0 | 12 | 0.650 [-6.518, 4.441] |
| step18 | R1→C2 | export | module_first=A1 | 18 | 2.280 [0.229, 5.388] |
| step18 | R1→C2 | export | pair=0 | 15 | 3.347 [-2.214, 10.146] |
| step18 | R1→C2 | export | pair=1 | 15 | 0.594 [-1.166, 4.440] |

A0/A1在顺序表仅代表该进程左右角色；共享R0/R1只编译一个Module，因此没有“哪个Module先编译”的分层。左右执行先后15/15配对平衡；非共享边的Module准备顺序按进程交替，15进程最多8/7不完全相等。所有原始反向和首笔样本保留，不因顺序不利删去。

原件左右先执行的export分层CI都跨零。首笔/第二笔结果有变化，但这不是单因素随机化的Guest缓存干预；不把“前一次执行过normalCal”与温度、时间位置、内存或调度效应自动等同。

## GC、CPU与执行路径

主性能在f.run前后用runtime/metrics，包含host上下文/receipt处理的外层计数，总host GC周期增量77，不能宣称77次发生在export。精确pause只在诊断MemStats取得；主数据保留pause histogram上下界。Host Go与WASM内Go是两个运行时，Guest GC一律not_observed。

独立诊断（原件R0有1次业务预热，Step18 Copy/A均Fresh；各1对/3进程）不进入主CI：

| 家族 | 批 | 组 | export wall ms | owner线程CPU ms | host GC/pause ns |
|---|---:|---|---:|---:|---:|
| original | 1 | R1 | 78.855 | 72.779 | 0/0 |
| original | 1 | R0 | 77.824 | 72.668 | 0/0 |
| original | 2 | R0 | 74.880 | 74.292 | 0/0 |
| original | 2 | R1 | 78.742 | 76.466 | 0/0 |
| original | 3 | R1 | 72.674 | 68.812 | 0/0 |
| original | 3 | R0 | 72.810 | 71.167 | 0/0 |
| step18 | 1 | C2 | 74.129 | 71.825 | 0/0 |
| step18 | 1 | C1 | 77.293 | 75.740 | 0/0 |
| step18 | 2 | C1 | 77.780 | 76.490 | 0/0 |
| step18 | 2 | C2 | 85.918 | 84.077 | 0/0 |
| step18 | 3 | C2 | 73.248 | 68.885 | 0/0 |
| step18 | 3 | C1 | 76.720 | 73.710 | 0/0 |

该诊断的原B5 wall边界仍紧贴Call；RUSAGE_THREAD和MemStats位于其外，完整Invoke/CallMethod包含诊断开销，不能替代主性能。owner线程CPU不是所有native线程CPU，也不是指令计数；wall−CPU不能直接全算调度等待。CPU差和wall差方向/幅度都变化，当前证据不支持单一“off-CPU等待”或“host GC”解释。

本轮未采CPU堆栈信号样本，使用owner CPU与实际WASM路径作为替代证据；没有Guest符号动态调用栈、Guest GC计数/暂停、Windows调度/温度/物理频率。未猜测内存偏移读取Guest状态，没有为追平Gas清除R0缓存或重写合约。

## 已证实、假设与未定位

- 已证实：旧600条差在宽export窗口；新同Store对照没有稳定8ms幅度；原件三批点估计Fresh稍快但总体CI跨零；完整同步Invoke中Fresh明确更慢。Store/Module身份和每次生命周期边界有原日志证据。
- 已证实：Copy和A的初始化窗口有改变，但长normalCal的export波动会抵消/放大整笔净收益；C1/C2直接差未证明A带来稳定增量。
- 合理假设：R0 Guest运行时历史、内存/代码布局及CPU/调度状态会影响导出耗时。首笔/第二笔与两家族方向不同提供线索，但不是唯一归因。
- 未定位：具体Guest函数/分支、Guest GC、JIT/缓存/频率分别贡献多少。不能把相同Gas当相同指令路径，也不能因host GC为0排除Guest GC。

下一步若继续，需保持同Module串行协议，明确区分init后首次业务与已有业务历史，并获得可审计Guest GC/执行路径或时钟/调度证据；这不是本轮已实现的新优化。原件A构建仍待恢复，不能跨家族替代。

## 资源与退出

102个测试进程均退出；峰值RSS 401.23MiB、host heap objects 63.56MiB、线程109，没有触发768MiB/125线程软限。实例与Scope守卫全部通过；每Store最多3个WASI，不能据此认证长寿命Store有界。表格资源是整进程，不拆为某一模式精确消耗。
