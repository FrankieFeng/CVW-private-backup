# CVW Store 生命周期与隔离修复移植说明

## 1. 交付基线与状态

本分支以用户明确指定的王浅秋 CVW `main` 为基线：

- 仓库：`https://github.com/wqqkakuiii/CVW.git`。
- 原始提交：`c3e8f2cc1479a11450d61e342a93c3b2416b7cff`。
- 修复分支：`review/wangqianqiu-store-lifecycle-fix`。
- 独立工作目录：`/home/frankie/mygitprojects/.worktrees/cvw-wangqianqiu-store-fix`。
- 修复提交：以此文件所在分支的 `git rev-parse HEAD` 为准；提交哈希不能自包含在自己的提交内容中。

**版本边界：此基线随附 Linux amd64 库的 `wasmer_version()` 实测为 6.0.1，头文件也为 6.0.1。本次没有将运行库升级为 6.1.0，不能将结果表述为已经在 6.1.0 上验证。** 工作区另一个 `TKOTKCh/chainmaker-vm-wasmer` 仓库的 `v2.4.0_wasmer6.1.0@ec185bb521036877ef1fd88f3afea18e2cfcd26a` 未用作本次基线。

只修改新 worktree。原始 CVW 工作区存在的未提交修改、实验分支和其他 worktree 均未更改。未 push，未执行 reset、清理或删除用户文件。

## 2. 原始架构及代码确认的问题

以下位置均相对于 `chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/`，行号指原始提交，便于用 `git show c3e8f2cc:<路径>` 核对。

| 原始位置 | 由代码确认的行为 | 本次处置 |
|---|---|---|
| `vm_instances_manager.go` 的 `getVmPool` | 按 name_version 缓存 pool，启动后台扩缩容 | 业务入口改为 Module 缓存及固定线程执行 |
| `vm_pool.go:1019`、`:1229`、`:1243`、`:1255` | 一个 pool 的 `p.store` 同时参与 Module 编译、WASI/Imports 和多个 Instance 的创建 | 编译 Store 与每次执行 Store 分离 |
| `runtime.go` 的 `Invoke`、`InvokeTime` | 借出、归还已执行 Instance，跨次状态可延续 | 两个入口都使用相同 Fresh 路径 |
| `vm_pool.go:1272` 附近 | `_start` 的调用错误被忽略 | 初始化及启动错误返回并回滚 |
| `vm_pool.go:689`、`:708` | WASI 环境跨 Instance 回收复用；关闭路径与创建失败路径不同 | 每次调用拥有自己的 WASI 和宿主环境 |
| `wasmer-go/instance.go:138` 附近 | Close 不清空原生指针，Exports 被重复 Close | 注册表防重、清空指针、同步释放 |
| `wasmer-go/store.go:55` 附近 | 手动 Close 之后重复 Close 仍会调用原生删除 | Close 幂等；关闭后访问被拒绝 |
| `wasmer-go/*` 的 `runtime.SetFinalizer` | 原生对象可能在 GC finalizer 线程销毁 | 改为 owner 线程内确定性资源作用域 |
| `vm_instances_manager.go` 的 `StopVM` | 返回 nil，不 drain 和清理 | 停止接收、等待已接收工作、清理缓存、释放 owner |
| `vm_bridge.go` 的 `GetVmBridgeManager` | 双重检查中的首次读没有同步 | 使用既有 mutex 完整保护初始化 |

在这个准确的 CVW 基线中，没有 `CloneStore`、`NewInstanceByStore` 或 `NewInstanceFromModule` 这几个同名公开实现；实际函数是 `vmPool.newInstanceFromModule` 和 `wasmer-go.NewInstance`，不能把另一仓库的实现套到此基线上。

另已读取本地原生仓库 `origin/chainmaker/v6.1.0@9262eb118` 对应的 Rust `store.rs`：`wasm_store_clone` 调用 `store.inner.clone()`，而 `StoreRef` 内为 `Rc<UnsafeCell<Store>>`，因此仅共享底层 Store。相对地，原生 6.0.1 基线 `091074013fa056df0c6502262eae425927272e10` 中的 `wasm_store_new` 调用 `Store::new(engine.inner.clone())` 和 `Rc::new`。本修复实际只调用 `wasm_store_new`，没有以 clone 作为隔离手段。

**这些代码行为不等于已经发生数据泄漏。** 本次没有发现或声称有真实用户数据泄漏事件；原始池的跨请求状态保留也可能是此前有意采用的复用策略，但它不满足本交付的 Fresh 隔离目标。

## 3. 修复后架构及调用链

```text
原始：NewRuntimeInstance → getVmPool → p.store/p.module
      → pool GetInstance → 复用 Instance/WASI → CallMethod → RevertInstance

修复：NewRuntimeInstance → owner.Do → 缓存编译 Store / Engine / Module / 元数据
      Invoke 或 InvokeTime → owner.Do
      → 以缓存 Engine 调用 NewStore（独立底层 Store）
      → 当前 Store 的 WASI（若需要）/ Imports / CMEnvironment
      → NewInstanceInStore(module, imports, 当前 Store)
      → WASI Initialize（若需要）→ _start（若需要）
      → 设置 Gas → SimContext.CallMethod → 获取 Gas/结果
      → deallocate → 同步关闭本次全部原生资源
      → 返回调用方
```

- `SafeFreshOwner` 用 `runtime.LockOSThread` 固定原生线程。多个链 manager 共用该线程，各自拥有 Module 缓存，避免跨线程使用 `Rc<UnsafeCell<Store>>`。
- 每次执行使用 `NewStore(rec.store.Engine)`；Module 是可缓存的编译产物，不随每次 Fresh 重新编译。Go wrapper 的 `module.store` 仍保留编译上下文引用；实例化时显式传目标 Store，不再把该字段当执行 Store。
- Engine 使用同一个 Go Engine 对象以满足兼容条件。读取的 Wasmer C API Module 实现持有编译后的 `Module`，不持有执行状态；真实测试证明缓存 Module 可在同 Engine 的新 Store 中实例化。
- `NewInstanceInStore` 验证有效对象、Engine 和 Imports 的 Store 来源；导入来自另一 Store、来源不明或缺失时，在进入 C API 前报错。Exports 保存目标 Store；借用的 Function/Memory/Global/Table 有关闭检查。
- 缓存 key 是 name、version、字节码 SHA-256 的结构体，链与编译配置由 manager 固定。哈希只用于正确识别缓存内容；没有引入 SHA 性能优化、编译产物实验缓存或 Copy/CDO。
- 原来的 Gas 表、函数成本表、middleware 参数和 512 页上限从原始 `newVmPool` 原样提取到 `store_compile.go`。
- 同步跨合约回调允许在同一 owner 上内联执行，但子调用有新的 Store 和作用域；禁止从活动回调停止 owner 或删除仍被使用的缓存。**业务回调若换 goroutine 并同步等待，需要另行验证，不能假设支持。**

`vmPool` 旧构造器保留给已有计时调用代码作为兼容入口，但不再启动池后台循环。`RuntimeInstance` 经该入口构造时也转到 Fresh manager。直接借出原生 Instance 的旧 pool API 被拒绝；`getVmPool` 仅为旧包内测试保留报错签名。旧后台池代码未大规模删除，但生产 manager 不再创建或启动它，也没有配置开关可以退回旧业务路径。

## 4. 生命周期、回滚与必要依赖

每个请求资源作用域按逆序同步关闭：导出向量/Instance、Imports 容器与宿主函数、WASI、Store；编译作用域保留到缓存失效或 Stop，再关闭元数据、Module、编译 Store、Engine。作用域会继续尝试其余清理并汇总错误，重复 Close 不再次调用析构。关闭活动 native call 使用的作用域/Store 会被拒绝。

编译验证、缺少 Imports、Instance start section trap、WASI 初始化、`_start`、CallMethod、deallocate 的失败都沿同一作用域回滚。deallocate trap 不会跳过原生清理。native 清理 panic 会记录到 owner 的失败状态，拒绝后续 prepare，并通过 Stop 上报；native 清理失败时保留进程 owner 租约，禁止创建新 owner，需要进程级处置，不会将其当作清理成功。Go 无法拦截进程 abort、段错误或强制退出。

请求取消只影响入队阶段；已经进入队列的 Do 会等待执行和清理完成，避免返回后 native 代码继续访问事务上下文。Stop 停止接收新工作，并 drain 已接收工作；manager 的 Stop 并发、重复调用都等待同一结果。不同 manager 可独立停止；最后一个 manager 释放原生线程。Reset/缓存删除在 owner 上执行，并拒绝从活动父调用删除相关缓存。

移植过程中额外修正了三项与清理直接相关的问题：

1. Trap trace 向量的析构使用局部 C 向量值，避免 cgo 将 Go 对象内其他 Go 指针视为传入 C 的指针；`wasm_trap_origin` 返回的独立 Frame 也纳入释放。扩展异常测试曾实际失败，修复后重测通过。
2. 宿主 callback 环境改为 **C 分配的整数索引**，C 不长期保留 Go 对象地址；Go 注册表保活宿主对象，作用域关闭时释放注册项、C 函数 wrapper 和 C 环境。
3. WASI Initialize 前检查名为 `memory` 的导出及 Store 归属。原库缺少 memory 的路径在 Rust 中 unwrap，并曾在本次测试中实际 SIGABRT；修复后同一个失败 fixture 返回错误并正常回滚。

### 原生 Selector 关闭补丁

独立 Store/WASI 的同步删除还依赖 Step-35B 的一行原生补丁：`mio::Waker` 的 Token 从 0 改为与 `token_close` 相同的 1，否则 Selector 收不到关闭事件。未修改其他 Rust 实现。

- 原生源码基线：`091074013fa056df0c6502262eae425927272e10`。
- 对应补丁提交：`24b6afd798cafb01d86d1e2d5d5a7ccb0cc503fe`。
- 补丁和重建脚本：`native/store-lifecycle/selector-token.patch`、`rebuild.sh`。
- 重用已经由 Step-35B 构建、Step-36 使用的库，本次核对 SHA 并重新运行真实测试；**本次没有重新执行 Rust 全量构建**。
- 默认 `libwasmer.so` 及相同配置的 `libwasmer_cranelift.so` 更新；SHA-256 均为 `56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc`。
- 原始默认库 SHA-256：`dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。

二进制及来源清单随 Git 分支交付，不依赖实验目录的软链接。原生线程退出可能稍后完成；C 断言等待最多 2 秒验证静默线程回到初值，不把 wrapper 计数当作线程释放证明。

## 5. 与 Step-34～36 的代码对应关系

| 来源提交/实现 | 本次实现 | 适配说明 |
|---|---|---|
| Step-34 `9845db9841bc963634c8f7d28d644e8756d5ac22` 的 `step34_owner.go`、`wasmer-go/managed.go` | `store_owner.go`、`wasmer-go/managed.go` | 保留固定线程、作用域、反重入和错误字符串化；取消实验累计请求次数限制，改为有界队列和关闭 drain |
| 同上 `NewInstanceInStore` 及 bindings 改动 | `wasmer-go/instance.go` 等 | 显式目标 Store、Exports 指向目标 Store、确定性析构，并补充 import 来源验证和 Trap 清理 |
| Step-35 `c48cf9070710250f630a693217e79f90e3d375f6` 的 `step35_node.go` | `store_fresh.go`、manager、runtime | 使用真实业务入口；去除环境实验开关、静态内存 Copy 和观察代码；复用原始 Gas 配置 |
| Step-35B 原生 `24b6afd798cafb01d86d1e2d5d5a7ccb0cc503fe` | Selector patch 及 Linux amd64 两个库 | Store/WASI 删除真正收敛的必要依赖 |
| Step-35C `c6750469` 至 Step-36 `abc2ce356ad821c451c788d19cded9cbe21d55fd` 中 owner/节点同步释放路径 | manager 的 Stop、Reset、缓存关闭及同步返回 | 移植 VM 边界内的 drain；不移植 ChainMaker 节点/账本实验改动 |

代码对照读取的是各提交跟踪的 `experiments/instance-lifecycle/step-*/source/vm/`，并查看 git log/diff 和实际调用链；没有直接 cherry-pick 包含大量实验的提交。

## 6. 修改文件及原因

完整路径列表见 `audit/store-lifecycle/changed-files.txt`。VM 下的分组如下：

| 文件 | 修改原因 |
|---|---|
| `store_owner.go` | 固定原生线程、队列、同线程嵌套、进程级 manager 引用与退出 |
| `store_compile.go` | 从原始 pool 提取原样编译配置 |
| `store_fresh.go` | Module 缓存及独立 Store 的完整执行/回滚路径 |
| `runtime.go` | Invoke 与 InvokeTime 统一走修复路径，保留 Gas 导出辅助函数 |
| `vm_instances_manager.go` | 缓存生命周期、Reset/Close/Stop drain，替代执行 Instance 池 |
| `vm_pool.go` | 旧构造器转接，禁止借出句柄；停止旧后台池入口 |
| `vm_bridge.go` | 宿主 bridge 单例初始化的同步依赖 |
| `wasmer-go/managed.go` | 同线程资源注册、逆序关闭、活动调用/借用检查、计数与清理错误 |
| `wasmer-go/instance.go`、`store.go`、`engine.go`、`module.go` | 显式目标 Store、确定性所有权、防重与关闭检查 |
| `wasmer-go/exports.go`、`extern.go`、`function.go`、`memory.go`、`global.go`、`table.go` | 借用句柄和 Store 来源、宿主函数环境生命周期 |
| `wasmer-go/import_object.go`、`wasi.go`、`trap.go` | Imports、WASI、错误路径的同步清理和前置校验 |
| `wasmer-go/config.go` | 原生创建前校验 owner |
| `wasmer-go/exporttype.go`、`importtype.go`、`functiontype.go`、`externtype.go`、`memorytype.go`、`globaltype.go`、`tabletype.go`、`valuetype.go`、`target.go` | 将这些依赖对象的原 GC finalizer 纳入同一作用域；不移植这些析构会导致线程归属与释放顺序不完整 |
| `store_lifecycle_test.go` | 真实原生/业务路径测试，不修改原有测试 |
| `native/store-lifecycle/*`、Linux amd64 两个动态库 | Selector 必要补丁、来源、重建及原生线程测试 |
| `scripts/test_store_lifecycle.sh`、本报告、`audit/store-lifecycle/*` | 独立复验入口、修改清单和成功/失败证据 |

## 7. 测试与复验

环境：Linux amd64，Go 1.25.0，CGO，项目自带头文件与修复后的 Cranelift 动态库；`GOMAXPROCS=2`。没有运行其他实验或节点集群。

从仓库根目录运行：

```bash
# 常规 Go 安装直接运行；本机器的裁剪版 go 需要显式 GOROOT。
GOROOT=/usr/local/go GOTOOLCHAIN=local scripts/test_store_lifecycle.sh
```

脚本执行 VM 包 `go build`、真实测试的 `go test -race`、生成独立测试可执行文件再运行，以及严格编译/运行 C 线程收敛断言。产物在 `audit/store-lifecycle/bin/`，不提交生成的可执行文件。没有连接或替换现有实验节点。

| 验证项 | 结果及证据 |
|---|---|
| VM 包编译 | PASS；`validation.log` 对应脚本 `go build -p=2 .` |
| 两次及多次 Fresh，Module 缓存与独立 Store 并存 | PASS；两合约交替 40 次，精确检查 Store/Instance 创建与关闭差值及缓存数量 |
| Memory / Global / Table 隔离 | PASS；真实 WASM 校验初态、修改三种状态，下一次 Fresh 必须再次看到初态，否则 trap |
| 宿主 Imports 生命周期 | PASS；两个实际目标 Store 返回不同宿主值；跨 Store 和缺失 import 被拒绝；scope 后宿主注册项归零 |
| Instance 创建、合约、WASI `_start` 失败 | PASS；真实 start section trap / unreachable，逐次验证对象与 Store 计数恢复 |
| WASI 初始化失败 | PASS；缺少 memory 的真实 WASM 返回失败且完整回滚；此前 abort 的失败日志也保留 |
| deallocate / 关闭错误 | PASS；真实 deallocate trap 后 native 资源仍平衡；owner cleanup 的真实 trap 能由 Stop 返回 |
| 正常 Close、重复 Instance/Store/owner/manager Close | PASS；重复释放无额外析构，已关闭 Function 使用被拒绝 |
| 并发执行、Stop、嵌套回调和活动关闭 | PASS；Go Race Detector 无报告，真实宿主回调中拒绝活动 Close，子 Store 调用返回预期结果 |
| 取消 | PASS；已接收调用取消后仍等待清理完成；停止接收后拒绝执行 |
| 真实 Go 合约 | PASS；基线 `testdata/compute-go.wasm` 经生产 manager/WASI/_start/CallMethod 执行两次，检查 `bigNumCal` 数学结果和 WASI 计数平衡 |
| 原生 WASI 线程回收 | PASS（补丁库）；4 次创建删除，原库静默线程 `1→5`（断言失败），补丁库 `1→1`（通过） |
| `go vet .`（VM 包） | PASS |
| 原有 `go test ./...` | FAIL；原生绑定旧测试参数签名不兼容；旧 pool 探针仍要求已禁用的 Instance 借出路径，部分旧 fixture 缺失。未修改或删除这些测试 |
| 原有 `TestInvoke` 默认配置 | 缺少 `compute-test-go.wasm`；显式指定 `compute` 后，原测试全局 `ContractName` 为空，触发 manager 的输入校验。见 `original-invoke.log` |
| 仓库根 `go build ./...` | FAIL；遗留嵌套 Git 元数据导致 VCS stamping 失败；`-buildvcs=false` 后仍因未修改的 `test/output/formatTest.go` 的 int32/uint64 类型冲突失败。VM 修复包独立编译通过 |

完整成功输出：`validation.log`、`repair-race.log`。原库/补丁库线程对照：`native-original.log`、`native-patched.log`。未通过项：`original-suite.log`、`original-invoke.log`、`root-build*.log`。中间失败见 `port-trace-cgo-failure.log`、`port-wasi-abort.log`；它们是移植过程中发现并修复的问题，不是最终测试结果。

业务测试使用真实 Wasmer、WASM 和实际生产调用链。真实 Go 合约的链上下文由仓库既有测试夹具提供，因此它是 VM 集成测试，不能替代真实节点、账本及跨链集成验证。其余纯 WASM 状态和原生 C 线程测试不依赖 Mock。

## 8. 尚未解决的问题与安全边界

**已确认的限制：**

1. 交付验证范围是当前基线的 Linux amd64 / Cranelift / Wasmer 6.0.1。6.1.0、LLVM、其他架构/操作系统的库未替换或验证；保留的原始库不能自动视为含 Selector 修复。切换运行库须重新构建和复验。
2. 所有原生对象 API 必须在有效 owner 线程和作用域内使用；不能把句柄交给任意 goroutine。旧低层测试/工具若直接使用 Store/Instance，要按这一约束适配。`Pool()` 不能再用于生产业务借出原生 Instance。
3. 固定线程会串行执行多个 manager 的 native 调用，这是原有 Step-34 安全模型的移植，可能降低吞吐；本次没有性能优化或吞吐保证，也没有保留不安全复用开关。
4. 项目原有全量测试和根目录示例构建没有全部通过。没有降低断言、删除测试或把这些失败写为 PASS。
5. C/Rust abort、段错误、OOM kill、进程强退不可能由 Go defer 完整回滚。已修复观测到的 missing-memory 初始化 abort 入口，未宣称覆盖所有 Wasmer 原生错误。
6. 全节点 StopVM 与账本、存储、共识后台 goroutine 的顺序不在这个 CVW 仓库内。未移植 Step-35C 的外部 ChainMaker 账本改动，未在现有实验集群上做节点退出验证。

**潜在风险及未验证假设：**

- 长期运行的 RSS、所有原生 worker 的长期收敛和大量合约版本缓存增长没有压力测试；计数平衡只证明 wrapper/注册项路径，不能证明整个进程无原生泄漏。Module 缓存目前与基线相同未设置容量/淘汰策略。
- 外部修改编译配置、预先加载其他 `libwasmer.so`、在 C 中保留额外句柄，均超出当前所有权约束。复验脚本固定 `LD_LIBRARY_PATH`，交付者应核对实际加载库的来源和哈希。
- 没有审计所有宿主接口本身的内存边界检查、WASI 权限模型或通用沙箱安全。Store 隔离不等于完整的多租户安全证明。
- 原生补丁二进制来源已经核对，复验已通过；本次未从 Rust 源码全量重建，重建脚本需要网络、Rust 1.81.0 和对应构建依赖；不同工具链下的二进制哈希不保证相同。

## 9. 给审查者的重点

优先检查：真实 Invoke/InvokeTime 是否都只进入 owner；Module 与目标 Store 的 Engine 一致性；Imports/Exports 的归属及逆序销毁；嵌套调用与 Stop/Reset 的互斥；宿主环境的 C 分配和注册表释放；WASI memory 前置检查与 Selector 单行补丁。然后复跑脚本，阅读所有失败记录，再决定是否将此分支用于超出上述验证边界的环境。
