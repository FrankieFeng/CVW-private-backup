# Step-35B 详细说明：修复了什么、为什么停下、是否与模型额度有关

本报告只复核已经保存的日志和数据；没有新启动实验，没有修改VM、native补丁或原始记录。

## 1. 先回答“是不是模型没有额度导致的”

**现有证据不能证明当时模型额度耗尽。可以确定，最后一次节点测试确实因程序错误退出；后续动态测试是按任务中的安全停止规则主动暂停的。**

需要区分三个事件：

| 事件 | 本轮证据 | 能得出什么 |
|---|---|---|
| Codex会话可能断开、暂时没有回复或额度不足 | 实验目录中没有平台侧额度/网络错误记录；本报告没有访问账户额度 | 无法确认或排除另有会话层问题，不能把它写成实验失败原因 |
| 被测试的ChainMaker节点退出 | `raw_logs/patched-stop-node.log:21` 有明确Go panic；outcome记录exit2 | 已证实发生节点程序错误，不是只因Codex停止回复而缺数据 |
| 后续重启/回滚/正式E2E未继续 | PROGRESS和STOP.json记录主动停止；启动脚本保留停止守卫 | 是安全决策，不能通过换模型、等额度恢复、删除STOP后续跑来解决程序问题 |

OpenAI官方文档说明，当前额度和重置时间应查看账户的usage dashboard；CLI会话可用`/status`查看剩余额度。文档无法替我们恢复当时的账户状态：https://learn.chatgpt.com/docs/pricing?codex-pricing-plans=individual 。即使当时另外发生过额度中断，也不能解释本地程序日志中的LevelDB panic。

所以，更准确的说法是：**会话是否另有中断未知；本轮最后一个已证实的实验停止原因是节点退出阶段的账本错误。**

## 2. Step-35B原来要解决哪个问题

此前Step-35A发现：反复创建、使用、删除WASI后，后台线程数量还在增长。WASI是合约运行所需的一组宿主环境资源；它内部会准备任务运行时和网络事件处理组件。

需要判断这些线程是正常全局线程，还是每次创建WASI遗留下来的线程。本轮先使用纯C程序，绕开Go的Finalizer、节点共识、业务压力和实例池，单独调用：

```text
创建Engine
  → 创建Store
  → 创建WASI配置和环境
  → 删除WASI环境
  → 删除Store
  → 删除Engine
  → 静默观察线程是否退出
```

静默1/2/3秒仅用于观察析构后的线程状态，不是业务请求之间的100ms Sleep，也没有用于制造性能收益。本轮没有测TPS或Copy端到端性能。

每个线程同时记录创建阶段、pthread创建调用栈、TID、线程名、等待点与EXIT。不是看到“epoll”名称就认定它是哪一类线程。

## 3. 真正发现的native错误

网络事件组件`Selector`在创建后台线程时，给关闭用的唤醒事件注册了`Token(0)`；后台循环却只在收到`Token(1)`时退出。

可以把Token理解为事件编号：发出的关闭通知编号是0，而接收端把1当成关闭通知，编号对不上。

```rust
// 修复前
closer: mio::Waker::new(poll.registry(), Token(0)).unwrap(),
token_close: Token(1),

// 后台循环
if token == engine.token_close {
    return;
}
```

原始so的跟踪还证明：`LocalNetworking`析构已经调用`Selector::shutdown`，也确实向eventfd写入了唤醒。因此不能把原因简单写成“Go没有调用WASI删除”或“缺少shutdown调用”。问题在于唤醒后没有识别为退出事件。

本例中，删除WASI wrapper之后，Store仍可能持有相关环境对象；最后Store释放时才触发网络组件的析构。Selector线程自身又持有Arc引用，错误通知使线程继续等待，从而保留该线程及关联资源。

关键源码是独立native工作树的：

- `lib/virtual-io/src/selector.rs:34`：注册关闭事件Token。
- 同文件`:45`：创建后台线程。
- 同文件`:53`：shutdown发送唤醒。
- 同文件`:153`：退出判断。
- `lib/virtual-net/src/host.rs:57`：LocalNetworking析构调用shutdown。

## 4. 补丁究竟改了多少

只改一行：把唤醒事件注册的`Token(0)`改为`Token(1)`，与现有退出判断一致。

没有修改Store架构、Module缓存、Gas规则、Guest WASM、编译器配置、A或Copy实现，没有杀线程、强制关闭仍在使用的epoll FD，也没有关闭安全守卫。

| 产物 | 版本/哈希 |
|---|---|
| 原始库 | Wasmer6.0.1，SHA256 `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9` |
| 同源未修复重建库 | SHA256 `75dea41cd2d9b7d83a77b54c21fcda756b187305a1a967e5877a0ce370cab07b` |
| 单行补丁库 | SHA256 `56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc` |

重建对照与补丁使用同一源码基线、Rust1.81、Cargo.lock和features。原始so的完整历史构建清单未恢复，不能声称重建库与原始库逐字节相同；因此另外检查了原始库、重建库和补丁库的实际业务Gas与状态一致性。

第一次native构建曾因build.rs不接受自定义输出目录名失败，随后用标准target目录名恢复。这是另一个已解决的构建问题，也不是模型额度问题。详情见PATCH.md。

## 5. 实际跑完了哪些验证

### 5.1 纯C线程对照

| 方案 | 初始线程数 | 删除1个WASI后静默3秒 | 删除4个WASI后静默3秒 | 4个Selector是否均退出 |
|---|---:|---:|---:|---|
| 原始so | 1 | 2 | 5 | 否，4个残留 |
| 未修复重建库 | 1 | 2 | 5 | 否，4个残留 |
| 补丁库 | 1 | 1 | 1 | 是，4个都有EXIT |

这说明在已测路径中，残留线程是逐WASI累积的Selector，不是允许长期存在的固定全局线程。补丁版第1秒观察时已恢复主线程，但本轮没有新增同步join API，不能将采样结果写成任意调度条件下都满足的硬实时退出上界。

### 5.2 安全Fresh原型和节点真实业务

| 检查 | 实际结果 |
|---|---|
| Step-34 Owner协议，未修复/补丁 | 均通过；包括独立Store、缓存Module、关闭和Reset/Stop相关单测 |
| 原型compute.bigNumCal | 原始/重建/补丁Gas均120027，结果与状态一致 |
| 原型exchange.buyNow | 三种库Gas均12612158，六次真实子调用及状态一致 |
| 节点每组2轮，每轮compute+buyNow | 两组各4笔根业务交易成功并取得提交记录；不是3批性能实验 |
| 节点compute Gas | 两组均120135 |
| 节点buyNow Gas | 两组均12620048，六次真实下游调用 |
| 节点空闲/在途Reset | compute与buyNow均通过，Reset期间新请求排队后正常执行 |

原型与真实节点的上下文不同，不把两类Gas直接相减判断回归。节点两组使用同源WASM和等价初始账本，事件及读写集核对时仅规范化TxID/区块高度等交易元数据，原始记录仍保留；没有额外证明两个节点完整账本的原始hash逐字节相同。

### 5.3 节点有限资源记录

| 指标 | 未修复节点 | 补丁节点 |
|---|---:|---:|
| 第1轮后静默线程数 | 19 | 11 |
| 第2轮后静默线程数 | 27 | 11 |
| 此次节点Smoke峰值RSS | 1177.32MiB | 1156.88MiB |
| 正常结束时Store创建/关闭 | 20/20 | 20/20 |
| 正常结束时Instance创建/关闭 | 16/16 | 16/16 |

每轮buyNow有根调用和六个子调用，加compute共8个Instance；两轮共16个，不是只执行4个Instance。额外4个Store用于缓存Module准备。

1536MiB软保护阈值未提高。短期两轮数据支持Selector不再按请求累积，不足以证明长期RSS完全收敛或任意并发安全。节点剩余11个线程还包括Go调度/网络等组件，不能把它们全部称为Selector。

## 6. 最后究竟停在哪里

最后的测试不是普通连续请求，而是一个专门的退出边界测试：

1. 提交真实compute请求。
2. 从日志确认请求已经进入VM。
3. 调用Manager Reset，确认resetting状态。
4. 在请求仍在途且Reset正在等待时，向隔离节点发送SIGTERM，触发Stop。
5. 观察请求、Reset、VM关闭和节点退出能否协调完成。

这段触发逻辑在`scripts/diagnose.py:47`开始，`:59`发送SIGTERM。

实际日志顺序如下：

| 顺序 | 事件 | 证据 |
|---|---|---|
| 1 | compute进入VM，随后开始Reset和Stop | patched-stop-node.log:8、9、11 |
| 2 | compute业务返回code0，Gas120135 | 同文件:14 |
| 3 | Reset完成，在途数为0 | 同文件:17 |
| 4 | VM Owner关闭完成：Store2/2、Instance1/1、pending0 | 同文件:19 |
| 5 | VM stop_finished，error为nil | 同文件:20 |
| 6 | 账本历史DB写入panic：`leveldb: closed` | 同文件:21 |
| 7 | 节点进程退出码2 | patched-stop-outcome.json |

关键原始错误为：

```text
panic: Error writing db: error writing leveldbprovider key
[historySavepointKey]: leveldb: closed
HistoryKvDB.writeBatch
HistoryKvDB.CommitBlock
BlockStoreImpl.putBlock2DB
BlockStoreImpl.WriteKvDb.func3
```

这里的`chainmaker/store/v2`是**链上账本数据库组件**，与Wasmer的`Store`不是同一个概念。

能够直接确定的是：VM关闭记录已经完成，之后仍有账本历史DB写入碰到了已关闭的LevelDB。尚未完整定位整个节点哪个排空/关闭关系有缺口，不能直接把某一个WaitGroup或某一函数认定为根因。

未修复组相同边界测试此次exit0，补丁组exit2。只有各一次边界样本，不能证明“Token补丁导致账本panic”；它也可能与停止时序有关。目前应同时保留两种结果，不忽略不利样本，也不强行归因。

两组Stop测试的客户端均丢失了RPC响应，因此VM业务code0也不能自动解释为该笔交易已经确认提交。

## 7. 为什么不继续把剩下的数据跑完

用户原任务明确要求：出现节点异常就停止并保留现场，不无限扩大修复范围。本轮已经完成一种native修复和一组前后对照；继续修整个ChainMaker账本停止协议会超出原任务。

因此补丁组后续重启/异常回滚未执行，标为not_tested。未修复组的重启和重复buyNow失败回滚在异常结果返回前已经独立启动并完成，保留其数据，但不能把它填成补丁组也通过。

此次失败节点峰值RSS为668.48MiB、25线程，分别低于1536MiB和220线程软保护线。已证实退出原因是panic，不是本次记录中的内存/线程保护触发；不能据此推断之前每一次WSL异常的原因。

原进程已退出，cgroup为空，相关RPC端口没有遗留节点监听。原生产库和生产VM未替换。继续实验的阻碍不是等待模型额度，而是需要单独验证节点停止时的账本写入排空。

## 8. 当前可以如何表述研究结果

可以写：

> 在Wasmer6.0.1已恢复源码中发现Selector关闭事件Token不匹配。单行修复后，纯C逐WASI累积线程消失，受控节点compute和真实buyNow执行、Gas及状态检查保持一致。

需要同时写：

> 在途Reset与Stop重叠验证中，观测到VM资源关闭后账本HistoryDB写已关闭LevelDB的节点panic。该问题尚未定位，与native补丁的因果关系尚未证实，因此真实客户端E2E最终准入仍未完成。

不能写：Copy端到端收益已确认、所有生命周期问题均解决、补丁已通过生产认证，或者实验因为模型额度而没有实际执行。

## 9. 最小后续工作

只需另开一个范围明确的节点停止诊断：确认停止接纳请求、等待VM调用结束、等待区块/账本写入结束、关闭数据库的先后关系。修复并验证该路径后，再补补丁组重启与异常回滚，最后决定是否开始有限客户端E2E。

不需要重跑本轮已通过的纯C线程矩阵，不需要重新研究A/Copy/Gas，不应删掉STOP后直接跑大规模实验。

证据索引：`ROOT_CAUSE.md`、`PATCH.md`、`CORRECTNESS.md`、`THREAD_BEFORE_AFTER.csv`、`RESOURCE_SUMMARY.csv`、`raw_logs/patched-stop-node.log`、`raw_logs/patched-stop-outcome.json`。本轮结果提交为473bf027，交接守卫提交为a46a8058，native补丁为24b6afd79。
