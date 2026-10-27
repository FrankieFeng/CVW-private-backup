# 复算与恢复

先读PROGRESS.md、state.json、全部outcome和STOP.json；已有label不重跑。STOP存在时仅分析，不能清除或换进程凑数。

```bash
# 仅离线复算（不执行guest）
python3 -B scripts/analyze.py
python3 -B scripts/write_report.py
```

本机复验依赖已有Step21C源码/WASM和本地Go cache，固定Go1.25、同hash Wasmer6.0.1；绝对路径在go.work、manifest、command.json中。重定位时必须显式校验，不能下载新库/重新编业务替代。native/test ELF不入Git；scripts/restore_native.py只从固定本机路径恢复同hash so。packaged/lib的Go dummy也为继承依赖，脚本恢复应保持同一源目录。所有本轮真实构建/运行命令、binary SHA、资源和退出状态已逐进程保存。

scripts/formal_suite.py和buy_suite.py是**本轮已完成/登记的实验驱动**，不是可以随意换label扩大测试的通用许可。每有界进程最多2配对、buyNow单变体单根，禁止提高Go预算或资源guard。若需要新构建，应使用新的输出label，核对native/source/config SHA；当前run.py固定build1 binary，只能在明确登记的新实验中修改，不替换历史binary/数据。

进程启动只有systemd-run对应step24b-<label>，外部限额MemoryMax2G、TasksMax256、Runtime60s、Go45s；软限RSS1536MiB/线程220，单合约另限768MiB/125线程、全机Available8GiB/Swap1GiB。无人工100ms Sleep；监视器25ms采样属于资源观测，不在业务路径等待。

停止具体活跃unit：从state.json取active_unit后`systemctl --user stop <unit>`；不要全局kill或停止其他实验。退出后runner保存原ExecMainStatus/Result，再stop并核对PID/cgroup为空。

统计用Python标准库、10000次层次配对bootstrap，seed240027；先抽批次，再抽process保留其中两对，不额外抽独立pair。Median节省是逐对A0−A1的中位数，不是两组Median相减。P95最近秩。buyNow只有3独立对，CI探索性很强。所有预检/初始化/失败行保留但性能筛选显式只取成功formal目标root。

生产VM未改，无需应用反向patch；22/23目录未变，远程未push。主CVW同名目录最终仅作为Git交付文件阅读镜像，实际执行在独立worktree。
