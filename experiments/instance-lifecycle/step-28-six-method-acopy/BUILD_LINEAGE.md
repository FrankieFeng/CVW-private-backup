# Step-28构建、实现与计时冻结

实验分支`experiment/step28-six-method-acopy`，工作树`.worktrees/cvw-step28`，父提交`c8c46ee`。生产CVW保持不变。实际host binary/build3 SHA为`01e9c03c410a271e4f29e8eba6a59eb31ee4a98026bd96e473ff0043ad5e5e09`；完整编译命令、每个Go源码SHA见`audit/build3-command.json`、`environment.json`。本目录保存的是实验VM副本，不是生产VM部署。

Guest统一取Step18源码提交`95903a3`、Go1.24.1、原SDK0.1.3、registry相同Gas插桩；host Go1.25.0，ChainMaker2.4.0/原native库不变。库SHA `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。具体CPU/WSL/内存/affinity及工具SHA见`audit/host-environment.json`与`audit/guest-lineage.json`。

compute、fact、ERC721复用Step18保存的P0/plain与A/P0/plain二进制，逐份校验旧variants.csv哈希；其历史源码/环境记录见`audit/step18/`，冻结源码另存`guest-source/`。未声称今天重新构建出了逐字节相同的旧三个WASM。exchange和identity此前没有此家族的A产物：本轮从同提交源码、同Go/SDK/registry，按原A脚本构建plain及独立probe，各自重算padding。新源码目录路径会进入Go构建元数据，命令与SHA逐份保留，不把它们冒充历史预编译WASM。

A是链接时可达静态padding，调整Go moduledata/end及初始bloc，使运行时第一次4MiB arena reserve对齐；不是简单把initial memory改为128页。使用原公式`padding=4MiB-baseline_bloc-5*64KiB`，每个合约、plain/probe分别重算，plain A的bloc均检查为3866624。新增identity/exchange在独立诊断构建实际调用`Step18Read(4/5/6)`，首次reserve bloc4194304、distance0、align4194304；日志`raw_logs/alignment-preflight.log`。诊断runtime带时间/对齐观测，只用于预检，绝不进入性能样本。既有三个A产物沿用Step18/26已验证版本。

B1完全关闭；SDK源码与历史保存的zip来源哈希核对，`GetBatchState`仍存在。不使用删除公共API的P1 SDK，不混入Step24B原件家族。compute bigNumCal/hashCal为10000循环，normalCal为10000000，三组不改变业务工作量；A改变静态布局和WASM哈希，G0/G1同原件，G2是同源A变体，不能描述为三个相同二进制。

## 实际Copy链路

- `source/vm/step25_test.go:30` `e25Prepare`：按源码SHA取/生成计划，`prepareStaticMemory`解析最终WASM，按Data段声明顺序构造S1 image，去掉Data section生成noData。计划绑定合约名、版本、最终源码SHA、配置SHA；缓存Store内编译好的Module。准备、编译不在每次Invoke内。
- `source/vm/step22_static_test.go:85` `prepareStaticMemory`：仅支持单个本地导出Memory、简单i32.const active Data及受限元素初始化；拒绝自动start、导入Memory/global/table、DataCount、passive等。先按声明顺序覆盖image，再合并重叠/相邻覆盖区间，跳过整段全零的并集区间。**不是逐字节剔除零，仍复制保留区间内部的零。**
- `source/vm/step22_runtime_test.go:140` `makeE22`：独立Store中的cached Module →新WASI/imports → `w.NewInstance`（G0原Module，G1/G2 noData Module）→计划restore→S1→WASI Initialize→`_start`→S2。
- `source/vm/step22_static_test.go:235` `restore`：校验Module/配置/长度，以Memory.Data()作为dst，逐个`copy(dst[Begin:End],Image[Begin:End])`。真正替代active Data初始化，绝不先原Data初始化再重复Copy。Memory初始页数来自各自最终WASM，Copy不改页数。image在进程内只读，不跨不同二进制复用。
- `source/vm/step21d_runtime_test.go:232` `dRuntime.Invoke`：新Instance同步创建、SetGas、真实CallMethod/GetGas、同步CallDeallocate/managed scope Close；根Invoke包含真实跨合约的嵌套执行与子实例关闭。按固定owner严格串行执行，无后台池、grow、异步Close或全局锁。`managed.go`所有权守卫不变。

## 计时边界（单调时钟）

`NewInstance`只包`w.NewInstance`，**不含Copy**；Copy只包restore，含Memory访问/边界与key检查及实际Go copy。S0→S1从dRuntime.Invoke进入开始，含WASI/imports、新建与Copy；S1→S2=S2-S1，含WASI Initialize、取_start、_start；S2→S3=S3-S2，含SetGas、CallMethod/GetGas和结果处理。`CallMethod`包含`exportFunc.Call()`；根buyNow的两者均包含下游同步执行。Close包含CallDeallocate和managed清理；完整Invoke从进入到退出，含Fresh创建、业务和同步Close，主指标不是仅Guest导出窗口。Module/模板预计算、真实init_contract、账本克隆、结果JSON落盘、host resource采样均另列/在外。根Invoke退出后的JSON输出不在其计时内；子调用的诊断输出发生在根调用内，仍是本测试夹具的开销。

S1内存SHA仅功能preflight启用，正式性能关闭。每次正式调用保留低开销分段计时和子调用trace；本轮为诊断串行VM路径，不是原池并发、节点客户端延迟或链上TPS。

## 构建与恢复

`python3 -B scripts/prepare_guest.py`校验/恢复产物；`python3 -B scripts/build.py <new-label>`生成host binary；主runner当前固定build3。命令使用绝对路径，依赖已有固定Step21C/Step18 worktree及工具链，移动机器需显式调整go.work/脚本路径并单列新构建哈希。新build不得覆盖旧日志；先确认无活动unit。`.so`保留本地，Git不上传，按以上SHA校验恢复，不能任意替换。

`python3 -B scripts/experiment.py preflight`完成六方法三组预检、buyNow两条失败回滚对照；通过后`python3 -B scripts/experiment.py formal`按已保存outcome跳过已完成进程。网络断开先查PROGRESS/state.json与systemctl，不重复启动。`python3 -B scripts/analyze.py`仅复算，不启动Guest。原始host build1和Guest首次准备失败均保留，发生在性能采样前，未删除数据。

实验源码/Guest产物已在本分支本地提交`e7924d8`冻结。该提交在测量结束后生成；运行时HEAD为c8c46ee加已保存实验文件，所有host Go文件与编译时source_hashes逐项再次校验完全一致，见audit/source-freeze.json。TIMING明确区分code_snapshot_commit和execution_git_head，未伪称测量时已处于后生成提交。MATRIX.csv列出每个方法/组/root与callee的完整WASM、执行noData及模板SHA和缓存key。统计脚本的后续修订仅影响离线复算，不改host二进制与计时边界。
