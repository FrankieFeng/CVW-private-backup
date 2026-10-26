# 安全基线选型（运行前登记）

版本依据：Step21B 620650d与Step21C 32d257b。使用同一SHA为dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9的packaged Wasmer6.0.1；精确native构建源仍未知，不宣称认证所有实现。

| 方案 | Store/Module | 所有权与回收 | 对性能的影响 |
|---|---|---|---|
| A 同Store串行参考 | 每合约一个Store和Module，所有Instance顺序访问 | 必须固定owner并接管Finalizer；同Store对象表可能保留guest状态，WASI重绑定还需契约 | 可少付编译成本，但所有操作串行，改变原后台供给并行 |
| B 独立生命周期 | 每Fresh调用全新Store及在该Store编译的Module，host/WASI同Store创建；不分享Module或克隆Store | 单OS线程owner，严格LIFO资源scope，返回前显式关闭；父/子调用使用不同Store；禁止同合约递归复用 | 创建包含编译、WASI、start；新参考基线，不能冒称原池TPS |

选择B的串行版本。理由是目前可以明确证明module.store就是目标Store，不依赖尚未认证的跨Store Module分享和WASI重绑定；Fresh销毁整个Store边界比长期共享Store对象表更清楚。R0仅为隔离参考，缓存同一bundle，不能生产使用。

不实现并发创建/执行。一个固定OS线程处理全部native API及嵌套host回调；C API同Store不得重叠，跨合约父调用等待子调用时，子使用独立Store。拒绝任何递归调用活动中的同合约Store，限定最大depth和最多3个合约注册。无后台grow、apply/remove/add通道；同步需求创建，库存上界每合约1（R0），R1只保留在途调用栈，最多depth+1。排队0、未完成请求不接受新根请求。创建失败同步回滚scope，不发布nil对象。

实验复制模块保留原Gas配置、CallMethod、SetGas/GetGas和真实VM manager/TxSimContext。只替换实验Runtime供给/回收，不调用原池。R1不复用任何业务执行过的Instance。R0缓存bundle但使用相同构造/调度和Gas路径。

必须接管绑定所有runtime.SetFinalizer：实验版本改为固定owner的强引用清理登记，不注册Go自动native Finalizer；scope按反序同步执行登记函数，并支持手动Close注销，GC不再有权删除这些对象。全量调用点替换后静态核对零遗漏。FunctionType.Close需幂等/注销，Function.Type的独立native类型明确管理；清理时捕获Go panic，标失败并停止，不将void native delete包装成可观测成功错误码。native abort/阻塞由独立进程timeout/cgroup隔离。

每个独立进程明确join全部在途调用（串行计数为0）、关闭R0缓存scope、根scope登记清空，之后强制GC验证无native Finalizer回调。强引用登记和资源计数有硬上限；进程退出仅作native残留线程的最终隔离，不声称已经解决Tokio长期回收。

运行顺序：先编译及纯host所有者/错误路径检查→R1 bigNumCal 1次→R1 normalCal 1次→相同输入两模式各3次→根据资源趋势决定扩大。exchange独立进程先真实三合约init再最多1个buyNow，只有全部初始化成功及资源预算通过才能进入六callee。失败保存receipt，不伪造结果/改Gas/提高阈值。

保护：RSS1536MiB、Threads220、MemoryMax2GiB、TasksMax256、60秒硬时限/45秒Go timeout、MemAvailable8GiB、SwapUsed1GiB。每进程采样线程/RSS并记录阶段事件；不以短样本通过自动放行100次。若WASI删除后线程或Store资源未收敛，禁止100次。
