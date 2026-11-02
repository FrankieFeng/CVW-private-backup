"""Read-only recomputation and report generation after scripts/analyze.py."""
from pathlib import Path
import csv,json,statistics as st,random,hashlib,collections,platform,subprocess,shutil
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
def write(n,r):
 keys=list(dict.fromkeys(k for x in r for k in x))
 with(P/n).open('w',newline='')as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(r)
def doc(n,s):(P/n).write_text(s.strip()+'\n')
def q(v,p):
 v=sorted(v);k=(len(v)-1)*p;i=int(k);return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(k-i)
def fmt(x):return f'{float(x):.3f}'
C=json.loads((P/'inputs/cases.json').read_text());S=read('STATISTICS.csv');E=read('PAIRED_EFFECTS.csv');W=[x for x in read('THROUGHPUT.csv')if x['valid_main']=='True'];T=[x for x in read('RAW_TRANSACTIONS.csv')if x['valid_main']=='True'];R=read('RESOURCE_SUMMARY.csv')
# Add preserved seed/restart outcomes to resource table (do not alter raw artifacts).
known={x['run']for x in R}
for pat,phase in [('*-seed.json','deployment'),('post-*-postcheck.json','restart')]:
 for f in sorted((P/'raw_logs').glob(pat)):
  x=json.loads(f.read_text());z=x.get('node')or{};label=z.get('label',f.stem)
  if label in known:continue
  o=z.get('owner')or{};R.append(dict(run=label,case=x.get('case',x.get('contract','')),group=x.get('group',x.get('flavor','')),phase=phase,passed=x['passed'],rss_peak_mib=z.get('peak_rss_kib',0)/1024,threads_peak=z.get('peak_threads'),go_heap_boundary_peak_mib='not_recorded',goroutines_snapshot_max='not_recorded',stores_created=o.get('stores_created'),stores_closed=o.get('stores_closed'),instances_created=o.get('instances_created'),instances_closed=o.get('instances_closed'),pending=o.get('managed_pending'),exit_code=(z.get('systemd')or{}).get('ExecMainStatus'),pid_exited=z.get('pid_exited'),cgroup_empty=z.get('cgroup_empty'),stop_seconds=z.get('stop_s')))
write('RESOURCE_SUMMARY.csv',R)
TPS=[];TE=[]
for case in C:
 for g in ['G0','G1','G2','G3']:
  a=[x for x in W if x['case']==case and x['group']==g];v=[float(x['submitted_tps'])for x in a]
  TPS.append(dict(case=case,group=g,batches=len(a),confirmed=sum(int(x['confirmed_unique'])for x in a),window_seconds=sum(float(x['window_seconds'])for x in a),pooled_submitted_tps=sum(int(x['confirmed_unique'])for x in a)/sum(float(x['window_seconds'])for x in a),batch_mean_tps=st.mean(v),batch_median_tps=st.median(v),batch1=v[0],batch2=v[1],batch3=v[2]))
 for l,r in [('G0','G1'),('G1','G2'),('G0','G2'),('G0','G3')]:
  a={int(x['batch']):float(x['submitted_tps'])for x in W if x['case']==case and x['group']==l};b={int(x['batch']):float(x['submitted_tps'])for x in W if x['case']==case and x['group']==r};d=[b[k]-a[k]for k in sorted(a)];rng=random.Random(int(hashlib.sha256((case+l+r+'TPS').encode()).hexdigest()[:16],16));bs=[st.median(rng.choices(d,k=3))for _ in range(10000)]
  TE.append(dict(case=case,left=l,right=r,N_windows=3,median_tps_gain=st.median(d),ci95_low=q(bs,.025),ci95_high=q(bs,.975),batch1=d[0],batch2=d[1],batch3=d[2],all_batches_positive=all(x>0 for x in d)))
write('TPS_STATISTICS.csv',TPS);write('TPS_EFFECTS.csv',TE)
ss={(x['case'],x['group']):x for x in S if x['metric']=='e2e_ms'and x['batch']=='all'};ee={(x['case'],x['left'],x['right'],x['metric']):x for x in E};ts={(x['case'],x['group']):x for x in TPS}
rows=['| 方法 | 每组N/批数 | Fresh P50/P95 | Copy P50/P95 | A+Copy P50/P95 | A-only P50/P95 | Copy配对节省[95%CI] | A+Copy配对节省[95%CI] |','|---|---:|---:|---:|---:|---:|---:|---:|']
trows=['| 方法 | Fresh | Copy | A+Copy | A-only |','|---|---:|---:|---:|---:|']
for c in C:
 vals=[f"{fmt(ss[c,g]['median'])}/{fmt(ss[c,g]['p95'])}"for g in ['G0','G1','G2','G3']]
 eff=[]
 for g in ['G1','G2']:
  x=ee[c,'G0',g,'e2e_ms'];eff.append(f"{fmt(x['paired_saving_median'])} [{fmt(x['ci95_low'])}, {fmt(x['ci95_high'])}]")
 rows.append('| '+c.replace('_','.',1)+' | '+str(ss[c,'G0']['N'])+'/3 | '+' | '.join(vals+eff)+' |')
 trows.append('| '+c.replace('_','.',1)+' | '+' | '.join(fmt(ts[c,g]['pooled_submitted_tps'])for g in ['G0','G1','G2','G3'])+' |')
counts={}
for l,r in [('G0','G1'),('G1','G2'),('G0','G2'),('G0','G3')]:
 z=[x for x in E if x['left']==l and x['right']==r and x['metric']=='e2e_ms'];counts[l+r]={'CI_positive':sum(float(x['ci95_low'])>0 for x in z),'CI_negative':sum(float(x['ci95_high'])<0 for x in z),'three_batches_positive':sum(x['all_batches_positive']=='True'for x in z)}
summary='\n'.join(f"- {a}→{b}：37方法中，CI全正{counts[a+b]['CI_positive']}项，全负{counts[a+b]['CI_negative']}项；三批配对中位数均正{counts[a+b]['three_batches_positive']}项。"for a,b in [('G0','G1'),('G1','G2'),('G0','G2'),('G0','G3')])
limits='只有3个独立批次；一般每组12次，alterAdminAddress每组3次，raffle每组9次。95%CI采用批次/槽位两层成对bootstrap 10,000次；3个批次不足以稳定估计总体尾部或消除环境/顺序混杂。37方法、多对照未作多重比较校正，因此局部CI为探索性信号，不是普遍收益证明。四组顺序平衡但三个批次无法覆盖四个位置的全部排列。'
doc('E2E_RESULTS.md','# 真实 SDK 提交响应延迟\n\n全部单位ms，P50=Median。完整客户端窗口，非S1、非NewInstance。正配对节省表示右侧更快；配对按同一方法/批次/槽位，不是独立Median相减。\n\n'+'\n'.join(rows)+'\n\n'+summary+'\n\n'+limits+'\n\n逐批Mean/P50/P95：STATISTICS.csv；直接配对、正向比例和三批差值：PAIRED_EFFECTS.csv；顺序分层：ORDER_EFFECTS.csv。无首笔剔除。')
doc('TPS_RESULTS.md','# 同步单客户端提交 TPS\n\n表中为三批成功提交数之和/三批正式窗口秒数之和；不是三批TPS的简单平均，不是节点最大TPS。每笔同步返回后才发下一笔。\n\n'+'\n'.join(trows)+'\n\nTHROUGHPUT.csv保留每个窗口起止、分子、成功/失败/超时及客户端响应率；TPS_STATISTICS.csv给出逐批结果；TPS_EFFECTS.csv仅有3个配对窗口的探索性增量CI。主矩阵1728/1728成功提交，0超时、0拒绝；原无效raffle窗口单列，不混入此成功率。\n\n'+limits)
# VM vs E2E direct paired effects, preserving repeated execution sums.
vr=['| 方法 | Copy VM节省 | Copy E2E节省 | A+Copy VM节省 | A+Copy E2E节省 |','|---|---:|---:|---:|---:|']
for c in C:
 vals=[]
 for g in ['G1','G2']:
  for metric in ['vm_inner_ms','e2e_ms']:
   x=ee.get((c,'G0',g,metric));vals.append(fmt(x['paired_saving_median'])if x else'未记录')
 vr.append('| '+c.replace('_','.',1)+' | '+' | '.join(vals)+' |')
doc('VM_E2E_ATTRIBUTION.md','# VM 与端到端收益\n\n'+'\n'.join(vr)+'\n\nVM列为同一TxID全部根invoke_end单调计时之和的配对节省；E2E为SDK窗口。1728笔中1584笔观察到1次根执行，144笔观察到2次：erc721.accountTokens、itinerary.queryHistory、itinerary.saveAndQueryHistory各48笔。不能把这些交易只算一次VM执行；没有仅凭计数判定重执行原因。buyNow每次观察到六次真实下游调用，子调用嵌套于根Invoke，未重复加到根时长。\n\nNewInstance、Copy、_start、S0→S1、CallMethod、Close原始分段见VM_EVENTS.csv；NewInstance不含随后Copy，S0→S1包含创建Store、WASI/import、NewInstance与Copy，_start和Close嵌于完整Invoke。首次Module准备含模板/编译，单列MODULE_PREPARATION.csv，正式前Query已加载缓存，但每次业务仍创建独立Instance。\n\n本轮VM节省并未普遍转化为稳定客户端收益；多数E2E CI跨零。PutBlock、RPC通知、排队及其他宿主开销位于真实路径内，但本轮没有对全部VM外耗时作无重叠的细分，不能认定某个组件是负收益根因。禁止跨进程绝对时间直接相减。外层REUSE_VM日志使用UnixNano，保留其墙钟局限；Owner内部与客户端分别使用本进程单调时钟。\n\n保留既有诊断日志（含ReadMemStats）；各组相同，但其扰动未单独量化，本结果不是低插桩生产基准。')
post=[json.loads(f.read_text())for f in(P/'raw_logs').glob('post-*-postcheck.json')];par=[json.loads(f.read_text())for f in(P/'raw_logs').glob('*parity.json')];bad=[x for x in R if x.get('exit_code')not in['0',0]or str(x.get('pid_exited'))not in['True','true']or str(x.get('cgroup_empty'))not in['True','true']or str(x.get('stores_created'))!=str(x.get('stores_closed'))or str(x.get('instances_created'))!=str(x.get('instances_closed'))]
peak=max(float(x['rss_peak_mib'])for x in R);threads=max(int(x['threads_peak'])for x in R if x.get('threads_peak'));errors=[x for x in post if'exception'in x]
assert len(T)==1728 and len(W)==444 and len(post)==148 and all(x['passed']for x in post)and not bad,(len(T),len(W),len(post),len(bad))
doc('CORRECTNESS.md',f'''# 正确性和失败保留

37业务方法×4配置，均通过独立功能预检和3批正式执行；1728正式调用全部同步成功，并由GetTxWithRWSetByTxId确认相同TxID、高度、ContractResult。149份配对核对文件（含预检）均通过。四组逐槽Gas、返回值、排序读写集、事件及已写键的实际状态回读一致。TxID/区块高度等元数据按配对标签规范化；历史查询记录时间仅在识别的HistoryValue结构中规范化，规则见scripts/parity.py。

不能将“已写键最终状态一致”扩大为全账本字节哈希一致。每个配置的batch3账本独立重启，148/148次重新查询交易、高度和状态通过。{len(errors)}次真实错误提交/回滚检查通过：每合约每配置无效export，以及raffle空名单真实Guest错误；无写集，已知状态投影不变。其余业务特定异常分支、真实Table函数身份均not_tested，不标记为全面安全认证。

buyNow使用真实identity/ERC721/exchange，48笔正式根调用各保留六次子调用，无固定返回值。根Gas同槽四组相同；不同token/槽可为12,620,047或12,620,048，未强制跨输入相等。compute.bigNumCal根Gas120,135，fact.saveAndFindByFileHash285，均四组一致。

原raffle4次计划超过三人名单，第三次后为空，第四次真实Guest ExitCode2。整个原窗口排除，原case/client/node日志完整保留；新revision用相同Alice/Bob/Carol名单执行3次，预期Carol/Alice/Bob，独立3批，每组9次。未添加人口或改算法。失败不是资源异常，节点正常退出。最早node编译GetState符号错误及node2基础设施预检亦保留，不算正式样本。

异常测试和重启验证在主采样后单列；不宣称所有方法异常分支已在主实验前覆盖。''')
doc('SAFETY_GATE.md',f'''# 安全准入与结果

条件通过：限定单节点、Common(write_block_type=0)、SDK同步单客户端、独立Store Owner串行创建/执行/同步Close。保留Step35C RPC/Core/PutBlock排空协议与Selector修复库；没有原池后台Fresh/异步Close，没有提高资源阈值。

资源表含{len(R)}个有结构化结果的进程（部署、预检、正式、重启；含失败夹具进程）。全部Store/Instance创建关闭配平、managed_pending=0、退出码0、PID退出、cgroup空。观测RSS峰值{peak:.2f}MiB <1536MiB，OS线程峰值{threads}<220；无STOP_SHARED触发。25ms采样可能漏掉瞬时峰值；Go heap为事件边界采样，非连续峰值。goroutine未在所有正式进程独立采样，具体CSV标not_recorded；Selector线程身份/数量未逐次检测，以固定so哈希+Step35B已有验证为依据，不把OS线程数等同Selector数。

148次重启读回和{len(errors)}次错误提交后回滚/关闭通过。此次未重复全部在途Reset/Stop压力矩阵，依赖35C已有证据；不批准多客户端、Quick、异步提交、多节点或长期资源稳定性结论。正式有限E2E/TPS已在此边界内完成。''')
doc('FIXTURE_STATUS.md','# 夹具状态\n\n8个独立部署业务合约、37个业务方法均PASSED；状态和每组实测N在METHOD_COVERAGE.csv。identity.callerAddress已通过真实独立节点、自合约下游执行，不沿用Step33旧blocked。exchange保留六次真实子调用。大输入按冻结配置执行512KiB/1MiB，ioHeavy原100×256，不缩减输入。\n\n扫描2590个Go/WASM文件、40个export源码、617份WASM（含历史/重复）。清单121行包含重复源码、辅助模块和非业务exports，不等于121个独立合约。八个业务家族的生命周期/Gas/库预热/人为延迟探针登记为未纳入业务性能；不是PASSED。构建来源95903a3及Step33冻结A产物；完整路径、哈希见清单与inputs/variants.json。\n\n首轮raffle夹具失败及revision原因见CORRECTNESS.md；所有其他方法无需改写Guest。')
doc('README.md',f'''# Step-36：安全Fresh / Copy / A+Copy / A-only真实节点E2E

已完成8个独立部署Go/WASM业务合约、37个业务方法的四组对照。每方法3个独立批次，共444个正式窗口、1728次有效提交；一般每组12次，identity.alterAdminAddress每组3次、raffle.raffle每组9次。无生产代码覆盖、无并发压测、无远程推送。

G0 Fresh；G1 Copy；G2 A+Copy；G3 A-only。同源Step18/33家族，无B1。原始样本、失败窗口和反向收益均保留。测量SDK同步提交响应，而非仅AddTx ACK；提交结果用链上RWSet查询与重启后读回复核。

{summary}

结论：VM内部初始化收益不能自动推出客户端收益。本轮多数方法E2E CI跨零，少数出现正/负信号；A+Copy没有得到普遍稳定优于Copy的证据。具体方法、P50/P95和TPS见E2E_RESULTS.md与TPS_RESULTS.md。单客户端TPS不代表节点最大吞吐。

RSS观测峰值{peak:.2f}MiB、OS线程峰值{threads}，原1536MiB守卫保留。148次重启及{len(errors)}次真实失败/回滚检查通过。不能据此认证所有异常路径、Table身份或原池并发。

复算：`python3 scripts/analyze.py`，随后`python3 scripts/report.py`。脚本只读原始JSON/日志并重建本目录派生CSV/报告，不启动节点。执行实验入口scripts/experiment.py，专项raffle脚本retry_raffle.py，重启验证postcheck_all.py；均有已完成结果检查，禁止无理由重跑。

{limits}

详见EXPERIMENT_DESIGN.md、SDK_TIMING_CODE.md、TPS_MEASUREMENT.md、SAFETY_GATE.md、CORRECTNESS.md。''')
(P/'audit/final-counts.json').write_text(json.dumps(dict(contracts=8,methods=37,formal_transactions=len(T),formal_windows=len(W),postchecks=len(post),error_checks=len(errors),resource_processes=len(R),resource_peak_mib=peak,threads_peak=threads,e2e_effect_counts=counts),indent=2))
print((P/'audit/final-counts.json').read_text())

with(P/"VM_E2E_ATTRIBUTION.md").open("a")as f:f.write("\n"+(P/"audit/vm-extra.md").read_text())
