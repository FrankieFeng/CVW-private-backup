# CVW Copy + A对齐：集成候选交接

状态：**共同基线上可构建、最小正确性/Gas验证通过的候选分支；尚未与Store泄漏修复合并验证。** 未push。

## 基线与改动边界

- 分支：`integration/copy-arena-candidate`；独立worktree：`/home/frankie/mygitprojects/.worktrees/cvw-copy-arena-integration`。
- 共同基线：`c3e8f2cc1479a11450d61e342a93c3b2416b7cff`。
- 本地王浅秋修复候选`ae7c779dbbbc3f3da3a28242e7b7169ff705b860`的直接父提交也是该基线；依据`STORE_LIFECYCLE_REPAIR_CN.md`确认，不猜测远端当前main状态。
- 基线、主工作区、历史实验未修改。没有合入Owner、安全策略、Worker、S2、SHA优化、Runtime替换、Pool容量/刷新/丢弃/关闭修改。原基线已有的日志/行为保留，没有引入新性能插桩。

## 选择依据与来源

### Copy C0（Host）

路径前缀`chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/`：

- `copy_static.go`：提取既有staticMemoryPlan，解析并冻结初始化Image/Ranges；编译NoData模块，实例创建后恢复相同静态内存。
- `vm_pool.go`：仅增加计划字段、可选编译输入选择及恢复接入点；`copy_static_test.go`为最小验证入口。
- 来源：历史Original Fresh F1/F3冻结实现`of_static.go`，后由`17170d188`/`2062b69c9`实验快照保留。提取的是相同C0算法，不是这些提交的Worker/Store方案。删除未使用profiling类型、耗时字段和实验字节统计；没有改解析/恢复算法，也没有重新实现Copy。
- 运行时依赖仅原wasmer-go Module/Instance/Memory API及pb-go Contract类型，不依赖实验Runner、Owner或Artifact。

### A对齐（Guest）

**本轮A指既有Step18 Arena padding，不是Host allocator改造。** 选同源Guest parity后的版本，排除旧Toolkit Plain/Arena构建差异严重、Gas不一致的那组。

- `integration/copy-arena/prepare_alignment.py`复用历史`guest-parity-20261113/build_pair.py`布局解析及公式，生成padding；没有另创算法。
- `compute/`和`erc721/`中的`.go.example`是已通过parity的padding样例；扩展名避免进入Host构建。
- Guest业务源码身份：`95903a3ea031893305e6e9c660f24ec4157642ea`；Go1.24.1、同依赖、同目录/命令，padding外输入一致。构建身份见GUEST_BUILD_PROVENANCE.json。
- 已有公式：`padding = 4MiB - plain.bloc - 5*64KiB`，Arena目标bloc=3866624。必须对每个精确Plain Guest重新计算、构建后复核，不能给所有合约硬套样例长度。Go版本/链接布局变动需要重新验证；不承诺任意WASM支持。

## 配置与顺序

| 配置 | Copy | A对齐 |
|---|---|---|
| 原行为 | CM_CVW_COPY未设置/0 | Plain Guest |
| Copy | CM_CVW_COPY=1 | 同一Plain Guest |
| A | CM_CVW_COPY=0 | 同源padding Guest |
| Copy+A | CM_CVW_COPY=1 | 同源padding Guest |

开关在Pool构造时读取；不支持对存活Pool热切换。未知布局/不支持的数据段在Copy启用时返回错误，不伪装成功。A是Guest选择，无Host运行时A开关。Copy可单独启用，A可单独启用，不互相依赖；Copy必须读取最终实际Guest字节，而非使用Plain计划恢复Arena实例。

顺序：最终Guest→一次构建静态计划→编译NoData Module→新Instance→恢复Copy→WASI Initialize→原_start→原业务/Gas。每个Module绑定独立计划；不可将计划跨不同Module/Guest使用。

## 本次验证与历史证据

本次构建Go1.25.0、`-ldflags=-checklinkname=0`，冻结Native为既有6.0.1构件，未替换/重编Native。

1. TestCopyStaticCandidate：真实Native模块，数据恢复为hello；错误配置身份被拒绝。
2. TestCopyArenaCandidateBusiness：复用原runtime_test.go准备函数、SnapshotMock及RuntimeInstance.InvokeTime，真实compute.bigNumCal；四组各1笔，固定同TxID，完整ContractResult（含Gas/事件）与RWSet JSON一致，Gas均120027、返回success。此读操作测试不冒充写业务全覆盖，也不报告TPS。
3. A工具生成compute padding与历史样例逐字相同；对冻结Arena复核bloc通过。
4. 首次业务测试仅因旧夹具每次生成不同TxID而不相等；保留失败日志，随后固定实际输入TxID，没有忽略RWSet字段。

验证清单及精确SHA：`integration/copy-arena/VALIDATION.json`。原始本机日志和离线依赖工作文件保留在`/home/frankie/mygitprojects/integration-validation/copy-arena-20261119/`，没有带进优化代码分支。

历史参考：`guest-parity-20261113/GUEST_PARITY.md`的bigNumCal/setApprovalForAll2/transferFrom各10对，共30/30，Gas/return/RWSet/events/状态一致；`unified-guest-20261114`及VM-Only Run `20261115T221351-5f6ac2cd`保留统一Guest五组性能。setApprovalForAll2历史VM Invoke TPS：Original Reuse3891.321、Original Fresh447.471、Copy577.821、Arena679.349、Copy+Arena1065.625。**不是本候选重新测量的收益**，更不是与泄漏修复合并后的性能保证。历史Pool关闭异常仍需区别于业务语义通过。

## 合并顺序与未解决事项

建议先合入王浅秋的Store/泄漏修复，再合入本分支纯Copy helper和Guest对齐工具，最后人工迁移创建路径的极小接入点并跑回归。也可从共同基线先cherry-pick本分支，但不能以无冲突视作语义兼容。

关键冲突：现有修复分支引入`NewInstanceInStore`及执行Store生命周期，业务不再使用本基线vmPool创建路径。**只cherry-pick vm_pool.go会可能使优化不在实际执行路径生效。** 应在缓存Module记录上放Copy计划，在修复后的实际NewInstanceInStore后恢复该实例自己的Memory，再执行WASI/_start。保持修复后的资源作用域及错误清理；不要为本优化撤掉其Store修复。

修复Module缓存标识必须包含Copy编译模式/配置，避免同一原始Guest SHA对应的NoData和原Module误用；当前候选一个Pool只固定一种模式，不引入缓存架构修改。初始化失败清理仍按接收方修复实现处理。本轮未验证其生命周期修复与NoData编译缓存的组合，未证明线程安全或Native内存释放。

原测试依赖解析复用现有离线工作文件（protocol/vm/utils旧工作树，store为Step36既有镜像），没有提交依赖替换。接收方应使用自己的正式依赖图复验；本机PASS不能证明所有依赖版本兼容。不是可直接发布的生产版本。

## 构建和回归命令

在完整CVW依赖环境中，设置接收方本机合法GOWORK与Native库路径，然后：

```bash
cd chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0
# Go1.25本机验证命令；如接收方使用其他工具链，须记录实际版本
GOMAXPROCS=2 go test -p=2 -ldflags=-checklinkname=0 -run '^TestCopyStaticCandidate$' -count=1 -v
CVW_INTEGRATION_GUEST_DIR=/absolute/path/to/frozen/artifacts/compute \
GOMAXPROCS=2 go test -p=2 -ldflags=-checklinkname=0 \
  -run '^TestCopy(StaticCandidate|ArenaCandidateBusiness)$' -count=1 -v
```

Guest构建：在隔离源码目录、相同Go1.24.1和锁定依赖下，先运行`GOOS=wasip1 GOARCH=wasm CGO_ENABLED=0 go build -trimpath -buildvcs=false -o guest.wasm .`取得Plain；用prepare_alignment.py生成该目录的新layout_pad_step18.go；原样再构建Arena；`--arena`复核目标布局。生成脚本拒绝覆盖已有文件。不可在用户dirty Guest目录操作。

```bash
python3 integration/copy-arena/prepare_alignment.py plain-new.wasm /new/path/layout_pad_step18.go --arena arena-new.wasm
```

合并修复后：上述Native/static+四组测试先过；随后在实际修复Factory路径复用既有guest parity夹具验证bigNumCal、setApprovalForAll2、transferFrom的四组逐笔Gas/return/RWSet/events/状态，并验证Instance/Store关闭配平。当前最小测试走原Runtime InvokeTime，不能替代迁移后的Factory路径回归；没有虚构适配后的Runner开关。本轮不启动四节点或37方法完整实验。

## Git交付

Copy Host及最小测试为一个提交，对齐工具/样例和交接文档为后续提交；可顺序cherry-pick。提交SHA见`git log integration/copy-arena-candidate -2 --oneline`。相对基线差异：

```bash
git diff c3e8f2cc1479a11450d61e342a93c3b2416b7cff..integration/copy-arena-candidate
git format-patch c3e8f2cc1479a11450d61e342a93c3b2416b7cff..integration/copy-arena-candidate
```
