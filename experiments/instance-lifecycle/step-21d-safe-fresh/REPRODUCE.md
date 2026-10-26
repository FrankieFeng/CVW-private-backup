# 本地复现和恢复

本轮构建和执行位于独立worktree：`/home/frankie/mygitprojects/.worktrees/cvw-step21d/experiments/instance-lifecycle/step-21d-safe-fresh`。对应分支experiment/step21d-safe-fresh；父620650d，不包含Step21C整分支合并。

本目录source/vm是已提交的实验module，go.mod/go.work指向本机原21C worktree的固定缓存依赖。`audit/source-inputs.json`标出复制来源，`audit/final-source-manifest.json`固定最终Go源码hash，source.patch相对21C。依赖关键源见audit/dependencies，库/Go/binary/linkage见environment与audit/environment-commands.json。跨机器移植需要重新审计路径、依赖hash和版本，不能默认移植后仍是本轮环境。

只读恢复：

```bash
cat PROGRESS.md
cat verification.json
python3 -B scripts/analyze.py
```

原实际构建命令保存在audit/build-12-command.json。原测试命令均为raw_logs/*-command.json，执行binary前有systemd/cgroup及软限。不要把整包go test当复现命令，包中保留的原池代码不是当前新安全入口；只登记了TestStep21D*入口，旧21C准备入口仍Skip。

本地构建（不会运行guest）：必要时`python3 -B scripts/restore_native.py`只恢复/核对Git忽略的6.0.1 so，然后`python3 -B scripts/build.py <一个新的构建标签>`。binary和native库不提交；packaged头文件和占位Go文件提交。不要运行prepare.py覆盖最终源码：它只记录最初复制流程，不包含后续scope修正，且已有module会拒绝执行。

全部23个已有运行标签和final_suite均已结束，不需要重复执行。final_suite可恢复跳过已有通过结果，遇已有失败或不完整log会停止；它不是新的100次许可。新运行要先评审相应安全门、定义新目录/标签和预算，保留旧结果。

当前source/脚本没有主动修改系统代理、Clash、WSL或VSCode配置。Git提交只归档本目录，未push。主工作区同名目录如为结果镜像，编译/执行仍以独立worktree及记录的绝对路径为准。
