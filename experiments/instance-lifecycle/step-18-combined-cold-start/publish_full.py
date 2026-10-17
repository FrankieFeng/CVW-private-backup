"""Publish full-pilot tables while preserving the earlier blocked pilot."""
import csv,json,hashlib,shutil,subprocess,datetime
from pathlib import Path
import pipeline as p
R=p.ROOT;D=R/'full-pilot'
def rows(name):return list(csv.DictReader((D/name).open()))
def pick(rs,**kw):return next(r for r in rs if all(r.get(k)==str(v) for k,v in kw.items()))
def ms(r,k='median_ns'):return float(r[k])/1e6
def saving(r):return f"{-ms(r):.3f} [{-ms(r,'ci95_high_ns'):.3f}, {-ms(r,'ci95_low_ns'):.3f}]"
def main():
 s=rows('summary.csv');e=rows('paired_effects.csv');ints=rows('interactions.csv');checks=rows('correctness.csv');cost=rows('template_cost.csv');variants=rows('variants.csv')
 assert len(checks)==24 and all(v['status']=='tested_scope_pass' and v['safe']=='not_certified' for v in checks)
 lines=['# Step-18 完整8组：PB补丁恢复后的初步结果','','**已从历史记录恢复原PB裁剪补丁，补齐三合约全部8组。三项组合在本批的Invoke中位数及配对差优于Copy单独开启；compute的P95未全面胜出，不能宣称稳定生产收益。** 旧blocked判断已被恢复证据更新，原4组pilot和失败数据完整保留。','','## 记录找回与适用条件','','历史WASM内的SDK replace路径指向/tmp，原会话保留SDK补丁和构建命令，见[恢复审计](recovered-pb/RECOVERY.md)。P是删除GetBatchState接口/实现及PB import，会缩减SDK公开API；8目标合约未发现相关直接调用，均通过P1构建，但本轮仅compute/ERC721/fact执行完整组合。不能推广给使用该API或SDK反射行为的合约。','','## 完整Invoke与追加收益','','本批每合约每组40次，960条plain原始样本；另有960条probe诊断样本。所有正式性能来自plain。真实RuntimeInstance.Invoke + mock TxSimContext，含同步fresh创建、WASI/_start、SetGas、业务、Gas读取、defer清理和关闭；不含模块编译、模板预处理、测试Tx构造，也不是节点/RPC延迟。','', '|合约|Baseline Median/P95 ms|C Median/P95 ms|A+C Median/P95 ms|A+P+C Median/P95 ms|三项对C配对节省 ms [95% CI]|P在A+C上配对节省 ms [95% CI]|','|---|---|---|---|---|---|---|']
 for c in p.CONTRACTS:
  parts=[]
  for a,pv,cc in [(0,0,0),(0,0,1),(1,0,1),(1,1,1)]:
   v=pick(s,contract=c,A=a,P=pv,C=cc,metric='invoke_ns');parts.append(f"{ms(v):.3f} / {ms(v,'p95_ns'):.3f}")
  lines.append('|'+ '|'.join([c]+parts+[saving(pick(e,contract=c,contrast=k,metric='invoke_ns')) for k in ['AP_on_C','P_on_AC']])+'|')
 lines+=['','差值按同轮先配对再取中位数；不能用上表两个中位数直接相减替代。4000次循环移动块bootstrap、块长5轮，CI为配对差中位数区间。每合约单独进程、8组每轮随机顺序、5轮预热、固定CPU/GOMAXPROCS=1、自动GC关闭且每20轮边界显式GC。所有WASM各自独立首次编译并Serialize，计时进程Deserialize；相同WASM/配置的P0原隔离编译产物按哈希复用。','', 'compute三项P95为27.899ms，高于A+C的20.100ms；40次P95只靠最慢几个样本，不认证P95/P99稳定改善。当前只有一个完整矩阵批次，不能把前一轮4组pilot当作第二批完整验证。相同P0 WASM的完整Invoke也从旧4组pilot约31.6ms变化到本批20.3ms，表明存在明显批次/工作集/环境漂移；未采集足够系统细分，不能把原因指定为频率、缓存或调度。仅作本批内比较，不拼接跨批中位数或旧step-16不同WASM/Gas的数据。','','## 七种开关效果与非加性','','正数为相对000的配对节省，全部为完整Invoke ms。','', '|合约|A|P|C|A+P|A+C|P+C|A+P+C|','|---|---|---|---|---|---|---|---|']
 for c in p.CONTRACTS:lines.append('|'+ '|'.join([c]+[saving(pick(e,contract=c,contrast=k+'_vs_000',metric='invoke_ns')) for k in ['100','010','001','110','101','011','111']])+'|')
 lines+=['','P在C单独开启之上的追加收益P_on_C，三个合约的本批CI均跨零；P在A+C之上的P_on_AC则均为正向节省。这说明不能把单项收益机械相加。','', '交互Γ用每轮的二阶/三阶有限差分；正数为延迟改善小于简单相加。`interactions.csv`同时给出各二阶交互在第三因素0/1时的结果，以及三阶交互。', '', '|合约|A×P，C0，_start Γ ms [CI]|P×C，A0，S1 Γ ms [CI]|三阶Invoke Γ ms [CI]|','|---|---|---|---|']
 for c in p.CONTRACTS:
  vals=[]
  for name,metric in [('A_x_P_other0','start_ns'),('P_x_C_other0','s1_ns'),('A_x_P_x_C','invoke_ns')]:
   v=pick(ints,contract=c,interaction=name,metric=metric);vals.append(f"{ms(v):.3f} [{ms(v,'ci95_low_ns'):.3f}, {ms(v,'ci95_high_ns'):.3f}]")
  lines.append('|'+ '|'.join([c]+vals)+'|')
 lines+=['','A×P在_start有明确的本批负交互：P缩小静态布局后，未开A时首次arena前对齐距离增大，诊断A段也变长；按最终P0/P1各自校准A后，两者首次arena bloc均4194304、对齐距离均0。这支持A补偿P引入的布局副作用；未单独计量全部memclr和memory.grow，不能把整段差值全指定为清零。P×C在S1存在本批正交互，静态实例化收益有重叠；P同时改变data、函数和Table布局，不能仅凭S1时间把全部重叠指定为Memcpy或Table成本。三阶Invoke交互CI全部跨零，未分辨独立三阶机制。','','## A与B1分段证据','','以下为独立probe构建，C0；不得和plain Invoke中位数相加。guest/host单调时钟校准记录最小RTT误差，probe S2观察者污染其S3/Invoke，后两者不用于性能结论。','', '|合约|诊断A：000→010→100→110 ms|诊断B1：000→010→100→110 ms|','|---|---|---|']
 for c in p.CONTRACTS:
  vals=[]
  for metric in ['a_ns','b1_ns']:vals.append(' → '.join(f"{ms(pick(s,contract=c,A=a,P=pv,C=0,metric=metric)):.3f}" for a,pv in [(0,0),(0,1),(1,0),(1,1)]))
  lines.append('|'+ '|'.join([c]+vals)+'|')
 lines+=['','A是可达静态数组经Go链接器重新布局，不是仅改initial memory。每个P/构建flavor单独计算padding，所有诊断A1均检查首次预留对齐成功。C针对每个最终WASM重新生成模板，先移除active Data，再在WASI Initialize/_start之前Copy；没有先标准Data初始化再重复拷贝。','','## 模板构建与内存','','每个逻辑版本独立30次预计算样本，Go heap在保留对象/GC前后核查；下表不包含原始WASM、native Module/Store或其他池开销。','', '|合约|C模板 MiB|A+C模板 MiB|A+P+C模板 MiB|三项模板构建Median / P95 ms|','|---|---|---|---|---|']
 for c in p.CONTRACTS:
  vs=[pick(cost,label=f'{c}-a{a}p{pv}-plain') for a,pv in [(0,0),(1,0),(1,1)]]
  lines.append('|'+ '|'.join([c]+[f"{int(v['logical_retained_bytes'])/(1<<20):.3f}" for v in vs]+[f"{ms(vs[2]):.3f} / {ms(vs[2],'p95_ns'):.3f}"])+'|')
 lines+=['','三项模板比C单独开启增加约1.21–1.34MiB/合约；P让WASM和范围元数据缩小，可抵消部分额外占用，但未分离native Module/Store稳态占用，不能声称整体RSS净减少。A1的S1 memory始终74页，A0各版本按自身Go链接器输出；同AP逻辑版本的C0/C1初始memory一致。样本进程共存8个实验池/Module，native Store关闭前可能保留资源，峰值RSS不是单个模板大小，也不等同生产稳态缓存容量。','','## 正确性与Gas范围','','24个组合在已测路径上通过：S1 Memory/Globals、业务返回/写集/事件、同逻辑WASM C0/C1的registry及native初始化/业务Gas、fresh Memory/Globals隔离、模板不变性。每个最终WASM的Function/Code/Global/Table/Element节C变换前后逐字节保持，另核查S1/S2/S3全表nullness。真实Table函数身份、真实跨合约、全部OOG/trap均not_tested，所有组safe=not_certified。','', 'ERC721非法tokenId、fact非法time的guest错误输出也与000相同；compute guest异常未覆盖。missing export是host派发错误，既有VM仅打错误日志而API仍code0/空结果，本轮没有把它当正确guest错误返回或修复该行为。','', '跨A/P：本批registry和native业务Gas均相同；P使native初始化+SetGas减少3000、A增加16。因此不能宣称跨WASM总Gas必然相等；新SDK/Gas政策可接受性尚未认证。SDK API删除、step-17缓存回收/共享Store race及Table身份限制，使本轮不具备生产启用资格。','','## 结论与下一步','','本批的三项组合可以比现有C进一步降低完整VM Invoke中位数，也比A+C进一步降低中位数；收益存在A/P布局补偿和P/C静态阶段重叠，不能相加。compute尾延迟证据不足，且批间绝对时间漂移明显。先对三合约完整矩阵做至少两批独立确认，固定产物/配置并核查P95，再决定是否扩展八合约；本次未运行正式节点或八合约性能批次。不提出通用padding/Copy/P启用阈值。']
 (D/'RESULTS.md').write_text('\n'.join(lines)+'\n')
 initial=R/'initial-pilot';initial.mkdir(exist_ok=True)
 for name in ['README.md','RESULTS.md','PPT.md','variants.csv','samples.csv','summary.csv','paired_effects.csv','interactions.csv','correctness.csv','ppt_data.csv','template_cost.csv','static_sections.csv','error_paths.csv','final_checks.json','artifact_hashes.json','branch.json']:
  if (R/name).exists() and not (initial/name).exists():shutil.copyfile(R/name,initial/name)
 for name in ['RESULTS.md','PPT.md','variants.csv','samples.csv','summary.csv','paired_effects.csv','interactions.csv','correctness.csv','ppt_data.csv','template_cost.csv','static_sections.csv','error_paths.csv']:shutil.copyfile(D/name,R/name)
 before=json.loads((R/'production-source-before.json').read_text());assert all(p.sha(Path(path).read_bytes())==h for path,h in before.items())
 artifacts={str(path.relative_to(R)):p.sha(path.read_bytes()) for path in R.rglob('*') if path.is_file() and path.suffix in ['.wasm','.module','.bin','.test'] and 'toolchains' not in path.parts}
 (R/'artifact_hashes.json').write_text(json.dumps(artifacts,indent=2)+'\n')
 meta=dict(scope='three-contract single-thread eight-cell VM pilot; not live node',baseline_commit='4cdf6c51df36f3ff350baf120863edc893da7383',previous_report_commit='d9a117b6c446b262390b599679560f2aa94ac7aa',plain_samples=960,probe_samples=960,n_per_cell=40,fully_tested_contracts=p.CONTRACTS,p1_eight_contracts_build_only=True,pb_source_recovered=True,production_go_sources_unchanged=True,safe='not_certified',performance_binary_sha256=p.sha((R/'binaries/full-plain.test').read_bytes()),validation_binary_sha256=p.sha((R/'step18.test').read_bytes()),test_source_sha256=p.sha((p.VM/'step18_test.go').read_bytes()),wasmer_library_sha256=p.sha((p.VM/'wasmer-go/packaged/lib/linux-amd64/libwasmer.so').read_bytes()),sdk_patch_sha256=p.sha((R/'recovered-pb/sdk.diff').read_bytes()))
 (R/'final_checks.json').write_text(json.dumps(meta,indent=2)+'\n')
 print('published full matrix; 24 tested scopes, P recovered; production hashes unchanged')
if __name__=='__main__':main()
