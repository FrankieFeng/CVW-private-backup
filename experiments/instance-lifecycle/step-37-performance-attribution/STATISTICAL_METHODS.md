# 统计口径、复算与多重比较

## 匹配与估计量

读取冻结case.json/window.rows及node日志，按case、batch、slot匹配四组；不按耗时排序配对。37方法各3批：通常每组12笔，alterAdminAddress3笔、raffle9笔；111四组block、1728正式交易。所有失败/慢/首笔与反向原始记录保留；原raffle超出名单的失败窗口遵守原排除规则，未挑其前3笔混进新批。

5对照：G0−G1、G0−G3、G0−G2、G1−G2、G3−G2；正表示右组更快。absolute improvement就是逐对差的中位数，非两独立中位数相减。相对改善为每对100*(left−right)/left再取中位数，非中位节省/独立基线中位数。Mean/P50/P95各组另列，P95按线性插值q=(N−1)*.95；小N的P95不代表稳定尾部。

三批保留独立结果；left-first/right-first、first-slot/later-slots为描述分层。各组固定平衡次序，不是充分随机化，也无法在3批内解耦位置、日内环境与批次。没有删除首笔。

## 95% CI独立复算

与原报告同样：先有放回抽3个batch，再在每个选中batch内有放回抽同数paired slots，两侧始终一同抽；每次取逐对差中位数。10,000次、SHA256(case+left+right+metric)前16hex作固定seed，2.5/97.5分位。925项结果最大差0。

这是有限3clusters的百分位bootstrap，实际覆盖率未保证。跨零=不足以确定方向，不是等效检验或零效应证明。未校正CI保留为探索性。

## 交互符号

本轮G3=A-only，G2=A+Copy。

- 单独节省A=G0−G3，Copy=G0−G1，总节省=G0−G2。
- **saving synergy**=(总节省−A节省−Copy节省)=G1+G3−G0−G2。正=额外协同，负=抵消。
- **cost interaction**=G0−G3−G1+G2=−saving synergy。正=成本上超加性/收益抵消，不能叫协同。

每block先计算这四项再对分布bootstrap；不从三个独立配对Median拼差。INTERACTION_ANALYSIS.csv输出两种符号。历史Step32成本公式被称为正协同的解释不能沿用，本轮只纠正解释，不改历史文件。

## 多重比较校正

主家族预先在PROGRESS记录为37×(5种E2E对照+1种交互)=222项，Holm排序p_(i)后按max_{j<=i} min(1,(222−j+1)*p_(j))校正。次要VM分段未纳入此家族，不将未校正分段CI冒充确认性显著。

原始p是**三批各自配对差均值**的均值绝对值，遍历3个cluster整组符号翻转的8种组合，用大于等于观测绝对值的比例作双侧p；batch内不将12笔当独立随机化单位。交互同理。CI估计的是配对中位数，p检验统计量是批均值，两者不是同一统计量，明确分列，不从CI反算p。

最小双侧p=2/8=.25；本轮所有p_holm=1。不存在有统计能力以.05水平确认单个方法的可能，因此“校正无显著”不反驳局部效应，更不是收敛到无效结论。

该检验需批次独立、零假设下cluster符号对称/可交换。由于实际组次序非充分随机化，这是**带假设的敏感性分析**，不是随机分配保证的因果随机化检验；Holm的族错误控制也只在原始p有效条件下成立。没有报告无条件FWER保证。必须增加独立环境重复/更充分随机化才能确认，不靠同进程多跑几笔制造显著。

## TPS与VM

TPS沿用实际窗口首SDK开始至末同步返回，唯一成功并核对提交的交易数/窗口秒数；每批分别算，合并按总数/总秒数。对照中右减左TPS为正改善，和延迟left−right符号一致。不是1/VM Mean，也不是P50倒数。同一方法每批数量相同，所以TPS是整个窗口总时长的函数，不与单笔中位数等价。

1728笔对应1872根Invoke，逐TxID汇总所有根执行；子Invoke已在根内，禁止加到总VM时长。Store/WASI等缺独立timer的值留not_measured；没有用估算补充缺值或混入历史样本。

Copy关闭组的copy_ms=0是源码分支不执行该操作，不代表另有一条耗时0的native计时。COPY_RANGE_SCENARIOS只算静态字节/次数；不输出WASM、不计时，不与本轮性能样本混合。

GROUP_BATCH_STATISTICS.csv另存各组逐批Mean/P50/P95/N，TPS_EFFECTS.csv为3个同批窗口TPS增量的探索性bootstrap CI（次要描述，不混进主延迟Holm家族）。ACTUAL_RUN_ORDER.csv逐run读取proposer_ready的节点单调时间只做顺序核验，111个block均与记录的平衡组次序一致；未用跨进程时间做延迟差。
