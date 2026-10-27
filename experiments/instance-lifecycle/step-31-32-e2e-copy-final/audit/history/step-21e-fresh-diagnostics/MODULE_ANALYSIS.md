# Module编译成本来源与可用能力

Step21D约0.56秒是独立Store架构每次重新编译引入的成本，不能称原ChainMaker每笔交易的固有成本。原路径按合约名/版本缓存pool，pool一次创建Store与Module；后续grow通过同Module创建Instance。

证据：本次复制源码 `vm_instances_manager.go:91–115`的双检缓存；`vm_pool.go:1062–1090`创建Store/Module、`newInstanceFromModule`复用p.module。原冻结路径为21B `evidence/current/vm_pool.go:1029–1047、1238起`，避免因实验观测行号变化混淆。池失效、版本变化等会重新编译，不能简化为整个进程只编译一次。

## D计时窗口

`step21d_runtime_test.go:85–153`每个R1 Invoke创建bundle，`dCompile`含Gas配置map/middleware、Engine、Store、ValidateModule、NewModule。其compile_ns从create_begin起计至dCompile返回，因此还含少量日志/验证/构造，**不是独立纯编译器CPU时间**。后段create_ns−compile_ns才覆盖WASI、host imports、instance_new、Initialize和_start等，亦非单独instance_new的计时。close_ns单列deallocate/scope回收。

[21D原始summary](../step-21d-safe-fresh/summary.csv)：bigNumCal R1 compile均值563.952ms、create568.977ms、close3.750ms，差约5.025ms是上述实例构造组合。D R0缓存bundle，首笔才支付此成本。不能拿R0热态与R1包含重新编译的Invoke之差推导纯Instance创建损耗。

本轮normal-ab预建4个bundle的compile_ns分别594.065、573.041、586.586、569.512ms，[原日志](raw_logs/normal-ab.log)保留。全部在normal测量前完成；没有把编译藏到另一条并发线程中，也没有测出稳态补池能力。

## 当前库实际支持什么

| 能力 | 源码/二进制 | 本轮实际验证与限制 |
|---|---|---|
| 同Store缓存一个Module，串行创建不同Instance | 原池已有此路径，绑定NewInstance使用module.store | 微型WAT同Module创建2个Instance，实际answer均42；无WASI，不证明业务长期同Store清理后无资源残留 |
| Serialize / DeserializeModule(targetStore, bytes) | module.go:228/255；实际so导出符号见audit/native-module-symbols.txt | 一个可信本机产物3888字节，在相同Engine、新Store反序列化、实例化、返回42，正常回收 |
| 跨Store直接用原Module wrapper | module.store固定 | 不会自动使用新Store，未作为隔离方案 |
| wasm_module_share/obtain/copy、wasm_store_clone | 本次实际so未导出这些名字，当前Go路径也未实现分享封装 | 不能因头文件/threads.c示例出现接口就宣称可用；这是对21D示例引用边界的澄清 |

能力检查见[TestStep21EModule](source/vm/step21e_checks_test.go#L140)、[日志](raw_logs/module-capability.log)及[outcome](raw_logs/module-capability-outcome.json)。候选源码见[audit/native-0910740](audit/native-0910740/)，上游固定版本[6.0.1 C API Module源码](https://github.com/wasmerio/wasmer/blob/v6.0.1/lib/c-api/src/wasm_c_api/module.rs)已保存[audit/official-v6.0.1-module.rs](audit/official-v6.0.1-module.rs)及下载/hash记录。

Native Module是编译代码；序列化不复制Instance运行状态。Deserialize是加载本机可执行产物的unsafe边界，只允许可信自生成、同版本/引擎配置/平台及Gas中间件的产物，不能从“微型42成功”推出五个业务合约、WASI与Gas全部等价。Go wrapper仍按目标Store管理生命周期。当前so的精确构建来源缺口也保留。

## Step22的最小前置工作

可以选择固定owner同Store缓存Module的串行参考，但须界定Store对象表与每Instance/WASI清理；也可以继续独立Store，先对实际业务验证可信序列化/反序列化路径和Gas配置等价。二者都要分列一次性编译、每次反序列化/实例化、执行、关闭。此轮没有实现业务Module缓存优化、没有序列化性能benchmark，也没有放行跨Store并行供给。D整笔约0.56秒不是必须保留的Fresh定义，但也不能未经验证直接从端到端时间减去它，冒充可运行优化方案。
