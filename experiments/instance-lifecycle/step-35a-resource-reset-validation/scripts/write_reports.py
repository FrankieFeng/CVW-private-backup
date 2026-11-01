from pathlib import Path
import json,csv
P=Path(__file__).resolve().parents[1]
def put(n,s):(P/n).write_text(s.strip()+'\n')
put('README.md','''# Step-35A：节点资源收敛与Reset生命周期验证

**Reset/Stop阻塞已修正并通过节点验证；Step-36仍不准入，当前明确阻塞是固定native库的WASI线程回收。** 不启动正式Copy E2E矩阵。

基线 `experiment/step35-node-fresh-integration@c48cf907`。独立工作树 `.worktrees/cvw-step35a`，分支 `experiment/step35a-resource-reset-validation`。生产VM、历史数据、Guest、Gas、Go/Wasmer版本不变；native SHA仍为`dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。全程1536MiB软RSS/220线程，未提高上限。

已复用Step35的六轮24笔交易进行历史复算；新增仅14笔成功提交的compute/buyNow/Reset期间请求，以及1个在Stop中未确认提交的请求。不是重跑全功能或性能矩阵。新增6次buyNow均有真实六个下游；所有四个测试节点进程正常退出，Store/Instance配平，pending0。

| 本轮结论 | 证据 |
|---|---|
| RSS不能整体判泄漏 | Reset释放正常Module缓存；显式GC降低live heap；单独scavenging使已空闲Go页返回OS |
| 部分RSS来自allocator保留 | resource2 Reset后glibc仍有约380MiB free arena；free不等于已经归还OS |
| 线程未收敛，已定位到native/WASI创建关闭路径 | 24次WASI创建/删除配平后多24个epoll线程；Reset/GC/scavenge不清除 |
| 纯C排除Go/节点干扰 | Store-only四次后线程仍1；WASI四次后静默3s线程5，其中4个epoll；单次WASI残留1个epoll持续10s |
| 真节点Reset通过 |9次实际Manager Reset，含空闲、连续、compute和buyNow在途；后续交易正确提交 |
| Stop/Reset竞态已修复 |Stop改为等待正在进行的Reset完成；两个顺序unit测试和真实节点重叠Stop/Reset通过 |

源代码可直接阅读 `source/vm/step35a_control.go`（0600 Unix socket触发实际Manager）、`step34_owner.go`（最小Stop等待修正）、`wasmer-go/step35a_resources.go`（只读诊断，含固定ELF私有布局探针，禁止作为通用生产ABI）。完整diff在audit/source.diff。

RSS、线程和native剩余问题分别见RSS_ANALYSIS.md、THREAD_ANALYSIS.md、NATIVE_LIFECYCLE.md。Reset证据见RESET_TEST.md。报告不把句柄配平当作所有后台任务已关闭，也不把forced GC/scavenge当正常运行配置或准入条件。

现有native二进制Selector.shutdown反汇编与本地当前源码不一致，旧双waker实现是有证据支持的候选原因；未在本轮重编native或验证补丁，不能声称某个patch已解决。后续最小工作是固定native构建来源，在独立native实验分支验证Selector/WASI线程关闭修复；不继续修改Copy或提高资源阈值。

运行脚本拒绝覆盖旧日志/账本。网络账本由已正常停止的Step35小账本复制到`/tmp/cvw-step35a-diag`，未改存储配置；测试凭据仅存在/tmp，不打包私钥。native/binaries不入Git，使用已有固定库并校验SHA。无远程推送。
''')
put('RSS_ANALYSIS.md','''# RSS与Go Heap归因

## 历史复算

HISTORICAL_WAVES.csv复用了Step35原始六轮24笔交易；未把它们计为本轮新独立样本。每轮结束Go heap为705.399、780.591、855.771、930.934、521.580、597.088MiB。第5轮发生GC，NumGC从8至9，HeapSys仍约994.6MiB、HeapReleased仅约6MiB；live heap下降不要求RSS同步下降。

原资源轮询只有`monotonic_s`，VM日志为`wall_ns`，没有保存可审计的历史转换偏移。逐轮RSS/线程、goroutine、WASI计数和静默快照缺失；不能用后来时钟校准伪造精确轮末数据。整体RSS峰值1481.109MiB仍有效。新同步快照补齐本轮测量，不能冒充原六轮记录。

## 新有界诊断（resource2，四个缓存合约，非Step35五合约全集）

| 阶段 | RSS MiB | Go heap MiB | HeapReleased MiB | glibc in-use MiB | glibc free MiB |
|---|---:|---:|---:|---:|---:|
| 3轮compute/buyNow后静默 |1214.35|750.75|5.56|238.68|352.32|
| 实际Manager Reset后 |1052.85|750.92|5.34|22.74|380.30|
| 单独诊断GC后 |1053.12|477.74|5.00|22.74|380.30|
| 单独诊断Go scavenge后 |781.41|477.61|276.86|22.74|380.30|

直接支持：

1. Reset清除4个Module缓存后native glibc in-use减少约216MiB，属于正常长期缓存释放；缓存不是业务Instance复用。
2. GC回收约273MiB live Go对象，但还在Go heap保留页中；scavenging后RSS下降约272MiB，HeapReleased相应增加。这部分并非不可释放的native线性内存。
3. glibc仍报告约380MiB空闲arena，表明部分已free内存没有立即归还OS；mallinfo2不是Rust/Wasmer专用计量，不覆盖全部mmap，也不能把全部free arena视为全部resident。
4. 进程RSS包含Go页、native allocator、代码/文件映射和线程等，不能仅凭RSS斜率给出统一“内存泄漏”结论。

resource1独立诊断观察到同方向：Go heap739→478MiB，RSS1016MiB基本不随单次GC下降，scavenge后749MiB。没有改GOGC=100、GOMAXPROCS=2，没有malloc_trim，没有把强制回收插入业务请求之间。

边界：自然观察窗只有有限3轮和约1秒静默；RSS未证明长驻平台。本轮峰值最高1214.668MiB，低于1536MiB，但不能用forced scavenge后的低RSS宣称正常服务准入。已直接发现native线程持续残留，对应栈/selector资源也可能贡献内存，尚未完整量化。
''')
put('THREAD_ANALYSIS.md','''# 线程未收敛：有native/WASI因果对照

resource2同一节点，常规GC/参数不变：

| 检查点 | 已创建/关闭WASI | OS线程 | epoll等待线程 | Go thread-create records |
|---|---:|---:|---:|---:|
| 启动 |0/0|8|1|9|
| 第1轮后 |8/8|17|9|14|
| 第2轮后 |16/16|27|17|16|
| 第3轮后 |24/24|35|25|16|
| 静默、Reset及GC/scavenge后 |24/24|35|25|16|

新TID和wchan原件在snapshot JSON。Go thread-create profile为累计记录，不能与当前OS TID一一对应；但后两轮该记录不增，OS epoll线程仍每8次WASI增加8，不能都归因于Go M缓存。

纯C对照使用完全相同native so，不运行Go、Guest或节点：

- 4次Store创建/删除，Engine关闭后及静默3秒始终1个主线程、0 epoll。
- 4次Store+WASI环境创建/删除，所有Store的最后strong count均1；Engine关闭、静默3秒后仍5线程/4 epoll。
- 另一个仅1次WASI的进程，静默1、3、10秒均为2线程/1 epoll。

因此，已经直接复现WASI创建/关闭路径的线程回收缺陷或至少观察窗内持续残留，不是只有“缺少安全证明”；不是合约业务或Go Finalizer造成的必要条件。不能将10秒有限观察写成数学上证明永不退出，但当前也没有平台证据。

源码/二进制指向virtual networking Selector：本地候选源码PluggableRuntime::new会创建LocalNetworking/Selector及独立poll线程。当前源码shutdown设置close_requested并wake；实际固定so的Selector::shutdown @0xabf070只调用mio Waker::wake（重定位及反汇编已保存）。旧实现有两个waker/token；历史修复`e3c75f14f3d`改成单waker+关闭标记。本轮仅保存该patch供定位，未修改或重编so。

已证实：native存在Selector符号，实际shutdown机器码与当前候选源码不同，WASI-only产生epoll残留。尚未完全证实：每个残留TID的用户态栈正是该Selector，以及该历史patch单独能消除当前二进制缺陷。gdb本地未安装，未为此更新环境。

不采用WASI复用、进程反复重启或线程上限放宽来掩盖增长。下一步必须在可追溯native构建上修复并验证关闭/唤醒/线程退出。
''')
put('NATIVE_LIFECYCLE.md','''# Native生命周期：计数、实际析构与剩留任务

固定实际库SHA为dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9（Step35相同，版本6.0.1），未重编/升级。节点加载maps、纯C RUNPATH/ldd及systemd loader环境在audit/raw_logs；不存在LD_PRELOAD替换。

- Go Store.Close -> wasm_store_delete。实际ELF @0x2ce610取Rc块并dec strong；仅减至0才调用StoreInner drop。CAPI调用计数本来不能单独证明Drop。
- 本轮只读探针固定上述ELF布局，在Owner线程、有效Store删除前读取strong，不写native内存、不改变ABI。resource2的24个runtime Store加4个compile Store全部strong=1，shared=0；调用返回且反汇编分支支持最后引用析构已执行。该私有布局不是生产接口，换库必须撤销/重新审查，不能拿它作为独立Store隔离证明。
- Instance.Close先清export/import vector，再wasm_instance_delete；Memory借用跟随Instance/Store。源码候选StoreObjects持有memory/table/function arena，Mmap::drop对系统映射munmap。精确整个native构建来源仍未锁定，不把候选源码每一行当实际二进制。
- WASI env delete调用on_exit并删除环境引用。新增计数显示空闲快照WASI与Imports容器全部配平，host函数登记归零；ImportObject计数是Go容器生命周期，不能称为每个native extern的物理释放计数。
- Module/Engine/compile Store在缓存有效期长期保留；实际Manager Reset关闭它们，native in-use显著下降，属于预期缓存。
- glibc arena free增多但RSS未同步释放，属于已free仍保留的资源；Go heap idle/released证据另见RSS_ANALYSIS.md。

关键反证：即使Store进入最后strong析构分支，pure-C的WASI环境与Engine也关闭，仍遗留epoll线程。因此Store析构、Instance配平和WASI API delete不等于所有native后台任务退出。问题已收敛至WASI/native网络运行时关闭路径。

候选实现LocalNetworking.Drop调用Selector.shutdown；实际二进制也有对应析构和shutdown符号，后者仅wake。旧双waker与当前单waker修复的关系有静态证据，尚未通过原生补丁验证。不得直接编译本地当前全量源码替换so以宣称通过，因为这会引入不可审计的其他差异。

本轮Go源码只做Stop/Reset同步修正、Unix诊断入口和只读计数/观测；不改Guest、Gas、A/Copy或native ABI。未来最小native实验需恢复构建来源，仅修复Selector/WASI关闭，先重复本轮C对照，再验证节点Reset，最后才考虑E2E。
''')
put('RESET_TEST.md','''# 真节点Manager Reset验证

Unix socket只在CM_STEP35A_CONTROL显式设置时创建，权限0600，无TCP监听。/reset POST直接调用实际节点InstancesManager.ResetAllPool，未用内部clear函数冒充公共入口。/state只读Owner准入状态；/snapshot通过既有Owner取数并计入32-job预算。生命周期数据与原始控制响应保存。

实际节点9次Manager Reset：resource1的两次空闲/连续Reset；reset1的空节点Reset、compute在途Reset、buyNow在途Reset；resource2两次空闲Reset；stop-reset-race空闲及在途Reset。全部返回nil，9个开始/结束配对。

- compute在途Reset约545ms、buyNow在途Reset约2004ms；先排空当前调用，buyNow六次真实下游完整返回。
- Reset清理后可继续真实交易，缓存重新建立。两笔Reset期间提交的compute请求都成功提交；其真正进入VM在manager_reset_end之后（ADMISSION_ORDER.csv）。因此本次观察到节点排队，不是丢弃，也没有伪称VM层发生了拒绝。
- Owner层拒绝新job的分支由unit直接验证；本次节点调度没有让这些后续交易在resetting窗口进入VM。两类证据分开。
- 没有触发旧resetC无缓冲发送路径，新适配器仍路由到Owner.Reset。
- Stop/Reset源代码发现：原Stop在resetting时返回ErrOwnerClosed，节点可能继续关闭账本。新代码等待resetDone，然后执行Stop；先Stop后Reset则拒绝Reset。两个unit顺序通过。
- 真节点stop-reset-race在Reset等待真实在途compute时SIGTERM，Stop等待Reset和当前调用；Store2/2、Instance1/1、pending0、进程exit0。客户端因停机未收到成功响应，提交未确认，不能写成“Stop时交易绝不丢失”。Reset正常组的在途/排队交易均逐TxID查到了提交。

Reset后：Module缓存0、Store创建关闭配平、WASI/Imports配平、host登记0，但native epoll线程不随Reset下降。所以Reset协议功能通过不等于资源准入通过。

原始证据：reset1-node.log、*-reset-*.json、*-admission-*.json、stop-reset-race-node.log，RESET_EVENTS.csv、COMMIT_CHECKS.csv、owner-both-orders.log。没有全局执行锁、100ms补池等待或关闭守卫；1秒静默窗口只用于观察资源，forced GC/scavenge在业务完成且Reset之后单列。
''')
put('SAFETY_GATE.md','''# Step-36准入：不通过

| 条件 | 判定 |
|---|---|
| Store/Instance调用级创建删除配平 | PASS；4节点进程退出，pending0，51实例/66 Store总体配平 |
| 最后strong析构分支 | resource2及C对照有直接只读观测；不是仅CAPI次数推断 |
| RSS归因 | 部分通过：缓存、Go retained页、glibc free arena有直接证据；自然长驻平台未证明 |
| 线程收敛 | **FAIL**：每个WASI关闭后仍新增epoll线程，纯C隔离复现并持续10秒 |
| 节点级Reset | PASS：9次实际Manager入口，覆盖空闲、连续和compute/buyNow在途 |
| Reset后继续执行及排队 | PASS（已覆盖请求）：14笔新业务查到提交；buyNow真实六下游 |
| Stop/Reset竞态与退出 | 最小修正后PASS于已覆盖顺序；真实重叠Stop/Reset exit0，硬保护保留 |
| 1536MiB下合理余量 | 有限4合约诊断峰值1214.668MiB，但存在持续线程残留，不能据此签发长期/扩大负载准入 |

当前不是“所有Store生命周期都没做完”的泛化阻塞，而是一个明确native/WASI后台线程关闭问题。不能靠增加RSS/线程上限、反复重启、强制GC或复用WASI绕过。

不启动Step36正式Copy E2E；不将本轮观察器耗时当作性能样本。最小下一步是针对固定native构建恢复/回移Selector关闭修复，保持Wasmer版本、ABI、Gas与编译器其他配置不变；先通过Store-only/WASI-only线程对照及10秒静默，再复核节点Reset资源平台。该原生修复本轮未执行。
''')
put('.gitignore','binaries/\n**/*.so\n**/*.test\n**/__pycache__/\n*.pyc\n')
print('reports written')
