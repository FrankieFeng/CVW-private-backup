# normalCal差异归因：定位窗口，未证明机制

## WASM、输入和工作量

两模式同一compute-go.wasm，SHA256 `e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507`；100行输入文件SHA见cases.json。本轮没有重编合约。当前二进制重新只读反汇编，main.normalCal包含i64.const10000000及循环比较，见audit/current-normalcal-disassembly.txt；没有为了倍率改循环。

原Step21正常计时的b/c/d三对逐索引参数哈希相同，Gas均100000072，返回success normalCal:666。返回值是常量，单靠结果相同不能证明循环量；相同二进制、固定循环和Gas共同构成证据。当前对应源码normalCal只使用局部循环及SuccessResult，没有自定义业务缓存/持久读写。旧原始B5每次syscall_count=1、syscall_method=SuccessResult；未发现GetState/PutState路径。精确嵌入SDK构建源未重建，不将本地SDK代码视为完整来源证明。

Go Runtime/SDK仍有实例内全局、堆栈和初始化状态，R0保留、R1重建；未认证这些状态完全相同，也未证明某个缓存/GC造成8ms差异。WASM中runtime相关全局检查不应直接命名为业务缓存。

## 原始细分定位（此前300次/模式，不是本轮新性能样本）

直接读取旧raw_logs的600条B5，不引用报告数字推断。详见audit/previous_normalcal_components.csv和history-observations.json。

| 窗口 | R0均值ms | R1均值ms | R0−R1 ms |
|---|---:|---:|---:|
| InvokeTime | 82.118080 | 73.870941 | 8.247139 |
| CallMethod | 81.975486 | 73.675233 | 8.300253 |
| exportFunc.Call | 81.739296 | 73.445268 | 8.294028 |
| allocate | 0.013943 | 0.031438 | -0.017495 |
| copy+lookup | 0.006846 | 0.014581 | -0.007735 |

约8.300ms的CallMethod差异中，8.294ms落在导出函数调用窗口（sim_context.go:186–191，time.Sub单调计时）。不是靠不同中位数相减，而是同批原始逐调用时长总量/均值分解；嵌套窗口不重复相加。exportFunc.Call包含guest运行、SDK/Runtime及host syscall/调度停顿，并非纯10M循环CPU时间。当前细分不能进一步分离循环、guest GC、CPU频率或调度影响。

## 本轮真实执行与重复性

本轮先跑原始/修复模式×R0/R1的小样本真实guest，每进程3次。为满足安全预检，该诊断预置1个Instance、逐调用后维护排空，R0确实复用同一业务Instance，R1每次用不同Instance并关闭。它不同于原空池连续负载，不作主TPS，也不替代三批100次。

| 方法 | 池模式 | 每模式成功数 | R0 Invoke均值ms | R1 Invoke均值ms | R0 export均值ms | R1 export均值ms |
|---|---|---|---:|---:|---:|---:|
| bigNumCal | original | 3/3 | 0.548 | 0.477 | 0.334 | 0.259 |
| bigNumCal | capacity | 3/3 | 0.363 | 0.392 | 0.205 | 0.208 |
| normalCal | original | 3/3 | 72.912 | 78.763 | 72.558 | 78.434 |
| normalCal | capacity | 3/3 | 75.153 | 75.197 | 74.892 | 74.856 |

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
