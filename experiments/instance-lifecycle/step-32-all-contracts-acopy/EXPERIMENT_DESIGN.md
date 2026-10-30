# Step32 四组有界串行方案

G0 Fresh；G1 Fresh+A；G2 Fresh+Copy；G3 Fresh+A+Copy。不得沿用Step28 G1/G2编号含义。每方法3批，每批10个四组配对区块；6方法合计180新区块、720正式根调用。所有WASM冻结来自同源Step18 P0/plain家族，非Step24B旧原件；compute bigNum/hash为10000轮、normal10000000轮。

每组每合约独立Store+cached Module，固定OS owner；每次新WASI/Instance，同步执行与scope清理，无池后台、异步关闭、B1或新Gas策略。最多每进程2个组/2正式根调用；buyNow每进程1组，全部六真实子调用。一个block跨两个/四个连续独立进程完成，所有组等价账本，相同输入与TxID，三批独立进程无残留。该进程拆分用于保持旧资源限，不能称原池或E2E。

顺序采用随机重命名、随机行序的Williams四组平衡设计；每批各组每位置出现2或3次，种子320027/320127加batch/case，实际顺序保存在command/outcome/block。无业务100ms Sleep；资源监控25ms轮询不属于请求间隔。

## 计时

Module编译、模板准备、init_contract、账本克隆和根回执输出在目标Invoke外。S0→S1包含WASI/imports和新Instance/Copy，不包含缓存Module编译；S1→S2包含WASI.Initialize和_start；S2→S3包含SetGas/CallMethod/GetGas及结果处理，不能标成CallMethod前剩余准备。CallMethod包含export，根buyNow export包含子调用。Close随后执行并包含在Invoke总窗。以上均用time.Now/time.Since单调时钟，不重复加嵌套阶段。

## 统计预登记

主效应直接按同(batch,slot)四组计算：G0−G1，G0−G2，G0−G3，G2−G3，G1−G3。Mean/Median/P50/P95单列；CI为10000次batch→whole-block层次bootstrap，固定seed320027+case/edge，线性分位；3批只是3个时间层，不是30独立环境。另报告位置、前后执行与批次分层。

原需求Interaction=G0−G1−G2+G3保留为interaction_cost_ms。若把耗时降低称收益，额外协同应为synergy_saving_ms=−Interaction。例如单项各省1ms、组合省3ms，原式为−1ms；因此原式负代表协同，正代表抵消。两种符号都报告，不反转实测数据、不把独立Median相减当交互。

## 门槛及局限

逐block比较Gas/返回/业务操作及实际root RWSet/事件/完整初始最终账本。buyNow比较7条真实根/子调用；空参数和重复token失败回滚四组独立预检，不称全部异常路径覆盖。真实Table函数身份、一般OOG/异常、长期Store回收、节点并发均not_tested。全局MemAvailable≥8GiB、swap used≤1GiB；非exchange软RSS768MiB/125线程，exchange1536MiB/220线程；原hard2GiB/256tasks、Go45s/process60s保持不变。任何STOP保留并禁止继续。
