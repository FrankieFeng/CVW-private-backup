# step-20 端到端性能归因：命名记录

按用户要求，将原E20统一命名为“step-20 端到端性能归因”。

- 当前目录：`experiments/instance-lifecycle/step-20-e2e-performance-attribution/`。
- 当前工作树：`.worktrees/cvw-step20`；当前分支：`experiment/step20-e2e-performance-attribution`。
- 原目录名：`e20-e2e-copy-attribution`，原工作树`.worktrees/cvw-e20`，原分支`experiment/e20-e2e-copy-attribution`。这些只作为历史标识保留。
- 后续新实验目录统一`step-N-<英文描述>`，文档名称统一“step-N 中文主题”。

本次只变更命名和路径，没有运行新的性能实验，也不改变计时、样本或数值结论。历史JSONL、节点日志、启动命令JSON和状态记录保持原始字节，因此其中旧E20标识/绝对路径是执行时证据，不能当作当前重跑命令。

原环境与执行器分别保存在environment.at-execution.json、run.at-execution.py；更名前校验单保存在manifest.before-step20-rename.sha256。当前可执行配置的隔离路径已随目录更新，原YAML另保存在本机config-paths-before-rename（不纳入版本提交）。原实验资源停止限制继续适用，不因改名放行重跑。

当前analyze.py只读重算会更新派生CSV中的source_file定位路径，数值字段不变；当前校验单为manifest.sha256。
