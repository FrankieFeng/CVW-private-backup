# Step-21C：exchange.buyNow真实跨合约夹具准备

2026-10-26。按用户最新范围，**本轮只完成真实夹具源码准备、编译及静态验证；没有执行测试binary、WASM、功能交易或正式压测。** Step21B仅规划、尚未执行，以Step21A Store风险为边界，不再继续寻找分支。Step21C编号/目录保持独立。

## 已完成

- 审计三份实际WASM及源码；成功路径包含identity三个调用和ERC721三个调用，根+子预期7个Invoke、源码depth1。当前WASM确认6个静态CallContract点，动态成功/深度仍未验证。
- 准备真实VmManager/TxSimContext、三合约登记、内存账本、公开测试身份、实际初始化与成功/异常断言；所有callee业务由原WASM执行，未写固定响应或Mock成功。
- 记录真实读写集、事件、Gas、每层inclusive时间、逐交易状态hash的代码已准备；根失败不提交写集。恢复toolkit可查的初始化和buyNow输入规则，没有改合约或Gas。
- go test -p2 -c已成功，只编译/链接；必需WASM导出、冻结100行参数及唯一token检查通过。冻结100行只是保留产物，本轮没有运行100次。
- 新增guest测试入口第一条语句无条件t.Skip，避免未审计Store生命周期时误启。编译通过不等于功能、安全或Gas通过。

源码编译commit `d9f5390688d211f780b2bdb3c7bc251a1c1a43c4`，分支`experiment/step21c-exchange-real-fixture`，父fc3e90d；只新增_test.go，不改生产源码。完整差异source.patch；最终报告commit以分支HEAD为准。Go/OS/native和binary哈希见environment.json。未推送远程。

## 本轮状态

| 项目 | 状态 |
|---|---|
| 三WASM哈希、必需导出、六个静态跨调用点 | 已静态检查 |
| fixture编译/链接 | 通过 |
| 根/子真实业务执行、状态和事件 | not_tested |
| Gas一致性、Fresh不复用、Table | not_tested |
| Store安全与资源生命周期 | 待独立Step21B |
| 本轮业务样本/正式100次负载 | 0 / 未启动 |
| buyNow R0/R1 TPS与15.27倍率比较 | 缺失，不能生成 |

只检查源码中的expected输出，不会产生guest成功；实际运行必须同时检查根/全部子调用Code、读写集和状态，不能仅Go PASS或根字符串。身份提供器是VM层测试上下文，不认证节点签名、现代ACL、共识或真实数据库。SnapshotMock未实现项只对未用API保留显式失败，实际合约/状态查读已由新夹具实现；动态可用性仍需验证。

## 安全阻碍和下一步

Step21A已观察创建/执行粗粒度区间重叠；这不是已证实native race，但不足以允许原池负载。R1连续子调用之间，异步Close/grow仍可触碰同一个Store。多合约三个池还增加WASI线程/RSS预算压力。没有通过全局锁、修改Gas、伪造callee结果、禁用守卫或提高资源阈值绕过。

按用户安排，下一阶段应独立执行Step21B，核实同Store创建/执行/关闭与finalizer所有权、跨调用重入、资源回收及池退出。确认边界后，才可评审解除Skip并运行已准备的少量真实功能场景；再决定是否另行恢复正式3批100次。当前未提供任何自动压测命令，runtime-safety-plan.json只是原保护阈值记录，执行仍为false。

## 交付与只读恢复

- AUDIT.md：历史入口、源码调用链、原夹具缺失、参数上限0原因、状态/Gas/计时与生命周期。
- source/step21c_fixture_test.go、source.patch：已编译的真实业务夹具，入口禁用。
- fixture-manifest.json、inputs/、audit/artifact-exports.json：三WASM SHA及冻结参数。
- audit/compile.log、compile-command.json、static-validation.json、current-buynow-disassembly.txt：构建和静态证据。
- correctness.csv、summary.csv：动态项目not_tested，TPS留空。
- six_method_comparison.csv：复用Step21原五方法数据；exchange仍缺失，不以新静态检查冒充实测。原五方法为容量修复版VM层历史数据，ERC721/fact的复用Gas不一致，且Store安全尚未认证，不作生产收益。
- PROGRESS.md、state.json：每阶段进度与恢复入口。raw_logs/无新guest日志，仅有范围说明。

只读/静态命令：

```bash
cat PROGRESS.md
python3 -B scripts/static_readiness.py
python3 -B scripts/report.py
```

这些脚本不会执行测试binary或guest。scripts/compile_only.py只输出/执行构建命令并拒绝覆盖已有binary；原实际完整命令见audit/compile-command.json。不要运行整个测试包来代替构建检查，父分支其他TestInvoke入口不是本轮执行范围。

所有构建单元已退出。未修改代理、Clash或VSCode配置，未覆盖旧实验。回滚仅弃用Step21C独立分支/二进制；不要reset/clean生产脏工作区。
