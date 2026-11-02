# 执行设计与统计口径

## 冻结因素

Step36代码abc2ce35/节点依赖图c28bfa8，Step37静态分析72b916d8。Guest为Step36 plain G0同源8个合约，不重编业务WASM；仅native边界测试使用小WAT。Go host1.25.0、native6.0.1 Selector补丁SHA56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc；GOMAXPROCS2/GOGC100；Gas、编译器、512pages、Owner、同步Close不改。

10方法：compute.hashCal/bigNumCal/normalCal、fact.saveAndFindByFileHash、erc721.mint、exchange.buyNow、bigInput.inputSize（512KiB）、identity.address、itinerary.save、raffle.query。其余27方法没有新测，不能把一个方法的性能代替全合约方法结论。

## Step38A

F0无Copy参照；C0原Ranges；C1 gap≤16B；C2≤64B；C3≤256B；C4单span。每个独立进程只一种策略、一个方法，单Owner串行。先真实init/setup，两次业务预热（每次重置等价初始账本，Module缓存命中、Instance仍fresh），再两次正式目标。正式前每笔恢复同一initial ledger快照，入参/TxID/时间戳固定配对。模块编译和模板准备全部在主采样前；冷准备另存MODULE_PREPARATION.csv。

每方法3独立批次，每批每组一个独立进程、两笔正式目标，形成6配对block/方法。组间用循环移位并反向的预定顺序，记录actual command/outcome/log；不是6次独立环境重复。完整策略/参数在scripts/experiment.py，进程标签A-*-bN-策略。记录全部首笔、慢样本与反向结果。

F0的restore=0表示没有Host restore，不表示native Data初始化复制了0字节。净初始化应比较newinstance_restore_ms、init_through_s2_ms及完整Invoke，而不是用F0的0与C0 restore直接判胜负。

## Step38B

完全独立源码/二进制，原C0路径不合并。每方法3进程×2正式目标=6次time-only；另1进程×2次allocation diagnostic，不混为主时间。每目标包含root及buyNow六子调用，原始call_id/root_call字段保留。Native/Go分配不同，不将MemStats作为Rust allocation。

另对hash/fact/buyNow分别3批A/B交替校准，每进程两正式目标，数据单列CALIBRATION_SAMPLES，不追加主矩阵。B-clock的1000空窗口仅一个进程内底噪诊断，不伪称1000独立实验。

## 指标边界

主Factory Invoke沿原vm_factory RuntimeInstance.Invoke前后，不改边界；Owner内部单调Invoke和含runtime构造的RunContract分别记录。NewInstance+restore为相邻不重叠窗口之和；再加_start构成部分初始化，不等于S2。init_through_s2_ms来自同一次累计s2_ns端点。

根Invoke/CallMethod已包含六子调用，不加七个完整Invoke；all_instance_init/restore仅相加彼此不重叠的实例化/restore窗口。WASI/Imports/Store缺native allocation不填估算。外层Factory原UnixNano有墙钟局限，内部与RunContract使用单调时钟。

## 统计与证据等级

SUMMARY按各组Mean/P50/P95，P95线性插值；配对节省=同batch+slot左−右，正值右更快。分层bootstrap先抽3个batch、再在batch内抽2个配对槽位，10,000次、SHA固定seed，给中位差95%CI。不是两个独立Median相减。

3clusters的覆盖率不稳定，所有主CI是探索性的。80项C0对四候选×10方法×restore/Factory的事后cluster符号翻转+Holm仅敏感性分析：最小双侧p=.25，校正未显著。其交换/对称假设亦不能由平衡顺序自动保证；不宣称无效或确认性因果。

A=源码/直接观察；B=数据支持但原因未唯一；C=合理源码假设；D=未验证。当前改善/回归表属于有限样本B，不能凭更少ranges或更大bytes直接断言缓存、带宽或page fault根因。
