"""Offline safety-gate report. No node startup, builds or RPC."""
from pathlib import Path
import json,csv,hashlib,subprocess
P=Path(__file__).resolve().parents[1];ROOT=Path('/home/frankie/mygitprojects')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(n,rows,keys=None):
 keys=keys or list(dict.fromkeys(k for r in rows for k in r))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
base=ROOT/'CVW/experiments/instance-lifecycle';refs=[]
specs={'step-17-real-node':['README.md','AUDIT.md','prototype/runtime.go','prototype/vm_pool.go','prototype/vm_instances_manager.go','samples.csv','network/baseline/stdout.log','network/optimized/stdout.log'],'step-20-e2e-performance-attribution':['README.md','AUDIT.md','low-a-status.json','low-a-requests.jsonl','low-a-resources.jsonl','environment.json','network/baseline/low-a.log','network/optimized/low-a.log'],'step-21b-wasmer-store-lifecycle':['CONCURRENCY_CONTRACT.md'],'step-21d-safe-fresh':['OWNERSHIP.md','NEXT_STEP.md'],'step-21e-fresh-diagnostics':['README.md','MODULE_ANALYSIS.md'],'step-22-serial-static-copy':['README.md','source/vm/wasmer-go/managed.go','samples.csv'],'step-28-six-method-acopy':['README.md','RESULTS.md','TIMING.csv'],'step-29-buy-now-attribution':['README.md','BUY_NOW_ANALYSIS.md','TIMING.csv'],'step-30-e2e-copy-validation':['AUDIT.md','RESULTS.md','audit/final-verification.json']}
for directory,names in specs.items():
 for name in names:
  s=base/directory/name;assert s.exists(),str(s);refs.append(dict(path=str(s),sha256=sha(s),kind='historical reference; never new Step31/32 result'))
  if s.suffix in ['.md','.go']:
   dest=P/'audit/history'/directory/name;dest.parent.mkdir(parents=True,exist_ok=True);b=s.read_bytes()
   if dest.exists():assert dest.read_bytes()==b
   else:dest.write_bytes(b)
for commit in ['394d291','29950ab','f1609b80','bb2772d9']:subprocess.run(['git','-C',str(ROOT/'CVW'),'cat-file','-e',commit+'^{commit}'],check=True)
old=ROOT/'.worktrees/cvw-step17/experiments/instance-lifecycle/step-17-real-node/prototype';new=ROOT/'.worktrees/cvw-step29/experiments/instance-lifecycle/step-29-buy-now-attribution/source/vm'
files=[old/'runtime.go',old/'vm_pool.go',old/'vm_instances_manager.go',new/'wasmer-go/managed.go',new/'step21d_checks_test.go',new/'step21d_runtime_test.go',new/'step22_runtime_test.go',ROOT/'.worktrees/node-step17/module/blockchain/blockchain_stop.go',ROOT/'.worktrees/cvw-step17/chainmaker/chainmaker-vm-wasmer/vm/v2@v2.4.0/vm_factory.go']
index=[]
for i,s in enumerate(files):
 dest=P/'audit/evidence'/f'{i:02d}-{s.name}';dest.parent.mkdir(exist_ok=True);b=s.read_bytes()
 if dest.exists():assert dest.read_bytes()==b
 else:dest.write_bytes(b)
 refs.append(dict(path=str(s),sha256=sha(s),copy=str(dest.relative_to(P)),kind='code inspected; no source edits'))
 for line,text in enumerate(s.read_text().splitlines(),1):
  if text.startswith('func ')and any(x in text for x in ['NewRuntimeInstance','StartVM','StopVM','CloseAllVmPool','ResetAllPool','dOwner','Managed','makeE22','closeE22','TestStep21DOwnerFailure','TestStep22ModuleLifecycle','Stop(','stopVM(']):index.append(dict(source=str(s),copy=str(dest.relative_to(P)),line=line,function=text))
(P/'audit/HISTORICAL_MANIFEST.json').write_text(json.dumps(refs,indent=2)+'\n');write('audit/SOURCE_INDEX.csv',index)
outcomes=[dict(label=f.name.removesuffix('-outcome.json'),**json.loads(f.read_text()))for f in sorted((P/'raw_logs').glob('*-outcome.json'))]
assert len(outcomes)==3 and sum(o['passed']for o in outcomes)==2
res=[]
for o in outcomes:res.append(dict(label=o['label'],scope='existing_protocol_probe_not_node_E2E',test=o['test'],passed=o['passed'],failure_class=''if o['passed']else'configuration_init_rejection_before_test_body',peak_rss_kib=o['peak_rss_kib'],peak_threads=o['peak_threads'],go_heap_bytes='',go_heap_status='not_collected',pid_stopped=o['pid_stopped'],cgroup_empty=o['cgroup_empty'],managed_pending=o['owner_closed']['managed_pending']if o['owner_closed']else'',rss_soft_kib=768*1024,threads_soft=125,memory_max_mib=1024,tasks_max=128,binary_sha=o['binary_sha']))
write('RESOURCE_SUMMARY.csv',res)
write('E2E_SAMPLES.csv',[],['round','pair_id','group','request_id','tx_id','sdk_begin_mono_ns','sdk_response_mono_ns','client_elapsed_ns','success','timeout','commit_evidence','commit_time_ns','gas','result','vm_attempts','newinstance_ns','copy_ns','start_ns','invoke_ns','status'])
write('PAIRED_EFFECTS.csv',[dict(scope='Step32 new E2E',left='G0',right='G1',round=r,planned_pairs=10,valid_pairs=0,paired_save_median_ms='',ci95_low_ms='',ci95_high_ms='',positive_fraction='',status='not_run_safety_gate_not_passed')for r in [1,2]])
write('THROUGHPUT.csv',[dict(scope='Step32 new E2E',group=g,metric=m,numerator='',window_start='',window_end='',denominator_seconds='',value_per_second='',status='not_measured_safety_gate_not_passed')for g in ['G0','G1']for m in ['client_success_response_rate','successful_commit_tps','vm_factory_log_equivalent_tps']])
(P/'raw_logs/E2E_NOT_RUN.json').write_text(json.dumps(dict(verdict='C',safety_gate='NOT_PASSED',new_nodes_started=0,new_sdk_clients_started=0,new_rpc_requests=0,round1='not_run',round2='not_run',new_valid_pairs=0,source='SAFETY_GATE.md'),indent=2)+'\n')
(P/'AUDIT.md').write_text('''# Step-31/32最小准入审计

以实际文件/分支为准：Step17、Step22 394d291、Step28 29950ab、Step29 f1609b80、Step30 bb2772d9均存在；原e20-e2e-copy-attribution目录未找到，实际已改名step-20-e2e-performance-attribution。Step20 low-a原始客户端/资源/status可用，Step30没有新E2E。各历史文件哈希、源码快照、行号索引在audit/HISTORICAL_MANIFEST.json与SOURCE_INDEX.csv；未写历史原件。

## 可复用协议

Step21B规定当前C API Store及其对象只能在已建立的所有者协议下访问；实际so有非原子StoreRef计数证据，native源码逐字构建来源仍不完整。Step21D/21E建立固定OS owner、ManagedScope强引用、按scope逆序清理、有限Gas回调重入及拒绝在途Close。Step22把同Store Module缓存与fresh Instance结合，预计算Copy与编译在Invoke外；Metadata的Imports/Exports先在持久scope物化，每次Instance对象临时scope同步关闭。

本轮没有重新设计协议，使用Step29同源已保存binary重跑两个原有小检查。它们验证了缓存Module串行fresh隔离、非owner拒绝、错误创建/关闭后清理以及进程终结；不是节点业务正确性或长寿命WASI认证。原配置失败和重试不混为成功，原STOP留存。

## 真实节点差距

旧node仍为InstancesManager.NewRuntimeInstance→getVmPool→Store/Module准备，随后Runtime.Invoke才获根锁；native Finalizer在Go运行时线程触发，不受该锁统一路由。StartVM/StopVM均返回nil；VmManager.Stop确实调用StopVM，故这里有适配钩子，但现有实现没有排空/owner销毁。CloseAllVmPool只保护map并触发pool.close；pool.close关channel，reset发channel，不是线程所有权与在途join。不能说“节点已有Stop调用”就等价于“native回收已完成”。

managedOwner/current/entries在实验绑定中是进程级单owner；测试dManager还直接引用fixture.nextID/calls与testing生命周期。不能直接把它设为node VmInstancesManager，也不能只复制managed.go或加根锁。需要节点初始化/准备/运行/嵌套回调/Reset/Stop的完整owner适配及确定回收验证；现有资料未提供可直接复用的此类节点补丁。

Step22的缓存Store每创建WASI可能累积线程，已有安全许可明确限制每Store/每进程次数；进程最终退出才是资源隔离终点。这不是10或20笔长寿命节点请求的通用准入。旧Step20 RSS在2564.707MiB触及2560MiB软限，两组都增长约1GiB，归属未完全定位；不证明20对必然超限，但不能通过抬限/隐式进程轮换绕过。

## 有限决定

只执行两个已有小协议检查，不启动真实节点。已有根锁不足；直接迁移单个finalizer文件不足；完整owner节点适配尚无实现及验证，不在本轮继续临时移植/扩大。SAFETY_GATE最终NOT_PASSED，采用用户指定结论C。没有新优化、clone GC研究、A/B1、原池并发或新的全局锁；VM/SDK/绑定/Gas代码改动0。

## 若未来恢复E2E的冻结条件（本轮未执行）

优先G0/G1同原件家族，compute.bigNumCal逻辑WASM SHA e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507，参数{}、同源Module/template与等价账本；不加入A/B1。SDK-Go/v2 2.4.0单客户端闭环，无100ms Sleep；两条隔离单验证节点TBFT测试链，20ms出块，无生产连接。客户端计时SDK begin→同步RPC响应返回，先冻结真实node适配版本/构建hash再运行。

第一轮10对，第二轮只有准入/业务/资源/退出验证通过才10对；平衡G0/G1先后，每笔唯一TxID。节点RSS软限仍2560MiB、hard3GiB、线程soft220/hard256、SDK timeout60s/外部watchdog15s；Go heap必须新增低开销采集而非填写旧RSS。新集成改变调度/回收模型时登记为受控新E2E，不能冒充原节点生产性能。新代码/账本/客户端配置尚未生成，因此不能把这些条件写成已执行配置。
''')
(P/'TIMING_BOUNDARIES.md').write_text('''# 本轮计时与缺失值

新E2E未启动，所有新Median/Mean/P95/配对CI/正向比例/成功率/吞吐均not_measured，不能填0或从Step20搬入。本轮只有两个既有协议测试的新日志，RESOURCE_SUMMARY标记not_node_E2E。初始配置拒绝进程也保留。

未来客户端主窗口保持SDK调用开始→同步响应返回，使用同进程单调time.Now/time.Since；不含Python启动/SDK初始化，不以driver管道窗替代SDK窗。旧client只保存elapsed，SDK绝对begin/end缺失；新请求应另存这些时间。

历史同步路径已由Step30源码追踪：SendRequestSync注册TxID→AddTx→本地PutBlock返回→BlockInfo事件→结果dispatcher→RPC响应。它覆盖本节点提交结果通知，不提供每笔精确PutBlock完成时间或全网最终性；没有独立提交事件时间窗时不报告独立成功提交TPS。

VM factory外层包runtime.Invoke，旧STEP17内部invoke_ns在根锁之后；后者不含锁前模板/Module准备与根锁等待。S1含NewInstance+Copy，旧S2-S1是WASI+_start合计；不能补造独立NewInstance/_start。Step28/29测试管理器另有完整窗口，不是客户端E2E。根与子调用嵌套，不能重复相加；同TxID重执行须保留全部尝试。不同进程timestamp不直接相减。

客户端成功响应速率=成功响应唯一TxID数/明确SDK/driver观测墙钟窗；提交TPS=确认提交唯一TxID数/明确提交事件窗；VM日志等效速率=筛选成功调用N/同集合factory Invoke秒数之和。王浅秋恢复脚本另有并发N/(maxEnd-minStart)及过滤顺序差异，旧入口未完全确认；这几种指标不得混用。本轮所有分子/分母均缺新测量，THROUGHPUT留空而不写0。

未实施新的高开销VM追踪，也不研究clone内部。若将来改变安全生命周期，必须冻结新节点构建与计时协议、单列一次性准备和每调用成本。当前只冻结协议，没有运行。
''')
(P/'RESULTS.md').write_text('''# 本轮结果：C，真实节点E2E仍被安全准入阻塞

## 本轮直接测量

- 重用固定binary/native，两个原有协议检查通过：3个scalar fresh隔离/返回42/缓存Module作用域回收；另一检查验证非owner拒绝、非法创建回滚、缺deallocate错误后继续回收、关闭后拒新请求。两个有效独立进程managed/pending0、PID/cgroup均已结束。
- 有效检查峰RSS约52.71MiB、线程23，未触发资源阈值；Go heap未由既有probe采集，缺失不填0。另有1次package init配置拒绝，测试未开始，单独留档。
- 新SDK客户端0、新节点0、新RPC请求0、新E2E配对0、第一轮/第二轮均未启动。两个protocol probe不能称两轮E2E，也不能计算Copy收益。

## 七个问题

1. **真实节点是否通过准入？没有。** 有界测试所有权协议可复用，但节点Start/准备/Invoke/Reset/Stop没有相应完整owner/在途排空/native回收适配。详见SAFETY_GATE逐项判定。
2. **Copy是否降低客户端响应延迟？本轮未测。** 不能把未执行写成正收益或负收益。
3. **P95/成功率/提交TPS支持什么？全部新指标not_measured。** 没有新失败交易也不等于成功率100%；守卫预配置失败不是业务失败率。
4. **VM收益是否传递到客户端？本轮无新证据。** 已有串行VM初始化收益仍保留，不能替代客户端证据；旧Step20单个资源删失批88对VM平均省0.273ms、client平均慢1.148ms，属于历史描述，不构成本轮独立验证。
5. **与旧Step20哪些可比？** 未来可保持SDK开始→同步响应、同WASM/参数/输入与对照定义；一旦采用新owner模型，运行时准备/排队/回收行为有变化，应登记受控新E2E，绝不能拼接绝对耗时或借旧样本凑20对。历史RSS停止及源hash可作为资源保护依据。
6. **可开始总结阶段成果吗？可以。** 当前阶段可以诚实总结“静态Copy替代Data初始化在若干串行VM测试有可重复局部收益、已覆盖成功路径Gas/业务对照，但真实客户端E2E收益尚未确认，最终节点准入受生命周期/资源适配阻塞”。这足够写阶段性研究总结，不足以写Copy生产上线成功或Copy整体无效。
7. **哪些留待后续？** 最小后续仅一项节点生命周期适配包：固定owner覆盖创建/回调/析构/Reset/Stop、在途排空及同阈值WASI/native回收；适配通过后才做两轮10对与节点业务/提交验证。clone内部GC、A/B1组合、COW/页面映射、原池并发TPS、Table全覆盖、长期生产压测可明确留待后续，不必为当前阶段总结无限扩展。

## 证据等级

直接测量：本轮两个有界协议检查、错误处理与资源/退出。源码支持：旧节点owner/stop缺口与测试协议不同。未验证：新节点安全集成、长寿命WASI回收、节点业务与提交、新E2E收益。未作断言：Copy导致GC/排队退化、20对一定OOM、旧单客户端必然race。没有继续改VM或追查clone。
''')
(P/'CORRECTNESS.md').write_text('''# 正确性边界

本轮protocol checks通过项目：scalar新Memory不继承上次修改、函数返回42、固定owner断言拒绝其他线程、非法WASM创建错误清理、真实WASI小模块缺deallocate时保留错误并继续清理、关闭后拒绝新建、缓存scope/最终owner登记为0、进程及cgroup结束。程序正常退出不是native所有内部资源长期安全的充分证明；native线程完全终结只确认在本次进程终点。

未验证：真实节点G0/G1 Gas、业务返回、读写集、事件、最终账本、提交成功、异常/回滚、跨合约以及Table身份，均not_tested；旧21D/22/28/29业务证据不能当本轮节点pass。本轮没有SDK请求，因此业务成功/超时/失败率未测。

初始package init因缺少显式R1配置拒绝，未进入测试体；失败原件与STOP.json保留。补齐要求配置后另命名重试，没有关闭managed、store guard、资源限制或扩大次数。2个有效probe+1个配置拒绝过程全部保留，不删除不利记录。

真实节点的生命周期准入未通过，按用户规则停止，不启用旧原池背景创建/异步关闭、不用全局锁掩盖所有权、不提高RSS、不做每请求强制GC或进程轮换来凑20对。现有协议的测试末尾GC来自原测试，未更改，不是E2E负载控制手段。
''')
(P/'README.md').write_text('''# Step-31/32：真实节点安全准入与Copy E2E收尾

**本轮结论C：真实节点安全门槛未通过，Step32未启动。** 新节点/SDK请求/E2E配对/完成轮次均0；没有把历史样本或本轮小WAT测试冒充真实E2E。

已实际复验两个既有有界生命周期检查并通过，确认测试协议可复用的一部分；但真实节点Store/Module锁前准备、native Finalizer、Reset/Stop与在途排空仍缺完整owner适配，不能直接搬测试manager进节点。首次配置拒绝保留，不隐去。VM/绑定/SDK/Gas代码改动0，没有生产修改、推送、PPT、新优化或clone内部研究。

先读[SAFETY_GATE](SAFETY_GATE.md)，再读[AUDIT](AUDIT.md)、[RESULTS](RESULTS.md)、[计时边界](TIMING_BOUNDARIES.md)、[正确性](CORRECTNESS.md)。E2E_SAMPLES只有表头，PAIRED_EFFECTS和THROUGHPUT为明确not_run占位、缺失指标空值；RESOURCE_SUMMARY只含3个protocol/config进程，不能解读为节点资源。

分支experiment/step31-32-e2e-copy-final，父bb2772d9；源码/历史快照及hash见audit。脚本归档既有检查命令、失败及资源监视，**最终gate失败后不应继续运行检查或节点**。离线复算仅：

```bash
python3 -B scripts/archive_and_report.py
python3 -B scripts/verify.py
```

复算在原独立worktree中运行；IDE镜像用于阅读。所有原始probe日志、命令、outcome、资源、配置纠正与停止记录保留，source/SDK版本未改，历史原始数据未覆盖。旧Step20实际路径为step-20-e2e-performance-attribution，不是原e20路径。

可以结束当前研究阶段并开始总结：支持局部VM初始化收益与有限语义证据，真实客户端收益尚未确认；无需把clone内部机制、A/B1、COW或原池高并发继续扩为当前结题条件。下一项工作应单列节点生命周期适配及回收验证，完成后最多两轮E2E。回退无需改生产；本轮所有自有进程已退出，不停止任何其他现有节点。
''')
print('finite safety gate report saved; verdict C; no E2E run')
