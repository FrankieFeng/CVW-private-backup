"""Produce Step21A reports exclusively from saved evidence; never starts a benchmark."""
from pathlib import Path
import json,csv,hashlib,subprocess,statistics
ROOT=Path(__file__).resolve().parent.parent
read=lambda f:list(csv.DictReader((ROOT/f).open()))
e=json.loads((ROOT/'environment.json').read_text());h=json.loads((ROOT/'audit/history-observations.json').read_text());v=json.loads((ROOT/'verification.json').read_text())
runs=[x for x in read('summary.csv') if x['phase']=='isolated'];diag=[]
for method in ['bigNumCal','normalCal']:
 for pool in ['original','capacity']:
    a=next(x for x in runs if x['method']==method and x['pool']==pool and x['policy']=='R0');b=next(x for x in runs if x['method']==method and x['pool']==pool and x['policy']=='R1')
    diag.append(f"| {method} | {pool} | 3/3 | {float(a['invoke_mean_ms']):.3f} | {float(b['invoke_mean_ms']):.3f} | {float(a['b5_export_mean_ms']):.3f} | {float(b['b5_export_mean_ms']):.3f} |")
(ROOT/'NORMALCAL_ANALYSIS.md').write_text(f'''# normalCal差异归因：定位窗口，未证明机制

## WASM、输入和工作量

两模式同一compute-go.wasm，SHA256 `e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507`；100行输入文件SHA见cases.json。本轮没有重编合约。当前二进制重新只读反汇编，main.normalCal包含i64.const10000000及循环比较，见audit/current-normalcal-disassembly.txt；没有为了倍率改循环。

原Step21正常计时的b/c/d三对逐索引参数哈希相同，Gas均100000072，返回success normalCal:666。返回值是常量，单靠结果相同不能证明循环量；相同二进制、固定循环和Gas共同构成证据。当前对应源码normalCal只使用局部循环及SuccessResult，没有自定义业务缓存/持久读写。旧原始B5每次syscall_count=1、syscall_method=SuccessResult；未发现GetState/PutState路径。精确嵌入SDK构建源未重建，不将本地SDK代码视为完整来源证明。

Go Runtime/SDK仍有实例内全局、堆栈和初始化状态，R0保留、R1重建；未认证这些状态完全相同，也未证明某个缓存/GC造成8ms差异。WASM中runtime相关全局检查不应直接命名为业务缓存。

## 原始细分定位（此前300次/模式，不是本轮新性能样本）

直接读取旧raw_logs的600条B5，不引用报告数字推断。详见audit/previous_normalcal_components.csv和history-observations.json。

| 窗口 | R0均值ms | R1均值ms | R0−R1 ms |
|---|---:|---:|---:|
| InvokeTime | {h['means_ms']['R0']['invoke_ns']:.6f} | {h['means_ms']['R1']['invoke_ns']:.6f} | {h['means_ms']['R0']['invoke_ns']-h['means_ms']['R1']['invoke_ns']:.6f} |
| CallMethod | {h['means_ms']['R0']['callmethod_ns']:.6f} | {h['means_ms']['R1']['callmethod_ns']:.6f} | {h['callmethod_delta_ms']:.6f} |
| exportFunc.Call | {h['means_ms']['R0']['export_call_ns']:.6f} | {h['means_ms']['R1']['export_call_ns']:.6f} | {h['export_delta_ms']:.6f} |
| allocate | {h['means_ms']['R0']['allocate_ns']:.6f} | {h['means_ms']['R1']['allocate_ns']:.6f} | {h['means_ms']['R0']['allocate_ns']-h['means_ms']['R1']['allocate_ns']:.6f} |
| copy+lookup | {h['means_ms']['R0']['copy_lookup_ns']:.6f} | {h['means_ms']['R1']['copy_lookup_ns']:.6f} | {h['means_ms']['R0']['copy_lookup_ns']-h['means_ms']['R1']['copy_lookup_ns']:.6f} |

约8.300ms的CallMethod差异中，8.294ms落在导出函数调用窗口（sim_context.go:186–191，time.Sub单调计时）。不是靠不同中位数相减，而是同批原始逐调用时长总量/均值分解；嵌套窗口不重复相加。exportFunc.Call包含guest运行、SDK/Runtime及host syscall/调度停顿，并非纯10M循环CPU时间。当前细分不能进一步分离循环、guest GC、CPU频率或调度影响。

## 本轮真实执行与重复性

本轮先跑原始/修复模式×R0/R1的小样本真实guest，每进程3次。为满足安全预检，该诊断预置1个Instance、逐调用后维护排空，R0确实复用同一业务Instance，R1每次用不同Instance并关闭。它不同于原空池连续负载，不作主TPS，也不替代三批100次。

| 方法 | 池模式 | 每模式成功数 | R0 Invoke均值ms | R1 Invoke均值ms | R0 export均值ms | R1 export均值ms |
|---|---|---|---:|---:|---:|---:|
'''+ '\n'.join(diag)+'''

normalCal原池诊断R1更慢，容量模式近似持平；这些仅3次/条件且有窗口外维护，不呈现旧约8ms同方向差异，但不能据此认定原异常消失或反转。正式原负载预检遇守卫停止，本轮未获得可用于重复性判断的100次主批。

## 环境因素核查与缺口

| 因素 | 实际检查 | 结论边界 |
|---|---|---|
| 执行顺序/热态 | 旧a/c为R0→R1、b为R1→R0；normal有效b/c/d仍均R1较快但幅度0.86–0.98 | 不是仅一组运行顺序；无频率/热态配对控制，不能排除偏差 |
| CPU频率 | WSL无sysfs cpufreq文件，见audit/cpu-frequency.json | 物理频率、温度/Windows调度未测，不能把8ms归因睿频 |
| 线程调度 | 本轮资源jsonl保存进程CPU ticks、last_cpu、leader_schedstat | 不是每笔guest CPU时间或全部native worker调度，不能量化8ms |
| host/guest GC | GOGC100两组相同；未修改GODEBUG，未取guest GC统计 | 未测暂停时间，不能声称GC是原因；host GC不等同guest Go GC |
| 后台工作 | 旧normal R1每进程106次创建（含验证）、旧b/c/d记录创建/业务区间重叠309条、关闭/业务区间重叠156条；R0亦有初始创建重叠12条 | 是保守记录区间交叠，不是原生race证明或CPU争用定量归因 |
| 业务路径/Gas | 原始和本轮功能样本输入、结果、Gas一致；SuccessResult一次 | 没发现工作量变更，但不认证Runtime全局/全部业务语义、Table或链上状态 |

最终状态：已定位差异窗口；Fresh更快的机制、正常负载下重复性及容量补丁的量化影响均未确定。安全前提修复后才可进行相同100次负载复验，不通过加入Copy或改计算量来解释。
''')
(ROOT/'README.md').write_text(f'''# Step-21A-实例池容量修复与normalCal归因

2026-10-26。**部分完成，按安全预检停止正式矩阵。** 已完成准确源码审计、24次真实guest功能调用及一次原空池路径fail-fast预检。不是仅分析旧报告；没有为完成100次而绕过守卫。

## 直接结论

1. 容量修复不是只修退出。c6addbf在正常grow中约束max-currentSize，可能改变运行期供给，Step21精确10～15倍不能认定完全不受影响。本轮没有安全完成原/修复版主对照，影响大小未知。旧原版100次已返回样本也有明显损失，但退出失败，只作诊断，不用跨批数字相减证明补丁无影响。
2. normalCal的Fresh更快未取得本轮100次重复证据。新功能预检原池R1更慢、容量池近似持平，但只有3次/组且库存/维护方式不同，不能推广。
3. 旧8.300ms CallMethod差异中8.294ms位于exportFunc.Call；参数准备、allocate/copy不解释主要差异。该窗口内具体原因尚未证明。
4. 本轮bigNum/normal功能样本均输入、返回、Gas一致（105920/100000072）。不认证Table、真实链上读写或R0普遍生产正确性。
5. **不足以安全进入Step22默认Fresh+Copy补池测试。** 同Store创建/执行/关闭所有权、native安全及原池退场问题需要先解决；Copy不解决这些前提。

## 已实际执行

| 阶段 | 实际执行 | 结果 |
|---|---|---|
| 审计 | 原dc4d63b/077a8cb与容量c6addbf准确diff | 非退出专用补丁，详见POOL_DIFF.md |
| 隔离功能预检 | 2方法×2池×R0/R1，每进程3次：8进程、24次真实业务 | 全部业务成功、输入/返回/Gas相同，正常排空 |
| 原空池TestInvoke预检 | bigNumCal、original、R0，请求3次 | 首次业务执行前触发粗粒度区间守卫，0次业务返回；保存栈，立即停止 |
| 正式100次矩阵 | 计划2方法×2池×2模式×3批=24进程 | 全部未运行，0主性能样本，formal_matrix.csv明确留空 |
| 分析 | 旧600条normal B5、新24条功能样本和安全现场 | 定位窗口；不生成新的正式TPS倍率 |

隔离功能诊断改变了初始库存（1）和逐调用维护等待，完全排除主吞吐比较。原空池预检则仍是库存0、原入口和连续调用；没有加全局锁或Sleep。

## 为什么停止，守卫证明了什么

源码共用p.store的构造、执行、异步Close没有统一所有权保障。为避免直接触发native不安全重叠，原/容量模式使用**同一binary和无等待atomic CAS守卫**：1=create，2=execute，3=close；争用则输出全goroutine栈并exit86，不等待、不串行化。InvokeTime原UnixNano起止未改，仅在获取Instance后加入共同执行区间守卫，原版/修复版通过显式CM_STEP21A_POOL选择grow内是否限额。

实际preflight-bigNumCal-original-r0-a.log:50记录owner1/requested2。栈显示调用线程在InvokeTime，worker在newInstanceFromModule→acquireWasiEnv→wasi_config_new。**这证明保守的创建/执行生命周期区间重叠，不证明采样时两次具体Store native访问同时发生**（wasi_config_new本身没有Store参数），更不是已复现native数据竞争/内存破坏。由于下一步Store访问/所有权保证没有建立，按本轮预登记的保守安全门停止。C API本地源码Rc<UnsafeCell<Store>>无统一外部同步的证据与packaged so哈希记录在环境中；本轮未重新认证二进制精确映射。

不得禁用守卫、略过初始grow、加入全局执行锁或把隔离诊断当原负载，来补出正式倍率。容量修复在grow计数上生效，不能替代Store所有权保障。失败进程为中止退出，其已创建对象未全部显式Close，不能写“正常排空”；进程结束后OS回收，全部自启进程已消失。

## 数值与正确性

小样本只用于功能/安全预检，完整数值在summary.csv（primary_accepted全false）。normalCal差异窗口和新功能表见NORMALCAL_ANALYSIS.md；CSV每进程完成后立即保存，没有等待套件结束。未执行组不填TPS，sample行0不等于0TPS。

资源阈值沿用2GiB硬限、RSS1536MiB、Tasks256、线程220、60秒；Go测试45秒；全局MemAvailable8GiB、SwapUsed1GiB。没有提高阈值、无界并发、节点压测或Copy/A/PB。新功能进程峰值采样约259.5MiB/25线程；守卫进程约207.4MiB/23线程。boot ID前后一致。Go race/native安全认证本轮未完成。

## 版本和复现

独立分支experiment/step21a-pool-normalcal，编译源码`{e['source_commit']}`，最终报告commit以分支HEAD为准；父c6addbf。原始差异audit/capacity-fix.patch，本轮共同诊断差异audit/step21a-source.patch。Go/OS/native/输入与binary哈希见environment.json/cases.json，未重编WASM或更新依赖。

脚本：run.py每次保存command/outcome/resources/samples并更新summary/PROGRESS；suite.py可恢复且遇STOP拒绝新执行；analyze.py仅重建CSV；audit_history.py读旧原始资料；report.py生成本报告。二进制未纳入Git，重建命令见audit/build-command.json；构建输出保存audit/build.log。

恢复只读操作：

```bash
cat PROGRESS.md
cat STOP.json
python3 -B scripts/analyze.py
python3 -B scripts/report.py
```

当前STOP为安全门，不允许直接重新启动正式批次。最小下一步是明确同Store所有权、初始化/执行/回收的可重入生命周期方案，两个模式同一补丁后重新登记主对照。正常负载下再取物理CPU频率/调度与guest GC证据，才有条件判断8ms机制。仅通过延迟请求、换WASM、改变业务量或加入Copy不能完成本轮归因。

回滚：弃用本实验binary/分支；不reset/clean生产工作区，不删除历史结果。本轮只提交独立实验分支，不推送远程。
''')
print('wrote README.md and NORMALCAL_ANALYSIS.md; formal remains blocked')
