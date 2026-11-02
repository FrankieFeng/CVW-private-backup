# 建议与停止点

- 不自动开始Step39，不运行真实节点/全量E2E。
- 保留原C0；下一轮若继续区间归因，先做固定copy字节量的分块控制，不同时改算法和业务。
- 对step35_node.go runtime/Invoke/prepare做不可变bytecode record草案，明确源[]byte所有权、升级/版本失效、同名不同binary、跨合约校验。只能在正反例通过后减少重复hash/copy。
- 分窗先做独立A/B校准，考虑更小timer mark和低扰动输出；不能把fact观察到的插桩成本隐去。allocation仍与timing分开。
- WASI优化先审计native wasi_config_new中的Tokio Runtime/FS创建及所有权；不能缓存整个Env或直接共享native imports，Selector/Stop协议必须保持。NewStore本身只几微秒，低于上述优先级。
- 若后续拟进节点，只带单项通过独立确认的修改，使用Step35C准入与固定patched so；不扩大并发、内存或任务限制。

本轮结果可用于说明“更少区间不必然更快”“成本分窗与真实字节量”的研究现象。论文中的普遍阈值、净E2E收益、精确Native内存流量与长期资源结论仍需独立样本。
