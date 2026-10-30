# Step-32 可恢复进度（2026-10-30）

全部六重点方法四组正式实验完成。独立分支experiment/step32-all-contracts-acopy-matrix，worktree /home/frankie/mygitprojects/.worktrees/cvw-step32。

- 审计：Step18/22/24B/25/26/27/28/29/30报告及对应产物hash冻结在audit/history-manifest.json。全项目8类Go合约、18个canonical wasm候选；四组矩阵优先六方法，其他独立方法明确未覆盖。
- 构建：Step28同源P0/plain原件及A产物冻结；新A-only使用已有A原WASM关闭Copy。源码仅四组driver及Invoke外scope计数变动。Host build1成功，Go1.25/native6.0.1及Gas版本固定，原命令及SHA保存。
- 预检：6个四组block通过；buyNow空参数与重复token四组真实失败/回滚通过。无mock子调用。
- 正式：3批，每批每方法10区块，180有效block、720正式根调用；buyNow额外720真实子调用。420正式进程，含预检/异常共442进程，全部退出，无STOP/失败/无效样本。每个block即时原日志/回执/outcome/meta落盘。
- 统计：analyze.py/report.py完成，所有Median/Mean/P95、五条直接效应/CI/正向率、三批/顺序分层及四项交互保存；不拼历史样本。交互原式正代表抵消，额外协同为其负数。
- 验证：verify.py核对2528样本行、442原始日志，root配对及Gas/账本/事件、Store scope关闭与owner pending=0、PID/cgroup退出。VERIFICATION.json通过。历史hash及编译Go源码hash未变。
- 资源：峰RSS571.01MiB、host heap105.96MiB、线程177，阈值不变；1016个Module/Store scope与2528个Instance均完成有界关闭。此scope计数不等于native Rc泄漏认证。

运行命令（已完成，不应重复Guest）：
python3 scripts/experiment.py preflight
python3 -u scripts/experiment.py formal > raw_logs/formal-driver.log 2>&1
python3 scripts/analyze.py
python3 scripts/report.py
python3 scripts/verify.py

本轮预检曾运行旧的三组顺序生成方式扩为四组（仅预检）；正式前冻结为每批Williams平衡顺序，实际命令如实记录。正式中仅在140根样本时运行过一次约0.43秒离线统计，潜在扰动未据此剔除任何样本；其余主要统计在正式结束后进行。

下一步：只读RESULTS/README/VERIFICATION；没有需要自动继续的负载。不可扩大Store生命周期/阈值，不启动节点。Table函数身份、一般异常/OOG、原池并发及长寿命回收仍not_tested。原生产工作区未改，仅新增交付镜像目录；未推远程。
