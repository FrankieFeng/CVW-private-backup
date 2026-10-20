# Step-19：默认实例池 reuse/no_reuse 复现前置冒烟

日期：2026-10-20。**已完成环境审计和有界冒烟，未运行四节点4000笔压测；历史TPS差距尚未复现。**

## 本轮结论与停止原因

- 同一二进制、原始WASM、输入和默认队列逻辑下，R0归还业务实例，R1关闭后后台补池。没有Static Copy、A、PB、同步fresh或根VM串行保护。
- 首轮三合约各部署一次，compute两方法、ERC721 mint、fact save各3次预热+20次采样；补充独立fact目标方法测试。共230笔业务调用均通过TxID查到已提交交易，200条正式冒烟样本，100组同输入结果比较。
- 100组返回值和事件（仅去除事件TxID）相同。ERC721原始写集20组不相同，差异为`latestTxInfo.TxId`；只去除此字段后写集相同，BlockHeight及其余内容保留比较。不得把原始写集标为相等。
- **fact.saveAndFindByFileHash存在18/20组返回Gas不一致**：R0首次使用五个池实例时为1707，后续复用时降为1113；R1始终1707。结果/写集一致不代表执行Gas或Instance语义等价。这里采集的是Runtime通过合约GetGas上报的Gas，native middleware独立计数未采集。
- 三合约进程结束前RSS：R0 1848.7MiB、R1 2232.5MiB；虚拟地址空间分别120.4GiB、690.5GiB，线程峰值均265。R0也持续增长，不能把全部增长归因于fresh创建。空闲5秒未回落，尚未证明稳态或无界泄漏。
- 因资源尚未收敛、历史关键配置不齐及共享Store并发安全未完成验证，按本次停止条件**不扩大四节点压测，不继续exchange**。现有全部实验节点已停止。没有更新依赖、覆盖旧结果或改动生产源码。

## 冒烟VM结果

单位ms；每组N=20、P95为nearest-rank。顺序固定R0后R1，仅单次低负载描述性结果；不报告显著性、配对效应CI或饱和吞吐结论。

| 历史目标方法 | R0 Median / P95 | R1 Median / P95 | Median差 R1−R0 | Median变化 |
|---|---:|---:|---:|---:|
| compute.bigNumCal | 0.350693 / 0.531519 | 0.376022 / 0.419176 | +0.025329 | +7.22% |
| compute.hashCal | 0.289369 / 0.389863 | 0.338673 / 0.391340 | +0.049304 | +17.04% |
| erc721.mint | 0.476882 / 0.628032 | 0.679168 / 0.840730 | +0.202286 | +42.42% |
| fact.saveAndFindByFileHash | 0.413782 / 0.507059 | 0.553275 / 0.666496 | +0.139493 | +33.71% |
| exchange.buyNow | 未测 | 未测 | 缺失 | 缺失 |

fact的Gas不一致使其不能被解读为“严格相同执行成本下的额外开销”。fact.save是额外冒烟负载，结果单列在summary.csv，未拿它替代历史目标方法。该目标方法补测在新的单合约空账本进程执行，不能与前三合约批次的阶段中位数相加。

两组均**没有空队列等待事件**。R1的创建至可用成本主要在后台：三合约合计R0创建18次，R1创建113次；包含每合约1个verification、5个初始grow，以及init/业务调用后的替补。R0业务使用每合约5个固定实例，R1每次取得不同实例。

R1 compute/erc721/fact创建至可用Median分别4.576/4.485/4.629ms，含WASI、imports、NewInstance和_start，不是纯NewInstance。该成本没有逐次串行加入Invoke。日志输出有观测开销，未单独校准。

客户端P50/P95、关闭、创建及资源原始值分别见summary.csv、instance_summary.csv、resources.jsonl/resource_summary.csv；CPU是全进程累计时间及一个逻辑核为100%的平均利用率，包含启动、编译、账本核验和空闲，不能解读为纯交易CPU。

## 历史TPS与当前测量口径

历史数值来自本轮用户提供，未找到对应原始输出、原始WASM哈希和完整四节点配置：

| 方法 | 历史reuse TPS | 历史no_reuse TPS | 历史下降 | 当前R0/R1饱和TPS |
|---|---:|---:|---:|---|
| compute.bigNumCal | 295.8 | 210.4 | 28.87% | 未测 / 未测 |
| compute.hashCal | 769.6 | 277.0 | 64.01% | 未测 / 未测 |
| erc721.mint | 4077.5 | 311.4 | 92.36% | 未测 / 未测 |
| fact.saveAndFindByFileHash | 2959.1 | 380.3 | 87.15% | 未测 / 未测 |
| exchange.buyNow | 881.2 | 57.7 | 93.45% | 未测 / 未测 |

当前使用已有常驻SDK客户端进行同步调用，客户端收到结果后人为等待100ms，目的为检查正确性和资源；不是cmc异步压测。summary中的`observed_successful_commit_rate_tps`仅是这一受控窗口里已核验成功提交数/首个请求至最后结果的墙钟跨度，约7–8笔/秒，**不代表节点容量，不与历史TPS计算下降比例，不使用Invoke耗时倒数**。

发现两份现成cmc二进制：`chainmaker-go/tools/cmc/cmc`及`chainmaker-go.bak/tools/cmc/cmc`（后者文件时间为9月7日）。已保存哈希和Go buildinfo；不能据文件时间判定哪份生成历史数据，未用它们进行正式压测。

当前cmc源码`tools/cmc/parallel/parallel_statistician.go:238`：`TPS=successCount/(endTime-startTime)`，成功计数来自RPC请求结果；`parallel_request.go:88`调用`SendTxRequest(...,false)`，不能默认其成功等价于业务提交成功。`parallel_statistician.go:154`另有节点`CTps=nodeTxTotal/elapsedSeconds`，364行按区块TxCount累加，并不逐笔筛掉业务失败。四节点同链提交记录不能简单求和。**未证实上述哪种口径对应给定历史五个数值**。

## 源码、版本和计时审计

- CVW独立worktree：`/home/frankie/mygitprojects/.worktrees/cvw-step19-reuse`，branch `experiment/step19-reuse-reproduction`，base `c3e8f2c`。先复制当前环境vm_pool/runtime/sim_context/vm_bridge改动；保存在baseline-workspace.patch中，生产工作区原修改未覆盖。
- Node独立worktree：`/home/frankie/mygitprojects/.worktrees/node-step19-reuse`，同名实验branch，base `351b816`。该基线只含本地依赖路径/既有客户端及关闭一处proposer调试日志，不带Step-19客户端追踪补丁。go.mod仅将本地CVW替换路径改到本轮worktree。
- host Go1.25.0、ChainMaker依赖版本不变、packaged Wasmer6.0.1；native SHA `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。WASM不重新构建，使用Step-16保存的original.wasm，完整SHA见contracts.json；compute为历史保存的100轮版本。与王浅秋WASM是否一致未知。
- 复用开关：实验`instance_lifecycle_trace.go:12`捕获`CM_REUSE_EXPERIMENT=R0/R1`，其他值拒绝启动；`vm_pool.go:670`仅修改丢弃条件，R0仍保留原shouldDiscard错误策略。两组用同一个binary、同样观测。
- `vm_instances_manager.go:112`首次grow5；`vm_pool.go:628`GetInstance；`startRefreshingLoop`原队列逻辑保留，shouldGrow/min5/max10/步长5未改。当前环境已有WASI freelist，因此不同于历史可能每次新建WASI线程的版本。
- `vm_factory.go:432–438`沿原有边界读取`RuntimeInstance.Invoke`起止纳秒。包含GetInstance/可能的等待、SetGas、业务及defer归还；不包含前面的NewRuntimeInstance/pool创建、member/参数准备、客户端/RPC/提交。R1异步Close和后台grow不保证在窗口内完成。
- 轻量REUSE_EVENT记录创建至ready、关闭、取实例时间及队列事件；没有Memory哈希或模板。stdout输出锁只保护输出，不保护整个Invoke/Store，不能等同根VM串行保护。
- 没有采集独立`wasm_instance_new`耗时；create是复合窗口。没有开启Copy，也没有模板准备成本。
- 共享Store的后台创建/关闭与业务重叠仍缺native安全证明，Go race不能覆盖所有native风险；本轮未扩大并发来宣称安全。

## 文件与复查

- `requests.jsonl`和`fact-target-smoke/requests.jsonl`：部署、预热、采样、逐笔提交核验的原始SDK响应。
- `network/*/stdout.log`：REUSE_VM原始起止、REUSE_EVENT和原有native日志。
- `samples.csv`：200条采样与TxID/VM时长/客户端时长/提交高度/Gas关联。
- `summary.csv`、`historical_comparison.csv`：P50/P95、成功率及历史对照，缺失TPS明确标记。
- `correctness.csv`：返回、原始/规范化写集、事件、Gas逐对检查；Table/native Gas/生产安全未通过项明确保留。
- `instance_summary.csv`、`resource_summary.csv`及原始`resources.jsonl`：创建、关闭、池等待、CPU/RSS/Threads。
- `environment.json`：版本、二进制/native/config/source哈希、负载、停止原因。
- `smoke.py`、`analyze.py`、`vm.patch`、`node.patch`、独立分支源码：运行和统计实现。
- `startup-attempt1/`：第一次启动端口字段转换遗漏，尚无交易，触发60秒启动watchdog；已保留原记录。修正独立配置后才执行上述冒烟，没有删失败业务样本。第一次编译计时插桩位置错误的build.log也保留，修正后构建见build-attempt2.log。

只复核现有数据：`python3 -B analyze.py`，不会启动节点。Gas不一致作为结果记录，返回/规范化写集/事件意外差异则令统计检查失败。

不要直接重跑smoke.py覆盖结果，它会拒绝已有requests.jsonl。继续前先解决资源与配置门槛；新运行必须准备新的输出目录、独立空账本和无冲突端口，使用保存的相同binary/config及显式R0/R1，记录变更。fact补测使用`REUSE_SMOKE_ROOT=<new-output>`，不是覆盖主批次。

## 后续最小需求与回滚

需向王浅秋取得：历史node/VM/native/cmc commit或完整patch、原始WASM及输入、cmc命令/并发/发送节奏、四节点配置和机器分布、原始TPS输出/统计脚本、节点VM与资源日志，以及WASI freelist/进程隔离/实例复用修改情况。

扩大前先解释RSS/虚拟地址空间增长，验证Store访问和在途实例回收；确定cmc的请求TPS、CTPS及业务成功提交TPS口径。若门槛满足，再用同一四节点配置按R0/R1独立批次、相同输入及负载运行，分别统计成功提交和VM attempts。不要通过改成同步fresh或加根锁来代替历史池行为。

回滚：本轮节点均已停止，生产启动脚本/二进制/主分支未替换。实验binary只有显式设置R0/R1才启动；弃用本实验binary、保留独立worktree和结果即可。不要对原脏工作区执行reset/restore，不删除历史账本或产物。
