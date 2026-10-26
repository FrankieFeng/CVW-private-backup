# 分级验证与真实结果

所有独立测试进程均保存command、binary SHA、log、资源JSONL、outcome及receipt；全部已停止。最终版本build12，主分析只读取`final-*`，完整开发尝试在[all_processes.csv](all_processes.csv)。没有race通过替代native证明、没有高并发或100次。

## 实际门槛顺序

1. 静态审计：继承B的Store/Rc/Finalizer和关闭风险；审阅C真实fixture、三WASM/冻结输入、VM manager/TxSimContext；设计B串行隔离。
2. 构建与所有者预检：自动native Finalizer全量接管、Gas maps/config与21C一致；invalid字节码回滚，非owner在native前拒绝。最终还验证缺deallocate报错后scope清理归零。
3. 真实compute单次：bigNumCal/normalCal输出、Gas、关闭通过后才增加至每模式3次；早期强制GC诊断保留，最终不逐笔强制GC。
4. exchange入口：源码审计同步Gas重入并加限深限制；独立进程先真实初始化，再一次真实buyNow；失败阶段不跳过初始化/断言。
5. 最终build12重新验证同一实现的六个业务条件；不是把不同binary的数据拼成一组。

## 最终七个进程

| 标签 | 真实目标业务 | 回收与退出 |
|---|---|---|
| final-owner | 无业务交易；invalid字节码、无deallocate小WASM、非owner拒绝 | 创建错误回滚、关闭错误清理、registry0，exit0 |
| final-big-r0/r1 | 各3个bigNumCal，全部code0、结果607723520、Gas105920 | R0 1/1、R1 3/3创建/关闭，exit0 |
| final-normal-r0/r1 | 各3个normalCal，全部code0、结果666、Gas100000072 | 同上，exit0 |
| final-exchange-r0/r1 | 各3次init+1根buyNow，根和六子均code0 | R0 3/3、R1 10/10，exit0 |

以上14个目标根调用；含初始化及子调用共32个实际VM Invoke。所有者线程ID每进程唯一，inFlight0、scope登记0，创建关闭计数相等。业务“成功”包含真实callee结果和状态断言，不以Go PASS单独认定。

## buyNow成功路径（实际执行）

两模式都实际记录以下序列，root depth0、全部callee depth1：

1. identity.addWriteList
2. identity.isApprovedUser(from)
3. identity.isApprovedUser(to)
4. erc721.mint
5. erc721.setApprovalForAll2
6. erc721.transferFrom

[Fresh receipt](raw_logs/final-exchange-r1-receipts/success-1.json)和[Reuse receipt](raw_logs/final-exchange-r0-receipts/success-1.json)保存各层Gas/结果、读写集、事件、前后账本hash及实际输入。真实init创建管理员；成功后验证两地址白名单=1、token owner=to、from授予调用者操作权、buyNow事件存在。没有直接seed这些业务状态、没有Mock callee成功。

R0/R1根Gas分别12761395/12765774，差4379；复用参考并不Gas等价。旧块版本传入累计Gas、下游返回Gas再次累计的规则保持原样，**不得手工把各层Gas求和替代根Gas**，差异来源尚未逐指令归因。根/子耗时同样inclusive，不重复相加。

## 修正的静态夹具缺陷与保留失败

- `big-fresh-1`：实验简化Snapshot未实现GetSnapshotSize，进入native前Go panic；按真实空串行snapshot补0。
- `big-fresh-1-v2`：标准Go WASI _start的ExitCode::0被严格构造拒绝；精确允许该ABI零退出，其余start错误仍失败，未跳过_start。
- `normal-fresh-1`：真实成功/Gas正确，但预期字符串漏空格；依据合约源码修正为`success normalCal: 666`。
- `owner-errors-v2`：无deallocate负向WAT未声明WASI import，构造先失败；加入真实preview1 import后才到达预期关闭错误。
- `exchange-fresh-1`：BlockVersion1不能配CHAINMAKER地址模式，identity init拒绝。
- `exchange-fresh-1-v2`：ZXL可初始化，但原fixture期望UID，实际SDK得到PEM；源码表明ZXL旧块版本注入MemberInfo。最终ETHEREUM是旧版本明确支持、仍注入UID的模式。没有更改Gas规则/BlockVersion/合约来绕过，详见[address-decision](audit/address-decision.md)。

开发阶段共23次测试尝试，17进程通过、6失败；旧失败全留在raw_logs，不纳入最终性能表。构建/编译失败另保存在audit，不作业务样本。未出现已观察到的native崩溃、保护越限或超时，但这些阴性结果不是线程安全证明。

## 资源、时间与证据边界

外部20ms左右轮询配合进程内生命周期事件点读/proc；取两者最大值，最终峰值约681.24MiB、57线程。event数据补充了外部采样遗漏，不能当作精确连续峰值。单次Fresh后可看到线程下降约16，但最终Fresh exchange仍有16线程，未判定全部归属；进程退出确认收束，不声称逐调用native后台全部已join。

部分早期进程出现墙钟回拨，原vm_factory的UnixNano差出现负值。最终自定义Invoke/CallMethod/阶段耗时用Go time.Sub/time.Since单调分量，事件另记monotonic_ns；未改任何系统时间配置。最终主样本没有end<begin，但统计仍只用单调时长。

未验证：长期RSS稳态、100次、并发创建/执行、生产节点签名/ACL/共识、任意合约/同合约递归、Table全语义、duplicate token/非法地址负向业务矩阵（代码保留但本轮未运行）。固定公开测试身份和内存账本是VM功能夹具；不认证真实节点安全或原生ChainMaker吞吐。
