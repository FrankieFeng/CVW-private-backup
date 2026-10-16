# step-16 集成审计与 step-17 变更

审计对象为 step-16 的 `4cdf6c5`，正式 step-17 构建源码另有 commit/source SHA 记录。未重设计模板或引入 S2 Snapshot；未改 Wasmer、Go 或 ChainMaker 依赖版本。

| 边界/问题 | 证据与处理 | 覆盖判断 |
|---|---|---|
| 模块变换 | Wasmer 先验证原始Wasm；准备只省略section11；active data按顺序覆盖模板；其余section完全相同。start/DataCount/passive/imported memory等拒绝 | 支持清单内通过；未覆盖Wasm特性走原路径 |
| Copy时点 | noData Module→fresh NewInstance→restore→S1→WASI Initialize→_start→S2→SetGas→S3→business→关闭 | 未先执行原data再Copy |
| 模板关联 | 原始Wasm SHA、Contract.Name/Version、ConfigID、Module指针、Memory长度；私有原始bytes、私有Image/ranges | 外部不直接取得模板；跨实例只读 |
| 原缓存查找 | manager原来只用name_version，不比Wasm | step17加入bytes.Equal，遇同身份不同Wasm返回错误，拒绝陈旧Module；cache-key-safety.log通过 |
| 编译artifact | step16进程级CM_STEP16_SERIALIZED_MODULE只适用于单模块worker | step17按编译Wasm SHA选artifact；校验WasmSHA、ConfigID、ArtifactSHA后Deserialize。只允许本地自建可信artifact，不支持任意外部输入；当前artifact目录仅覆盖本轮8个合约，任意新模块缺artifact时返回编译错误，不能宣称节点模式对任意模块自动回退已测通过 |
| 缓存层次 | InstancesManager每链map、每合约版本一个pool；模板只在pool内，没有独立全局模板缓存 | 命中率为manager pool命中，不是磁盘/编译命中 |
| 共享lastCreated | step16测试字段每次GetInstance写同一指针 | 节点路径移除该写入；保留字段供旧测试编译，step16Integration依赖它的测试不可直接当step17验证 |
| 原global float计数器 | newInstanceTime/compileTime无同步 | 节点不再写入；观测使用实例局部profile和受锁stdout/atomic counters |
| profileObserver | 可能由测试修改的回调 | 节点始终nil，没有运行时安装/修改接口；测试进程独立 |
| fresh预建 | manager会grow(5)，但freshOnDemand不消费队列 | step17跳过；每次Invoke同步新建并同步关闭，不回收业务实例 |
| initialMemory悬空视图 | newVmPool取Memory后关闭verification实例，字段仍保留 | step17关闭前清空字段，不使用该已关闭实例的view |
| 并发Store | 本地Wasmer C-API源码StoreRef为Rc<UnsafeCell<Store>>，Go binding没有Store互斥 | 该Rust目录未证明与自定义so逐字同源，故作为风险证据，不当作so线程安全的完整证明。实验根Invoke每链互斥；同一root的同步子调用不重复加锁。没有native并行安全结论 |
| WASI环境 | freelist由mutex保护，计数atomic，一次环境只借给一个实例 | 真实节点fresh请求正常；长期native线程回收不作通过判断 |
| 错误恢复 | restore失败关闭新实例并返回错误；不继续执行未恢复内存 | 合成错误key/模块验证通过；无法取得native Module时拒绝加载，不自动静默编译导致Gas漂移 |
| native指纹路径 | staticCopyConfigID使用runtime.Caller源码目录读取linux-amd64/libwasmer.so，flag关闭也调用 | 本机源码可用并记录ldd/hash；部署移走源码、trimpath、其他平台未验证，仍是可移植性缺陷 |
| 配置变化 | ConfigID含opcode/function map、pages/meter/schema、Go/platform/native hash | 环境flag按pool创建捕获，不支持运行中热切换；修改配置须重启；全局meter maps只初始化一次，不能支持进程内多个计费配置 |
| cache身份 | manager的name_version分隔可能别名；contractId指针未克隆 | 本轮8个固定简单名称/版本、链框架持有不可变Contract。任意身份字符串碰撞、外部并发修改Contract没有通过验证 |
| Reset | fresh模式没有startRefreshingLoop，reset仍向无buffer resetC发送 | cache-lifecycle-audit.log确定复现阻塞；禁止在线reset，不把测试断言PASS误报为reset功能PASS |
| close/逐出 | fresh close只close(closeC)，无后台loop释放Module/Store/freelist | 没有安全逐出/在线升级证明；无LRU/内存预算。只用进程退出释放缓存。当前不满足生产cache生命周期要求 |
| 错误传播 | runtime业务CallMethod错误随后被getGasByExport的err赋值覆盖；callContractCore也覆盖CallContract err | 缺方法两模式均空成功；非法业务参数显式错误正常。属于基线缺陷，未在本轮修改原有语义 |

## 并发/race结果

- 真实节点：A4/B4并发客户端均完成，所有热调用结果/Gas配对相同；根VM互斥保护有效范围包括创建、业务、关闭，等待锁的时间由客户端总延迟体现。跨合约子调用沿同步root执行，无循环调用/异步host回调的安全性结论。
- 独立测试：`-race`下4个worker共用Image/ranges，每worker拥有自己的Store/Module，120轮×2 fresh实例，修改实例Memory后peer和模板不变；合成表11/22及清空元素隔离通过。Go检测不到全部native竞争。
- 整节点默认`go build -race`在恢复账本的store/bloom/filter.go:191触发checkptr，未到VM业务；原始堆栈保留stdout。
- 仅对store/bloom关闭checkptr的诊断构建（**没有用于性能**）随后在RollingWindowCacher.ResetRWCache/recoverRollingWindowCache报告Go race，两路径都发生；`race-node.<pid>`保留详情。
- 又以**全新独立race-data账本、未关闭checkptr的原始-race构建**启动，仍在RollingWindowCacher.ResetRWCache/InitGenesis报告race，`race-fresh.<pid>`保留详情。均在存储初始化处停下，不算Copy并发验证通过，也不将堆栈归因于Copy。
- 因此“真实整节点无数据竞争”是**未通过/未完成业务覆盖**，不是pass。没有为掩盖race而修改依赖或正式配置。

## 后续最小修补方案（未实现、无性能声明）

1. 为fresh pool新增退休/活跃实例计数与延迟销毁；阻止退休后新借出，等最后一个fresh实例关闭后释放Module/Store/模板。明确manager锁与Invoke/跨调用锁顺序，避免在线升级死锁。
2. fresh reset应定义为销毁并重建pool，或在配置/模块未变时显式无操作；不可发送给不存在的刷新loop。
3. manager缓存用无歧义复合key并克隆身份，配置/native fingerprint采用可部署的只读构建/运行时标识；配置变化必须生成新pool。
4. 再研究独立Store的真正并行执行与有界内存回收。在固定版本约束下，本轮没有修改native runtime；如下一步改Wasmer，应另开分支并重测全路径、Gas和跨合约。
