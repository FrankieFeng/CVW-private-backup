# Step24B 可恢复执行进度

**当前状态：所有登记动态实验与离线报告已完成，146测试进程/277配对语义通过，无STOP；不再扩大运行。下文保留历史检查点。Git与IDE镜像收尾也已完成，见末尾记录。**

2026-10-27 Asia/Shanghai。分支experiment/step24b-copy-invoke，独立工作区/home/frankie/mygitprojects/.worktrees/cvw-step24b，父Step23 ba57368；Step22基准394d291。主CVW脏文件及21/22/23原始目录不修改，不push。

阶段1进行中：已定位提交、建立工作区、读取22/23 README。尚未构建或执行新guest进程。
下一条安全操作：审计Step22代码、运行脚本、计时及线程增长，决定安全配对批结构。目标3独立批、每批30–50对；若资源线程持续累积，停止扩大并按实际完成量报告，不解除守卫。
限定：仅A0 Fresh/A1静态Memory Copy；单owner、同生命周期、缓存Module准备单列，无原池并发，无人为100ms sleep，无A/PB等新优化。Table身份/异常仍not_tested。
恢复：先读本文件及state/outcome/日志、检查unit，不重复失败/未完成进程。

阶段1审计完成：22原主实验三合约完整Invoke CI跨零；平衡补充为6对/合约探索数据；buyNow第三批反向主要在callee WASI/import。Store内每个WASI带来线程累积，禁止增加单进程预算。采用预登记多进程小块聚合，每进程最多2对，同Model、同初始状态。首次文件准备因忽略的native目录不存在中断，无guest运行；已创建目录并恢复同hash库，build1构建中。

发现22单合约只在A0 Store执行真实init，导致两组Store历史不对称；E24在两组分别真实init并核对相同账本，测量前完成。Module准备顺序平衡，交易TxID/tokenId固定；Invoke/Copy/Gas/guard不改。方案完整见PLAN.md。

首次源码复制后的native恢复目录缺失属于准备错误，尚无guest启动；补齐原始Go dummy与同hash so后build1已提交构建命令，原失败没有被写成功能样本。源码/计时不对称修正及分级计划已经先落盘。

启动 preflight-compute，unit=step24b-preflight-compute，pairs=1；命令已保存。

结束 preflight-compute：passed=True，reason=exited，peak_threads=74，RSS_KiB=374536，PID/cgroup结束=True。

启动 preflight-fact，unit=step24b-preflight-fact，pairs=1；命令已保存。

结束 preflight-fact：passed=True，reason=exited，peak_threads=74，RSS_KiB=398660，PID/cgroup结束=True。

启动 preflight-erc721，unit=step24b-preflight-erc721，pairs=1；命令已保存。

结束 preflight-erc721：passed=True，reason=exited，peak_threads=74，RSS_KiB=413288，PID/cgroup结束=True。

启动 compute-b1-p00，unit=step24b-compute-b1-p00，pairs=2；命令已保存。

结束 compute-b1-p00：passed=True，reason=exited，peak_threads=108，RSS_KiB=372988，PID/cgroup结束=True。

启动 fact-b1-p00，unit=step24b-fact-b1-p00，pairs=2；命令已保存。

结束 fact-b1-p00：passed=True，reason=exited，peak_threads=108，RSS_KiB=403004，PID/cgroup结束=True。

启动 erc721-b1-p00，unit=step24b-erc721-b1-p00，pairs=2；命令已保存。

结束 erc721-b1-p00：passed=True，reason=exited，peak_threads=108，RSS_KiB=402700，PID/cgroup结束=True。

启动 fact-b1-p01，unit=step24b-fact-b1-p01，pairs=2；命令已保存。

结束 fact-b1-p01：passed=True，reason=exited，peak_threads=108，RSS_KiB=408792，PID/cgroup结束=True。

启动 erc721-b1-p01，unit=step24b-erc721-b1-p01，pairs=2；命令已保存。

结束 erc721-b1-p01：passed=True，reason=exited，peak_threads=108，RSS_KiB=421100，PID/cgroup结束=True。

启动 compute-b1-p01，unit=step24b-compute-b1-p01，pairs=2；命令已保存。

结束 compute-b1-p01：passed=True，reason=exited，peak_threads=108，RSS_KiB=385844，PID/cgroup结束=True。

启动 erc721-b1-p02，unit=step24b-erc721-b1-p02，pairs=2；命令已保存。

结束 erc721-b1-p02：passed=True，reason=exited，peak_threads=108，RSS_KiB=405880，PID/cgroup结束=True。

启动 compute-b1-p02，unit=step24b-compute-b1-p02，pairs=2；命令已保存。

结束 compute-b1-p02：passed=True，reason=exited，peak_threads=108，RSS_KiB=376260，PID/cgroup结束=True。

启动 fact-b1-p02，unit=step24b-fact-b1-p02，pairs=2；命令已保存。

结束 fact-b1-p02：passed=True，reason=exited，peak_threads=108，RSS_KiB=395184，PID/cgroup结束=True。

启动 compute-b1-p03，unit=step24b-compute-b1-p03，pairs=2；命令已保存。

结束 compute-b1-p03：passed=True，reason=exited，peak_threads=108，RSS_KiB=384860，PID/cgroup结束=True。

启动 fact-b1-p03，unit=step24b-fact-b1-p03，pairs=2；命令已保存。

结束 fact-b1-p03：passed=True，reason=exited，peak_threads=108，RSS_KiB=413032，PID/cgroup结束=True。

启动 erc721-b1-p03，unit=step24b-erc721-b1-p03，pairs=2；命令已保存。

结束 erc721-b1-p03：passed=True，reason=exited，peak_threads=108，RSS_KiB=432452，PID/cgroup结束=True。

启动 fact-b1-p04，unit=step24b-fact-b1-p04，pairs=2；命令已保存。

结束 fact-b1-p04：passed=True，reason=exited，peak_threads=108，RSS_KiB=406708，PID/cgroup结束=True。

启动 erc721-b1-p04，unit=step24b-erc721-b1-p04，pairs=2；命令已保存。

结束 erc721-b1-p04：passed=True，reason=exited，peak_threads=108，RSS_KiB=429812，PID/cgroup结束=True。

启动 compute-b1-p04，unit=step24b-compute-b1-p04，pairs=2；命令已保存。

结束 compute-b1-p04：passed=True，reason=exited，peak_threads=109，RSS_KiB=376832，PID/cgroup结束=True。

启动 erc721-b1-p05，unit=step24b-erc721-b1-p05，pairs=2；命令已保存。

结束 erc721-b1-p05：passed=True，reason=exited，peak_threads=108，RSS_KiB=424536，PID/cgroup结束=True。

启动 compute-b1-p05，unit=step24b-compute-b1-p05，pairs=2；命令已保存。

结束 compute-b1-p05：passed=True，reason=exited，peak_threads=108，RSS_KiB=394960，PID/cgroup结束=True。

启动 fact-b1-p05，unit=step24b-fact-b1-p05，pairs=2；命令已保存。

结束 fact-b1-p05：passed=True，reason=exited，peak_threads=108，RSS_KiB=411392，PID/cgroup结束=True。

启动 compute-b1-p06，unit=step24b-compute-b1-p06，pairs=2；命令已保存。

结束 compute-b1-p06：passed=True，reason=exited，peak_threads=108，RSS_KiB=383176，PID/cgroup结束=True。

启动 fact-b1-p06，unit=step24b-fact-b1-p06，pairs=2；命令已保存。

结束 fact-b1-p06：passed=True，reason=exited，peak_threads=108，RSS_KiB=403992，PID/cgroup结束=True。

启动 erc721-b1-p06，unit=step24b-erc721-b1-p06，pairs=2；命令已保存。

结束 erc721-b1-p06：passed=True，reason=exited，peak_threads=108，RSS_KiB=431716，PID/cgroup结束=True。

启动 fact-b1-p07，unit=step24b-fact-b1-p07，pairs=2；命令已保存。

结束 fact-b1-p07：passed=True，reason=exited，peak_threads=108，RSS_KiB=407000，PID/cgroup结束=True。

启动 erc721-b1-p07，unit=step24b-erc721-b1-p07，pairs=2；命令已保存。

结束 erc721-b1-p07：passed=True，reason=exited，peak_threads=108，RSS_KiB=425156，PID/cgroup结束=True。

启动 compute-b1-p07，unit=step24b-compute-b1-p07，pairs=2；命令已保存。

结束 compute-b1-p07：passed=True，reason=exited，peak_threads=108，RSS_KiB=394136，PID/cgroup结束=True。

启动 erc721-b1-p08，unit=step24b-erc721-b1-p08，pairs=2；命令已保存。

结束 erc721-b1-p08：passed=True，reason=exited，peak_threads=108，RSS_KiB=428368，PID/cgroup结束=True。

启动 compute-b1-p08，unit=step24b-compute-b1-p08，pairs=2；命令已保存。

结束 compute-b1-p08：passed=True，reason=exited，peak_threads=108，RSS_KiB=384076，PID/cgroup结束=True。

启动 fact-b1-p08，unit=step24b-fact-b1-p08，pairs=2；命令已保存。

结束 fact-b1-p08：passed=True，reason=exited，peak_threads=108，RSS_KiB=399360，PID/cgroup结束=True。

启动 compute-b1-p09，unit=step24b-compute-b1-p09，pairs=2；命令已保存。

结束 compute-b1-p09：passed=True，reason=exited，peak_threads=108，RSS_KiB=377712，PID/cgroup结束=True。

启动 fact-b1-p09，unit=step24b-fact-b1-p09，pairs=2；命令已保存。

结束 fact-b1-p09：passed=True，reason=exited，peak_threads=108，RSS_KiB=412388，PID/cgroup结束=True。

启动 erc721-b1-p09，unit=step24b-erc721-b1-p09，pairs=2；命令已保存。

结束 erc721-b1-p09：passed=True，reason=exited，peak_threads=108，RSS_KiB=429068，PID/cgroup结束=True。

启动 fact-b1-p10，unit=step24b-fact-b1-p10，pairs=2；命令已保存。

结束 fact-b1-p10：passed=True，reason=exited，peak_threads=108，RSS_KiB=395788，PID/cgroup结束=True。

启动 erc721-b1-p10，unit=step24b-erc721-b1-p10，pairs=2；命令已保存。

结束 erc721-b1-p10：passed=True，reason=exited，peak_threads=108，RSS_KiB=415144，PID/cgroup结束=True。

启动 compute-b1-p10，unit=step24b-compute-b1-p10，pairs=2；命令已保存。

结束 compute-b1-p10：passed=True，reason=exited，peak_threads=108，RSS_KiB=382352，PID/cgroup结束=True。

启动 erc721-b1-p11，unit=step24b-erc721-b1-p11，pairs=2；命令已保存。

结束 erc721-b1-p11：passed=True，reason=exited，peak_threads=109，RSS_KiB=428652，PID/cgroup结束=True。

启动 compute-b1-p11，unit=step24b-compute-b1-p11，pairs=2；命令已保存。

结束 compute-b1-p11：passed=True，reason=exited，peak_threads=108，RSS_KiB=385396，PID/cgroup结束=True。

启动 fact-b1-p11，unit=step24b-fact-b1-p11，pairs=2；命令已保存。

结束 fact-b1-p11：passed=True，reason=exited，peak_threads=108，RSS_KiB=389764，PID/cgroup结束=True。

启动 compute-b1-p12，unit=step24b-compute-b1-p12，pairs=2；命令已保存。

结束 compute-b1-p12：passed=True，reason=exited，peak_threads=108，RSS_KiB=386160，PID/cgroup结束=True。

启动 fact-b1-p12，unit=step24b-fact-b1-p12，pairs=2；命令已保存。

结束 fact-b1-p12：passed=True，reason=exited，peak_threads=108，RSS_KiB=409540，PID/cgroup结束=True。

启动 erc721-b1-p12，unit=step24b-erc721-b1-p12，pairs=2；命令已保存。

结束 erc721-b1-p12：passed=True，reason=exited，peak_threads=108，RSS_KiB=410484，PID/cgroup结束=True。

启动 fact-b1-p13，unit=step24b-fact-b1-p13，pairs=2；命令已保存。

结束 fact-b1-p13：passed=True，reason=exited，peak_threads=108，RSS_KiB=404096，PID/cgroup结束=True。

启动 erc721-b1-p13，unit=step24b-erc721-b1-p13，pairs=2；命令已保存。

结束 erc721-b1-p13：passed=True，reason=exited，peak_threads=108，RSS_KiB=420208，PID/cgroup结束=True。

启动 compute-b1-p13，unit=step24b-compute-b1-p13，pairs=2；命令已保存。

结束 compute-b1-p13：passed=True，reason=exited，peak_threads=108，RSS_KiB=389648，PID/cgroup结束=True。

启动 erc721-b1-p14，unit=step24b-erc721-b1-p14，pairs=2；命令已保存。

结束 erc721-b1-p14：passed=True，reason=exited，peak_threads=108，RSS_KiB=428988，PID/cgroup结束=True。

启动 compute-b1-p14，unit=step24b-compute-b1-p14，pairs=2；命令已保存。

结束 compute-b1-p14：passed=True，reason=exited，peak_threads=108，RSS_KiB=373528，PID/cgroup结束=True。

启动 fact-b1-p14，unit=step24b-fact-b1-p14，pairs=2；命令已保存。

结束 fact-b1-p14：passed=True，reason=exited，peak_threads=108，RSS_KiB=413832，PID/cgroup结束=True。

正式批1完成：每合约15进程×2对，逐对语义/真实init一致，资源包络及进程终结通过；未依据耗时筛选样本。

启动 fact-b2-p00，unit=step24b-fact-b2-p00，pairs=2；命令已保存。

结束 fact-b2-p00：passed=True，reason=exited，peak_threads=108，RSS_KiB=401548，PID/cgroup结束=True。

启动 erc721-b2-p00，unit=step24b-erc721-b2-p00，pairs=2；命令已保存。

结束 erc721-b2-p00：passed=True，reason=exited，peak_threads=108，RSS_KiB=428160，PID/cgroup结束=True。

启动 compute-b2-p00，unit=step24b-compute-b2-p00，pairs=2；命令已保存。

结束 compute-b2-p00：passed=True，reason=exited，peak_threads=108，RSS_KiB=385884，PID/cgroup结束=True。

启动 erc721-b2-p01，unit=step24b-erc721-b2-p01，pairs=2；命令已保存。

结束 erc721-b2-p01：passed=True，reason=exited，peak_threads=109，RSS_KiB=425296，PID/cgroup结束=True。

启动 compute-b2-p01，unit=step24b-compute-b2-p01，pairs=2；命令已保存。

结束 compute-b2-p01：passed=True，reason=exited，peak_threads=108，RSS_KiB=374600，PID/cgroup结束=True。

启动 fact-b2-p01，unit=step24b-fact-b2-p01，pairs=2；命令已保存。

结束 fact-b2-p01：passed=True，reason=exited，peak_threads=108，RSS_KiB=403856，PID/cgroup结束=True。

启动 compute-b2-p02，unit=step24b-compute-b2-p02，pairs=2；命令已保存。

结束 compute-b2-p02：passed=True，reason=exited，peak_threads=108，RSS_KiB=376608，PID/cgroup结束=True。

启动 fact-b2-p02，unit=step24b-fact-b2-p02，pairs=2；命令已保存。

结束 fact-b2-p02：passed=True，reason=exited，peak_threads=108，RSS_KiB=415336，PID/cgroup结束=True。

启动 erc721-b2-p02，unit=step24b-erc721-b2-p02，pairs=2；命令已保存。

结束 erc721-b2-p02：passed=True，reason=exited，peak_threads=109，RSS_KiB=425436，PID/cgroup结束=True。

启动 fact-b2-p03，unit=step24b-fact-b2-p03，pairs=2；命令已保存。

结束 fact-b2-p03：passed=True，reason=exited，peak_threads=108，RSS_KiB=401864，PID/cgroup结束=True。

启动 erc721-b2-p03，unit=step24b-erc721-b2-p03，pairs=2；命令已保存。

结束 erc721-b2-p03：passed=True，reason=exited，peak_threads=108，RSS_KiB=423676，PID/cgroup结束=True。

启动 compute-b2-p03，unit=step24b-compute-b2-p03，pairs=2；命令已保存。

结束 compute-b2-p03：passed=True，reason=exited，peak_threads=108，RSS_KiB=372304，PID/cgroup结束=True。

启动 erc721-b2-p04，unit=step24b-erc721-b2-p04，pairs=2；命令已保存。

结束 erc721-b2-p04：passed=True，reason=exited，peak_threads=108，RSS_KiB=393760，PID/cgroup结束=True。

启动 compute-b2-p04，unit=step24b-compute-b2-p04，pairs=2；命令已保存。

结束 compute-b2-p04：passed=True，reason=exited，peak_threads=108，RSS_KiB=379580，PID/cgroup结束=True。

启动 fact-b2-p04，unit=step24b-fact-b2-p04，pairs=2；命令已保存。

结束 fact-b2-p04：passed=True，reason=exited，peak_threads=108，RSS_KiB=408324，PID/cgroup结束=True。

启动 compute-b2-p05，unit=step24b-compute-b2-p05，pairs=2；命令已保存。

结束 compute-b2-p05：passed=True，reason=exited，peak_threads=108，RSS_KiB=382476，PID/cgroup结束=True。

启动 fact-b2-p05，unit=step24b-fact-b2-p05，pairs=2；命令已保存。

结束 fact-b2-p05：passed=True，reason=exited，peak_threads=108，RSS_KiB=413864，PID/cgroup结束=True。

启动 erc721-b2-p05，unit=step24b-erc721-b2-p05，pairs=2；命令已保存。

结束 erc721-b2-p05：passed=True，reason=exited，peak_threads=108，RSS_KiB=417292，PID/cgroup结束=True。

启动 fact-b2-p06，unit=step24b-fact-b2-p06，pairs=2；命令已保存。

结束 fact-b2-p06：passed=True，reason=exited，peak_threads=109，RSS_KiB=404680，PID/cgroup结束=True。

启动 erc721-b2-p06，unit=step24b-erc721-b2-p06，pairs=2；命令已保存。

结束 erc721-b2-p06：passed=True，reason=exited，peak_threads=108，RSS_KiB=419020，PID/cgroup结束=True。

启动 compute-b2-p06，unit=step24b-compute-b2-p06，pairs=2；命令已保存。

结束 compute-b2-p06：passed=True，reason=exited，peak_threads=108，RSS_KiB=383728，PID/cgroup结束=True。

启动 erc721-b2-p07，unit=step24b-erc721-b2-p07，pairs=2；命令已保存。

结束 erc721-b2-p07：passed=True，reason=exited，peak_threads=108，RSS_KiB=428504，PID/cgroup结束=True。

启动 compute-b2-p07，unit=step24b-compute-b2-p07，pairs=2；命令已保存。

结束 compute-b2-p07：passed=True，reason=exited，peak_threads=108，RSS_KiB=377580，PID/cgroup结束=True。

启动 fact-b2-p07，unit=step24b-fact-b2-p07，pairs=2；命令已保存。

结束 fact-b2-p07：passed=True，reason=exited，peak_threads=108，RSS_KiB=406312，PID/cgroup结束=True。

启动 compute-b2-p08，unit=step24b-compute-b2-p08，pairs=2；命令已保存。

结束 compute-b2-p08：passed=True，reason=exited，peak_threads=108，RSS_KiB=382008，PID/cgroup结束=True。

启动 fact-b2-p08，unit=step24b-fact-b2-p08，pairs=2；命令已保存。

结束 fact-b2-p08：passed=True，reason=exited，peak_threads=108，RSS_KiB=403184，PID/cgroup结束=True。

启动 erc721-b2-p08，unit=step24b-erc721-b2-p08，pairs=2；命令已保存。

结束 erc721-b2-p08：passed=True，reason=exited，peak_threads=108，RSS_KiB=414800，PID/cgroup结束=True。

启动 fact-b2-p09，unit=step24b-fact-b2-p09，pairs=2；命令已保存。

结束 fact-b2-p09：passed=True，reason=exited，peak_threads=108，RSS_KiB=415088，PID/cgroup结束=True。

启动 erc721-b2-p09，unit=step24b-erc721-b2-p09，pairs=2；命令已保存。

结束 erc721-b2-p09：passed=True，reason=exited，peak_threads=108，RSS_KiB=417316，PID/cgroup结束=True。

启动 compute-b2-p09，unit=step24b-compute-b2-p09，pairs=2；命令已保存。

结束 compute-b2-p09：passed=True，reason=exited，peak_threads=108，RSS_KiB=374228，PID/cgroup结束=True。

启动 erc721-b2-p10，unit=step24b-erc721-b2-p10，pairs=2；命令已保存。

结束 erc721-b2-p10：passed=True，reason=exited，peak_threads=108，RSS_KiB=419520，PID/cgroup结束=True。

启动 compute-b2-p10，unit=step24b-compute-b2-p10，pairs=2；命令已保存。

结束 compute-b2-p10：passed=True，reason=exited，peak_threads=108，RSS_KiB=373912，PID/cgroup结束=True。

启动 fact-b2-p10，unit=step24b-fact-b2-p10，pairs=2；命令已保存。

结束 fact-b2-p10：passed=True，reason=exited，peak_threads=108，RSS_KiB=409540，PID/cgroup结束=True。

启动 compute-b2-p11，unit=step24b-compute-b2-p11，pairs=2；命令已保存。

结束 compute-b2-p11：passed=True，reason=exited，peak_threads=108，RSS_KiB=384224，PID/cgroup结束=True。

启动 fact-b2-p11，unit=step24b-fact-b2-p11，pairs=2；命令已保存。

结束 fact-b2-p11：passed=True，reason=exited，peak_threads=108，RSS_KiB=402916，PID/cgroup结束=True。

启动 erc721-b2-p11，unit=step24b-erc721-b2-p11，pairs=2；命令已保存。

结束 erc721-b2-p11：passed=True，reason=exited，peak_threads=108，RSS_KiB=421340，PID/cgroup结束=True。

启动 fact-b2-p12，unit=step24b-fact-b2-p12，pairs=2；命令已保存。

结束 fact-b2-p12：passed=True，reason=exited，peak_threads=108，RSS_KiB=410444，PID/cgroup结束=True。

启动 erc721-b2-p12，unit=step24b-erc721-b2-p12，pairs=2；命令已保存。

结束 erc721-b2-p12：passed=True，reason=exited，peak_threads=108，RSS_KiB=404496，PID/cgroup结束=True。

启动 compute-b2-p12，unit=step24b-compute-b2-p12，pairs=2；命令已保存。

结束 compute-b2-p12：passed=True，reason=exited，peak_threads=108，RSS_KiB=389148，PID/cgroup结束=True。

启动 erc721-b2-p13，unit=step24b-erc721-b2-p13，pairs=2；命令已保存。

结束 erc721-b2-p13：passed=True，reason=exited，peak_threads=108，RSS_KiB=436228，PID/cgroup结束=True。

启动 compute-b2-p13，unit=step24b-compute-b2-p13，pairs=2；命令已保存。

结束 compute-b2-p13：passed=True，reason=exited，peak_threads=108，RSS_KiB=389040，PID/cgroup结束=True。

启动 fact-b2-p13，unit=step24b-fact-b2-p13，pairs=2；命令已保存。

结束 fact-b2-p13：passed=True，reason=exited，peak_threads=108，RSS_KiB=397380，PID/cgroup结束=True。

启动 compute-b2-p14，unit=step24b-compute-b2-p14，pairs=2；命令已保存。

结束 compute-b2-p14：passed=True，reason=exited，peak_threads=108，RSS_KiB=375384，PID/cgroup结束=True。

启动 fact-b2-p14，unit=step24b-fact-b2-p14，pairs=2；命令已保存。

结束 fact-b2-p14：passed=True，reason=exited，peak_threads=109，RSS_KiB=418084，PID/cgroup结束=True。

启动 erc721-b2-p14，unit=step24b-erc721-b2-p14，pairs=2；命令已保存。

结束 erc721-b2-p14：passed=True，reason=exited，peak_threads=108，RSS_KiB=429972，PID/cgroup结束=True。

正式批2完成：每合约15进程×2对，逐对语义/真实init一致，资源包络及进程终结通过；未依据耗时筛选样本。

启动 erc721-b3-p00，unit=step24b-erc721-b3-p00，pairs=2；命令已保存。

结束 erc721-b3-p00：passed=True，reason=exited，peak_threads=108，RSS_KiB=418368，PID/cgroup结束=True。

启动 compute-b3-p00，unit=step24b-compute-b3-p00，pairs=2；命令已保存。

结束 compute-b3-p00：passed=True，reason=exited，peak_threads=108，RSS_KiB=377896，PID/cgroup结束=True。

启动 fact-b3-p00，unit=step24b-fact-b3-p00，pairs=2；命令已保存。

结束 fact-b3-p00：passed=True，reason=exited，peak_threads=108，RSS_KiB=407340，PID/cgroup结束=True。

启动 compute-b3-p01，unit=step24b-compute-b3-p01，pairs=2；命令已保存。

结束 compute-b3-p01：passed=True，reason=exited，peak_threads=108，RSS_KiB=384116，PID/cgroup结束=True。

启动 fact-b3-p01，unit=step24b-fact-b3-p01，pairs=2；命令已保存。

结束 fact-b3-p01：passed=True，reason=exited，peak_threads=108，RSS_KiB=410920，PID/cgroup结束=True。

启动 erc721-b3-p01，unit=step24b-erc721-b3-p01，pairs=2；命令已保存。

结束 erc721-b3-p01：passed=True，reason=exited，peak_threads=108，RSS_KiB=432464，PID/cgroup结束=True。

启动 fact-b3-p02，unit=step24b-fact-b3-p02，pairs=2；命令已保存。

结束 fact-b3-p02：passed=True，reason=exited，peak_threads=108，RSS_KiB=416212，PID/cgroup结束=True。

启动 erc721-b3-p02，unit=step24b-erc721-b3-p02，pairs=2；命令已保存。

结束 erc721-b3-p02：passed=True，reason=exited，peak_threads=108，RSS_KiB=418000，PID/cgroup结束=True。

启动 compute-b3-p02，unit=step24b-compute-b3-p02，pairs=2；命令已保存。

结束 compute-b3-p02：passed=True，reason=exited，peak_threads=108，RSS_KiB=382300，PID/cgroup结束=True。

启动 erc721-b3-p03，unit=step24b-erc721-b3-p03，pairs=2；命令已保存。

结束 erc721-b3-p03：passed=True，reason=exited，peak_threads=108，RSS_KiB=432964，PID/cgroup结束=True。

启动 compute-b3-p03，unit=step24b-compute-b3-p03，pairs=2；命令已保存。

结束 compute-b3-p03：passed=True，reason=exited，peak_threads=108，RSS_KiB=389940，PID/cgroup结束=True。

启动 fact-b3-p03，unit=step24b-fact-b3-p03，pairs=2；命令已保存。

结束 fact-b3-p03：passed=True，reason=exited，peak_threads=108，RSS_KiB=407960，PID/cgroup结束=True。

启动 compute-b3-p04，unit=step24b-compute-b3-p04，pairs=2；命令已保存。

结束 compute-b3-p04：passed=True，reason=exited，peak_threads=108，RSS_KiB=378044，PID/cgroup结束=True。

启动 fact-b3-p04，unit=step24b-fact-b3-p04，pairs=2；命令已保存。

结束 fact-b3-p04：passed=True，reason=exited，peak_threads=108，RSS_KiB=407948，PID/cgroup结束=True。

启动 erc721-b3-p04，unit=step24b-erc721-b3-p04，pairs=2；命令已保存。

结束 erc721-b3-p04：passed=True，reason=exited，peak_threads=108，RSS_KiB=410500，PID/cgroup结束=True。

启动 fact-b3-p05，unit=step24b-fact-b3-p05，pairs=2；命令已保存。

结束 fact-b3-p05：passed=True，reason=exited，peak_threads=108，RSS_KiB=420112，PID/cgroup结束=True。

启动 erc721-b3-p05，unit=step24b-erc721-b3-p05，pairs=2；命令已保存。

结束 erc721-b3-p05：passed=True，reason=exited，peak_threads=108，RSS_KiB=405092，PID/cgroup结束=True。

启动 compute-b3-p05，unit=step24b-compute-b3-p05，pairs=2；命令已保存。

结束 compute-b3-p05：passed=True，reason=exited，peak_threads=108，RSS_KiB=368444，PID/cgroup结束=True。

启动 erc721-b3-p06，unit=step24b-erc721-b3-p06，pairs=2；命令已保存。

结束 erc721-b3-p06：passed=True，reason=exited，peak_threads=109，RSS_KiB=416560，PID/cgroup结束=True。

启动 compute-b3-p06，unit=step24b-compute-b3-p06，pairs=2；命令已保存。

构建build1通过，binary e88abe03256055eb6463eda6aeba5179c39975194f7cc0e07d7dab50568ba147。预检三合约各1对均通过；formal先导各2对均通过，全部退出/登记0、线程108。计划运行3×15进程/合约多进程聚合，进程内预算始终2，未提高guard。suite离线setup检查首次遇protobuf省略零Gas字段的KeyError，保留audit/formal-driver-attempt1.log，修正为默认0后仅复算/继续未完成label，没有重跑已有guest。

结束 compute-b3-p06：passed=True，reason=exited，peak_threads=108，RSS_KiB=367708，PID/cgroup结束=True。

启动 fact-b3-p06，unit=step24b-fact-b3-p06，pairs=2；命令已保存。

结束 fact-b3-p06：passed=True，reason=exited，peak_threads=108，RSS_KiB=412512，PID/cgroup结束=True。

启动 compute-b3-p07，unit=step24b-compute-b3-p07，pairs=2；命令已保存。

结束 compute-b3-p07：passed=True，reason=exited，peak_threads=108，RSS_KiB=382260，PID/cgroup结束=True。

启动 fact-b3-p07，unit=step24b-fact-b3-p07，pairs=2；命令已保存。

结束 fact-b3-p07：passed=True，reason=exited，peak_threads=108，RSS_KiB=418900，PID/cgroup结束=True。

启动 erc721-b3-p07，unit=step24b-erc721-b3-p07，pairs=2；命令已保存。

结束 erc721-b3-p07：passed=True，reason=exited，peak_threads=108，RSS_KiB=432628，PID/cgroup结束=True。

启动 fact-b3-p08，unit=step24b-fact-b3-p08，pairs=2；命令已保存。

结束 fact-b3-p08：passed=True，reason=exited，peak_threads=108，RSS_KiB=388576，PID/cgroup结束=True。

启动 erc721-b3-p08，unit=step24b-erc721-b3-p08，pairs=2；命令已保存。

结束 erc721-b3-p08：passed=True，reason=exited，peak_threads=108，RSS_KiB=421736，PID/cgroup结束=True。

启动 compute-b3-p08，unit=step24b-compute-b3-p08，pairs=2；命令已保存。

结束 compute-b3-p08：passed=True，reason=exited，peak_threads=108，RSS_KiB=374332，PID/cgroup结束=True。

启动 erc721-b3-p09，unit=step24b-erc721-b3-p09，pairs=2；命令已保存。

结束 erc721-b3-p09：passed=True，reason=exited，peak_threads=108，RSS_KiB=419116，PID/cgroup结束=True。

启动 compute-b3-p09，unit=step24b-compute-b3-p09，pairs=2；命令已保存。

结束 compute-b3-p09：passed=True，reason=exited，peak_threads=108，RSS_KiB=382480，PID/cgroup结束=True。

启动 fact-b3-p09，unit=step24b-fact-b3-p09，pairs=2；命令已保存。

结束 fact-b3-p09：passed=True，reason=exited，peak_threads=108，RSS_KiB=404640，PID/cgroup结束=True。

启动 compute-b3-p10，unit=step24b-compute-b3-p10，pairs=2；命令已保存。

结束 compute-b3-p10：passed=True，reason=exited，peak_threads=108，RSS_KiB=380440，PID/cgroup结束=True。

启动 fact-b3-p10，unit=step24b-fact-b3-p10，pairs=2；命令已保存。

结束 fact-b3-p10：passed=True，reason=exited，peak_threads=108，RSS_KiB=404844，PID/cgroup结束=True。

启动 erc721-b3-p10，unit=step24b-erc721-b3-p10，pairs=2；命令已保存。

结束 erc721-b3-p10：passed=True，reason=exited，peak_threads=108，RSS_KiB=428364，PID/cgroup结束=True。

启动 fact-b3-p11，unit=step24b-fact-b3-p11，pairs=2；命令已保存。

结束 fact-b3-p11：passed=True，reason=exited，peak_threads=108，RSS_KiB=393800，PID/cgroup结束=True。

启动 erc721-b3-p11，unit=step24b-erc721-b3-p11，pairs=2；命令已保存。

结束 erc721-b3-p11：passed=True，reason=exited，peak_threads=108，RSS_KiB=399212，PID/cgroup结束=True。

启动 compute-b3-p11，unit=step24b-compute-b3-p11，pairs=2；命令已保存。

结束 compute-b3-p11：passed=True，reason=exited，peak_threads=108，RSS_KiB=382224，PID/cgroup结束=True。

启动 erc721-b3-p12，unit=step24b-erc721-b3-p12，pairs=2；命令已保存。

结束 erc721-b3-p12：passed=True，reason=exited，peak_threads=108，RSS_KiB=421564，PID/cgroup结束=True。

启动 compute-b3-p12，unit=step24b-compute-b3-p12，pairs=2；命令已保存。

结束 compute-b3-p12：passed=True，reason=exited，peak_threads=108，RSS_KiB=382068，PID/cgroup结束=True。

启动 fact-b3-p12，unit=step24b-fact-b3-p12，pairs=2；命令已保存。

结束 fact-b3-p12：passed=True，reason=exited，peak_threads=108，RSS_KiB=407960，PID/cgroup结束=True。

启动 compute-b3-p13，unit=step24b-compute-b3-p13，pairs=2；命令已保存。

结束 compute-b3-p13：passed=True，reason=exited，peak_threads=108，RSS_KiB=374000，PID/cgroup结束=True。

启动 fact-b3-p13，unit=step24b-fact-b3-p13，pairs=2；命令已保存。

结束 fact-b3-p13：passed=True，reason=exited，peak_threads=108，RSS_KiB=410472，PID/cgroup结束=True。

启动 erc721-b3-p13，unit=step24b-erc721-b3-p13，pairs=2；命令已保存。

结束 erc721-b3-p13：passed=True，reason=exited，peak_threads=108，RSS_KiB=420304，PID/cgroup结束=True。

启动 fact-b3-p14，unit=step24b-fact-b3-p14，pairs=2；命令已保存。

结束 fact-b3-p14：passed=True，reason=exited，peak_threads=108，RSS_KiB=414240，PID/cgroup结束=True。

启动 erc721-b3-p14，unit=step24b-erc721-b3-p14，pairs=2；命令已保存。

结束 erc721-b3-p14：passed=True，reason=exited，peak_threads=108，RSS_KiB=429420，PID/cgroup结束=True。

启动 compute-b3-p14，unit=step24b-compute-b3-p14，pairs=2；命令已保存。

结束 compute-b3-p14：passed=True，reason=exited，peak_threads=108，RSS_KiB=371740，PID/cgroup结束=True。

正式批3完成：每合约15进程×2对，逐对语义/真实init一致，资源包络及进程终结通过；未依据耗时筛选样本。

启动 exchange-preflight-b0-A0，unit=step24b-exchange-preflight-b0-A0，pairs=1；命令已保存。

结束 exchange-preflight-b0-A0：passed=True，reason=exited，peak_threads=176，RSS_KiB=776120，PID/cgroup结束=True。

启动 exchange-preflight-b0-A1，unit=step24b-exchange-preflight-b0-A1，pairs=1；命令已保存。

结束 exchange-preflight-b0-A1：passed=True，reason=exited，peak_threads=176，RSS_KiB=779816，PID/cgroup结束=True。

buyNow preflight批0两独立变体各根1+六真实子调用已比较，通过Gas/返回/根读写集/事件/初始最终账本，保持split预算。

启动 exchange-formal-b1-A1，unit=step24b-exchange-formal-b1-A1，pairs=1；命令已保存。

结束 exchange-formal-b1-A1：passed=True，reason=exited，peak_threads=176，RSS_KiB=769688，PID/cgroup结束=True。

启动 exchange-formal-b1-A0，unit=step24b-exchange-formal-b1-A0，pairs=1；命令已保存。

结束 exchange-formal-b1-A0：passed=True，reason=exited，peak_threads=176，RSS_KiB=762380，PID/cgroup结束=True。

buyNow formal批1两独立变体各根1+六真实子调用已比较，通过Gas/返回/根读写集/事件/初始最终账本，保持split预算。

启动 exchange-formal-b2-A0，unit=step24b-exchange-formal-b2-A0，pairs=1；命令已保存。

结束 exchange-formal-b2-A0：passed=True，reason=exited，peak_threads=176，RSS_KiB=780976，PID/cgroup结束=True。

启动 exchange-formal-b2-A1，unit=step24b-exchange-formal-b2-A1，pairs=1；命令已保存。

结束 exchange-formal-b2-A1：passed=True，reason=exited，peak_threads=176，RSS_KiB=767440，PID/cgroup结束=True。

buyNow formal批2两独立变体各根1+六真实子调用已比较，通过Gas/返回/根读写集/事件/初始最终账本，保持split预算。

启动 exchange-formal-b3-A1，unit=step24b-exchange-formal-b3-A1，pairs=1；命令已保存。

结束 exchange-formal-b3-A1：passed=True，reason=exited，peak_threads=176，RSS_KiB=779672，PID/cgroup结束=True。

启动 exchange-formal-b3-A0，unit=step24b-exchange-formal-b3-A0，pairs=1；命令已保存。

结束 exchange-formal-b3-A0：passed=True，reason=exited，peak_threads=176，RSS_KiB=781324，PID/cgroup结束=True。

buyNow formal批3两独立变体各根1+六真实子调用已比较，通过Gas/返回/根读写集/事件/初始最终账本，保持split预算。

## 阶段3完成：正式单合约测量
- 三合约各3批，每批15独立进程×2对=30对，总计各90有效配对。每个单Store预算未扩大，Module每变体每进程仅准备一次、计时外列出。135正式进程＋3预检均正常，后续没有因耗时剔除样本。
- 完整Invoke配对节省Median：compute0.6696525ms [0.467867,1.013870]，fact0.7496765ms [0.654408,0.966715]，ERC721 0.711377ms [0.485127,0.956906]；95%为固定seed层次batch/process bootstrap。
- 已保存TIMING、PAIRED_EFFECTS、PAIRED_SAMPLES、各批/顺序、MODULE_PREPARATION、RESOURCE_SUMMARY。三个合约各批中位数均正，但270对中49反向，保留原始数据。不是长寿命Store或节点结论。

## 阶段4完成：buyNow扩展
- 仅在核心语义/资源门槛通过后执行；split预检1对＋正式3独立对，共8进程，每变体真实init3＋根1＋六子调用，原预算不变。
- 正式完整Invoke节省6.628448、28.385431、2.698496ms，未重复旧正式15.765ms反向；但预检保留-1.351166ms（含S1 hash，不计性能）。六callee准备差分别+2.628764、+11.344312、+0.733838ms；第2批的正向放大不能归因全为Copy。
- BUY_NOW_STAGES/STAGE_EFFECTS/DECOMPOSITION保存逐根/六callee窗口与非重叠阶段分解。旧22第三批原log重算-15.764944ms，六callee WASI/imports=-19.732278ms，证据保留audit/reference-step22。

## 阶段5：交付与安全结论
- 146测试进程全部原退出0，PID/cgroup全部终结，注册表最终0；277配对语义核对通过（含预检），902条真实Invoke记录保留。无STOP、没有放宽guard。峰值763.01MiB/176线程；单合约Store内线程仍累积，未证明长期回收。
- README、RESULTS、CORRECTNESS、AUDIT、PLAN、RUNNING以及所有CSV、源码diff、原始记录与离线脚本已落盘。真实Table身份/动态Globals/异常/OOG/并发/长期Store与节点仍not_tested。
- scripts/analyze.py、buy_stages.py、write_report.py、provenance.py完成；构建与新guest均已结束，不再增加动态实验。下一条安全操作：静态完整性核对、独立分支提交及主CVW新增阅读镜像，不push。

## 离线敏感性与边界补充
- 顺序分层不是继续运行的依据，全部动态测量完成后才计算。fact在A0先45对分层的Median0.141577ms、95%CI[-0.113321,0.487912]跨零；A1先分层约1.053ms。三个合约均明显受顺序影响，因此最终表述限定为预登记平衡顺序总体，不声称任意顺序稳定。
- Copy timer未包含随后Ranges计数循环，但S0→S1/Invoke包含它；保留22观测代码，报告明确。TIMING补链每根返回后的RSS/线程，子调用只引用所属根边界，不伪报每callee瞬时资源。
- 修复恢复脚本同时校验/恢复Git忽略的packaged Go dummy依赖；仅静态恢复相同文件，没有新guest或新构建。

## 交付静态核对完成
- 新增文档/脚本/改动测试入口的空白检查、Python静态编译、本地报告链接检查通过；verification确认146进程/277配对、无STOP。902调用完整TIMING保留，33列以上阶段/准备/资源字段可追溯到原日志。
- 参考22/23/21C工作区仍clean，所有step24b unit已卸载，WSL boot ID未变；未修改代理/WSL/VSCode或生产VM。
- 下一步只提交独立Step24B目录、生成校验manifest及主CVW新目录镜像。不再运行动态实验。后续须先解决长期Store、Table/异常和节点路径，不能以本轮结果直接放行并发节点测试。

## Git与IDE收尾完成
交付提交adcf230已创建；仅新增Step24B目录，1735个Git交付文件已复制到主CVW同名新目录并按manifest核验。后续本收尾记录单独提交。未复制ELF/native库，未覆盖22/23或生产文件，未push。所有登记任务完成；恢复后无待执行guest，后续限制见README/RESULTS与PLAN。
