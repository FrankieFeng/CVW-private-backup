# 运行与回滚

仅限本机已准备的独立worktree。历史实际每次运行的完整env/systemd/test命令在 `raw_logs/*-command.json`，binary SHA也保存在每份命令中。保留的build1失败日志属于unused import构建问题，未执行guest；build3为探索预检，最终build4正式数据不混用。

```bash
cd /home/frankie/mygitprojects/.worktrees/cvw-step22/experiments/instance-lifecycle/step-22-serial-static-copy
python3 -B scripts/reduce_raw.py
python3 -B scripts/analyze_balanced.py
python3 -B scripts/provenance.py
python3 -B scripts/write_report.py
```

上述命令只分析已有数据，不执行guest。统计脚本使用Python标准库；P95最近秩，CI为固定seed22026026、10000次三批层次配对bootstrap（先抽batch，再在batch抽pair slot）。N很小，CI是探索性估计，P95实质等于样本最大值。

需复验时先确认资源和原artifact存在，不运行已经有outcome的label，不覆盖本轮数据：

```bash
# 不更新依赖；从固定本地Step21C库恢复git忽略的.so，核对SHA
python3 -B scripts/restore_native.py
# 新文件名输出，不覆盖测量用step22.test
python3 -B scripts/build.py replay-build
# binary SHA从audit/replay-build-outcome.json读取，必须明确指定
python3 -B scripts/run.py replay-probe probe --phase probe --binary "$PWD/binaries/replay-build.test" --binary-sha '<new SHA>'
python3 -B scripts/run.py replay-compute compute --pairs 1 --phase preflight --binary "$PWD/binaries/replay-build.test" --binary-sha '<new SHA>'
```

当前原binary仍在本地binaries/step22.test（git忽略）。不重建时省略 `--binary/--binary-sha`，默认强制校验冻结build4 SHA。新binary的补测必须保存在新label并独立分析，不能静默混进本轮标签/统计。

原始3×3主实验由 `scripts/core_suite.py` 和记录的erc721-batch-*命令完成；exchange用 `scripts/exchange_suite.py`，先比较真实预检receipt再每批两个独立进程（顺序A0A1/A1A0/A0A1）。顺序平衡补充在 `scripts/balanced_suite.py`，与主结果分表。不要把套件中的保留label换名后无意启动全套；先单次预检。

依赖：本地Step21C worktree中的root/模块与testdata、Step21D显式所有权代码、Go1.25.0和已有module cache。go.work及manifest保留实际绝对路径。原WASM未重编译，路径/hash在inputs/variants中。路径不存在或hash不同就停止，不能下载另一个版本替代。native .so未入git，可按restore脚本恢复。源码diff相对父提交的Step21D source/vm。

资源不放宽：MemoryMax2GiB，RSS软限1536MiB；TasksMax256/线程软限220；Runtime60秒、Go timeout45秒；全机MemAvailable≥8GiB、SwapUsed≤1GiB；每进程最多3对（实际平衡组2对），exchange单变体单根。STOP.json存在则自动拒绝后续测试。进程失败、超时、健康阈值命中保存日志后停止，不清除STOP继续跑。

停止当前某一测试：使用state.json记录的**具体unit**执行 `systemctl --user stop step22-<label>`。runner正常退出也会stop unit并核对PID已消失。不要停止其他历史实验/节点或使用全局kill命令。

回滚：关闭本轮test unit，回到原工作区；生产VM未应用任何patch，无需反向修改。保留本目录及分支。需要卸载实验代码时只移除独立worktree/分支，先归档原始结果；本轮未自动执行删除或远程push。
