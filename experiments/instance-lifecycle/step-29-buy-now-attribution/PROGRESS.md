# Step-29可恢复进度
父29950ab，独立experiment/step29-buy-now-attribution。先审计28并复算，不覆盖历史。
当前：恢复源码/计时边界。已有28仅能计算root export扣6childInvoke的残余，缺每个host sysCall和跨调用准备/结算。计划追加内存buffer单调span，root调用外flush，保留原28未插桩binary作为独立对照，不改变业务/Gas/调度。
沿原buyNow每group独立进程/10WASI/220threads1536MiB软限，硬限2G/256tasks，45s/60s。禁止后台池/异步关闭。

启动 preflight-b1-s01-plain-G0，unit=step29-preflight-b1-s01-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-b1-s01-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=561220，PID/cgroup结束=True。

启动 preflight-b1-s01-plain-G1，unit=step29-preflight-b1-s01-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-b1-s01-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=513528，PID/cgroup结束=True。

启动 preflight-b1-s01-plain-G2，unit=step29-preflight-b1-s01-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-b1-s01-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=530328，PID/cgroup结束=True。

启动 preflight-b1-s01-trace-G0，unit=step29-preflight-b1-s01-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-b1-s01-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=560992，PID/cgroup结束=True。

启动 preflight-b1-s01-trace-G1，unit=step29-preflight-b1-s01-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-b1-s01-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=515944，PID/cgroup结束=True。

启动 preflight-b1-s01-trace-G2，unit=step29-preflight-b1-s01-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 preflight-b1-s01-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=513860，PID/cgroup结束=True。

启动 exception-b1-s01-trace-empty-G0，unit=step29-exception-b1-s01-trace-empty-G0，pairs=1 triple or 1 split group；命令已保存。

结束 exception-b1-s01-trace-empty-G0：passed=True，reason=exited，peak_threads=75，RSS_KiB=533924，PID/cgroup结束=True。

启动 exception-b1-s01-trace-empty-G1，unit=step29-exception-b1-s01-trace-empty-G1，pairs=1 triple or 1 split group；命令已保存。

结束 exception-b1-s01-trace-empty-G1：passed=True，reason=exited，peak_threads=74，RSS_KiB=489656，PID/cgroup结束=True。

启动 exception-b1-s01-trace-empty-G2，unit=step29-exception-b1-s01-trace-empty-G2，pairs=1 triple or 1 split group；命令已保存。

结束 exception-b1-s01-trace-empty-G2：passed=True，reason=exited，peak_threads=74，RSS_KiB=481944，PID/cgroup结束=True。

启动 exception-b1-s01-trace-duplicate-G0，unit=step29-exception-b1-s01-trace-duplicate-G0，pairs=1 triple or 1 split group；命令已保存。

结束 exception-b1-s01-trace-duplicate-G0：passed=True，reason=exited，peak_threads=142，RSS_KiB=545748，PID/cgroup结束=True。

启动 exception-b1-s01-trace-duplicate-G1，unit=step29-exception-b1-s01-trace-duplicate-G1，pairs=1 triple or 1 split group；命令已保存。

结束 exception-b1-s01-trace-duplicate-G1：passed=True，reason=exited，peak_threads=142，RSS_KiB=524452，PID/cgroup结束=True。

启动 exception-b1-s01-trace-duplicate-G2，unit=step29-exception-b1-s01-trace-duplicate-G2，pairs=1 triple or 1 split group；命令已保存。

结束 exception-b1-s01-trace-duplicate-G2：passed=True，reason=exited，peak_threads=142，RSS_KiB=511504，PID/cgroup结束=True。

启动 preflight2-b1-s01-plain-G0，unit=step29-preflight2-b1-s01-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 preflight2-b1-s01-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=552580，PID/cgroup结束=True。

启动 preflight2-b1-s01-plain-G1，unit=step29-preflight2-b1-s01-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 preflight2-b1-s01-plain-G1：passed=True，reason=exited，peak_threads=177，RSS_KiB=535168，PID/cgroup结束=True。

启动 preflight2-b1-s01-plain-G2，unit=step29-preflight2-b1-s01-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 preflight2-b1-s01-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=507784，PID/cgroup结束=True。

启动 preflight2-b1-s01-trace-G0，unit=step29-preflight2-b1-s01-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 preflight2-b1-s01-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=578308，PID/cgroup结束=True。

启动 preflight2-b1-s01-trace-G1，unit=step29-preflight2-b1-s01-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 preflight2-b1-s01-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=538692，PID/cgroup结束=True。

启动 preflight2-b1-s01-trace-G2，unit=step29-preflight2-b1-s01-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 preflight2-b1-s01-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=528496，PID/cgroup结束=True。

静态审计/HISTORICAL_AUDIT完成。build1添加buffer trace并完成三组on/off功能与empty/duplicate回滚预检；build2增加原夹具bytecode clone与metadata span；build3追加保留行为的原logger委托计时。三次host编译均成功，正式仅build3 trace + Step28原binary plain，版本分别保存并冻结source_hashes，无覆盖。preflight2六进程通过，root export覆盖、6child串行、syscall嵌套/剩余时间恒等式通过。
预检发现root准备时间主要在fixture GetContractBytecode整份WASM分配/拷贝；G0约6.48ms，G1约23.61ms，G2约21.36ms（只作预检，含S1 hash不进性能）。logger/JSON不足以单独解释该量级。尚未证明GC等具体原因。
下一条：python3 -B scripts/continue.py。先build3异常回滚确认，再3批×10三组块×plain/trace同期对照；每组独立进程，总180正式root进程。跨模式逐组Gas/结果/RW/events/账本比对，raw始终保留。中断先查state/outcome/systemctl，脚本不会重跑已完成进程。

启动 exception2-b1-s01-trace-empty-G0，unit=step29-exception2-b1-s01-trace-empty-G0，pairs=1 triple or 1 split group；命令已保存。

结束 exception2-b1-s01-trace-empty-G0：passed=True，reason=exited，peak_threads=74，RSS_KiB=526880，PID/cgroup结束=True。

启动 exception2-b1-s01-trace-empty-G1，unit=step29-exception2-b1-s01-trace-empty-G1，pairs=1 triple or 1 split group；命令已保存。

结束 exception2-b1-s01-trace-empty-G1：passed=True，reason=exited，peak_threads=74，RSS_KiB=500784，PID/cgroup结束=True。

启动 exception2-b1-s01-trace-empty-G2，unit=step29-exception2-b1-s01-trace-empty-G2，pairs=1 triple or 1 split group；命令已保存。

结束 exception2-b1-s01-trace-empty-G2：passed=True，reason=exited，peak_threads=74，RSS_KiB=468384，PID/cgroup结束=True。

启动 exception2-b1-s01-trace-duplicate-G0，unit=step29-exception2-b1-s01-trace-duplicate-G0，pairs=1 triple or 1 split group；命令已保存。

结束 exception2-b1-s01-trace-duplicate-G0：passed=True，reason=exited，peak_threads=142，RSS_KiB=548548，PID/cgroup结束=True。

启动 exception2-b1-s01-trace-duplicate-G1，unit=step29-exception2-b1-s01-trace-duplicate-G1，pairs=1 triple or 1 split group；命令已保存。

结束 exception2-b1-s01-trace-duplicate-G1：passed=True，reason=exited，peak_threads=142，RSS_KiB=511796，PID/cgroup结束=True。

启动 exception2-b1-s01-trace-duplicate-G2，unit=step29-exception2-b1-s01-trace-duplicate-G2，pairs=1 triple or 1 split group；命令已保存。

结束 exception2-b1-s01-trace-duplicate-G2：passed=True，reason=exited，peak_threads=142，RSS_KiB=522588，PID/cgroup结束=True。

启动 formal-b1-s01-plain-G0，unit=step29-formal-b1-s01-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s01-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=574380，PID/cgroup结束=True。

启动 formal-b1-s01-plain-G1，unit=step29-formal-b1-s01-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s01-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=527456，PID/cgroup结束=True。

启动 formal-b1-s01-plain-G2，unit=step29-formal-b1-s01-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s01-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=512068，PID/cgroup结束=True。

启动 formal-b1-s01-trace-G0，unit=step29-formal-b1-s01-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s01-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=575524，PID/cgroup结束=True。

启动 formal-b1-s01-trace-G1，unit=step29-formal-b1-s01-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s01-trace-G1：passed=True，reason=exited，peak_threads=177，RSS_KiB=542640，PID/cgroup结束=True。

启动 formal-b1-s01-trace-G2，unit=step29-formal-b1-s01-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s01-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=534144，PID/cgroup结束=True。

启动 formal-b1-s02-trace-G0，unit=step29-formal-b1-s02-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s02-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=566812，PID/cgroup结束=True。

启动 formal-b1-s02-trace-G2，unit=step29-formal-b1-s02-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s02-trace-G2：passed=True，reason=exited，peak_threads=177，RSS_KiB=544128，PID/cgroup结束=True。

启动 formal-b1-s02-trace-G1，unit=step29-formal-b1-s02-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s02-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=529664，PID/cgroup结束=True。

启动 formal-b1-s02-plain-G0，unit=step29-formal-b1-s02-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s02-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=550804，PID/cgroup结束=True。

启动 formal-b1-s02-plain-G2，unit=step29-formal-b1-s02-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s02-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=520080，PID/cgroup结束=True。

启动 formal-b1-s02-plain-G1，unit=step29-formal-b1-s02-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s02-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=526772，PID/cgroup结束=True。

启动 formal-b1-s03-plain-G1，unit=step29-formal-b1-s03-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s03-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=527380，PID/cgroup结束=True。

启动 formal-b1-s03-plain-G0，unit=step29-formal-b1-s03-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s03-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=571132，PID/cgroup结束=True。

启动 formal-b1-s03-plain-G2，unit=step29-formal-b1-s03-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s03-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=501472，PID/cgroup结束=True。

启动 formal-b1-s03-trace-G1，unit=step29-formal-b1-s03-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s03-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=520004，PID/cgroup结束=True。

启动 formal-b1-s03-trace-G0，unit=step29-formal-b1-s03-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s03-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=559280，PID/cgroup结束=True。

启动 formal-b1-s03-trace-G2，unit=step29-formal-b1-s03-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s03-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=514012，PID/cgroup结束=True。

启动 formal-b1-s04-trace-G1，unit=step29-formal-b1-s04-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s04-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=535668，PID/cgroup结束=True。

启动 formal-b1-s04-trace-G2，unit=step29-formal-b1-s04-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s04-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=524464，PID/cgroup结束=True。

启动 formal-b1-s04-trace-G0，unit=step29-formal-b1-s04-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s04-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=553976，PID/cgroup结束=True。

启动 formal-b1-s04-plain-G1，unit=step29-formal-b1-s04-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s04-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=514448，PID/cgroup结束=True。

启动 formal-b1-s04-plain-G2，unit=step29-formal-b1-s04-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s04-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=530128，PID/cgroup结束=True。

启动 formal-b1-s04-plain-G0，unit=step29-formal-b1-s04-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s04-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=561560，PID/cgroup结束=True。

启动 formal-b1-s05-plain-G2，unit=step29-formal-b1-s05-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s05-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=525936，PID/cgroup结束=True。

启动 formal-b1-s05-plain-G0，unit=step29-formal-b1-s05-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s05-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=551200，PID/cgroup结束=True。

启动 formal-b1-s05-plain-G1，unit=step29-formal-b1-s05-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s05-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=524496，PID/cgroup结束=True。

启动 formal-b1-s05-trace-G2，unit=step29-formal-b1-s05-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s05-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=510484，PID/cgroup结束=True。

启动 formal-b1-s05-trace-G0，unit=step29-formal-b1-s05-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s05-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=581072，PID/cgroup结束=True。

启动 formal-b1-s05-trace-G1，unit=step29-formal-b1-s05-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s05-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=534060，PID/cgroup结束=True。

启动 formal-b1-s06-trace-G2，unit=step29-formal-b1-s06-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s06-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=534364，PID/cgroup结束=True。

启动 formal-b1-s06-trace-G1，unit=step29-formal-b1-s06-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s06-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=521200，PID/cgroup结束=True。

启动 formal-b1-s06-trace-G0，unit=step29-formal-b1-s06-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s06-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=571580，PID/cgroup结束=True。

启动 formal-b1-s06-plain-G2，unit=step29-formal-b1-s06-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s06-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=515944，PID/cgroup结束=True。

启动 formal-b1-s06-plain-G1，unit=step29-formal-b1-s06-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s06-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=512036，PID/cgroup结束=True。

启动 formal-b1-s06-plain-G0，unit=step29-formal-b1-s06-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s06-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=544056，PID/cgroup结束=True。

启动 formal-b1-s07-plain-G0，unit=step29-formal-b1-s07-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s07-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=562696，PID/cgroup结束=True。

启动 formal-b1-s07-plain-G1，unit=step29-formal-b1-s07-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s07-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=530664，PID/cgroup结束=True。

启动 formal-b1-s07-plain-G2，unit=step29-formal-b1-s07-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s07-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=509784，PID/cgroup结束=True。

启动 formal-b1-s07-trace-G0，unit=step29-formal-b1-s07-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s07-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=563544，PID/cgroup结束=True。

启动 formal-b1-s07-trace-G1，unit=step29-formal-b1-s07-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s07-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=519140，PID/cgroup结束=True。

启动 formal-b1-s07-trace-G2，unit=step29-formal-b1-s07-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s07-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=525484，PID/cgroup结束=True。

启动 formal-b1-s08-trace-G0，unit=step29-formal-b1-s08-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s08-trace-G0：passed=True，reason=exited，peak_threads=177，RSS_KiB=579424，PID/cgroup结束=True。

启动 formal-b1-s08-trace-G2，unit=step29-formal-b1-s08-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s08-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=513324，PID/cgroup结束=True。

启动 formal-b1-s08-trace-G1，unit=step29-formal-b1-s08-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s08-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=531372，PID/cgroup结束=True。

启动 formal-b1-s08-plain-G0，unit=step29-formal-b1-s08-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s08-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=550324，PID/cgroup结束=True。

启动 formal-b1-s08-plain-G2，unit=step29-formal-b1-s08-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s08-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=527224，PID/cgroup结束=True。

启动 formal-b1-s08-plain-G1，unit=step29-formal-b1-s08-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s08-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=533084，PID/cgroup结束=True。

启动 formal-b1-s09-plain-G1，unit=step29-formal-b1-s09-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s09-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=532292，PID/cgroup结束=True。

启动 formal-b1-s09-plain-G0，unit=step29-formal-b1-s09-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s09-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=543464，PID/cgroup结束=True。

启动 formal-b1-s09-plain-G2，unit=step29-formal-b1-s09-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s09-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=514412，PID/cgroup结束=True。

启动 formal-b1-s09-trace-G1，unit=step29-formal-b1-s09-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s09-trace-G1：passed=True，reason=exited，peak_threads=177，RSS_KiB=526992，PID/cgroup结束=True。

启动 formal-b1-s09-trace-G0，unit=step29-formal-b1-s09-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s09-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=569852，PID/cgroup结束=True。

启动 formal-b1-s09-trace-G2，unit=step29-formal-b1-s09-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s09-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=540532，PID/cgroup结束=True。

启动 formal-b1-s10-trace-G1，unit=step29-formal-b1-s10-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s10-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=536700，PID/cgroup结束=True。

启动 formal-b1-s10-trace-G2，unit=step29-formal-b1-s10-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s10-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=544788，PID/cgroup结束=True。

启动 formal-b1-s10-trace-G0，unit=step29-formal-b1-s10-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s10-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=561376，PID/cgroup结束=True。

启动 formal-b1-s10-plain-G1，unit=step29-formal-b1-s10-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s10-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=522252，PID/cgroup结束=True。

启动 formal-b1-s10-plain-G2，unit=step29-formal-b1-s10-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s10-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=518488，PID/cgroup结束=True。

启动 formal-b1-s10-plain-G0，unit=step29-formal-b1-s10-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b1-s10-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=552000，PID/cgroup结束=True。

启动 formal-b2-s01-plain-G2，unit=step29-formal-b2-s01-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s01-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=519476，PID/cgroup结束=True。

启动 formal-b2-s01-plain-G0，unit=step29-formal-b2-s01-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s01-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=554876，PID/cgroup结束=True。

启动 formal-b2-s01-plain-G1，unit=step29-formal-b2-s01-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s01-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=543124，PID/cgroup结束=True。

启动 formal-b2-s01-trace-G2，unit=step29-formal-b2-s01-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s01-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=528856，PID/cgroup结束=True。

启动 formal-b2-s01-trace-G0，unit=step29-formal-b2-s01-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s01-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=555440，PID/cgroup结束=True。

启动 formal-b2-s01-trace-G1，unit=step29-formal-b2-s01-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s01-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=534408，PID/cgroup结束=True。

启动 formal-b2-s02-trace-G2，unit=step29-formal-b2-s02-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s02-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=531092，PID/cgroup结束=True。

启动 formal-b2-s02-trace-G1，unit=step29-formal-b2-s02-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s02-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=536088，PID/cgroup结束=True。

启动 formal-b2-s02-trace-G0，unit=step29-formal-b2-s02-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s02-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=561384，PID/cgroup结束=True。

启动 formal-b2-s02-plain-G2，unit=step29-formal-b2-s02-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s02-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=529576，PID/cgroup结束=True。

启动 formal-b2-s02-plain-G1，unit=step29-formal-b2-s02-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s02-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=525368，PID/cgroup结束=True。

启动 formal-b2-s02-plain-G0，unit=step29-formal-b2-s02-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s02-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=578716，PID/cgroup结束=True。

启动 formal-b2-s03-plain-G0，unit=step29-formal-b2-s03-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s03-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=539360，PID/cgroup结束=True。

启动 formal-b2-s03-plain-G1，unit=step29-formal-b2-s03-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s03-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=522740，PID/cgroup结束=True。

启动 formal-b2-s03-plain-G2，unit=step29-formal-b2-s03-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s03-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=513036，PID/cgroup结束=True。

启动 formal-b2-s03-trace-G0，unit=step29-formal-b2-s03-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s03-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=553540，PID/cgroup结束=True。

启动 formal-b2-s03-trace-G1，unit=step29-formal-b2-s03-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s03-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=524904，PID/cgroup结束=True。

启动 formal-b2-s03-trace-G2，unit=step29-formal-b2-s03-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s03-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=517476，PID/cgroup结束=True。

启动 formal-b2-s04-trace-G0，unit=step29-formal-b2-s04-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s04-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=570884，PID/cgroup结束=True。

启动 formal-b2-s04-trace-G2，unit=step29-formal-b2-s04-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s04-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=531304，PID/cgroup结束=True。

启动 formal-b2-s04-trace-G1，unit=step29-formal-b2-s04-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s04-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=543020，PID/cgroup结束=True。

启动 formal-b2-s04-plain-G0，unit=step29-formal-b2-s04-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s04-plain-G0：passed=True，reason=exited，peak_threads=177，RSS_KiB=554448，PID/cgroup结束=True。

启动 formal-b2-s04-plain-G2，unit=step29-formal-b2-s04-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s04-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=512488，PID/cgroup结束=True。

启动 formal-b2-s04-plain-G1，unit=step29-formal-b2-s04-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s04-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=536248，PID/cgroup结束=True。

启动 formal-b2-s05-plain-G1，unit=step29-formal-b2-s05-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s05-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=538416，PID/cgroup结束=True。

启动 formal-b2-s05-plain-G0，unit=step29-formal-b2-s05-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s05-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=555332，PID/cgroup结束=True。

启动 formal-b2-s05-plain-G2，unit=step29-formal-b2-s05-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s05-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=515204，PID/cgroup结束=True。

启动 formal-b2-s05-trace-G1，unit=step29-formal-b2-s05-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s05-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=544168，PID/cgroup结束=True。

启动 formal-b2-s05-trace-G0，unit=step29-formal-b2-s05-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s05-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=582476，PID/cgroup结束=True。

启动 formal-b2-s05-trace-G2，unit=step29-formal-b2-s05-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s05-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=534340，PID/cgroup结束=True。

启动 formal-b2-s06-trace-G1，unit=step29-formal-b2-s06-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s06-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=529764，PID/cgroup结束=True。

启动 formal-b2-s06-trace-G2，unit=step29-formal-b2-s06-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s06-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=513184，PID/cgroup结束=True。

启动 formal-b2-s06-trace-G0，unit=step29-formal-b2-s06-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s06-trace-G0：passed=True，reason=exited，peak_threads=177，RSS_KiB=579260，PID/cgroup结束=True。

启动 formal-b2-s06-plain-G1，unit=step29-formal-b2-s06-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s06-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=522672，PID/cgroup结束=True。

启动 formal-b2-s06-plain-G2，unit=step29-formal-b2-s06-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s06-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=525888，PID/cgroup结束=True。

启动 formal-b2-s06-plain-G0，unit=step29-formal-b2-s06-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s06-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=560000，PID/cgroup结束=True。

启动 formal-b2-s07-plain-G2，unit=step29-formal-b2-s07-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s07-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=518960，PID/cgroup结束=True。

启动 formal-b2-s07-plain-G0，unit=step29-formal-b2-s07-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s07-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=558864，PID/cgroup结束=True。

启动 formal-b2-s07-plain-G1，unit=step29-formal-b2-s07-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s07-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=531088，PID/cgroup结束=True。

启动 formal-b2-s07-trace-G2，unit=step29-formal-b2-s07-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s07-trace-G2：passed=True，reason=exited，peak_threads=177，RSS_KiB=522888，PID/cgroup结束=True。

启动 formal-b2-s07-trace-G0，unit=step29-formal-b2-s07-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s07-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=569632，PID/cgroup结束=True。

启动 formal-b2-s07-trace-G1，unit=step29-formal-b2-s07-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s07-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=538736，PID/cgroup结束=True。

启动 formal-b2-s08-trace-G2，unit=step29-formal-b2-s08-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s08-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=538252，PID/cgroup结束=True。

启动 formal-b2-s08-trace-G1，unit=step29-formal-b2-s08-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s08-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=530716，PID/cgroup结束=True。

启动 formal-b2-s08-trace-G0，unit=step29-formal-b2-s08-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s08-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=552720，PID/cgroup结束=True。

启动 formal-b2-s08-plain-G2，unit=step29-formal-b2-s08-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s08-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=530504，PID/cgroup结束=True。

启动 formal-b2-s08-plain-G1，unit=step29-formal-b2-s08-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s08-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=530460，PID/cgroup结束=True。

启动 formal-b2-s08-plain-G0，unit=step29-formal-b2-s08-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s08-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=555640，PID/cgroup结束=True。

启动 formal-b2-s09-plain-G0，unit=step29-formal-b2-s09-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s09-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=553064，PID/cgroup结束=True。

启动 formal-b2-s09-plain-G1，unit=step29-formal-b2-s09-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s09-plain-G1：passed=True，reason=exited，peak_threads=177，RSS_KiB=519412，PID/cgroup结束=True。

启动 formal-b2-s09-plain-G2，unit=step29-formal-b2-s09-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s09-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=515956，PID/cgroup结束=True。

启动 formal-b2-s09-trace-G0，unit=step29-formal-b2-s09-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s09-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=557848，PID/cgroup结束=True。

启动 formal-b2-s09-trace-G1，unit=step29-formal-b2-s09-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s09-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=527436，PID/cgroup结束=True。

启动 formal-b2-s09-trace-G2，unit=step29-formal-b2-s09-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s09-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=532800，PID/cgroup结束=True。

启动 formal-b2-s10-trace-G0，unit=step29-formal-b2-s10-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s10-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=564696，PID/cgroup结束=True。

启动 formal-b2-s10-trace-G2，unit=step29-formal-b2-s10-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s10-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=503860，PID/cgroup结束=True。

启动 formal-b2-s10-trace-G1，unit=step29-formal-b2-s10-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s10-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=531868，PID/cgroup结束=True。

启动 formal-b2-s10-plain-G0，unit=step29-formal-b2-s10-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s10-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=561852，PID/cgroup结束=True。

启动 formal-b2-s10-plain-G2，unit=step29-formal-b2-s10-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s10-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=528184，PID/cgroup结束=True。

启动 formal-b2-s10-plain-G1，unit=step29-formal-b2-s10-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b2-s10-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=550344，PID/cgroup结束=True。

启动 formal-b3-s01-plain-G1，unit=step29-formal-b3-s01-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s01-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=525988，PID/cgroup结束=True。

启动 formal-b3-s01-plain-G0，unit=step29-formal-b3-s01-plain-G0，pairs=1 triple or 1 split group；命令已保存。

正式进程正常推进到第2批，未触发guard。阶段性离线复算12块/模式（仅审计，不作最终结论）显示：trace模式额外prepare与bytecode_clone同量级；JSON/logger/gas较小。plain/trace同期差异可能达数毫秒，不能认定插桩无扰动；保留原binary plain作为唯一新的主性能证据，trace仅诊断定位，绝不混合。所有旧/新源与计时仍保留，未为改变结果更换工作量。

结束 formal-b3-s01-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=556216，PID/cgroup结束=True。

启动 formal-b3-s01-plain-G2，unit=step29-formal-b3-s01-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s01-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=539488，PID/cgroup结束=True。

启动 formal-b3-s01-trace-G1，unit=step29-formal-b3-s01-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s01-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=539244，PID/cgroup结束=True。

启动 formal-b3-s01-trace-G0，unit=step29-formal-b3-s01-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s01-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=572352，PID/cgroup结束=True。

启动 formal-b3-s01-trace-G2，unit=step29-formal-b3-s01-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s01-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=530244，PID/cgroup结束=True。

启动 formal-b3-s02-trace-G1，unit=step29-formal-b3-s02-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s02-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=529212，PID/cgroup结束=True。

启动 formal-b3-s02-trace-G2，unit=step29-formal-b3-s02-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s02-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=505472，PID/cgroup结束=True。

启动 formal-b3-s02-trace-G0，unit=step29-formal-b3-s02-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s02-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=569104，PID/cgroup结束=True。

启动 formal-b3-s02-plain-G1，unit=step29-formal-b3-s02-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s02-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=522808，PID/cgroup结束=True。

启动 formal-b3-s02-plain-G2，unit=step29-formal-b3-s02-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s02-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=513512，PID/cgroup结束=True。

启动 formal-b3-s02-plain-G0，unit=step29-formal-b3-s02-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s02-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=569804，PID/cgroup结束=True。

启动 formal-b3-s03-plain-G2，unit=step29-formal-b3-s03-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s03-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=535268，PID/cgroup结束=True。

启动 formal-b3-s03-plain-G0，unit=step29-formal-b3-s03-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s03-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=563200，PID/cgroup结束=True。

启动 formal-b3-s03-plain-G1，unit=step29-formal-b3-s03-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s03-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=533772，PID/cgroup结束=True。

启动 formal-b3-s03-trace-G2，unit=step29-formal-b3-s03-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s03-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=518756，PID/cgroup结束=True。

启动 formal-b3-s03-trace-G0，unit=step29-formal-b3-s03-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s03-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=565328，PID/cgroup结束=True。

启动 formal-b3-s03-trace-G1，unit=step29-formal-b3-s03-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s03-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=531708，PID/cgroup结束=True。

启动 formal-b3-s04-trace-G2，unit=step29-formal-b3-s04-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s04-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=512612，PID/cgroup结束=True。

启动 formal-b3-s04-trace-G1，unit=step29-formal-b3-s04-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s04-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=545540，PID/cgroup结束=True。

启动 formal-b3-s04-trace-G0，unit=step29-formal-b3-s04-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s04-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=563432，PID/cgroup结束=True。

启动 formal-b3-s04-plain-G2，unit=step29-formal-b3-s04-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s04-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=498732，PID/cgroup结束=True。

启动 formal-b3-s04-plain-G1，unit=step29-formal-b3-s04-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s04-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=510848，PID/cgroup结束=True。

启动 formal-b3-s04-plain-G0，unit=step29-formal-b3-s04-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s04-plain-G0：passed=True，reason=exited，peak_threads=177，RSS_KiB=572444，PID/cgroup结束=True。

启动 formal-b3-s05-plain-G0，unit=step29-formal-b3-s05-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s05-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=572840，PID/cgroup结束=True。

启动 formal-b3-s05-plain-G1，unit=step29-formal-b3-s05-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s05-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=523756，PID/cgroup结束=True。

启动 formal-b3-s05-plain-G2，unit=step29-formal-b3-s05-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s05-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=502872，PID/cgroup结束=True。

启动 formal-b3-s05-trace-G0，unit=step29-formal-b3-s05-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s05-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=578304，PID/cgroup结束=True。

启动 formal-b3-s05-trace-G1，unit=step29-formal-b3-s05-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s05-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=537932，PID/cgroup结束=True。

启动 formal-b3-s05-trace-G2，unit=step29-formal-b3-s05-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s05-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=511436，PID/cgroup结束=True。

启动 formal-b3-s06-trace-G0，unit=step29-formal-b3-s06-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s06-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=557196，PID/cgroup结束=True。

启动 formal-b3-s06-trace-G2，unit=step29-formal-b3-s06-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s06-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=516328，PID/cgroup结束=True。

启动 formal-b3-s06-trace-G1，unit=step29-formal-b3-s06-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s06-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=534380，PID/cgroup结束=True。

启动 formal-b3-s06-plain-G0，unit=step29-formal-b3-s06-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s06-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=566872，PID/cgroup结束=True。

启动 formal-b3-s06-plain-G2，unit=step29-formal-b3-s06-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s06-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=540720，PID/cgroup结束=True。

启动 formal-b3-s06-plain-G1，unit=step29-formal-b3-s06-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s06-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=523396，PID/cgroup结束=True。

启动 formal-b3-s07-plain-G1，unit=step29-formal-b3-s07-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s07-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=522592，PID/cgroup结束=True。

启动 formal-b3-s07-plain-G0，unit=step29-formal-b3-s07-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s07-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=550036，PID/cgroup结束=True。

启动 formal-b3-s07-plain-G2，unit=step29-formal-b3-s07-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s07-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=514556，PID/cgroup结束=True。

启动 formal-b3-s07-trace-G1，unit=step29-formal-b3-s07-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s07-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=513732，PID/cgroup结束=True。

启动 formal-b3-s07-trace-G0，unit=step29-formal-b3-s07-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s07-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=566060，PID/cgroup结束=True。

启动 formal-b3-s07-trace-G2，unit=step29-formal-b3-s07-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s07-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=522636，PID/cgroup结束=True。

启动 formal-b3-s08-trace-G1，unit=step29-formal-b3-s08-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s08-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=539436，PID/cgroup结束=True。

启动 formal-b3-s08-trace-G2，unit=step29-formal-b3-s08-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s08-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=511588，PID/cgroup结束=True。

启动 formal-b3-s08-trace-G0，unit=step29-formal-b3-s08-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s08-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=563616，PID/cgroup结束=True。

启动 formal-b3-s08-plain-G1，unit=step29-formal-b3-s08-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s08-plain-G1：passed=True，reason=exited，peak_threads=177，RSS_KiB=509444，PID/cgroup结束=True。

启动 formal-b3-s08-plain-G2，unit=step29-formal-b3-s08-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s08-plain-G2：passed=True，reason=exited，peak_threads=177，RSS_KiB=526256，PID/cgroup结束=True。

启动 formal-b3-s08-plain-G0，unit=step29-formal-b3-s08-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s08-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=552468，PID/cgroup结束=True。

启动 formal-b3-s09-plain-G2，unit=step29-formal-b3-s09-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s09-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=518520，PID/cgroup结束=True。

启动 formal-b3-s09-plain-G0，unit=step29-formal-b3-s09-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s09-plain-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=555128，PID/cgroup结束=True。

启动 formal-b3-s09-plain-G1，unit=step29-formal-b3-s09-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s09-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=529740，PID/cgroup结束=True。

启动 formal-b3-s09-trace-G2，unit=step29-formal-b3-s09-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s09-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=537672，PID/cgroup结束=True。

启动 formal-b3-s09-trace-G0，unit=step29-formal-b3-s09-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s09-trace-G0：passed=True，reason=exited，peak_threads=176，RSS_KiB=562032，PID/cgroup结束=True。

启动 formal-b3-s09-trace-G1，unit=step29-formal-b3-s09-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s09-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=534160，PID/cgroup结束=True。

启动 formal-b3-s10-trace-G2，unit=step29-formal-b3-s10-trace-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s10-trace-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=518304，PID/cgroup结束=True。

启动 formal-b3-s10-trace-G1，unit=step29-formal-b3-s10-trace-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s10-trace-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=531364，PID/cgroup结束=True。

启动 formal-b3-s10-trace-G0，unit=step29-formal-b3-s10-trace-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s10-trace-G0：passed=True，reason=exited，peak_threads=177，RSS_KiB=569872，PID/cgroup结束=True。

启动 formal-b3-s10-plain-G2，unit=step29-formal-b3-s10-plain-G2，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s10-plain-G2：passed=True，reason=exited，peak_threads=176，RSS_KiB=511656，PID/cgroup结束=True。

启动 formal-b3-s10-plain-G1，unit=step29-formal-b3-s10-plain-G1，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s10-plain-G1：passed=True，reason=exited，peak_threads=176，RSS_KiB=539432，PID/cgroup结束=True。

启动 formal-b3-s10-plain-G0，unit=step29-formal-b3-s10-plain-G0，pairs=1 triple or 1 split group；命令已保存。

结束 formal-b3-s10-plain-G0：passed=True，reason=exited，peak_threads=177，RSS_KiB=574780，PID/cgroup结束=True。

正式完成：plain与trace各3批×10个三组区块，各90根调用，共180根/1080真实子调用；另预检/异常24进程，总204进程全部正常结束。无主样本失败、无无效/排除块、无资源/生命周期守卫触发。每块三组与同组跨模式Gas/返回/RW/event/完整最终账本均一致；根Gas12612158；empty/duplicate错误/回滚最终build3复核通过。
最终新plain直接配对节省：Copy−4.466ms CI[−9.283,5.393]；A叠加Copy3.385[−3.426,12.430]；A+Copy对Fresh2.549[−2.296,8.937]；均未确认稳定完整收益。plain七实例NewInstance+Copy的Copy净节省4.343[3.551,6.713]，A在Copy基础的七_start净节省5.606[5.147,6.123]，但没有稳定传递到root Invoke。
trace定位：root残余Median G0/G1/G2=7.124/15.831/17.118ms；prepare6.196/14.899/16.218ms；fixture clone5.596/14.088/15.238ms。G0/G1克隆字节量完全相同29,588,469B；G2仅多4038B。故不能用“Copy复制更多字节”解释时差，也不能把clone窗口直接叫纯memcpy/GC。JSON/stdout/getsetGas较小；wacsi内部Gas/Guest JSON/clone内机制仍未分离。
扰动不能忽略：G2 trace相对plain完整Invoke额外3.617ms CI[0.882,9.149]；只用plain作最终性能结论。trace证据定位现有夹具窗口，不能把旧28所有7.025ms因果归属clone，更不能说生产节点一样。
审计/统计/账本重放/所有原始log与命令已落盘。最高RSS568.8MiB、threads177、boundary Go heap105.7MiB；所有managed/pending=0、created=closed、PID/cgroup退出，已无step29 unit。verify通过，历史引用SHA全部保持不变。
下一步仅最终本地commit/IDE镜像，不再Guest执行。复算：scripts/analyze.py→report.py→verify.py。Table身份/长期Store/原池并发/节点收益仍not_tested，不制作PPT、不push。

交付复核完成：historical.py重新读取Step28原90个buyNow root日志，重算三条Invoke/残余配对中位数，与旧报告完全吻合，未写历史目录。分析全量重复复算通过；final-verification.json确认两套各30区块/3批，6真实callee/每root，204进程退出与历史hash不变。SOURCE_INDEX.csv与INSTRUMENTATION.diff记录准确插桩位置。原binary同期控制保留完整原计时，正式源build3的source_hashes校验完全一致。
当前：无活动unit/Guest，仅本地版本保存与IDE镜像。恢复不用再运行Guest；离线historical.py、analyze.py、report.py、verify.py。没有需凑数的未完成样本；未定位机制和未验证项已在报告保留。

本地结果/源码快照已提交8788b08（测量后形成，运行时29950ab+记录的新增源码；所有Go编译源hash逐项匹配，SOURCE_FREEZE明确区分）。未push、未修改生产VM。即将把本实验Git跟踪交付精确镜像至CVW/experiments/instance-lifecycle/step-29-buy-now-attribution，供IDE查看；运行/恢复仍在原独立worktree，镜像不含native库/host binary。所有目标交付与实际有界测试完成，无待继续的Guest任务。
