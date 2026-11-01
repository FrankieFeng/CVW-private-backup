# Step-36 准入：NO-GO

| 门槛 | 证据与判定 |
|---|---|
| Selector根因定位 | PASS：真实库创建/唤醒调用栈、epoll token与同源单行对照 |
| C单次/四次WASI删除后Selector退出 | PASS：补丁各线程EXIT，静默恢复主线程 |
| native所有权/Module缓存未改变 | 源码单行差异；Owner与真实业务测试通过 |
| 节点compute与真实buyNow | PASS：成功提交、结果/Gas/规范化读写集/事件一致 |
| 有限资源阈值 | PASS于已执行样本：1536MiB/220线程软阈值未触发；不代表长期完全收敛 |
| 空闲/在途Manager Reset | PASS于两组已覆盖compute/buyNow和Reset期间排队请求 |
| Reset与Stop重叠、节点完整排空 | **FAIL**：patched-stop-node.log exit2，账本historydb写已关闭LevelDB |
| 补丁组重启及真实失败回滚 | not_tested，异常后停止 |
| 同步join/强有界native shutdown API | 未新增；现有异步协议实测及时退出，非任意调度下时间保证 |

结论：native逐WASI Selector累积问题在本轮受控对照中已解决，但不能称已解除Step-36最后一个准入阻塞。必须保留账本停止/写入排空阻塞及补丁组未完成项。本轮未启动客户端E2E性能矩阵，未提高内存/线程阈值，未关闭守卫。

`patched-stop`失败后MainPID0、cgroup空、RPC27535无监听；没有遗留实验节点。systemd失败记录保留作为现场。未故意重启同一失败账本验证恢复，避免扩大范围。
