# Step-21A-实例池容量修复与normalCal归因

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

独立分支experiment/step21a-pool-normalcal，编译源码`3c01a4b9937ca5bfd061f3484fe9f074a7def1d0`，最终报告commit以分支HEAD为准；父c6addbf。原始差异audit/capacity-fix.patch，本轮共同诊断差异audit/step21a-source.patch。Go/OS/native/输入与binary哈希见environment.json/cases.json，未重编WASM或更新依赖。

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
