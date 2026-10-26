"""Render reports from existing primary and balanced CSVs. Never executes guest code."""
from pathlib import Path
import csv,json,statistics as st
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
def write_csv(n,rs):
    with(P/n).open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def fmt(x):return f'{float(x):.3f}'
primary=read('ppt_table.csv');balanced=read('balanced_ppt_table.csv');summ=read('summary.csv');eff=read('paired_effects.csv')
bs=read('balanced_summary.csv');be=read('balanced_paired_effects.csv');prep=read('preparation.csv');samples=read('samples.csv');resources=read('resource_summary.csv');variants=read('variants.csv')
env=json.loads((P/'environment.json').read_text())
def table(rows):
    t='| 合约/方法 | A0 Median | A1 Median | A0 P95 | A1 P95 | 配对节省 Median [95% CI] | 对数/独立批 |\n|---|---:|---:|---:|---:|---:|---:|\n'
    for r in rows:
        name={'compute':'compute.bigNumCal','fact':'fact.saveAndFindByFileHash','erc721':'erc721.mint','exchange':'exchange.buyNow'}[r['contract']]
        t+=f"| {name} | {fmt(r['baseline_median_ms'])} | {fmt(r['copy_median_ms'])} | {fmt(r['baseline_p95_ms'])} | {fmt(r['copy_p95_ms'])} | {fmt(r['median_saving_ms'])} [{fmt(r['median_ci95_low_ms'])}, {fmt(r['median_ci95_high_ms'])}] | {r['n_pairs']}/3 |\n"
    return t
stage='| 合约 | 指标 | A0 Median | A1 Median | 配对节省 [95% CI] |\n|---|---|---:|---:|---:|\n'
for c in ['compute','fact','erc721','exchange']:
    for metric in ['newinstance','copy','static_init','wasi_imports','to_s1','start','to_s2','callmethod','to_s3','close','invoke']:
        a=next(x for x in summ if x['contract']==c and x['variant']=='A0'and x['metric']==metric)
        b=next(x for x in summ if x['contract']==c and x['variant']=='A1'and x['metric']==metric)
        e=next(x for x in eff if x['contract']==c and x['metric']==metric)
        stage+=f"| {c} | {metric} | {fmt(a['median_ms'])} | {fmt(b['median_ms'])} | {fmt(e['median_saving_ms'])} [{fmt(e['median_ci95_low_ms'])}, {fmt(e['median_ci95_high_ms'])}] |\n"

formal_labels={r['label']for r in resources if r['phase']=='formal'and '-balanced-'not in r['label']}
cost=[]
for c in ['compute','fact','erc721','exchange','identity']:
    ts=[r for r in prep if r['event']=='template'and r['contract']==c and r['label']in formal_labels]
    vr=next(r for r in variants if r['contract']==c and r['variant']=='A1')
    sr=next(r for r in samples if r['contract']==c and r['variant']=='A1')
    mods={v:[int(r['module_prepare_ns'])/1e6 for r in prep if r['event']=='module'and r['contract']==c and r['variant']==v and r['label']in formal_labels]for v in ['A0','A1']}
    cost.append(dict(contract=c,preparation_observations=len(ts),template_prepare_median_ms=st.median(int(r['prepare_ns'])/1e6 for r in ts),A0_module_prepare_median_ms=st.median(mods['A0']),A1_module_prepare_median_ms=st.median(mods['A1']),image_bytes=int(vr['template_image_bytes']),image_MiB=int(vr['template_image_bytes'])/2**20,range_count=int(vr['copy_ranges']),range_entry_bytes_lower_bound=16*int(vr['copy_ranges']),nodata_wasm_bytes=int(vr['wasm_bytes']),image_ranges_nodata_bytes_lower_bound=int(vr['template_image_bytes'])+16*int(vr['copy_ranges'])+int(vr['wasm_bytes']),copy_bytes=int(sr['copy_bytes']),native_cache_bytes='not_measured',scope='primary formal processes; template_prepare includes SHA audit; Go backing capacity/native overhead not included'))
write_csv('template_cost.csv',cost)
ct='| 合约 | 模板准备ms | A0 Module准备ms | A1 Module准备ms | Image MiB | 区间数 | 每次Copy Bytes |\n|---|---:|---:|---:|---:|---:|---:|\n'
for r in cost:ct+=f"| {r['contract']} | {fmt(r['template_prepare_median_ms'])} | {fmt(r['A0_module_prepare_median_ms'])} | {fmt(r['A1_module_prepare_median_ms'])} | {r['image_MiB']:.4f} | {r['range_count']} | {r['copy_bytes']} |\n"

text=f'''# Step-22：Copy方案串行性能与正确性验证

2026-10-26（Asia/Shanghai）。**已真实执行**原始随机顺序三批及单列的平衡顺序三批。既有Host区间Copy减少的主要是S0→S1静态初始化：NewInstance省掉active Data初始化，再支付Host Copy成本。未改Copy算法，未启用Arena/PB，未运行原池或节点并发压测。

在顺序平衡补充中，compute/ERC721完整串行Invoke分别节省中位数0.738/0.903ms，6/6对正向；fact一批接近零；exchange主实验第三批反向。**不能把这些短小样本写成通用稳定收益或生产收益**。原主实验完整Invoke的CI全部跨零，仍全部保留。

## 测量范围

每合约/变体一个所有者线程上的Store+Module缓存；每次新WASI、新Instance，串行创建→Copy（A1）→WASI.Initialize/_start→SetGas/真实业务→Gas/result→CallDeallocate/Instance scope同步关闭。完整Invoke包含以上每次调用路径，**不含一次性模板/编译及最终Module/Store缓存销毁**。这是Step21D基础上的新串行参考管理器dRuntime.Invoke，真实SimContext和业务WASM执行；不是生产RuntimeInstance.Invoke、原池TPS或真实节点/客户端结果。

## 原始主实验，单位ms

三个单合约各3独立进程×3配对；exchange各3个独立配对批、每变体独立进程执行1根及6个真实子调用。全部保留首个正式样本，无额外预热或Sleep。

{table(primary)}
“配对节省”是每对A0−A1的中位数，**不是两组Median相减**，因此表中两者可能明显不同。P95为最近秩；N≤9时等于最大值。95%CI为先抽3个batch、再抽pair slot的10000次配对bootstrap（seed22026026）；仅作探索性区间，3批不能证明长周期稳定。

## 顺序平衡补充，独立统计，单位ms

审计发现主实验每单合约A1先7对、A0先2对；其中compute两次反向在A0先，fact/ERC不满足统一关系。不能据此认定顺序是原因。补充保持同一build4/业务/Gas/上限；每进程只2对、恰好一对A0先一对A1先，3独立批。种子只按顺序选择，不按耗时选择。原始数据未剔除、未替换、未与补充混合。

{table(balanced)}
compute两种顺序各3对均为正向，支持Copy收益不完全由原7:2顺序失衡解释；ERC721也6/6正向。fact 5/6正向，第二批配对均值仅0.002293ms（两样本均值=中位数），不足以称稳定；主实验三个合约CI跨零的事实不因补充变更。详见balanced_*、execution_order.csv、order_sensitivity.csv。

## 正确性与安全

预检逐实例在_start前核对全Memory SHA；A0/A1业务返回、根Gas、读写集、事件、等价初始/最终账本hash全部匹配；三个单合约主实验+预检各10对，平衡补充各6对；exchange主实验+预检4对，根与六个真实callee的Gas/结果/顺序都核对。所有调用均Fresh，未复用业务Instance。非Data section原字节相同，格式验证通过。

**真实Table函数身份、内部Globals动态比较、异常/OOG全路径仍not_tested**；不把静态section保持不变认定为所有动态状态均验证。标量模块做了实际写Memory后新Instance仍全零的隔离预检；真实合约在顺序fresh实例间的S1哈希/业务结果隔离已检查，未验证并发隔离。见CORRECTNESS.md与correctness.csv。

共{len(resources)}个有界测试进程（含探索和所有预检/补充）正常退出；外采样+边界日志最大RSS {max(int(r['peak_rss_kib'])for r in resources)/1024:.2f}MiB、线程{max(int(r['peak_threads'])for r in resources)}，未触发阈值。**Store缓存存活时线程随WASI创建累积**：单合约主实验结束125线程、最终owner关闭约13；exchange176→约16。只有退出进程后资源终结可确认，不认证长寿命缓存有界，不允许据此直接扩大连续100次或并发池。

## 准备与容量

{ct}
模板成本含完整SHA审计；Module准备含validate/compile及持久metadata，不是单纯编译函数。两者均独立于每次Invoke，preparation.csv还记录实验双组总准备与最终cache close。Image+16×区间数只是部分Go空间下界，plan还持有noData代码，底层capacity/Module/Store/native线程成本另计。template_cost.csv给出下界，native缓存精确大小未测。原始设计的每次Store编译约0.5–0.7秒不能算入Copy收益，本轮实际每变体每合约只准备一次。

A0/A1在同进程都保留模板和两个Module；exchange分进程也准备同样两组Module。因此RSS是**双组实验配置**，不是生产Copy独占增量RSS。未隔离的native资源成本和宽CI也不足以给可靠摊销次数。

## 版本、交付和下一步

分支 `experiment/step22-serial-static-copy`，父87eb925；实验代码冻结提交 `{env.get('source_commit','pending')}`；固定Go1.25.0/native6.0.1（SHA见environment）。最终测量binary `{env['binary_sha256']}`。所有原WASM/hash、noData/template SHA在variants.csv；仅ERC721与Step16旧binary不同，沿用Step21D候选，本轮两组完全相同。SDK精确原二进制构建来源未重新认证。

- [RESULTS.md](RESULTS.md)：完整阶段表及exchange反向样本定位。
- [AUDIT.md](AUDIT.md)、[source.diff](source.diff)、[audit/source_hashes.json](audit/source_hashes.json)：真实函数/行号、版本和增量源。
- [CORRECTNESS.md](CORRECTNESS.md)、[correctness.csv](correctness.csv)、[balanced_correctness.csv](balanced_correctness.csv)：通过范围与not_tested。
- [samples.csv](samples.csv)、[summary.csv](summary.csv)、[paired_effects.csv](paired_effects.csv)、balanced_*：全部原始Invoke行（含init、子调用、预检），性能筛选明确保留在脚本中。
- [raw_logs](raw_logs/)、[resource_summary.csv](resource_summary.csv)、[template_cost.csv](template_cost.csv)、[environment.json](environment.json)：原命令、receipt、资源与准备成本。
- [RUNNING.md](RUNNING.md)、[PROGRESS.md](PROGRESS.md)：复现、保护、恢复与回滚。只提交独立分支，不push。

下一步应先拆分WASI/import准备窗口的波动及解释Store持有的线程生命周期，在同样有界进程中做更多独立、顺序平衡批次；Table/异常语义仍需补齐。不能把本轮成功视为默认共享Store池或生产启用许可。本轮不继续实现优化或节点实验。
'''
(P/'README.md').write_text(text)
results=f'''# Step-22 分阶段结果

以下为主实验，同一条样本的累计S1/S2/S3及Invoke是嵌套边界，不相加。NewInstance不含Copy；static_init是逐行NewInstance+Copy再统计。所有单位ms。

{stage}
完整分位数/均值/N及Median CI在summary.csv，逐对记录在paired_samples.csv，配对Mean及Median CI在paired_effects.csv。平衡补充的同一组字段在balanced_summary/paired_effects，不能混合批次相减。

## Copy减少什么

主实验三个单合约static_init配对中位数节省0.938/0.786/0.829ms，全部9/9正向；累计to_s1分别节省0.693/0.353/0.743ms。额外的WASI/import准备及其他前导开销，使到S1的实际收益小于只看标准Data初始化移除的数字。启动和业务开销的变化没有被证明是Copy的因果效果。

平衡补充static_init分别节省0.774/0.589/0.792ms；to_s1分别0.759/0.857/0.699ms。新实例化API由约2ms降到约0.1ms，但必须支付约1ms的restore，不能把API差值直接当作完整路径收益。

## exchange真实调用链

`buyNow → identity.addWriteList → identity.isApprovedUser → identity.isApprovedUser → erc721.mint → erc721.setApprovalForAll2 → erc721.transferFrom`，六个callee均深度1、真实WASM/真实TxSimContext，未伪造成功响应。根CallMethod已包含子Invoke，不再次相加。exchange_transaction_stages.csv只对不相互嵌套的七次static/start/close求和。

第三批：A0根Invoke66.385277ms，A1为82.150221ms，反向15.764944ms；根CallMethod增加16.876238ms，六个子Invoke总和增加16.832774ms。七个Instance的NewInstance+Copy总和反而节省5.195181ms。

明确的大波动在其中erc721.mint的wasi_imports窗口：A0 15.836714ms，A1 34.912888ms（精确值以outlier_stages.csv为准）；它包含Finalize/GenerateImportObject/host GetImports。**已定位到计时窗口，尚未定位到GC、调度或native线程创建的具体原因**。没有数据支持把负收益归于memcpy慢、业务变更或节点共识。本实验没有节点/客户端阶段。

## 统计与局限

三独立进程批不等于每对均独立环境。主实验随机顺序有7:2失衡，补充逐批平衡但属于后续审计触发的小样本补充，均分表。P95=max，置信区间不能保证未来长周期稳定。不预设内存预热或segment数量是原因。

进程内正式性能没有S1 hash；预检hash会拉长S2/Invoke，严禁混入。父Invoke包含子调用日志开销；批末Store清理和部分native资源终结不在单Invoke中。原池/真实节点/长期吞吐仍未测定。
'''
# Use exact raw values in the outlier discussion.
outliers=[]
for r in samples:
    if r['label'].startswith('exchange-batch-3-')and r['method']!='init_contract':
        outliers.append({k:r[k]for k in ['label','variant','contract','method','depth','instance_id','wasi_imports_ns','newinstance_ns','copy_ns','start_ns','callmethod_ns','invoke_ns']})
write_csv('outlier_stages.csv',outliers)
for r in outliers:
    if r['contract']=='erc721'and r['method']=='mint':
        old='15.836714'if r['variant']=='A0'else'34.912888'
        results=results.replace(old,f"{int(r['wasi_imports_ns'])/1e6:.6f}")
(P/'RESULTS.md').write_text(results)

correct='''# Step-22 正确性范围

所有结果限定为tested_scope_pass，不认证production_safe。

| 项目 | 实际证据 | 状态/限制 |
|---|---|---|
| WASM格式 | 原版与noData均走ValidateModule/NewModule | tested_pass |
| S1 Memory | 最终build4预检，在_start前全Memory SHA与预计算Image相等 | tested_pass，正式性能不做hash |
| Fresh与隔离 | 每次新Instance/WASI；used保护；标量写Memory→下一实例仍零；真实合约下一fresh S1 hash无前次业务修改 | tested_pass仅串行范围，无并发隔离认证 |
| 返回/Gas | compute固定计算结果、fact JSON、mint结果及owner、buyNow结果及最终owner；同输入逐对比较 | tested_pass |
| 读写/事件 | 同一初始账本clone、相同TxID/参数、实际RWSet/ContractEvent、before/after ledger hash | tested_pass，不是相同失败返回 |
| exchange | 真registry/bytecode/TxSimContext，六个真实callee全成功，逐callee结果/Gas/调用顺序 | tested_pass指定成功路径 |
| Globals | 原Global section原字节保留、Go启动/业务实际成功 | 内部mutable globals逐元素动态等价not_tested |
| Table | 原Table/Element section逐字节保留、真实Go间接调用实际执行 | 真实Table各元素函数身份not_tested；未将nullness当身份 |
| 异常/回滚/OOG | 没有专门guest错误/越界/OOG业务样本 | not_tested，不能用成功路径推出异常等价 |
| 模板只读 | restore只有Image读取，初始Image hash已记录；真实fresh实例S1一致 | 运行末全Image再次hash not_tested，不认证并发只读机制 |
| 回收 | 同owner显式Close，每实例ManagedCount回到起点，缓存尾部计数0，所有进程已退出 | tested_pass注册边界；native长期有界not_tested |

主实验+正确性预检：compute/fact/ERC各10对；顺序平衡补充各6对；exchange合计4对。所有同配对根Gas相等；成功路径Gas：compute105920，fact1585，ERC mint15449，exchange根12767294。真实exchange各子Gas以audit/comparison-*.json为准，不拿其他版本的业务参数/Gas相减。

业务状态来自Step21D真实fixture：固定公开测试公钥/逻辑member provider、BlockVersion1/ETHEREUM地址类型；不是完整节点ACL/共识/数据库认证。初始化真实执行，样本间回到同一post-init账本；ERC每配对tokenId规则唯一，A0/A1使用同一个tokenId且分别恢复账本，因此不把重复mint失败当成功。

代码保留既有CallMethod错误被GetGas错误覆盖的runtime行为，但单独记录call_error_observed；正式样本全部<nil>。此事实不免除异常路径未覆盖的限制。无Gas逻辑更改，无跨不同逻辑WASM强求Gas相等。
'''
(P/'CORRECTNESS.md').write_text(correct)
(P/'ENVIRONMENT.md').write_text(f'''# Step-22 环境

- 日期2026-10-26（Asia/Shanghai），WSL boot ID前后一致，未发生本轮可观察的WSL重启。
- 父commit87eb9256d5617b1ea07e7ea23e820f4720ff819b；实验代码冻结提交{env.get('source_commit','pending')}；独立分支experiment/step22-serial-static-copy，执行工作树/home/frankie/mygitprojects/.worktrees/cvw-step22。
- {env['go_version']}；{env['os']}；CPU Intel Core Ultra 9 285H，16逻辑核；WSL可见约31GiB内存/8GiB swap，测试未用swap。未固定CPU亲和/频率，未采GC暂停或逐线程调度事件。
- 固定GOMAXPROCS2/GOGC100；同binary同时运行A0/A1，无100ms Sleep。
- native6.0.1 SHA {env['config']['settings']['native_sha']}；动态加载位置核对audit/ldd.txt；精确源码/构建映射缺失仍保留。
- 最终build4 SHA {env['binary_sha256']}；早期build3 SHA {env['prior_preflight_binary_sha256']}，仅探索预检。
- config SHA {env['config_sha']}；Gas map/MaxPages固定，runtimeGasLimit2^31−1，Module初始meter1e19。
- source.diff相对父D私有模块；仅四文件变化，两新测试文件、D运行器实验分派、fixture放行fact。managed.go/dCompile以及其余绑定全部保持D版；哈希见audit/source_hashes.json。
- 原WASM、noData与Image SHA逐合约见variants.csv；所有A0/A1逻辑source hash相同。ERC与Step16旧artifact不同（9b6e vs4fba），另外四个相同；audit/step16_artifact_identity.json保留核对。
- 附近合约源声明SDK v0.1.3，但既有WASM精确原始构建来源未独立重新证明；未重编译或改SDK。
- 依赖本地Step21C worktree/module cache，不更新版本；go.mod/go.sum/go.work/source/native hashes已存。
- ResourceMax2GiB、RSS软1536MiB；TasksMax256、线程软220；Runtime60s/Go timeout45s；全机MemAvailable最少8GiB、swapUsed最多1GiB；未提高阈值。
- 主实验和补充共33个测试进程均退出，后检查无Step22活动unit。详见audit/final-health.json与resource_summary.csv。

完整可机读环境environment.json；原执行命令raw_logs/*-command.json。build4完整手工orchestrator命令未另存原始JSON，但保留构建输出、binary/source hash；scripts/build.py提供同编译设置的重建命令，不能把重建命令伪称原始launcher逐字记录。
''')
print('rendered README, RESULTS, CORRECTNESS, ENVIRONMENT, template_cost and outlier_stages')
