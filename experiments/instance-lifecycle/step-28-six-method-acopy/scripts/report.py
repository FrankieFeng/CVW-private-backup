from pathlib import Path
import csv,json,statistics as st,hashlib,subprocess
P=Path(__file__).resolve().parents[1]
def rows(n):return list(csv.DictReader((P/n).open()))
E=rows('PAIRED_EFFECTS.csv');S=rows('SUMMARY.csv');D=rows('STRATIFIED_EFFECTS.csv');R=rows('RESOURCE_SUMMARY.csv');C=rows('CORRECTNESS.csv');T=rows('TIMING.csv');ST=rows('STAGE_EFFECTS.csv');M=rows('MODULE_PREPARATION.csv')
cases=['bigNumCal','hashCal','normalCal','fact','erc721','buyNow'];names=['compute.bigNumCal','compute.hashCal','compute.normalCal','fact.saveAndFindByFileHash','erc721.mint','exchange.buyNow'];N=dict(zip(cases,names))
fmt=lambda x:f'{float(x):.3f}'
def sm(c,g,m):return next(r for r in S if r['case']==c and r['group']==g and r['metric']==m)
def se(c,l,r,m):return next(x for x in ST if x['case']==c and x['left']==l and x['right']==r and x['metric']==m)
def criterion(e):
 vals=[float(r['paired_save_median_ms'])for r in D if r['case']==e['case']and r['left']==e['left']and r['right']==e['right']and r['stratum']=='batch']
 return '三批同向、总体CI>0'if float(e['ci95_low_ms'])>0 and all(v>0 for v in vals)else '总体CI>0，批次有反向'if float(e['ci95_low_ms'])>0 else 'CI跨零，未确认稳定收益'if float(e['ci95_high_ms'])>=0 else '总体CI<0'
lines=['# Step-28：六方法独立新样本结果','', '全部为本轮新执行的同源Step18/P0/plain家族；历史数据不进入本轮统计。G0=Fresh Baseline，G1=Fresh+Copy，G2=Fresh+A+Copy。正的配对节省=左−右，右组更快。三组共享相同逻辑源/业务输入/初始账本；A改变WASM布局和哈希。','', '## 完整Invoke绝对耗时','', '| 方法 | 有效区块/批 | G0 Median / Mean / P95 ms | G1 Median / Mean / P95 ms | G2 Median / Mean / P95 ms |','|---|---:|---:|---:|---:|']
for c in cases:
 ss=[sm(c,g,'invoke_ns')for g in ['G0','G1','G2']];lines.append('| '+N[c]+' | '+ss[0]['n']+'/'+ss[0]['batches']+' | '+' | '.join(' / '.join(fmt(r[k])for k in ['median_ms','mean_ms','p95_ms'])for r in ss)+' |')
lines+=['','## 同一区块直接配对结果','', '95%CI为10000次batch→整块bootstrap，固定seed280027+case×10+edge；P95和CI端点线性插值。三组整块对应，不用独立Median相减。仅3批，CI为探索性区间，18项主比较未校正多重性；三个批次不是跨天长期验证。','', '| 方法 | 对照 | N | 配对节省Median [95%CI] ms | 正向/总数 | 配对相对节省Median | P95右−左 ms | 判断 |','|---|---|---:|---:|---:|---:|---:|---|']
for e in E:lines.append('| '+N[e['case']]+' | '+e['left']+'→'+e['right']+' | '+e['n']+' | '+fmt(e['paired_save_median_ms'])+' ['+fmt(e['ci95_low_ms'])+', '+fmt(e['ci95_high_ms'])+'] | '+e['positive_count']+'/'+e['n']+' | '+fmt(e['median_pair_relative_percent'])+'% | '+fmt(e['p95_change_ms'])+' | '+criterion(e)+' |')
lines+=['','## 批次与调用顺序','', '| 方法 | 对照 | 批1 / 批2 / 批3节省Median ms | 左先 / 右先节省Median ms |','|---|---|---:|---:|']
for e in E:
 rr=[r for r in D if r['case']==e['case']and r['left']==e['left']and r['right']==e['right']];b=sorted([r for r in rr if r['stratum']=='batch'],key=lambda r:r['value']);o={r['value']:r for r in rr if r['stratum']=='left_before_right'}
 lines.append('| '+N[e['case']]+' | '+e['left']+'→'+e['right']+' | '+' / '.join(fmt(r['paired_save_median_ms'])for r in b)+' | '+' / '.join(fmt(o[k]['paired_save_median_ms'])for k in ['True','False'])+' |')
lines+=['','30区块中六种排列各5次，每个组各占第一/第二/第三10次。Module准备和init也按同一排列轮换，不能把顺序分层当作已隔离的cache或CPU机制。buyNow每组独立进程，3进程按此排列组成匹配区块；其他方法一个进程包含一个三组区块。文件STRATIFIED_EFFECTS.csv还保留六种排列细分。','', '## 阶段归因','', '| 方法 | 对照 | NewInstance节省 | Copy净节省 | S0→S1节省 | _start节省 | S1→S2节省 | export节省 | 完整Invoke节省 |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
for e in E:
 lines.append('| '+N[e['case']]+' | '+e['left']+'→'+e['right']+' | '+' | '.join(fmt(se(e['case'],e['left'],e['right'],m)['paired_save_median_ms'])for m in ['newinstance_ns','copy_ns','to_s1_ns','start_ns','s1_to_s2_ns','export_call_ns','invoke_ns'])+' |')
lines+=['','所有值ms、均为各窗口的直接配对差的中位数。Copy净节省为左Copy−右Copy，G0→G1应为负，表示新增成本。各列嵌套且分别取Median，**不可横向求和**。S1包括WASI/imports，不是NewInstance别名；S2→S3/CallMethod包含export。buyNow export/CallMethod包含所有下游完整执行，root/child时间不可相加。','', '已证实的实现机制：Copy省去active Data初始化但支付host restore；A使用原静态padding让首次arena reserve对齐，影响_start并增大初始Memory。数据能定位发生变化的窗口，不能单凭时间变化断言Go GC、CPU预热或segment数量是机制根因。','', '## 一次性准备、复制与资源','', '| 方法 | G0/G1/G2 NewInstance Median ms | G1/G2 Copy Median ms | G1/G2实际Copy bytes | G0/G1/G2 _start Median ms |','|---|---:|---:|---:|---:|']
for c in cases:
 target=[r for r in T if r['phase']=='formal'and r['case']==c and r['depth']=='0'and r['method']!='init_contract'];b=[]
 for g in ['G1','G2']:b.append(str(int(st.median(int(r['copy_bytes'])for r in target if r['group']==g))))
 lines.append('| '+N[c]+' | '+' / '.join(fmt(sm(c,g,'newinstance_ns')['median_ms'])for g in ['G0','G1','G2'])+' | '+' / '.join(fmt(sm(c,g,'copy_ns')['median_ms'])for g in ['G1','G2'])+' | '+' / '.join(b)+' | '+' / '.join(fmt(sm(c,g,'start_ns')['median_ms'])for g in ['G0','G1','G2'])+' |')
lines+=['','buyNow此表只列root；各callee记录在TIMING.csv，MODULE_PREPARATION.csv记录所有module/template的真实编译、准备耗时及容量。模板从最终WASM重建，Module在该进程内只编译一次，每次Fresh调用不重新编译。Baseline为共用oracle也预建plan，在Invoke外；本测试RSS含三组Module/两个image以及编译暂存，不能直接当生产优化的RSS增量。','', '| 合约 | G0模板image bytes | G2模板image bytes | G2增加 bytes | 模板准备Median ms（G0/G2） |','|---|---:|---:|---:|---:|']
for c in ['compute','fact','erc721','exchange','identity']:
 vals={g:[r for r in M if r['phase']=='formal'and r['event']=='template'and r['contract']==c and r['group']==g]for g in ['G0','G2']}
 # G0/G1共用模板，若G1先准备则事件group=G1。
 vals['G0']=[r for r in M if r['phase']=='formal'and r['event']=='template'and r['contract']==c and r['group']in['G0','G1']]
 a,b=vals['G0'],vals['G2'];size=[int(x[0]['image_bytes'])for x in [a,b]]
 lines.append('| '+c+' | '+str(size[0])+' | '+str(size[1])+' | '+str(size[1]-size[0])+' | '+' / '.join(fmt(st.median(int(v['prepare_ns'])/1e6 for v in x))for x in[a,b])+' |')
lines+=['','模板image容量与同模块初始Linear Memory大小相同；A的额外页在每个Fresh实例上也需要地址空间/实际按需物理页，两者不能直接相加当RSS。模块native内部峰值未逐分配跟踪。','', f"本轮{len(R)}个Guest测试进程，最大采样RSS {max(int(r['peak_rss_kib'])for r in R)/1024:.1f}MiB，最大线程{max(int(r['peak_threads'])for r in R)}；单合约最多{max(int(r['peak_threads'])for r in R if r['case']not in ['buyNow','alignment'])}线程。所有过程退出、cgroup为空、manager created=closed、managed/pending=0。RESOURCE_SUMMARY.csv保留每个进程的RSS/heap/线程/退出；RSS为轮询与边界观测峰值，不是无遗漏的内核峰值。未提高原软限：单合约768MiB/125线程，真实跨合约1536MiB/220线程；硬限2GiB/256tasks，45s测试/60s进程。长Store WASI线程累积风险仍未解决。",'', '## 与历史证据的关系','', 'Step24B原件100循环bigNum与本轮10000循环不同家族，不比较绝对耗时/Gas。Step26仅复算Step25旧18对，并不是独立新批次；本轮180新区块可独立检查其倾向，但不合并样本。Step27没有稳定复现8.294ms的Reuse/Fresh导出差，Step18家族Copy→A+Copy的normalCal CI跨零。本轮没有Reuse组，只能复核该家族Fresh/Copy/A+Copy排序及Guest波动，不能确认或否认Reuse/Fresh异常机制。','', '## 下一步范围','', '以总体CI和三批方向同时判断哪些方法值得继续；跨零/批次反转的方法保留专项分析。当前支持的是有界独立Store串行路径，不能直接进入原池并发或宣称节点收益。继续节点前需解决Store长期WASI线程回收、原池并发所有权、真实Table身份和更完整异常/回滚覆盖。']
(P/'RESULTS.md').write_text('\n'.join(lines)+'\n')
lines=['# Step-28正确性与边界','', '六方法三组均完成新的功能预检；每个正式三组区块逐对严格比较根Gas、返回值、状态码、完整根读写集、事件、初始/最终账本摘要。对buyNow还对root和六个真实子调用逐次核对contract/method/order/depth/TxID/Gas/code/result/message，不能仅凭Go测试PASS判成功。','', '| 方法 | 有效正式区块 | 独立批 | 根Gas（三组一致） | 真实调用/根交易 |','|---|---:|---:|---:|---:|']
for c in cases:
 rr=[r for r in C if r['case']==c and r['phase']=='formal'];lines.append('| '+N[c]+' | '+str(len(rr))+' | '+str(len(set(r['batch']for r in rr)))+' | '+','.join(sorted(set(r['gas']for r in rr)))+' | '+','.join(sorted(set(r['calls']for r in rr)))+' |')
lines+=['','每次完整账本另存`raw_logs/*-receipts/target-Gx-ledger.json`：由实际init/目标RW写集重放，并逐阶段复核进程内snapshot.hash()的SHA256；CHAIN_CONFIG值直接取真实setup-identity读集，非手填。三组重建的完整最终账本逐键/值相等。未成功的交易不提交写集。原始回执包含返回bytes(base64)、所有读写、事件和根/子调用记录，保留可复核数据。','', '## buyNow真实与失败路径','', 'init顺序identity→ERC721→exchange；真实调用顺序exchange.buyNow→identity.addWriteList→identity.isApprovedUser(from)→identity.isApprovedUser(to)→erc721.mint→erc721.setApprovalForAll2→erc721.transferFrom。每次新建目标token1的等价初始账本，验证最终owner=to和buyNow success。G2对root、identity和ERC721全部应用各自A+Copy。','', '空参数在root拒绝；重复token预置已有owner，使第4个子调用mint失败，此前identity写入不得提交。两条路径每组三个独立进程之一，各G0/G1/G2一次，均真实运行并核对Gas/结果/读写/事件/最终账本。它们是小样本功能证据，不是覆盖所有异常。']
for kind in ['empty','duplicate']:
 d=json.loads((P/'raw_logs'/f'exception-{kind}-parity.json').read_text());lines.append(f"- {kind}：三组根Gas {d['gas']}、root+child调用数{d['calls']}，失败且最终账本等于初始；原始对照通过。")
lines+=['','## 不得标为通过的范围','', '- 真实Table元素函数身份：**not_tested**。Data变换保留Table/element字节与成功间接调用，不等于逐元素身份验证。','- 所有其他业务异常、深层trap、Gas耗尽、节点级回滚、共识/持久化/签名：**not_tested**。夹具使用公钥身份/真实VM状态，并非完整节点认证。','- 实例隔离：已验证每次fresh、uses_before=0、同步销毁、S1预检与各自静态模板一致、每次账本独立克隆；未做同时存活实例互写Memory压力测试，不把它标为本轮已通过。','- Store owner/生命周期：本轮有界串行guard与回收计数通过；长期Store内WASI线程/native资源完全回收仍未证明，不称生产安全。','- A跨二进制Gas不是默认假设，本轮实测三组及所有下游一致。B1未纳入，公共API未删除。']
(P/'CORRECTNESS.md').write_text('\n'.join(lines)+'\n')
lines=['# Step-28：六方法A+Copy独立收益确认','', '本轮已完成六方法功能预检、3批×10个三组配对区块/方法：**180区块、540次正式根调用**，未混入历史样本。所有有效区块完成Gas/结果/读写集/事件/完整最终账本对照；buyNow包含六次真实子调用。详细数据与限制见[RESULTS](RESULTS.md)、[CORRECTNESS](CORRECTNESS.md)、[构建来源](BUILD_LINEAGE.md)。','', '| 方法 | Copy相对Fresh | A叠加Copy | A+Copy相对Fresh |','|---|---|---|---|']
for c in cases:
 es=[e for e in E if e['case']==c];lines.append('| '+N[c]+' | '+' | '.join(fmt(e['paired_save_median_ms'])+'ms；'+criterion(e)for e in es)+' |')
lines+=['','正值为优化组节省，直接配对统计，非独立中位数相减。30区块/方法，只有3个时间批；短期单机串行证据，不是节点并发或生产收益。normalCal/buyNow不利样本全部保留。','', '运行：先检查PROGRESS/state/outcome及活跃unit，再按BUILD_LINEAGE命令恢复；`python3 -B scripts/analyze.py`、`python3 -B scripts/report.py`可只读原始测量复算汇总。不要删除outcome重跑后覆盖原记录。','', '回滚：本实验仅改本目录副本/独立分支，无生产开关需回退。停止具体`step28-<label>.service`并核对PID/cgroup为空；保留日志，切回原分支即可。禁止通配杀其他实验进程。不推送远程、不制作PPT。','', '交付：TIMING.csv包括init/preflight/正式/异常及children，`phase`、`depth`、`valid_block`区分；主表仅formal+depth0+目标方法+完整有效区块。SUMMARY、PAIRED_EFFECTS、STRATIFIED_EFFECTS、STAGE_EFFECTS、MODULE_PREPARATION、RESOURCE_SUMMARY及原始日志完整保留。PROGRESS注明失败构建，性能样本没有静默排除。']
(P/'README.md').write_text('\n'.join(lines)+'\n')
print('reports written')
