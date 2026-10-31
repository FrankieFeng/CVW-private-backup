# 实现及版本

实际代码是本目录source/vm（不是只编入go test的另一个假入口）。节点go.mod将vm-wasmer替换到该目录，将core vm替换为Step21C已核查版本；差异仅两条replace，完整node go.mod/go.sum及diff在audit/。节点其余基线为351b816e，适配提交4dd3ae3。

- `vm_instances_manager.go`：NewInstancesManager创建唯一SafeFreshOwner；NewRuntimeInstance分流到非测试adapter；Close/Reset路由到Owner；StartVM传播配置错误；StopVM等待真实排空。
- `step35_node.go`：新增真实节点adapter和缓存，不复制另一套Owner。
- `step35_tid.go`：仅用于沿用Step34 Owner线程识别。
- `step35_static.go`：由Step34 `step22_static_test.go`提升到非测试文件，SHA-256完全相同，见audit/static-template-rename.json。
- `step34_owner.go`、managed绑定、dCompile Gas表、SimContext及Guest与Step34保持；本轮不改native ABI、Gas规则、A实现或Copy算法。
- `step35_node_test.go`：实际InstancesManager接口的串行夹具测试、Reset后重执行、真实错误回滚、Stop等待/幂等、失配准入测试。其底层业务调用使用真实WASM，非模拟子合约返回值。

缓存：chain/name/version/WASM SHA256/config identity/copy开关为Key；不以名称单独索引。config包含已固定native/compiler/Gas/最大页数等身份，本轮runner核对实际so SHA并保存加载maps。缓存最多8项、Owner最多32个外部job/进程，子调用内联不扣另一个外部job。拒绝多链多Owner同时运行；这是有限实验准入原型，不是长驻生产调度器。

Copy：prepareStaticMemory解析最终原WASM生成Image/Ranges/NoData；缓存Module使用NoData；runtime NewInstanceInStore后restore，然后WASI.Initialize/_start。未知/不支持模块记录fallback并用原模块标准初始化。本轮不引入A版本。Copy关闭也保留完全相同Fresh/Owner模型。

每个缓存record保留自己的Config/Engine及compile Store。runtime Store通过wasm_store_new使用该Engine；缓存Module跨该Engine的真正独立Store实例化，沿用Step34验证的ABI；不用wasm_store_clone。不宣称所有合约共享同一个Engine。

准备失败在缓存scope内回滚；实例创建、WASI/start失败在runtime scope内回滚；执行错误保留Code1和既有Gas；显式Close由managed scope幂等执行。完整失败注入属于Step34历史覆盖，本轮新增的实际节点只覆盖成功和业务失败，不把native OOM/析构失败标通过。

后期修正：StopVM取消了会提前返回节点shutdown链的10s上下文，改为等待排空，硬超时交给外部整进程保护；最后增加未opt-in的fail-closed启动拒绝，避免managed绑定落回旧worker路径。每个构建命令、源码哈希、二进制SHA在audit/*outcome.json；node2/4/5实际调用记录分别保留，node6/vm5为最后构建，不混作同版本性能数据。
