# Step-35C：节点异步任务排空与Reset/Stop修复

**已定位Common写入模式下的Close竞态并实现实验修复。冻结候选完成8种节点生命周期场景、3次同账本重启核对，均exit0；可以准备限定条件的Step-36小规模同步客户端验证。** 不代表四节点、高并发、异步提交、Quick写入或生产安全认证。

直接缺口：Core接收CommitBlock后另起AddBlock goroutine，旧Core.Stop只停止提案循环；旧账本Close没有等待CommonPutBlock在途调用。WriteKvDb的局部WaitGroup只保护单次PutBlock内部子任务，不能阻止另一个goroutine提前Close数据库。

纯观测版在区块46的DB写入窗口暂停既有任务，再触发Stop，实测Core停止→DB Close开始→写入恢复→`leveldb: closed`、exit2。此任务配置是`write_block_type=0`，未走快速写队列，不能把它归因于队列消费者积压。历史35B为HistoryDB子任务，本轮观测为StateDB子任务，属于同一父写入生命周期缺口。

最终原型加入HTTP请求接纳/排空、提案worker与Core提交/验证任务排空、账本PutBlock租约和WAL清理等待、归档循环/压缩等待、显式诊断服务退出。VM Owner沿用Step34/35所有权协议，Stop增加10秒错误传播；模块停止错误会中止关闭流程，避免继续关闭仍在使用的DB。

| 场景 | 退出码 | Store创建/关闭 | Instance创建/关闭 | 峰值RSS MiB | 峰值线程 |
|---|---:|---:|---:|---:|---:|
| 在途buyNow Stop | 0 | 10/10 | 7/7 | 1006.74 | 42 |
| 在途compute+Reset+Stop | 0 | 2/2 | 1/1 | 704.55 | 24 |
| 空闲Stop | 0 | 0/0 | 0/0 | 396.54 | 9 |
| 正常业务后Stop | 0 | 20/20 | 16/16 | 1153.46 | 45 |
| Reset后compute+buyNow | 0 | 14/14 | 9/9 | 1173.84 | 45 |
| 空闲Manager Reset两次 | 0 | 0/0 | 0/0 | 481.84 | 8 |
| Reset清理中Stop | 0 | 0/0 | 0/0 | 475.44 | 9 |
| 已进入DB写入窗口时Stop | 0 | 2/2 | 1/1 | 630.71 | 25 |


冻结矩阵合计Store48/48、Instance34/34；随后3次重启检查Store10/10、Instance7/7。所有计数均来自各进程原始日志，不把不同候选的样本合并。相关Core/PutBlock/DB-write/WAL计数配平，归档及诊断线程有退出事件，进程/cgroup全部结束。最高RSS1173.84MiB、线程45，未提高1536MiB软限制。

- 真实compute和buyNow结果、Gas、事件及规范化提交读写集与35B同WASM/同输入对照一致。
- buyNow完整6次真实子调用；重启后3笔在途交易可查，返回/Gas一致；重复buyNow失败、写集为空、NFT所有者不变。
- native一直为35B补丁SHA `56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc`。未改Selector、Gas、Guest、A/Copy。
- 节点源码提交`0ce8fba61761f0ced5fb598ab28727080706577a`；CVW独立分支`experiment/step35c-node-shutdown-drain`，基线`a9910fb7`。候选二进制SHA `c07aeffc171be1c3da8d8b4a69c74d19ef7008cf0253b78f916887b5cf47cc77`。

阅读顺序：NODE_SHUTDOWN_CALLCHAIN.md → LEVELDB_WRITE_ANALYSIS.md → SHUTDOWN_PROTOCOL.md → CORRECTNESS.md → SAFETY_GATE.md。原始失败也完整保留：观测版DB竞态、fixed3不支持的grpc GracefulStop、fixed4诊断socket残留。未把这些失败记为通过。

复算：`python3 scripts/analyze.py`，只读raw_logs并生成派生CSV/JSON。所有启动argv/环境/二进制hash在`raw_logs/*-command.json`，构建在`audit/*-command.json`。动态回归脚本为`regress.py`、`restart_check.py`；候选已冻结，本轮不再启动实验。二进制在独立worktree的ignored binaries/，报告镜像不含so/私钥。未覆盖35B或生产基线，未推送远程。
