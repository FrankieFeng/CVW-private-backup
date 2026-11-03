# 全链就绪屏障：条件、源码和事件顺序

这是单链隔离节点的实验Harness协议，不会阻止其他客户端绕过协议提前发送SDK请求，不是生产就绪API。E0/E3使用同一节点二进制、同一屏障和相同请求流程。原2秒发现等待、channel容量3、共识参数、业务消息发布/接收和安全Fresh Owner未改。

## 1. 为什么不能复用旧readyC

节点`module/blockchain/chainmaker_server.go:450–464`异步`go startBlockchain(chain)`后关闭server.readyC；单验证节点TBFT又会跳过同步到理想高度的等待。RPC可连接/首次proposer_ready只能表明部分模块已工作。Step-39D原24笔和两次抓栈/序号移动证据继续只读引用，不重新触发旧故障。

## 2. 实际实现

以下节点路径以`/home/frankie/mygitprojects/.worktrees/node-step39e/`为根；依赖实验源码在本目录source/。关键完整源码及diff归档在evidence/。

| 条件/操作 | 文件、函数、位置 | 验证的含义 |
|---|---|---|
| 开始观测 | `module/blockchain/blockchain_start.go:14–15` | 建立0600 Unix诊断socket，记录本链Start开始；不改变模块启动顺序 |
| Core/Consensus启动调用完成 | 同文件:62 | 原start函数成功返回后才置对应标志 |
| 整链启动完成 | 同文件:67 | 原模块启动循环全部成功结束后置chain_started |
| Registry实际返回 | `source/sync/block_sync_service.go:154` | 在原nodeRegistry.Start返回成功后、调用Provider前记录；原Registry源码未改 |
| Provider实际返回 | 同文件:159 | 原Provider.Start成功返回后记录 |
| Sync实际完成 | 同文件:178 | 原s.syncStatus=started之后记录 |
| 规则通知发布 | `source/sync/rule/manager/rule_manager.go:108–110` | 原channel发送前增加Notified并记高度；发送操作本身未改变 |
| 消费者真实运行/完成 | 同文件:114–120；`source/readiness/observer.go:30–33` | 在实际goroutine循环头报告Waiting；处理上一项的全部原代码之后、再次循环时增加Completed；取到下一项后Taken并标active |
| Core提案状态 | `module/core/syncmode/core_syncmode_impl.go`中OnMessage | 原OnReceiveProposeStatusChange完成后观察布尔状态；不改变状态更新或timer |
| 双队列确认 | `module/blockchain/readiness39e.go:38–56` | 注册独立诊断Topic1000039；同原safe队列发送唯一run/chain/id标记，由该队列的订阅回调ACK |
| 有界标记入队 | `source/msgbus/message_bus.go:289` Diagnostic39EFence | 仅增加可选诊断方法，使用同一safeMessageC，select请求context截止；原PublishSafe/notify/Close源码不变 |
| 后探针对应高度完成 | `source/readiness/observer.go:38` AwaitHeight | 不仅要求数量配平，还要求LastCompletedHeight至少为真实探针提交高度 |
| 关闭诊断 | `blockchain_stop.go:15`、`readiness39e.go:62–64` | Stop首先标记closing、使等待返回错误并关闭实验HTTP服务，再继续原Stop协议；不改变VM/Core/Store释放次序 |

### 消费完成判定

`consumer_started && !consumer_active && Notified == Completed`。Waiting在处理上一项后才计完成；正常continue分支也回到同一循环头。仅成功写入channel、或仅执行过消费者go语句，不满足此条件。原规则处理正文、continue/switch/状态更新未变；原range循环只展开为显式接收以放置观测点。

### 为什么双标记不是另一个“等待两秒”

标记走原safeMessageC串行消费队列，ACK证明此前已入队的安全消息订阅回调都已返回。规则回调返回只代表已发送到其channel，故还必须等待规则处理Completed配平。TBFT高度处理本身异步，故另外等待Core真实应用ready=true；随后再做一次队列标记并复查条件。两次ACK只是事件顺序确认，不设置请求间隔或修改提案节奏。

它不声称异步系统此后永远没有新消息，也不把所有类型的后台任务都宣称“全局排空”。所证明的是本次确认点之前的安全队列回调已通过、规则通知已处理、当前提案状态允许业务，且没有已知启动背压尚未解除。

## 3. 全部准入流程

```text
Harness发起隔离节点进程
  → Unix诊断报告各组件完成（未完成时passed=false）
  → 原safe队列标记1 ACK
  → 消费者已运行、通知处理配平、Core ready=true
  → 原safe队列标记2 ACK，并复查条件
  → 组件/队列预检通过（尚不能直接开始正式窗口）
  → SDK提交真实hashCal/inputSize探针，等待同步提交结果
  → GetTxWithRWSet查TxID/高度/结果
  → 再次双标记，要求LastCompletedHeight≥探针高度
  → 保留首次缓存准备/冷调用记录
  → 相同业务的Query预热及窗口前同规则确认
  → 6笔同步SDK正式调用（无Sleep、无窗口内查询或就绪标记）
  → 查回每笔交易并再次确认最新高度已消费
  → 原安全Stop，释放资源并正常退出
```

`/ready`端点明确只返回components_and_safe_queue scope，它不会伪造业务成功。真正的全链业务准入由`scripts/run_case.py:11–13`把真实提交收据和后高度确认组合完成。探针是正式方法、冻结输入、真实Gas和账本执行，未用Mock。两个方法本身不写业务状态；未来状态型方法必须单独设计等价初始状态及探针的真实账本影响。

## 4. 有界性和失败处理

HTTP处理有3秒context，标记入队及ACK/消费等待使用该截止；Harness总准入15秒，进程还有原资源/超时兜底。组件未完成不发送标记；closing、错误、超时均拒绝准入并保留STOP_SHARED和日志，不开始正式窗口。诊断服务先于业务模块Stop关闭，受控Harness不在Stop开始后提交新的就绪请求。内部总线元数据锁只在原注册/关闭短临界区持有；本协议不认证任意外部并发注册/关闭或多链使用。

原RSS1536MiB、线程220、Owner32不变；Root观察及标记不调用native、不占Owner根请求预算。没有通过Reset重置预算；6次实际Reset前后accepted不变。并行/在途Stop协议没有重新设计，继续使用35C原代码。本轮没有专门制造readiness HTTP与Stop并发的测试。

## 5. 验证证据

- `raw_logs/*-preflight-gate.json`保留启动过程中passed=false及最终通过的观察；`*-post-probe-gate.json`保留真实高度及两枚ACK。
- `GATE_EVIDENCE.csv`列出15个业务节点四个边界的阶段标志、run/chain、Notified/Taken/Completed、最后消费高度和fence IDs；原始`STEP39E`节点日志保留阶段事件。
- `VALIDATION_GATE.json`：先有3个独立验证节点全部通过、当时正式窗口为0，再进行12个E0/E3配对节点。
- 单元检查TestIncompleteCallbacksCannotPass覆盖通知仍active/未完成不能通过、Stop后不能通过；不把该单元测试当作真实节点验证。
- `raw_logs/*-case.json`及SDK日志保留全部90笔目标、15笔冷探针、15次Query预热；`*-restart.json`保留24笔正式查回及Reset后继续交易。
- 本轮没有采样删除、强制GC或额外请求Sleep。原monitor的短周期资源/启动轮询发生在Harness管理路径，不是业务请求之间的100ms间隔。

## 6. 构建与恢复

当前Host Go1.25.0，节点go指令保持1.24.0/toolchain1.24.1，Guest沿39C的Go1.24.1同源plain/A padding；native SHA256 `56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc`，C0 Ranges、安全Owner/Selector及Core排空均未改。

Go1.25拒绝对GOMODCACHE文件做overlay，失败日志保留；`source/overlay.json`只是失败尝试记录，不是实际构建参数。有效构建使用`scripts/prepare_common.py`把固定common/v2@v2.4.0复制到独立`.worktrees/cvw-step39e-deps/common`，555个文件逐项核对，只有msgbus诊断方法文件不同。生产目录和模块缓存没有写入。Sync固定版本副本仅两个文件增加观测，原Registry两秒等待和DefaultChanCap=3的源文件SHA保持。observer模块的go指令曾导致go.mod更新提示，已改为与主模块兼容的1.24.0，没有tidy/升级外部依赖；所有失败构建日志保留。

实际成功编译是`evidence/build-node-r2-command.json`，二进制/依赖身份及patch在evidence/。节点go.mod仅本地替换common、sync及新增实验observer模块，VM依赖仍是原39C路径。重建时应使用新隔离目录，不能覆盖本轮二进制/日志。原/tmp账本已不存在，恢复配置时只将开发证书拷到/tmp，未将私钥加入交付。

只读复算：`python3 scripts/analyze.py`、`python3 scripts/report.py`。原实际执行入口为`study.py seeds`、`study.py validate`、`study.py formal`、`restarts.py`；它们只在明确的新实验执行时使用，本轮完成后不自动重跑。
