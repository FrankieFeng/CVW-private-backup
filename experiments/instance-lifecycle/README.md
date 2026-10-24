# Instance lifecycle 第一批实验（2026-10-08）

本批保留当前 no-reuse 策略，不修改合约、Wasmer binding 或池大小常量。
日志保存在本目录，不依赖 /tmp。

## 修改

- instance_lifecycle_trace.go：CM_INSTANCE_LIFECYCLE_TRACE=1 才启用；读取 linear memory 的地址、长度、页数、SHA-256，输出 JSON 行。
- vm_pool.go：提前生成已有 UUID；T0–T5/T8；关闭后和 channel 发送完成后不再读取 memory。
- runtime.go：Invoke / InvokeTime 的 T6/T7。
- sim_context.go：业务导出调用前后快照。
- instance_lifecycle_test.go：10 个 fresh 实例（前 5 个首次调用）；另做 5 次 no-reuse 调用，每次等到补充实例入池。

module_id/store_id/wasm_instance_ptr 是 Go wrapper 身份，仅进程内有效；memory_ptr 是底层 linear memory 地址。
T0/close_done/enqueue_done 的 memory 字段缺省，表示不可读取。
T3 原样记录 _start 返回，未修改错误处理策略。

## 结果

两次独立测试进程均通过。每轮共创建 17 个实例：1 验证、10 fresh、1 池预置、5 补充。

- T1 instantiate 和 T2 WASI Initialize 后：17 个样本均 49 页，全部 hash 相同；两进程也相同。
- T3 _start 返回后：均 128 页 / 8 MiB；17 个 hash 各不相同。10 个 fresh 的 hash 也各不相同。
- _start 原始返回均为 `WASI exited with code: ExitCode::0`；后续业务成功。不能写成“返回 nil 的初始化成功”。
- run-2 中 fresh 对第一份 clean 快照：差异 1119–1199 字节，涉及 6–7 个 64 KiB 页；仅记录前 32 个不同字节偏移，尚未定位变量。
- SetGas：每次修改 14 字节、涉及 2 页，无扩页。
- CallMethod：每次修改 4749–4750 字节、涉及 12 页，无扩页。这包含 runtime 查询、allocate、参数写入和业务调用，不等同于业务函数本体。
- 两轮每个 no-reuse 调用均有 drop → close_done → 新 ID 创建/入池；5 个调用 ID 各不相同。
- 首次调用、no-reuse 和关闭 trace 的基线 Gas 均为 105920。
- trace-disabled-baseline.log 中没有 LIFECYCLE 输出，5 次调用均成功。

判读：页数稳定不代表字节稳定；首次调用无需扩页也能产生 dirty memory。
全 memory 字节级 clean state 在当前样本中不成立；不等于证明初始化有交易污染。
时间、随机数、Go runtime 调度或 WASI 环境等可能来源尚未归因。
没有读取内部 globals/tables/Store/WASI 状态；没有做二次复用对照。
全内存 hashing 会改变宿主时间，本批数据不用于 TPS 或耗时优化结论。

## 重跑

```bash
cd /home/frankie/mygitprojects/CVW/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0
GOROOT=/usr/local/go /usr/local/go/bin/go test -count=1 -run '^TestInstanceLifecycleMinimal$' -v . \
  > /home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/run-next.log 2>&1
```

run-1.log/run-2.log 是两次独立进程；summary.json 是提取的阶段统计和内存差异。

## 回滚

backup-before-trace 保存修改前的三个文件，包含用户原有未提交改动。
trace-only.patch 仅包含本批对这三个文件的修改，已验证反向应用检查通过。
不要 git restore 这些文件，会丢失此前工作。

在 CVW 根目录先检查，再反向应用；如后续修改冲突，先审阅 patch，不要覆盖备份：

```bash
cd /home/frankie/mygitprojects/CVW
git apply --reverse --check experiments/instance-lifecycle/trace-only.patch
git apply --reverse experiments/instance-lifecycle/trace-only.patch
```

然后删除本批新增的 instance_lifecycle_trace.go 和 instance_lifecycle_test.go。
实验日志与报告可保留。

## 第二批结果

见 [step-2/README.md](step-2/README.md)：部分 fresh 差异对应随机状态和时钟；同实例回池保留 dirty memory；两次调用 Gas 相同，未复现 Gas 不一致。

## 第三批结果

见 [step-3-mint/README.md](step-3-mint/README.md)：已有插桩 ERC721 mint 在完全相同序列化参数和写集下，同实例 Gas 27190 → 21735；当前默认 Wasm 则为 235 → 235。生产策略未修改。

## 第四批结果

见 [step-4-mint-gas-path/README.md](step-4-mint-gas-path/README.md)：减少的 5455 全部位于 JSON Marshal 路径；编码器首次构建 5414、查询差额 -12、缓冲扩容 68、对象池差额 -15。JSON 之外两次完全相同。

## 第五批结果

见 [step-5-json-warmup/README.md](step-5-json-warmup/README.md)：已有同类型 JSON 预热后首次 mint 即为 21735，原首次为 27190；输入、写集、扣费 site 计数均完成对照。未改生产复用策略。

## 第六批结果

见 [step-6-lazy-init/README.md](step-6-lazy-init/README.md)：分场景检查哪些 lazy initialization 可提前完成。
同类型 JSON 编码可提前构建编码器/字段缓存，并在本样本中建立编码对象池和缓冲容量；
runtime_type、空结构体 JSON 解码未降低首次 mint Gas。重复预热不进一步降低 mint Gas，11 个独立测试进程通过。

## 初始化状态可复用性分析

见 [step-8-state-model/README.md](step-8-state-model/README.md)：以 S0/S1/S2/S3 边界观察 8 个标准 Go 合约和 1 个 TinyGo 对照件；记录逐页哈希、global、table size 与 `_start` 内的 `memory.grow`，并区分“跨实例稳定”和“已证明可安全恢复”。

## S2/S3 不一致状态定位

见 [step-9-unstable-map/README.md](step-9-unstable-map/README.md)：使用 step-8 的逐字节差异并集和前两份完整快照，输出不一致页的 byte 比例、偏移区间、8 合约交集及来源证据；定位 ChaCha8 状态、hashkey、Go g 跟踪字段、Map seed 和 SetGas 写入。

## 确定性初始化前移诊断

见 [step-10-deterministic-init/README.md](step-10-deterministic-init/README.md)：对 4 个合约的 960 次 fresh Instance 拆解 S0/S1/S2 成本，比较原始 initial memory 与 128 页、追踪 `_start` 内的 `memory.grow` 和 `memclr`，并评估 Module metadata 与 data segment 预计算候选。未改生产代码，也未恢复 S2 snapshot。

## S1 静态初始化成本

见 [step-11-static-init/README.md](step-11-static-init/README.md)：在固定 160 页的合成 Wasm 上改变 data 大小、段数和 globals 数量，测量 fresh Instance 的 S1 成本及预计算 memory image 的独立拷贝对照；保留逐字节 S1 image 核对和实例隔离验证。

## Data segment 原生实例化成本

见 [step-12-data-init/README.md](step-12-data-init/README.md)：固定 8 MiB 编码 payload，比较 1/8/32/128 段（另补 2/4 段）与不同 offset/覆盖方式；复用诊断 profile 把 `wasm_instance_new` 与 Go wrapper 分开，并用相同最终 image 校准辨认 segment、字节物化和页面覆盖的可识别边界。

## Data segment merge 原型

见 [step-13-data-merge/README.md](step-13-data-merge/README.md)：独立命令行原型只重写可证明等价的 active Data Section；在 step-12 合成件上验证 module、S1 memory hash、导出函数和 fresh 隔离，并配对测 `wasm_instance_new`。真实 compute 合约也做了 S1 适用性对照。


## 实验命名约定

后续实验统一使用`step-N-<英文描述>`目录前缀，文档名称使用“step-N 中文主题”。本轮为[step-20 端到端性能归因](step-20-e2e-performance-attribution/README.md)，原名称E20不再用于新文档和新实验。原始历史日志及命令保留当时标识。


## Step-21 多合约Instance复用性能损失复现

见[Step-21报告](step-21-instance-reuse-loss/README.md)：六方法小样本检查；首批正式R1的满队列维护排空失败后停止，三批主矩阵未完成，全部原始记录及E类结果保留。
