# 线程未收敛：有native/WASI因果对照

resource2同一节点，常规GC/参数不变：

| 检查点 | 已创建/关闭WASI | OS线程 | epoll等待线程 | Go thread-create records |
|---|---:|---:|---:|---:|
| 启动 |0/0|8|1|9|
| 第1轮后 |8/8|17|9|14|
| 第2轮后 |16/16|27|17|16|
| 第3轮后 |24/24|35|25|16|
| 静默、Reset及GC/scavenge后 |24/24|35|25|16|

新TID和wchan原件在snapshot JSON。Go thread-create profile为累计记录，不能与当前OS TID一一对应；但后两轮该记录不增，OS epoll线程仍每8次WASI增加8，不能都归因于Go M缓存。

纯C对照使用完全相同native so，不运行Go、Guest或节点：

- 4次Store创建/删除，Engine关闭后及静默3秒始终1个主线程、0 epoll。
- 4次Store+WASI环境创建/删除，所有Store的最后strong count均1；Engine关闭、静默3秒后仍5线程/4 epoll。
- 另一个仅1次WASI的进程，静默1、3、10秒均为2线程/1 epoll。

因此，已经直接复现WASI创建/关闭路径的线程回收缺陷或至少观察窗内持续残留，不是只有“缺少安全证明”；不是合约业务或Go Finalizer造成的必要条件。不能将10秒有限观察写成数学上证明永不退出，但当前也没有平台证据。

源码/二进制指向virtual networking Selector：本地候选源码PluggableRuntime::new会创建LocalNetworking/Selector及独立poll线程。当前源码shutdown设置close_requested并wake；实际固定so的Selector::shutdown @0xabf070只调用mio Waker::wake（重定位及反汇编已保存）。旧实现有两个waker/token；历史修复`e3c75f14f3d`改成单waker+关闭标记。本轮仅保存该patch供定位，未修改或重编so。

已证实：native存在Selector符号，实际shutdown机器码与当前候选源码不同，WASI-only产生epoll残留。尚未完全证实：每个残留TID的用户态栈正是该Selector，以及该历史patch单独能消除当前二进制缺陷。gdb本地未安装，未为此更新环境。

不采用WASI复用、进程反复重启或线程上限放宽来掩盖增长。下一步必须在可追溯native构建上修复并验证关闭/唤醒/线程退出。
