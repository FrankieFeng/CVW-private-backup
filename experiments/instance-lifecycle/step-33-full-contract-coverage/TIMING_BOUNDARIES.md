# 计时边界

source/vm/step21d_runtime_test.go:226 dRuntime.Invoke 入口time.Now到defer记录InvokeNS（含先注册的同步close defer执行），不含外部f.run创建模拟交易上下文/提交内存账本/收据写盘。不是SDK E2E，也不是默认Pool的InvokeTime。

source/vm/step22_runtime_test.go:140 makeE22：WASI imports准备→NewInstance→（Copy组restore）→S1→WASI Initialize→_start→S2→host/memory绑定；NewInstance单窗不含restore，S0→S1包含imports/NewInstance/restore。S1验证hash只在preflight，不作为formal性能样本。

source/vm/step21d_runtime_test.go:350 CallMethod窗口嵌套exportFunc.Call；S3NS在CallMethod和Gas读取/传播之后记录。因此S2→S3包含业务执行和结算，不是CallMethod之前的剩余准备！close在S3之后，完整Invoke包含close。NewInstance/Copy/_start/CallMethod/export为嵌套或子窗，不能与to_s2/to_s3重复累加。

source/vm/step25_test.go:25 e25Prepare：模板解析与noData变换→Store/Module编译→缓存；发生在init、setup和正式目标调用之前，每个组/进程一次；通过MODULE_PREPARATION.csv单列。Baseline也预建plan供S1预检，但正式NewInstance仍用原WASM。

输入初始化和所有真实prerequisite既不计入目标Invoke，也没有固定等待让后台补池：本轮没有后台池。监控25ms polling不是业务请求间100ms Sleep。
