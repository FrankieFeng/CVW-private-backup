# Step-39E 可恢复进度

状态：已完成，等待人工审阅，不自动启动Step-40。

## 已完成

- 基线审计：CVW 7a9b3b82，节点8ff98d6；没有引入39D抓栈watchdog。
- 实现：组件启动事件、实际规则消费者/完成计数、原safe队列双确认标记、真实SDK提交探针及对应高度消费确认。未改2秒等待、channel容量、共识、Gas、Guest、VM Owner、C0 Ranges。
- 构建：observer单元检查通过；有效节点构建为node-r2。overlay/GOMODCACHE及初始go指令问题的失败日志均保留，未升级外部依赖。
- 运行：4个部署seed；3次独立启动验证（18目标交易）通过后才进入3批E0/E3稳态预检（72正式交易）。没有秒级目标慢笔、失败、超时或剔除样本。
- 正确性：六个直接配对方法批次精确Gas/返回/事件/读写集一致；全部130次SDK业务Invoke/Query另行复核期望输出。
- 生命周期：6次Manager Reset不刷新32预算，Reset后继续真实交易；4个新进程重启查回24笔正式交易并继续业务。23进程均退出0，Store163/163，Instance134/134，native pending0。
- 资源：RSS采样峰值679.215MiB、OS线程峰值29，1536MiB/220线未提高。当前无测试进程。
- 工作集：历史37个PASSED方法/8合约的plain/A产物核验通过；总量约35.9MiB，8/64MiB限制保持。Step40按方法/配置隔离进程，根调用总预算预先≤32。

## 结果文件与复算

README.md、READINESS.md、RESULTS.csv为主交付。WINDOWS.csv、SUMMARY.csv、PAIRED_EFFECTS.csv、STARTUP_COLD.csv、GATE_EVIDENCE.csv、RESOURCES.csv支持复算；raw_logs保存所有SDK/节点/收据/退出记录，evidence保存diff、命令、来源、哈希及失败构建。

只读复算命令：

```sh
python3 scripts/analyze.py
python3 scripts/report.py
```

实际运行入口及逐进程argv已保留：study.py seeds、study.py validate、study.py formal、restarts.py。不要在已完成目录重建二进制、重写验证准入标记或重复正式运行。中断恢复先读结果文件和历史progress-checkpoints，不按旧后台状态重启。

## 当前限制及下一步

已知启动背压在本轮有界样本中被排除，不宣称永久无尾延迟。每组18笔/仅3独立批次；bigInput收益CI跨零，部分批次反向。新屏障只认证单链隔离Harness，不是生产启动/并发准入。完整进程生命周期TPS未统一测量，不用阶段Median相加构造。

节点实验源码提交：c6382c3babff6841f33f68a993a372761aa50c66；其二进制在提交前构建，Go buildinfo为8ff98d6+modified，实际源文件哈希已冻结。CVW实验提交随后完成；不推送远程。原始39C/39D及生产基线未改。

下一步命令：阅读README.md和READINESS.md，人工决定是否启动Step-40。当前不再执行交易。
