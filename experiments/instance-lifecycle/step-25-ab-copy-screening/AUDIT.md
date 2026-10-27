# Step-25 实施及计时审计

基线Step22 394d291、Step24B 570b06a，宿主源码从24B冻结副本恢复。`audit/recomputed-step24b.json`从90对原始PAIRED_SAMPLES复算：bigNumCal/fact/ERC721完整Invoke节省中位数0.6696525/0.7496765/0.711377ms，正向74/72/75对；不是根据提示数字反推。原报告/计时代码与CSV保存在audit/step24b，未改写历史。

## A、B1、Copy的准确含义

| 方向 | 实际代码/历史证据 | 本轮范围与限制 |
|---|---|---|
| A | Step18 95903a3，pipeline.py及prototype/*layout_pad.go.txt；可达静态字节数组、unsafe指针与init引用，由Go链接器重排并修正全部地址 | 目标是第一次arena预留bloc达到4MiB；不是initial-memory=128页方案。增加初始页和完整模板，不能当零内存成本。仅固定Go1.24.1和这组已验证产物 |
| B1 | 仅采用Step18 recovered-pb恢复的**原历史PB依赖裁剪**；原会话的b1-pb-total/B1诊断工具链、SDK补丁与构建链见audit/step18/recovered-pb/RECOVERY.md/original-sdk-patch.txt | 删除SDK0.1.3的PB import、SimContext.GetBatchState、实现及batchKeysLimit。它是一个针对B1 package init依赖的具体实验，不等于通用B1优化。没有自动把所有B1机制与PB混同；未恢复出其他独立通用B1实现 |
| Copy | 22/24B prepareStaticMemory、staticMemoryPlan.restore、makeE22 | 从最终WASM Data构造S1模板，编译对应noData，NewInstance后、WASI.Initialize/_start前区间Copy。不是在原Data初始化后重复复制。Globals/Table等非Data section保留，实际Table函数身份仍未验证 |

B1减少WASM函数/Data/Table布局，SDK公开API不兼容。现有目标无GetBatchState调用不代表通用兼容。A必须在每个P版本独立计算padding；本轮沿用**已分别校准且哈希固定**的P0/P1 plain产物，未把P0 padding套在P1。旧诊断probe产物不作为性能样本，不使用旧B1分段时间充当本轮实测。

## 共同基线及工作负载

Step24B预编译compute为100次bigNumCal循环，现存可恢复Step18原源/布局变体为10000次；normalCal均10000000次。本轮不为对齐数字临时修改业务逻辑或WASM，而使用Step18完整同源plain家族作五组内比较。原始SHA逐一匹配Step18 variants.csv后复制进inputs，wasm-validate通过，MATRIX记录全部。**这是一组明确的新二进制家族，不能把绝对耗时直接与24B的约5ms/0.67ms相减归因。** fact/ERC721也使用同家族各变体；同组内参数和初始状态固定，原件摘要另列历史证据。

A0/A1在本轮日志仅是进程左右两个角色，G0..G4才是实验配置。新`e25Prepare`为每角色选择原Module或noData Module，新增doCopy布尔值避免把左右角色误当Copy开关。makeE22的原Copy算法、WASI/start顺序及close guard不变；原24B旧入口的A1语义也保留。每个进程只编译两个所需Module，不编译未测的组合；模板按最终WASM SHA/配置/contract版本缓存，同源G0/G1在进程共享模板，Copy module绑定唯一。不同WASM绝不共用模板。编译、模板均不在目标Invoke计时内。

一进程一合约、每角色独立Store+Module、单一LockOSThread owner串行操作，角色真实init对称且账本clone相等。每次正式调用新WASI/imports/Instance，同步deallocate和scope.Close，不复用已执行业务Instance，不使用后台grow/原池/根全局锁。每角色最多init+2正式Instance，最多6个WASI Instance/进程；不通过五Store一起运行提高资源预算。

## 计时边界（同一条样本派生，禁止嵌套相加）

- S0=dRuntime.Invoke入口，Module和模板已准备；S1=NewInstance及必要Copy完成，之前包括WASI/imports准备。
- NewInstance=整个Go绑定调用，不是native-only wasm_instance_new；**不含随后Copy**。
- Copy=原restore校验/Memory lookup/区间copy；实际复制字节和范围数量另记录。随后统计CopyBytes的记账在S0→S1/Invoke内，copy_ns外，保持22/24B做法。
- S2=WASI.Initialize、_start返回并关闭start wrapper；S1→S2=to_s2−to_s1。
- S3=CallMethod及Gas/结果结算完成、关闭前；S2→S3=to_s3−to_s2。
- exportFunc.Call沿用sim_context.go既有B5计时，将ExportCallNs复制到profile；CallMethod包含RuntimeType/参数编解码/Allocate/方法查找和Guest调用，不能再与S2→S3相加。
- Full Invoke=入口到所有每次清理defer执行后，含NewInstance/Copy/start/业务/GetGas/deallocate/同步关闭。init、账本clone/commit、receipt序列化和root sample输出在外；末尾持久Module/Store关闭也另列。
- 模板prepare含解析/image构造/hash，Module prepare含dCompile的Validate/Config/Engine/Store/Compile及metadata物化；**未单独取得native纯编译器CPU时间**，不把它叫纯编译时间。
- 新Go heap读数在f.run完成之后采集，与RSS/线程处于相同业务边界，不加入被比较的完整Invoke。它不是native堆；RSS为整个进程两个Module/Store的占用，不能拆成单组精确RSS。

本轮plain WASM没有新增Guest A/B1单独计时。start耗时可比较，但不能全部认定为A或B1。阶段、Copy与整条Invoke都由同条记录导出，不拼接历史不同批次中位数。这里是**串行实验参考管理器**，真实CallMethod及VM Manager/mock账本路径执行，不是生产原池RuntimeInstance.Invoke或真实节点延迟/TPS。

## 安全包络和停止

沿用24B单合约软限RSS768MiB、线程125；硬限2GiB/256task、45s Go/60s unit；global available8GiB/swap1GiB，未提高。每进程立即写log/receipt/outcome，确认owner managed/pending=0、created=closed、无存活PID/cgroup。任何新异常STOP禁止扩大。旧Store线程累积未修复，有限进程退出只是隔离，不认证长Store/并发。

build1首次一对预检通过；build2在正式数据前补全复制源码旧入口的doCopy默认值（仅兼容旧测试入口），新Step25测试路径语义相同；主预检及全部正式使用build2。环境记录保留两binary hash，首build1预检不混入正式结果。
