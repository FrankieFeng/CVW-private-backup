# Step-25：A/B1/Copy组合收益验证（串行筛选）

独立分支`experiment/step25-ab-copy-screening`，父`570b06a`。以Step22/24B固定owner、独立Store的串行参考管理器为基线，不改生产VM、原池或Gas，不push。可直接用于组会的表格和结论优先见[PPT.md](PPT.md)；完整结果在[RESULTS.md](RESULTS.md)，条件与实现见[AUDIT.md](AUDIT.md)。

## 配置与版本

G0 Baseline Fresh；G1 Copy；G2 A+Copy；G3 B1+Copy；G4 A+B1+Copy。

- A：Step18原型，添加可达静态padding并由Go链接器修正引用，使首次arena预留对齐。不是改initial memory到128页，不改Go Runtime清零算法本身。P0/P1的padding历史上分别重新计算。
- B1：本轮**明确限定为历史恢复的PB依赖裁剪补丁**，删除SDK0.1.3的GetBatchState公共接口/实现以及PB导入；不是把任意B1优化与PB自动视为同一件事，也没有另造一个实现。对现有不使用该API的方法成立，不是通用SDK兼容方案。
- Copy：原22/24B Data解析→模板/noData→新Instance→restore→WASI.Initialize/_start，替代原active Data初始化，无重复原始Data初始化。每个最终WASM单独模板，Key绑定hash/配置/合约版本。

宿主Go1.25.0、Guest Go1.24.1、ChainMaker VM/protocol2.4.0、原6.0.1 native（SHA固定）。源码提交、构建binary与WASM SHA见MATRIX.csv、environment.json、audit/delivery.json；SDK补丁/历史证据见audit/step18。所有正式用build2，同一宿主代码和Gas配置。

**主矩阵使用Step18同源plain家族**；compute.bigNumCal为10000轮，Step24B原件为100轮。normalCal仍10000000轮。未临时改业务计算量，未重编译或手改这些WASM。Step24B的90对原CSV已独立复算确认0.6696525/0.7496765/0.711377ms；不能将不同二进制家族的绝对耗时直接相减。三其他合约/业务输入也全部逐组固定，参见MATRIX及逐笔receipt。

## 设计与计时

先预检四条G0直接对照以及G2/G3/G4各自Copy off/on，再对通过配置扩大。正式8条直接对照：G0→G1/G2/G3/G4、G1→G2/G3/G4、G2→G4。每条每方法3独立批×6对，6对由3个独立进程各2对组成；每角色独占Store+Module，每次Fresh，最多init+2正式Instance，不持久连续100次。

对内交替、跨进程平衡Module准备/init顺序，第二批倒转对照和方法顺序；无100ms Sleep。所有进程、失败、冷态调用都保留。统计只取正式成功配对，不用预检中的S1 SHA开销当性能结果。95%CI为批次→进程聚类bootstrap（10000，seed250027）；每进程2对视为一个相关簇，非18次完全独立实验，多重比较未校正。

每条样本记录NewInstance、Copy字节/范围/时间、S0→S1、S1→S2、S2→S3、CallMethod、原有exportFunc.Call计时、关闭及Full Invoke。Full Invoke含创建/start/业务/同步关闭；模板、Module准备、真实init、账本clone、receipt输出及末尾持久缓存关闭在外。Module prepare含验证/Store/metadata，不是纯编译器时间。所有准备/关闭成本单列MODULE_PREPARATION.csv。各层嵌套不能相加，不通过Median相减构造增量；详见AUDIT。

init双方实际执行，从等价账本重置后每次目标调用使用同一输入/TxID，mint tokenId=1，每个目标调用前回到等价init账本；因此不是在同一账本重复mint同token。Gas/返回/RWSet/事件/账本均逐对检查，完整条件和未验证项见CORRECTNESS.md。

## 安全与限制

RSS768MiB/线程125软限，2GiB/256task硬限，45s Go/60s进程超时，available≥8GiB/swap≤1GiB，未提高预算。fixed OS owner/ManagedScope guard保留，每次同步close；禁止原池后台创建/异步关闭、共享Store并发和全局锁绕过。进程结束检查created=closed、managed/pending=0、PID/cgroup退出。

有限进程预算只是隔离长期WASI线程累积，未修复长期Store问题。Table真实函数身份、异常/OOG/真实跨合约、长期回收/并发均not_tested，不能据本轮筛选宣布安全生产或节点收益。五组没有R0，不能重新判定历史normalCal Fresh/复用的反直觉现象是否仍然存在。

## 运行与恢复

```bash
cd /home/frankie/mygitprojects/.worktrees/cvw-step25/experiments/instance-lifecycle/step-25-ab-copy-screening
# 只复算已有数据（无Guest执行）
python3 -B scripts/analyze.py
python3 -B scripts/write_report.py
# 原运行命令，已有outcome复用，不重复运行；新失败保留STOP。
python3 -B scripts/suite.py preflight-primary
python3 -B scripts/suite.py formal-primary
python3 -B scripts/suite.py preflight-normal
python3 -B scripts/suite.py formal-normal
```

开始前读PROGRESS/state和活动systemd unit，不重复partial label；不要删除STOP或放宽阈值。输入WASM已保存在inputs，native库和Go workspace其他依赖仍依赖原CVW本机环境；`.so`不入Git，hash在environment。构建用`python3 -B scripts/build.py 新label`，新binary需独立记录/核对，不覆盖原build/outcome。原脚本固定build2是为了重用已有结果，不自动切换到新binary。

关键交付：PPT、RESULTS、MATRIX、TIMING、PAIRED_SAMPLES、PAIRED_EFFECTS、BATCH_EFFECTS、ORDER_SENSITIVITY、STAGE_EFFECTS、RESOURCE_SUMMARY、MODULE_PREPARATION、CORRECTNESS以及raw_logs。每个进程的argv/env/binary hash和receipt全部保存。

回退：停止本实验unit并离开独立worktree；无生产VM、服务或Gas配置需要回滚。保留原始数据，不删除历史，不推送。

## 重要补充：不是相同Guest计费基线

Step18家族在本轮五组之间Gas完全相等，但其compute/fact/ERC的120027/154/235与原24B的105920/1585/15677不同。具体Guest计费插桩覆盖来源尚未完全恢复，不能只用Go版本号相同宣称原件构建等价。主矩阵属于Step18家族的组合筛选；24B原件上的A/B1组合仍未验证。另执行原24B WASM三方法G0/G1参考，保存在REFERENCE_EFFECTS/REFERENCE_PAIRED_SAMPLES，逐过程phase=reference。不得把参考样本拼入组合矩阵，或用两家族Gas/性能直接相减。参考复算由同一analyze脚本完成，运行入口scripts/reference_suite.py。

原24B WASM参考使用相同业务参数，固定TxID采用Step25格式；ERC本轮Gas15981、旧24B为15677。它不是Copy开关导致的Gas差异，本轮两侧完全相等；跨二进制家族的Guest计费来源仍未对齐。

## 最终问题的回答

1. **Copy是否复现？** Step18家族三个优先方法均为三批正向、总体CI在零以上。原24B WASM独立参考中compute/fact分别节省0.688/0.956ms、区间为正；ERC节省0.704ms但CI跨零，不能据18对称其稳定。
2. **A叠加是否更快？** 主矩阵三个优先方法相对Copy直接节省0.711/0.957/0.966ms，三批正向；normalCal为−0.394ms、CI跨零。仅限此Guest家族。
3. **B1叠加是否更快？** 不普遍。compute −0.230ms、fact +0.182ms均CI跨零；ERC −0.252ms，CI在零以下，三批负向。
4. **完整组合是否优于Copy？** 主矩阵三个优先方法直接节省1.799/1.128/1.089ms，三批正向；normalCal −0.270ms、CI跨零。B1在A+Copy基础上的增量独立由G2→G4给出，不由两条Median相减。
5. **normalCal反直觉现象？** 本轮无R0，无法复核Fresh/复用方向。组合对Fresh的净增量不稳定；A约1ms启动节省可被Guest export窗口波动抵消，不归因某具体缓存/调度机制。
6. **批次/顺序？** 上述三短方法A和完整组合正向跨3批；PB单独不普遍成立。ORDER_SENSITIVITY完整保留先后/Module顺序分层与CI，不能把平衡总体结论写成顺序无关。
7. **Gas/语义？** 662个有效配对（含预检/独立原件参考）对内一致。两个家族Gas绝对基线不同，不能混称同一构建；接口兼容、Table/异常等限制不因Gas相等解除。
8. **下一步节点？** 这些是有界串行筛选，不能直接支持原池并发Fresh节点压测。可优先保留SDK API的A+Copy研究路线；完整组合虽在主矩阵短业务更快，SDK删API限制需单独解决。先恢复原24B家族匹配A/B1构建/计费来源，再做相同家族确认及有限功能验证，不能把这里的毫秒收益称为节点收益。
