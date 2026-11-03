# 三个热路径审计

实际Factory依赖不是就近目录推断，而是GOWORK + go list -m恢复：
`/home/frankie/mygitprojects/.worktrees/cvw-step21c/chainmaker/chainmaker-vm-wasmer/vm/v2@v2.4.0/vm_factory.go`。
其393–394行先调用NewRuntimeInstance；432–436行才开始/结束Runtime.Invoke计时，438行输出REUSE_VM。Factory不直接Clone，Clone由Manager.runtime执行。

| 原始操作 | Step-38原始位置（source/A/vm） | 输入/用途/输出 | 本轮可缓存部分/失效 |
|---|---|---|---|
| Runtime Clone | step35_node.go:91–95 runtime；vm_instances_manager.go:56–66转入safe.runtime | append(nil,raw...)，每Runtime快照，阻止调用方随后修改影响预期身份。克隆不是每次编译 | 管理器拥有的私有字节可复用；初次登记仍Clone。内容/版本/链/配置变化重新登记 |
| Invoke SHA×2 | step35_node.go:185–191 Invoke | nodeSHA(raw)与nodeSHA(r.raw)；不相等拒绝，防止Runtime与实际输入错配 | 保留输入SHA，缓存内部快照SHA；不能只比较名称/版本就接受内容 |
| Prepare SHA | step35_node.go:126–137 prepare | SHA(raw)进入chain/name/version/digest/config/copy键，每次命中也先计算 | 通过已校验的Runtime Artifact摘要复用键身份；版本、内容、配置变化产生其他键 |

Step-38冷prepare:177 source=nodeSHA(raw)还有一次SHA，仅在缓存未命中；prepareStaticMemory:97还算SourceSHA，232构建短身份Key，restore:237每次验证该短Key。它们不等于三次热路径全WASM SHA。原native ValidateModule/NewModule冷验证保留。新B/D冷source复用已确定摘要；A/C保留冷source SHA。没有修改Copy模板、Ranges或restore。

## 新原型调用链

vm_factory.NewRuntimeInstance → InstancesManager.NewRuntimeInstance → nodeFreshManager.runtime → B/C/D的e39Registry.acquire → nodeFreshRuntime.Invoke（输入SHA仍存在） → SafeFreshOwner.Do → invoke → prepare（B/D复用摘要） → 同Engine缓存Module → 真独立Store + WASI/Imports → NewInstanceInStore → C0 restore → Initialize → _start → CallMethod → 同步Close。

新主源码准确位置：step35_node.go runtime:97，prepare:136，Invoke:198；step39_artifact.go acquire:50，hash:44；测试位置见audit/SOURCE_FUNCTIONS.csv。修改全部限制在本实验source目录。

## 不可变性的证据与边界

acquire对外部字节只读，以tuple(chain,config,name,version)取候选；命中仍bytes.Equal完整内容。首次/内容变化时append拥有字节再计算其SHA，将*e39Artifact发布到受mutex保护的map。raw/digest不导出，后续没有写入它们的代码；不同Runtime只读取。旧快照不在升级时就地修改。上游c.Contract按值复制，实际身份只用Name/Version。C/D引用内部owned字节；B仍每次Clone，但digest来自已逐字节核对的内部快照。

B/C/D完成输入摘要校验后，Owner使用Runtime私有快照，避免校验后再依赖外部可变切片。仍要求调用者在acquire/Invoke读取期间不并发写输入；原Clone/SHA也有同样要求。**没有证明外部字节天然不可变，因此不做直接外部零拷贝。**

本地GetContractBytecode在step21d_fixture_test.go:80–86自身还有append；保留。根f.run:266取码发生在RunContract计时前，子调用取码则在根export内。本轮消除的是Runtime再次Clone，绝不是所有源字节复制。

原Go NewModule:76–106把只读输入传C桥；native `/home/frankie/mygitprojects/.worktrees/native-step35b/lib/c-api/src/wasm_c_api/module.rs:28–37` wasm_module_new通过bytes.as_slice()调用Module::from_binary。prepareStaticMemory创建新NoData和Image，没有写入source。本轮不改这些实现。

## 缓存身份和失效

Artifact identity=tuple + 实际内容；digest是私有内容的SHA。Module identity仍是原完整key，含内容摘要、运行配置、Copy开关；缓存record.source也绑定摘要。模板还验证实际Module指针与Key。不要将Go Artifact可共享误认为native Store/Imports可共享。

内容变化（包括同Version变内容）替换该tuple的Artifact引用；已有Runtime保持旧快照，旧Module按旧digest区分，不复用错版本。版本/链/配置变化为另一tuple。Copy开关是Manager生命周期固定属性，不改变原WASM，因此不用Copy把Artifact原字节重复存一份。Module继续区分Copy配置。

本轮registry上限8个tuple，Module上限仍8；升级旧内容保留的Module达到原限会返回显式错误，而非无限增长。Reset清native Module，Go Artifact可保留、再次核对内容后重用；Module实际重编译测试通过。新tuple超过registry容量仍会拒绝，即使之前Reset过；生产集成前需要定义缓存淘汰/Reset清理策略和验证。Stop不显式清空pure-Go registry，由Manager引用生命周期/Go GC回收；这不是已完成长期缓存治理的生产实现。

## 观察窗口

原Factory、Owner、Close窗口保持；SHA/Clone阶段用短time.Now及小结构记录，结束后统一输出。runtime_create包含Artifact acquire、可能Clone、对象构建，artifact_acquire包含冷Clone/SHA和锁等待/比较，prepare_total包含key、命中及既有日志。不能重复加总。cold_cost不进入正式热态主统计。

主A/B/C/D都使用同一二进制，平衡顺序。stage count/bytes指记录到的全WASM操作，不包括短Template Key、TxID及业务Guest里的SHA。Go分配是外层f.run envelope的进程Go allocator增量，含收据/JSON/其他工作，不是纯VM或者native分配。

lean单独删除Step-39成本插桩，保留所有校验、原日志及生命周期；源码差异audit/lean.diff，使用相同输入另做3批配对。它验证方向而不是从主结果中减去一个插桩中位数；不能证明所有观察扰动均为零。
