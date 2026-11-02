# 同步单客户端提交TPS口径

本轮窗口为有限预定请求批的首笔SDK开始至末笔SDK同步返回。方法固定一般每组每批4笔，identity.alterAdminAddress每批1笔；raffle修订后每批3笔。三批窗口各自独立。不是预先固定秒长的开放窗口；窗口定义在正式采样前冻结，raffle修订按真实名单容量单列。

`t_start=window_start_mono_ns`；`t_end=window_end_mono_ns`；`seconds=(t_end-t_start)/1e9`。

分子：这个窗口内发起且在末笔返回前取得成功同步结果的唯一TxID，并在窗口外GetTxWithRWSetByTxId确认链上成功、正高度且结果匹配。失败、超时、拒绝不进成功分子；仍保留在尝试数与窗口时长中。窗口外部署、setup、预热、核对查询及之后错误探针不进入分子。尾部未完成交易不得事后补进当前窗口；本轮有效窗口均无在途尾笔。

`实际提交TPS = confirmed_unique/window_seconds`。
`客户端成功响应速率 = successful_responses/window_seconds`。
两者本轮主数据相等，因为全部响应均复核为真实提交，不意味着定义可混用。

THROUGHPUT.csv保存444个有效窗口及无效窗口。TPS_STATISTICS.csv合并口径为三批成功数之和/三批秒数之和，另给出每批TPS。TPS_EFFECTS.csv为同批窗口右组TPS减左组TPS，正值更快，3窗口成对bootstrap仅探索性。

VM日志等效TPS另列：该窗口内所有根VM Invoke执行次数 / 根VM外层Invoke时长总和（秒）。同TxID可能多次Invoke，执行次数1872、交易1728，不对交易去重后又使用执行总耗时。它不包含所有排队/提交/RPC成本，不等于实际TPS，不能与王浅秋历史值直接解释为节点吞吐的变化。

唯一性作用域为独立账本/run：为了保持事件/Gas元数据可比，跨组独立账本使用相同配对TxID；全局request_id带run命名空间。不能在不同账本间全局去重。统计与跨边界规则代码：source/client.go:63、:114；scripts/analyze.py窗口断言和分子；scripts/report.py三批汇总。
