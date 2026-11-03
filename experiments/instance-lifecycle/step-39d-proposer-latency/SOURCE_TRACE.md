# 源码调用链与证据等级

基线CVW ee87355b、节点8ff98d6。Sync V2实际依赖 `chainmaker.org/chainmaker/sync/v2@v2.4.0`，不是仅查看节点仓库中的旧Sync V1。下面路径按本机实际编译源列出；完整行号原文与SHA256保存在evidence/source-excerpts.json。原39C的SDK提交路径说明保持有效，未修改其文件。

## 源码索引

| 环节 | 实际文件及行号 | 直接证明的行为 |
|---|---|---|
| 选用Sync V2 | `/home/frankie/mygitprojects/.worktrees/node-step39d/module/sync/sync_server_aggregation.go:337–369` | 链版本2040000走V2；:86–94的适配器实际调用BlockSyncService.Start |
| 初始化注册订阅 | `/home/frankie/go/pkg/mod/chainmaker.org/chainmaker/sync/v2@v2.4.0/provider/provide_server.go:26–48` | 构造期注册BlockInfo；notifyFuncList先RuleManager.NotifyNewBlock、后notifier.Notify |
| 通道容量 | 同module的 `types/watcher.go:13–14`；`rule/manager/rule_manager.go:49–58` | DefaultChanCap=3，newBlockC按此容量创建 |
| 消费者何时启动 | `rule/manager/rule_manager.go:84–98,107–113` | Start之后go watchNewBlock；NotifyNewBlock直接channel发送，不丢弃 |
| Sync启动顺序 | `block_sync_service.go:139–163` | 先nodeRegistry.Start，再provider.Start |
| 固定启动等待 | `noderegistry/registry.go:99–115` | 先启动发现/心跳，再time.Sleep(2*time.Second)，随后才返回 |
| Provider启动 | `provider/provide_server.go:87–99` | 调用ruleManager.Start，启动消费者 |
| PublishSafe | `/home/frankie/go/pkg/mod/chainmaker.org/chainmaker/common/v2@v2.4.0/msgbus/message_bus.go:171–180,214–255` | safeMessageC单个消费循环；notify按订阅顺序同步调用sub.OnMessage |
| 单验证节点例外 | `consensus_tbft_impl.go:398–401` | 只有一个本地验证节点时跳过ListenSyncToIdealHeight等待；不能以首次TBFT可提案代替Sync启动完成 |
| 异步启动链 | `node-step39d/module/blockchain/chainmaker_server.go:450–460` | go startBlockchain(chain)，不以RPC监听成功证明chain.Start已返回 |
| 节点模块启动 | `/home/frankie/mygitprojects/.worktrees/node-step39d/module/blockchain/blockchain_start.go:28–55` | 先Core/Consensus/TxPool，再Sync；Start尚未返回时Consensus已可提案 |
| SDK区块订阅在前 | `module/blockchain/blockchain_init.go:66,114,855–862`；`module/subscriber/subscriber.go:23–25` | initSubscriber早于initSync；OnMessage另启goroutine向blockFeed送事件。因此后面的Rule订阅阻塞不阻止已投递SDK事件 |
| TBFT订阅时机 | `/home/frankie/mygitprojects/.worktrees/cvw-step17/chainmaker/chainmaker-vm-wasmer/consensus-tbft/v2@v2.4.0/consensus_tbft_impl.go:394–429` | Consensus.Start才注册topics，晚于初始化期Rule订阅 |
| TBFT高度推进 | 同文件:551–567、1007–1021、1691–1799、1830–1846 | BlockInfo→blockHeightC→handleBlockHeight→enterNewHeight→enterPropose→sendProposeState(true) |
| 提案状态总线 | 同文件:439–442 | sendProposeState通过同一PublishSafe发送 |
| Core应用状态 | `node-step39d/module/core/syncmode/core_syncmode_impl.go:171–174` | 先更新proposer状态，再记录proposer_ready事件；事件是状态应用端，不是TBFT发送端时间 |
| 提案门控 | `module/core/syncmode/proposer/block_proposer_impl.go:216–233,440–459,620–638` | 非proposer跳过timer/TxPoolSignal；false停止timer，恢复true重置timer |
| 定时周期 | 同文件:561–571 | 取链配置BlockInterval×毫秒；本轮20ms，不是2秒 |

## 实际堵塞调用链

```text
PutBlock完成
  → PublishSafe(BlockInfo)
  → msgbus safe消费循环 → notify同步遍历订阅者
      → EventSubscriber：异步推送SDK区块结果（已投递）
      → Sync V2 messageBusSubscriber.OnMessage
          → RuleManager.NotifyNewBlock
              → newBlockC <- block  【实际栈：chan send】
      → TBFT.OnMessage(BlockInfo)   【此时尚不能轮到】

另一启动goroutine：Blockchain.Start
  → ServerAggregator.Start → BlockSyncServiceV2.Start
  → BlockSyncService.Start → Registry.Start
      → time.Sleep(2s)              【实际栈：sleep】
  → Provider.Start → RuleManager.Start → watchNewBlock（睡眠后才启动）
```

消费者启动后排空channel，总线线程解除发送阻塞，TBFT得到高度消息，Core重新应用true并恢复提案。这里的“发送阻塞发生在高度5”根据完整已提交事件、高度序列和容量3推导；goroutine栈没有直接打印block参数内容或运行时channel长度，不冒充直接读出了这些字段。

## 直接观测与推导分界

| 结论 | 证据等级 | 证据位置 |
|---|---|---|
| 历史24笔全在第5笔/高度6 | 原始逐笔观测 | TIMELINE.csv；原39C收据/VM/PutBlock日志 |
| 历史恢复在首次ready后约2s | 同进程单调时间观测 | TIMELINE.csv、evidence/proposer-events.jsonl |
| msgbus线程阻塞于规则通知发送 | 两次诊断直接栈证据 | evidence/window8-selected-stacks.txt、window12-prelude2-selected-stacks.txt；完整栈在raw_logs/*-node.log |
| 同时Registry仍在启动Sleep | 两次诊断直接栈证据 | 同上；栈中的Sleep=0x77359400ns=2s，来源registry.go:114 |
| 同时TBFT主循环等待事件 | 两次诊断直接栈证据 | 同上；handle select而非耗时Guest或共识运算 |
| 容量3、消费者在Sleep后启动 | 源码直接证明 | watcher.go、rule_manager.go、block_sync_service.go、registry.go |
| 第四块通知阻塞，下一笔无法进VM | 源码控制流+计数/状态观测推导 | 上述调用链、各run的height2/3/4/5/6及ready序列 |
| 不是正式序号本身 | 受控序号移动验证 | DIAGNOSTIC_TIMELINE.csv：窗口前两笔后，慢笔5→3、高度仍6 |
| 历史24笔均由同一调用栈造成 | 机制归因得到强支持，但非逐笔抓栈 | 历史模式完全一致，新增两栈吻合；不能称历史每笔都有栈证据 |
| 精确修复后TPS提升多少 | 未验证 | 本轮没有功能修复版或新优化性能对照 |

## 未记录与不能推出的内容

历史未记录交易池即时库存、每次AddTx完成时间、TBFT round/height消息入队和处理时间、RuleManager channel实时长度。TIMELINE.csv明确填not_recorded。诊断时SDK处理栈在等待交易结果，加上成功提交与后续同TxID执行，可证请求已经过AddTx进入结果等待；不据此虚构队列长度。

旧时间戳客户端和节点各有单调原点，只在各进程内作差。SDK/节点wall_ns保留以关联事件，不直接相减当作网络耗时。VM Owner入口与Factory不是相同边界，Factory SHA部分可先于Owner入口，二者不能简单相加。所有原始失败/慢样本仍保留。

本轮诊断唯一节点改动为SendRequestSync的300ms并行watchdog，抓runtime.Stack；无共识参数、消息队列、VM Owner、Gas、Guest、日志级别修改。原生产节点及旧Step39C二进制/源码未覆盖。该栈观测会扰动耗时，所以DIAGNOSTIC_WINDOWS仅用于机制与位置验证，不加入原360笔的效果统计。
