# Step-18 第二阶段：基于 95903a3 的组合优化确认

2026-10-19。此前只做过每组40次完整pilot，未做过本次第二阶段。现在已完成三批plain完整8组、每合约每组150次，以及两批独立probe各150次。没有新优化、没有重建guest、没有节点或并发压测。

## 结论

1. **A+C在三个合约、三批完整Invoke的配对中位效应都优于Copy-only。** compute节省0.964–1.136ms，ERC721节省0.725–0.813ms，fact节省0.776–0.840ms；9个95% CI都支持正向节省。但compute B批A+C的P95较C高0.323ms，尾延迟不能宣称全部稳定胜出。
2. **PB加入正确校准的A+C后仍有直接增量。** compute节省0.398–0.562ms，ERC721节省0.263–0.338ms，fact节省0.296–0.330ms，9个配对CI均为正；本轮APC相对AC的9个P95均下降。旧40次pilot的compute P95反向结果保留，不视为通用尾延迟保证。
3. **A+C更适合作为保持SDK公开API的后续候选；APC适合不使用GetBatchState且可接受Gas变化的限定合约。** P不是透明裁剪。所有组合尚未生产认证，Table身份/真实跨合约/全部异常、Store/cache生命周期等限制继续存在。

完整8组每批Median/P95见 [PPT.md](PPT.md)，配对CI与内存见 [RESULTS.md](RESULTS.md)。机器可读数据为 summary.csv、paired_effects.csv、interactions.csv、correctness.csv、variants.csv。

## 固定版本、执行与计时

- 独立分支 `experiment/step18-phase2`、worktree `.worktrees/cvw-step18-phase2`，基线明确为 `95903a3`。原Step-18分支及生产main源码未改。
- 复用最新完整矩阵同一个 `step18.test`，SHA `64f9f0a234d1cceb48701190e9d4d1edd4f8afe6e16e54cb009f0953a2dfc2e6`。未重新编译，避免引入新的编译序号变化。binary/native/WASM/serialized Module/template均核对哈希。
- host Go1.25.0、guest Go1.24.1、ChainMaker/protocol2.4.0、packaged Wasmer6.0.1不变；SDK为v0.1.3原版或该版本私有补丁副本。
- 三个plain批seed 181951/52/53，每合约独立进程、8池共存、5轮预热、150轮采样，每轮8组随机排列；固定CPU affinity=0、GOMAXPROCS1，自动GC关闭，每20轮边界显式GC。各批顺序中穿插独立probe进程，probe不并入plain统计。
- 10800条plain + 7200条probe；全部每次fresh Instance、同步创建与关闭。没有业务后Instance复用。
- 完整Invoke包围真实RuntimeInstance.Invoke，含GetInstance同步创建、WASI Initialize、_start、SetGas、SimContext/CallMethod、业务与Gas读取及defer关闭。Tx/参数准备、Module加载/编译和模板准备在窗口外；不是真实节点或客户端延迟。
- S1含imports、UUID等和必要Copy；start_ns仅_start调用；S2/S3为同一起点的累计值。A与B1来自另一个probe产物，probe S2观测会污染其S3/Invoke，故只用probe的A/B1诊断，不与plain中位数相加。
- summary给Median、nearest-rank P95、N；配对CI为4000次循环移动块bootstrap、block10、seed181950。各批分开。P95变化是两个分布P95之差，不是配对差的P95。探索性比较没有多重检验校正。

## A与PB布局审计

全部24个逻辑WASM（plain/probe）及48个C变体通过产物/模板哈希核对；Module sidecar的WasmSHA/ArtifactSHA匹配，加载时还检查ConfigID。只删除Data section，其他sections逐项逐字节相同。方法/输入沿用同一个manifest，各AP变体使用相同fixture，模板分别绑定最终逻辑WASM。

P1没有沿用P0 padding。plain A1参数如下，单位Bytes：

| 合约 | P0 padding | P1 padding | A1初始页数 |
|---|---:|---:|---:|
| compute | 1,638,400 | 2,359,296 | 74 |
| ERC721 | 1,507,328 | 2,097,152 | 74 |
| fact | 1,638,400 | 2,228,224 | 74 |

公式对每个P及plain/probe分别计算：`padding = 4MiB − A0.initBloc − 5×64KiB`。plain静态initBloc目标为3,866,624；probe A1的全部采样实际首个arena reserve bloc=4,194,304、skip=0、alignment=4MiB。plain未新增guest探针，动态arena断言来自各自重新校准的probe副本，不能声称逐plain实例直接读取过该值。详见audit.json、layout_audit.csv。

## PB对各阶段的影响

两批probe，C0，箭头按 `000 → 010 → 100 → 110`；单位ms、各组150次。诊断与plain是不同产物/进程，不相加：

| 合约 | 批次 | A段Median序列 | B1 Median序列 |
|---|---|---|---|
| compute | probe-a | 1.500 → 1.986 → 0.351 → 0.342 | 0.203 → 0.139 → 0.214 → 0.143 |
| compute | probe-b | 1.426 → 1.828 → 0.350 → 0.330 | 0.210 → 0.145 → 0.212 → 0.141 |
| ERC721 | probe-a | 0.947 → 1.210 → 0.265 → 0.253 | 0.150 → 0.101 → 0.154 → 0.098 |
| ERC721 | probe-b | 1.229 → 1.631 → 0.296 → 0.296 | 0.182 → 0.124 → 0.169 → 0.113 |
| fact | probe-a | 1.203 → 1.496 → 0.303 → 0.303 | 0.172 → 0.112 → 0.178 → 0.111 |
| fact | probe-b | 0.970 → 1.239 → 0.275 → 0.261 | 0.149 → 0.102 → 0.149 → 0.094 |

P1缩小静态布局，A0首次arena对齐距离改变，观测A段变长；它同时降低B1。按P1重校准A后，A段回到相近低水平，未看到PB使A1启动明显退化。不能把整段差值全部指定为memclr，未分离memory.grow/全部清零成本。

本轮plain直接`111−101`配对增量：

| 合约 | S1节省Median跨批范围 ms | Host恢复节省范围 ms | _start节省范围 ms |
|---|---:|---:|---:|
| compute | 0.347–0.452 | 0.319–0.449 | 0.065–0.086 |
| ERC721 | 0.215–0.261 | 0.201–0.240 | 0.059–0.073 |
| fact | 0.221–0.248 | 0.215–0.242 | 0.064–0.077 |

这支持PB在AC之上的增量包含更低的Copy/S1成本及更低的package-init相关启动成本。S1覆盖Copy，这些列嵌套，不能加列中位数还原Invoke。P还改变函数/Table等布局，不能仅凭相关性给出每字节/每段因果常数。

交互严格先在每轮计算，例如 `Γ_AP|C1 = T111−T101−T011+T001`，再统计CI；正数表示延迟上的抵消/负面交互，负数表示协同。本轮3批3合约的Invoke Γ_AP|C1 CI都小于零，不支持“重新校准后PB与A存在负面性能交互”。这不否认P1在未开A时引入对齐副作用，也不能把数学负交互误写成性能退化。所有分阶段二阶交互在interactions.csv。

## 31.6ms与历史约4ms的compute不是同一个工作量

审计依据是实际WASM反汇编，不是当前源码注释：

- Step-16原始compute `main.bigNumCal` 在循环比较中使用 `i64.const 100; i64.lt_s`。
- Step-18重建产物使用 `i64.const 10000; i64.lt_s`。当前源码也明确10000次；Step-16工作树当前源码同样10000，说明不能从今天的源码反推历史预编译WASM。
- 见step16-bigNumCal-disassembly.txt:309与step18-bigNumCal-disassembly.txt:404。WASM hash不同，native business Gas分别14,824,571与1,480,822,341。返回值虽相同，不表示工作量相同。

| 数据集 | Invoke Median ms | S1 Median ms | _start Median ms | 每样本Invoke−S3窗口Median ms |
|---|---:|---:|---:|---:|
| Step-16 A baseline，100轮业务 | 4.669 | 2.277 | 未独立采集 | 见workload_audit.csv |
| Step-18旧四组pilot，10000轮 | 31.600 | 3.452 | 2.811 | 24.916 |
| Step-18完整40次pilot，10000轮 | 20.259 | 2.428 | 1.883 | 15.787 |

最后一列从每条样本的时间戳求差再取Median，是SetGas后至Invoke返回的复合窗口（业务、Gas读取、关闭等），不是纯CallMethod。各列Median不能相加。

旧31.6和20.3ms两批P0原始WASM hash相同，Gas及输入相同，但批次环境和池工作集不同；其绝对漂移原因仍未独立识别。本轮三批也不跨批相减归因。与Step-16约4ms的主要可验证差异则是预编译产物的100 vs10000业务循环，不能再笼统归咎于计时边界或Copy失效。本轮未改变这个10000次工作负载。

## 正确性、Gas和兼容性

- 72个plain批次/组合记录各150样本：返回/写集/事件与同批000一致，所有C0/C1同逻辑WASM的registry/native初始化及业务Gas相同，每worker1200个ID唯一，全部预期成功，无删除失败样本。
- 另重新运行6个TestStep18Checks进程覆盖24组合，及12个TestStep16Validation进程覆盖原始/Copy诊断副本。S1完整Memory、Globals、Table size/nullness、fresh Memory/Globals隔离和模板不变性通过。ERC721/fact非法数字guest错误与对应Copy一致。
- compute guest异常、真实Table函数身份/修改隔离、真实跨合约、全部trap/OOG仍not_tested。missing export继承host日志报错但API code0的已知问题，不作为正确guest错误证明。全部safe=not_certified。
- 跨A/P的业务Gas与registry Gas在本fixture相同；P使native初始化+SetGas少3000，A使其多16。跨WASM总Gas不相等，接受性未认证，不能默认可无差别部署。
- P补丁基于SDK v0.1.3，删除`GetBatchState`公共接口及其实现/PB依赖；对使用该接口的合约API不兼容。8合约P1构建通过只说明这些源码能构建；其余五合约完整组合、业务与异常未验证，不推广为通用SDK兼容。私有SDK全部11个保存文件的SHA与95903a3 inventory一致，未改module cache。

## 内存和回退

memory.csv复用同一已验hash产物的旧30次模板准备/Go heap测量；rss.csv为本轮全进程峰值。A+C相对C多约1.44–1.56MiB逻辑模板缓存/合约，APC因PB缩小metadata而低于AC，但仍高于C。三项组合约5.13–5.20MiB/合约。不能以此代表native Module总占用或生产RSS。

本轮8池、1200次调用工作进程峰值约4.13–6.86GiB。它包括Store保留、8池和运行资源，不能精确分离A的单组合稳态RSS；此项仍缺独立测量。原有Store/cache回收与race问题未修复，因此即使性能收益成立，也不生产启用。

复查统计：`python3 -B phase-2/analyze.py`。run.py拒绝覆盖批次目录，所有原始JSONL/log/resources在confirm-*、probe-*和validation/。重跑必须选新输出目录。没有节点进程需要回退；回到000原始WASM且关闭Copy即可恢复实验基线，勿对脏main执行reset/restore。保留95903a3、独立分支、environment.json和完整产物即可复核。

复用二进制的rpath及runtime.Caller指纹路径仍依赖旧 `.worktrees/cvw-step18`；phase2分支是新编排与报告的隔离基线，未重新链接该binary。旧工作树也须保留以复跑，准确ldd行见environment.json。
