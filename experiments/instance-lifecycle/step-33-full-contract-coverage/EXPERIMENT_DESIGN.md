# 实验设计

继承 Step32 7eccc36e，G0=Fresh、G1=A、G2=Copy、G3=A+Copy。Step32 六个已完成方法不重跑。新增业务逐项预检，之后各3批×10完整四组区块。同区块相同输入与等价初始账本；四组 Williams 顺序 G0G1G3G2 / G1G2G0G3 / G2G3G1G0 / G3G0G2G1 轮转。10区块/批无法完全平衡，提供顺序分层。

独立进程至多两组；有两个真实 prerequisite 的方法每进程一组。每个组缓存同源预编译Module与Store，严格串行 Fresh 创建/执行/同步关闭。初始化、真实状态准备、Module编译、模板构建不计入目标 Invoke；逐样本记录这些准备成本。完整 Invoke 包含 Fresh NewInstance、Copy、WASI/_start、CallMethod、同步 Close，具体起止继承 source/vm/step22_runtime_test.go。CallMethod/export 等嵌套窗口不得重复相加。

不添加100ms Sleep，不运行原池后台 grow 或异步关闭，不测真实节点/E2E。资源沿用 Step32：普通合约 RSS768MiB、线程125；cgroup MemoryMax2GiB/TasksMax256/60s，Go timeout45s；宿主可用内存至少8GiB，swap使用至多1GiB。每进程正常退出且cgroup清空才继续。

完整区块四组Gas、结果、实际读写集、事件、初末账本一致且所有进程/生命周期守卫通过，才进入主统计。保留预检/失败/慢样本，不裁剪。仅成功路径不得标作异常或Table真实函数身份验证通过。

统计以区块直接差计算。报告分层3批、顺序和先后关系。95% CI使用10000次按批次再按整区块重采样的bootstrap中位数，固定seed320027+方法索引*100+效应索引；P95线性插值。raw interaction=G0-G1-G2+G3，正为抵消，负为额外协同；同时输出synergy_saving=-raw。中位配对效应不能通过独立中位数相减代替；不同方法/历史新样本不合并。
