# 实际实现

- `source/vm/wasmer-go/instance.go:33`：新显式target Store入口，检查live Module/Store与共享Engine；真正传入wasm_instance_new，不靠wrappedInstance.store字段装作隔离。
- `source/vm/step22_runtime_test.go:140`：在instance scope里NewStore(cache.Engine)，WASI/host imports/Instance/Initialize都使用Si；Copy仍复用原模板和noData Module，restore位于WASI Initialize/_start之前。Cached Module与编译Store不逐次销毁。
- `source/vm/wasmer-go/managed.go:51` 和scope.Close：显式释放采用一次claim，scope不再提前移除登记导致Close被跳过。Store/Instance/WASI/Module等重复Close不会重复调用C析构。Memory与function增加借用scope检查，Store/Instance关闭后指针清空或拒绝访问。
- `source/vm/step34_owner.go:102` / `source/vm/step34_owner.go:136` / `source/vm/step34_owner.go:173`：有界队列、inline callback、排空、取消、幂等Stop、Reset失败poison。没有恢复原pool grow、异步关闭或无主finalizer。
- source/vm/step34_business_test.go：真实ChainMaker SimContext、Step32四组recipe与buyNow依赖，不模拟子调用。source/vm/step34_fault_test.go仅提供明确的Go层故障，普通路径无Gas修改。原dRuntime继承的CallMethod错误被gasErr覆盖问题已在本原型修正：保留CallMethod错误，仍按原规则读取/计算Gas。增加真实unreachable trap与缺失方法；owner返回错误时只返回Go消息，避免TrapError的native Frame跨scope逃逸。

编译冻结build9 SHA `68dd961719f14f3e6022ca9e4e412637f9cb391090d34b81e55f536c996aa005`。Race单独二进制，不参与计时。早期构建/启动/诊断错误全部保留；build6/7数据另有prefix和原件，最终性能与正确性只选v9标签。派生区块labels曾漏前缀，修正原件备份audit/block-metadata-prefix-correction，原日志/收据未改。继承的e27Probe诊断定义原先仅在_test，导致常规go build失败，现原样移入step27_diagnostic.go并通过非test编译；没有改原导出窗口。源码包含gofmt差异，语义补丁另存audit/source-semantic.diff。

计时仍dRuntime.Invoke入口到延迟close完成后记录：含新Store、WASI imports、NewInstance、Copy、Initialize/_start、CallMethod/Gas、关闭。owner排队在此窗之外。编译/模板/缓存最终销毁单列；不能把排队窗或编译差异算Copy收益。父export嵌套子Invoke，禁止相加。

非test实现包含owner与binding；完整业务桥接目前是测试适配器，尚未将生产NewRuntimeInstance/getVmPool/StopVM路由到它。不是可直接替换的node binary，低级native句柄不得外泄给任意调用者。
