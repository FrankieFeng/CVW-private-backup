# Step-31/32最小准入审计

以实际文件/分支为准：Step17、Step22 394d291、Step28 29950ab、Step29 f1609b80、Step30 bb2772d9均存在；原e20-e2e-copy-attribution目录未找到，实际已改名step-20-e2e-performance-attribution。Step20 low-a原始客户端/资源/status可用，Step30没有新E2E。各历史文件哈希、源码快照、行号索引在audit/HISTORICAL_MANIFEST.json与SOURCE_INDEX.csv；未写历史原件。

## 可复用协议

Step21B规定当前C API Store及其对象只能在已建立的所有者协议下访问；实际so有非原子StoreRef计数证据，native源码逐字构建来源仍不完整。Step21D/21E建立固定OS owner、ManagedScope强引用、按scope逆序清理、有限Gas回调重入及拒绝在途Close。Step22把同Store Module缓存与fresh Instance结合，预计算Copy与编译在Invoke外；Metadata的Imports/Exports先在持久scope物化，每次Instance对象临时scope同步关闭。

本轮没有重新设计协议，使用Step29同源已保存binary重跑两个原有小检查。它们验证了缓存Module串行fresh隔离、非owner拒绝、错误创建/关闭后清理以及进程终结；不是节点业务正确性或长寿命WASI认证。原配置失败和重试不混为成功，原STOP留存。

## 真实节点差距

旧node仍为InstancesManager.NewRuntimeInstance→getVmPool→Store/Module准备，随后Runtime.Invoke才获根锁；native Finalizer在Go运行时线程触发，不受该锁统一路由。StartVM/StopVM均返回nil；VmManager.Stop确实调用StopVM，故这里有适配钩子，但现有实现没有排空/owner销毁。CloseAllVmPool只保护map并触发pool.close；pool.close关channel，reset发channel，不是线程所有权与在途join。不能说“节点已有Stop调用”就等价于“native回收已完成”。

managedOwner/current/entries在实验绑定中是进程级单owner；测试dManager还直接引用fixture.nextID/calls与testing生命周期。不能直接把它设为node VmInstancesManager，也不能只复制managed.go或加根锁。需要节点初始化/准备/运行/嵌套回调/Reset/Stop的完整owner适配及确定回收验证；现有资料未提供可直接复用的此类节点补丁。

Step22的缓存Store每创建WASI可能累积线程，已有安全许可明确限制每Store/每进程次数；进程最终退出才是资源隔离终点。这不是10或20笔长寿命节点请求的通用准入。旧Step20 RSS在2564.707MiB触及2560MiB软限，两组都增长约1GiB，归属未完全定位；不证明20对必然超限，但不能通过抬限/隐式进程轮换绕过。

## 有限决定

只执行两个已有小协议检查，不启动真实节点。已有根锁不足；直接迁移单个finalizer文件不足；完整owner节点适配尚无实现及验证，不在本轮继续临时移植/扩大。SAFETY_GATE最终NOT_PASSED，采用用户指定结论C。没有新优化、clone GC研究、A/B1、原池并发或新的全局锁；VM/SDK/绑定/Gas代码改动0。

## 若未来恢复E2E的冻结条件（本轮未执行）

优先G0/G1同原件家族，compute.bigNumCal逻辑WASM SHA e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507，参数{}、同源Module/template与等价账本；不加入A/B1。SDK-Go/v2 2.4.0单客户端闭环，无100ms Sleep；两条隔离单验证节点TBFT测试链，20ms出块，无生产连接。客户端计时SDK begin→同步RPC响应返回，先冻结真实node适配版本/构建hash再运行。

第一轮10对，第二轮只有准入/业务/资源/退出验证通过才10对；平衡G0/G1先后，每笔唯一TxID。节点RSS软限仍2560MiB、hard3GiB、线程soft220/hard256、SDK timeout60s/外部watchdog15s；Go heap必须新增低开销采集而非填写旧RSS。新集成改变调度/回收模型时登记为受控新E2E，不能冒充原节点生产性能。新代码/账本/客户端配置尚未生成，因此不能把这些条件写成已执行配置。
