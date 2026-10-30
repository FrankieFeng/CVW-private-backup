from pathlib import Path
import json,csv,statistics as st
P=Path(__file__).resolve().parents[1]
def rows(n):return list(csv.DictReader((P/n).open()))
def put(n,s):(P/n).write_text(s.strip()+'\n')
a=json.loads((P/'analysis.json').read_text());rs=rows('RESOURCE_SUMMARY.csv');ok=[r for r in rs if r['passed']=='True'];new=[r for r in ok if r['independent']=='True'and r['label'].startswith('v9-')];cost=rows('ARCHITECTURE_COST.csv');index=rows('CODE_INDEX.csv')
def ref(name):
 r=next((r for r in index if name in r['declaration']),None);return f"`{r['path']}:{r['line']}`"if r else'见CODE_INDEX.csv'
put('MODULE_STORE_COMPATIBILITY.md',f'''# Module / Store兼容性

实际加载6.0.1库SHA256 `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`，未替换native。C预检 `source/compat.c`/`compat.wat`、日志raw_logs/native-compat.log、完整命令audit/compat-command.json。dladdr记录实际.so；Go Race进程/proc/maps另确认同一文件。

1. wasm_store_new创建三个Store。缓存Module仅在S0编译一次，S1/S2使用同Engine、同Module实例化成功。
2. S0 Memory当作S1 import时，wasm_instance_new拒绝；换成S1/S2各自Memory后都成功。不是只依据Go指针不同认定独立Store。
3. 两个实例同时存在，Memory1写123，Memory2仍0；实例1真实函数返回123。
4. 3个Store/2个Instance的C API创建和删除平衡；这是handle操作计数，不是Rust Rc最终Drop探针。

实际ABI不导出wasm_store_clone，也没有module_share/module_obtain；不能使用陈航的新接口来替代本库。内部StoreRef.clone在6.0.1候选源码是Rc共享，不等于wasm_store_new。module_serialize/deserialize导出存在，但本轮未调用，无需在每次Invoke反序列化或重复编译。

候选旧native源码wasmer提交3189527eec99cfea7e6991328509e72ed0bec2e0：store.rs调用Store::new(engine.inner.clone())；Module只包编译代码，instance.rs实际使用传入Store并保存该StoreRef。不是6.1分支。未证明候选源码是该.so逐字构建来源；以固定二进制的兼容性运行证据补足API问题，不宣称重建认证。wasm_extern_vec_destroy是现有库扩展，逐函数反汇编归档，未修改ABI。

Go显式入口 {ref('NewInstanceInStore')}；原NewInstance仍可委托module.store，独立路径显式传targetStore。WASI Finalize/GenerateImportObject/host imports/Initialize也全用同一targetStore。Module的编译Store保留到cache释放，Module元数据先在cache scope预热；native Module跨Store可用不意味着Go wrapper可跨线程共享。
''')
put('ARCHITECTURE.md',f'''# 安全Fresh原型架构

本轮是独立可运行原型，不是生产替换。生产main和版本未改，父963b47b4。已有A/Copy Guest和Gas规则不变，未合并陈航分支、未加入B1。

```text
请求 -> SafeFreshOwner.Do(context) -> 唯一native owner(OS线程)
  缓存: Config/Engine E + 编译Store S0 + Module M + lazy类型元数据/静态plan
  每次Fresh: new Store Si(E) -> WASI/imports(Si)
     -> NewInstanceInStore(M,Si) -> 可选原restore -> WASI.Initialize(Si) -> _start
     -> SetGas/真实CallMethod/Gas结果 -> 同步scope清理 -> 删除Si handle
  buyNow host回调 -> 同owner直接进入子Runtime -> 子Store Sj -> 执行/关闭 -> 返回父调用
Reset: 停止接纳 -> 等在途job结束 -> owner执行cache释放 -> 重建或继续
Stop: 停止接纳 -> 排空job -> owner清理cache/root -> owner结束
```

独立Store解决runtime arena所有权隔离；不假定全部Wasmer操作都必须固定OS线程。C API StoreRef为Rc/UnsafeCell，API文档要求store及对象单线程访问；Go wrapper的元数据和managed registry也非多owner设计，所以本原型保守选择一个进程一个owner，Engine/Module未认证跨线程共享。固定线程与资源scope、回收顺序、排空协议共同构成约束，不能单凭LockOSThread当安全证明。

{ref('NewSafeFreshOwner')} 为非test源码。queue容量1，最多接纳32个外部job（含取消），不提供生产无限服务承诺。同owner重入Do直接inline，不等待自己队列；从owner内部Reset/Stop拒绝。真实buyNow仍经过真实Core VM和六个Guest，下游不走外部排队。合约重入/depth守卫保留，未用全局锁掩盖原池并发。

截止/取消仅在排队或安全检查点生效；不会强行销毁正在native执行的资源。Stop ctx到期可返回，但cleanup仍在任务完成后执行。所有reply缓冲1避免调用者取消后owner卡在回复。Reset失败后poison并拒绝新job，仍可Stop。原始Pool resetC及空StopVM没有直接改写；节点必须接线到此新协议后才可使用。

缓存tuple冻结合约/版本/WASM SHA/配置；实际缓存selector沿用测试recipe的contract+group。本轮不认证动态升级和任意缓存失效，节点适配必须固定部署并拒绝不匹配或使用完整key。Module编译/模板在目标Invoke前，缓存用于真实init/业务/故障后恢复；不是每Fresh重复编译。
''')
put('OWNERSHIP_MATRIX.md',f'''# 所有权及释放矩阵

|资源|创建/所有者|共享范围|释放/约束|本轮证据|
|---|---|---|---|---|
|Config、Engine|cache scope、native owner|该Module的新Store共用Engine|cache退出最后释放，禁止用户线程析构|兼容性+真实业务|
|编译Store S0、Module、import/export type元数据|e25Prepare；cache scope|同owner缓存Module|预热元数据；排空后关Module/类型/Store/Engine|MODULE_PREPARATION及owner计数|
|运行Store Si|makeE22；instance scope|每个Fresh独立，不clone|其他运行对象清理后删除Store handle|C外Store导入拒绝、store_created事件、CAPI计数|
|WASI配置/环境|Si内创建；配置由native消费|不跨Store freelist|instance scope，WASI env_delete on_exit在Si存活时执行|故障回滚、真实_start|
|Imports、host functions、exports|Si/instance scope|不得逃逸请求|同步显式/逆序scope清理；borrowed类型不重复释放|claimed destructor、实际close测试|
|Instance、Memory、Globals/Table|NewInstanceInStore(M,Si)|Guest运行态不复用|CallMethod返回后同步关闭，Store最后删除|48根+72子调用；Table真实函数身份not_tested|
|Guest函数/Memory借用视图|当前live scope|只在该调用内|关闭后函数/Memory scope/exports检查拒绝；禁止保留Data切片|owner测试post-Close调用拒绝|
|返回值/RWSet/事件|Go宿主对象|可离开owner，不能带native handle|sysCall先make+copy请求body，SuccessResult持有Go bytes|vm_bridge.go:请求body复制；逐次语义对比|
|子Instance|父调用同owner同步创建独立Sj|同cache Module，不共用运行Store|子完成并关闭再返回父；父scope仍存活|buyNow真实六callee/Gas传播|

managedSetFinalizer并非runtime.SetFinalizer：所有native wrapper登记强引用scope，不安装任意Go Finalizer goroutine的native析构。GC不能抢先析构，scope在owner执行。{ref('managedSetFinalizer')} 返回是否成功claim，重复Close无二次C删除；{ref('Close() (err error)')} 在active native call时拒绝关闭，cleanup继续处理其他登记项。没有保留已关闭对象的永久tombstone表。

C API删除计数与Rust最后引用析构分开；未加native Drop探针、不认证长期全部Rc/后台任务。原型以同步C API回收、in-flight=0、scope无登记、资源采样和进程正常退出建立有界证据，不把OS进程退出替代运行期间的所有权协议。
''')
put('IMPLEMENTATION.md',f'''# 实际实现

- {ref('NewInstanceInStore')}：新显式target Store入口，检查live Module/Store与共享Engine；真正传入wasm_instance_new，不靠wrappedInstance.store字段装作隔离。
- {ref('makeE22')}：在instance scope里NewStore(cache.Engine)，WASI/host imports/Instance/Initialize都使用Si；Copy仍复用原模板和noData Module，restore位于WASI Initialize/_start之前。Cached Module与编译Store不逐次销毁。
- {ref('managedSetFinalizer')} 和scope.Close：显式释放采用一次claim，scope不再提前移除登记导致Close被跳过。Store/Instance/WASI/Module等重复Close不会重复调用C析构。Memory与function增加借用scope检查，Store/Instance关闭后指针清空或拒绝访问。
- {ref('Do(ctx')} / {ref('Reset(ctx')} / {ref('Stop(ctx')}：有界队列、inline callback、排空、取消、幂等Stop、Reset失败poison。没有恢复原pool grow、异步关闭或无主finalizer。
- source/vm/step34_business_test.go：真实ChainMaker SimContext、Step32四组recipe与buyNow依赖，不模拟子调用。source/vm/step34_fault_test.go仅提供明确的Go层故障，普通路径无Gas修改。原dRuntime继承的CallMethod错误被gasErr覆盖问题已在本原型修正：保留CallMethod错误，仍按原规则读取/计算Gas。增加真实unreachable trap与缺失方法；owner返回错误时只返回Go消息，避免TrapError的native Frame跨scope逃逸。

编译冻结build9 SHA `{a['final_build_sha']}`。Race单独二进制，不参与计时。早期构建/启动/诊断错误全部保留；build6/7数据另有prefix和原件，最终性能与正确性只选v9标签。派生区块labels曾漏前缀，修正原件备份audit/block-metadata-prefix-correction，原日志/收据未改。继承的e27Probe诊断定义原先仅在_test，导致常规go build失败，现原样移入step27_diagnostic.go并通过非test编译；没有改原导出窗口。源码包含gofmt差异，语义补丁另存audit/source-semantic.diff。

计时仍dRuntime.Invoke入口到延迟close完成后记录：含新Store、WASI imports、NewInstance、Copy、Initialize/_start、CallMethod/Gas、关闭。owner排队在此窗之外。编译/模板/缓存最终销毁单列；不能把排队窗或编译差异算Copy收益。父export嵌套子Invoke，禁止相加。

非test实现包含owner与binding；完整业务桥接目前是测试适配器，尚未将生产NewRuntimeInstance/getVmPool/StopVM路由到它。不是可直接替换的node binary，低级native句柄不得外泄给任意调用者。
''')
put('LIFECYCLE_TESTS.md',f'''# 已执行生命周期测试

|场景|证据|范围|
|---|---|---|
|真实独立Store+同Module|native-compat.log|三Store，两活Instance；foreign Memory拒绝，自有Memory通过且隔离|
|Fresh/WASI/_start/业务/关闭|verify-*三批|4合约×4组×3轮=48根；buyNow12根、72真子调用|
|Module准备失败|TestStep34Owner bad-module|真实畸形WASM拒绝；新Store部分资源scope回滚，缓存随后可调用|
|Store/WASI/Instance/Initialize失败|freeze-fault-*|Go安全检查点注入；不冒称实际OOM或C错误被制造|
|执行失败及回滚|fault-execute与business-error-*|Go Guest后故障、真实ERC空输入、真实buyNow重复token、缺失方法；账本未提交|
|故障后恢复|recovery-G0.json|同缓存Module，下一Fresh实际成功|
|关闭失败/取消关闭|fault-close/cancel-close|先真正清理再注入Go返回错误；native void析构失败不可安全强制注入|
|取消创建|cancel-wasi、Do取消|创建Store后取消，scope回滚；队列取消不启动native业务|
|Reset、Stop在途等待|TestStep34Owner|channel barrier定位job，不使用Sleep；Stop超时不释放在途资源，释放任务后Stop完成|
|重复Close、GC、失效函数|TestStep34Owner|重复Instance/Store close、强制GC、关闭后函数拒绝|
|Reset失败|TestStep34Poison|poison拒绝新请求，Stop正常且可重复|
|Go Race|v9-race-owner/v9-race-poison|通过，仅Go协议诊断，不能认证native race不存在|

结构化记录{a['processes']}进程，成功{a['passed']}；失败owner-configured是诊断在ManagedEndOwner后读取ManagedCount触发守卫，build3及冻结版已修正。另保留build1编译参数错误和owner-preflight缺环境变量的package-init拒绝；未执行Guest，未隐藏。任何资源阈值均未提高，失败进程已结束。

保护：普通合约RSS768MiB/125线程，exchange1536MiB/220线程，硬MemoryMax2GiB/TasksMax256/60s，Go45s；宿主可用内存至少8GiB、swap不超过1GiB。owner C兼容性预检另更小边界。每进程至多2组/目标，exchange1组。无后台池、无100ms业务Sleep，无长期压测。
''')
put('CORRECTNESS.md',f'''# 正确性

CORRECTNESS.csv：12完整四组区块，48根全部通过。G0 Fresh、G1 A、G2 Copy、G3 A+Copy，Gas/返回/RWSet/事件/初末账本严格相同。buyNow每根真实调用identity.addWriteList、identity.isApprovedUser两次、ERC721.mint、setApprovalForAll2、transferFrom；12根共72子调用，全保留每层Gas与状态，不累加嵌套累计Gas。

HISTORICAL_SEMANTIC_CHECK.csv逐个组与Step32同WASM/输入/TxID原收据比较通过，包括真实业务Gas/写集/事件/账本；仅作语义复核，不比较旧时间。A和Copy Guest原件哈希冻结，未构建新Guest/删SDK接口/改Gas规则。

Go故障与真实业务异常均检查BeforeHash==AfterHash；故障后恢复收据仍执行真实业务。关闭/取消错误不会把未提交交易写入账本。native不可安全注入的OOM/析构失败未测，仅验证Go层相应回滚边界；不能标作真实native失败已全部认证。

真实Table函数身份、所有任意输入、原池并发、在线合约升级及长期资源释放：not_tested。日志内原recipe的table字段未改成通过。本轮只证明已覆盖路径，不证明生产普遍正确。
''')
put('SAFETY_GATE.md','''# 准入决定

**有界串行独立Store原型通过；真实节点E2E仍未准入，未启动节点或压测。**

|条件|本轮状态|
|---|---|
|独立Store，不是Rc clone|PASS：固定so外Store导入拒绝，实际跨Store同Module/Memory隔离|
|缓存Module/Engine/API契约|PASS于同owner同Engine；未认证跨线程wrapper共享|
|Fresh创建/执行/同步关闭|PASS：四组真实业务三轮|
|错误回滚、失效访问、重复关闭|PASS于列明的Go故障与真实业务错误；native OOM/析构失败not_tested|
|Finalizer/显式Close冲突|PASS于scope协议：不安装Go native finalizer，owner claim一次，GC与重复Close测试|
|Reset/Stop与在途job|PASS于SafeFreshOwner；不等于已修好原pool.reset/空StopVM|
|真实跨合约/Gas/状态|PASS于12 buyNow根/72子调用及其他三合约|
|有限资源|PASS于当前有界测试，非长期native Drop/线程join证明|
|节点实际NewRuntimeInstance/缓存/回调/Stop接线|NOT_IMPLEMENTED_AND_NOT_VALIDATED|

最小剩余阻塞是节点适配接线及其生命周期smoke，而非“本库不支持独立Store或缓存Module”。当前完整业务路径在测试适配器中；将其当成可替换节点实现会遗漏锁外Module准备、原manager reset/Stop与回调归属。不得直接替换Instance创建一行后启动E2E。

不把尚未证明安全写成已发生内存损坏；本轮没有观察到native资源损坏。没有因为GetRace通过就认证native安全。正式生产节点保持原样。
''')
put('NEXT_STEP.md','''# 最小后续工作

1. 独立节点适配分支中，将NewRuntimeInstance/合约缓存准备、根Invoke、嵌套回调、Reset/Stop全部路由到SafeFreshOwner；缓存按合约版本+WASM SHA+native/compiler/Gas/config键验证，固定部署时禁止未匹配二进制和在线升级。不接回原pool后台grow/freelist/async close。
2. 复用现有固定库、Guest和四组原件，只选Baseline/Copy恢复一个隔离节点。先启动→单根真实交易→在途Stop→正常退出，核对/proc maps、Gas/写集/事件/账本、CAPI计数及RSS/线程；这一步是接线验证，不是E2E性能结论。
3. 接线smoke通过后才进入有限SDK开始到同步响应的配对E2E。两组同新生命周期；编译/模板和owner排队另列；保留TxID/重复Invoke/提交语义。每owner外部job预算≤32，按有限实验计划配置，不解除守卫、不通过重启掩盖持续增长。

不再等待陈航、不换native ABI、不引入B1、不研究新Copy或Module编译优化。精确native构建来源、长期服务、多owner并行和Table身份作为后续认证问题，不能在当前有限原型上宣称已解决。
''')
peak=max(float(r['rss_peak_kib'])for r in new)/1024;thread=max(int(r['threads_peak'])for r in new)
lines=['# Step-34 安全Fresh源码原型','', '已实现并真实执行，尚非生产替换。独立分支experiment/step34-safe-fresh-runtime，父963b47b4。未修改生产、未推送、未启动节点E2E。','', '|最终问题|结果|','|---|---|','|真正独立Store？|是：wasm_store_new；跨Store错误导入拒绝和Memory隔离实测，不是Go/Rc clone|','|保留Module缓存？|是：缓存Module，同Engine不同Store，无逐Fresh重复编译/反序列化|','|Fresh完整路径？|是：新Store→WASI/imports→NewInstanceInStore→原Copy→Initialize/_start→CallMethod/Gas→同步回收|','|错误/Finalizer？|Go故障、真实业务回滚、GC、幂等Close、Reset/Stop/poison通过；native OOM/析构失败未强制制造|','|buyNow六下游？|三轮四组12根/72真实子调用正确|','|Gas/状态？|四合约48根四组一致，逐收据与Step32语义复核通过|','|生命周期固定成本？|同代码控制直接配对见下表；N3探索性，不能给通用固定常数|','|可直接开始节点E2E？|否；可进入最小节点适配接线验证，仍须完成生命周期smoke|','|最小阻塞？|节点manager/缓存/回调/Reset/Stop未路由新owner，当前业务适配仍是测试入口|','', '|方法|共享Store控制Median ms|独立Store Median ms|直接额外耗时 Median [95% CI] ms|对数|','|---|---:|---:|---|---:|']
for r in cost:lines.append('|'+r['case']+'|'+f"{float(r['control_median_ms']):.3f}|{float(r['independent_median_ms']):.3f}|{float(r['paired_extra_median_ms']):+.3f} [{float(r['ci95_low_ms']):.3f}, {float(r['ci95_high_ms']):.3f}]|{r['N_pairs']}|")
lines+=['','正值为新路径额外成本，负值为更快；三对bootstrap区间仅探索。控制组也是同owner/同补丁的安全串行共享Store，不是默认池或原生产版本；Module/模板准备均在外。exchange三对更快仅归属于此Store架构对照，不归因Copy或预设线程/GC原因。','',f'独立路径已通过进程观测峰值RSS {peak:.1f}MiB、线程{thread}，创建/删除计数平衡；含控制组及失败的所有记录在RESOURCE_SUMMARY.csv。计数是C API handle操作，非最终Rust Rc Drop测量。','', '入口：ARCHITECTURE、OWNERSHIP_MATRIX、IMPLEMENTATION、MODULE_STORE_COMPATIBILITY、LIFECYCLE_TESTS、CORRECTNESS、SAFETY_GATE、NEXT_STEP。原始命令/资源/收据在raw_logs；CODE_INDEX.csv给函数行号。','', '复算：python3 scripts/analyze.py；python3 scripts/report.py。构建：scripts/build.py使用新标签避免覆盖，固定本地native so与go.work依赖；运行：scripts/validate.py（已完成标签会跳过，不构成新实验）。完整参数见逐进程command.json。native兼容性完整编译命令仍应使用source/compat.c/WAT，原C API命令见audit；共享代码diff在audit。','', '回滚：停止state.json所列自有step34 unit、核对PID/cgroup清空，保留分支/目录即可；没有生产部署需回滚，不reset/clean原工作区。归档不含so或.test，固定哈希原件仍在原隔离工作树。']
put('README.md','\n'.join(lines));print('DOCS WRITTEN',peak,thread)
