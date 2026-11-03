# SDK计时与提交确认路径

本轮实际运行客户端为source/client.go（client3），SDK module `chainmaker.org/chainmaker/sdk-go/v2@v2.4.0`，Host Go1.25.0。节点为独立node-step39c工作树，原HEAD c28bfa8，保留35C的0ce8fba修复。源码原文片段与哈希归档见audit/source-evidence.json；完整客户端源码已交付。

## 客户端边界

source/client.go:70–71建立含单调时钟的begin/t0；:90调用 `cc.InvokeContract(...,60,true)`；:92–98取end/elapsed。参数和TxID生成在窗口之前。SDK内部签名/RPC/同步确认包含在窗口内。

```go
begin := time.Now()
t0 := begin.Sub(epoch).Nanoseconds()
resp, err = cc.InvokeContract(j.Contract, j.Method, j.TxID, p.KV, 60, true)
end := time.Now()
r["elapsed_ns"] = end.Sub(begin).Nanoseconds()
```

SDK sdk_user_contract.go:168起InvokeContract→InvokeContractWithLimit→proposalRequest；sdk_client.go:622起sendRequest、:674起sendTxRequestWithSyncResult；conn_pool.go:114–118实际调用rpcNode.SendRequestSync。逐笔节点trace也确认360笔均为SendRequestSync。

节点 module/rpcserver/api_service.go:596–659 dealTransact：:606先注册TxID结果channel，:615 AddTx；随后:636起等待txResultC，取ContractResult和TxBlockHeight；超时返回错误。它不是AddTx ACK就返回。

module/core/common/committer.go:61执行store.PutBlock；block_helper.go:1058附近commonCommit.CommitBlock完成后，:1087 PublishSafe(BlockInfo)。module/subscriber/subscriber.go:22起转为NewBlockEvent；rpcserver/tx_result_dispatcher.go:266 SubscribeBlockEvent，:275按tx逐个trySendTxResult，:320起填入同步结果。committer的NotifyMessage不是这条交易结果通知，不应按名字误判通知早于持久化。

360笔均读取 GetTxWithRWSetByTxId，要求TxID、区块高度>0、已存结果与SDK结果相等；节点同进程单调trace均为put_end不晚于rpc_tx_end。正常关机后另启36个只读节点，全部360笔仍可查，结果/高度/业务投影一致。因此本轮分子是实际确认提交数。

## TPS窗口

source/client.go:107–117记录批内首SDK开始和末SDK返回。scripts/case_run.py:54附近一次性client.batch(targets)执行10笔同步请求；期间没有Python循环、100ms Sleep、额外查询或手工重试。检查交易/状态发生在窗口后。

```python
seconds = (window_end_mono_ns - window_start_mono_ns) / 1e9
tps = unique_confirmed_commits / seconds
```

scripts/analyze.py逐笔验证start≤SDKstart<SDKend≤end、每个run内TxID唯一、结果/高度对应真实账本。36个窗口均10次发送、10次成功提交、0失败/超时。窗口终点就是最后成功同步提交返回，没有在途跨窗口交易；部署、节点启动、冷Query、第二次预热Query、读回与关闭不计入。三批汇总TPS=30/Σ窗口秒数。客户端成功完成吞吐与提交TPS本轮分子相同，分别保留字段；不是节点最大TPS。

VM日志等效TPS独立为`10/Σ根Factory_Invoke秒数`，另列TPS_RESULTS.csv，不能当作节点提交TPS。历史王浅秋VM口径也不能直接与SDK吞吐相除比较。

## VM窗口与嵌套

实际VM Factory依赖：`/home/frankie/mygitprojects/.worktrees/cvw-step21c/chainmaker/chainmaker-vm-wasmer/vm/v2@v2.4.0/vm_factory.go`：:393创建Runtime（根Clone在这里发生）；:432–436包围Runtime.Invoke，:438另输出REUSE_VM。scripts/analyze.py按TxID取begin_ns/end_ns，使用未四舍五入的ns，不用INFO的6位秒数重建。

source/vm/step35_node.go:103–105创建Runtime保留Clone；:139 prepare和Module缓存；:202–213执行输入SHA校验；:223起Owner invoke；:247 prepare；后续Fresh Store/WASI/Imports/NewInstance、Memory restore、_start、CallMethod及同步scope.Close。根Factory含SHA和Owner进入及六次子调用；Owner事件invoke_ns是其内部窗口，不能与Factory相加。子Factory已嵌套在根Factory内，不能重复求和。Instance Close已在invoke结束前执行，Close单项也不能再加到完整Invoke。

客户端单调时间只用于客户端自身差值；NODE_STAGES.csv各阶段只用节点自身mono_ns。两个进程的单调原点不能直接相减。E2E−Factory为两个实测持续时间的残余，包含Clone、SDK、排队、提案与提交等窗口，不能仅凭此差值指定某个组件根因。

## 已观察到的VM外尾延迟

24笔短方法慢交易均保留。对应节点RPC→VM窗口与proposer_ready=false重叠，见PROPOSER_OVERLAP.csv。源码module/core/syncmode/proposer/block_proposer_impl.go:220附近在非self proposer时不提案；:440 OnReceiveProposeStatusChange更新状态，core_syncmode_impl.go:174记录ready事件。这支持VM前提案状态等待的相关证据，尚未确定状态恢复延迟的根因。实际TBFT单验证配置，不能拿未选中的Solo实现Sleep解释本轮现象。

正式阶段沿用统一35C/Owner阶段日志，关闭39C详细SHA日志；这不是无日志生产性能。只证明该统一观测条件下的小样本效果。冷/热Query与首次登记另存raw_logs/COLD_WARM.csv；启动日志/firstready/初始空registry原始顺序保留，没有构造一个未实测的精确“启动延迟”。
