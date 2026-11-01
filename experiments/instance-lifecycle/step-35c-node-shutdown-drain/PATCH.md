# 实验补丁与版本

节点基线72e077a，实验提交`0ce8fba61761f0ced5fb598ab28727080706577a`，分支experiment/step35c-node-shutdown-drain。
CVW基线a9910fb7（35B最终报告提交），原始任务的34/35/35A提交已核实，见audit/baselines.json。

- 节点：HTTP2逐请求门、RPC有界排空；Core任务登记/排空；Proposer循环/子任务join与Stop幂等；模块停止失败不再继续DB关闭；最终诊断服务Stop。
- Store/v2@v2.4.0独立源码副本：PutBlock租约；Close幂等/错误缓存；WAL清理任务等待；Archive循环/压缩等待及可中断定时器。原module cache不修改，node go.mod仅新增本地replace。
- VM副本：原Owner不重写，仅Stop10秒context和统一单调时间诊断/测试rendezvous。
- native/Go版本/Gas规则/Guest/编译器/Copy算法不变。本轮CM_STATIC_MEMORY_COPY=0，无A/B1。

精确补丁：audit/node-final.diff、audit/store-blockstore_impl.go.diff、audit/store-archive-manager.go.diff、audit/final-vm.diff、audit/final-vm-observation.diff；新任务门/诊断代码位于source/store/step35c。

冻结候选binary `binaries/candidate` SHA `c07aeffc171be1c3da8d8b4a69c74d19ef7008cf0253b78f916887b5cf47cc77`。观察版和失败候选另有独立binary/hash/log，未覆盖。运行产物ignored保存在worktree；node/client.so加载路径逐进程核实，见audit/loaded-native.json。

回退：生产未替换，无需回滚生产。实验进程停止后，在另一个worktree取35B节点72e077a+其VM源即可回退；不要覆盖正在使用的so、不对历史工作区reset/clean。新旧生命周期的性能应建立新基线，不与旧样本拼成配对数据。
