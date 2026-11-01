# Step-36准入：不通过

| 条件 | 判定 |
|---|---|
| Store/Instance调用级创建删除配平 | PASS；4节点进程退出，pending0，51实例/66 Store总体配平 |
| 最后strong析构分支 | resource2及C对照有直接只读观测；不是仅CAPI次数推断 |
| RSS归因 | 部分通过：缓存、Go retained页、glibc free arena有直接证据；自然长驻平台未证明 |
| 线程收敛 | **FAIL**：每个WASI关闭后仍新增epoll线程，纯C隔离复现并持续10秒 |
| 节点级Reset | PASS：9次实际Manager入口，覆盖空闲、连续和compute/buyNow在途 |
| Reset后继续执行及排队 | PASS（已覆盖请求）：14笔新业务查到提交；buyNow真实六下游 |
| Stop/Reset竞态与退出 | 最小修正后PASS于已覆盖顺序；真实重叠Stop/Reset exit0，硬保护保留 |
| 1536MiB下合理余量 | 有限4合约诊断峰值1214.668MiB，但存在持续线程残留，不能据此签发长期/扩大负载准入 |

当前不是“所有Store生命周期都没做完”的泛化阻塞，而是一个明确native/WASI后台线程关闭问题。不能靠增加RSS/线程上限、反复重启、强制GC或复用WASI绕过。

不启动Step36正式Copy E2E；不将本轮观察器耗时当作性能样本。最小下一步是针对固定native构建恢复/回移Selector关闭修复，保持Wasmer版本、ABI、Gas与编译器其他配置不变；先通过Store-only/WASI-only线程对照及10秒静默，再复核节点Reset资源平台。该原生修复本轮未执行。
