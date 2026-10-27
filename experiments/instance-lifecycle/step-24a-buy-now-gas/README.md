# Step-24A：buyNow复用Gas差异根因诊断

日期：2026-10-27。独立分支 `experiment/step24a-buy-now-gas`，父提交 `ba57368320432551a71a5e1e77a6c43b40daf1ca`（Step-23）。本轮真实执行已完成，未启用Copy/A/PB，未改原WASM、Gas规则或生产VM，没有TPS压测。

## 本轮结果

三块独立对照，每块五条件、每条件独立进程，只执行一次目标buyNow；以下数字在三块中完全相同。主原始证据是 `raw_logs/safe-block{1,2,3}-{条件}-events.jsonl`、同名`.log`及`-receipts/target.json`。完整复算见 `BLOCK_SUMMARY.csv`、`PAIRED_GAS.csv`、`STATE_COMPARISON.csv`。

| 条件 | 目标transferFrom实例历史 | buyNow根Gas | 第6子调用Gas增量* | DeleteState→log窗口增量 | 相对R1根Gas |
|---|---|---:|---:|---:|---:|
| R0 正常复用 | init、mint、approval；此前用3次 | 12,761,395 | 12,679 | 7,564 | −4,379 |
| R1 Baseline Fresh | 新实例；此前用0次 | 12,765,774 | 17,058 | 11,943 | 0 |
| S0 提前创建未执行 | 预留新实例；此前用0次 | 12,765,774 | 17,058 | 11,943 | 0 |
| J 原有JSON编码导出预热 | 预留实例；此前执行1次诊断导出 | 12,761,395 | 12,679 | 7,564 | −4,379 |
| U 原有JSON解码导出预热 | 预留实例；此前执行1次诊断导出 | 12,765,774 | 17,058 | 11,943 | 0 |

*本次子调用增量=子调用累计输出−累计输入，仅用于这个无更深层子调用的transferFrom；不能把六个子调用累计Gas求和。

**已确认：4,379差值重复出现；运行原有JSON编码相关预热足以消除该差值；单纯提前创建及本次JSON解码预热不能消除。** J与R0在全部已记录目标Gas点均相等；S0/U与R1也相等。所有条件目标调用顺序、业务输入、返回值、透明记录的Get/Put/Del操作、根最终实际RWSet、事件及最终账本一致。R0的Gas仍与Fresh不一致，只能作诊断和性能参考。

**尚未确认：encoderCache或fieldCache中的哪一个条目/分支恰好贡献4,379。** J导出同时执行编码、fmt格式化、分配、日志和写状态；虽然恢复了账本，guest运行时状态有意保留。第一次内部cache读取器预检失败，已停用，不能用静态推测替代运行期命中证据。本轮定位至`main.setTokenLatestTxInfo`所在成功路径的Guest窗口，尚未缩至某一个首次扣费的内部函数。细节见 `GAS_ATTRIBUTION.md`、静态优先记录 `TRACE_PATH.md`。

## 条件与初始化

真实调用链（各子调用深度1，无虚构返回）：

`exchange.buyNow → identity.addWriteList → identity.isApprovedUser → identity.isApprovedUser → erc721.mint → erc721.setApprovalForAll2 → erc721.transferFrom`

每进程先真实执行identity、ERC721、exchange三个`init_contract`，ERC721参数`name=huanletoken,symbol=hlt,tokenURI=https://chainmaker.org.cn`。目标输入、固定TxID及完整摘要在 `inputs/business.json`；tokenId=1，每进程独立初始账本。

初始hash `a27f2d1e3ac3ab6c1e19c84c78c855eaf068cc21f4f31dc9e9641d8fe12274db`，最终hash `620b0453aca92f7c3a1ec4114528292b0e315dd1b20ca75f0d70c68c9b3cb158`；返回`buyNow success`。J/U在独立候选Instance运行原WASM已有诊断导出后，仅把fixture账本恢复至init后副本，不清除任何guest缓存；R1/S0的目标实例未执行业务，J/U明确属于预热复用诊断，不能称Fresh。

Step-23对比对象也经原CSV复算：5块真实复用/Fresh、5块Fresh/Copy；仅有效v2。R0目标ERC实例用过3次，Fresh用0次。不是两个都Fresh的冷/热比较。原v1受状态观察器影响的记录不纳入。

## 执行次数、顺序及失败保留

- build01：R1 probe off成功；随后内部cache reader on失败，在mint处抛出`cache key layout/uniqueness mismatch`。业务失败，根Gas 1,510,719 **不可用作目标性能/Gas数据**。STOP、日志、旧源码及构建信息保存在`audit/unsupported-cache-reader-build01/`及原raw_logs。
- build02：固定`A24_CACHE_READ=0`，保留Step-23有效v2 Gas/状态边界观察。五条件各probe off/on一对，共10个预检；逐call Gas、结果、最终RWSet/账本/事件一致。
- 正式3块×5条件=15个进程，15笔根buyNow、90笔真实子调用；每个条件3个独立观测，不是每组100次。
- 顺序：块1 R0,R1,S0,J,U；块2 U,J,S0,R1,R0；块3 S0,R1,J,R0,U。
- 总共27次运行，26次通过、1次探针失败，全部保留于`ALL_RUNS.csv`。已知失败由内部布局读取器造成，保留原STOP，经`audit/resume-decision.json`仅允许禁用读取器的新binary/safe标签恢复；任何新失败都禁止继续。

## 安全和计量边界

沿用Step-23固定OS owner和ManagedScope串行模型：每合约独立Store，Module只在所属Store缓存，所有创建/执行/关闭同一owner；Fresh同步关闭，父子调用使用不同Store；原Gas getter/setter同scope调用仍沿用原路径。`source/vm/step24a_checks_test.go:14`只编译原Module一次/合约，没有模板/noData变换；R0留用3个实例，R1/S0/J/U最多10个，结束均created=closed、managed/pending=0，详见`RESOURCE_LIFECYCLE.csv`。

RSS软限1536MiB，线程220；cgroup硬限2GiB/256tasks，Go45s/进程60s；全局available≥8GiB、swap≤1GiB，未提高限制。全部进程退出。监控采样最高RSS536744KiB（524.16MiB），线程176；这只是采样最大值，不能当精确瞬时峰值或长期无泄漏证明。

Gas探针只读原registry计数，结束与原GetGas核对；`gas_absolute=runtimeGasLimit−remaining`是累计已用Gas，不是native fuel或时间。目标seq36/37为窗口两端；嵌套累计传播不得重复加总。保留宿主边界详细日志，**本轮不报告其时间为性能结果**。原计量、CallMethod和Gas异常处理不改，另记录原CallMethod错误，不能只以进程PASS认定业务成功。

未验证：真实Table函数身份、异常/OOG/回滚全覆盖、原实例池并发、共享Store跨线程、长期资源回收、native精确源码重建。继承限制不因本轮串行通过而解除。

## 版本与复算

宿主Go1.25.0，原ERC721 producers Go1.24.1。不重新编译合约。三个WASM SHA和原路径在`inputs/manifest.json`，native SHA `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。ChainMaker模块v2.4.0，实际go.work依赖、主机环境、源码文件hash及逐过程env在`go.work`、`audit/host-environment.json`、`environment.json`和`raw_logs/*-command.json`。

实际build02 binary SHA `303c5a7680d3cfee20bd07dc8332ed929073a3a015fe25f03374963efd916fc1`。build设置中observer/model字符串保留旧名称；实际快照读取已禁用，条件以源码hash和command env为准。binary/native保留本机但不入Git，所需依赖worktree路径也未打包；不是可脱离现有CVW直接运行的分发包。

```bash
cd /home/frankie/mygitprojects/.worktrees/cvw-step24a/experiments/instance-lifecycle/step-24a-buy-now-gas
python3 -B scripts/analyze.py
# 原执行入口，可恢复且不会重复已完成label：
python3 -B scripts/suite.py
```

重建需已存在相同native库、WASM及go.work依赖（不联网升级）：`python3 -B scripts/build.py 新label`。这会形成新binary，不能用旧resume许可冒充已有运行。不要删除旧STOP或覆盖原label。源码最小差异在`audit/source-vs-step23.diff`；新诊断逻辑是`step24a_checks_test.go`、禁用的`step24a_cache.go`和目标预留实例选择，其他文件继承Step-23。

回退：停止本实验systemd unit并离开实验worktree即可；没有服务或生产配置需要回滚。不自动删除原日志、不push。IDE主工作区只同步新实验资料，生产文件/已有dirty改动保持原样。
