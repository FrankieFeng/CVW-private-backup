# Step-31安全准入决定：NOT_PASSED，Step-32不启动

本轮最终归类 **C：实验仍被阻塞**。本文件形成时未启动任何ChainMaker节点、SDK客户端或E2E请求。两个既有有界协议检查通过，不等于真实节点全生命周期通过；本轮不再扩大动态检查或临时修改VM。

## 本轮实际验证

沿用Step29保存的测试binary SHA `940ccc3adf6e4d03be01ee40c36fcb17861eb4517546d53c6da86aad41716f91`，原native库SHA `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。没有编译/改VM/Gas/业务，完整环境与命令在raw_logs/*-command.json。

| 检查 | 实际执行 | 结果 | 适用范围 |
|---|---|---|---|
| cached Module串行fresh | TestStep22ModuleLifecycle，一个独立进程，3个小WAT Instance | 新Memory首字节均0，改一实例后下一新实例不继承；每次函数返回42，清理登记回到基线，末尾0 | 无WASI/真实Go业务的有界wrapper/Module协议 |
| 非owner拒绝 | TestStep21DOwnerFailure里的另一goroutine只调用ManagedAssert | native操作前被拒绝；未让错误线程触碰C对象 | 测试管理器owner检查 |
| 创建失败回滚 | 同一检查真实加载非法字节码 | 返回预期错误，登记回到0 | 有界创建失败路径 |
| 关闭失败继续回收 | 真实WASI小模块缺deallocate | 保留错误，仍显式scope清理，created=closed=1，在途0 | 单次WASI错误关闭路径 |
| GC与退出 | owner线程关闭scope、执行测试末尾GC、ManagedEndOwner，外部检查PID/cgroup | 两个有效进程均正常退出、managed/pending0 | 进程终结后的有界退出，非长寿命native join证明 |

初始配置错误单独保留：首次遗漏CM_REUSE_EXPERIMENT，在package init被显式配置守卫拒绝，测试体未进入。没有把此失败删掉或计为成功。只补齐R1/capacity/守卫=1后另命名重试，保持owner、native、资源保护；原STOP.json及失败日志不变。详见audit/configuration-correction.json。

资源：两个有效检查采样+边界峰RSS分别51108/53980KiB（约49.91/52.71MiB），线程6/23；没有触发资源保护。原限为768MiB/125线程软限，本轮hard更严格为1GiB/128tasks，20s Go timeout/30s process watchdog，5s停止；未提高阈值。Go heap未由复用的probe采集，标missing。初始配置失败峰42368KiB/5线程另列。非E2E样本不得用作Copy性能值。

## 真实节点必须覆盖但尚未验证

| 必要条件 | 当前源码事实 | 门槛 |
|---|---|---|
| Store/Module创建在固定owner上 | 旧InstancesManager.NewRuntimeInstance→getVmPool先准备Store/Module；Runtime.Invoke内根锁较晚 | 未满足节点owner路由 |
| 执行、Memory、Gas、host callback、析构均同owner | 测试managed.go可断言，但旧node绑定仍用Go native Finalizer | 未满足节点全入口覆盖 |
| Finalizer不与native调用重叠 | 旧Store/Function/Memory/Exports/WASI仍注册native Finalizer，根锁不约束其goroutine | 未满足，不声称本轮复现race |
| 正常停止拒新任务、排空在途并回收缓存 | 节点Blockchain.stopVM→VmManager.Stop→InstancesManager.StopVM；末端是空实现 | 未满足节点排空/join |
| Reset/Close和异常清理同owner | 旧CloseAllVmPool持map锁调用pool.close；pool.close只close channel，pool.reset发送channel，无owner/in-flight排空协议 | 未验证；Fresh模式还不启动原refresh loop，不可靠该loop推导完成清理 |
| WASI与native资源在节点长寿命中有界 | Step22/28/29的许可依赖每Store/进程预算与最终进程退出；旧20 RSS增长约1GiB并触限 | 未满足长寿命资源准入；不等于断言20对必然超限 |
| 真实SDK业务/写集/事件/提交/回滚 | 目前只能用历史证据，节点新协议尚不存在 | 本轮not_tested |

## 有限候选及停止理由

1. **继续旧根锁或加全局锁**：不能覆盖锁前Module/Store准备、Finalizer及Reset/Stop，不采用。
2. **直接复制managed.go**：managedOwner/current/entries是进程级单owner状态；旧节点任意请求goroutine、模块创建、回调与关闭没有完整进入scope的入口。仅替换Finalizer会触发owner/outside-scope守卫或遗留缓存对象；不能通过关闭守卫修复，不采用。
3. **直接复用dManager/dRuntime**：源码属于_test管理器，依赖testing.T、s21cFixture.nextID/calls/真实测试账本及外部进程终结；不是现成node VmInstancesManager。将其名字换进node不能解决生命周期，不采用。
4. **固定owner节点适配**：方向可行，但至少需连接StartVM/准备/Invoke/嵌套callback/Reset/Stop、保证Module metadata与WASI scope归属，并验证队列在途/退出与资源。现有分支未找到已完成的该适配，也没有真实节点验证记录。不能将测试末尾进程退出当成节点每请求的回收完成。本轮没有可直接复用、已经满足这些条件的最小补丁，停止在此；**不是证明未来无法实现**。

## 本轮变更与准入结论

实际变更只有独立目录的审计、受限probe运行/复算脚本和记录。VM/Go绑定/SDK/节点/Gas/业务代码改动0；没有新锁、后台worker、复用Instance、强制每请求GC、WASI跨Store复用或阈值抬升。

**不准许进入Step-32。** 第一轮10对未启动，第二轮未启动，新增E2E配对0。按任务要求，门槛失败后不继续改VM、不发送请求；不把未执行写成Copy负收益。最小后续工作只保留：一个明确所有者且可排空退出的实验节点适配 + 同阈值下native/WASI回收与业务/提交预检。无需继续WASM clone内部机制、A/B1、COW、原池并发或无限扩样。

## 守卫观察范围补充

本轮异线程测试只调用ManagedAssert，因此只证明该断言能拒绝非owner；没有让错误线程调用所有Memory/Module/Store C入口，也没有证明每一个wrapper都会在触碰native之前自动检查owner。现有安全性依赖整个调用链被所有者路由，不是靠单条断言就覆盖所有入口。managedCallDepth的在途Close拒绝在源码中存在，但本轮未专门触发该场景，标未复验；退出正常也不证明native内部无残留。当前so精确构建链仍只有hash/6.0.1版本/候选源码等有限证据，不因probe通过扩大为正式native线程安全认证。
