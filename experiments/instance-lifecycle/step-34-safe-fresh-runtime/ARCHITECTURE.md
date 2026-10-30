# 安全Fresh原型架构

本轮是独立可运行原型，不是生产替换。生产main和版本未改，父963b47b4。已有A/Copy Guest和Gas规则不变，未合并陈航分支、未加入B1。

```text
请求 -> SafeFreshOwner.Do(context) -> 唯一native owner(OS线程)
  缓存: Config/Engine E + 编译Store S0 + Module M + lazy类型元数据/静态plan
  每次Fresh: new Store Si(E) -> WASI/imports(Si)
     -> NewInstanceInStore(M,Si) -> 可选原restore -> WASI.Initialize(Si) -> _start
     -> SetGas/真实CallMethod/Gas结果 -> 同步scope清理 -> 删除Si handle
  buyNow host回调 -> 同owner直接进入子Runtime -> 子Store Sj -> 执行/关闭 -> 返回父调用
Reset: 停止接纳 -> 等在途job结束 -> owner执行cache释放 -> 重建或继续
Stop: 停止接纳 -> 排空job -> owner清理cache/root -> owner结束
```

独立Store解决runtime arena所有权隔离；不假定全部Wasmer操作都必须固定OS线程。C API StoreRef为Rc/UnsafeCell，API文档要求store及对象单线程访问；Go wrapper的元数据和managed registry也非多owner设计，所以本原型保守选择一个进程一个owner，Engine/Module未认证跨线程共享。固定线程与资源scope、回收顺序、排空协议共同构成约束，不能单凭LockOSThread当安全证明。

`source/vm/step34_owner.go:38` 为非test源码。queue容量1，最多接纳32个外部job（含取消），不提供生产无限服务承诺。同owner重入Do直接inline，不等待自己队列；从owner内部Reset/Stop拒绝。真实buyNow仍经过真实Core VM和六个Guest，下游不走外部排队。合约重入/depth守卫保留，未用全局锁掩盖原池并发。

截止/取消仅在排队或安全检查点生效；不会强行销毁正在native执行的资源。Stop ctx到期可返回，但cleanup仍在任务完成后执行。所有reply缓冲1避免调用者取消后owner卡在回复。Reset失败后poison并拒绝新job，仍可Stop。原始Pool resetC及空StopVM没有直接改写；节点必须接线到此新协议后才可使用。

缓存tuple冻结合约/版本/WASM SHA/配置；实际缓存selector沿用测试recipe的contract+group。本轮不认证动态升级和任意缓存失效，节点适配必须固定部署并拒绝不匹配或使用完整key。Module编译/模板在目标Invoke前，缓存用于真实init/业务/故障后恢复；不是每Fresh重复编译。
