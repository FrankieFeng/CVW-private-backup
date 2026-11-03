# Step-39A WASM Artifact 热路径验证

结论：**仅优化SHA**，通过管理器持有的不可变Artifact复用内部摘要；保留每次输入内容校验。暂不推进仅消除Runtime Clone，也不将组合组当成最优配置。

## 实际基线与范围

父提交93c3bea0（Step-38），Guest/安全Owner来自Step-36 abc2ce35，节点依赖c28bfa8。独立分支experiment/step39a-wasm-artifact；Go1.25.0/WSL2。原native/Selector补丁库SHA256 `56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc`，每个业务进程检查实际maps。未运行节点、未改生产VM、未启用Arena A、未改Copy C0、Gas、Guest、Owner或native补丁。

本轮字母A/B/C/D表示Artifact实验组，**不是Arena A优化**。全部为Fresh+Copy C0。A+Copy的Artifact增量未独立测量，不能从这些数字直接给出其节省值；被消除的两次全WASM摘要位于_start之前，是否传递到完整A+Copy仍需同条件验证。

## 四组定义

- A：原Clone、Invoke两次全WASM SHA、Prepare一次全WASM SHA；增加统一短计时观察，非Step-38旧样本。
- B：每次仍Clone；Artifact缓存内部摘要；Invoke保留输入SHA，Prepare复用摘要。登记/命中验证成本计入Runtime创建，不在窗口外免费准备。
- C：Artifact持有私有快照，Runtime引用它，避免每次Runtime Clone；**保留原三次全WASM SHA**。
- D：B+C。Artifact首次登记仍有一次拥有权Clone及一次SHA，后续登记命中仍逐字节比较，不直接信任名称/版本。

## 有界设计与计时

3方法×4组×3独立批次×2正式调用=72次正式调用；每进程最多2正式区块，另2次业务预热。另有12进程功能预检、48目标调用，逐字节检查完整初始Memory。正式样本不扫描整Memory。3方法×2组×3批×2次=36次关闭新增成本插桩的补充调用，独立统计。每组6个配对样本来自3批，**不是6个独立实验批次**。预热/部署/编译/模板首次生成不进入正式统计，全部原始记录保留。固定输入、初始账本及TxID配对，组间轮转/反向顺序（有限平衡，见下述顺序限制），未加业务Sleep或强制GC。

Factory Invoke=实际依赖vm_factory.go:432至436，包含输入校验、Owner及其Close，**不包含根Runtime创建/Clone**。RunContract是既有夹具同进程单调时间，包含根Runtime创建；不等于SDK E2E，未计入根GetContractBytecode的夹具Clone。buyNow六次真实下游调用嵌套于根Factory范围，包含子Runtime创建，不能把七个完整Invoke相加。

## 主实验（ms，完整Factory Invoke）

| 方法 | 组 | Factory P50 | P95 | 相对A配对节省 | 95%探索CI | 批1/2/3节省 |
| --- | --- | --- | --- | --- | --- | --- |
| compute_hashCal | A | 11.436 | 12.487 | — | — | — |
| compute_hashCal | B | 8.497 | 8.965 | 2.933 | [2.153, 5.155] | 4.431/2.619/2.470 |
| compute_hashCal | C | 12.021 | 13.144 | -0.635 | [-1.642, 1.304] | -0.169/-0.873/-0.450 |
| compute_hashCal | D | 8.824 | 10.409 | 2.450 | [1.897, 3.005] | 2.451/2.270/2.551 |
| exchange_buyNow | A | 70.079 | 77.731 | — | — | — |
| exchange_buyNow | B | 49.778 | 53.773 | 18.530 | [10.851, 29.978] | 15.985/28.940/15.734 |
| exchange_buyNow | C | 81.710 | 89.133 | -9.483 | [-20.115, -5.443] | -12.779/-9.125/-9.483 |
| exchange_buyNow | D | 55.086 | 61.616 | 16.934 | [7.163, 27.322] | 11.664/27.322/12.433 |
| bigInput_inputSize | A | 8.817 | 11.310 | — | — | — |
| bigInput_inputSize | B | 5.814 | 6.205 | 3.123 | [1.993, 5.250] | 4.578/3.745/2.407 |
| bigInput_inputSize | C | 10.622 | 12.698 | -1.805 | [-3.779, 1.985] | 0.318/-2.574/-3.010 |
| bigInput_inputSize | D | 7.077 | 8.039 | 2.031 | [0.960, 3.858] | 2.957/2.794/0.960 |

每组N=6、3批。正值=原组减优化组。CI按批次聚类、有放回抽3批再在各批抽2槽，10000次bootstrap，SHA种子固定；P95线性插值。配对依据同case/batch/slot，而不是独立中位数相减。3批及6对不足以证明尾延迟稳定性，未作多重比较校正，均为探索性证据。主矩阵三批不能覆盖四组所有位置；hashCal主实验B始终在A之后，存在顺序混杂。独立lean A/B对照才明确交换先后，分层结果见ORDER_EFFECTS.csv；3批不足以单独估计顺序效应。

## 关闭新增成本插桩的独立补充（ms）

| 方法 | 原路径P50 | 缓存摘要P50 | 原/优化P95 | 配对节省 | 95%探索CI | 正向比例 |
| --- | --- | --- | --- | --- | --- | --- |
| bigInput_inputSize | 9.361 | 5.774 | 10.261/7.380 | 3.455 | [2.714, 3.902] | 1.0 |
| compute_hashCal | 11.199 | 8.382 | 12.242/11.127 | 2.727 | [-0.021, 3.693] | 0.8333333333333334 |
| exchange_buyNow | 65.762 | 46.875 | 71.393/58.703 | 19.395 | [5.888, 25.392] | 1.0 |

补充版删除Step-39各阶段time.Now/计数append/成本JSON输出；保留原Owner/资源日志和原Factory窗口。这是另一二进制、另一组新样本，不能与主实验合并，也不是无日志的生产基准。hashCal补充Factory CI略跨零，必须保留；其3批中位方向均正，RunContract CI为正。不能声称三个方法均已严格证明稳定加速。完整数据见LEAN_EFFECTS.csv。

## 七项回答

1. **三次全WASM SHA中有两次可摊销**：内部快照摘要与Prepare键摘要。每次Invoke传入内容的身份检查仍做一次SHA，没有删除必要校验。Template restore的小身份键SHA及冷解析/编译验证均未修改，不是“三次SHA涵盖整个VM全部SHA”。
2. 必须保留输入与快照绑定、Module配置/身份、Template绑定校验；缓存只能替代对已拥有且未变内部字节的重复摘要。哈希不是授权部署/升级的替代机制。
3. Runtime Clone在私有Artifact所有权下可避免，**不能直接借外部可变切片**。C/D确实减少Go分配，但本轮未得到性能增量支持；C的buyNow明显回归。不能凭复制字节数减少就预言提速，也未证明回归由cache/带宽造成。
4. Artifact应放在safe Manager的纯Go层，位于Runtime对象创建之前，独立于Store/Module native所有权；按chain/config/name/version区分，再核对完整内容，保存实际摘要。Module键继续包含摘要、配置及Copy选择。首次登记与升级创建新私有快照，旧引用保持有效；同版本不同内容不当作命中。
5. 主实验B完整Factory配对节省：hashCal2.933ms、buyNow18.530ms、bigInput3.123ms；D分别2.450/16.934/2.031ms。上述独立补充B为2.727/19.395/3.455ms，不能拼为一个估计。Clone根窗口不在Factory内，必须同时看RunContract与子调用。
6. 值得在保持既有安全门槛下，**下一轮有限验证仅SHA方案**，不自动启动E2E。本轮是VM夹具，不是节点收益；需验证真实升级/Manager Reset/缓存容量及准入，再做小规模客户端配对，不能运行37方法矩阵来替代准入。
7. 不优先转向WASI：两次大输入SHA有可行动的阶段性收益，先确认SHA真实节点传递。WASI Builder/Tokio作为后续备选，不能凭Step-38带扰动表立即修改其生命周期。

## 正确性、资源与局限

Gas/返回值/事件/读写集/初始及最终账本摘要在四组全部一致；逐层Gas也一致，buyNow确实7次Invoke（根+6子）。所有受监控的67个进程正常退出，Store/Instance配平、pending=0。RSS峰值557.062MiB，线程峰值41，未触及1536MiB/220线程软阈值。纯Go Artifact读并发Race通过，不代表native并发安全。

三根WASM仅4.23–4.58MB，不能外推全部体积；bigInput是真实512KiB输入。Artifact额外长期持有一份每合约字节快照，B热态仍Clone，RSS不能与Go分配减少等同。原Fixture BlockVersion=1/gasUsed=0，非Step-36真实节点完整上下文，绝对Gas不应与节点结果直接比较。真实Table函数身份、全部异常/回滚、长时间内存收敛以及真实节点升级路径未验证。本轮没有改变这些边界。

## 文件与复算

- SOURCE_AUDIT.md：实际三个路径、所有权及源码行号。
- BENCHMARK.csv：含预热/预检的原始逐调用汇总；主统计仅formal且verification=False、formal-*标签。
- COSTS.csv：逐Runtime阶段，root/child均保留；prepare_total、artifact_acquire为嵌套窗口，不能和其内部SHA/Clone相加。
- PAIRED_EFFECTS.csv / SUMMARY.csv：主实验配对与P50/P95。
- LEAN_SAMPLES.csv / LEAN_EFFECTS.csv：新增插桩关闭版独立证据。
- RESOURCE_SUMMARY.csv / CHILD_GAS_PARITY.csv / CORRECTNESS_CHECKS.csv。
- audit/：版本、依赖、库与WASM身份、完整diff、构建及校验命令。
- raw_logs/：所有日志、命令、实际加载maps、收据、退出结果。

只复算：`python3 scripts/analyze.py`。报告由`python3 scripts/report.py`生成。构建/运行命令已保存于audit及raw_logs，脚本有已有产物保护，不应为了重复计数覆盖有效运行。原始Step-38数据未修改；完成后停止，等待确认。
