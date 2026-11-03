# 资源汇总

| 实际节点进程 | RSS采样峰值MiB | OS线程峰值 | Store创建/关闭 | Instance创建/关闭 | 最长正常关闭秒 |
|---|---|---|---|---|---|
| 108 | 652.172 | 45 | 814/814 | 706/706 | 0.043 |

包含6个部署节点、25个预检节点、75个主实验节点和2个反序节点。均退出码0、PID退出/cgroup空、native managed_pending0、Store/Instance配平。原软限制RSS1536MiB、线程220、Owner根调用32未提高。正式普通方法每节点根预算7，raffle5；caller的子调用不另占根预算，实际Instance数量已计入资源总数。

G4最多单合约Artifact1项，8项/64MiB原限制及满容量拒绝策略保留；关闭后检查entries/bytes归零。RSS为原监控采样值，不是长期无泄漏证明。没有强制GC、后台并发Fresh或异步关闭路径。

最初配置归档路径误写audit而实际在evidence，失败seed未启动节点、没有SDK交易；原空目录、失败JSON和driver traceback保留，未算作成功节点或链上失败。后续六个新seed-v1部署及所有实际实验均成功。
