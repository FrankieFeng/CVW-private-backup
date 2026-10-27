# Step-28既有证据审计（新Guest运行前）

来源commit29950ab，完整原件保留在step-28-six-method-acopy；所有Step29复算/新样本单列。原始30区块/3批/90个独立group进程，不是原池并发。原始代码snapshot e7924d8、binary01e9c03c410a271e4f29e8eba6a59eb31ee4a98026bd96e473ff0043ad5e5e09。

根dRuntime.Invoke：step28/source/vm/step21d_runtime_test.go:232进入time.Now，end defer在同步CallDeallocate、managed cleanup之后取time.Now；结果profile输出在end之后。含WASI/imports、NewInstance、restore、Initialize/_start、SetGas、CallMethod、GetGas及同步Close，不含module/template准备与init_contract。根export在sim_context.go:187–193精确包exportFunc.Call；CallMethod包含allocate/copy/lookup和该export。子dRuntime.Invoke在根guest调用宿主sysCall时同步进入，六次串行且均嵌套根export。所有duration使用Go time.Time带单调分量，跨进程从不相减；TxID只用于关联。同一个root与children使用同进程同一单调时钟。原始wall UnixNano用于标记，不用作新的精密差。

旧数据可复算：G0→G1根Invoke −2.870ms CI[−11.853,4.898]；G1→G2 +5.077 [1.377,11.337]；G0→G2 −0.058 [−5.813,10.977]。根export扣6个非重叠子Invoke后剩余：G0→G1 −7.025[−9.145,−5.275]，G0→G2 −7.566[−9.261,−4.891]。不能把各自中位数相加；这些数字只代表旧样本，本轮不会混合做CI。

缺失：旧profile没有各sysCall span、cross wacsi准备/返回span、host日志JSON encode/write成本；B5内部已有SyscallNs累计但未输出到旧profile。因此旧日志只能定位到残余，无法把7ms归给JSON、Gas、Guest或调度。日志文本时间戳不能补出未采集窗口。

真实调用链：root exchange.buyNow依次identity.addWriteList、identity.isApprovedUser(from)、identity.isApprovedUser(to)、ERC721.mint、ERC721.setApprovalForAll2、ERC721.transferFrom。Cross宿主vm_bridge.go:389 callContractCore先getGas，调用wacsi.CallContract，合并结果/事件，再setGas。wacsi_with_gas.go:184在固定Step21C VM依赖中解析EasyCodec、校验参数/regex、查合约、txContext.CallContract、SubtractGasForCallContract及累计Gas。**此段是EasyCodec，不是host JSON解码**。Go合约源码里的JSON属于Guest，不能用宿主JSON计时冒充。已确认的host JSON为e22Emit/s21cEmit诊断输出与最终root回执落盘；回执落盘在根Invoke外，child profile/return输出在其end之后、仍在根export内。

最小新增观测：沿原时钟保存root/child Invoke与export begin/end、每个sysCall、cross getGas/wacsi/setGas，以及原有诊断JSON encode/stdout span；仅预分配内存append，root调用外统一flush。每个wacsi中若包含一子Invoke：entry→child.begin称准备合计，child.end→wacsi.end称返回合计，后者含child日志/VM管理器与Gas传播，不能全部命名为Gas。纯Gas getter/setter单列，wacsi内部Gas计算未单独插桩，保留未分离。root export减root-depth sysCall并集称“未被已观测sysCall覆盖”，不是纯Guest CPU。无插桩原binary作同期对照，不用旧样本替代新控制。

计划先功能/时间覆盖预检。若通过，3批×10个三组区块；为直接检查扰动，每块同时保留原binary与trace binary的匹配三组，共180个独立group进程/180正式根调用，3进程组成一三组区块；不把同Store预算扩大。六种组顺序均衡，trace/off顺序交替。Soft1536MiB/220线程、hard2GiB/256tasks、45/60s、全机8GiB available/1GiB swap守卫与Step28一致。正节省=左−右，10000次batch→整块bootstrap seed290029，CI仅短期3批探索，主/诊断两套不混合。
