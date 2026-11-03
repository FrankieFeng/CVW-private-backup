# Step-39C有限节点E2E建议：可条件准入，当前不启动

本轮缓存生命周期/正确性通过，G2→G3在三个方法上探索性收益为正且无明确严重回归，因此建议进入下一轮有限节点E2E。它是下一轮实验方案，不是宣称节点集成已完成或可以生产运行。

进入前最小条件：

1. 在独立节点实验构建仅接入本轮SHA-only及Manager有界治理，保留Runtime Clone、输入SHA、Copy C0、原Owner/Selector/Core drain/Gas。核对实际加载库及源文件SHA。
2. 对实际节点Manager Reset/Stop、真实部署升级和同版换码作少量Smoke，检查缓存容量拒绝能返回明确错误；旧Module不能被提前释放。VM夹具手工改metadata不替代节点部署升级语义。
3. 固定同源A/非A WASM、SDK提交确认路径、等价初始账本与业务输入；先只做有限同方法G0/G1或G2/G3，不扩37方法，保留失败/反向样本。
4. 根Runtime创建/Clone在Factory之外；同时记录SDK/RunContract/Factory边界，避免把准备成本移动到窗口外当作净收益。
5. 原Owner总根调用预算32不变，init/setup/warmup也需计入；按需部署buyNow依赖，达到预算结束进程，不提高限额。保持1536MiB/220线程及关闭/排空检查，剩余margin不足就停止。

当前不需要为E2E扩大为LRU或重构Owner，也不据此启动WASI/Tokio新研究。HashCal无A对照CI跨零，不承诺所有合约稳定获益。下一轮若性能收益未传递到客户端再记录结论，而不是追加无界负载。

完成本轮后停止，不自动开始Step-39C、不推送远程。
