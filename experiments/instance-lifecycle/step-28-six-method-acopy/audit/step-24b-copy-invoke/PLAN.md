# 运行前登记（2026-10-27，先于新guest）

仅使用22计时和Copy实现；23密集观测不用于性能。guard/Gas/native/Copy不改。E24测试入口只修改两组对称真实init、固定TxID/tokenId、Module准备先后顺序以及收紧预算为每进程最多2对。

A0/A1每变体独立Store+Module缓存，每进程各准备一次；缓存miss失败，不逐Invoke编译。每进程两对恰好A0先/A1先各一次；Module准备先后逐进程平衡。每次clone相同初始账本、执行Fresh Instance、同步Close；无业务预热及人为Sleep。

正式目标每合约3独立批次，每批15独立进程×2对=30对。三合约交错，所有进程逐一执行，不并发。30对是多进程聚合，**不是同一Store连续30对**。准备/进程重建/最终缓存关闭单列，不算入Invoke收益；只解释有界串行参考，不能称长期稳态池收益。

先三合约各1对preflight（全S1 Memory SHA、Gas/结果/实际RWSet/事件）；再各一个2对formal先导（保留为第一批slot00）。全部资源和语义合格才继续登记批次。

资源沿用RSS1536MiB/Threads220、MemoryMax2GiB/Tasks256、进程60秒/Go45秒、MemAvailable8GiB/SwapUsed1GiB。已知Store存活时线程累积，因此**不增加单Store寿命**，2对沿用22平衡组预算；额外对称init最多6个WASI。另收紧：单合约进程线程不得超过22原3对包络125、RSS不得超过768MiB；如果跨进程包络恶化/进程未退出/任何错误则STOP并停止全部续跑。进程隔离不解决长期Store问题，不通过多进程凑数越过任何已触发的STOP。

前三合约全部批次语义一致且过程包络正常，才允许buyNow小样本扩展：先split preflight，每变体独立进程，1根+六真实callee；再3独立正式配对，变体先后交替。每个进程准备相同的两组Module、真实init3次，只有单变体1根，沿用22安全split模型，不把两根挤进同一进程。

统计：每合约Median、最近秩P95、逐对A0−A1节省的中位数/均值/正向比例；95%CI使用10000次固定seed240027层次配对bootstrap（先batch再process，保留同进程两对）。单列各批/顺序，3批CI不能证明长周期稳定。嵌套阶段不相加，不能把子Invoke和根Invoke重复求和。Table身份、Globals动态/异常/OOG/并发/长期Store/真实节点继续not_tested。
