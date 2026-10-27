# 正确性及安全边界

新增102个测试进程全部通过：90正式进程180对，6个预检进程12对，6个独立CPU/GC诊断进程6对，共198个严格配对。编译失败和准备期脚本问题另保留，不冒充Guest测试失败或有效样本。没有因性能不利剔除样本。

## 核对的内容

所有目标调用返回`success normalCal: 666`，状态码/错误码正确；观察到的CallMethod错误均`<nil>`，不是仅依赖Go测试PASS。每对比较实际返回值/消息、Gas、初始/最终账本、根实际RWSet、事件及调用记录。输入为相同空业务参数、固定`step27-normalCal-fixed`，所有目标调用前恢复同一真实init后的外部账本。R0 Guest运行时状态保留，不清缓存、不deallocate追平；外部账本clone不等于恢复Guest快照。

原件R0/R1/C1 Gas全部100000072；Step18 R0/R1/C1/C2全部100000019。不同家族的差异公开保留，未修改Gas规则，也未用相同返回值或Memory hash推断Gas相等。

每个R0/R1进程只编译一个Module；所有目标StoreID和ModuleID完全相同。R0 init实例ID保持不变，prior uses记录1/2；R1每次新ID、uses_before=0、每次同步关闭。ABBA预检确认R1两次关闭后R0仍能正确执行。所有Fresh C1/C2同样uses_before=0；它们的独立Module/Store结构与R0/R1共享结构分别记录，不能混称纯Reuse因果。

原active Data与noData+Copy在对应逻辑WASM的预检S1都对照各自模板全Memory hash。R0初建init阶段可核对S1，reuse后Memory已执行，不强行和初始模板相等；逐次重置profile避免把init NewInstance/start/Close时间重复计入。A变体S1布局不同，不要求跨WASM整内存hash相等。正式性能不计算S1 SHA。

关闭维持原守卫：Fresh关闭后native对象数回到创建前，R0目标调用前后native live数一致，最终R0关闭仍按原创建base检查；最终created=closed、in_flight=0、managed/pending=0。所有PID/cgroup退出。R0最终关闭在RETAINED_CLOSE单列，完整Invoke不含进程最终Store/Module关闭。

## 未验证项

- Table真实函数身份：not_tested，保留section不等于验证每个funcref身份。
- 异常/OOG/回滚、真实跨合约：not_tested。
- 多Instance同时互写压力隔离：not_tested；本轮只验证受控串行及R1关闭后R0仍可执行。
- Guest GC/Guest内部缓存内容、具体动态函数分支：not_observed，不猜偏移。
- 长期Store资源有界性/线程即时join：not_tested；WASI线程随Store存活累积仍存在。
- 原池后台并发创建、异步关闭、跨线程Store访问、节点并发/TPS：not_tested且未运行。
- 原件A构建：blocked；不能用Step18不同WASM冒充原件C2。

安全阈值未提高，使用原768MiB/125线程软限，2GiB/256task硬限，Go45s/process60s及available8GiB/swap1GiB。实际峰RSS401.23MiB、host heap objects63.56MiB、线程109。每个共享Store最多R0一个+R1两个WASI；每Fresh Store最多init+2。每批10次由5个短进程组成，不是同Store长时间负载。固定OS owner/ManagedScope规则未解除，未添加全局锁。
