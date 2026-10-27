# 条件与计时审计

基准Step22 `394d291`、Step23 `ba57368`，新分支父为23；实验代码明确从22复制，不继承23密集Gas/RW观测器。22原始CSV、第三批buyNow原log和23已验证范围冻结于audit/reference-*，来源/hash在reference-manifest.json。22主实验CI跨零、平衡小补充不能据此变为确定性收益；23探针日志含显著开销，不作为性能样本。

## 仅有的VM实验源码变化

相对22仅step22_runtime_test.go变化，见source.diff与audit/source-identity.json：

1. 单合约两组分别真实init，起始账本重置并核对相同，补齐22原单合约只A0 init造成的Store历史不对称。init不计入目标Invoke，两组没有复用业务Instance；每对又从同一已初始化账本开始。
2. Module准备顺序按进程交替A0先/A1先；二者均准备一次，Module metadata物化在持久scope。固定TxID、tokenId与参数，排除跨样本字符串长度变化。
3. 测试入口改为Step24B，收紧每进程最大目标配对数至2；并未放宽原guard或引入锁。

Copy算法/静态模板、dRuntime.Invoke、CallMethod、deallocate、Managed所有者、Gas映射、Wasmer绑定与native库都保持22版本。生产VM、22/23原始文件未修改。环境/binary/源码hash固定；默认cgo rpath与LD_LIBRARY_PATH指向E24同hash库。so版本仍6.0.1，精确native构建来源仍未独立认证。

## 模型与等价条件

每个有界进程各变体/合约一个独占Store+Module，单一LockOSThread owner串行访问；每Invoke新WASI/imports/Instance，A1在noData Module实例化后restore静态Data Image。Copy发生在WASI.Initialize/_start前；不是先运行原版active Data再多复制一次。Module不跨Store借用，缓存miss立即失败，不暗中逐笔编译。

模板由相同原WASM解析active Data，保留非Data section原字节；全零image按原segment覆盖、记录非零区间。模板与两个Module在Invoke前准备，并在进程尾部关闭。prepare还含Validate/Engine/Store/config及持久metadata，**不是纯编译器CPU时间**；本轮不另拆编译器内部耗时。相同业务WASM/配置/输入，A0编译原版、A1编译对应noData，这是Copy机制本身的区别。

单合约进程中两组均有相同init调用次数；两个正式配对逐对交替先后，保留相同数量Store内对象历史。预检全S1 Memory SHA在业务前核对，正式不做该SHA，不混入性能表。目标Gas/返回/根RWSet/事件与初始/最终账本逐对离线再比较。真实子调用的Gas/结果逐层比较，但完整callee内部RWMap不额外读取（避免23受影响v1观察器副作用）。

## S0/S1/S2/S3和完整Invoke

本轮统一使用22的Invoke级S0定义，避免将纯静态初始化与完整供给阶段混称：

| 字段 | 边界与含义 |
|---|---|
| S0 | dRuntime.Invoke入口的单调时间，Module/模板已准备 |
| S1 | NewInstance完成并且A1 Copy完成；A0为原active Data已初始化 |
| S2 | WASI.Initialize、_start、关闭临时start函数后 |
| S3 | CallMethod、原Getter与Gas/result处理完成、关闭Instance前 |
| S0→S1 | to_s1_ns，含每次WASI/imports准备，不等于纯Data初始化 |
| pure static_init | newinstance_ns+copy_ns，各为同一条样本相邻计时，不混算两组中位数 |
| S1→S2 | to_s2_ns−to_s1_ns，预检hash也会落入此段，故预检排除 |
| S2→S3 | to_s3_ns−to_s2_ns；root buyNow包含六callee的完整Invoke |
| Full Invoke | Invoke入口至全部每次清理defer完成；含新WASI/Instance、Copy、start、真实业务、GetGas、deallocate/scope.Close |
| Close | CallDeallocate+临时scope清理；最终持久Module/Store cache close另列 |

TIMING.csv保留原ns和派生段；MODULE_PREPARATION.csv独立列模板/Module/缓存关闭，TIMING每行指向对应缓存Key/一次性prepare值（不是重复计入Invoke）。newinstance是整个Go NewInstance调用，不是native-only；copy包含Key/Memory lookup及区间copy，不是纯memcpy。A1在Copy计时后另遍历Ranges累计CopyBytes/CopyRanges，该观测记账成本不在copy_ns、但在S0→S1和Full Invoke中；原22代码即如此，本轮保持不变，未假设其开销为零。完整Invoke为**实验dRuntime参考管理器**，不是生产RuntimeInstance.Invoke或客户端/节点TPS。真实CallMethod及TxSimContext/VmManager调用链实际执行。

账本clone、init、receipt序列化、根sample日志与最终cache close均不在目标Invoke中；子调用的诊断输出仍在父Invoke内，双方同一代码。阶段有嵌套，不能把CallMethod再加到S2→S3，不能把六子Invoke与根再相加。

## 资源和样本解释

已知WASI线程在Store存活期间持续增长，**不提高单Store预算**。30对/批由15个独立进程各2对组成；每进程Module缓存保持到其4次目标Invoke完成，另有对称真实init。全部进程串行，非后台池。prepare重复发生在不同进程，但两组操作对称且全数单列；结果不包含该一次性启动成本，不能外推为长寿命Store稳态。

保留既有限额并收紧单合约包络，见PLAN。若任何STOP或语义错误发生，停止全套，不清STOP换进程凑数。已知每进程内线程增长并未被“修复”，进程终结只是有界隔离；没有据此认证连续30/100对、并发或真实节点可用。

## 源码定位

- `source/vm/step22_runtime_test.go:79` e22Prepare（模板/两Module）；`:126` makeE22（WASI/imports、NewInstance、Copy、S1/S2）；关闭函数与测试初始化/配对入口见[SOURCE_INDEX](SOURCE_INDEX.md)。
- `source/vm/step21d_runtime_test.go:226` dRuntime.Invoke（入口/关闭defer/最终计时）；`source/vm/sim_context.go:76` CallMethod。
- `source/vm/step22_static_test.go:235` staticMemoryPlan.restore（Key校验、Memory.Data与区间copy）；`wasmer-go/managed.go`为原固定OS owner/清理协议，未改。

全部时间均用Go单调时钟；没有将日志Unix时间差用于计算性能。
