# 当前版本的并发约束与证据

## 实际版本和来源

| 层次 | 本轮实际检查 | 能确认/不能确认 |
|---|---|---|
| ChainMaker Go绑定 | module `chainmaker.org/chainmaker/vm-wasmer/v2`，目录v2@v2.4.0内的wasmer-go；主库HEAD c3e8f2c且有脏修改 | 不是go.mod中独立固定版本的wasmerio/wasmer-go依赖；上游Go SDK精确tag/commit**尚无明确证据**，不能直接命名v1.x |
| 本地绑定改动 | [binding-normalized.patch](evidence/binding-normalized.patch)、[逐文件比较](evidence/binding-normalized-comparison.json) | 与本地`vm-wasmer-official-v2.4.0`目录比较，消除CRLF噪声；该目录不是独立认证的上游tag。包括Store.Inner、imports保持/Close、WASI Store参数、Gas配置等修改，以diff为准 |
| 实际默认CGO | [cgo.go](evidence/current/wasmer-go/cgo.go):1–14；自定义tag另见cgo_with_custom_wasmer_runtime.go | 默认链接packaged so，rpath指向本机目录；环境/自定义tag可覆盖，不能只靠头文件确定运行库 |
| 实际so | SHA256 `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`；ELF BuildID `69a11e39bb80e3024770895acf2b093aae04b04f` | 头文件与本轮串行进程`wasmer_version()`均6.0.1；本轮ldd及Step21A binary ldd指向的库同hash；详见[artifacts.json](evidence/artifacts.json)、[commands.jsonl](evidence/commands.jsonl)、[serial-artifact.json](evidence/serial-artifact.json) |
| 同版本候选源码 | 本地仓库remote TKOTKCh/wasmer_chainmaker，6.0.1分支`091074013fa056df0c6502262eae425927272e10` | 已冻结[N源码](evidence/native-0910740/)；与上游v6.0.1关键结构交叉核对；缺so的编译记录、编译器/features/依赖锁定及可重建证明 |
| 历史线索纠正 | 本地main `7c14de7f8efa8879f57cc95b40783198273cdee2`的Cargo是7.1.0 | 不能当6.0.1的构建来源。6.1.0分支有wasm_store_clone历史记录，但当前Go绑定未调用；不能用它证明独立Store，更不能把Rc clone当深拷贝 |

真实二进制有“Total function bodies”输出等定制痕迹；版本字符串不是完整来源认证。没有重建/替换so，没有更新依赖。

## 证据类别和调用组合

“官方明确禁止”仅用于API项目明确写出的通用规则；本定制so的具体结论同时列源码/二进制证据。未找到当前定制版本官方明确支持共享Store无同步并发的说明。

| 场景 | 类别 | 当前可接受结论 |
|---|---|---|
| Store及其对象在多个OS线程无同步访问 | **官方明确禁止（C API通用规则）+源码证据** | C API项目README要求Store及对象由单线程访问；本地6.0.1 C层Rc/UnsafeCell不补充同步，不能放行 |
| 单Store同Instance串行调用 | **源码证据** | 所有者线程生命周期正确、无外部Finalizer/访问时可执行；本轮仅最小C API验证，不是Go业务认证 |
| 单Store不同Instance串行调用 | **源码证据** | 同上；支持多实例不等于支持并行；本轮已执行串行最小样例 |
| 同Store创建A与执行B | **源码证据** | 两者取得同一Store的StoreMut；创建imports/WASI还修改Store对象表和Rc，禁止作为当前无同步实验场景 |
| 同Store不同Instance并行执行 | **源码证据** | 每次wasm_func_call clone共享Rc并取得StoreMut；无并行隔离保证，不能放行 |
| 同一Instance并发调用 | **源码证据** | native StoreMut/可变VM状态，以及Go lazyNative/funcType/exports等无锁状态、Gas和memory共享，不能放行 |
| 创建A与关闭B、执行A与关闭B、关闭A与关闭B（同Store） | **源码证据** | Close包含guest deallocate、Gas、Rc删除、WASI返回/潜在Finalizer，均需要同Store访问协议，当前不能放行 |
| 同一Instance执行与Close | **源码证据** | handle/exports可能释放，且无借用计数或同步；禁止 |
| Store/Module/Env释放与仍使用相关对象 | **源码证据** | Go强制Close不检查在途借用；native Rc可能延后底层Store释放，但不能挽救已删handle，禁止作为生命周期方案 |
| 跨goroutine顺序交接同Store | **尚无明确证据（定制绑定完整契约）** | goroutine可迁移OS线程；短时LockOSThread不是Store所有者。候选修复用固定OS线程所有者，不能据“串行”自动认证任意线程迁移 |
| 独立Store并行 | **源码证据（隔离方向）/尚无明确证据（工程端到端）** | 可隔离StoreMut/Rc；还需审计Module分享方式、Go全局状态、host回调、WASI线程和销毁；本轮未执行 |
| 只读Module分享、Memory并发读 | **尚无明确证据（当前Go wrapper）** | Rust Module可分享或内存逻辑只读不能推导Go包装器缓存、类型wrapper、StoreRef clone安全。Memory.Data的slice也必须受生命周期/guest写入约束 |

上表“不放行”是本实验安全决策，不声称所有可能定制实现都违反同一规则；也不把区间重叠当已发生的native数据竞争。

## 当前版本的实质性源码证据

路径以`N=evidence/native-0910740/lib`为基准：

- `c-api/src/wasm_c_api/store.rs:6–18`：StoreRef clone共享`Rc<UnsafeCell<Store>>`，store_mut从同一地址生成StoreMut；没有互斥、借用检查或线程所有者检查。
- `c-api/src/wasm_c_api/instance.rs:38–59、96–108`：新建取得StoreMut并保存StoreRef clone，delete丢弃该引用。该文件注释“store参数忽略”与函数体不一致，以实际函数体为准；Go层恰好传module.store。
- `c-api/src/wasm_c_api/externals/function.rs:212–241`：调用期间保存共享Store clone并传StoreMut；func_new/new_with_env也取得StoreMut。
- `c-api/src/wasm_c_api/externals/memory.rs:26–34、54–108`：内存创建/增长和类型/数据访问涉及Store引用；“不同内存”不意味着这些包装操作没有共享Store访问。
- `c-api/src/wasm_c_api/wasi/mod.rs:332–380、605–626`：Env新建/初始化/删除接触StoreMut，start函数也clone该StoreRef。
- `api/src/entities/store/mod.rs:119–122、146–159`：Rust Store虽声明Send/Sync，取得可变Store仍需要`&mut self`。这不能越过C层Rc、UnsafeCell或Rust独占借用要求。
- `vm/src/store.rs:46起、269–274`：StoreObjects内多种Vec，插入时push。创建期间修改容器与另一个调用的可变Store借用不能靠Instance地址不同证明不相交。

[wasm_func_call反汇编](evidence/wasm_func_call.asm.txt)中`0x45dde6`取得Function内共享引用，`0x45ddea`执行普通`incq`，`0x45e004`普通`decq`；[wasm_instance_delete](evidence/wasm_instance_delete.asm.txt)中`0x4618c1`普通`decq`，对应Rc引用计数结构。函数内另有`lock decq`属于其他引用，不能据此把整个对象当成线程安全。反汇编不是逐字源码映射，却是**实际库未统一采用原子引用计数**的直接证据。

即使加一把只保护wasm_instance_new的锁，执行仍会clone Rc/借StoreMut，关闭/exports/WASI Finalizer也不在锁中，因此不充分。只保护Function.Call同样漏掉创建、Gas、memory、exports与删除。完整Store串行所有者可作为功能诊断方案，但改变原池创建/执行重叠度，不可用来冒称原性能。

## 官方文档与Issue的边界

- [WebAssembly C API项目README](https://github.com/WebAssembly/wasm-c-api#interfaces)说明Store及对象的线程限制和共享Module接口；本轮[保存快照](evidence/official/wasm-c-api-README.md)。它是通用C API设计约束，当前main文本不作为定制6.0.1构建逐字契约或独立证明；本轮关键判断还依赖6.0.1和实际so。
- 上游固定版本[v6.0.1 Store源码](https://github.com/wasmerio/wasmer/blob/v6.0.1/lib/c-api/src/wasm_c_api/store.rs)、[v6.0.1 Function源码](https://github.com/wasmerio/wasmer/blob/v6.0.1/lib/c-api/src/wasm_c_api/externals/function.rs)与本地分支关键结构一致，保存于[evidence/official](evidence/official/)；没有用latest Rust文档替旧版本背书。
- [wasmer-go Issue #413](https://github.com/wasmerio/wasmer-go/issues/413)是用户2025-01-08的并发疑问，检索页面未见维护者支持性结论；它只能证明有公开疑问，不能把用户的崩溃陈述视作本机Bug复现或官方禁止。

没有官方明确支持项被发现，不以缺文档反推一定崩溃。Go race通过不覆盖native Rc/UnsafeCell；本轮也没有用少量成功次数证明线程安全。
