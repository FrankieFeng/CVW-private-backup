# Step-25 可恢复进度

2026-10-27，独立分支experiment/step25-ab-copy-screening，父570b06a。当前动态测试与报告均已完成，主矩阵及原24B参考分开；以下保留历史阶段记录；初始化发现24B Git未跟踪packaged/lib中的Go package占位文件，正从实际原目录恢复，保留hash。

计划：审计→预检→三批配对筛选→复算/PPT。固定OS owner，独立Store+Module、同步fresh及关闭，每进程最多2对、每Store最多init+2正式Instance。不同时把五组放入一个进程增加线程预算；每进程只测一个直接组间对照。
A已恢复padding原型；B1限定历史GetBatchState/PB裁剪补丁，有API限制；Copy沿用22/24B。Step18现存同源plain家族compute为10000大数循环，24B原件100，主矩阵不改既有产物工作量，严禁跨家族配对。
所有阈值沿用24B（单合约RSS768MiB、线程125软限，2GiB/256tasks硬限；45/60s超时；available8GiB/swap1GiB）。任何新失败保留STOP、日志并停止扩大；不修改生产VM或Gas，不做原池并发，不push。
下一步：固定hash/输入，准备诊断入口。中断先读本文件/state/outcome/unit，不重复有效label。

启动 pre-compute-G0-G1，unit=step25-pre-compute-G0-G1，pairs=1；命令已保存。

结束 pre-compute-G0-G1：passed=True，reason=exited，peak_threads=74，RSS_KiB=391240，PID/cgroup结束=True。

启动 pre2-compute-G0-G1，unit=step25-pre2-compute-G0-G1，pairs=1；命令已保存。

结束 pre2-compute-G0-G1：passed=True，reason=exited，peak_threads=74，RSS_KiB=391988，PID/cgroup结束=True。

启动 pre2-compute-G0-G2，unit=step25-pre2-compute-G0-G2，pairs=1；命令已保存。

结束 pre2-compute-G0-G2：passed=True，reason=exited，peak_threads=74，RSS_KiB=397728，PID/cgroup结束=True。

启动 pre2-compute-G0-G3，unit=step25-pre2-compute-G0-G3，pairs=1；命令已保存。

结束 pre2-compute-G0-G3：passed=True，reason=exited，peak_threads=74，RSS_KiB=343304，PID/cgroup结束=True。

启动 pre2-compute-G0-G4，unit=step25-pre2-compute-G0-G4，pairs=1；命令已保存。

结束 pre2-compute-G0-G4：passed=True，reason=exited，peak_threads=74，RSS_KiB=363152，PID/cgroup结束=True。

启动 pre2-compute-G2-copycheck，unit=step25-pre2-compute-G2-copycheck，pairs=1；命令已保存。

结束 pre2-compute-G2-copycheck：passed=True，reason=exited，peak_threads=74，RSS_KiB=370264，PID/cgroup结束=True。

启动 pre2-compute-G3-copycheck，unit=step25-pre2-compute-G3-copycheck，pairs=1；命令已保存。

结束 pre2-compute-G3-copycheck：passed=True，reason=exited，peak_threads=74，RSS_KiB=286924，PID/cgroup结束=True。

启动 pre2-compute-G4-copycheck，unit=step25-pre2-compute-G4-copycheck，pairs=1；命令已保存。

结束 pre2-compute-G4-copycheck：passed=True，reason=exited，peak_threads=74，RSS_KiB=267352，PID/cgroup结束=True。

compute四个G0配对及三种新WASM各自Copy off/on功能/S1/Gas/业务预检全部通过。

启动 pre2-fact-G0-G1，unit=step25-pre2-fact-G0-G1，pairs=1；命令已保存。

结束 pre2-fact-G0-G1：passed=True，reason=exited，peak_threads=74，RSS_KiB=401192，PID/cgroup结束=True。

启动 pre2-fact-G0-G2，unit=step25-pre2-fact-G0-G2，pairs=1；命令已保存。

结束 pre2-fact-G0-G2：passed=True，reason=exited，peak_threads=74，RSS_KiB=409944，PID/cgroup结束=True。

启动 pre2-fact-G0-G3，unit=step25-pre2-fact-G0-G3，pairs=1；命令已保存。

结束 pre2-fact-G0-G3：passed=True，reason=exited，peak_threads=74，RSS_KiB=369220，PID/cgroup结束=True。

启动 pre2-fact-G0-G4，unit=step25-pre2-fact-G0-G4，pairs=1；命令已保存。

结束 pre2-fact-G0-G4：passed=True，reason=exited，peak_threads=74，RSS_KiB=376072，PID/cgroup结束=True。

启动 pre2-fact-G2-copycheck，unit=step25-pre2-fact-G2-copycheck，pairs=1；命令已保存。

结束 pre2-fact-G2-copycheck：passed=True，reason=exited，peak_threads=74，RSS_KiB=384808，PID/cgroup结束=True。

启动 pre2-fact-G3-copycheck，unit=step25-pre2-fact-G3-copycheck，pairs=1；命令已保存。

结束 pre2-fact-G3-copycheck：passed=True，reason=exited，peak_threads=74，RSS_KiB=308248，PID/cgroup结束=True。

启动 pre2-fact-G4-copycheck，unit=step25-pre2-fact-G4-copycheck，pairs=1；命令已保存。

结束 pre2-fact-G4-copycheck：passed=True，reason=exited，peak_threads=74，RSS_KiB=305416，PID/cgroup结束=True。

fact四个G0配对及三种新WASM各自Copy off/on功能/S1/Gas/业务预检全部通过。

启动 pre2-erc721-G0-G1，unit=step25-pre2-erc721-G0-G1，pairs=1；命令已保存。

结束 pre2-erc721-G0-G1：passed=True，reason=exited，peak_threads=74，RSS_KiB=421092，PID/cgroup结束=True。

启动 pre2-erc721-G0-G2，unit=step25-pre2-erc721-G0-G2，pairs=1；命令已保存。

结束 pre2-erc721-G0-G2：passed=True，reason=exited，peak_threads=74，RSS_KiB=423972，PID/cgroup结束=True。

启动 pre2-erc721-G0-G3，unit=step25-pre2-erc721-G0-G3，pairs=1；命令已保存。

结束 pre2-erc721-G0-G3：passed=True，reason=exited，peak_threads=74，RSS_KiB=381680，PID/cgroup结束=True。

启动 pre2-erc721-G0-G4，unit=step25-pre2-erc721-G0-G4，pairs=1；命令已保存。

结束 pre2-erc721-G0-G4：passed=True，reason=exited，peak_threads=74，RSS_KiB=397564，PID/cgroup结束=True。

启动 pre2-erc721-G2-copycheck，unit=step25-pre2-erc721-G2-copycheck，pairs=1；命令已保存。

结束 pre2-erc721-G2-copycheck：passed=True，reason=exited，peak_threads=75，RSS_KiB=414596，PID/cgroup结束=True。

启动 pre2-erc721-G3-copycheck，unit=step25-pre2-erc721-G3-copycheck，pairs=1；命令已保存。

结束 pre2-erc721-G3-copycheck：passed=True，reason=exited，peak_threads=74，RSS_KiB=323800，PID/cgroup结束=True。

启动 pre2-erc721-G4-copycheck，unit=step25-pre2-erc721-G4-copycheck，pairs=1；命令已保存。

结束 pre2-erc721-G4-copycheck：passed=True，reason=exited，peak_threads=74，RSS_KiB=312680，PID/cgroup结束=True。

erc721四个G0配对及三种新WASM各自Copy off/on功能/S1/Gas/业务预检全部通过。

启动 compute-b1-G0-G1-p0，unit=step25-compute-b1-G0-G1-p0，pairs=2；命令已保存。

结束 compute-b1-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=403672，PID/cgroup结束=True。

启动 compute-b1-G0-G1-p1，unit=step25-compute-b1-G0-G1-p1，pairs=2；命令已保存。

结束 compute-b1-G0-G1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=395504，PID/cgroup结束=True。

启动 compute-b1-G0-G1-p2，unit=step25-compute-b1-G0-G1-p2，pairs=2；命令已保存。

结束 compute-b1-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=408276，PID/cgroup结束=True。

启动 fact-b1-G0-G1-p0，unit=step25-fact-b1-G0-G1-p0，pairs=2；命令已保存。

结束 fact-b1-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=404960，PID/cgroup结束=True。

启动 fact-b1-G0-G1-p1，unit=step25-fact-b1-G0-G1-p1，pairs=2；命令已保存。

结束 fact-b1-G0-G1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=427516，PID/cgroup结束=True。

启动 fact-b1-G0-G1-p2，unit=step25-fact-b1-G0-G1-p2，pairs=2；命令已保存。

结束 fact-b1-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=415060，PID/cgroup结束=True。

启动 erc721-b1-G0-G1-p0，unit=step25-erc721-b1-G0-G1-p0，pairs=2；命令已保存。

结束 erc721-b1-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=426976，PID/cgroup结束=True。

启动 erc721-b1-G0-G1-p1，unit=step25-erc721-b1-G0-G1-p1，pairs=2；命令已保存。

结束 erc721-b1-G0-G1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=427708，PID/cgroup结束=True。

启动 erc721-b1-G0-G1-p2，unit=step25-erc721-b1-G0-G1-p2，pairs=2；命令已保存。

结束 erc721-b1-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=435484，PID/cgroup结束=True。

启动 compute-b1-G0-G2-p0，unit=step25-compute-b1-G0-G2-p0，pairs=2；命令已保存。

结束 compute-b1-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=392664，PID/cgroup结束=True。

启动 compute-b1-G0-G2-p1，unit=step25-compute-b1-G0-G2-p1，pairs=2；命令已保存。

结束 compute-b1-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=408304，PID/cgroup结束=True。

启动 compute-b1-G0-G2-p2，unit=step25-compute-b1-G0-G2-p2，pairs=2；命令已保存。

结束 compute-b1-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=400072，PID/cgroup结束=True。

启动 fact-b1-G0-G2-p0，unit=step25-fact-b1-G0-G2-p0，pairs=2；命令已保存。

结束 fact-b1-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=431144，PID/cgroup结束=True。

启动 fact-b1-G0-G2-p1，unit=step25-fact-b1-G0-G2-p1，pairs=2；命令已保存。

结束 fact-b1-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=410984，PID/cgroup结束=True。

启动 fact-b1-G0-G2-p2，unit=step25-fact-b1-G0-G2-p2，pairs=2；命令已保存。

结束 fact-b1-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=412516，PID/cgroup结束=True。

启动 erc721-b1-G0-G2-p0，unit=step25-erc721-b1-G0-G2-p0，pairs=2；命令已保存。

结束 erc721-b1-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=448716，PID/cgroup结束=True。

启动 erc721-b1-G0-G2-p1，unit=step25-erc721-b1-G0-G2-p1，pairs=2；命令已保存。

结束 erc721-b1-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=420172，PID/cgroup结束=True。

启动 erc721-b1-G0-G2-p2，unit=step25-erc721-b1-G0-G2-p2，pairs=2；命令已保存。

结束 erc721-b1-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=434860，PID/cgroup结束=True。

启动 compute-b1-G0-G3-p0，unit=step25-compute-b1-G0-G3-p0，pairs=2；命令已保存。

结束 compute-b1-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=364752，PID/cgroup结束=True。

启动 compute-b1-G0-G3-p1，unit=step25-compute-b1-G0-G3-p1，pairs=2；命令已保存。

结束 compute-b1-G0-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=359148，PID/cgroup结束=True。

启动 compute-b1-G0-G3-p2，unit=step25-compute-b1-G0-G3-p2，pairs=2；命令已保存。

结束 compute-b1-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=371848，PID/cgroup结束=True。

启动 fact-b1-G0-G3-p0，unit=step25-fact-b1-G0-G3-p0，pairs=2；命令已保存。

结束 fact-b1-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=363660，PID/cgroup结束=True。

启动 fact-b1-G0-G3-p1，unit=step25-fact-b1-G0-G3-p1，pairs=2；命令已保存。

结束 fact-b1-G0-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=401492，PID/cgroup结束=True。

启动 fact-b1-G0-G3-p2，unit=step25-fact-b1-G0-G3-p2，pairs=2；命令已保存。

结束 fact-b1-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=374344，PID/cgroup结束=True。

启动 erc721-b1-G0-G3-p0，unit=step25-erc721-b1-G0-G3-p0，pairs=2；命令已保存。

结束 erc721-b1-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=406412，PID/cgroup结束=True。

启动 erc721-b1-G0-G3-p1，unit=step25-erc721-b1-G0-G3-p1，pairs=2；命令已保存。

结束 erc721-b1-G0-G3-p1：passed=True，reason=exited，peak_threads=109，RSS_KiB=391568，PID/cgroup结束=True。

启动 erc721-b1-G0-G3-p2，unit=step25-erc721-b1-G0-G3-p2，pairs=2；命令已保存。

结束 erc721-b1-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=400992，PID/cgroup结束=True。

启动 compute-b1-G0-G4-p0，unit=step25-compute-b1-G0-G4-p0，pairs=2；命令已保存。

结束 compute-b1-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=351488，PID/cgroup结束=True。

启动 compute-b1-G0-G4-p1，unit=step25-compute-b1-G0-G4-p1，pairs=2；命令已保存。

结束 compute-b1-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=369676，PID/cgroup结束=True。

启动 compute-b1-G0-G4-p2，unit=step25-compute-b1-G0-G4-p2，pairs=2；命令已保存。

结束 compute-b1-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=348492，PID/cgroup结束=True。

启动 fact-b1-G0-G4-p0，unit=step25-fact-b1-G0-G4-p0，pairs=2；命令已保存。

结束 fact-b1-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=400340，PID/cgroup结束=True。

启动 fact-b1-G0-G4-p1，unit=step25-fact-b1-G0-G4-p1，pairs=2；命令已保存。

结束 fact-b1-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=377712，PID/cgroup结束=True。

启动 fact-b1-G0-G4-p2，unit=step25-fact-b1-G0-G4-p2，pairs=2；命令已保存。

结束 fact-b1-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=394416，PID/cgroup结束=True。

启动 erc721-b1-G0-G4-p0，unit=step25-erc721-b1-G0-G4-p0，pairs=2；命令已保存。

结束 erc721-b1-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=373940，PID/cgroup结束=True。

启动 erc721-b1-G0-G4-p1，unit=step25-erc721-b1-G0-G4-p1，pairs=2；命令已保存。

结束 erc721-b1-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=398736，PID/cgroup结束=True。

启动 erc721-b1-G0-G4-p2，unit=step25-erc721-b1-G0-G4-p2，pairs=2；命令已保存。

结束 erc721-b1-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=383360，PID/cgroup结束=True。

启动 compute-b1-G1-G2-p0，unit=step25-compute-b1-G1-G2-p0，pairs=2；命令已保存。

结束 compute-b1-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=387436，PID/cgroup结束=True。

启动 compute-b1-G1-G2-p1，unit=step25-compute-b1-G1-G2-p1，pairs=2；命令已保存。

结束 compute-b1-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=400864，PID/cgroup结束=True。

启动 compute-b1-G1-G2-p2，unit=step25-compute-b1-G1-G2-p2，pairs=2；命令已保存。

结束 compute-b1-G1-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=395828，PID/cgroup结束=True。

启动 fact-b1-G1-G2-p0，unit=step25-fact-b1-G1-G2-p0，pairs=2；命令已保存。

结束 fact-b1-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=405456，PID/cgroup结束=True。

启动 fact-b1-G1-G2-p1，unit=step25-fact-b1-G1-G2-p1，pairs=2；命令已保存。

结束 fact-b1-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=412584，PID/cgroup结束=True。

启动 fact-b1-G1-G2-p2，unit=step25-fact-b1-G1-G2-p2，pairs=2；命令已保存。

结束 fact-b1-G1-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=396328，PID/cgroup结束=True。

启动 erc721-b1-G1-G2-p0，unit=step25-erc721-b1-G1-G2-p0，pairs=2；命令已保存。

结束 erc721-b1-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=407976，PID/cgroup结束=True。

启动 erc721-b1-G1-G2-p1，unit=step25-erc721-b1-G1-G2-p1，pairs=2；命令已保存。

结束 erc721-b1-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=428436，PID/cgroup结束=True。

启动 erc721-b1-G1-G2-p2，unit=step25-erc721-b1-G1-G2-p2，pairs=2；命令已保存。

结束 erc721-b1-G1-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=418416，PID/cgroup结束=True。

启动 compute-b1-G1-G3-p0，unit=step25-compute-b1-G1-G3-p0，pairs=2；命令已保存。

结束 compute-b1-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=358448，PID/cgroup结束=True。

启动 compute-b1-G1-G3-p1，unit=step25-compute-b1-G1-G3-p1，pairs=2；命令已保存。

结束 compute-b1-G1-G3-p1：passed=True，reason=exited，peak_threads=109，RSS_KiB=357592，PID/cgroup结束=True。

启动 compute-b1-G1-G3-p2，unit=step25-compute-b1-G1-G3-p2，pairs=2；命令已保存。

结束 compute-b1-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=352888，PID/cgroup结束=True。

启动 fact-b1-G1-G3-p0，unit=step25-fact-b1-G1-G3-p0，pairs=2；命令已保存。

结束 fact-b1-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=352440，PID/cgroup结束=True。

启动 fact-b1-G1-G3-p1，unit=step25-fact-b1-G1-G3-p1，pairs=2；命令已保存。

结束 fact-b1-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=362832，PID/cgroup结束=True。

启动 fact-b1-G1-G3-p2，unit=step25-fact-b1-G1-G3-p2，pairs=2；命令已保存。

结束 fact-b1-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=372348，PID/cgroup结束=True。

启动 erc721-b1-G1-G3-p0，unit=step25-erc721-b1-G1-G3-p0，pairs=2；命令已保存。

结束 erc721-b1-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=382188，PID/cgroup结束=True。

启动 erc721-b1-G1-G3-p1，unit=step25-erc721-b1-G1-G3-p1，pairs=2；命令已保存。

结束 erc721-b1-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=386760，PID/cgroup结束=True。

启动 erc721-b1-G1-G3-p2，unit=step25-erc721-b1-G1-G3-p2，pairs=2；命令已保存。

结束 erc721-b1-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=384052，PID/cgroup结束=True。

启动 compute-b1-G1-G4-p0，unit=step25-compute-b1-G1-G4-p0，pairs=2；命令已保存。

结束 compute-b1-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=352792，PID/cgroup结束=True。

启动 compute-b1-G1-G4-p1，unit=step25-compute-b1-G1-G4-p1，pairs=2；命令已保存。

结束 compute-b1-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=344600，PID/cgroup结束=True。

启动 compute-b1-G1-G4-p2，unit=step25-compute-b1-G1-G4-p2，pairs=2；命令已保存。

结束 compute-b1-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=352384，PID/cgroup结束=True。

启动 fact-b1-G1-G4-p0，unit=step25-fact-b1-G1-G4-p0，pairs=2；命令已保存。

结束 fact-b1-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=356656，PID/cgroup结束=True。

启动 fact-b1-G1-G4-p1，unit=step25-fact-b1-G1-G4-p1，pairs=2；命令已保存。

结束 fact-b1-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=387280，PID/cgroup结束=True。

启动 fact-b1-G1-G4-p2，unit=step25-fact-b1-G1-G4-p2，pairs=2；命令已保存。

结束 fact-b1-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=359012，PID/cgroup结束=True。

启动 erc721-b1-G1-G4-p0，unit=step25-erc721-b1-G1-G4-p0，pairs=2；命令已保存。

结束 erc721-b1-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=385000，PID/cgroup结束=True。

启动 erc721-b1-G1-G4-p1，unit=step25-erc721-b1-G1-G4-p1，pairs=2；命令已保存。

结束 erc721-b1-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=366324，PID/cgroup结束=True。

启动 erc721-b1-G1-G4-p2，unit=step25-erc721-b1-G1-G4-p2，pairs=2；命令已保存。

结束 erc721-b1-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=382960，PID/cgroup结束=True。

启动 compute-b1-G2-G4-p0，unit=step25-compute-b1-G2-G4-p0，pairs=2；命令已保存。

结束 compute-b1-G2-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=339500，PID/cgroup结束=True。

启动 compute-b1-G2-G4-p1，unit=step25-compute-b1-G2-G4-p1，pairs=2；命令已保存。

结束 compute-b1-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=347408，PID/cgroup结束=True。

启动 compute-b1-G2-G4-p2，unit=step25-compute-b1-G2-G4-p2，pairs=2；命令已保存。

结束 compute-b1-G2-G4-p2：passed=True，reason=exited，peak_threads=109，RSS_KiB=347780，PID/cgroup结束=True。

启动 fact-b1-G2-G4-p0，unit=step25-fact-b1-G2-G4-p0，pairs=2；命令已保存。

结束 fact-b1-G2-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=365300，PID/cgroup结束=True。

启动 fact-b1-G2-G4-p1，unit=step25-fact-b1-G2-G4-p1，pairs=2；命令已保存。

结束 fact-b1-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=363784，PID/cgroup结束=True。

启动 fact-b1-G2-G4-p2，unit=step25-fact-b1-G2-G4-p2，pairs=2；命令已保存。

结束 fact-b1-G2-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=356200，PID/cgroup结束=True。

启动 erc721-b1-G2-G4-p0，unit=step25-erc721-b1-G2-G4-p0，pairs=2；命令已保存。

结束 erc721-b1-G2-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=368644，PID/cgroup结束=True。

启动 erc721-b1-G2-G4-p1，unit=step25-erc721-b1-G2-G4-p1，pairs=2；命令已保存。

结束 erc721-b1-G2-G4-p1：passed=True，reason=exited，peak_threads=109，RSS_KiB=378208，PID/cgroup结束=True。

启动 erc721-b1-G2-G4-p2，unit=step25-erc721-b1-G2-G4-p2，pairs=2；命令已保存。

结束 erc721-b1-G2-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=379252，PID/cgroup结束=True。

正式批1 contracts=['compute', 'fact', 'erc721']完成，所有8条直接对照各6对，逐过程日志/receipt/check/outcome已保存。

启动 erc721-b2-G2-G4-p0，unit=step25-erc721-b2-G2-G4-p0，pairs=2；命令已保存。

结束 erc721-b2-G2-G4-p0：passed=True，reason=exited，peak_threads=109，RSS_KiB=365924，PID/cgroup结束=True。

启动 erc721-b2-G2-G4-p1，unit=step25-erc721-b2-G2-G4-p1，pairs=2；命令已保存。

结束 erc721-b2-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=372068，PID/cgroup结束=True。

启动 erc721-b2-G2-G4-p2，unit=step25-erc721-b2-G2-G4-p2，pairs=2；命令已保存。

结束 erc721-b2-G2-G4-p2：passed=True，reason=exited，peak_threads=109，RSS_KiB=364124，PID/cgroup结束=True。

启动 fact-b2-G2-G4-p0，unit=step25-fact-b2-G2-G4-p0，pairs=2；命令已保存。

结束 fact-b2-G2-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=367424，PID/cgroup结束=True。

启动 fact-b2-G2-G4-p1，unit=step25-fact-b2-G2-G4-p1，pairs=2；命令已保存。

结束 fact-b2-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=350992，PID/cgroup结束=True。

启动 fact-b2-G2-G4-p2，unit=step25-fact-b2-G2-G4-p2，pairs=2；命令已保存。

结束 fact-b2-G2-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=361896，PID/cgroup结束=True。

启动 compute-b2-G2-G4-p0，unit=step25-compute-b2-G2-G4-p0，pairs=2；命令已保存。

结束 compute-b2-G2-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=350652，PID/cgroup结束=True。

启动 compute-b2-G2-G4-p1，unit=step25-compute-b2-G2-G4-p1，pairs=2；命令已保存。

结束 compute-b2-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=354564，PID/cgroup结束=True。

启动 compute-b2-G2-G4-p2，unit=step25-compute-b2-G2-G4-p2，pairs=2；命令已保存。

结束 compute-b2-G2-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=333884，PID/cgroup结束=True。

启动 erc721-b2-G1-G4-p0，unit=step25-erc721-b2-G1-G4-p0，pairs=2；命令已保存。

结束 erc721-b2-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=375096，PID/cgroup结束=True。

启动 erc721-b2-G1-G4-p1，unit=step25-erc721-b2-G1-G4-p1，pairs=2；命令已保存。

结束 erc721-b2-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=375408，PID/cgroup结束=True。

启动 erc721-b2-G1-G4-p2，unit=step25-erc721-b2-G1-G4-p2，pairs=2；命令已保存。

结束 erc721-b2-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=374148，PID/cgroup结束=True。

启动 fact-b2-G1-G4-p0，unit=step25-fact-b2-G1-G4-p0，pairs=2；命令已保存。

结束 fact-b2-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=359444，PID/cgroup结束=True。

启动 fact-b2-G1-G4-p1，unit=step25-fact-b2-G1-G4-p1，pairs=2；命令已保存。

结束 fact-b2-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=373248，PID/cgroup结束=True。

启动 fact-b2-G1-G4-p2，unit=step25-fact-b2-G1-G4-p2，pairs=2；命令已保存。

结束 fact-b2-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=354444，PID/cgroup结束=True。

启动 compute-b2-G1-G4-p0，unit=step25-compute-b2-G1-G4-p0，pairs=2；命令已保存。

结束 compute-b2-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=356872，PID/cgroup结束=True。

启动 compute-b2-G1-G4-p1，unit=step25-compute-b2-G1-G4-p1，pairs=2；命令已保存。

结束 compute-b2-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=343196，PID/cgroup结束=True。

启动 compute-b2-G1-G4-p2，unit=step25-compute-b2-G1-G4-p2，pairs=2；命令已保存。

结束 compute-b2-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=360944，PID/cgroup结束=True。

启动 erc721-b2-G1-G3-p0，unit=step25-erc721-b2-G1-G3-p0，pairs=2；命令已保存。

结束 erc721-b2-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=370716，PID/cgroup结束=True。

启动 erc721-b2-G1-G3-p1，unit=step25-erc721-b2-G1-G3-p1，pairs=2；命令已保存。

结束 erc721-b2-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=376468，PID/cgroup结束=True。

启动 erc721-b2-G1-G3-p2，unit=step25-erc721-b2-G1-G3-p2，pairs=2；命令已保存。

结束 erc721-b2-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=367712，PID/cgroup结束=True。

启动 fact-b2-G1-G3-p0，unit=step25-fact-b2-G1-G3-p0，pairs=2；命令已保存。

结束 fact-b2-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=379452，PID/cgroup结束=True。

启动 fact-b2-G1-G3-p1，unit=step25-fact-b2-G1-G3-p1，pairs=2；命令已保存。

结束 fact-b2-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=362060，PID/cgroup结束=True。

启动 fact-b2-G1-G3-p2，unit=step25-fact-b2-G1-G3-p2，pairs=2；命令已保存。

结束 fact-b2-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=373508，PID/cgroup结束=True。

启动 compute-b2-G1-G3-p0，unit=step25-compute-b2-G1-G3-p0，pairs=2；命令已保存。

结束 compute-b2-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=343492，PID/cgroup结束=True。

启动 compute-b2-G1-G3-p1，unit=step25-compute-b2-G1-G3-p1，pairs=2；命令已保存。

结束 compute-b2-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=355100，PID/cgroup结束=True。

启动 compute-b2-G1-G3-p2，unit=step25-compute-b2-G1-G3-p2，pairs=2；命令已保存。

结束 compute-b2-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=350400，PID/cgroup结束=True。

启动 erc721-b2-G1-G2-p0，unit=step25-erc721-b2-G1-G2-p0，pairs=2；命令已保存。

结束 erc721-b2-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=414600，PID/cgroup结束=True。

启动 erc721-b2-G1-G2-p1，unit=step25-erc721-b2-G1-G2-p1，pairs=2；命令已保存。

结束 erc721-b2-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=400824，PID/cgroup结束=True。

启动 erc721-b2-G1-G2-p2，unit=step25-erc721-b2-G1-G2-p2，pairs=2；命令已保存。

结束 erc721-b2-G1-G2-p2：passed=True，reason=exited，peak_threads=109，RSS_KiB=416136，PID/cgroup结束=True。

启动 fact-b2-G1-G2-p0，unit=step25-fact-b2-G1-G2-p0，pairs=2；命令已保存。

结束 fact-b2-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=389164，PID/cgroup结束=True。

启动 fact-b2-G1-G2-p1，unit=step25-fact-b2-G1-G2-p1，pairs=2；命令已保存。

结束 fact-b2-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=403696，PID/cgroup结束=True。

启动 fact-b2-G1-G2-p2，unit=step25-fact-b2-G1-G2-p2，pairs=2；命令已保存。

结束 fact-b2-G1-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=391248，PID/cgroup结束=True。

启动 compute-b2-G1-G2-p0，unit=step25-compute-b2-G1-G2-p0，pairs=2；命令已保存。

结束 compute-b2-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=404900，PID/cgroup结束=True。

启动 compute-b2-G1-G2-p1，unit=step25-compute-b2-G1-G2-p1，pairs=2；命令已保存。

结束 compute-b2-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=392260，PID/cgroup结束=True。

启动 compute-b2-G1-G2-p2，unit=step25-compute-b2-G1-G2-p2，pairs=2；命令已保存。

结束 compute-b2-G1-G2-p2：passed=True，reason=exited，peak_threads=109，RSS_KiB=403408，PID/cgroup结束=True。

启动 erc721-b2-G0-G4-p0，unit=step25-erc721-b2-G0-G4-p0，pairs=2；命令已保存。

结束 erc721-b2-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=378752，PID/cgroup结束=True。

启动 erc721-b2-G0-G4-p1，unit=step25-erc721-b2-G0-G4-p1，pairs=2；命令已保存。

结束 erc721-b2-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=409120，PID/cgroup结束=True。

启动 erc721-b2-G0-G4-p2，unit=step25-erc721-b2-G0-G4-p2，pairs=2；命令已保存。

结束 erc721-b2-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=373420，PID/cgroup结束=True。

启动 fact-b2-G0-G4-p0，unit=step25-fact-b2-G0-G4-p0，pairs=2；命令已保存。

结束 fact-b2-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=388348，PID/cgroup结束=True。

启动 fact-b2-G0-G4-p1，unit=step25-fact-b2-G0-G4-p1，pairs=2；命令已保存。

结束 fact-b2-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=362880，PID/cgroup结束=True。

启动 fact-b2-G0-G4-p2，unit=step25-fact-b2-G0-G4-p2，pairs=2；命令已保存。

结束 fact-b2-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=380468，PID/cgroup结束=True。

启动 compute-b2-G0-G4-p0，unit=step25-compute-b2-G0-G4-p0，pairs=2；命令已保存。

结束 compute-b2-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=349408，PID/cgroup结束=True。

启动 compute-b2-G0-G4-p1，unit=step25-compute-b2-G0-G4-p1，pairs=2；命令已保存。

结束 compute-b2-G0-G4-p1：passed=True，reason=exited，peak_threads=109，RSS_KiB=368828，PID/cgroup结束=True。

启动 compute-b2-G0-G4-p2，unit=step25-compute-b2-G0-G4-p2，pairs=2；命令已保存。

结束 compute-b2-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=356280，PID/cgroup结束=True。

启动 erc721-b2-G0-G3-p0，unit=step25-erc721-b2-G0-G3-p0，pairs=2；命令已保存。

结束 erc721-b2-G0-G3-p0：passed=True，reason=exited，peak_threads=109，RSS_KiB=418040，PID/cgroup结束=True。

启动 erc721-b2-G0-G3-p1，unit=step25-erc721-b2-G0-G3-p1，pairs=2；命令已保存。

结束 erc721-b2-G0-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=396188，PID/cgroup结束=True。

启动 erc721-b2-G0-G3-p2，unit=step25-erc721-b2-G0-G3-p2，pairs=2；命令已保存。

结束 erc721-b2-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=401092，PID/cgroup结束=True。

启动 fact-b2-G0-G3-p0，unit=step25-fact-b2-G0-G3-p0，pairs=2；命令已保存。

结束 fact-b2-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=369056，PID/cgroup结束=True。

启动 fact-b2-G0-G3-p1，unit=step25-fact-b2-G0-G3-p1，pairs=2；命令已保存。

结束 fact-b2-G0-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=388252，PID/cgroup结束=True。

启动 fact-b2-G0-G3-p2，unit=step25-fact-b2-G0-G3-p2，pairs=2；命令已保存。

结束 fact-b2-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=376560，PID/cgroup结束=True。

启动 compute-b2-G0-G3-p0，unit=step25-compute-b2-G0-G3-p0，pairs=2；命令已保存。

结束 compute-b2-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=370540，PID/cgroup结束=True。

启动 compute-b2-G0-G3-p1，unit=step25-compute-b2-G0-G3-p1，pairs=2；命令已保存。

结束 compute-b2-G0-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=355988，PID/cgroup结束=True。

启动 compute-b2-G0-G3-p2，unit=step25-compute-b2-G0-G3-p2，pairs=2；命令已保存。

结束 compute-b2-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=369144，PID/cgroup结束=True。

启动 erc721-b2-G0-G2-p0，unit=step25-erc721-b2-G0-G2-p0，pairs=2；命令已保存。

结束 erc721-b2-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=437876，PID/cgroup结束=True。

启动 erc721-b2-G0-G2-p1，unit=step25-erc721-b2-G0-G2-p1，pairs=2；命令已保存。

结束 erc721-b2-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=425436，PID/cgroup结束=True。

启动 erc721-b2-G0-G2-p2，unit=step25-erc721-b2-G0-G2-p2，pairs=2；命令已保存。

结束 erc721-b2-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=434840，PID/cgroup结束=True。

启动 fact-b2-G0-G2-p0，unit=step25-fact-b2-G0-G2-p0，pairs=2；命令已保存。

结束 fact-b2-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=419924，PID/cgroup结束=True。

启动 fact-b2-G0-G2-p1，unit=step25-fact-b2-G0-G2-p1，pairs=2；命令已保存。

结束 fact-b2-G0-G2-p1：passed=True，reason=exited，peak_threads=109，RSS_KiB=420084，PID/cgroup结束=True。

启动 fact-b2-G0-G2-p2，unit=step25-fact-b2-G0-G2-p2，pairs=2；命令已保存。

结束 fact-b2-G0-G2-p2：passed=True，reason=exited，peak_threads=109，RSS_KiB=426488，PID/cgroup结束=True。

启动 compute-b2-G0-G2-p0，unit=step25-compute-b2-G0-G2-p0，pairs=2；命令已保存。

结束 compute-b2-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=410812，PID/cgroup结束=True。

启动 compute-b2-G0-G2-p1，unit=step25-compute-b2-G0-G2-p1，pairs=2；命令已保存。

结束 compute-b2-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=405552，PID/cgroup结束=True。

启动 compute-b2-G0-G2-p2，unit=step25-compute-b2-G0-G2-p2，pairs=2；命令已保存。

结束 compute-b2-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=411004，PID/cgroup结束=True。

启动 erc721-b2-G0-G1-p0，unit=step25-erc721-b2-G0-G1-p0，pairs=2；命令已保存。

结束 erc721-b2-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=438800，PID/cgroup结束=True。

启动 erc721-b2-G0-G1-p1，unit=step25-erc721-b2-G0-G1-p1，pairs=2；命令已保存。

结束 erc721-b2-G0-G1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=423264，PID/cgroup结束=True。

启动 erc721-b2-G0-G1-p2，unit=step25-erc721-b2-G0-G1-p2，pairs=2；命令已保存。

结束 erc721-b2-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=429276，PID/cgroup结束=True。

启动 fact-b2-G0-G1-p0，unit=step25-fact-b2-G0-G1-p0，pairs=2；命令已保存。

结束 fact-b2-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=418668，PID/cgroup结束=True。

启动 fact-b2-G0-G1-p1，unit=step25-fact-b2-G0-G1-p1，pairs=2；命令已保存。

结束 fact-b2-G0-G1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=426196，PID/cgroup结束=True。

启动 fact-b2-G0-G1-p2，unit=step25-fact-b2-G0-G1-p2，pairs=2；命令已保存。

结束 fact-b2-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=414672，PID/cgroup结束=True。

启动 compute-b2-G0-G1-p0，unit=step25-compute-b2-G0-G1-p0，pairs=2；命令已保存。

结束 compute-b2-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=402968，PID/cgroup结束=True。

启动 compute-b2-G0-G1-p1，unit=step25-compute-b2-G0-G1-p1，pairs=2；命令已保存。

结束 compute-b2-G0-G1-p1：passed=True，reason=exited，peak_threads=109，RSS_KiB=410396，PID/cgroup结束=True。

启动 compute-b2-G0-G1-p2，unit=step25-compute-b2-G0-G1-p2，pairs=2；命令已保存。

结束 compute-b2-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=404552，PID/cgroup结束=True。

正式批2 contracts=['compute', 'fact', 'erc721']完成，所有8条直接对照各6对，逐过程日志/receipt/check/outcome已保存。

启动 compute-b3-G0-G1-p0，unit=step25-compute-b3-G0-G1-p0，pairs=2；命令已保存。

结束 compute-b3-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=402760，PID/cgroup结束=True。

启动 compute-b3-G0-G1-p1，unit=step25-compute-b3-G0-G1-p1，pairs=2；命令已保存。

结束 compute-b3-G0-G1-p1：passed=True，reason=exited，peak_threads=109，RSS_KiB=406500，PID/cgroup结束=True。

启动 compute-b3-G0-G1-p2，unit=step25-compute-b3-G0-G1-p2，pairs=2；命令已保存。

结束 compute-b3-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=407068，PID/cgroup结束=True。

启动 fact-b3-G0-G1-p0，unit=step25-fact-b3-G0-G1-p0，pairs=2；命令已保存。

结束 fact-b3-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=419500，PID/cgroup结束=True。

启动 fact-b3-G0-G1-p1，unit=step25-fact-b3-G0-G1-p1，pairs=2；命令已保存。

结束 fact-b3-G0-G1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=409752，PID/cgroup结束=True。

启动 fact-b3-G0-G1-p2，unit=step25-fact-b3-G0-G1-p2，pairs=2；命令已保存。

结束 fact-b3-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=403520，PID/cgroup结束=True。

启动 erc721-b3-G0-G1-p0，unit=step25-erc721-b3-G0-G1-p0，pairs=2；命令已保存。

结束 erc721-b3-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=425456，PID/cgroup结束=True。

启动 erc721-b3-G0-G1-p1，unit=step25-erc721-b3-G0-G1-p1，pairs=2；命令已保存。

结束 erc721-b3-G0-G1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=434564，PID/cgroup结束=True。

启动 erc721-b3-G0-G1-p2，unit=step25-erc721-b3-G0-G1-p2，pairs=2；命令已保存。

结束 erc721-b3-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=430816，PID/cgroup结束=True。

启动 compute-b3-G0-G2-p0，unit=step25-compute-b3-G0-G2-p0，pairs=2；命令已保存。

结束 compute-b3-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=405504，PID/cgroup结束=True。

启动 compute-b3-G0-G2-p1，unit=step25-compute-b3-G0-G2-p1，pairs=2；命令已保存。

结束 compute-b3-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=411188，PID/cgroup结束=True。

启动 compute-b3-G0-G2-p2，unit=step25-compute-b3-G0-G2-p2，pairs=2；命令已保存。

结束 compute-b3-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=407512，PID/cgroup结束=True。

启动 fact-b3-G0-G2-p0，unit=step25-fact-b3-G0-G2-p0，pairs=2；命令已保存。

结束 fact-b3-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=424096，PID/cgroup结束=True。

启动 fact-b3-G0-G2-p1，unit=step25-fact-b3-G0-G2-p1，pairs=2；命令已保存。

结束 fact-b3-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=425180，PID/cgroup结束=True。

启动 fact-b3-G0-G2-p2，unit=step25-fact-b3-G0-G2-p2，pairs=2；命令已保存。

结束 fact-b3-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=419560，PID/cgroup结束=True。

启动 erc721-b3-G0-G2-p0，unit=step25-erc721-b3-G0-G2-p0，pairs=2；命令已保存。

结束 erc721-b3-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=423760，PID/cgroup结束=True。

启动 erc721-b3-G0-G2-p1，unit=step25-erc721-b3-G0-G2-p1，pairs=2；命令已保存。

结束 erc721-b3-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=416396，PID/cgroup结束=True。

启动 erc721-b3-G0-G2-p2，unit=step25-erc721-b3-G0-G2-p2，pairs=2；命令已保存。

结束 erc721-b3-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=433048，PID/cgroup结束=True。

启动 compute-b3-G0-G3-p0，unit=step25-compute-b3-G0-G3-p0，pairs=2；命令已保存。

结束 compute-b3-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=377548，PID/cgroup结束=True。

启动 compute-b3-G0-G3-p1，unit=step25-compute-b3-G0-G3-p1，pairs=2；命令已保存。

结束 compute-b3-G0-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=351576，PID/cgroup结束=True。

启动 compute-b3-G0-G3-p2，unit=step25-compute-b3-G0-G3-p2，pairs=2；命令已保存。

结束 compute-b3-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=369356，PID/cgroup结束=True。

启动 fact-b3-G0-G3-p0，unit=step25-fact-b3-G0-G3-p0，pairs=2；命令已保存。

结束 fact-b3-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=381244，PID/cgroup结束=True。

启动 fact-b3-G0-G3-p1，unit=step25-fact-b3-G0-G3-p1，pairs=2；命令已保存。

结束 fact-b3-G0-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=394896，PID/cgroup结束=True。

启动 fact-b3-G0-G3-p2，unit=step25-fact-b3-G0-G3-p2，pairs=2；命令已保存。

结束 fact-b3-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=373164，PID/cgroup结束=True。

启动 erc721-b3-G0-G3-p0，unit=step25-erc721-b3-G0-G3-p0，pairs=2；命令已保存。

结束 erc721-b3-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=409944，PID/cgroup结束=True。

启动 erc721-b3-G0-G3-p1，unit=step25-erc721-b3-G0-G3-p1，pairs=2；命令已保存。

结束 erc721-b3-G0-G3-p1：passed=True，reason=exited，peak_threads=109，RSS_KiB=386748，PID/cgroup结束=True。

启动 erc721-b3-G0-G3-p2，unit=step25-erc721-b3-G0-G3-p2，pairs=2；命令已保存。

结束 erc721-b3-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=399756，PID/cgroup结束=True。

启动 compute-b3-G0-G4-p0，unit=step25-compute-b3-G0-G4-p0，pairs=2；命令已保存。

结束 compute-b3-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=358136，PID/cgroup结束=True。

启动 compute-b3-G0-G4-p1，unit=step25-compute-b3-G0-G4-p1，pairs=2；命令已保存。

结束 compute-b3-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=372876，PID/cgroup结束=True。

启动 compute-b3-G0-G4-p2，unit=step25-compute-b3-G0-G4-p2，pairs=2；命令已保存。

结束 compute-b3-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=358748，PID/cgroup结束=True。

启动 fact-b3-G0-G4-p0，unit=step25-fact-b3-G0-G4-p0，pairs=2；命令已保存。

结束 fact-b3-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=398700，PID/cgroup结束=True。

启动 fact-b3-G0-G4-p1，unit=step25-fact-b3-G0-G4-p1，pairs=2；命令已保存。

结束 fact-b3-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=374476，PID/cgroup结束=True。

启动 fact-b3-G0-G4-p2，unit=step25-fact-b3-G0-G4-p2，pairs=2；命令已保存。

结束 fact-b3-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=398560，PID/cgroup结束=True。

启动 erc721-b3-G0-G4-p0，unit=step25-erc721-b3-G0-G4-p0，pairs=2；命令已保存。

结束 erc721-b3-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=379984，PID/cgroup结束=True。

启动 erc721-b3-G0-G4-p1，unit=step25-erc721-b3-G0-G4-p1，pairs=2；命令已保存。

结束 erc721-b3-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=405232，PID/cgroup结束=True。

启动 erc721-b3-G0-G4-p2，unit=step25-erc721-b3-G0-G4-p2，pairs=2；命令已保存。

结束 erc721-b3-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=383364，PID/cgroup结束=True。

启动 compute-b3-G1-G2-p0，unit=step25-compute-b3-G1-G2-p0，pairs=2；命令已保存。

结束 compute-b3-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=404000，PID/cgroup结束=True。

启动 compute-b3-G1-G2-p1，unit=step25-compute-b3-G1-G2-p1，pairs=2；命令已保存。

结束 compute-b3-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=391600，PID/cgroup结束=True。

启动 compute-b3-G1-G2-p2，unit=step25-compute-b3-G1-G2-p2，pairs=2；命令已保存。

结束 compute-b3-G1-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=403456，PID/cgroup结束=True。

启动 fact-b3-G1-G2-p0，unit=step25-fact-b3-G1-G2-p0，pairs=2；命令已保存。

结束 fact-b3-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=391200，PID/cgroup结束=True。

启动 fact-b3-G1-G2-p1，unit=step25-fact-b3-G1-G2-p1，pairs=2；命令已保存。

结束 fact-b3-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=393836，PID/cgroup结束=True。

启动 fact-b3-G1-G2-p2，unit=step25-fact-b3-G1-G2-p2，pairs=2；命令已保存。

结束 fact-b3-G1-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=404984，PID/cgroup结束=True。

启动 erc721-b3-G1-G2-p0，unit=step25-erc721-b3-G1-G2-p0，pairs=2；命令已保存。

结束 erc721-b3-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=420736，PID/cgroup结束=True。

启动 erc721-b3-G1-G2-p1，unit=step25-erc721-b3-G1-G2-p1，pairs=2；命令已保存。

结束 erc721-b3-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=418196，PID/cgroup结束=True。

启动 erc721-b3-G1-G2-p2，unit=step25-erc721-b3-G1-G2-p2，pairs=2；命令已保存。

结束 erc721-b3-G1-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=408740，PID/cgroup结束=True。

启动 compute-b3-G1-G3-p0，unit=step25-compute-b3-G1-G3-p0，pairs=2；命令已保存。

结束 compute-b3-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=353508，PID/cgroup结束=True。

启动 compute-b3-G1-G3-p1，unit=step25-compute-b3-G1-G3-p1，pairs=2；命令已保存。

结束 compute-b3-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=363980，PID/cgroup结束=True。

启动 compute-b3-G1-G3-p2，unit=step25-compute-b3-G1-G3-p2，pairs=2；命令已保存。

结束 compute-b3-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=339636，PID/cgroup结束=True。

启动 fact-b3-G1-G3-p0，unit=step25-fact-b3-G1-G3-p0，pairs=2；命令已保存。

结束 fact-b3-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=355876，PID/cgroup结束=True。

启动 fact-b3-G1-G3-p1，unit=step25-fact-b3-G1-G3-p1，pairs=2；命令已保存。

结束 fact-b3-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=360212，PID/cgroup结束=True。

启动 fact-b3-G1-G3-p2，unit=step25-fact-b3-G1-G3-p2，pairs=2；命令已保存。

结束 fact-b3-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=373036，PID/cgroup结束=True。

启动 erc721-b3-G1-G3-p0，unit=step25-erc721-b3-G1-G3-p0，pairs=2；命令已保存。

结束 erc721-b3-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=371480，PID/cgroup结束=True。

启动 erc721-b3-G1-G3-p1，unit=step25-erc721-b3-G1-G3-p1，pairs=2；命令已保存。

结束 erc721-b3-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=393136，PID/cgroup结束=True。

启动 erc721-b3-G1-G3-p2，unit=step25-erc721-b3-G1-G3-p2，pairs=2；命令已保存。

结束 erc721-b3-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=367072，PID/cgroup结束=True。

启动 compute-b3-G1-G4-p0，unit=step25-compute-b3-G1-G4-p0，pairs=2；命令已保存。

结束 compute-b3-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=345304，PID/cgroup结束=True。

启动 compute-b3-G1-G4-p1，unit=step25-compute-b3-G1-G4-p1，pairs=2；命令已保存。

结束 compute-b3-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=349000，PID/cgroup结束=True。

启动 compute-b3-G1-G4-p2，unit=step25-compute-b3-G1-G4-p2，pairs=2；命令已保存。

结束 compute-b3-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=355108，PID/cgroup结束=True。

启动 fact-b3-G1-G4-p0，unit=step25-fact-b3-G1-G4-p0，pairs=2；命令已保存。

结束 fact-b3-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=358636，PID/cgroup结束=True。

启动 fact-b3-G1-G4-p1，unit=step25-fact-b3-G1-G4-p1，pairs=2；命令已保存。

结束 fact-b3-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=374728，PID/cgroup结束=True。

启动 fact-b3-G1-G4-p2，unit=step25-fact-b3-G1-G4-p2，pairs=2；命令已保存。

结束 fact-b3-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=360400，PID/cgroup结束=True。

启动 erc721-b3-G1-G4-p0，unit=step25-erc721-b3-G1-G4-p0，pairs=2；命令已保存。

结束 erc721-b3-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=388192，PID/cgroup结束=True。

启动 erc721-b3-G1-G4-p1，unit=step25-erc721-b3-G1-G4-p1，pairs=2；命令已保存。

结束 erc721-b3-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=364876，PID/cgroup结束=True。

启动 erc721-b3-G1-G4-p2，unit=step25-erc721-b3-G1-G4-p2，pairs=2；命令已保存。

结束 erc721-b3-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=383600，PID/cgroup结束=True。

启动 compute-b3-G2-G4-p0，unit=step25-compute-b3-G2-G4-p0，pairs=2；命令已保存。

结束 compute-b3-G2-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=338920，PID/cgroup结束=True。

启动 compute-b3-G2-G4-p1，unit=step25-compute-b3-G2-G4-p1，pairs=2；命令已保存。

结束 compute-b3-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=335252，PID/cgroup结束=True。

启动 compute-b3-G2-G4-p2，unit=step25-compute-b3-G2-G4-p2，pairs=2；命令已保存。

结束 compute-b3-G2-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=348716，PID/cgroup结束=True。

启动 fact-b3-G2-G4-p0，unit=step25-fact-b3-G2-G4-p0，pairs=2；命令已保存。

结束 fact-b3-G2-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=379420，PID/cgroup结束=True。

启动 fact-b3-G2-G4-p1，unit=step25-fact-b3-G2-G4-p1，pairs=2；命令已保存。

结束 fact-b3-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=357632，PID/cgroup结束=True。

启动 fact-b3-G2-G4-p2，unit=step25-fact-b3-G2-G4-p2，pairs=2；命令已保存。

结束 fact-b3-G2-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=357636，PID/cgroup结束=True。

启动 erc721-b3-G2-G4-p0，unit=step25-erc721-b3-G2-G4-p0，pairs=2；命令已保存。

结束 erc721-b3-G2-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=366916，PID/cgroup结束=True。

启动 erc721-b3-G2-G4-p1，unit=step25-erc721-b3-G2-G4-p1，pairs=2；命令已保存。

结束 erc721-b3-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=370388，PID/cgroup结束=True。

启动 erc721-b3-G2-G4-p2，unit=step25-erc721-b3-G2-G4-p2，pairs=2；命令已保存。

结束 erc721-b3-G2-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=371064，PID/cgroup结束=True。

正式批3 contracts=['compute', 'fact', 'erc721']完成，所有8条直接对照各6对，逐过程日志/receipt/check/outcome已保存。

启动 pre2-normal-G0-G1，unit=step25-pre2-normal-G0-G1，pairs=1；命令已保存。

结束 pre2-normal-G0-G1：passed=True，reason=exited，peak_threads=74，RSS_KiB=375672，PID/cgroup结束=True。

启动 pre2-normal-G0-G2，unit=step25-pre2-normal-G0-G2，pairs=1；命令已保存。

结束 pre2-normal-G0-G2：passed=True，reason=exited，peak_threads=74，RSS_KiB=374572，PID/cgroup结束=True。

启动 pre2-normal-G0-G3，unit=step25-pre2-normal-G0-G3，pairs=1；命令已保存。

结束 pre2-normal-G0-G3：passed=True，reason=exited，peak_threads=74，RSS_KiB=345460，PID/cgroup结束=True。

启动 pre2-normal-G0-G4，unit=step25-pre2-normal-G0-G4，pairs=1；命令已保存。

结束 pre2-normal-G0-G4：passed=True，reason=exited，peak_threads=74，RSS_KiB=353500，PID/cgroup结束=True。

启动 pre2-normal-G2-copycheck，unit=step25-pre2-normal-G2-copycheck，pairs=1；命令已保存。

结束 pre2-normal-G2-copycheck：passed=True，reason=exited，peak_threads=74，RSS_KiB=383500，PID/cgroup结束=True。

启动 pre2-normal-G3-copycheck，unit=step25-pre2-normal-G3-copycheck，pairs=1；命令已保存。

结束 pre2-normal-G3-copycheck：passed=True，reason=exited，peak_threads=74，RSS_KiB=284836，PID/cgroup结束=True。

启动 pre2-normal-G4-copycheck，unit=step25-pre2-normal-G4-copycheck，pairs=1；命令已保存。

结束 pre2-normal-G4-copycheck：passed=True，reason=exited，peak_threads=75，RSS_KiB=270416，PID/cgroup结束=True。

normal四个G0配对及三种新WASM各自Copy off/on功能/S1/Gas/业务预检全部通过。

启动 normal-b1-G0-G1-p0，unit=step25-normal-b1-G0-G1-p0，pairs=2；命令已保存。

结束 normal-b1-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=386480，PID/cgroup结束=True。

启动 normal-b1-G0-G1-p1，unit=step25-normal-b1-G0-G1-p1，pairs=2；命令已保存。

结束 normal-b1-G0-G1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=392092，PID/cgroup结束=True。

启动 normal-b1-G0-G1-p2，unit=step25-normal-b1-G0-G1-p2，pairs=2；命令已保存。

结束 normal-b1-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=386248，PID/cgroup结束=True。

启动 normal-b1-G0-G2-p0，unit=step25-normal-b1-G0-G2-p0，pairs=2；命令已保存。

结束 normal-b1-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=393092，PID/cgroup结束=True。

启动 normal-b1-G0-G2-p1，unit=step25-normal-b1-G0-G2-p1，pairs=2；命令已保存。

结束 normal-b1-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=386380，PID/cgroup结束=True。

启动 normal-b1-G0-G2-p2，unit=step25-normal-b1-G0-G2-p2，pairs=2；命令已保存。

结束 normal-b1-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=409544，PID/cgroup结束=True。

启动 normal-b1-G0-G3-p0，unit=step25-normal-b1-G0-G3-p0，pairs=2；命令已保存。

结束 normal-b1-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=368320，PID/cgroup结束=True。

启动 normal-b1-G0-G3-p1，unit=step25-normal-b1-G0-G3-p1，pairs=2；命令已保存。

结束 normal-b1-G0-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=356556，PID/cgroup结束=True。

启动 normal-b1-G0-G3-p2，unit=step25-normal-b1-G0-G3-p2，pairs=2；命令已保存。

结束 normal-b1-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=346244，PID/cgroup结束=True。

启动 normal-b1-G0-G4-p0，unit=step25-normal-b1-G0-G4-p0，pairs=2；命令已保存。

结束 normal-b1-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=334868，PID/cgroup结束=True。

启动 normal-b1-G0-G4-p1，unit=step25-normal-b1-G0-G4-p1，pairs=2；命令已保存。

结束 normal-b1-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=354984，PID/cgroup结束=True。

启动 normal-b1-G0-G4-p2，unit=step25-normal-b1-G0-G4-p2，pairs=2；命令已保存。

结束 normal-b1-G0-G4-p2：passed=True，reason=exited，peak_threads=109，RSS_KiB=342200，PID/cgroup结束=True。

启动 normal-b1-G1-G2-p0，unit=step25-normal-b1-G1-G2-p0，pairs=2；命令已保存。

结束 normal-b1-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=392384，PID/cgroup结束=True。

启动 normal-b1-G1-G2-p1，unit=step25-normal-b1-G1-G2-p1，pairs=2；命令已保存。

结束 normal-b1-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=383708，PID/cgroup结束=True。

启动 normal-b1-G1-G2-p2，unit=step25-normal-b1-G1-G2-p2，pairs=2；命令已保存。

结束 normal-b1-G1-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=377608，PID/cgroup结束=True。

启动 normal-b1-G1-G3-p0，unit=step25-normal-b1-G1-G3-p0，pairs=2；命令已保存。

结束 normal-b1-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=341568，PID/cgroup结束=True。

启动 normal-b1-G1-G3-p1，unit=step25-normal-b1-G1-G3-p1，pairs=2；命令已保存。

结束 normal-b1-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=347084，PID/cgroup结束=True。

启动 normal-b1-G1-G3-p2，unit=step25-normal-b1-G1-G3-p2，pairs=2；命令已保存。

结束 normal-b1-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=336004，PID/cgroup结束=True。

启动 normal-b1-G1-G4-p0，unit=step25-normal-b1-G1-G4-p0，pairs=2；命令已保存。

结束 normal-b1-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=351952，PID/cgroup结束=True。

启动 normal-b1-G1-G4-p1，unit=step25-normal-b1-G1-G4-p1，pairs=2；命令已保存。

结束 normal-b1-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=328380，PID/cgroup结束=True。

启动 normal-b1-G1-G4-p2，unit=step25-normal-b1-G1-G4-p2，pairs=2；命令已保存。

结束 normal-b1-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=346756，PID/cgroup结束=True。

启动 normal-b1-G2-G4-p0，unit=step25-normal-b1-G2-G4-p0，pairs=2；命令已保存。

结束 normal-b1-G2-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=340496，PID/cgroup结束=True。

启动 normal-b1-G2-G4-p1，unit=step25-normal-b1-G2-G4-p1，pairs=2；命令已保存。

结束 normal-b1-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=333424，PID/cgroup结束=True。

启动 normal-b1-G2-G4-p2，unit=step25-normal-b1-G2-G4-p2，pairs=2；命令已保存。

结束 normal-b1-G2-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=327436，PID/cgroup结束=True。

正式批1 contracts=['normal']完成，所有8条直接对照各6对，逐过程日志/receipt/check/outcome已保存。

启动 normal-b2-G2-G4-p0，unit=step25-normal-b2-G2-G4-p0，pairs=2；命令已保存。

结束 normal-b2-G2-G4-p0：passed=True，reason=exited，peak_threads=109，RSS_KiB=339044，PID/cgroup结束=True。

启动 normal-b2-G2-G4-p1，unit=step25-normal-b2-G2-G4-p1，pairs=2；命令已保存。

结束 normal-b2-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=340040，PID/cgroup结束=True。

启动 normal-b2-G2-G4-p2，unit=step25-normal-b2-G2-G4-p2，pairs=2；命令已保存。

结束 normal-b2-G2-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=344252，PID/cgroup结束=True。

启动 normal-b2-G1-G4-p0，unit=step25-normal-b2-G1-G4-p0，pairs=2；命令已保存。

结束 normal-b2-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=346064，PID/cgroup结束=True。

启动 normal-b2-G1-G4-p1，unit=step25-normal-b2-G1-G4-p1，pairs=2；命令已保存。

结束 normal-b2-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=341028，PID/cgroup结束=True。

启动 normal-b2-G1-G4-p2，unit=step25-normal-b2-G1-G4-p2，pairs=2；命令已保存。

结束 normal-b2-G1-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=341172，PID/cgroup结束=True。

启动 normal-b2-G1-G3-p0，unit=step25-normal-b2-G1-G3-p0，pairs=2；命令已保存。

结束 normal-b2-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=341112，PID/cgroup结束=True。

启动 normal-b2-G1-G3-p1，unit=step25-normal-b2-G1-G3-p1，pairs=2；命令已保存。

结束 normal-b2-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=351528，PID/cgroup结束=True。

启动 normal-b2-G1-G3-p2，unit=step25-normal-b2-G1-G3-p2，pairs=2；命令已保存。

结束 normal-b2-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=335640，PID/cgroup结束=True。

启动 normal-b2-G1-G2-p0，unit=step25-normal-b2-G1-G2-p0，pairs=2；命令已保存。

结束 normal-b2-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=390260，PID/cgroup结束=True。

启动 normal-b2-G1-G2-p1，unit=step25-normal-b2-G1-G2-p1，pairs=2；命令已保存。

结束 normal-b2-G1-G2-p1：passed=True，reason=exited，peak_threads=109，RSS_KiB=396440，PID/cgroup结束=True。

启动 normal-b2-G1-G2-p2，unit=step25-normal-b2-G1-G2-p2，pairs=2；命令已保存。

结束 normal-b2-G1-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=384280，PID/cgroup结束=True。

启动 normal-b2-G0-G4-p0，unit=step25-normal-b2-G0-G4-p0，pairs=2；命令已保存。

结束 normal-b2-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=352348，PID/cgroup结束=True。

启动 normal-b2-G0-G4-p1，unit=step25-normal-b2-G0-G4-p1，pairs=2；命令已保存。

结束 normal-b2-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=365276，PID/cgroup结束=True。

启动 normal-b2-G0-G4-p2，unit=step25-normal-b2-G0-G4-p2，pairs=2；命令已保存。

结束 normal-b2-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=340392，PID/cgroup结束=True。

启动 normal-b2-G0-G3-p0，unit=step25-normal-b2-G0-G3-p0，pairs=2；命令已保存。

结束 normal-b2-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=366620，PID/cgroup结束=True。

启动 normal-b2-G0-G3-p1，unit=step25-normal-b2-G0-G3-p1，pairs=2；命令已保存。

结束 normal-b2-G0-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=354420，PID/cgroup结束=True。

启动 normal-b2-G0-G3-p2，unit=step25-normal-b2-G0-G3-p2，pairs=2；命令已保存。

结束 normal-b2-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=366060，PID/cgroup结束=True。

启动 normal-b2-G0-G2-p0，unit=step25-normal-b2-G0-G2-p0，pairs=2；命令已保存。

结束 normal-b2-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=392788，PID/cgroup结束=True。

启动 normal-b2-G0-G2-p1，unit=step25-normal-b2-G0-G2-p1，pairs=2；命令已保存。

结束 normal-b2-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=397528，PID/cgroup结束=True。

启动 normal-b2-G0-G2-p2，unit=step25-normal-b2-G0-G2-p2，pairs=2；命令已保存。

结束 normal-b2-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=400736，PID/cgroup结束=True。

启动 normal-b2-G0-G1-p0，unit=step25-normal-b2-G0-G1-p0，pairs=2；命令已保存。

结束 normal-b2-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=388428，PID/cgroup结束=True。

启动 normal-b2-G0-G1-p1，unit=step25-normal-b2-G0-G1-p1，pairs=2；命令已保存。

结束 normal-b2-G0-G1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=405264，PID/cgroup结束=True。

启动 normal-b2-G0-G1-p2，unit=step25-normal-b2-G0-G1-p2，pairs=2；命令已保存。

结束 normal-b2-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=399552，PID/cgroup结束=True。

正式批2 contracts=['normal']完成，所有8条直接对照各6对，逐过程日志/receipt/check/outcome已保存。

启动 normal-b3-G0-G1-p0，unit=step25-normal-b3-G0-G1-p0，pairs=2；命令已保存。

结束 normal-b3-G0-G1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=390424，PID/cgroup结束=True。

启动 normal-b3-G0-G1-p1，unit=step25-normal-b3-G0-G1-p1，pairs=2；命令已保存。

结束 normal-b3-G0-G1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=376812，PID/cgroup结束=True。

启动 normal-b3-G0-G1-p2，unit=step25-normal-b3-G0-G1-p2，pairs=2；命令已保存。

结束 normal-b3-G0-G1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=391308，PID/cgroup结束=True。

启动 normal-b3-G0-G2-p0，unit=step25-normal-b3-G0-G2-p0，pairs=2；命令已保存。

结束 normal-b3-G0-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=378712，PID/cgroup结束=True。

启动 normal-b3-G0-G2-p1，unit=step25-normal-b3-G0-G2-p1，pairs=2；命令已保存。

结束 normal-b3-G0-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=383776，PID/cgroup结束=True。

启动 normal-b3-G0-G2-p2，unit=step25-normal-b3-G0-G2-p2，pairs=2；命令已保存。

结束 normal-b3-G0-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=401004，PID/cgroup结束=True。

启动 normal-b3-G0-G3-p0，unit=step25-normal-b3-G0-G3-p0，pairs=2；命令已保存。

结束 normal-b3-G0-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=362528，PID/cgroup结束=True。

启动 normal-b3-G0-G3-p1，unit=step25-normal-b3-G0-G3-p1，pairs=2；命令已保存。

结束 normal-b3-G0-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=356808，PID/cgroup结束=True。

启动 normal-b3-G0-G3-p2，unit=step25-normal-b3-G0-G3-p2，pairs=2；命令已保存。

结束 normal-b3-G0-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=355972，PID/cgroup结束=True。

启动 normal-b3-G0-G4-p0，unit=step25-normal-b3-G0-G4-p0，pairs=2；命令已保存。

结束 normal-b3-G0-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=338940，PID/cgroup结束=True。

启动 normal-b3-G0-G4-p1，unit=step25-normal-b3-G0-G4-p1，pairs=2；命令已保存。

结束 normal-b3-G0-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=353900，PID/cgroup结束=True。

启动 normal-b3-G0-G4-p2，unit=step25-normal-b3-G0-G4-p2，pairs=2；命令已保存。

结束 normal-b3-G0-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=353768，PID/cgroup结束=True。

启动 normal-b3-G1-G2-p0，unit=step25-normal-b3-G1-G2-p0，pairs=2；命令已保存。

结束 normal-b3-G1-G2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=379772，PID/cgroup结束=True。

启动 normal-b3-G1-G2-p1，unit=step25-normal-b3-G1-G2-p1，pairs=2；命令已保存。

结束 normal-b3-G1-G2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=381620，PID/cgroup结束=True。

启动 normal-b3-G1-G2-p2，unit=step25-normal-b3-G1-G2-p2，pairs=2；命令已保存。

结束 normal-b3-G1-G2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=395648，PID/cgroup结束=True。

启动 normal-b3-G1-G3-p0，unit=step25-normal-b3-G1-G3-p0，pairs=2；命令已保存。

结束 normal-b3-G1-G3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=339380，PID/cgroup结束=True。

启动 normal-b3-G1-G3-p1，unit=step25-normal-b3-G1-G3-p1，pairs=2；命令已保存。

结束 normal-b3-G1-G3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=351168，PID/cgroup结束=True。

启动 normal-b3-G1-G3-p2，unit=step25-normal-b3-G1-G3-p2，pairs=2；命令已保存。

结束 normal-b3-G1-G3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=341188，PID/cgroup结束=True。

启动 normal-b3-G1-G4-p0，unit=step25-normal-b3-G1-G4-p0，pairs=2；命令已保存。

结束 normal-b3-G1-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=348356，PID/cgroup结束=True。

启动 normal-b3-G1-G4-p1，unit=step25-normal-b3-G1-G4-p1，pairs=2；命令已保存。

结束 normal-b3-G1-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=335912，PID/cgroup结束=True。

启动 normal-b3-G1-G4-p2，unit=step25-normal-b3-G1-G4-p2，pairs=2；命令已保存。

结束 normal-b3-G1-G4-p2：passed=True，reason=exited，peak_threads=109，RSS_KiB=351928，PID/cgroup结束=True。

启动 normal-b3-G2-G4-p0，unit=step25-normal-b3-G2-G4-p0，pairs=2；命令已保存。

结束 normal-b3-G2-G4-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=336012，PID/cgroup结束=True。

启动 normal-b3-G2-G4-p1，unit=step25-normal-b3-G2-G4-p1，pairs=2；命令已保存。

结束 normal-b3-G2-G4-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=333484，PID/cgroup结束=True。

启动 normal-b3-G2-G4-p2，unit=step25-normal-b3-G2-G4-p2，pairs=2；命令已保存。

结束 normal-b3-G2-G4-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=329356，PID/cgroup结束=True。

正式批3 contracts=['normal']完成，所有8条直接对照各6对，逐过程日志/receipt/check/outcome已保存。

四方法主矩阵正式288进程/576对及29次预检全部通过。补充审计发现两家族Guest Gas差别（24B compute/fact/ERC=105920/1585/15677；主矩阵120027/154/235），不能跨家族宣称原路径完全相同。将用原24B WASM单列3方法G0/G1参考（先各一预检，再3批×6对，仍最多2对/进程），不混入组合主矩阵，不重写任何Guest/Gas；其余24B原件的A/B1匹配构建仍未恢复。

启动 ref-pre-compute，unit=step25-ref-pre-compute，pairs=1；命令已保存。

结束 ref-pre-compute：passed=True，reason=exited，peak_threads=74，RSS_KiB=375144，PID/cgroup结束=True。

启动 ref-pre-fact，unit=step25-ref-pre-fact，pairs=1；命令已保存。

结束 ref-pre-fact：passed=True，reason=exited，peak_threads=74，RSS_KiB=417620，PID/cgroup结束=True。

启动 ref-pre-erc721，unit=step25-ref-pre-erc721，pairs=1；命令已保存。

结束 ref-pre-erc721：passed=True，reason=exited，peak_threads=74，RSS_KiB=424068，PID/cgroup结束=True。

启动 ref-compute-b1-p0，unit=step25-ref-compute-b1-p0，pairs=2；命令已保存。

结束 ref-compute-b1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=401088，PID/cgroup结束=True。

启动 ref-compute-b1-p1，unit=step25-ref-compute-b1-p1，pairs=2；命令已保存。

结束 ref-compute-b1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=382900，PID/cgroup结束=True。

启动 ref-compute-b1-p2，unit=step25-ref-compute-b1-p2，pairs=2；命令已保存。

结束 ref-compute-b1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=379228，PID/cgroup结束=True。

启动 ref-fact-b1-p0，unit=step25-ref-fact-b1-p0，pairs=2；命令已保存。

结束 ref-fact-b1-p0：passed=True，reason=exited，peak_threads=109，RSS_KiB=417952，PID/cgroup结束=True。

启动 ref-fact-b1-p1，unit=step25-ref-fact-b1-p1，pairs=2；命令已保存。

结束 ref-fact-b1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=412320，PID/cgroup结束=True。

启动 ref-fact-b1-p2，unit=step25-ref-fact-b1-p2，pairs=2；命令已保存。

结束 ref-fact-b1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=420576，PID/cgroup结束=True。

启动 ref-erc721-b1-p0，unit=step25-ref-erc721-b1-p0，pairs=2；命令已保存。

结束 ref-erc721-b1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=438908，PID/cgroup结束=True。

启动 ref-erc721-b1-p1，unit=step25-ref-erc721-b1-p1，pairs=2；命令已保存。

结束 ref-erc721-b1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=443520，PID/cgroup结束=True。

启动 ref-erc721-b1-p2，unit=step25-ref-erc721-b1-p2，pairs=2；命令已保存。

结束 ref-erc721-b1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=439380，PID/cgroup结束=True。

原Step24B WASM参考批1全部3方法G0/G1每组6对完成；与主矩阵分开。

启动 ref-erc721-b2-p0，unit=step25-ref-erc721-b2-p0，pairs=2；命令已保存。

结束 ref-erc721-b2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=438124，PID/cgroup结束=True。

启动 ref-erc721-b2-p1，unit=step25-ref-erc721-b2-p1，pairs=2；命令已保存。

结束 ref-erc721-b2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=454232，PID/cgroup结束=True。

启动 ref-erc721-b2-p2，unit=step25-ref-erc721-b2-p2，pairs=2；命令已保存。

结束 ref-erc721-b2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=424012，PID/cgroup结束=True。

启动 ref-fact-b2-p0，unit=step25-ref-fact-b2-p0，pairs=2；命令已保存。

结束 ref-fact-b2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=420360，PID/cgroup结束=True。

启动 ref-fact-b2-p1，unit=step25-ref-fact-b2-p1，pairs=2；命令已保存。

结束 ref-fact-b2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=423516，PID/cgroup结束=True。

启动 ref-fact-b2-p2，unit=step25-ref-fact-b2-p2，pairs=2；命令已保存。

结束 ref-fact-b2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=413588，PID/cgroup结束=True。

启动 ref-compute-b2-p0，unit=step25-ref-compute-b2-p0，pairs=2；命令已保存。

结束 ref-compute-b2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=393348，PID/cgroup结束=True。

启动 ref-compute-b2-p1，unit=step25-ref-compute-b2-p1，pairs=2；命令已保存。

结束 ref-compute-b2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=377744，PID/cgroup结束=True。

启动 ref-compute-b2-p2，unit=step25-ref-compute-b2-p2，pairs=2；命令已保存。

结束 ref-compute-b2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=397020，PID/cgroup结束=True。

原Step24B WASM参考批2全部3方法G0/G1每组6对完成；与主矩阵分开。

启动 ref-compute-b3-p0，unit=step25-ref-compute-b3-p0，pairs=2；命令已保存。

结束 ref-compute-b3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=388896，PID/cgroup结束=True。

启动 ref-compute-b3-p1，unit=step25-ref-compute-b3-p1，pairs=2；命令已保存。

结束 ref-compute-b3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=399480，PID/cgroup结束=True。

启动 ref-compute-b3-p2，unit=step25-ref-compute-b3-p2，pairs=2；命令已保存。

结束 ref-compute-b3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=387280，PID/cgroup结束=True。

启动 ref-fact-b3-p0，unit=step25-ref-fact-b3-p0，pairs=2；命令已保存。

结束 ref-fact-b3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=432300，PID/cgroup结束=True。

启动 ref-fact-b3-p1，unit=step25-ref-fact-b3-p1，pairs=2；命令已保存。

结束 ref-fact-b3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=407308，PID/cgroup结束=True。

启动 ref-fact-b3-p2，unit=step25-ref-fact-b3-p2，pairs=2；命令已保存。

结束 ref-fact-b3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=411760，PID/cgroup结束=True。

启动 ref-erc721-b3-p0，unit=step25-ref-erc721-b3-p0，pairs=2；命令已保存。

结束 ref-erc721-b3-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=432172，PID/cgroup结束=True。

启动 ref-erc721-b3-p1，unit=step25-ref-erc721-b3-p1，pairs=2；命令已保存。

结束 ref-erc721-b3-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=440304，PID/cgroup结束=True。

启动 ref-erc721-b3-p2，unit=step25-ref-erc721-b3-p2，pairs=2；命令已保存。

结束 ref-erc721-b3-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=428080，PID/cgroup结束=True。

原Step24B WASM参考批3全部3方法G0/G1每组6对完成；与主矩阵分开。

## 全部动态测试结束
四方法主矩阵完成：8条直接边×3批×6对=576对，288个正式独立进程；主预检29进程。另原24B家族三方法G0/G1参考54对/27正式进程及3预检，完全分开。
全部347进程成功、无STOP；所有退出PID/cgroup已核查，owner managed/pending清零，源WASM/Copy/Gas/Managed源hash不变。无活动step25 unit，未发生WSL重启。主机/源码审计见audit/final-state与delivery。源码冻结501200f、binary固定build2；wrapper增加参考family不改变Guest/二进制。
统计脚本analyze→write_report（PPT首先写入）已运行；主矩阵TIMING/PAIRED_EFFECTS和独立REFERENCE数据分开。核心：三短方法Copy和A增量成立，单PB不普遍成立，ERC负向；完整组合短方法优于Copy；normal增量CI跨零，不能把Fresh优化组比较当Reuse对照。
精确原24B的A/B1组合仍blocked（Guest计费构建/匹配布局产物未恢复），当前主矩阵限定Step18产物家族。Table身份、异常、长期回收、原池并发未验证。
下一步只做离线核对、报告和本分支提交/IDE同步，不再启动Guest。中断恢复先读本文件/verification/outcome；不要重跑有效label，不删原日志，不push。

## 最终交付状态
主矩阵576对/288正式进程，原24B参考54对/27正式进程；含32个预检共347进程、662个语义配对。全部通过、无资源保护触发、PID/cgroup退出、owner清零；RSS最高443.59MiB、线程109。保留每个进程2对预算，没有长期Store压测。统计/PPT已生成；正在最终离线hash核验和本分支提交，不再执行Guest。
原24B参考G0/G1：compute0.688ms、fact0.956ms（CI正），ERC0.704ms（CI跨零）。原件ERC当前Gas15981而历史15677，固定TxID格式不同，不能把跨轮差异归给Copy。本轮原件参考两侧Gas一致。主矩阵所有五组内部也一致，但跨家族不可混用；24B原件的A/B1组合仍blocked。
中断恢复下一条命令为python3 -B scripts/analyze.py && python3 -B scripts/write_report.py（仅离线）。不要再次启动正式Guest，不覆盖历史label。分支不推送。

最终离线核验完成：32条主对照及3条原件参考均每条18对/3批；统计数据hash在元数据修正前后相同；所有初始账本hash每方法/家族只有1个。PPT/RESULTS/README均标明原件组合blocked与Guest Gas家族限制。Go heap Alloc峰66.77MiB。当前准备提交完整数据并同步IDE，不再启动Guest。
