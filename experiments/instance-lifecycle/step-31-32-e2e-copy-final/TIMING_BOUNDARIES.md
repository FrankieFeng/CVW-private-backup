# 本轮计时与缺失值

新E2E未启动，所有新Median/Mean/P95/配对CI/正向比例/成功率/吞吐均not_measured，不能填0或从Step20搬入。本轮只有两个既有协议测试的新日志，RESOURCE_SUMMARY标记not_node_E2E。初始配置拒绝进程也保留。

未来客户端主窗口保持SDK调用开始→同步响应返回，使用同进程单调time.Now/time.Since；不含Python启动/SDK初始化，不以driver管道窗替代SDK窗。旧client只保存elapsed，SDK绝对begin/end缺失；新请求应另存这些时间。

历史同步路径已由Step30源码追踪：SendRequestSync注册TxID→AddTx→本地PutBlock返回→BlockInfo事件→结果dispatcher→RPC响应。它覆盖本节点提交结果通知，不提供每笔精确PutBlock完成时间或全网最终性；没有独立提交事件时间窗时不报告独立成功提交TPS。

VM factory外层包runtime.Invoke，旧STEP17内部invoke_ns在根锁之后；后者不含锁前模板/Module准备与根锁等待。S1含NewInstance+Copy，旧S2-S1是WASI+_start合计；不能补造独立NewInstance/_start。Step28/29测试管理器另有完整窗口，不是客户端E2E。根与子调用嵌套，不能重复相加；同TxID重执行须保留全部尝试。不同进程timestamp不直接相减。

客户端成功响应速率=成功响应唯一TxID数/明确SDK/driver观测墙钟窗；提交TPS=确认提交唯一TxID数/明确提交事件窗；VM日志等效速率=筛选成功调用N/同集合factory Invoke秒数之和。王浅秋恢复脚本另有并发N/(maxEnd-minStart)及过滤顺序差异，旧入口未完全确认；这几种指标不得混用。本轮所有分子/分母均缺新测量，THROUGHPUT留空而不写0。

未实施新的高开销VM追踪，也不研究clone内部。若将来改变安全生命周期，必须冻结新节点构建与计时协议、单列一次性准备和每调用成本。当前只冻结协议，没有运行。
