# 节点关闭与账本调用链

源码前缀：N=`.worktrees/node-step35c`，S=`本目录/source/store`，V=`本目录/source/vm`。版本/精确diff见audit/node-final.diff、audit/store-*.diff。

## 正常交易

`SDK SendRequestSync → N/module/rpcserver/middleware.go:GrpcHandlerFunc(HTTP2 ServeHTTP) → api_service.go:SendRequestSync → TxPool → Core Proposer → SafeFresh Owner执行Guest → ProposedBlock消息 → Solo共识 → VerifyBlock消息 → CommitBlock消息 → syncmode.CoreEngine.OnMessage → goroutine AddBlock → common.BlockCommitterImpl.AddBlock → common.CommitBlock.CommitBlock → S.BlockStoreImpl.PutBlock → CommonPutBlock → WriteKvDb → 五个KV子任务 → 本地wg.Wait → PutBlock返回 → 提交缓存/通知/结果处理 → 同步RPC响应`。

真实buyNow的Guest内部还有identity.addWriteList、identity.isApprovedUser两次、erc721.mint、setApprovalForAll2、transferFrom。它们属于根请求的真实执行，Owner的既有可重入协议不变。

## 数据库来源与析构

- N/module/blockchain/blockchain_init.go:254/307注册storeFactory.NewStore。
- S/store_factory.go:86→store_builder.Build；store_builder.go:375/408等创建StateKvDB/HistoryKvDB并注入DBHandle。具体DBProvider和LevelDB版本仍用原依赖图。
- S/blockstore_impl.go的Close关闭Block/State/History/Result等DB；HistoryKvDB.Close位于historydb/historykvdb/historykvdb.go:177，最终dbHandle.Close。
- 历史直接失败在historykvdb.writeBatch:220，经CommitBlock与BlockStoreImpl.WriteKvDb.func3；本轮观测版失败为StateKvDB.writeBatch，经WriteKvDb.func2。

## 关闭

`SIGTERM → cli_start.handleExitSignal → RPCServer.Stop → ChainMakerServer.Stop → Blockchain.Stop → 停模块 → VM Manager.Stop/InstancesManager.StopVM → Owner.Stop → ledger.Close → 网络停止 → 诊断服务停止 → 进程退出`。

当前实际模块顺序见每条module_stop_begin：TxPool→Core→VM→Consensus→NetService→Store；如果Sync/其他模块启动，源码还有对应停止项，不能把该列表泛化为全部拓扑。CoreStop加入提案任务和Core回调排空；账本Close最后再等待本组件已接收任务。

## 异步入口与覆盖范围

| 入口 | 原行为 | 本轮处理/限制 |
|---|---|---|
| CommonPutBlock | cache/SQL阶段、5个KV并行子任务，本地wg等待 | PutBlock租约覆盖整个入口；Close等待租约归零 |
| WriteKvDb | block/state/history/result/bigfilter goroutine | 不改变计价/写入内容；等待父任务即覆盖其局部wg |
| Common WAL清理 | 另起deleteBlockFromLog goroutine | 登记worker，DB/文件Close前等待 |
| Core Verify/Commit | OnMessage另起goroutine | 创建前登记，结束注销，Core.Stop排空 |
| Proposer循环及提案任务 | 循环退出不代表worker结束 | loopDone+worker等待，停止信号可中断接收 |
| Archive移动/压缩 | Close只发stop、循环Sleep，压缩独立goroutine | 等待循环和压缩；原定时等待可被stop打断 |
| QuickPutBlock队列 | WAL/cache→writeBatchChan→consumer→WriteKvDb | 当前mode0不进入；没有实测队列入/出，非本轮准入范围 |
| blockfile异步写/SQL/归档恢复业务 | 配置或业务路径不同 | 未激活或未测试，不能视为通过 |
| 全局消息总线/网络/Go运行时 | 存在进程级goroutine | 未逐个全局join认证；本轮相关资源任务归零，进程/cgroup退出。不能声称每个全局goroutine都已单独证明 |

Reset由真实InstancesManager.ResetAllPool控制入口触发，只清理VM缓存；它不负责排空区块提交。原Owner已协调resetting/closing；本轮保留该协议，Stop等待进行中的Reset，不在Stop后创建新Owner。
