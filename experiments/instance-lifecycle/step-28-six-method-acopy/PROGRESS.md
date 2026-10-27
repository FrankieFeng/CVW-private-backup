# Step-28可恢复进度
2026-10-27。分支experiment/step28-six-method-acopy，父c8c46ee。
当前：审计/准备，未执行新Guest。全部性能只取新样本，不制作PPT、不改生产、不push。
三配置三组区块每进程先限定1块：各Store真实init+1目标=2个WASI，进程总6，保持125线程/768MiB单合约软限。不能把两个三组区块挤入125线程包络。每方法目标3批×10个三组区块，所有3条直接差从同区块计算。
buyNow拟拆为每组三个独立进程组成一个匹配区块，每进程仅一个group的3模块/3init+真实root与6callee（10WASI），沿24B buyNow既有220线程/1536MiB包络，不提高。若不能安全同源构建A或真实/异常预检失败，该方法blocked。
已有Step18 P0/A产物compute/fact/ERC哈希可恢复。exchange/identity无现成P0 A；计划从95903a3源码、同Go1.24.1/SDK0.1.3及原padding脚本构建，独立诊断验证首次arena4MiB对齐后才许可正式plain测量。P1/PB不使用。
下一步：构建来源冻结→六方法预检→通过者新三组区块正式采样。中断先查PROGRESS/state/outcome/unit，不重跑有效区块。

启动 alignment-preflight，unit=step28-alignment-preflight，pairs=1 triple or 1 split group；命令已保存。

结束 alignment-preflight：passed=True，reason=exited，peak_threads=22，RSS_KiB=371392，PID/cgroup结束=True。

准备阶段完成：Step18保存6变体校验；exchange/identity源码95903a3、Go1.24.1、原SDK及原A padding重建8个plain/probe变体。首次构建因workspace先引用identity未落盘而失败，attempt1日志保留；第二次成功，无Guest运行。host build1编译错误修正，build2成功后发现alignment registry多列ERC，修正为build3；正式冻结binary01e9c03c410a271e4f29e8eba6a59eb31ee4a98026bd96e473ff0043ad5e5e09。
对齐诊断alignment-preflight已成功，identity/exchange首次reserve均4MiB，distance0，未计入性能。原始日志保留。主实验1组三组区块/进程；buyNow分3进程直接匹配，所有6下游真实执行。
统计预声明：三配置同区块直接差，正值=左减右；P95线性插值；95%CI固定seed280027、10000次batch→block分层/聚类bootstrap，三配置整块同抽；保留全部首笔、慢样本、反向结果；只有语义/Gas/state/exit及安全均通过区块进入主统计。批次/顺序独立分层，不合并历史数据。正式计划3批每方法10块，主循环按batch→slot→六方法，六种执行排列循环平衡。
下一步命令：python3 -B scripts/experiment.py preflight；成功后formal。异常路径empty/duplicate单独进程，不混入性能。

启动 preflight-bigNumCal-b1-s01，unit=step28-preflight-bigNumCal-b1-s01，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-bigNumCal-b1-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=504032，PID/cgroup结束=True。

启动 preflight-hashCal-b1-s01，unit=step28-preflight-hashCal-b1-s01，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-hashCal-b1-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=480336，PID/cgroup结束=True。

启动 preflight-normalCal-b1-s01，unit=step28-preflight-normalCal-b1-s01，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-normalCal-b1-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=484816，PID/cgroup结束=True。

启动 preflight-fact-b1-s01，unit=step28-preflight-fact-b1-s01，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-fact-b1-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=506272，PID/cgroup结束=True。

启动 preflight-erc721-b1-s01，unit=step28-preflight-erc721-b1-s01，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-erc721-b1-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=531524，PID/cgroup结束=True。

启动 preflight-buyNow-b1-s01-G0，unit=step28-preflight-buyNow-b1-s01-G0，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-buyNow-b1-s01-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=556224，PID/cgroup结束=True。

启动 preflight-buyNow-b1-s01-G1，unit=step28-preflight-buyNow-b1-s01-G1，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-buyNow-b1-s01-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=524464，PID/cgroup结束=True。

启动 preflight-buyNow-b1-s01-G2，unit=step28-preflight-buyNow-b1-s01-G2，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-buyNow-b1-s01-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=513092，PID/cgroup结束=True。

启动 exception-empty-G0，unit=step28-exception-empty-G0，pairs=1 triple or 1 split group；命令已保存。

结束 exception-empty-G0：passed=True，reason=exited，peak_threads=74，RSS_KiB=519612，PID/cgroup结束=True。

启动 exception-empty-G1，unit=step28-exception-empty-G1，pairs=1 triple or 1 split group；命令已保存。

结束 exception-empty-G1：passed=True，reason=exited，peak_threads=74，RSS_KiB=504484，PID/cgroup结束=True。

启动 exception-empty-G2，unit=step28-exception-empty-G2，pairs=1 triple or 1 split group；命令已保存。

结束 exception-empty-G2：passed=True，reason=exited，peak_threads=74，RSS_KiB=488688，PID/cgroup结束=True。

启动 exception-duplicate-G0，unit=step28-exception-duplicate-G0，pairs=1 triple or 1 split group；命令已保存。

结束 exception-duplicate-G0：passed=True，reason=exited，peak_threads=142，RSS_KiB=561664，PID/cgroup结束=True。

启动 exception-duplicate-G1，unit=step28-exception-duplicate-G1，pairs=1 triple or 1 split group；命令已保存。

结束 exception-duplicate-G1：passed=True，reason=exited，peak_threads=142，RSS_KiB=541180，PID/cgroup结束=True。

启动 exception-duplicate-G2，unit=step28-exception-duplicate-G2，pairs=1 triple or 1 split group；命令已保存。

结束 exception-duplicate-G2：passed=True，reason=exited，peak_threads=142，RSS_KiB=529824，PID/cgroup结束=True。

启动 formal-bigNumCal-b1-s01，unit=step28-formal-bigNumCal-b1-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b1-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=492052，PID/cgroup结束=True。

启动 formal-hashCal-b1-s01，unit=step28-formal-hashCal-b1-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b1-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=475540，PID/cgroup结束=True。

启动 formal-normalCal-b1-s01，unit=step28-formal-normalCal-b1-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b1-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=486540，PID/cgroup结束=True。

启动 formal-fact-b1-s01，unit=step28-formal-fact-b1-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b1-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=504956，PID/cgroup结束=True。

启动 formal-erc721-b1-s01，unit=step28-formal-erc721-b1-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b1-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=528488，PID/cgroup结束=True。

启动 formal-buyNow-b1-s01-G0，unit=step28-formal-buyNow-b1-s01-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s01-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=570200，PID/cgroup结束=True。

启动 formal-buyNow-b1-s01-G1，unit=step28-formal-buyNow-b1-s01-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s01-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=533348，PID/cgroup结束=True。

启动 formal-buyNow-b1-s01-G2，unit=step28-formal-buyNow-b1-s01-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s01-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=528308，PID/cgroup结束=True。

启动 formal-bigNumCal-b1-s02，unit=step28-formal-bigNumCal-b1-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b1-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=491772，PID/cgroup结束=True。

启动 formal-hashCal-b1-s02，unit=step28-formal-hashCal-b1-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b1-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=485924，PID/cgroup结束=True。

启动 formal-normalCal-b1-s02，unit=step28-formal-normalCal-b1-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b1-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=493048，PID/cgroup结束=True。

启动 formal-fact-b1-s02，unit=step28-formal-fact-b1-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b1-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=507820，PID/cgroup结束=True。

启动 formal-erc721-b1-s02，unit=step28-formal-erc721-b1-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b1-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=541148，PID/cgroup结束=True。

启动 formal-buyNow-b1-s02-G0，unit=step28-formal-buyNow-b1-s02-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s02-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=567988，PID/cgroup结束=True。

启动 formal-buyNow-b1-s02-G2，unit=step28-formal-buyNow-b1-s02-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s02-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=508504，PID/cgroup结束=True。

启动 formal-buyNow-b1-s02-G1，unit=step28-formal-buyNow-b1-s02-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s02-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=522228，PID/cgroup结束=True。

启动 formal-bigNumCal-b1-s03，unit=step28-formal-bigNumCal-b1-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b1-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=494676，PID/cgroup结束=True。

启动 formal-hashCal-b1-s03，unit=step28-formal-hashCal-b1-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b1-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=496016，PID/cgroup结束=True。

启动 formal-normalCal-b1-s03，unit=step28-formal-normalCal-b1-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b1-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=497744，PID/cgroup结束=True。

启动 formal-fact-b1-s03，unit=step28-formal-fact-b1-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b1-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=497324，PID/cgroup结束=True。

启动 formal-erc721-b1-s03，unit=step28-formal-erc721-b1-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b1-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=535792，PID/cgroup结束=True。

启动 formal-buyNow-b1-s03-G1，unit=step28-formal-buyNow-b1-s03-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s03-G1：passed=True，reason=exited，peak_threads=177，RSS_KiB=537516，PID/cgroup结束=True。

启动 formal-buyNow-b1-s03-G0，unit=step28-formal-buyNow-b1-s03-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s03-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=572016，PID/cgroup结束=True。

启动 formal-buyNow-b1-s03-G2，unit=step28-formal-buyNow-b1-s03-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s03-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=517168，PID/cgroup结束=True。

启动 formal-bigNumCal-b1-s04，unit=step28-formal-bigNumCal-b1-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b1-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=494292，PID/cgroup结束=True。

启动 formal-hashCal-b1-s04，unit=step28-formal-hashCal-b1-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b1-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=496856，PID/cgroup结束=True。

启动 formal-normalCal-b1-s04，unit=step28-formal-normalCal-b1-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b1-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=498080，PID/cgroup结束=True。

启动 formal-fact-b1-s04，unit=step28-formal-fact-b1-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b1-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=517840，PID/cgroup结束=True。

启动 formal-erc721-b1-s04，unit=step28-formal-erc721-b1-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b1-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=538936，PID/cgroup结束=True。

启动 formal-buyNow-b1-s04-G1，unit=step28-formal-buyNow-b1-s04-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s04-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=524244，PID/cgroup结束=True。

启动 formal-buyNow-b1-s04-G2，unit=step28-formal-buyNow-b1-s04-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s04-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=550672，PID/cgroup结束=True。

启动 formal-buyNow-b1-s04-G0，unit=step28-formal-buyNow-b1-s04-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s04-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=572852，PID/cgroup结束=True。

启动 formal-bigNumCal-b1-s05，unit=step28-formal-bigNumCal-b1-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b1-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=482680，PID/cgroup结束=True。

启动 formal-hashCal-b1-s05，unit=step28-formal-hashCal-b1-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b1-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=499656，PID/cgroup结束=True。

启动 formal-normalCal-b1-s05，unit=step28-formal-normalCal-b1-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b1-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=479104，PID/cgroup结束=True。

启动 formal-fact-b1-s05，unit=step28-formal-fact-b1-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b1-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=498992，PID/cgroup结束=True。

启动 formal-erc721-b1-s05，unit=step28-formal-erc721-b1-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b1-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=550824，PID/cgroup结束=True。

启动 formal-buyNow-b1-s05-G2，unit=step28-formal-buyNow-b1-s05-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s05-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=518460，PID/cgroup结束=True。

启动 formal-buyNow-b1-s05-G0，unit=step28-formal-buyNow-b1-s05-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s05-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=556172，PID/cgroup结束=True。

启动 formal-buyNow-b1-s05-G1，unit=step28-formal-buyNow-b1-s05-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s05-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=530048，PID/cgroup结束=True。

启动 formal-bigNumCal-b1-s06，unit=step28-formal-bigNumCal-b1-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b1-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=498800，PID/cgroup结束=True。

启动 formal-hashCal-b1-s06，unit=step28-formal-hashCal-b1-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b1-s06：passed=True，reason=exited，peak_threads=109，RSS_KiB=494612，PID/cgroup结束=True。

启动 formal-normalCal-b1-s06，unit=step28-formal-normalCal-b1-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b1-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=490360，PID/cgroup结束=True。

启动 formal-fact-b1-s06，unit=step28-formal-fact-b1-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b1-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=524764，PID/cgroup结束=True。

启动 formal-erc721-b1-s06，unit=step28-formal-erc721-b1-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b1-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=538760，PID/cgroup结束=True。

启动 formal-buyNow-b1-s06-G2，unit=step28-formal-buyNow-b1-s06-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s06-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=522144，PID/cgroup结束=True。

启动 formal-buyNow-b1-s06-G1，unit=step28-formal-buyNow-b1-s06-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s06-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=539168，PID/cgroup结束=True。

启动 formal-buyNow-b1-s06-G0，unit=step28-formal-buyNow-b1-s06-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s06-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=559552，PID/cgroup结束=True。

启动 formal-bigNumCal-b1-s07，unit=step28-formal-bigNumCal-b1-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b1-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=490280，PID/cgroup结束=True。

启动 formal-hashCal-b1-s07，unit=step28-formal-hashCal-b1-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b1-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=481560，PID/cgroup结束=True。

启动 formal-normalCal-b1-s07，unit=step28-formal-normalCal-b1-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b1-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=479792，PID/cgroup结束=True。

启动 formal-fact-b1-s07，unit=step28-formal-fact-b1-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b1-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=518620，PID/cgroup结束=True。

启动 formal-erc721-b1-s07，unit=step28-formal-erc721-b1-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b1-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=538708，PID/cgroup结束=True。

启动 formal-buyNow-b1-s07-G0，unit=step28-formal-buyNow-b1-s07-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s07-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=568064，PID/cgroup结束=True。

启动 formal-buyNow-b1-s07-G1，unit=step28-formal-buyNow-b1-s07-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s07-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=517484，PID/cgroup结束=True。

启动 formal-buyNow-b1-s07-G2，unit=step28-formal-buyNow-b1-s07-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s07-G2：passed=True，reason=exited，peak_threads=177，RSS_KiB=536412，PID/cgroup结束=True。

启动 formal-bigNumCal-b1-s08，unit=step28-formal-bigNumCal-b1-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b1-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=486448，PID/cgroup结束=True。

启动 formal-hashCal-b1-s08，unit=step28-formal-hashCal-b1-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b1-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=490300，PID/cgroup结束=True。

启动 formal-normalCal-b1-s08，unit=step28-formal-normalCal-b1-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b1-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=488280，PID/cgroup结束=True。

启动 formal-fact-b1-s08，unit=step28-formal-fact-b1-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b1-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=496584，PID/cgroup结束=True。

启动 formal-erc721-b1-s08，unit=step28-formal-erc721-b1-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b1-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=530424，PID/cgroup结束=True。

启动 formal-buyNow-b1-s08-G0，unit=step28-formal-buyNow-b1-s08-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s08-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=574416，PID/cgroup结束=True。

启动 formal-buyNow-b1-s08-G2，unit=step28-formal-buyNow-b1-s08-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s08-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=550564，PID/cgroup结束=True。

启动 formal-buyNow-b1-s08-G1，unit=step28-formal-buyNow-b1-s08-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s08-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=548856，PID/cgroup结束=True。

启动 formal-bigNumCal-b1-s09，unit=step28-formal-bigNumCal-b1-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b1-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=493424，PID/cgroup结束=True。

启动 formal-hashCal-b1-s09，unit=step28-formal-hashCal-b1-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b1-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=467400，PID/cgroup结束=True。

启动 formal-normalCal-b1-s09，unit=step28-formal-normalCal-b1-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b1-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=485744，PID/cgroup结束=True。

启动 formal-fact-b1-s09，unit=step28-formal-fact-b1-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b1-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=517936，PID/cgroup结束=True。

启动 formal-erc721-b1-s09，unit=step28-formal-erc721-b1-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b1-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=539496，PID/cgroup结束=True。

启动 formal-buyNow-b1-s09-G1，unit=step28-formal-buyNow-b1-s09-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s09-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=545680，PID/cgroup结束=True。

启动 formal-buyNow-b1-s09-G0，unit=step28-formal-buyNow-b1-s09-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s09-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=571304，PID/cgroup结束=True。

启动 formal-buyNow-b1-s09-G2，unit=step28-formal-buyNow-b1-s09-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s09-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=527008，PID/cgroup结束=True。

启动 formal-bigNumCal-b1-s10，unit=step28-formal-bigNumCal-b1-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b1-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=499792，PID/cgroup结束=True。

启动 formal-hashCal-b1-s10，unit=step28-formal-hashCal-b1-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b1-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=485280，PID/cgroup结束=True。

启动 formal-normalCal-b1-s10，unit=step28-formal-normalCal-b1-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b1-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=476172，PID/cgroup结束=True。

启动 formal-fact-b1-s10，unit=step28-formal-fact-b1-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b1-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=505720，PID/cgroup结束=True。

启动 formal-erc721-b1-s10，unit=step28-formal-erc721-b1-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b1-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=534164，PID/cgroup结束=True。

启动 formal-buyNow-b1-s10-G1，unit=step28-formal-buyNow-b1-s10-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s10-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=516428，PID/cgroup结束=True。

启动 formal-buyNow-b1-s10-G2，unit=step28-formal-buyNow-b1-s10-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s10-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=513664，PID/cgroup结束=True。

启动 formal-buyNow-b1-s10-G0，unit=step28-formal-buyNow-b1-s10-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b1-s10-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=565832，PID/cgroup结束=True。

启动 formal-bigNumCal-b2-s01，unit=step28-formal-bigNumCal-b2-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b2-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=496704，PID/cgroup结束=True。

启动 formal-hashCal-b2-s01，unit=step28-formal-hashCal-b2-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b2-s01：passed=True，reason=exited，peak_threads=109，RSS_KiB=467896，PID/cgroup结束=True。

启动 formal-normalCal-b2-s01，unit=step28-formal-normalCal-b2-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b2-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=487140，PID/cgroup结束=True。

启动 formal-fact-b2-s01，unit=step28-formal-fact-b2-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b2-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=501756，PID/cgroup结束=True。

启动 formal-erc721-b2-s01，unit=step28-formal-erc721-b2-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b2-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=522500，PID/cgroup结束=True。

启动 formal-buyNow-b2-s01-G2，unit=step28-formal-buyNow-b2-s01-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s01-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=510176，PID/cgroup结束=True。

启动 formal-buyNow-b2-s01-G0，unit=step28-formal-buyNow-b2-s01-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s01-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=552176，PID/cgroup结束=True。

启动 formal-buyNow-b2-s01-G1，unit=step28-formal-buyNow-b2-s01-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s01-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=539180，PID/cgroup结束=True。

启动 formal-bigNumCal-b2-s02，unit=step28-formal-bigNumCal-b2-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b2-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=500108，PID/cgroup结束=True。

启动 formal-hashCal-b2-s02，unit=step28-formal-hashCal-b2-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b2-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=480100，PID/cgroup结束=True。

启动 formal-normalCal-b2-s02，unit=step28-formal-normalCal-b2-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b2-s02：passed=True，reason=exited，peak_threads=109，RSS_KiB=500788，PID/cgroup结束=True。

启动 formal-fact-b2-s02，unit=step28-formal-fact-b2-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b2-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=513604，PID/cgroup结束=True。

启动 formal-erc721-b2-s02，unit=step28-formal-erc721-b2-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b2-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=539000，PID/cgroup结束=True。

启动 formal-buyNow-b2-s02-G2，unit=step28-formal-buyNow-b2-s02-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s02-G2：passed=True，reason=exited，peak_threads=177，RSS_KiB=543880，PID/cgroup结束=True。

启动 formal-buyNow-b2-s02-G1，unit=step28-formal-buyNow-b2-s02-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s02-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=523324，PID/cgroup结束=True。

启动 formal-buyNow-b2-s02-G0，unit=step28-formal-buyNow-b2-s02-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s02-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=560440，PID/cgroup结束=True。

启动 formal-bigNumCal-b2-s03，unit=step28-formal-bigNumCal-b2-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b2-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=481884，PID/cgroup结束=True。

启动 formal-hashCal-b2-s03，unit=step28-formal-hashCal-b2-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b2-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=492016，PID/cgroup结束=True。

启动 formal-normalCal-b2-s03，unit=step28-formal-normalCal-b2-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b2-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=480288，PID/cgroup结束=True。

启动 formal-fact-b2-s03，unit=step28-formal-fact-b2-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b2-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=506412，PID/cgroup结束=True。

启动 formal-erc721-b2-s03，unit=step28-formal-erc721-b2-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b2-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=544984，PID/cgroup结束=True。

启动 formal-buyNow-b2-s03-G0，unit=step28-formal-buyNow-b2-s03-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s03-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=578404，PID/cgroup结束=True。

启动 formal-buyNow-b2-s03-G1，unit=step28-formal-buyNow-b2-s03-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s03-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=534516，PID/cgroup结束=True。

启动 formal-buyNow-b2-s03-G2，unit=step28-formal-buyNow-b2-s03-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s03-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=506520，PID/cgroup结束=True。

启动 formal-bigNumCal-b2-s04，unit=step28-formal-bigNumCal-b2-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b2-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=485344，PID/cgroup结束=True。

启动 formal-hashCal-b2-s04，unit=step28-formal-hashCal-b2-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b2-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=482704，PID/cgroup结束=True。

启动 formal-normalCal-b2-s04，unit=step28-formal-normalCal-b2-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b2-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=483052，PID/cgroup结束=True。

启动 formal-fact-b2-s04，unit=step28-formal-fact-b2-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b2-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=510452，PID/cgroup结束=True。

启动 formal-erc721-b2-s04，unit=step28-formal-erc721-b2-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b2-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=535988，PID/cgroup结束=True。

启动 formal-buyNow-b2-s04-G0，unit=step28-formal-buyNow-b2-s04-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s04-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=556644，PID/cgroup结束=True。

启动 formal-buyNow-b2-s04-G2，unit=step28-formal-buyNow-b2-s04-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s04-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=514212，PID/cgroup结束=True。

启动 formal-buyNow-b2-s04-G1，unit=step28-formal-buyNow-b2-s04-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s04-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=545696，PID/cgroup结束=True。

启动 formal-bigNumCal-b2-s05，unit=step28-formal-bigNumCal-b2-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b2-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=496240，PID/cgroup结束=True。

启动 formal-hashCal-b2-s05，unit=step28-formal-hashCal-b2-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b2-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=482504，PID/cgroup结束=True。

启动 formal-normalCal-b2-s05，unit=step28-formal-normalCal-b2-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b2-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=478824，PID/cgroup结束=True。

启动 formal-fact-b2-s05，unit=step28-formal-fact-b2-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b2-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=507700，PID/cgroup结束=True。

启动 formal-erc721-b2-s05，unit=step28-formal-erc721-b2-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b2-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=530152，PID/cgroup结束=True。

启动 formal-buyNow-b2-s05-G1，unit=step28-formal-buyNow-b2-s05-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s05-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=533732，PID/cgroup结束=True。

启动 formal-buyNow-b2-s05-G0，unit=step28-formal-buyNow-b2-s05-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s05-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=559584，PID/cgroup结束=True。

启动 formal-buyNow-b2-s05-G2，unit=step28-formal-buyNow-b2-s05-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s05-G2：passed=True，reason=exited，peak_threads=177，RSS_KiB=519376，PID/cgroup结束=True。

启动 formal-bigNumCal-b2-s06，unit=step28-formal-bigNumCal-b2-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b2-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=487500，PID/cgroup结束=True。

启动 formal-hashCal-b2-s06，unit=step28-formal-hashCal-b2-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b2-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=506248，PID/cgroup结束=True。

启动 formal-normalCal-b2-s06，unit=step28-formal-normalCal-b2-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b2-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=493092，PID/cgroup结束=True。

启动 formal-fact-b2-s06，unit=step28-formal-fact-b2-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b2-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=505628，PID/cgroup结束=True。

启动 formal-erc721-b2-s06，unit=step28-formal-erc721-b2-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b2-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=531508，PID/cgroup结束=True。

启动 formal-buyNow-b2-s06-G1，unit=step28-formal-buyNow-b2-s06-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s06-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=530600，PID/cgroup结束=True。

启动 formal-buyNow-b2-s06-G2，unit=step28-formal-buyNow-b2-s06-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s06-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=528492，PID/cgroup结束=True。

启动 formal-buyNow-b2-s06-G0，unit=step28-formal-buyNow-b2-s06-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s06-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=572764，PID/cgroup结束=True。

启动 formal-bigNumCal-b2-s07，unit=step28-formal-bigNumCal-b2-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b2-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=503472，PID/cgroup结束=True。

启动 formal-hashCal-b2-s07，unit=step28-formal-hashCal-b2-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b2-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=487452，PID/cgroup结束=True。

启动 formal-normalCal-b2-s07，unit=step28-formal-normalCal-b2-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b2-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=482152，PID/cgroup结束=True。

启动 formal-fact-b2-s07，unit=step28-formal-fact-b2-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b2-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=516040，PID/cgroup结束=True。

启动 formal-erc721-b2-s07，unit=step28-formal-erc721-b2-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b2-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=542400，PID/cgroup结束=True。

启动 formal-buyNow-b2-s07-G2，unit=step28-formal-buyNow-b2-s07-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s07-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=519108，PID/cgroup结束=True。

启动 formal-buyNow-b2-s07-G0，unit=step28-formal-buyNow-b2-s07-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s07-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=553132，PID/cgroup结束=True。

启动 formal-buyNow-b2-s07-G1，unit=step28-formal-buyNow-b2-s07-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s07-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=533132，PID/cgroup结束=True。

启动 formal-bigNumCal-b2-s08，unit=step28-formal-bigNumCal-b2-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b2-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=496004，PID/cgroup结束=True。

启动 formal-hashCal-b2-s08，unit=step28-formal-hashCal-b2-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b2-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=494384，PID/cgroup结束=True。

启动 formal-normalCal-b2-s08，unit=step28-formal-normalCal-b2-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b2-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=481284，PID/cgroup结束=True。

启动 formal-fact-b2-s08，unit=step28-formal-fact-b2-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b2-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=510700，PID/cgroup结束=True。

启动 formal-erc721-b2-s08，unit=step28-formal-erc721-b2-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b2-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=533372，PID/cgroup结束=True。

启动 formal-buyNow-b2-s08-G2，unit=step28-formal-buyNow-b2-s08-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s08-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=528160，PID/cgroup结束=True。

启动 formal-buyNow-b2-s08-G1，unit=step28-formal-buyNow-b2-s08-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s08-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=556360，PID/cgroup结束=True。

启动 formal-buyNow-b2-s08-G0，unit=step28-formal-buyNow-b2-s08-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s08-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=557608，PID/cgroup结束=True。

启动 formal-bigNumCal-b2-s09，unit=step28-formal-bigNumCal-b2-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b2-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=495828，PID/cgroup结束=True。

启动 formal-hashCal-b2-s09，unit=step28-formal-hashCal-b2-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b2-s09：passed=True，reason=exited，peak_threads=109，RSS_KiB=479896，PID/cgroup结束=True。

启动 formal-normalCal-b2-s09，unit=step28-formal-normalCal-b2-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b2-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=497860，PID/cgroup结束=True。

启动 formal-fact-b2-s09，unit=step28-formal-fact-b2-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b2-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=504532，PID/cgroup结束=True。

启动 formal-erc721-b2-s09，unit=step28-formal-erc721-b2-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b2-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=526036，PID/cgroup结束=True。

启动 formal-buyNow-b2-s09-G0，unit=step28-formal-buyNow-b2-s09-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s09-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=545668，PID/cgroup结束=True。

启动 formal-buyNow-b2-s09-G1，unit=step28-formal-buyNow-b2-s09-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s09-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=538156，PID/cgroup结束=True。

启动 formal-buyNow-b2-s09-G2，unit=step28-formal-buyNow-b2-s09-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s09-G2：passed=True，reason=exited，peak_threads=177，RSS_KiB=525100，PID/cgroup结束=True。

启动 formal-bigNumCal-b2-s10，unit=step28-formal-bigNumCal-b2-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b2-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=502576，PID/cgroup结束=True。

启动 formal-hashCal-b2-s10，unit=step28-formal-hashCal-b2-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b2-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=483392，PID/cgroup结束=True。

启动 formal-normalCal-b2-s10，unit=step28-formal-normalCal-b2-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b2-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=487100，PID/cgroup结束=True。

启动 formal-fact-b2-s10，unit=step28-formal-fact-b2-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b2-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=516816，PID/cgroup结束=True。

启动 formal-erc721-b2-s10，unit=step28-formal-erc721-b2-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b2-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=530940，PID/cgroup结束=True。

启动 formal-buyNow-b2-s10-G0，unit=step28-formal-buyNow-b2-s10-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s10-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=570408，PID/cgroup结束=True。

启动 formal-buyNow-b2-s10-G2，unit=step28-formal-buyNow-b2-s10-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s10-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=515216，PID/cgroup结束=True。

启动 formal-buyNow-b2-s10-G1，unit=step28-formal-buyNow-b2-s10-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b2-s10-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=528684，PID/cgroup结束=True。

启动 formal-bigNumCal-b3-s01，unit=step28-formal-bigNumCal-b3-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b3-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=482168，PID/cgroup结束=True。

启动 formal-hashCal-b3-s01，unit=step28-formal-hashCal-b3-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b3-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=480172，PID/cgroup结束=True。

启动 formal-normalCal-b3-s01，unit=step28-formal-normalCal-b3-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b3-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=485452，PID/cgroup结束=True。

启动 formal-fact-b3-s01，unit=step28-formal-fact-b3-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b3-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=514916，PID/cgroup结束=True。

启动 formal-erc721-b3-s01，unit=step28-formal-erc721-b3-s01，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b3-s01：passed=True，reason=exited，peak_threads=108，RSS_KiB=521604，PID/cgroup结束=True。

启动 formal-buyNow-b3-s01-G1，unit=step28-formal-buyNow-b3-s01-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s01-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=530340，PID/cgroup结束=True。

启动 formal-buyNow-b3-s01-G0，unit=step28-formal-buyNow-b3-s01-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s01-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=567464，PID/cgroup结束=True。

启动 formal-buyNow-b3-s01-G2，unit=step28-formal-buyNow-b3-s01-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s01-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=513208，PID/cgroup结束=True。

启动 formal-bigNumCal-b3-s02，unit=step28-formal-bigNumCal-b3-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b3-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=492976，PID/cgroup结束=True。

启动 formal-hashCal-b3-s02，unit=step28-formal-hashCal-b3-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b3-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=502200，PID/cgroup结束=True。

启动 formal-normalCal-b3-s02，unit=step28-formal-normalCal-b3-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b3-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=477096，PID/cgroup结束=True。

启动 formal-fact-b3-s02，unit=step28-formal-fact-b3-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b3-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=519368，PID/cgroup结束=True。

启动 formal-erc721-b3-s02，unit=step28-formal-erc721-b3-s02，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b3-s02：passed=True，reason=exited，peak_threads=108，RSS_KiB=538484，PID/cgroup结束=True。

启动 formal-buyNow-b3-s02-G1，unit=step28-formal-buyNow-b3-s02-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s02-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=541532，PID/cgroup结束=True。

启动 formal-buyNow-b3-s02-G2，unit=step28-formal-buyNow-b3-s02-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s02-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=538640，PID/cgroup结束=True。

启动 formal-buyNow-b3-s02-G0，unit=step28-formal-buyNow-b3-s02-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s02-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=572248，PID/cgroup结束=True。

启动 formal-bigNumCal-b3-s03，unit=step28-formal-bigNumCal-b3-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b3-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=503872，PID/cgroup结束=True。

启动 formal-hashCal-b3-s03，unit=step28-formal-hashCal-b3-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b3-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=491256，PID/cgroup结束=True。

启动 formal-normalCal-b3-s03，unit=step28-formal-normalCal-b3-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b3-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=489600，PID/cgroup结束=True。

启动 formal-fact-b3-s03，unit=step28-formal-fact-b3-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b3-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=511564，PID/cgroup结束=True。

启动 formal-erc721-b3-s03，unit=step28-formal-erc721-b3-s03，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b3-s03：passed=True，reason=exited，peak_threads=108，RSS_KiB=528216，PID/cgroup结束=True。

启动 formal-buyNow-b3-s03-G2，unit=step28-formal-buyNow-b3-s03-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s03-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=515800，PID/cgroup结束=True。

启动 formal-buyNow-b3-s03-G0，unit=step28-formal-buyNow-b3-s03-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s03-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=565252，PID/cgroup结束=True。

启动 formal-buyNow-b3-s03-G1，unit=step28-formal-buyNow-b3-s03-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s03-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=537628，PID/cgroup结束=True。

启动 formal-bigNumCal-b3-s04，unit=step28-formal-bigNumCal-b3-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b3-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=502872，PID/cgroup结束=True。

启动 formal-hashCal-b3-s04，unit=step28-formal-hashCal-b3-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b3-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=497828，PID/cgroup结束=True。

启动 formal-normalCal-b3-s04，unit=step28-formal-normalCal-b3-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b3-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=472180，PID/cgroup结束=True。

启动 formal-fact-b3-s04，unit=step28-formal-fact-b3-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b3-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=516436，PID/cgroup结束=True。

启动 formal-erc721-b3-s04，unit=step28-formal-erc721-b3-s04，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b3-s04：passed=True，reason=exited，peak_threads=108，RSS_KiB=541924，PID/cgroup结束=True。

启动 formal-buyNow-b3-s04-G2，unit=step28-formal-buyNow-b3-s04-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s04-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=504424，PID/cgroup结束=True。

启动 formal-buyNow-b3-s04-G1，unit=step28-formal-buyNow-b3-s04-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s04-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=527692，PID/cgroup结束=True。

启动 formal-buyNow-b3-s04-G0，unit=step28-formal-buyNow-b3-s04-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s04-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=570068，PID/cgroup结束=True。

启动 formal-bigNumCal-b3-s05，unit=step28-formal-bigNumCal-b3-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b3-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=495408，PID/cgroup结束=True。

启动 formal-hashCal-b3-s05，unit=step28-formal-hashCal-b3-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b3-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=495596，PID/cgroup结束=True。

启动 formal-normalCal-b3-s05，unit=step28-formal-normalCal-b3-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b3-s05：passed=True，reason=exited，peak_threads=109，RSS_KiB=486048，PID/cgroup结束=True。

启动 formal-fact-b3-s05，unit=step28-formal-fact-b3-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b3-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=506856，PID/cgroup结束=True。

启动 formal-erc721-b3-s05，unit=step28-formal-erc721-b3-s05，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b3-s05：passed=True，reason=exited，peak_threads=108，RSS_KiB=528672，PID/cgroup结束=True。

启动 formal-buyNow-b3-s05-G0，unit=step28-formal-buyNow-b3-s05-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s05-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=563780，PID/cgroup结束=True。

启动 formal-buyNow-b3-s05-G1，unit=step28-formal-buyNow-b3-s05-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s05-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=529580，PID/cgroup结束=True。

启动 formal-buyNow-b3-s05-G2，unit=step28-formal-buyNow-b3-s05-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s05-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=553148，PID/cgroup结束=True。

启动 formal-bigNumCal-b3-s06，unit=step28-formal-bigNumCal-b3-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b3-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=493524，PID/cgroup结束=True。

启动 formal-hashCal-b3-s06，unit=step28-formal-hashCal-b3-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b3-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=478076，PID/cgroup结束=True。

启动 formal-normalCal-b3-s06，unit=step28-formal-normalCal-b3-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b3-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=496000，PID/cgroup结束=True。

启动 formal-fact-b3-s06，unit=step28-formal-fact-b3-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b3-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=511864，PID/cgroup结束=True。

启动 formal-erc721-b3-s06，unit=step28-formal-erc721-b3-s06，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b3-s06：passed=True，reason=exited，peak_threads=108，RSS_KiB=536620，PID/cgroup结束=True。

启动 formal-buyNow-b3-s06-G0，unit=step28-formal-buyNow-b3-s06-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s06-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=555804，PID/cgroup结束=True。

启动 formal-buyNow-b3-s06-G2，unit=step28-formal-buyNow-b3-s06-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s06-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=524564，PID/cgroup结束=True。

启动 formal-buyNow-b3-s06-G1，unit=step28-formal-buyNow-b3-s06-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s06-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=535232，PID/cgroup结束=True。

启动 formal-bigNumCal-b3-s07，unit=step28-formal-bigNumCal-b3-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b3-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=489368，PID/cgroup结束=True。

启动 formal-hashCal-b3-s07，unit=step28-formal-hashCal-b3-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b3-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=486612，PID/cgroup结束=True。

启动 formal-normalCal-b3-s07，unit=step28-formal-normalCal-b3-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b3-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=492408，PID/cgroup结束=True。

启动 formal-fact-b3-s07，unit=step28-formal-fact-b3-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b3-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=502148，PID/cgroup结束=True。

启动 formal-erc721-b3-s07，unit=step28-formal-erc721-b3-s07，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b3-s07：passed=True，reason=exited，peak_threads=108，RSS_KiB=534156，PID/cgroup结束=True。

启动 formal-buyNow-b3-s07-G1，unit=step28-formal-buyNow-b3-s07-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s07-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=523592，PID/cgroup结束=True。

启动 formal-buyNow-b3-s07-G0，unit=step28-formal-buyNow-b3-s07-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s07-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=569864，PID/cgroup结束=True。

启动 formal-buyNow-b3-s07-G2，unit=step28-formal-buyNow-b3-s07-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s07-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=519992，PID/cgroup结束=True。

启动 formal-bigNumCal-b3-s08，unit=step28-formal-bigNumCal-b3-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b3-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=495356，PID/cgroup结束=True。

启动 formal-hashCal-b3-s08，unit=step28-formal-hashCal-b3-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b3-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=499360，PID/cgroup结束=True。

启动 formal-normalCal-b3-s08，unit=step28-formal-normalCal-b3-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b3-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=487140，PID/cgroup结束=True。

启动 formal-fact-b3-s08，unit=step28-formal-fact-b3-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b3-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=505256，PID/cgroup结束=True。

启动 formal-erc721-b3-s08，unit=step28-formal-erc721-b3-s08，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b3-s08：passed=True，reason=exited，peak_threads=108，RSS_KiB=529264，PID/cgroup结束=True。

启动 formal-buyNow-b3-s08-G1，unit=step28-formal-buyNow-b3-s08-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s08-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=532024，PID/cgroup结束=True。

启动 formal-buyNow-b3-s08-G2，unit=step28-formal-buyNow-b3-s08-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s08-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=526268，PID/cgroup结束=True。

启动 formal-buyNow-b3-s08-G0，unit=step28-formal-buyNow-b3-s08-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s08-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=579356，PID/cgroup结束=True。

启动 formal-bigNumCal-b3-s09，unit=step28-formal-bigNumCal-b3-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b3-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=508552，PID/cgroup结束=True。

启动 formal-hashCal-b3-s09，unit=step28-formal-hashCal-b3-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b3-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=482292，PID/cgroup结束=True。

启动 formal-normalCal-b3-s09，unit=step28-formal-normalCal-b3-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b3-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=489204，PID/cgroup结束=True。

启动 formal-fact-b3-s09，unit=step28-formal-fact-b3-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b3-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=513724，PID/cgroup结束=True。

启动 formal-erc721-b3-s09，unit=step28-formal-erc721-b3-s09，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b3-s09：passed=True，reason=exited，peak_threads=108，RSS_KiB=537784，PID/cgroup结束=True。

启动 formal-buyNow-b3-s09-G2，unit=step28-formal-buyNow-b3-s09-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s09-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=516896，PID/cgroup结束=True。

启动 formal-buyNow-b3-s09-G0，unit=step28-formal-buyNow-b3-s09-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s09-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=581456，PID/cgroup结束=True。

启动 formal-buyNow-b3-s09-G1，unit=step28-formal-buyNow-b3-s09-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s09-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=512952，PID/cgroup结束=True。

启动 formal-bigNumCal-b3-s10，unit=step28-formal-bigNumCal-b3-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-bigNumCal-b3-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=492072，PID/cgroup结束=True。

启动 formal-hashCal-b3-s10，unit=step28-formal-hashCal-b3-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-hashCal-b3-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=498248，PID/cgroup结束=True。

启动 formal-normalCal-b3-s10，unit=step28-formal-normalCal-b3-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-normalCal-b3-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=493840，PID/cgroup结束=True。

启动 formal-fact-b3-s10，unit=step28-formal-fact-b3-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-fact-b3-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=511828，PID/cgroup结束=True。

启动 formal-erc721-b3-s10，unit=step28-formal-erc721-b3-s10，pairs=1 triple or 1 split group；命令已保存。

结束 formal-erc721-b3-s10：passed=True，reason=exited，peak_threads=108，RSS_KiB=526788，PID/cgroup结束=True。

启动 formal-buyNow-b3-s10-G2，unit=step28-formal-buyNow-b3-s10-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s10-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=522944，PID/cgroup结束=True。

启动 formal-buyNow-b3-s10-G1，unit=step28-formal-buyNow-b3-s10-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s10-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=539968，PID/cgroup结束=True。

启动 formal-buyNow-b3-s10-G0，unit=step28-formal-buyNow-b3-s10-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-buyNow-b3-s10-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=552932，PID/cgroup结束=True。

已完成全部动态阶段：6个三组功能预检区块、buyNow empty/duplicate各三组异常与回滚功能检查、1次新增合约A对齐检查。正式3批×10块×6方法=180区块、540根调用；255个Guest测试进程全部正常退出，0失败、0无效区块、0资源/生命周期守卫触发。buyNow90正式根调用均真实执行6子调用。保留所有首笔、慢样本与反向结果。
已完成统计：SUMMARY/PAIRED_EFFECTS/STRATIFIED_EFFECTS/STAGE_EFFECTS/TIMING/RESOURCE_SUMMARY/MODULE_PREPARATION/CORRECTNESS，以及最终账本RW重放+进程内SHA核验。所有正式区块三组Gas/结果/读写/事件/完整最终账本一致。max采样RSS567.8MiB，max线程177；未提高资源限制，末尾managed/pending=0、PID/cgroup全部结束。
代码快照e7924d8（测量后提交，编译时源hash逐项复核一致），未push。首次git commit因无作者配置失败，后按历史Codex<codex@local>只在该commit命令设定作者，没有更改全局或仓库配置。
当前：结果校核/本地保存与IDE镜像；无活动实验，不需补跑。恢复仅运行scripts/analyze.py、report.py、children.py离线复算；正式outcome完整，禁止删除重跑覆盖。最重要限制：Table身份not_tested；长期Store线程回收/原池并发/真实节点收益未验证；buyNow残余窗口差异尚未定位到运行时机制。

离线复核完成：audit/final-verification.json确认180有效三组区块、540正式根调用、540正式真实子调用、255独立测试进程；所有计时嵌套非负、uses_before=0、不复用且同步Close，编译源/二进制SHA一致，无活动step28 unit。失败/无效/排除的主样本均0。buyNow两个异常夹具的所有真实子调用Gas/结果也再次离线逐项比较通过。
离线统计脚本首次重建账本时遗漏系统CHAIN_CONFIG初始项，随后从真实identity读集恢复并逐阶段SHA核验；未修改任何Guest/测量/账本原始记录。保存derived ledger后，恢复脚本原target-G*.json glob会误读derived ledger；已收窄target-G[0-2].json，不影响已完成的正式样本。相关复算过程均非新实验。
最终发现：hashCal/fact/ERC的Copy与A增量三批正；bigNumCal三项CI跨零；normalCal总体A+Copy较Fresh为正、A相对Copy跨零；buyNow A相对Copy正，但总体相对Fresh跨零且批次反转。buyNow根export扣除六个不重叠childInvoke后残余在Copy组额外7.025ms，窗口明确但机制未定位。均按真实结果报告，无删样本。
下一步只做本地commit与IDE镜像，不再运行Guest；完整复算命令依次analyze.py、report.py、children.py、verify.py。未push。

最终完成：源码/Guest冻结commit e7924d8，完整结果commit17e8c88，均仅本地分支experiment/step28-six-method-acopy，未push。已把本实验3799个Git跟踪文件精确镜像到CVW/experiments/instance-lifecycle/step-28-six-method-acopy，逐文件SHA一致。镜像用于IDE阅读；重建/恢复命令在原独立worktree运行（镜像不带未跟踪native库和host binary，go.work保留实际工作树路径），不要在镜像目录误启动新测试。
全部交付完成，无活动Guest进程/step28 unit，无待补样本。后续只需阅读README/RESULTS/BUY_NOW_ANALYSIS/CORRECTNESS；如要复核，在独立工作树离线运行统计与verify。Table身份、完整异常覆盖、长期Store及真实节点问题仍保留为未验证，不影响本轮有界串行数据的保存。
