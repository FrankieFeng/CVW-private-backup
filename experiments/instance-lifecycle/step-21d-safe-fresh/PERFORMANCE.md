# 性能计时和供给机制核对

这里只报告**新安全实现的小样本成本**。主表为build12同一binary、ETHEREUM地址模式、相同WASM/业务输入，无逐调用强制GC；每条件一个独立进程。compute每组3次，exchange每组1根，不能据此认证稳态或普遍倍率，不发布TPS。

## 实测小样本（ms）

| 方法/模式 | Invoke均值 | CallMethod均值 | bundle创建均值 | 其中编译均值 | bundle关闭均值 |
|---|---:|---:|---:|---:|---:|
| bigNumCal R0 | 196.882 | 0.256 | 589.474 | 583.958 | 3.615 |
| bigNumCal R1 | 573.186 | 0.293 | 568.977 | 563.952 | 3.750 |
| normalCal R0 | 278.715 | 77.728 | 602.341 | 597.716 | 3.651 |
| normalCal R1 | 656.240 | 73.175 | 578.186 | 573.038 | 4.551 |
| buyNow R0 | 7.482 | 7.358 | 622.758 | 616.948 | 4.312 |
| buyNow R1 | 4557.583 | 4022.264 | 637.195 | 632.170 | 4.746 |

compute包含首笔冷创建，没有删掉首样本；R0后两笔Invoke均值分别0.366/79.296ms，单列说明冷态效应，不替代全样本主表。exchange已在前置真实init创建过R0的三个bundle，所以根调用没有首次编译；R1三次init关闭，根/六子再次各自创建。创建/关闭均值按进程内所有bundle计，exchange包含初始化，不能加到表内根Invoke或解释为根只创建一次。

buyNow的CallMethod包含六个子合约编译/创建/执行/关闭，是inclusive，不是纯业务CPU；根耗时不能再加六个子耗时。Gas差4379使buyNow两模式不具备严格Gas等价。normalCal少量CallMethod差异没有重复批次/调度控制，本轮不把它命名为Fresh优势或重新证明Step21A的8ms机制。

## 与Step21容量修复版的机制差异

| 项目 | Step21容量修复版 | 本轮安全参考 |
|---|---|---|
| Store/Module | 每合约池共享Store，Module预编译 | R1每Invoke独立Store并重编Module；R0缓存一bundle |
| 创建供给 | 单worker后台grow，min5/max10/grow5，apply/add触发 | 无worker、无预填、无异步补充，需求到达同步构造 |
| GetInstance | 空池channel接收，等待后台供给 | 不调用原GetInstance；acquire是缓存查找/同步构造总时长 |
| 库存/排队 | 原有channel库存、借出及待remove计数 | 请求队列/库存0；R0缓存每合约1，R1仅同步在途栈 |
| 回收 | R1异步Close→remove→add，与创建/执行可能重叠 | R1 owner同步deallocate及scope清理，计入Invoke；R0最后关闭 |
| Finalizer | Go可能在其他线程删除native对象 | 自动native Finalizer改为所有者的确定清理登记，GC无native删除权 |
| 计时 | 原InvokeTime边界，预编译/验证通常窗外 | 自定义Invoke入口到全部defer完成；编译和R1关闭在窗内 |
| 观测/夹具 | 原TestInvoke/SnapshotMock及已有日志 | 真实VmManager/TxSimContext、逐笔receipt写盘、生命周期/proc事件 |

因此，本轮R1约0.57秒不能与旧3ms相减认定“池修复让性能下降多少”，也不能用新R0/R1的差值宣称复现原10–15倍。两者对象/供给/上下文/计时都不同。原grow容量裁剪在正常apply/add/refresh/reset都生效的结论仍成立；本轮没有量化其单独影响，也没有恢复该不安全共享路径。

## 等待、供给与资源如何解释

`acquire_ns`是新路径的总获取时间，R1包含同步编译/创建；compute R1约568.998/578.215ms。没有channel，`channel_block_ns=0`来自结构本身，**不代表原GetInstance已实测零等待**，该旧指标在本实现不适用。

R1的创建窗口观测速率约bigNum1.744次/秒、normal1.585次/秒，完整值在summary.csv的`observed_create_per_s_not_steady`。这只是本次3个创建完成数/首创建至末创建的窗口，含中间业务/日志/receipt，不是稳态供给能力；`steady_supply_rate`明确为未建立。没有后台库存可测，库存0不能与原池借出后queue_len比较。

逐笔事件含创建/编译/执行/关闭纳秒、Instance ID/previous_uses、scope计数、线程/RSS及单调时间线；外部资源JSONL补充进程采样。事件读/proc和日志开销没有单独校准，CallMethod窗口紧贴实际调用，但总Invoke含诊断开销。最终资源峰值见README，长期RSS尚未验证。

所有自定义时长采用time.Sub/time.Since单调时钟。旧vm_factory输出仍按UnixNano，不改生产依赖；早期回拨产生的负数日志保留，不用于主统计。
