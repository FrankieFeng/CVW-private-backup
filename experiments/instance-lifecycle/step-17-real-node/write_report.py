from pathlib import Path
import csv,json,statistics,math,collections,sys
O=Path(__file__).resolve().parent
read=lambda f:list(csv.DictReader((O/f).open()))
S=read('summary.csv');E=read('paired_effects.csv');C=read('cache_events.csv')
names=['compute','erc721','fact','bigInput','exchange','identity','itinerary','raffle']
def find(rows,b,c,m,mode=None):return next(r for r in rows if r['batch']==b and r['contract']==c and r['metric']==m and (mode is None or r.get('mode')==mode))
def ms(x):return f'{float(x)/1e6:.3f}'
def effect(b,c,m):
 r=find(E,b,c,m);return f'{ms(r["median_ns"])} [{ms(r["ci95_low_ns"])}, {ms(r["ci95_high_ns"])}]'
def table(metric,batches):
 out=['| 合约 | '+' | '.join(batches)+' |','|---|'+'---|'*len(batches)]
 for c in names:out.append('| '+c+' | '+' | '.join(effect(b,c,metric) for b in batches)+' |')
 return '\n'.join(out)
prep={};templates={}
for c in names:
 rows=[r for r in C if r['mode']=='optimized' and r['contract']==c][1:5] # skip deployment, use 4 formal process starts
 prep[c]=statistics.median(int(r['precompute_ns']) for r in rows)
 templates[c]=(int(rows[0]['template_bytes'])+16*int(rows[0]['range_count']))/1048576
prep_rows=[]
for c in names:
 costs=[int(r['precompute_ns']) for r in C if r['mode']=='optimized' and r['contract']==c][1:5]
 savings=[-float(find(E,b,c,'s1_ns')['median_ns']) for b in ['a','b']]
 prep_rows.append(dict(contract=c,n=4,precompute_median_ns=statistics.median(costs),precompute_min_ns=min(costs),precompute_max_ns=max(costs),template_payload_bytes=round(templates[c]*1048576),s1_amortization_best=math.ceil(prep[c]/max(savings)),s1_amortization_worst=math.ceil(prep[c]/min(savings)),node_rpc_amortization='not_established'))
sys.path.insert(0,str(O.parent/'step-15-copy-attribution'));from common import csvwrite
csvwrite(O/'template_cost.csv',prep_rows)
cachetable='\n'.join(['| 合约 | 预计算 Median ms（n=4） | Image+range payload MiB | 按本合约 S1 节省摊销次数 |','|---|---:|---:|---:|']+[f'| {r["contract"]} | {ms(r["precompute_median_ns"])} | {templates[r["contract"]]:.3f} | {r["s1_amortization_best"]}–{r["s1_amortization_worst"]} |' for r in prep_rows])
absolute=['| 合约 | A Baseline Median/P95 ms | A Optimized Median/P95 ms | B Baseline Median/P95 ms | B Optimized Median/P95 ms |','|---|---:|---:|---:|---:|']
for c in names:
 cells=[]
 for b in ['a','b']:
  for mode in ['baseline','optimized']:
   r=find(S,b,c,'client_ns',mode);cells.append(ms(r['median_ns'])+'/'+ms(r['p95_ns']))
 absolute.append('| '+c+' | '+' | '.join(cells)+' |')
readme=f'''# Step-17：静态 Memory 模板的真实节点验证

本轮完成两个相互隔离的 ChainMaker 单验证节点 TBFT 测试链，经 SDK→RPC→交易池→出块执行→提交→同步结果查询调用。**节点内 S1 收益能够保留；8 个合约的完整客户端延迟没有统一、稳定收益，暂不建议生产启用或直接投入 Wasmer COW 实现。** exchange 已完成真实跨合约成功路径，取代 step-16 的 mock 证据。原型仍有缓存生命周期和并发适用限制。

## 实验范围与版本

- CVW 基线：step-16 `4cdf6c51df36f3ff350baf120863edc893da7383`；节点原始仓库 `86894c25c12cd633568c5fbe839ecaf16d7e3312`。分别在 `.worktrees/cvw-step17`、`.worktrees/node-step17` 的 `experiment/step17-real-node` 分支工作。
- 沿用节点工作区现有 go.mod/go.sum 和已有 proposer 修改的快照；未更新依赖。Go1.25.0、ChainMaker v2.4.0 依赖、原 libwasmer 二进制不变，native SHA `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。
- 正式节点二进制 SHA：`ba5cbd3b956fb24f10ac0e73aec1a21a17998709c4977cd5db7cd316141cc2b0`；计时客户端 SHA：`8c54eab4ca354d21ddbf0129909f10cc366e1143a02266b6f6417a7f7ebafd2f`。后续 ledger/race 客户端另存构建哈希，未用于正式计时。
- 两个进程、独立账本、RPC 127.0.0.1:27301/27302、P2P 127.0.0.1:28301/28302、空 seeds，不连接正式节点；测试证书复制自已有 release。相同合约名/字节码/业务参数。SOLO 首次尝试在交易池空 NetService 处崩溃，日志保留，未修改共识/交易池代码规避。
- 本轮为**真实单节点测试链**，不等同于多组织生产网络或生产吞吐量验证；未重做微基准。

## 方法与计时边界

A/B 各 8 合约×100 对；A4/B4 各 8 合约×64 对、4 个客户端并发。同一对的两种模式随机先后，同一模式的 4 个请求可并发发送。每批重启两个进程，清空 Module/template 常驻缓存；已有链上状态保留，同批两链保持相同工作量。每组合约先记录冷请求，再运行 5 对 warmup。

共 **5248 条有效热调用、2624 对**；全部配对结果和 Gas 相同。另有 320 warmup 和 64 冷请求；B4 Baseline compute 首次 RPC 连接失败，原始记录保留在 cold_cache.csv，冷请求有效数63，禁止将该条当作快速成功。热样本没有删失。`samples.csv` 连接成功请求与节点日志，`vm_invocations.csv` 保留子调用及调度重试。

`client_ns` 从常驻 SDK 的 InvokeContract(withSyncResult=true) 前至返回，包含签名、RPC、排队、执行、共识/提交、SDK结果查询；不包含创建客户端或启动子进程。出块间隔20ms，SDK重试间隔5ms，它们可掩盖亚毫秒差异。未做细分RPC/出块/查询等待的独立计时，因此不能确定噪声的唯一来源。

VM S1 从 fresh 创建入口至 NewInstance+必要 Copy 完成；S2 加 WASI Initialize/_start；S3 加设置执行 Gas。`invoke_ns` 从获取根VM保护锁后至业务和实例关闭完成，**不包含等待该锁、NewRuntimeInstance/冷模板准备**。客户端指标包含这些等待与准备。并发重调度时，summary 的分段采用最终一次根 Invoke，原始文件保留全部尝试，客户端总延迟不删重试成本。exchange 根 Invoke 包含6次真实子调用；S1 仅为根实例。

GOMAXPROCS=4、默认 GC、两节点同机；无CPU绑核、无系统页缓存清空、无端口角色交换。所谓冷缓存是**进程内 Module/template cache cold**，磁盘 artifact/OS page cache 可能已热。不是从原始 Wasm 首编译的冷启动：首编译 Gas 异常沿用 step-15/16 的独立首编译产物隔离，所有 Module 从经SHA和ConfigID校验的 artifact反序列化。未测量可上线的编译器修复。

Median 用常规中位数；P95 为 nearest rank；95% CI 为中位数的 circular moving-block bootstrap（2000次、长度10、固定seed），每批独立。并发组按提交索引成块，不能消除调度相关性。32组探索性比较未作多重检验校正。

## 节点调用结果

下列均为 **Optimized−Baseline，ms；括号为配对中位差95% CI**。负值表示优化更快。

{table('client_ns',['a','b','a4','b4'])}

单客户端绝对延迟（每格 Median/P95，n=100）：

{chr(10).join(absolute)}

顺序两批中，没有合约的客户端改善都达到 CI 上界小于零。erc721 在两个4并发批次均有负向CI，属当前配置的局部正向证据；不能由此推广到顺序调用或未经串行保护的生产并发。exchange B 批次和若干孤立组有收益，另一独立批次不足。identity B 单客户端出现反向CI；这也说明不能从 S1 自动推断客户端收益。

节点 S1：

{table('s1_ns',['a','b','a4','b4'])}

节点 Invoke（包含业务、子调用和关闭；不含锁等待/建池）：

{table('invoke_ns',['a','b','a4','b4'])}

S1 所有32组CI为负；顺序单合约约0.32–0.60ms，接近 step-16 的量级。exchange 顺序根 Invoke 节省2.23/4.24ms，与6次真实子调用各自省初始化的路径相符，但两批差异尚不能归因于单一因素。S2/S3、完整P95和每模式Median的CI见 summary.csv。无生产收益声明。

## 冷缓存、生成成本和内存

{cachetable}

生成成本是 prepareStaticMemory 全部构造时间，包含解码、模板、范围构造和 noData Wasm；不包含 artifact 读入/反序列化/首次实例验证。每合约4个正式进程样本，样本少，保留范围而不伪造高精度CI。摊销列仅用生成时间/本合约两批S1配对Median节省计算；不是完整节点调用的摊销结论。exchange 若首次连同 identity/erc721 全冷，应叠加三份准备成本；不存在有证据支持的统一RPC摊销次数。

8份 Image共24.688MiB，range元素payload共6.114MiB，合计**30.802MiB**。这不含slice多余容量、对象头、原始Wasm、native Module/Store和WASI。cache_scale.csv记录0、1、…、8份常驻规模；exchange首先触发子合约identity，因此加载数量跳增。没有跨进程/跨版本共享、没有LRU或容量预算，常驻增长与模块/版本数关联。

池缓存命中率约99.46–99.54%，含真实子调用和重调度；不是模板生成零成本的证明。每进程8次建池未发现错误artifact匹配。冷请求全过程见 cold_cache.csv；不把63个混合合约冷样本汇成可推广阈值。

两条路径均有**明显的 native/Store 保留成本**：每批结束 RSS 顺序约8.1GiB/节点，并发约10.0GiB/节点；进程重启显著下降。Template只有约31MiB，不能解释GB级RSS。既有证据指向 Store保留已关闭Instance的分配，但本轮未做native分配器追踪，不能将所有RSS增长精确归因。两节点RSS差有正有负，无法用净RSS差精确估计模板开销。长期稳定运行和缓存逐出不可宣称通过。

## 正确性与覆盖限制

- 全8合约在真实节点的T1/S1哈希与step-16原始模板一致，两条路径的所有诊断T1一致。哈希采集独立于计时；S2有随机状态，不要求S2 Memory哈希相等，也未做S2 Snapshot。
- 2624对热调用的客户端结果/返回码/Gas完全一致。真实跨合约exchange调用identity白名单、两次认证、erc721 mint/授权/transfer；子调用日志、最终ownerOf、白名单查询均有记录。诊断首次compute Baseline有一次RPC失败，保留原记录，retry-diagnostic随后成功、Gas与优化版一致。
- 从真实提交账本抽查64对交易写集，原始字节完全相同48对。NFT latestTxInfo含TxId/BlockHeight；只去除这两个链相关元数据后，58对相同，其中全部32对顺序样本相同。6对并发样本的中间余额受提交顺序影响，标为not_comparable_transaction_order，未标通过；最终两地址余额均为353、跨合约owner一致。未比较所有交易全部状态，也没有证明任意业务的状态等价。
- 全8合约的Table/Element及函数类型/索引/Code字节完全保留；6915等大小的完整表映射相同、无table写指令/无导入table。复用step-16 S1/S2/S3全表null-mask证据。合成测试动态检查元素11/22与表修改隔离通过。**真实Go表的native函数引用身份、真实表修改隔离仍为not_tested**；这些合约不可把该项改为pass。
- 不存在的方法两路径都会被既有错误覆盖逻辑表现为空成功：记录为known_baseline_defect，不能算正确异常处理。exchange缺参数、erc721非法地址的真实错误码/消息/Gas一致。其他trap/OOM/超Gas/升级等异常本轮not_tested。
- 节点原始日志的Instance UUID没有复用；无业务后实例回池。Memory彼此独立与模板只读还通过4个独立native Store工作线程、共享模板的-race测试：120轮，每轮同时保有两Instance，修改一个后peer和模板不变。该测试不是同一native Store并行安全性证明。
- 4客户端测试启用了**每链根VM Invoke互斥保护**，子调用同步沿同一执行链运行。验证并发请求下的功能与fresh隔离，不证明native VM可并行执行。Go race检测也不能检测全部CGO/native竞争。

## 审计发现与适用条件

调用边界、修补项、未解决项详见 AUDIT.md。关键上线阻碍包括：fresh模式Reset无接收者、close没有后台资源回收、cache无预算、shared Store并行安全性未知、源码路径依赖native指纹、跨合约/缺方法既有错误覆盖、首编译Gas异常。**本轮只支持固定版本合约、进程级清缓存、显式串行保护的隔离实验**。没有把这些限制包装成生产安全条件。

节点race启动尝试和结果记录在race相关日志；最终判断见verification.json与AUDIT.md。任何报告中not_tested、transport_failure或已复现缺陷均不算通过。

## 建议

保留默认关闭。若继续，先补齐fresh池退休/逐出与内存回收、编译Gas确定性、错误传播和Store并发模型，再在多节点网络中做角色交换/稳定负载/更精确RPC阶段观测。可以继续小规模研究Wasmer内部初始化，以判断是否减少Host Copy/Module模板双份存储；当前没有充分端到端证据支持直接实现页面COW。也没有COW安全性或生产收益数据。

运行和回退见 EXPERIMENT.md；原始CSV/JSONL、build日志、两个stdout日志与配置哈希均保留。正式节点与主分支生产代码保持原样。
'''
(O/'README.md').write_text(readme)
print('wrote README and template_cost.csv')
