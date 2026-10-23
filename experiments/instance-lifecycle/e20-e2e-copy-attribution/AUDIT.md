# E20历史审计（2026-10-23）

本文件在新实验启动前形成。生产工作区不修改；历史数据保留。本轮先复用保存的原Step-17二进制做compute.bigNumCal单客户端复现，详细追踪单列。默认池并发受安全门槛限制。

## 原始客户端的真实边界

`step-17-real-node/prototype/client-benchmark.go:17–24`中参数切片先构造，再`begin:=time.Now()`，业务走SDK-Go/v2 v2.4.0 `InvokeContract(...,60,true)`，返回后`time.Since(begin)`。同一SDK客户端常驻，不包含新建SDK或Python启动进程。它包含SDK构造请求/签名、同步RPC与结果等待，成功业务响应包含ContractResult/TxBlockHeight，不只是提交到交易池的ACK；不代表已经等待多个独立组织确认。

**纠正旧报告中的“5ms SDK轮询”解释：**当前冻结SDK的`WithNodeOnlyAsync`默认false（sdk_config.go:531），两份sdk.yml未设置node_only_async/结果订阅，客户端也未启用这两个选项。sdk_client.go:674的轮询条件要求nodeOnlyAsync=true；本配置走:699–700的`sendRequestSync`，conn_pool.go:114–117调用gRPC `SendRequestSync`。节点api_service.go的同步分支注册tx结果channel，AddTx后等待提交结果dispatcher；trace中的sync_result_received对此有动态证据。retry_interval=5仅配置存在，不能认定其在本路径按5ms轮询。没有证据把负收益归于此轮询量化。

## 负载、锁与实例路径

- 原Step-17 `run.py:74–88`：每合约1次冷访问、5对预热；a/b各100对、workers=1；a4/b4各64对、workers=4。热调用循环没有人为Sleep，随机决定每对先后。nodes.py中启动/停止轮询Sleep不是业务请求间隔。
- `nodes.py:15`固定`CM_FRESH_INVOKE=1, CM_STEP17_SERIALIZE_VM=1, CM_STEP17_OBSERVE=1, GOMAXPROCS=4`；Copy开关baseline=0/optimized=1，artifact目录相同，env去掉CM_STEP16_SERIALIZED_MODULE。未做CPU绑核和物理端点交换。
- 可恢复的是脚本显式设置的实验变量、配置和二进制；历史父进程完整继承环境没有逐项归档，不能声称全部系统环境变量逐字相同。本轮完整启动参数见每节点command.json，也没有把含潜在凭据的环境全量写入报告。
- runtime.go:50以后根Invoke在depth=0时获取每链invokeMu；step17Begin在获锁之后。因此STEP17 invoke_ns**不含根锁等待**，客户端包含。子调用同步沿执行链，不重复获取根锁。
- vm_pool.go:638–645 freshOnDemand同步NewInstance，:685–688同步CloseInstance；newVmPool fresh模式不启动grow worker。已完成业务的Instance不回池；WASI environment freelist复用不是Instance复用。
- 原Step-17是同步fresh测试，不能把其Copy收益解释成仅加速后台补池；默认池路径的解释需独立测试。

## 版本、产物与配置

Step-17记录CVW源基线4cdf6c5、源码快照提交202b666、最终文档b21ca6a；节点源提交351b816含已有工作区依赖/提案修改，不能仅以最早node仓库HEAD等同实际源码。以原source_hashes.json、prototype.patch、node-workspace.patch及保存binary为准。

原计时节点SHA256 `ba5cbd3b956fb24f10ac0e73aec1a21a17998709c4977cd5db7cd316141cc2b0`；原client-benchmark SHA256 `8c54eab4ca354d21ddbf0129909f10cc366e1143a02266b6f6417a7f7ebafd2f`。本轮已校验。两模式共享同一节点和客户端binary；各逻辑合约WASM一致，Copy内部noData module及artifact当然与baseline不同。compute逻辑WASM SHA为`e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507`。native SHA `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`不变。两独立节点端口/数据路径不同，物理运行环境未严格同相位。

## TxID关联与重执行

本轮重新从两个原stdout的STEP17行解析，不仅转抄summary。5248条热客户端调用对应**6008次根合约VM Invoke**。382个TxID有多次根执行，全部在workers=4批次：130条执行2次、126条执行3次、126条执行4次。原summary选择最后一次根Invoke，不包含此前attempt的VM时间和根锁等待；不能将其直接从客户端延迟扣除。exchange子调用另外记录，不和根窗口相加以免重复。

逐交易索引见historical_tx_join.csv、historical_attempt_counts.csv。workers=1热样本均只有一次根Invoke。原日志不能提取原版纯channel等待、独立根锁等待、客户端发出至节点收到的单向延迟；缺失不填0。

## 更新的端到端负向点估计

存在`step-19-client-latency-trace`（2026-10-19），compute.bigNumCal两批各30对，单客户端、无人工业务Sleep，第二批交换端点角色；120条热调用，20条预热、4条冷调用。VM节省配对Median为0.670/0.465ms；客户端节省为-2.034/-3.719ms，但两个95% CI均跨零，不能称稳定负收益。144次调用均只有一次VM attempt。

其原始requests.jsonl和stdout trace支持逐交易定位：同批平均值可加核算中，AddTx返回至VM入口的额外耗时约1.686/2.573ms，抵消VM节省。不能据此认定Copy造成调度退化、也不能笼统归为共识或固定出块吸收。详见原mean_accounting.csv和本轮重算。详细trace有观测扰动，不能替代低日志版性能。

## Step-19的100ms与最新TestInvoke

`step-19-reuse-reproduction/smoke.py:117–120`在SDK业务request完成后`time.sleep(.1)`，下一次循环才发下一笔，确实是业务请求间的人工间隔；不在单次Invoke计时里。首轮及fact补测每组3次预热+20次正式。

最新`testinvoke-reproduction`不启动节点、使用SnapshotMock、无间隔，每批R0/R1各100次、3个独立批次。R0/R1的等效TPS比10.4–12.2，R1全部100次都等待池；不等于真实节点TPS。`TPS(callMethod only)`标签误导，实际为成功数除完整InvokeTime总和。普通版结束有未完成创建/关闭，close没有join；native Store并发安全仍未验证。

## E20执行边界

先克隆已停机Step-17 baseline账本到新隔离目录，两个模式使用同源账本和相同配置，仅改隔离路径/端口；不运行旧start/clean脚本，不覆盖旧日志。先小批smoke，再compute三批、每批100对、无业务Sleep，复用原节点和计时客户端。该范围保留原w1负载形式，不声称重新覆盖8合约或4并发。

详细诊断另用已保存Step-19 trace binary，源码/构建哈希与原版分别记录。不直接相减跨进程时间戳：用节点进程内CLOCK_MONOTONIC阶段差、客户端自身elapsed，以及两种嵌套时长之差形成未细分残差。客户端发送到RPC入口、RPC返回到客户端的独立单向时间保持缺失。

默认池存在共享Store创建/执行/关闭所有权和异步回收缺口，严格禁止通过增加全局锁冒充原路径；本轮保留去Sleep的差异文件，但在门槛未通过时不宣称完成默认池R1/R2或并发验证。
