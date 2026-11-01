# Step-35B：native WASI / Selector 线程生命周期

已定位并以单行补丁修复 Selector 关闭通知的 Token 不匹配。纯 C 及受控节点业务对照支持线程累积问题得到修复；**Step-36 准入仍不通过**，因为在途 Reset 与 Stop 重叠时另观测到 ChainMaker 账本后台写入已关闭 LevelDB 的 panic。本轮按停止边界保留现场，不扩展到账本停止协议修复。

| 对照 | 删除 1 个 WASI 后静默线程数 | 删除 4 个 WASI 后静默线程数 | 4 个 Selector 的 EXIT |
|---|---:|---:|---:|
| 原始已加载库 | 2 | 5 | 0 |
| 同源码重建未修复库 | 2 | 5 | 0 |
| 单行 Token 补丁库 | 1 | 1 | 4 |

上述 C 进程初始均为 1 个主线程，静默点为删除后 3 秒；补丁版在第 1 秒采样已恢复。线程身份由创建调用栈、TID、等待点、退出记录确认，详见 `audit/thread-identities.json`。C 的静默观察不是业务请求人为间隔，不是性能样本。

节点两轮各 compute+buyNow 后：未修复静默线程 19→27，补丁版 11→11。各组最终 Store20/20、Instance16/16、WASI16/16、Imports16/16；补丁节点峰值 RSS1156.88MiB，低于1536MiB保护线。此为有限 Smoke，不能推断长期资源完全收敛或通用生产安全。

- CVW 分支：`experiment/step35b-native-wasi-thread`，基线 `b00f3bad740166b88a817e3c1ff6ef83e11aff68`。
- native 分支：`experiment/step35b-selector-token`，补丁提交 `24b6afd79`，基线 `091074013fa056df0c6502262eae425927272e10`。
- 节点适配分支：`experiment/step35b-native-smoke`，提交 `72e077a`，基线 `d834ae392781d9ae8ea1dfc4de6919d30b639af4`。
- 实验工作树位于 `/home/frankie/mygitprojects/.worktrees/`；生产 CVW、原 native 工作区、旧动态库均未替换，未推送远程。

复算：`python3 scripts/analyze.py`。该命令只读取日志、生成派生 CSV/JSON，不启动测试。动态复现命令在 `audit/*-command.json`、`raw_logs/*-command.json` 中；当前 `STOP.json` 保留，禁止直接续跑节点测试。

交付索引：`ROOT_CAUSE.md`、`NATIVE_CALLCHAIN.md`、`PATCH.md`、`CORRECTNESS.md`、`SAFETY_GATE.md`、`NEXT_STEP.md`。二进制和 so 保存在本地 ignored `binaries/`、`libraries/`，哈希、源码、命令和日志纳入实验提交。

主工作区同名目录提供本提交的报告/源码/日志副本；运行产物仍在上述独立worktree，不在主工作区安装或替换动态库。当前交付为“native修复完成、节点最终准入被新发现的账本停止异常阻塞”。
