# 关键计时代码与提交确认

本目录的source/client.go是实际编译、运行的客户端。Go二进制buildinfo和哈希保存在audit/client2-buildinfo.txt、client2-outcome.json。不是仅展示伪代码。

## 客户端计时

`source/client.go:40`在窗口前固定TxID、参数排序；`:63`同一Go进程顺序调用；`:69`开始、`:87`调用、`:89`结束、`:95`单调duration、`:101`成功判定、`:114`窗口输出。

```go
begin := time.Now()
resp, err = cc.InvokeContract(j.Contract, j.Method, j.TxID, p.KV, 60, true)
end := time.Now()
r["elapsed_ns"] = end.Sub(begin).Nanoseconds()
```

开始包含SDK内部构造payload、签名、RPC及同步结果等待；参数列表/TxID预处理在前。结束为同步SDK返回，不另加查询耗时。连续循环不Sleep，也没有Python逐笔驱动间隔。窗口包含Go循环本身的真实管理成本。Query预热、部署、业务前置状态和核对查询均在外。

## 为什么不是AddTx ACK

实际SDK `/home/frankie/go/pkg/mod/chainmaker.org/chainmaker/sdk-go/v2@v2.4.0/sdk_user_contract.go:168` → `sdk_client.go:666`同步发送 → `conn_pool.go:117`的`SendRequestSync`。

实际节点 `/home/frankie/mygitprojects/.worktrees/node-step36/module/rpcserver/api_service.go:147` → `dealTransact:596`：先`:606`注册TxID，`:617`AddTx，然后`:643`等待txResultC；从结果填写ContractResult和TxBlockHeight，不是AddTx立即ACK。

`module/core/common/block_helper.go:1060`调用CommitBlock；`module/core/common/committer.go:61`调用PutBlock；之后`block_helper.go:1087`发布BlockInfo。`module/rpcserver/tx_result_dispatcher.go:264`启动订阅消费，`:274`遍历交易，`:320`trySendTxResult将交易结果和高度送回已注册请求。以上路径限本轮Common模式，不推演Quick模式。

`source/client.go:72`实际执行GetTxWithRWSetByTxId；`scripts/case_run.py:21`的committed函数核对链上TxID对应的height>0、与SDK返回height相同及ContractResult完全相同。`:28`汇集业务写集，`:41/:48`调用真实状态回读。`scripts/postcheck.py:5`在节点重启后再次查询和回读。证明正常提交可查询及重启保留，不等于断电fsync认证。

## VM阶段

`source/vm/step35_node.go:199` Owner内invoke；`:204`开始，`:217`完整invoke_ns（defer执行，包含同步Close）；`:245`关闭计时；`:263`NewInstanceInStore、`:264`计时结束；`:270`开始restore、`:275`Copy计时结束；`:277`S1；`:278`WASI Initialize；`:285`开始_start、`:287`结束；`:292`S2；`:316`CallMethod开始、`:317`结束。

`source/vm/step35_static.go:85`生成模板和NoData；`:235`restore。`step35_node.go:125`prepare按合约/版本/源SHA/native编译Gas配置/Copy开关缓存；命中保留Module与模板，每次业务独立Store/Instance。Copy在NewInstance后、WASI Initialize及_start前。A为冻结的同源内存布局二进制，不临时改Guest。

NewInstance不含随后Copy；S0→S1含Store/WASI/import准备和Copy；S1→S2还包含WASI Initialize及_start导出获取，不能把start_ns等同整个S1→S2；S2→S3与exportFunc.Call未单独记录，标记未记录。CallMethod包含guest导出及host/子调用；buyNow六次子Invoke嵌套在根窗口，不可再加一次。

外层原vm_factory RuntimeInstance.Invoke前后日志保持原UnixNano边界，见VM_EVENTS与RAW_TRANSACTIONS关联字段。单调内层计时与其分开报告，不能忽视外层墙钟变化风险。

## PutBlock、通知及守卫

`source/store/step35c/trace.go:34` CLOCK_MONOTONIC事件；原始node日志的put_begin/put_end按区块高度关联，rpc_tx_begin/end按TxID关联。`scripts/stages.py`仅使用同节点进程单调事件，生成NODE_STAGES.csv。全部1728笔匹配PutBlock与RPC完成；这些事件含日志开销，不是跨进程SDK窗口的精确互斥分解。

`source/store/step35c/trace.go:61`只读Unix端点；`source/store/blockstore_impl.go:236`注册读函数，持原有drain lease调用ReadObject，不在正式计时窗口内。

`scripts/monitor.py:3`阈值1536MiB/220线程；`:8`验证native SHA；`:10`systemd 2GiB硬上限、Tasks256、180s；monitor方法25ms采样，Close发送退出并验证PID/cgroup。`scripts/case_run.py:57`检查Owner计数与退出，失败写STOP_SHARED并停止全部后续任务。没有关闭守卫。
