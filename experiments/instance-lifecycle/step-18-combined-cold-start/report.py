"""Render the evidence report and audit unchanged production inputs."""
import csv,hashlib,json,math,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def rows(name):return list(csv.DictReader((ROOT/name).open()))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pick(data,**filters):return next(r for r in data if all(r.get(k)==str(v) for k,v in filters.items()))
def ms(row,key='median_ns'):return float(row[key])/1e6
def effect(row):return f"{-ms(row):.3f} [{-ms(row,'ci95_high_ns'):.3f}, {-ms(row,'ci95_low_ns'):.3f}]"
def main():
 summary=rows('summary.csv');effects=rows('paired_effects.csv');interactions=rows('interactions.csv');costs=rows('template_cost.csv');variants=rows('variants.csv');checks=rows('correctness.csv')
 contracts=['compute','erc721','fact']
 lines=['# Step-18 初步结果','','**A+C 在本批三个合约中均比 C 单独开启更快；P=1 缺可恢复实现，三项叠加及含 P 的交互效应尚无结果。** 本轮未通过完整8组合构建门槛，停止于三合约pilot，没有扩大八合约、两批正式确认或真实节点测试。','', '有效性能样本480条（3合约×4组×40），独立诊断样本480条；所有正式收益只取未插桩plain。以下CI均为同批配对差中位数95%移动块bootstrap区间，不是两个中位数相减的区间。单批不足以宣称跨批稳定。','', '## 在现有 Copy 上叠加 A','','|合约|Baseline Invoke Median / P95 ms|C Invoke Median / P95 ms|A+C Invoke Median / P95 ms|A在C上配对节省 ms [95% CI]|n|','|---|---|---|---|---|---|']
 for c in contracts:
  base=pick(summary,contract=c,A=0,P=0,C=0,metric='invoke_ns');copy=pick(summary,contract=c,A=0,P=0,C=1,metric='invoke_ns');both=pick(summary,contract=c,A=1,P=0,C=1,metric='invoke_ns');delta=pick(effects,contract=c,contrast='A_on_C',metric='invoke_ns')
  lines.append(f"|{c}|{ms(base):.3f} / {ms(base,'p95_ns'):.3f}|{ms(copy):.3f} / {ms(copy,'p95_ns'):.3f}|{ms(both):.3f} / {ms(both,'p95_ns'):.3f}|{effect(delta)}|40|")
 lines+=['','compute 本轮完整Invoke约28–32ms，远高于step-16旧产物；这是重新构建的不同WASM，registry Gas120027对比旧产物105920、native业务Gas1480822341对比旧样本14824571。输出相同不等于计量/构建相同。二者producers都标记Go1.24.1，不能把旧新绝对时间混比或把差异直接归因某一个依赖。本轮固定当前源码、SDK与metering，并在同批内比较。SDK缓存与下载归档逐文件相同，见sdk-provenance.json。','','## 独立与组合收益','','正数为节省，负数为变慢。非配对中位数差不等于配对差中位数。','', '|合约|A独立 ms [CI]|C独立 ms [CI]|A+C相对baseline ms [CI]|','|---|---|---|---|']
 for c in contracts:
  vals=[effect(pick(effects,contract=c,contrast=k,metric='invoke_ns')) for k in ['A_only','C_only','A_plus_C']]
  lines.append('|'+ '|'.join([c]+vals)+'|')
 lines+=['','compute 的 C 独立收益区间跨零，本批不能声称其C单独收益稳定。三个合约 A_on_C 区间均为正向节省，但还需独立批次确认。P、A+P、P+C、A+P+C保留blocked/n=0，无法判断其Gas、收益或冲突。','','## 非加性影响','','交互定义 Γ=t101−t100−t001+t000，负值为比延迟变化简单相加更有利。每轮先求Γ，再估计其中位数，不能把各组中位数直接相加。','', '|合约|Invoke Γ ms [95% CI]|S1 Γ ms [95% CI]|`_start` Γ ms [95% CI]|','|---|---|---|---|']
 for c in contracts:
  cells=[]
  for metric in ['invoke_ns','s1_ns','start_ns']:
   v=pick(interactions,contract=c,interaction='A_x_C_at_P0',metric=metric);cells.append(f"{ms(v):.3f} [{ms(v,'ci95_low_ns'):.3f}, {ms(v,'ci95_high_ns'):.3f}]")
  lines.append('|'+ '|'.join([c]+cells)+'|')
 lines+=['','ERC721/fact未分辨出非零交互；compute的完整Invoke负交互估计区间贴近零且较宽，S1和_start各自的交互区间均跨零。`invoke_minus_s3_ns`残差的compute交互估计也跨零（它含业务、关闭及Invoke/创建入口差额，不能叫纯业务耗时）。这些指标的中位数不能相加，现有数据不能确定协同来自初始化机制、代码/数据缓存还是顺序/调度噪声；本轮不提出机制性因果结论。所有CI未经多重检验校正。','','## 启动阶段证据与内存代价','','以下A/B1来自独立诊断构建；诊断有不同静态布局，单独校准，绝对值不能和plain Invoke相加。A首次预留点对齐验证通过，三个合约开启A均为bloc4194304、对齐距离0；关闭A分别需要跳过约1.5MiB。该距离来自函数入口bloc与alignUp之差，并非全部memclr调用的计数。源码的首个arena预留路径及旧clear探针支持该优化方向，不将仅增大initial memory当作A。','', '|合约|诊断A耗时 A0→A1 ms（C0）|诊断B1耗时 A0→A1 ms（C0）|plain `_start` A0→A1 ms（C0）|','|---|---|---|---|']
 for c in contracts:
  cells=[]
  for metric in ['a_ns','b1_ns','start_ns']:
   vs=[pick(summary,contract=c,A=a,P=0,C=0,metric=metric) for a in [0,1]];cells.append(f'{ms(vs[0]):.3f} → {ms(vs[1]):.3f}')
  lines.append('|'+ '|'.join([c]+cells)+'|')
 lines+=['','A主要改善证据位于runtime启动：首次arena跳过空间消失，诊断A和未插桩_start下降；B1未作PB裁剪，不能把B1的小幅变化认定为PB优化。C减少S0→S1，Copy本身仍有约5万个范围循环及内存写入成本，参见summary的copy_ns。','','|合约|A0 / A1 WASM bytes|A0 / A1模板+范围容量 MiB|A0 / A1模板构建Median ms|A1模板构建P95 ms|','|---|---|---|---|---|']
 for c in contracts:
  v0=pick(variants,contract=c,A=0,P=0,C=1,flavor='plain');v1=pick(variants,contract=c,A=1,P=0,C=1,flavor='plain')
  t0=pick(costs,label=f'{c}-a0p0-plain');t1=pick(costs,label=f'{c}-a1p0-plain')
  lines.append(f"|{c}|{v0['wasm_bytes']} / {v1['wasm_bytes']}|{int(t0['logical_retained_bytes'])/(1<<20):.3f} / {int(t1['logical_retained_bytes'])/(1<<20):.3f}|{ms(t0):.3f} / {ms(t1):.3f}|{ms(t1,'p95_ns'):.3f}|")
 total0=sum(int(pick(costs,label=f'{c}-a0p0-plain')['logical_retained_bytes']) for c in contracts);total1=sum(int(pick(costs,label=f'{c}-a1p0-plain')['logical_retained_bytes']) for c in contracts)
 lines+=['',f'每个合约只保留一个选定版本时，三个C模板逻辑容量合计 {total0/(1<<20):.3f} MiB（A0）→{total1/(1<<20):.3f} MiB（A1），约增加{(total1-total0)/(1<<20):.3f} MiB。A使S1每Instance初始memory也增加约1.44–1.56MiB；实际稀疏Copy bytes仅增加174–361字节，不等于把padding全量拷贝。WASM只增加约645–668字节，因为零区间并未全量编码进Data。模板完整image仍保留零区间，存在明确内存代价。','', '模板构建每组30次，内存用独立GC前后保留对象差核查。仅以本批 C_on_A 的配对节省估计，A1模板预计算约需5/8/8次调用摊销（compute/ERC721/fact）；这是热Module VM内的粗略估计，不含编译/部署/存储/节点成本，不是生产盈亏点。','', 'plain测试进程最大RSS约0.80–1.19GiB（各进程共存四个实验Module，执行180次fresh调用含预热，另有建池验证实例）。这不能等同单个缓存条目大小；native Store保留native对象的既有限制仍在，Instance.Close不代表所有native占用立即下降，进程/Store结束后统一回收。','','## 正确性与尚未覆盖部分','','12个P0组合的已测试范围通过：S1 Memory hash、S1 Globals、业务输出/写集/事件、同逻辑WASM的registry/native启动和业务Gas、Memory/Globals fresh隔离、模板不变性。静态Function/Code/Table/Element/Global节C0/C1相同，全表nullness在S1/S2/S3核查。真实Table函数身份为not_tested，不能称Table完全动态等价。','', '跨A：本批registry与native业务Gas一致，但native初始化+SetGas计量均增加16，符合新增init代码的观测；这不等于不同WASM总Gas相等，也没有认证新二进制Gas政策可接受。P引起的Gas变化没有数据。','', 'ERC721非法tokenId、fact非法time实际进入guest错误路径，C0/C1结果/写集/事件/Gas一致。compute未验证guest业务异常；所有合约测试missing export的host dispatch错误。既有VM会打印method not export，但API结果仍是code0/空结果，本轮如实记录，不把它当正确的guest错误返回，也没有修改该行为。OOG、所有host trap及真实跨合约均not_tested。','', '第一次检查脚本因变体Label在循环中被覆盖而中断（第二个C池的序列化路径错误），已修复测试脚本，保留failed-harness原始日志并完成重查；不影响此前plain性能函数/样本。性能binary及其当时test源码单独保留在binaries/performance.test、prototype/performance_test.go.txt。','', '所有组safe字段均未认证；step-17缓存回收、共享Store并发race、真实Table身份限制未解决，不能生产启用。','','## 下一步门槛','','先恢复并校验真实PB裁剪源码/配方，再对最终P/A各版本重新校准布局、重算Copy模板、验证Gas与业务；不拿历史trimmed二进制拼接A源码。随后对三合约全8组重复独立批次，重点复核compute的C独立效果与交互估计。只有构建/等价门槛通过后才扩展八合约。当前证据支持继续验证A+C，不能回答三项叠加是否更优，也不能给出通用padding或PB/Copy启用阈值。']
 (ROOT/'RESULTS.md').write_text('\n'.join(lines)+'\n')
 before=json.loads((ROOT/'production-source-before.json').read_text());changed=[p for p,h in before.items() if sha(Path(p))!=h]
 assert not changed,changed
 assert len([r for r in checks if r['P']=='0' and r['status']=='tested_scope_pass'])==12
 assert all(r['safe']!='yes' for r in checks)
 files={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p.suffix in ['.wasm','.module','.bin','.test'] and 'toolchains' not in p.parts}
 (ROOT/'artifact_hashes.json').write_text(json.dumps(files,indent=2)+'\n')
 (ROOT/'final_checks.json').write_text(json.dumps(dict(production_go_sources_unchanged=not changed,plain_samples=480,probe_samples=480,pb_groups_per_contract='4 blocked, retained with n=0',safety='not_certified',fallback_test=(ROOT/'validation/fallback.log').read_text(errors='replace').rstrip().endswith('PASS'),synthetic_identity_isolation_test=(ROOT/'validation/synthetic.log').read_text(errors='replace').rstrip().endswith('PASS'),original_runtime_hashes={str(p):sha(p) for p in [Path('/usr/local/go-version/go1.24.1/src/runtime')/n for n in ['proc.go','mem_sbrk.go','symtab.go']]},validation_binary_sha256=sha(ROOT/'step18.test'),performance_binary_sha256=sha(ROOT/'binaries/performance.test')),indent=2)+'\n')
 print('report complete; production Go sources unchanged; 12 tested scope checks passed')
if __name__=='__main__':main()
