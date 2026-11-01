# 真节点Manager Reset验证

Unix socket只在CM_STEP35A_CONTROL显式设置时创建，权限0600，无TCP监听。/reset POST直接调用实际节点InstancesManager.ResetAllPool，未用内部clear函数冒充公共入口。/state只读Owner准入状态；/snapshot通过既有Owner取数并计入32-job预算。生命周期数据与原始控制响应保存。

实际节点9次Manager Reset：resource1的两次空闲/连续Reset；reset1的空节点Reset、compute在途Reset、buyNow在途Reset；resource2两次空闲Reset；stop-reset-race空闲及在途Reset。全部返回nil，9个开始/结束配对。

- compute在途Reset约545ms、buyNow在途Reset约2004ms；先排空当前调用，buyNow六次真实下游完整返回。
- Reset清理后可继续真实交易，缓存重新建立。两笔Reset期间提交的compute请求都成功提交；其真正进入VM在manager_reset_end之后（ADMISSION_ORDER.csv）。因此本次观察到节点排队，不是丢弃，也没有伪称VM层发生了拒绝。
- Owner层拒绝新job的分支由unit直接验证；本次节点调度没有让这些后续交易在resetting窗口进入VM。两类证据分开。
- 没有触发旧resetC无缓冲发送路径，新适配器仍路由到Owner.Reset。
- Stop/Reset源代码发现：原Stop在resetting时返回ErrOwnerClosed，节点可能继续关闭账本。新代码等待resetDone，然后执行Stop；先Stop后Reset则拒绝Reset。两个unit顺序通过。
- 真节点stop-reset-race在Reset等待真实在途compute时SIGTERM，Stop等待Reset和当前调用；Store2/2、Instance1/1、pending0、进程exit0。客户端因停机未收到成功响应，提交未确认，不能写成“Stop时交易绝不丢失”。Reset正常组的在途/排队交易均逐TxID查到了提交。

Reset后：Module缓存0、Store创建关闭配平、WASI/Imports配平、host登记0，但native epoll线程不随Reset下降。所以Reset协议功能通过不等于资源准入通过。

原始证据：reset1-node.log、*-reset-*.json、*-admission-*.json、stop-reset-race-node.log，RESET_EVENTS.csv、COMMIT_CHECKS.csv、owner-both-orders.log。没有全局执行锁、100ms补池等待或关闭守卫；1秒静默窗口只用于观察资源，forced GC/scavenge在业务完成且Reset之后单列。
