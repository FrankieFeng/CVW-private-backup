# Step-21C 可恢复进度

当前状态：真实夹具源码已准备并编译；静态检查通过；测试binary/guest执行0次，正式负载禁止。Step21B按用户确认仅规划未执行。下一步独立Step21B，不自动解除Skip。

实验：Step-21C exchange.buyNow真实跨合约复现补全。2026-10-26，Asia/Shanghai。

## 创建时阶段状态（历史记录）

1. 历史/源码审计：进行中。本地仅找到Step21/21A，尚未找到Step21B目录/分支，不能视为已通过Store安全审计。
2. 真实夹具：未开始。禁止固定返回值或Mock成功；拟用真实VM/实际三合约WASM与内存账本。
3. 正确性预检：未开始。可能只允许明确隔离、逐调用排空的功能诊断，不能冒充原池性能。
4. 正式3批100次：未开始。Store安全边界不明确则保持blocked。
5. 汇总分析：未开始。

## 已执行命令

- rg --files -g AGENTS.md CVW .worktrees
- ls experiments/instance-lifecycle | rg step-21
- git -C CVW worktree list
- free -h；systemctl --user list-units step21* --no-legend

## 当前结果与阻碍

无新业务样本，历史结果未覆盖。当前WSL可用内存约26GiB，swap未用，未启动节点或负载。

## 下一步

读取Step21A、buyNow完整预检、TxSimContext/VmManager/子合约源码；确认Step21B是否另有位置。每阶段及每进程立即落盘。中断恢复先读本文件、state.json和raw_logs/outcome，不重复有效进程。不得修改代理/Clash/VSCode，不承诺防止stream disconnected。

## 用户范围更正（2026-10-26）

Step-21B仅规划、未确认执行或报告；不再查找分支。以Step21A风险为边界。本轮只准备真实夹具、源码/参数/状态/Gas审计、编译和静态检查。所有guest测试入口无条件Skip；不启动3批100次或任何Store重叠风险未确认的功能调用。Step21C编号与目录不变，之后独立Step21B决定恢复执行。

下一步：从fc3e90d建独立Step21C分支；添加真实VmManager/TxSimContext/三WASM夹具并只构建测试binary（不运行）。

## 真实夹具源码准备及编译完成

- 新独立worktree .worktrees/cvw-step21c；分支experiment/step21c-exchange-real-fixture，父fc3e90d。
- step21c_fixture_test.go新增真实VmManager/TxSimContext、三合约注册、公开测试身份、内存账本、实际InvokeTime观测、真实初始化/状态/负向路径断言。没有子合约固定响应。
- TestStep21CRealCrossContractPrepared第一条语句无条件t.Skip；未执行该test或任何guest。
- 实际构建命令已保存audit/compile-command.json：有界systemd + go test -p2 -c，audit/compile.log显示退出0。没有运行测试binary，非功能验证通过。
- fixture-manifest.json和inputs/保存冻结输入及三WASM路径/hash，环境和source.patch已保存。
- 下一步只读静态验证与报告；正式负载禁止，Step21B未执行是阻塞前提。

## 静态审计及本轮收尾完成

- 根WASM反汇编6个CallContract静态点，三WASM必需导出齐全；100行冻结tokenId唯一。identity.callerAddress自调用不在本buyNow选定路径，已据实区分。
- 恢复了toolkit初始化顺序及ERC721 name=huanletoken/symbol=hlt/tokenURI=https://chainmaker.org.cn；源码变更后重新编译，均仅go test -c。最新audit/compile.log退出0，旧构建log保留。
- AUDIT.md详细记录参数上限0、SnapshotMock缺失、真实夹具/账户边界、Gas累计/错误覆盖/旧版本回滚疑点；本轮没有修改这些生产逻辑。
- README、correctness.csv、summary.csv、six_method_comparison.csv已保存；旧五方法数据只引用，buyNow TPS留空。所有动态项目not_tested。raw_logs仅范围说明，未生成业务日志/receipt。
- 构建单元已退出；未执行测试binary或guest，没有正式负载；未修改网络/代理配置。
- 下一条只读命令：`cat CVW/experiments/instance-lifecycle/step-21c-exchange-cross-contract/README.md`。后续按用户安排独立Step21B，不能自动解除Skip或恢复压测。

## 最终保存检查

脚本语法、源文件只新增测试、go test -c退出0、guest入口无条件Skip、六方法矩阵exchange留空均已检查。仅在experiment/step21c-exchange-real-fixture归档，不push。构建单元已停止。下一步只读README，等待独立Step21B结论。
