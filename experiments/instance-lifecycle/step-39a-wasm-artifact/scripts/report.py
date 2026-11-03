from pathlib import Path
import csv,json,hashlib,difflib,subprocess,re,statistics as st
P=Path(__file__).resolve().parents[1];R=P.parents[2];V=P/'source/vm';BASE=R/'experiments/instance-lifecycle/step-38-copy-range-cost/source/A/vm'
def rd(n):return list(csv.DictReader((P/n).open()))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def fmt(x):return f'{float(x):.3f}'
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+ ' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n'for r in rows)
effects=rd('PAIRED_EFFECTS.csv');summary=rd('SUMMARY.csv');lean=rd('LEAN_EFFECTS.csv');resources=rd('RESOURCE_SUMMARY.csv');bench=rd('BENCHMARK.csv')
main=table(['方法','组','Factory P50','P95','相对A配对节省','95%探索CI','批1/2/3节省'],[[case,mode,next(fmt(r['p50'])for r in summary if r['case']==case and r['mode']==mode and r['metric']=='factory_invoke_ms'),next(fmt(r['p95'])for r in summary if r['case']==case and r['mode']==mode and r['metric']=='factory_invoke_ms'),*( ['—','—','—']if mode=='A'else next([fmt(r['saving_median']),f"[{fmt(r['ci95_low'])}, {fmt(r['ci95_high'])}]",'/'.join(fmt(r[k])for k in ['batch1','batch2','batch3'])]for r in effects if r['case']==case and r['left']=='A'and r['right']==mode and r['metric']=='factory_invoke_ms'))]for case in ['compute_hashCal','exchange_buyNow','bigInput_inputSize']for mode in 'ABCD'])
lt=table(['方法','原路径P50','缓存摘要P50','原/优化P95','配对节省','95%探索CI','正向比例'],[[r['case'],fmt(r['A_p50']),fmt(r['B_p50']),fmt(r['A_p95'])+'/'+fmt(r['B_p95']),fmt(r['saving_median']),f"[{fmt(r['ci95_low'])}, {fmt(r['ci95_high'])}]",r['positive_fraction']]for r in lean if r['metric']=='factory_invoke_ms'])
(P/'README.md').write_text('''# Step-39A WASM Artifact 热路径验证

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

'''+main+'''
每组N=6、3批。正值=原组减优化组。CI按批次聚类、有放回抽3批再在各批抽2槽，10000次bootstrap，SHA种子固定；P95线性插值。配对依据同case/batch/slot，而不是独立中位数相减。3批及6对不足以证明尾延迟稳定性，未作多重比较校正，均为探索性证据。主矩阵三批不能覆盖四组所有位置；hashCal主实验B始终在A之后，存在顺序混杂。独立lean A/B对照才明确交换先后，分层结果见ORDER_EFFECTS.csv；3批不足以单独估计顺序效应。

## 关闭新增成本插桩的独立补充（ms）

'''+lt+'''
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

Gas/返回值/事件/读写集/初始及最终账本摘要在四组全部一致；逐层Gas也一致，buyNow确实7次Invoke（根+6子）。所有受监控的'''+str(len(resources))+'''个进程正常退出，Store/Instance配平、pending=0。RSS峰值'''+fmt(max(float(r['rss_peak_mib'])for r in resources))+'''MiB，线程峰值'''+str(max(int(r['threads_peak'])for r in resources))+'''，未触及1536MiB/220线程软阈值。纯Go Artifact读并发Race通过，不代表native并发安全。

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
''')
# Source inventory with exact current lines and hashes, including actual Factory dependency.
factory=Path('/home/frankie/mygitprojects/.worktrees/cvw-step21c/chainmaker/chainmaker-vm-wasmer/vm/v2@v2.4.0/vm_factory.go')
files=[V/'step35_node.go',V/'step39_artifact.go',V/'step39_artifact_test.go',V/'vm_instances_manager.go',V/'step35_static.go',V/'step21d_fixture_test.go',V/'step34_owner.go',factory]
idx=[]
for f in files:
 for i,line in enumerate(f.read_text().splitlines(),1):
  if re.match(r'func |type e39',line):idx.append({'path':str(f),'line':i,'definition':line,'sha256':sha(f)})
with(P/'audit/SOURCE_FUNCTIONS.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(idx[0]));w.writeheader();w.writerows(idx)
for name in ['step34_owner.go','step21d_compile.go','step35_static.go','wasmer-go/managed.go','wasmer-go/store.go','wasmer-go/instance.go','wasmer-go/wasi.go']:
 assert sha(V/name)==sha(BASE/name),name+' unexpectedly modified'
for f in [V/'step35_node.go',V/'step39_artifact.go']:
 orig=(BASE/f.name).read_text().splitlines(True)if(BASE/f.name).exists()else[];(P/'audit'/(f.name+'.diff')).write_text(''.join(difflib.unified_diff(orig,f.read_text().splitlines(True),fromfile='Step38/'+f.name,tofile='Step39/'+f.name)))
(P/'audit/lean.diff').write_text(''.join(''.join(difflib.unified_diff((V/name).read_text().splitlines(True),(P/'source/lean/vm'/name).read_text().splitlines(True),fromfile='timing/'+name,tofile='lean/'+name))for name in ['step35_node.go','step39_artifact.go']))
source='''# 三个热路径审计

实际Factory依赖不是就近目录推断，而是GOWORK + go list -m恢复：
`/home/frankie/mygitprojects/.worktrees/cvw-step21c/chainmaker/chainmaker-vm-wasmer/vm/v2@v2.4.0/vm_factory.go`。
其393–394行先调用NewRuntimeInstance；432–436行才开始/结束Runtime.Invoke计时，438行输出REUSE_VM。Factory不直接Clone，Clone由Manager.runtime执行。

| 原始操作 | Step-38原始位置（source/A/vm） | 输入/用途/输出 | 本轮可缓存部分/失效 |
|---|---|---|---|
| Runtime Clone | step35_node.go:91–95 runtime；vm_instances_manager.go:56–66转入safe.runtime | append(nil,raw...)，每Runtime快照，阻止调用方随后修改影响预期身份。克隆不是每次编译 | 管理器拥有的私有字节可复用；初次登记仍Clone。内容/版本/链/配置变化重新登记 |
| Invoke SHA×2 | step35_node.go:185–191 Invoke | nodeSHA(raw)与nodeSHA(r.raw)；不相等拒绝，防止Runtime与实际输入错配 | 保留输入SHA，缓存内部快照SHA；不能只比较名称/版本就接受内容 |
| Prepare SHA | step35_node.go:126–137 prepare | SHA(raw)进入chain/name/version/digest/config/copy键，每次命中也先计算 | 通过已校验的Runtime Artifact摘要复用键身份；版本、内容、配置变化产生其他键 |

Step-38冷prepare:177 source=nodeSHA(raw)还有一次SHA，仅在缓存未命中；prepareStaticMemory:97还算SourceSHA，232构建短身份Key，restore:237每次验证该短Key。它们不等于三次热路径全WASM SHA。原native ValidateModule/NewModule冷验证保留。新B/D冷source复用已确定摘要；A/C保留冷source SHA。没有修改Copy模板、Ranges或restore。

## 新原型调用链

vm_factory.NewRuntimeInstance → InstancesManager.NewRuntimeInstance → nodeFreshManager.runtime → B/C/D的e39Registry.acquire → nodeFreshRuntime.Invoke（输入SHA仍存在） → SafeFreshOwner.Do → invoke → prepare（B/D复用摘要） → 同Engine缓存Module → 真独立Store + WASI/Imports → NewInstanceInStore → C0 restore → Initialize → _start → CallMethod → 同步Close。

新主源码准确位置：step35_node.go runtime:97，prepare:136，Invoke:198；step39_artifact.go acquire:50，hash:44；测试位置见audit/SOURCE_FUNCTIONS.csv。修改全部限制在本实验source目录。

## 不可变性的证据与边界

acquire对外部字节只读，以tuple(chain,config,name,version)取候选；命中仍bytes.Equal完整内容。首次/内容变化时append拥有字节再计算其SHA，将*e39Artifact发布到受mutex保护的map。raw/digest不导出，后续没有写入它们的代码；不同Runtime只读取。旧快照不在升级时就地修改。上游c.Contract按值复制，实际身份只用Name/Version。C/D引用内部owned字节；B仍每次Clone，但digest来自已逐字节核对的内部快照。

B/C/D完成输入摘要校验后，Owner使用Runtime私有快照，避免校验后再依赖外部可变切片。仍要求调用者在acquire/Invoke读取期间不并发写输入；原Clone/SHA也有同样要求。**没有证明外部字节天然不可变，因此不做直接外部零拷贝。**

本地GetContractBytecode在step21d_fixture_test.go:80–86自身还有append；保留。根f.run:266取码发生在RunContract计时前，子调用取码则在根export内。本轮消除的是Runtime再次Clone，绝不是所有源字节复制。

原Go NewModule:76–106把只读输入传C桥；native `/home/frankie/mygitprojects/.worktrees/native-step35b/lib/c-api/src/wasm_c_api/module.rs:28–37` wasm_module_new通过bytes.as_slice()调用Module::from_binary。prepareStaticMemory创建新NoData和Image，没有写入source。本轮不改这些实现。

## 缓存身份和失效

Artifact identity=tuple + 实际内容；digest是私有内容的SHA。Module identity仍是原完整key，含内容摘要、运行配置、Copy开关；缓存record.source也绑定摘要。模板还验证实际Module指针与Key。不要将Go Artifact可共享误认为native Store/Imports可共享。

内容变化（包括同Version变内容）替换该tuple的Artifact引用；已有Runtime保持旧快照，旧Module按旧digest区分，不复用错版本。版本/链/配置变化为另一tuple。Copy开关是Manager生命周期固定属性，不改变原WASM，因此不用Copy把Artifact原字节重复存一份。Module继续区分Copy配置。

本轮registry上限8个tuple，Module上限仍8；升级旧内容保留的Module达到原限会返回显式错误，而非无限增长。Reset清native Module，Go Artifact可保留、再次核对内容后重用；Module实际重编译测试通过。新tuple超过registry容量仍会拒绝，即使之前Reset过；生产集成前需要定义缓存淘汰/Reset清理策略和验证。Stop不显式清空pure-Go registry，由Manager引用生命周期/Go GC回收；这不是已完成长期缓存治理的生产实现。

## 观察窗口

原Factory、Owner、Close窗口保持；SHA/Clone阶段用短time.Now及小结构记录，结束后统一输出。runtime_create包含Artifact acquire、可能Clone、对象构建，artifact_acquire包含冷Clone/SHA和锁等待/比较，prepare_total包含key、命中及既有日志。不能重复加总。cold_cost不进入正式热态主统计。

主A/B/C/D都使用同一二进制，平衡顺序。stage count/bytes指记录到的全WASM操作，不包括短Template Key、TxID及业务Guest里的SHA。Go分配是外层f.run envelope的进程Go allocator增量，含收据/JSON/其他工作，不是纯VM或者native分配。

lean单独删除Step-39成本插桩，保留所有校验、原日志及生命周期；源码差异audit/lean.diff，使用相同输入另做3批配对。它验证方向而不是从主结果中减去一个插桩中位数；不能证明所有观察扰动均为零。
'''
(P/'SOURCE_AUDIT.md').write_text(source)
(P/'CORRECTNESS.md').write_text('''# 正确性与安全边界

已验证：

- TestStep39Artifact（source/vm/step39_artifact_test.go:13）：拥有权Copy；调用方随后写源不改变内部内容/摘要；同version换内容失效；version/chain/config/contract隔离；8并发读者各20次核对。独立-race进程通过，仅限纯Go Artifact。
- TestStep39Reject（:69），A/B/C/D分别执行：错误字节、错误version在进入Owner前拒绝；没有用缓存绕过实际输入校验。
- TestStep39ModuleIdentity（:88）：合成小WAT同名同version不同内容分配不同Module；回到旧内容命中旧Module；Reset后清Module并重编译；native模块/Store全部释放。
- 12个真实业务预检进程：所有初始化后Memory逐字节与原Image一致，包含buyNow所有子Instance。旧Copy边界测试沿用Step-38，本轮没有改Ranges/restore。
- audit/parity-*.json比较四组及补充组的TxID、完整Result（含Gas/事件）、RWSet和初始/最终账本hash。全部相同；每个phase的所有调用层级Gas序列一致，见CHILD_GAS_PARITY.csv。buyNow根Gas12612158在本轮四组一致，不与历史不同上下文的12765774直接比较。
- 原step34_owner.go、step21d_compile.go、step35_static.go及wasmer-go managed/store/instance/wasi逐文件SHA与Step-38一致。未改安全Fresh生命周期、Gas、Guest或Copy策略。
- 所有受监控进程Store/Instance配平，pending=0，独立Store!=编译Store，已退出。真实六次下游调用保持执行。

未验证/限制：

- 不允许调用者在读期间并发写原输入；Race只覆盖只读缓存访问，不覆盖native并发/不合法输入并发修改。
- 真正生产部署升级、长时间缓存治理、Manager生命周期外引用、真实节点E2E尚未执行。
- registry容量8、Reset保留Go快照而清native Module；功能正确但生产淘汰政策尚未实现。需要有限额/可回收的管理器策略，不可做无界全局WASM缓存。
- 真实Table函数身份、业务全部异常/回滚未因本轮而宣称新增通过；未注入native危险错误。
- 夹具固定BlockVersion=1、gasUsed=0、内存账本，与真实节点输入上下文不等同；本轮只证明同一夹具内部方案一致。
- 没有发现本轮业务语义差异或资源守卫异常；这不等于全面生产认证。

失败记录保留：build-main工作区路径生成错误；build-main-r1链接阶段找不到本隔离目录的libwasmer（Git历史不含此忽略产物）；在核实已知库SHA后放入规定链接路径，main-r2成功。identity首轮缺少显式CM_REUSE_EXPERIMENT，包init退出2，没有创建native对象；补全原守卫要求后identity-r1通过。没有放宽或跳过守卫。所有失败日志仍在audit/raw_logs。
''')
(P/'NEXT_STEP.md').write_text('''# 建议：仅优化SHA，暂不优化Runtime Clone

1. 保留原输入SHA、Template Key及Module native校验。在safe Manager纯Go层缓存拥有权快照的摘要，避免Invoke对内部快照重复SHA和prepare对同内容重复SHA。不要把metadata当作真实性校验。
2. 进入有限真实节点E2E前，补齐管理器Artifact容量、Reset/Stop清理及真实升级/同名不同内容缓存验证；继续使用既有安全Owner和1536MiB/线程守卫。不得直接把本地原型当生产实现。
3. 仅SHA的有限客户端配对优先于Clone；保留Factory和RunContract/SDK不同边界，客户端传递仍待验证。hashCal关闭新增插桩后Factory CI跨零，应保留不确定性，不以它作稳定收益承诺。
4. C/D虽然降低每次Go分配，但本轮不支持Clone的额外性能收益。不能从“少复制33.8MB”推断buyNow一定更快，也不能无证据归因cache/内存带宽。
5. 不自动进入下一阶段。若后续有限E2E确认SHA未传递到客户端，再考虑WASI Builder/Tokio的独立研究；不改当前native生命周期，不将旧共享Store时间差解释为独立Store成本。

A+Copy的Guest family/二进制不同于本轮Fresh+Copy，下一轮若纳入应独立冻结WASM，不复用本轮绝对Gas/耗时配对。论文可用的当前材料是可审计实现/安全前提、调用边界及有界探索结果；普遍性能结论还需更多独立批次、体积分布和真实节点验证。
''')
print('reports saved')
