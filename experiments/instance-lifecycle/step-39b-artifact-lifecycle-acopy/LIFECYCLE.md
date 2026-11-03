# Manager范围缓存生命周期验证

## 唯一治理策略

Manager内8项/64MiB有界缓存，满即明确拒绝；无LRU、无后台淘汰、无native共享新机制。registry key为(chain,config,name,version)，命中仍bytes.Equal；首次/换内容owned Clone+SHA，不直接共享外部切片。Artifact本身仅key/raw/digest。Module仍按原含内容SHA/配置/Copy的完整键缓存，原Module8项限制保持。

正常Runtime创建沿InstancesManager.NewRuntimeInstance→safe.runtime。外部调用在原Owner.mu下核对closing/resetting/poisoned/原请求预算并完成Go登记/Clone；不改Owner实现。同Owner回调允许已接收根调用继续创建子Runtime，Stop排空前registry保持可用。Owner.Reset/Stop既有排空后调用clear，原native清理完成后detach registry：Reset清空并允许下次登记，Stop清空且closed永久置位。外部Go登记与生命周期状态变更使用同一Owner admission互斥，避免Stop清理后再登记。

prepare失败时discard只移除“该key仍指向该Artifact”的条目；旧失败Runtime不能误删后来替换的新内容。原native scope defer回滚仍负责native对象；Artifact不保存native引用。失败的输入/编译不会永久占用新的registry槽位，已有Module缓存不会因Artifact删除而被在途关闭。

## 场景及实际证据

| 场景 | 实测/源码证据 | 结论及边界 |
|---|---|---|
| 首次/命中 | TestStep39BRegistry；diag-{case}-G1/G3缓存事件 | 命中保留原快照，热调用无冷Clone/SHA |
| 合约/版本/链/配置 | TestStep39Artifact新二进制再次执行，另-race执行 | tuple隔离、不同内容摘要可核对；不是node多链运行测试 |
| 版本升级 | TestStep39BUpgrade，真实compute.hashCal metadata version变2.0.0 | 实际新Module及真实Guest执行；非SDK上链部署升级 |
| 同版换码 | 同测试将plain替换为既有同源A WASM | native缓存新增不同内容键，执行成功，原Module未错命中 |
| Manager Reset | 上述测试通过ResetAllPool→tracked35aReset→safe.reset | Go及native缓存清空，新Module/Store重建 |
| Stop与可回收 | Supplement UpgradeWeak，Manager仍KeepAlive | Stop新建/旧Invoke拒绝；弱引用自然GC释放，原始记录GC2次/约28MiB有界分配压力，未强制GC |
| 8项容量 | Registry第9个tuple拒绝；Reset后可登记 | 无自动淘汰；已有对象不受拒绝影响 |
| 64MiB预算 | TestStep39BByteBudget，两个32MiB条目后第三条拒绝；另验证单个超64MiB直接拒绝 | 计数8/字节64MiB双界；拒绝前不创建新的owned Clone |
| 旧Runtime与替换/清理 | TestStep39BPinnedLifetime：Owner job已接收并暂停，主线程登记同版新内容，然后旧请求执行；Reset后再执行保留Runtime | 老快照保持有效、新实例仍Fresh；这里“清理”是显式Reset，没有虚构LRU淘汰 |
| 并发只读 | Registry8读者各20次创建不同Runtime；-race通过 | 只证明Go registry/不同Runtime只读，不证明同一Runtime并发Invoke或native并发 |
| 失败回滚 | invalid-WASM及diag after_compile Go故障，随后恢复真实调用 | 错误没有吞掉；Artifact删除及native scope回滚，最终计数配平 |
| Reset+Stop | TestStep39BResetStop，真实Owner已接收job，Reset拒绝新Runtime、Stop等待；已接收job执行真实hashCal | 原日志顺序显示Stop requested在Reset完成前，无Sleep；幂等Stop成功 |
| Stop中的真实跨合约 | TestStep39BDrainBuyNow：Stop置closing后才释放已接收root job，完整6子调用执行 | 外部新Runtime拒绝，已接收业务成功，结果/RWSet/事件/账本与正常预检逐字相等 |

以上原始生命周期check字段在LIFECYCLE_CHECKS.csv；新并发读及独立Race日志分开保存。角色为Manager/Owner的VM测试，不称为真实节点生命周期认证。

## 内存和所有权

8项/64MiB是registry raw的强引用上界，不是包括调用方/Runtime/natives的进程总上界。替换时旧快照可能被旧Runtime合法持有，Go引用保活避免悬空；B仍每Runtime持有独立Clone。新旧快照瞬时并存和在途请求需由既有请求预算/1536MiB守卫限制，不把缓存字节限制说成全局内存预算。

Reset/Stop解除registry引用，不在Go调用方仍合法持有时强行清零raw；这会破坏旧请求。Artifact无Store/Module/Instance/WASI字段，不关闭native对象。Native关闭仍只经原Owner作用域/Finalizer协议；本轮没有重写或绕过它。

自然GC验证只作功能诊断，分配压力在独立进程中有界，未参与性能数据，没有调用runtime.GC/FreeOSMemory、Sleep或更改GC参数。它证明可回收性，不能证明RSS立刻回落或长时间无泄漏。

源码准确文件/行号见audit/SOURCE_FUNCTIONS.csv，代码差异audit/runtime.patch。Owner、编译器、Copy及wasmer-go生命周期文件SHA与39A完全一致。保留原Owner总请求上限32及原native缓存8项；达到上限需结束隔离批次/显式Reset相应缓存，不能擅自扩大守卫。Owner总调用预算不能通过Reset刷新。
