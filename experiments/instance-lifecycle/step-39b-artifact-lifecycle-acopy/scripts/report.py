from pathlib import Path
import json,csv,statistics as st,difflib,hashlib,re
P=Path(__file__).resolve().parents[1];R=P.parents[2];V=P/'source/vm';BASE=R/'experiments/instance-lifecycle/step-39a-wasm-artifact/source/vm'
def rd(n):return list(csv.DictReader((P/n).open()))
def fmt(v):return f'{float(v):.3f}'
def table(h,rows):return '| '+' | '.join(h)+' |\n| '+' | '.join('---'for _ in h)+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n'for r in rows)
ss=rd('SUMMARY.csv');ee=rd('PAIRED_EFFECTS.csv');resources=rd('RESOURCE_SUMMARY.csv');main=[r for r in rd('RESULTS.csv')if r['run'].startswith('formal-')and r['phase']=='formal']
assert len(main)==72
cases=['compute_hashCal','exchange_buyNow','bigInput_inputSize'];summary=table(['方法','配置','N/批次','Factory P50/P95 ms','RunContract P50/P95 ms'],[[c,g,'6/3',next(fmt(r['p50'])+'/'+fmt(r['p95'])for r in ss if r['case']==c and r['group']==g and r['metric']=='factory_invoke_ms'),next(fmt(r['p50'])+'/'+fmt(r['p95'])for r in ss if r['case']==c and r['group']==g and r['metric']=='runcontract_ms')]for c in cases for g in ['G0','G1','G2','G3']])
paired=table(['方法','直接对照','Factory配对节省 ms','探索性95%CI','三批节省 ms','正向比例'],[[r['case'],r['left']+'→'+r['right'],fmt(r['saving_median']),f"[{fmt(r['ci95_low'])}, {fmt(r['ci95_high'])}]",'/'.join(fmt(r[k])for k in ['batch1','batch2','batch3']),r['positive_fraction']]for r in ee if r['metric']=='factory_invoke_ms'and (r['left'],r['right'])in [('G0','G1'),('G2','G3')]])
(P/'README.md').write_text('''# Step-39B：SHA Artifact生命周期与Arena A+Copy验证

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

'''+summary+'''
'''+paired+'''
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
''')
(P/'LIFECYCLE.md').write_text('''# Manager范围缓存生命周期验证

## 唯一治理策略

Manager内8项/64MiB有界缓存，满即明确拒绝；无LRU、无后台淘汰、无native共享新机制。registry key为(chain,config,name,version)，命中仍bytes.Equal；首次/换内容owned Clone+SHA，不直接共享外部切片。Artifact本身仅key/raw/digest。Module仍按原含内容SHA/配置/Copy的完整键缓存，原Module8项限制保持。

正常Runtime创建沿InstancesManager.NewRuntimeInstance→safe.runtime。外部调用在原Owner.mu下核对closing/resetting/poisoned/原请求预算并完成Go登记/Clone；不改Owner实现。同Owner回调允许已接收根调用继续创建子Runtime，Stop排空前registry保持可用。Owner.Reset/Stop既有排空后调用clear，原native清理完成后detach registry：Reset清空并允许下次登记，Stop清空且closed永久置位。外部Go登记与生命周期状态变更使用同一Owner admission互斥，避免Stop清理后再登记。

prepare失败时discard只移除“该key仍指向该Artifact”的条目；旧失败Runtime不能误删后来替换的新内容。原native scope defer回滚仍负责native对象；Artifact不保存native引用。失败的输入/编译不会永久占用新的registry槽位，已有Module缓存不会因Artifact删除而被在途关闭。

## 场景及实际证据

| 场景 | 实测/源码证据 | 结论及边界 |
|---|---|---|
| 首次/命中 | TestStep39BRegistry；diag-{case}-G1/G3缓存事件 | 命中保留原快照，热调用无冷Clone/SHA |
| 合约/版本/链/配置 | TestStep39Artifact新二进制再次执行，另-race执行 | tuple隔离、不同内容摘要可核对；不是node多链运行测试 |
| 版本升级 | TestStep39BUpgrade，真实compute.hashCal metadata version变2.0.0 | 实际新Module及真实Guest执行；非SDK上链部署升级 |
| 同版换码 | 同测试将plain替换为既有同源A WASM | native缓存新增不同内容键，执行成功，原Module未错命中 |
| Manager Reset | 上述测试通过ResetAllPool→tracked35aReset→safe.reset | Go及native缓存清空，新Module/Store重建 |
| Stop与可回收 | Supplement UpgradeWeak，Manager仍KeepAlive | Stop新建/旧Invoke拒绝；弱引用自然GC释放，原始记录GC2次/约28MiB有界分配压力，未强制GC |
| 8项容量 | Registry第9个tuple拒绝；Reset后可登记 | 无自动淘汰；已有对象不受拒绝影响 |
| 64MiB预算 | TestStep39BByteBudget，两个32MiB条目后第三条拒绝；另验证单个超64MiB直接拒绝 | 计数8/字节64MiB双界；拒绝前不创建新的owned Clone |
| 旧Runtime与替换/清理 | TestStep39BPinnedLifetime：Owner job已接收并暂停，主线程登记同版新内容，然后旧请求执行；Reset后再执行保留Runtime | 老快照保持有效、新实例仍Fresh；这里“清理”是显式Reset，没有虚构LRU淘汰 |
| 并发只读 | Registry8读者各20次创建不同Runtime；-race通过 | 只证明Go registry/不同Runtime只读，不证明同一Runtime并发Invoke或native并发 |
| 失败回滚 | invalid-WASM及diag after_compile Go故障，随后恢复真实调用 | 错误没有吞掉；Artifact删除及native scope回滚，最终计数配平 |
| Reset+Stop | TestStep39BResetStop，真实Owner已接收job，Reset拒绝新Runtime、Stop等待；已接收job执行真实hashCal | 原日志顺序显示Stop requested在Reset完成前，无Sleep；幂等Stop成功 |
| Stop中的真实跨合约 | TestStep39BDrainBuyNow：Stop置closing后才释放已接收root job，完整6子调用执行 | 外部新Runtime拒绝，已接收业务成功，结果/RWSet/事件/账本与正常预检逐字相等 |

以上原始生命周期check字段在LIFECYCLE_CHECKS.csv；新并发读及独立Race日志分开保存。角色为Manager/Owner的VM测试，不称为真实节点生命周期认证。

## 内存和所有权

8项/64MiB是registry raw的强引用上界，不是包括调用方/Runtime/natives的进程总上界。替换时旧快照可能被旧Runtime合法持有，Go引用保活避免悬空；B仍每Runtime持有独立Clone。新旧快照瞬时并存和在途请求需由既有请求预算/1536MiB守卫限制，不把缓存字节限制说成全局内存预算。

Reset/Stop解除registry引用，不在Go调用方仍合法持有时强行清零raw；这会破坏旧请求。Artifact无Store/Module/Instance/WASI字段，不关闭native对象。Native关闭仍只经原Owner作用域/Finalizer协议；本轮没有重写或绕过它。

自然GC验证只作功能诊断，分配压力在独立进程中有界，未参与性能数据，没有调用runtime.GC/FreeOSMemory、Sleep或更改GC参数。它证明可回收性，不能证明RSS立刻回落或长时间无泄漏。

源码准确文件/行号见audit/SOURCE_FUNCTIONS.csv，代码差异audit/runtime.patch。Owner、编译器、Copy及wasmer-go生命周期文件SHA与39A完全一致。保留原Owner总请求上限32及原native缓存8项；达到上限需结束隔离批次/显式Reset相应缓存，不能擅自扩大守卫。Owner总调用预算不能通过Reset刷新。
''')
(P/'CORRECTNESS.md').write_text('''# 正确性与隔离

- 预检12进程×四目标调用，所有根/子Instance初始Memory与原Image逐字节相同；正式阶段不扫描，Copy原C0未修改。
- 四组3方法正式72次调用，按同case/batch/slot比较Gas、完整Result、事件、RWSet与初始/最终账本hash，全部一致；三批54？实际逐层比较以CHILD_GAS_PARITY.csv为准，不将生命周期测试混入性能N。
- buyNow每笔根+6真实子调用，正式每组6笔全部为7条invoke_end；没有用Mock子返回或空方法代替。各层gas/调用顺序也逐条相同。
- 输入SHA仍每Invoke执行；补充TestStep39Reject在本轮二进制验证不同内容/版本拒绝。输入读取期间仍要求调用方不并发写入，未声称外部[]byte天然不可变。
- 同版本换码/版本升级/保留旧Runtime实际执行/Reset后新Module及Store/Stop后拒绝都通过；案例见LIFECYCLE.md。
- Stop中的buyNow收据，与pre-exchange_buyNow-G3/formal0具有相同TxID、Gas/完整Result/RWSet/初始最终账本，audit/drain-buyNow-parity.json通过。原日志中Stop requested先于root开始，最终cache close晚于root及6子执行完毕。
- Owner/wasmer-go Store/Instance/WASI/Finalizer/Compiler/Copy文件不变；只在独立实验目录加Go Artifact治理及观测/测试。native库及加载路径保持原Selector修复版。

边界：这是VM夹具，不是SDK部署/链上升级/提交确认。BlockVersion1、gasUsed0等与Step36真实节点上下文不同。未验证真实Table函数身份、全部业务异常/回滚、同Runtime并发调用、长期节点运行；原安全Owner串行协议不放宽。

原始失败保留：初次diag编译因新测试未使用变量失败，修正后另建diag-r1。一次补充测试源码复制路径错误导致diag-r2仍为旧测试版本，未用于正式性能或新增检查；修正后diag-r3/r4/r5依次用于明确标记的补充验证。没有业务失败、native崩溃、资源守卫触发或样本删除。编译时测试文本快照与SHA另存audit/frozen-tests；各二进制与命令一一保留。
'''.replace('三批54？实际逐层比较以','逐层比较以'))
(P/'NEXT_STEP.md').write_text('''# Step-39C有限节点E2E建议：可条件准入，当前不启动

本轮缓存生命周期/正确性通过，G2→G3在三个方法上探索性收益为正且无明确严重回归，因此建议进入下一轮有限节点E2E。它是下一轮实验方案，不是宣称节点集成已完成或可以生产运行。

进入前最小条件：

1. 在独立节点实验构建仅接入本轮SHA-only及Manager有界治理，保留Runtime Clone、输入SHA、Copy C0、原Owner/Selector/Core drain/Gas。核对实际加载库及源文件SHA。
2. 对实际节点Manager Reset/Stop、真实部署升级和同版换码作少量Smoke，检查缓存容量拒绝能返回明确错误；旧Module不能被提前释放。VM夹具手工改metadata不替代节点部署升级语义。
3. 固定同源A/非A WASM、SDK提交确认路径、等价初始账本与业务输入；先只做有限同方法G0/G1或G2/G3，不扩37方法，保留失败/反向样本。
4. 根Runtime创建/Clone在Factory之外；同时记录SDK/RunContract/Factory边界，避免把准备成本移动到窗口外当作净收益。
5. 原Owner总根调用预算32不变，init/setup/warmup也需计入；按需部署buyNow依赖，达到预算结束进程，不提高限额。保持1536MiB/220线程及关闭/排空检查，剩余margin不足就停止。

当前不需要为E2E扩大为LRU或重构Owner，也不据此启动WASI/Tokio新研究。HashCal无A对照CI跨零，不承诺所有合约稳定获益。下一轮若性能收益未传递到客户端再记录结论，而不是追加无界负载。

完成本轮后停止，不自动开始Step-39C、不推送远程。
''')
# source index and exact patch, preserve historical source line endings/hashes.
paths=[V/'step39_artifact.go',V/'step39b_cache.go',V/'step35_node.go',V/'step39b_lifecycle_test.go',V/'vm_instances_manager.go',V/'step35a_control.go']
index=[]
for f in paths:
 for i,line in enumerate(f.read_text().splitlines(),1):
  if re.match(r'func |type |const ',line):index.append({'path':str(f),'line':i,'definition':line,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
with(P/'audit/SOURCE_FUNCTIONS.csv').open('w',newline='')as f:w=csv.DictWriter(f,list(index[0]),lineterminator='\n');w.writeheader();w.writerows(index)
names=['step35_node.go','step39_artifact.go','step38_driver_test.go','step39b_cache.go','step39b_flags.go']
(P/'audit/runtime.patch').write_text(''.join(''.join(difflib.unified_diff((BASE/n).read_text().splitlines(True)if(BASE/n).exists()else[],(V/n).read_text().splitlines(True),fromfile='Step39A/'+n,tofile='Step39B/'+n))for n in names))
assert all(hashlib.sha256((V/n).read_bytes()).digest()==hashlib.sha256((BASE/n).read_bytes()).digest()for n in ['step34_owner.go','step21d_compile.go','step35_static.go','wasmer-go/managed.go','wasmer-go/store.go','wasmer-go/instance.go','wasmer-go/wasi.go'])
print('Reports saved')
