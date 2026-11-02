from pathlib import Path
import csv,json,statistics as st,collections
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
def doc(n,s):(P/n).write_text(s.strip()+'\n')
def f(x):return f'{float(x):.3f}'
S=read('SUMMARY.csv');E=read('PAIRED_EFFECTS.csv');C=read('ROOT_COST_SUMMARY.csv');R=read('RESOURCE_SUMMARY.csv');J=json.loads((P/'audit/analysis.json').read_text());gs={(x['case'],x['strategy'],x['metric']):x for x in S};ef={(x['case'],x['left'],x['right'],x['metric']):x for x in E};cases=sorted({x['case']for x in S})
def pair(c,g,m):
 x=ef[c,'C0',g,m];return f"{f(x['saving_median'])} [{f(x['ci95_low'])}, {f(x['ci95_high'])}]"
rows=['| 方法 | C0 restore P50 | C1 P50 | C2 P50 | C3 P50 | C4 P50 | C0→C2 Factory Invoke节省[CI] | C0→C4 Factory Invoke节省[CI] |','|---|---:|---:|---:|---:|---:|---:|---:|']
for c in cases:rows.append('| '+c.replace('_','.',1)+' | '+' | '.join(f(gs[c,g,'restore_ms']['p50'])for g in ['C0','C1','C2','C3','C4'])+' | '+pair(c,'C2','factory_invoke_ms')+' | '+pair(c,'C4','factory_invoke_ms')+' |')
doc('RESULTS.md','# Step-38A：主要结果\n\n单位ms。每方法6个配对区块、3个独立批次、每组每批2次；正节省=左−右，CI为未校正层级bootstrap探索性区间。完整Mean/P50/P95在SUMMARY.csv，逐笔RANGE_BENCHMARK/VM_INVOKE_BENCHMARK；配对/批次/正向率在PAIRED_EFFECTS.csv。\n\n'+'\n'.join(rows)+'\n\nC0原Ranges；C1间隙≤16B；C2≤64B；C3≤256B；C4单span；F0无Copy Fresh另列CSV。restore没有任何C0→C1/C2/C3/C4对照CI全正；C2四方法、C3两方法CI全负。Factory Invoke有少量正/负信号，但与restore并不一致，不能认定是区间优化稳定收益。\n\nSPAN相对C0：buyNow Factory配对中位退化4.868ms、CI[-5.826,-2.670]，而根restore节省0.029ms、CI[-0.120,0.335]。不把根restore当七实例全部开销；all_instance_init_ms/all_instance_restore_ms单列。单span多复制的零间隙字节已精确记录，缓存/带宽/页fault未测，不据此唯一归因。\n\n最小双侧cluster符号翻转p=.25，80项补充Holm敏感性校正无显著。该敏感性是事后诊断、不是预注册确认试验。3批、每批2笔覆盖率与尾部精度有限；保留全部不利样本，不用不同组Median之差替代配对差。')
bs=['| 方法 | NewStore µs | Builder ms | Finalize ms | WASI Imports ms | CM Imports ms | 2×Invoke SHA ms | prepare SHA+key ms | runtime clone ms |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for c in cases:
 d={x['stage']:x for x in C if x['case']==c and x['allocation_diagnostic']=='False'};bs.append('| '+c.replace('_','.',1)+' | '+f(float(d['new_store']['p50_ms'])*1000)+' | '+' | '.join(f(d[k]['p50_ms'])for k in ['wasi_builder','wasi_finalize','wasi_generate_imports','cm_get_imports','invoke_two_SHA','prepare_SHA','runtime_bytecode_clone'])+' |')
doc('STORE_WASI_RESULTS.md','# Step-38B：原C0路径成本诊断\n\n以下为time-only版本根调用窗口P50，每方法6次/3批；alloc诊断另列，不混入时间主统计。各列P50**不可相加冒充总耗时**。ROOT_PREPARATION_SHARES.csv提供同次调用可相加的顺序窗口与比例。\n\n'+'\n'.join(bs)+'\n\nNewStore本身只含新Store包装及native创建；不是“独立Store相对共享Store的增量”。本轮没有共享Store反事实。NewStore/创建至S1逐笔比率整体中位约0.261%，WASI builder/finalize/两类imports顺序窗口占比整体中位约23.015%，只是当前插桩路径的描述。\n\nBuilder源码进入native wasi_config_new并创建Tokio multi_thread Runtime（native6.0.1 wasi/mod.rs:40），Finalize消费config.runtime并绑定目标Store，不是一个便宜Go struct。尚未单独测Tokio build/defaultFS等子窗，所以不能将Builder全部耗时归到某一个子组件。\n\n校准中fact Factory Invoke的B−A中位+1.570ms，CI[0.065,2.453]；观察到明显扰动/队列或环境信号，尚未唯一分离。B数字是诊断版本原始观察，不是无扰动绝对基准。NewStore远小于SHA/Builder的量级判断有依据，但不承诺每个短阶段达到纳秒级准确。')
peak=J['max_rss_mib'];threads=J['max_threads'];npass=sum(x['passed']=='True'for x in R)
doc('README.md',f'''# Step-38：Copy区间粒度与Fresh准备成本

已完成独立原型、真实安全Fresh VM功能预检与有界正式实验。未启动节点、E2E、客户端TPS或Step39；未修改生产VM、Guest、Gas、Selector或Core/PutBlock协议。

Step-38A：8独立合约、10方法，F0/C0/C1/C2/C3/C4六组，3独立批次，每组每批2正式目标+2预热，共360正式调用、每方法6个配对区块。Step-38B：独立原始C0源码只加观测，60次time-only正式调用、20次分配诊断调用。另18个交替A/B校准进程、1个空观察窗校准进程。所有原始日志保存。

## 十项回答

1. **当前Copy瓶颈？** B观测的restore_range_loop根窗口中位约0.686～0.994ms，导出获取/借用Data视图小得多；但它同时含内存复制与循环/检查，不能把整段都叫“5万次loop纯开销”。反汇编确有memmove与slice bounds失败分支。
2. **哪种合并最好？** 没有跨方法、CI和完整Invoke共同支持的赢家。按restore独立P50，C0在5方法最低，C1在3方法最低，C4在2方法最低；这些不是配对显著结论。64/256B没有赢得restore正CI，反而有回归，保留原C0。
3. **完整Invoke是否减少？** 个别比较有探索性正向CI，也有负向；没有普遍稳定改善。必须看Factory Invoke直接配对，不只看restore；RESULTS.md和PAIRED_EFFECTS.csv保留所有结果。
4. **跨合约一致吗？** 不一致。buyNow真实六子调用完成，C4根restore变化不确定，但Factory明显反向信号，不能挑快的方法宣称通用收益。
5. **Store/WASI/Imports？** NewStore根窗口中位5.46～11.72µs；Builder0.381～0.622ms、Finalize0.086～0.120ms、WASI imports0.080～0.109ms、CM imports0.028～0.034ms。逐方法、Mean/P95与分配量见ROOT_COST_SUMMARY/STORE_WASI_BREAKDOWN，不将不同中位数相加。
6. **WASM复制/SHA值得优化？** 是下一轮更有根据的候选：root每次复制整份WASM一次；Invoke做两次整WASM SHA约2.014～2.656ms；prepare再SHA并构建key约0.976～1.661ms；clone约0.328～1.469ms。它们均位于同RunContract同步路径，但clone在Factory Invoke之前。未删除校验或共享可变字节码。
7. **新安全/正确性问题？** Fresh正式数据Gas/返回/读写集/事件/最终内存账本完全一致，所有成功进程Store/Instance配平。负对照证实restore不是Reset，脏Memory空洞不会恢复；只准已零Fresh目标。初次memory测试缺少旧guard配置而panic，修正环境后独立重试；失败原件保留。
8. **接入Step36 E2E？** 当前不建议替换C0或扩大E2E。合并候选尚无稳定净收益，且B校准fact有扰动信号；先明确主成本与测量精度。
9. **下轮函数？** 优先研究step35_node.runtime/Invoke/prepare的clone/身份验证摊销，保持不可变性和失效校验；WASI builder的runtime创建成本另做安全生命周期研究。区间策略保留C0，下一步若继续需固定字节量对照区分loop/流量，不能只追求最少范围。
10. **论文可用性？** 可陈述实现、全Memory等价测试、冻结参数及本轮原始测量；普遍收益、精确短路径成本、最佳阈值、真实E2E与长期安全仍不能定论。只有3批/每批2笔、未校正主CI、诊断扰动都必须保留。

## 上下文限制

沿用VM夹具BlockVersion=1、RunContract初始gasUsed=0和内存账本，与Step36节点scheduler/最终Gas边界不同。这里只比较本轮各策略相同上下文，不能将本轮Gas154与Step36客户端285直接比较。fact写入`{{}}`是冻结合约json.Marshal未导出字段的原行为，未改业务来加重工作负载。

## 资源与正确性

结构化进程{len(R)}个，成功{npass}，唯一失败为缺guard参数的初始化测试；观测RSS峰值{peak:.2f}MiB <1536MiB，线程峰值{threads}<220。所有成功进程native Store/Instance配平、pending0、PID退出。Native WAT包含零/非零、短/长gap、相邻、重叠与显式零覆盖、OOB、automatic-start trap、grow和实例隔离；全零/脏目标负对照见MEMORY_CHECKS.csv。业务预检逐字节核对整个初始Memory，不只hash/抽样；正式计时关闭该扫描。

## 文件导航

RESULTS.md / STORE_WASI_RESULTS.md为两部分总结；RANGE_STRATEGIES、RANGE_BENCHMARK、VM_INVOKE_BENCHMARK为逐策略/逐次；SUMMARY、PAIRED_EFFECTS为统计；STORE_WASI_BREAKDOWN、WASM_COPY_SHA_BREAKDOWN、ROOT_COST_SUMMARY为B阶段；INSTRUMENTATION_CALIBRATION为独立校准；RESOURCE_SUMMARY、NEGATIVE_RESULTS、COPY_RANGE_CORRECTNESS保留边界。

只复算：`python3 scripts/analyze.py && python3 scripts/supplement.py && python3 scripts/report.py`。不要重启experiment.py：实验已完成且会读取已完成记录。构建/运行原命令和二进制/库SHA都在audit与raw_logs。source/A是Step38A，不是Arena A；本轮所有Guest均为冻结plain G0，无Arena/PB。
''')
print('reports complete')
