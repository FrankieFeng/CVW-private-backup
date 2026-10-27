# 计时源码与嵌套说明

所有新span使用`time.Time.Sub(e29Epoch)`保留单调分量；原profile保持原timer，不改起止。不同进程只比较duration，从不减绝对起止时间。每进程一个group、三个group进程组成匹配block。

- `source/vm/step21d_runtime_test.go` `dRuntime.Invoke`：进入创建result前time.Now；end defer在同步Close之后取end。新`invoke`span直接复用这两个time.Time，不替换计时。原profile/调用记录输出在end之后。六个子Invoke完全包含在root export内且串行不重叠，原Gas仍是嵌套累计边界，不相加。
- `source/vm/sim_context.go` `callContract`：既有exportCallStart/End只包`exportFunc.Call()`；新export span复用其时间。CallMethod还包含serialize、allocate、Memory写入、export查找/关闭，不能与export重复相加。
- `source/vm/step22_runtime_test.go` `makeE22`：NewInstance只包w.NewInstance；Copy只包plan.restore；S1包含两者及WASI/imports；WASI.Initialize/_start在S1后、S2前。G0原Module；G1/G2 noData Module加区间Copy，原Data初始化真正被替代。逐次Close同步CallDeallocate/managed cleanup。Module/模板在外预计算与缓存，未在每次Invoke重复编译。
- `source/vm/vm_bridge.go` `sysCall`：syscallStart到defer，包括Memory header/body拷贝、EasyCodec、Waci dispatch、内部cross及所有child执行。root-depth sysCall跨度互不重叠，union长度可从root export扣除。未覆盖段仍含Guest/其他导入与观测误差，不能称纯Guest计算。
- 同文件`callContractCore`：cross_get_gas包getGasByExport；cross_wacsi包固定依赖wacsi.CallContract；cross_set_gas包setGasByExport（成功路径）。get/set是实测宿主与Guest gas导出访问耗时。wacsi内部有EasyCodec/regex/contract查询/txSimContext.CallContract及SubtractGasForCallContract等，尚未逐个插桩。
- `source/vm/step21d_fixture_test.go` `s21cStore.GetContractBytecode`：fixture_bytecode_clone完整包函数；实际执行`return append([]byte(nil), b...), nil`。契约字节码独立拷贝的分配/复制/GC assist/调度均可在此发生，未分别测量。六次加载identity/ERC各3次；根f.run自身提前取字节码在root Invoke外，不能混入root export内六次clone合计。
- 同文件`GetContractByName` metadata是实际Contract protobuf marshal/unmarshal窗口。仅原本传给VM manager/txContext的logger加委托计时，logger等级/参数/实现不改；没有设置全局锁。
- `s21cEmit/e22Emit` JSON编码、原stdout write分别计时；只计原有输出，新span缓冲预分配4096条，上限守卫不允许扩容；统一STEP29输出在fixture关闭后、owner关闭前，root Invoke之外。trace缓冲/委托/时钟/方法字段格式化仍可能改变分配/调度，不能声称无扰动。

精确定义：每次root cross_wacsi内匹配唯一child invoke。`prepare=child.begin−cross_wacsi.begin`，`return=cross_wacsi.end−child.end`。child之前的fixture_bytecode_clone进一步单列。return包含child原计时之外的JSON日志、VM manager返回与Gas传播，**不是纯Gas结算**。没有child的第二次CallContract（取缓存结果）单列cross_no_child_wacsi。纯Gas传播算法与Guest JSON未可靠分离，保留未归因。

`ROOT_TIMING.csv`为root及聚合窗口，`TIMING.csv`为原始所有root/child/init/异常profile，`HOST_SPANS.csv`为有span的成功调用逐段记录（异常原span保留原始STEP29日志），`CHILD_PREPARATION.csv`为六次prepare/return。ROOT_TIMING早期build1预检缺clone/logger观测时写空值，不把缺失写成已测0；主统计只formal/valid_block且build3或原binary。

脚本`spans.py`在每个trace成功目标调用检查root/export包含、child6次且不重叠、root sysCall互不重叠、children≤syscalls≤export；`verify.py`再次验证正式90trace进程、六次clone、原始源码/二进制、历史文件SHA及资源退出。此为计时/生命周期覆盖校验，不能代替真实Table函数身份验证。
