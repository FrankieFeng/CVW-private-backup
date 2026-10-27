# Step-30：Copy端到端性能验证——审计与安全阻塞交付

本轮**没有启动新节点、客户端或发送新请求**；新E2E样本/有效配对/独立批次均为0。已完成历史口径、原始日志、二进制/源码与资源停止审计。保存的Step17/20节点未接入后续固定owner/managed-native回收协议，且旧RSS增长未闭合；按任务安全要求停止在新运行之前。未临时重写运行时或通过全局锁/抬限绕过。

先读[AUDIT](AUDIT.md)，再读[RESULTS](RESULTS.md)、[计时边界](TIMING_BOUNDARIES.md)与[正确性/缺口](CORRECTNESS.md)。真实SDK路径是InvokeContract(...60,true)→SendRequestSync→节点提交结果dispatcher返回；不是AddTx ACK，也不等于独立验证全网确认。

交付中的`E2E_SAMPLES.csv`是**历史Step20原始207响应+1个未知在途请求**的复算，每行origin_step=20/is_step30_new=False，不是新实验。PAIRED_EFFECTS、THROUGHPUT明确标注旧描述值与Step30 blocked缺失值；新缺失时延/CI/TPS不填0。原始客户端/VM/资源日志的逐字副本在raw_logs/historical-step20，未复制密钥、证书、账本。historical/目录为额外复算。

分支experiment/step30-e2e-copy-validation，父f1609b80；不修改生产VM、不推送远程、不制作PPT。原e20-e2e-copy-attribution路径未找到，实际已更名为step-20-e2e-performance-attribution。

离线复核（不启动网络/编译/测试）：

```bash
python3 -B scripts/environment_audit.py
python3 -B scripts/check_step17.py
python3 -B scripts/reanalyze.py
python3 -B scripts/report.py
python3 -B scripts/verify.py
```

命令在本实验独立worktree目录运行；绝对历史路径依赖现有CVW环境。IDE镜像用于查看。当前没有可放行的节点运行命令：不要将旧Step20脚本改标签继续跑，也不要重启其他监听端口的既有节点。未来准入与受控新E2E协议见TIMING_BOUNDARIES。

回滚：本轮未启动任何节点/客户端、未改VM/SDK/配置/资源上限；只需保留本目录并切回原分支。没有需要停止的本轮服务，不能误停其他实验/生产进程。
