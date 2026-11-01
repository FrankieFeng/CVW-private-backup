# 最小同步修正与诊断差异

`source/vm/step34_owner.go` 的Stop/Reset修正：Reset在mutex下创建resetDone；工作和回收结束后close广播；Stop遇到resetting时等待该广播，再进入既有排空/清理流程。不是向无接收者的channel发送；先Stop时Reset依旧拒绝。未新增Guest执行全局锁，没有修改Owner的32外部job上限。

`TestStep35AResetStop` 覆盖Reset正在等待活动job时Stop超时等待、后续正常排空、Reset期间拒绝新job；`TestStep35AStopThenReset`覆盖反顺序拒绝。真实节点stop-reset-race覆盖同一Manager入口与进程停止链。

其余均为实验诊断：0600 Unix control、WASI/import容器计数、mallocinfo2、/proc任务/内存快照、固定ELF私有Store强引用只读探针。不得将私有布局观测混入通用绑定API或性能基准。没有改native库、Gas、Guest、Module缓存策略、A/Copy机制。

node1为早期构建未用于节点；node2用于resource1/reset1（无强引用探针/Go thread profile）；node3用于resource2/stop-reset-race，非test Go源码冻结不变。vm3仅增加第二种Stop/Reset顺序的unit测试。每条原始记录有二进制SHA；不把不同观察版本拼为性能配对样本。

纯C诊断两个源码版本分别增加10秒观察窗，均使用相同so；编译器提示/proc路径字符串理论截断，实际task目录仅数字PID且远小于缓冲容量，未发生截断或程序失败，原警告保留。
