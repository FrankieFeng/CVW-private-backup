# Step-39B：SHA Artifact生命周期与Arena A+Copy验证

**结论：有界VM实验的缓存生命周期检查通过；SHA-only叠加Arena A+Copy在三个方法上均观察到正向增量，建议准入下一轮有限节点E2E，不自动启动。** 这不是生产安全认证或节点性能结论。

## 基线与四组

父提交0dd9f76e，独立分支experiment/step39b-artifact-lifecycle-acopy。原Step-35C安全Owner/Selector库/Compiler/Gas/Guest/Copy C0未改；host Go1.25.0，Guest为已确认Go1.24.1同源padding构建，无PB、B1或initial128页。冻结10份唯一WASM，含buyNow identity/ERC721下游，见audit/wasm-variants.json及padding-provenance.json。compute沿Step18旧产物；identity/exchange沿Step28同源码重建plain/A；bigInput沿Step33同源码plain/A，不把这些重建文件冒充Step18旧二进制。

- G0：Fresh+Copy C0。
- G1：G0+SHA-only，仍每次Clone，仍校验传入字节码SHA。
- G2：Fresh+Arena A+Copy C0。
- G3：G2+SHA-only。

## 七项结论

1. **生命周期闭环**：在本轮安全Fresh、有限请求路径内通过。升级、同版换码、真实旧Runtime请求、Manager Reset/Stop、错误回滚、并发只读、缓存引用释放均有实测；不外推长期/节点并发或全部业务异常。
2. **容量**：只采用Manager生命周期内有界缓存，最多8项且缓存raw总量≤64MiB；满时明确拒绝，不自动LRU。Reset清Artifact与Module；Stop排空后清理并永久关闭registry。没有同时引入多种缓存策略。
3. **升级/Reset/Stop**：通过实际VM Manager +真实WASM业务路径验证，非SDK链上升级测试。旧Artifact不修改、不持native资源；旧Runtime跨替换和Reset后仍能创建Fresh Store/Instance执行。Stop后新Runtime和已持有Runtime的Invoke均拒绝。弱引用检查在自然GC下看到Artifact释放，Manager仍被KeepAlive。
4. **Arena A+Copy增量**：G2→G3的Factory配对节省中位数：hashCal3.187ms、buyNow20.991ms、bigInput3.510ms，三批中位数均正，探索性CI均>0。
5. **方法差异**：buyNow根+6真实下游受益更大；不能把七个嵌套完整Invoke相加。不带A的hashCal仍有反向样本，Factory及RunContract探索性CI跨零，保留不确定性。
6. **额外开销**：SHA-only仍Clone且增加完整内容比较/缓存登记；常驻一份每key私有WASM会增加Go内存。某些Runtime创建窗口变慢，例如buyNow G2→G3该窗口配对“节省”为−0.323ms，CI[−0.628,−0.255]；整体Invoke收益已包含该代价。没有发现本轮正确性失败或资源守卫触发。
7. **下一步**：建议仅在原安全Owner、相同C0、预算内进行Step-39C有限节点配对；本轮没有运行节点或E2E。先检查实际节点构建/缓存集成/交易确认口径，再调用；不能把这份VM测试当作节点已准入或性能已确认。

## 正式性能（全部样本，不删反向值）

| 方法 | 配置 | N/批次 | Factory P50/P95 ms | RunContract P50/P95 ms |
| --- | --- | --- | --- | --- |
| compute_hashCal | G0 | 6/3 | 12.393/13.814 | 14.206/15.805 |
| compute_hashCal | G1 | 6/3 | 9.181/11.408 | 10.471/12.998 |
| compute_hashCal | G2 | 6/3 | 10.962/13.307 | 12.551/15.588 |
| compute_hashCal | G3 | 6/3 | 7.736/8.955 | 8.779/11.212 |
| exchange_buyNow | G0 | 6/3 | 69.136/74.265 | 69.891/74.972 |
| exchange_buyNow | G1 | 6/3 | 51.691/55.962 | 52.775/57.166 |
| exchange_buyNow | G2 | 6/3 | 64.569/69.424 | 65.144/70.056 |
| exchange_buyNow | G3 | 6/3 | 46.980/54.230 | 47.978/55.342 |
| bigInput_inputSize | G0 | 6/3 | 9.275/9.755 | 10.111/10.497 |
| bigInput_inputSize | G1 | 6/3 | 5.860/7.044 | 7.380/8.530 |
| bigInput_inputSize | G2 | 6/3 | 8.350/10.353 | 9.363/11.066 |
| bigInput_inputSize | G3 | 6/3 | 4.870/5.609 | 6.027/6.697 |

| 方法 | 直接对照 | Factory配对节省 ms | 探索性95%CI | 三批节省 ms | 正向比例 |
| --- | --- | --- | --- | --- | --- |
| bigInput_inputSize | G0→G1 | 2.881 | [2.272, 4.378] | 3.684/3.054/2.522 | 1.0 |
| bigInput_inputSize | G2→G3 | 3.510 | [1.457, 5.768] | 2.304/4.137/4.718 | 1.0 |
| compute_hashCal | G0→G1 | 2.795 | [-0.169, 4.959] | 0.970/4.876/2.754 | 0.8333333333333334 |
| compute_hashCal | G2→G3 | 3.187 | [2.608, 5.946] | 4.214/3.283/3.187 | 1.0 |
| exchange_buyNow | G0→G1 | 21.090 | [4.093, 23.429] | 6.471/21.990/22.184 | 1.0 |
| exchange_buyNow | G2→G3 | 20.991 | [5.135, 28.568] | 20.991/16.852/16.335 | 1.0 |

正值=左组耗时−右组耗时；均基于同case/batch/slot直接配对，绝不是两个独立Median相减。3个独立批次，每批每组2正式调用（进程上限2配对槽），每组总6样本；6对不是6个独立批次。每进程有2次业务预热，冷部署/编译/首次模板不计主统计，原始记录仍保留。组顺序轮转/反向，两个主对照均有正反执行顺序，详见ORDER_EFFECTS.csv；3批不能完整识别顺序效应。

CI：SHA种子固定的10000次批次聚类bootstrap（抽3批，批内抽2槽），分位数95%探索区间；P95线性插值。样本少、未做多重比较校正，不能把正CI当作所有负载下稳定提速的证明。RunContract配对CI、阶段时间、分配与顺序细项在PAIRED_EFFECTS/SUMMARY/COSTS中。

## 计时口径

实际Factory依赖为.worktrees/cvw-step21c/chainmaker/chainmaker-vm-wasmer/vm/v2@v2.4.0/vm_factory.go:393–394创建Runtime；432–436计时Invoke，438打印REUSE_VM。根Clone在Factory窗口外但在RunContract内；子Runtime创建在根export/Factory内。RunContract用既有fixture单调时钟，Factory保留原UnixNano窗口，不改变边界。

运行版不在Invoke内输出新增SHA成本JSON，只记录短time.Now/小结构，结束后由测试驱动在f.run计时结束后输出；保留原基线VM/安全日志。诊断版只增加cache hit/replace记录及故障注入，6个诊断进程不进入主统计。不是无日志生产基准，仍有短计时开销。

SHA-on每Invoke保留一次全WASM输入SHA；prepare零次全WASM SHA，内部快照摘要复用。SHA-off为Invoke2次+prepare1次。buyNow每根交易7次Invoke，因此计数14→7、prepare7→0，Runtime Clone仍7次。短Template Key SHA、Guest业务SHA、冷验证未删除。

## 正确性和资源

四组Gas、返回值、事件、RWSet和初始/最终账本摘要完全一致；逐层Gas与六次子调用序列核对一致。预检逐字节比较所有根/子实例初始Memory，正式样本不加该扫描。完整明细见CORRECTNESS.md。

67个受监控进程均正常退出，其中60个native Owner进程Store/Instance配平、pending=0；峰值RSS552.848MiB、OS线程41，未提高1536MiB/220线程软线。快速纯Go Registry进程没采到/proc，标not_sampled，不填写0。库加载在所有真实业务进程maps核对，SHA56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc未变。

缓存64MiB限制只约束registry当前拥有的raw字节，不包含native Module、Runtime每次Clone、调用方输入与仍被合法旧Runtime持有的快照。它不是进程总内存限制。旧引用释放后Go可回收；不能将RSS不立即下降判为泄漏。原Owner每Manager根请求总预算32不变，Reset不扩大该预算。

本轮账本是VM夹具，BlockVersion1/gasUsed0，与Step-36完整节点上下文不同，绝对Gas/耗时不混用。Table真实函数身份、所有异常/回滚、长期内存平台和节点部署升级仍不因本轮而宣称通过。

## 数据和复算

RESULTS.csv有216行目标调用，含正式72、其余预检/预热/诊断；主统计筛run=formal-*且phase=formal。这些216行不等于216个独立实验。SUMMARY/PAIRED_EFFECTS/ORDER_EFFECTS为派生表。LIFECYCLE_CHECKS.csv、CHILD_GAS_PARITY.csv、RESOURCE_SUMMARY.csv分别保留生命周期与资源证据。raw_logs包含命令、收据、VM日志、maps及退出结果；audit含源码diff/Guest/native/构建身份。

只复算：`python3 scripts/analyze.py`、`python3 scripts/report.py`；不重跑性能。构建/运行命令逐份保存，已有有效结果不覆盖。性能二进制原件留在工作树binaries（不入Git），源码及哈希可复核；后补测试的编译时旧文本另存audit/frozen-tests，避免以当前扩展测试文本冒充原构建。未推送，完成后停止，不自动开始Step-39C。
