# Step-23 复现、恢复与回滚

执行工作树 `/home/frankie/mygitprojects/.worktrees/cvw-step23`，父394d291，分支 `experiment/step23-buy-now-gas-attribution`。主CVW同名目录为IDE阅读镜像，运行请进入实际执行目录，不能把镜像的绝对go.work误认成已自动迁移。

```bash
cd /home/frankie/mygitprojects/.worktrees/cvw-step23/experiments/instance-lifecycle/step-23-buy-now-gas-attribution
# 只复算原始数据，无guest执行
python3 -B scripts/analyze.py
python3 -B scripts/write_report.py
```

统计为实际Gas整数/状态对比，无TPS、无耗时倒数、无跨进程时间相减、无性能显著性推断。5个独立配对块每个条件只有1根，合计每阶段10根，不是每组100次或5轮压测。初始化与正式目标TxID明确分开；全部调用和构建失败都保留。

环境固定：Go1.25.0、ChainMaker现有v2.4.0模块、原native6.0.1及SHA、原Gas映射、BlockVersion1/ETHEREUM地址类型、公开测试公钥/member夹具；三个WASM、参数、TxID、配置均固定。依赖本地Step21C工作树和module cache，GOPROXY=off；缺失artifact不能换版本继续。精确WASM SDK重建及native构建源码映射仍未认证。

若确需另做复验，原始实际命令在 `raw_logs/*-command.json`。先恢复固定库，输出到新build文件，保留旧binary/log：

```bash
python3 -B scripts/restore_native.py
python3 -B scripts/build.py replay-build
```

build脚本更新environment.json指向新binary，**会改变后续run选择**；因此复验应在新结果目录/分支复制夹具并保存旧environment，不能在本轮目录直接混入新版本。每进程的command.json单独冻结binary SHA和env，原日志不会因environment更新而失去证据。

本轮实际运行方式（示意新label，不会覆盖旧label）：

```bash
python3 -B scripts/run.py new-preflight-R0 R0 --probe on
python3 -B scripts/run.py new-preflight-R1 R1 --probe on
python3 -B scripts/compare.py new-preflight-R0 new-preflight-R1
python3 -B scripts/run.py new-preflight-C1 C1 --probe on
python3 -B scripts/compare.py new-preflight-R1 new-preflight-C1 --require-gas
```

本轮 `lifecycle_suite.py` 先验证六个已完成探针开/关预检，再运行3块、用保存的extension_gate判断是否扩至5；`copy_suite.py`必须在生命周期阶段完成后执行，另跑Fresh/Copy五块。套件的原标签已有outcome，会保留；不重复启动同标签。分析脚本固定本轮26个进程，新复验不能静默并入。

保持以下保护：MemoryMax2GiB、RSS软1536MiB，TasksMax256/线程软220，Go45秒/进程60秒，MemAvailable最低8GiB、SwapUsed最多1GiB。每进程硬编码一次buyNow；新建Fresh最多3个init+根和6个child=10实例，R0只建3个Instance保留历史。守卫/固定OS owner/显式scope清理保留，不用全局锁。

run.py遇失败写STOP.json，后续拒绝运行；不可删STOP绕过风险。已有.log但无outcome时先读state.json、查看相同unit及PID，确认现场后处理，禁止重复启动。每进程原始日志、events、receipt、resource、命令和outcome即时落盘，PROGRESS记录可恢复位置。

停止单个测试用state记录的具体unit：`systemctl --user stop step23-<label>`。不影响其他历史失败unit或节点，不做全局kill。

回滚：停止本轮unit、返回原工作区即可。生产VM、Gas规则和旧Step21E/22未应用patch，无需反向改生产文件。原分支/结果保留，不自动删除worktree，不推送远程。
