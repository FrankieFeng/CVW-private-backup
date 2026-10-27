# Step-27可恢复进度
2026-10-27，分支experiment/step27-normalcal-diagnostic，父81e1c0a。
当前：历史审计、新主实验/诊断及报告已完成；不再启动Guest。以下保留阶段进度。先复核历史600条和21E两独立反序短批，不把26复算称新重复。
模型候选：R0/R1用同一Store同一Module固定owner串行，R0保留init实例；每process最多2对，R1最多创建2次，总同Store实例数3，与22/24B原单Store预算相同。每批10对由5个独立进程组成，不是同一R0连续10次。先ABBA预检确认R1关闭后R0仍可执行；任何新风险STOP。
历史原WASM优先R0/R1、R1/Copy；匹配A原件仍blocked。四组Step18补充另列，A源码布局改变WASM，不能称同一hash。所有指标分家族、不拼接历史与新样本。
保持RSS768MiB/线程125软限、2GiB/256tasks硬限、Go45s/进程60s、available8GiB/swap1GiB；不提高预算，不开启原池或全局锁。本轮不PPT、不push、不改生产。
下一步冻结证据、准备只修改测试计时/角色选择的原型；预检之前不启动正式批次。

历史复核完成：600旧B5链接通过，Invoke均值差8.247138767ms、export8.294027577ms，原21E反序短批1.486065/3.019442ms；包含2个gate额外样本，不混入12个短批。CSV转化CallMethod最大1ns精度差保留说明。build1编译因unused time import失败，未产生binary/Guest；仅删除未用import准备build2，原log保留。

启动 pre-original-R0-R1，unit=step27-pre-original-R0-R1，pairs=2；命令已保存。

结束 pre-original-R0-R1：passed=True，reason=exited，peak_threads=57，RSS_KiB=303956，PID/cgroup结束=True。

启动 pre-step18-R0-R1，unit=step27-pre-step18-R0-R1，pairs=2；命令已保存。

结束 pre-step18-R0-R1：passed=True，reason=exited，peak_threads=57，RSS_KiB=297680，PID/cgroup结束=True。

启动 pre-original-R1-C1，unit=step27-pre-original-R1-C1，pairs=2；命令已保存。

结束 pre-original-R1-C1：passed=True，reason=exited，peak_threads=108，RSS_KiB=397928，PID/cgroup结束=True。

启动 pre-step18-R1-C1，unit=step27-pre-step18-R1-C1，pairs=2；命令已保存。

结束 pre-step18-R1-C1：passed=True，reason=exited，peak_threads=108，RSS_KiB=396180，PID/cgroup结束=True。

启动 pre-step18-R1-C2，unit=step27-pre-step18-R1-C2，pairs=2；命令已保存。

结束 pre-step18-R1-C2：passed=True，reason=exited，peak_threads=108，RSS_KiB=393016，PID/cgroup结束=True。

启动 pre-step18-C1-C2，unit=step27-pre-step18-C1-C2，pairs=2；命令已保存。

结束 pre-step18-C1-C2：passed=True，reason=exited，peak_threads=108，RSS_KiB=387220，PID/cgroup结束=True。

启动 original-b1-R0-R1-p0，unit=step27-original-b1-R0-R1-p0，pairs=2；命令已保存。

结束 original-b1-R0-R1-p0：passed=True，reason=exited，peak_threads=57，RSS_KiB=311576，PID/cgroup结束=True。

启动 original-b1-R0-R1-p1，unit=step27-original-b1-R0-R1-p1，pairs=2；命令已保存。

结束 original-b1-R0-R1-p1：passed=True，reason=exited，peak_threads=57，RSS_KiB=290372，PID/cgroup结束=True。

启动 original-b1-R0-R1-p2，unit=step27-original-b1-R0-R1-p2，pairs=2；命令已保存。

结束 original-b1-R0-R1-p2：passed=True，reason=exited，peak_threads=57，RSS_KiB=308812，PID/cgroup结束=True。

启动 original-b1-R0-R1-p3，unit=step27-original-b1-R0-R1-p3，pairs=2；命令已保存。

结束 original-b1-R0-R1-p3：passed=True，reason=exited，peak_threads=57，RSS_KiB=299844，PID/cgroup结束=True。

启动 original-b1-R0-R1-p4，unit=step27-original-b1-R0-R1-p4，pairs=2；命令已保存。

结束 original-b1-R0-R1-p4：passed=True，reason=exited，peak_threads=57，RSS_KiB=297576，PID/cgroup结束=True。

启动 step18-b1-R0-R1-p0，unit=step27-step18-b1-R0-R1-p0，pairs=2；命令已保存。

结束 step18-b1-R0-R1-p0：passed=True，reason=exited，peak_threads=57，RSS_KiB=303924，PID/cgroup结束=True。

启动 step18-b1-R0-R1-p1，unit=step27-step18-b1-R0-R1-p1，pairs=2；命令已保存。

结束 step18-b1-R0-R1-p1：passed=True，reason=exited，peak_threads=57，RSS_KiB=297368，PID/cgroup结束=True。

启动 step18-b1-R0-R1-p2，unit=step27-step18-b1-R0-R1-p2，pairs=2；命令已保存。

结束 step18-b1-R0-R1-p2：passed=True，reason=exited，peak_threads=57，RSS_KiB=304460，PID/cgroup结束=True。

启动 step18-b1-R0-R1-p3，unit=step27-step18-b1-R0-R1-p3，pairs=2；命令已保存。

结束 step18-b1-R0-R1-p3：passed=True，reason=exited，peak_threads=57，RSS_KiB=301676，PID/cgroup结束=True。

启动 step18-b1-R0-R1-p4，unit=step27-step18-b1-R0-R1-p4，pairs=2；命令已保存。

结束 step18-b1-R0-R1-p4：passed=True，reason=exited，peak_threads=57，RSS_KiB=300236，PID/cgroup结束=True。

启动 original-b1-R1-C1-p0，unit=step27-original-b1-R1-C1-p0，pairs=2；命令已保存。

结束 original-b1-R1-C1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=392968，PID/cgroup结束=True。

启动 original-b1-R1-C1-p1，unit=step27-original-b1-R1-C1-p1，pairs=2；命令已保存。

结束 original-b1-R1-C1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=391512，PID/cgroup结束=True。

启动 original-b1-R1-C1-p2，unit=step27-original-b1-R1-C1-p2，pairs=2；命令已保存。

结束 original-b1-R1-C1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=388720，PID/cgroup结束=True。

启动 original-b1-R1-C1-p3，unit=step27-original-b1-R1-C1-p3，pairs=2；命令已保存。

结束 original-b1-R1-C1-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=385152，PID/cgroup结束=True。

启动 original-b1-R1-C1-p4，unit=step27-original-b1-R1-C1-p4，pairs=2；命令已保存。

结束 original-b1-R1-C1-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=397272，PID/cgroup结束=True。

启动 step18-b1-R1-C1-p0，unit=step27-step18-b1-R1-C1-p0，pairs=2；命令已保存。

结束 step18-b1-R1-C1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=387412，PID/cgroup结束=True。

启动 step18-b1-R1-C1-p1，unit=step27-step18-b1-R1-C1-p1，pairs=2；命令已保存。

结束 step18-b1-R1-C1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=393576，PID/cgroup结束=True。

启动 step18-b1-R1-C1-p2，unit=step27-step18-b1-R1-C1-p2，pairs=2；命令已保存。

结束 step18-b1-R1-C1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=395520，PID/cgroup结束=True。

启动 step18-b1-R1-C1-p3，unit=step27-step18-b1-R1-C1-p3，pairs=2；命令已保存。

结束 step18-b1-R1-C1-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=397648，PID/cgroup结束=True。

启动 step18-b1-R1-C1-p4，unit=step27-step18-b1-R1-C1-p4，pairs=2；命令已保存。

结束 step18-b1-R1-C1-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=389240，PID/cgroup结束=True。

启动 step18-b1-R1-C2-p0，unit=step27-step18-b1-R1-C2-p0，pairs=2；命令已保存。

结束 step18-b1-R1-C2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=405204，PID/cgroup结束=True。

启动 step18-b1-R1-C2-p1，unit=step27-step18-b1-R1-C2-p1，pairs=2；命令已保存。

结束 step18-b1-R1-C2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=399668，PID/cgroup结束=True。

启动 step18-b1-R1-C2-p2，unit=step27-step18-b1-R1-C2-p2，pairs=2；命令已保存。

结束 step18-b1-R1-C2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=389120，PID/cgroup结束=True。

启动 step18-b1-R1-C2-p3，unit=step27-step18-b1-R1-C2-p3，pairs=2；命令已保存。

结束 step18-b1-R1-C2-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=410864，PID/cgroup结束=True。

启动 step18-b1-R1-C2-p4，unit=step27-step18-b1-R1-C2-p4，pairs=2；命令已保存。

结束 step18-b1-R1-C2-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=401084，PID/cgroup结束=True。

启动 step18-b1-C1-C2-p0，unit=step27-step18-b1-C1-C2-p0，pairs=2；命令已保存。

结束 step18-b1-C1-C2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=382544，PID/cgroup结束=True。

启动 step18-b1-C1-C2-p1，unit=step27-step18-b1-C1-C2-p1，pairs=2；命令已保存。

结束 step18-b1-C1-C2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=387124，PID/cgroup结束=True。

启动 step18-b1-C1-C2-p2，unit=step27-step18-b1-C1-C2-p2，pairs=2；命令已保存。

结束 step18-b1-C1-C2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=380272，PID/cgroup结束=True。

启动 step18-b1-C1-C2-p3，unit=step27-step18-b1-C1-C2-p3，pairs=2；命令已保存。

结束 step18-b1-C1-C2-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=390320，PID/cgroup结束=True。

启动 step18-b1-C1-C2-p4，unit=step27-step18-b1-C1-C2-p4，pairs=2；命令已保存。

结束 step18-b1-C1-C2-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=378268，PID/cgroup结束=True。

正式批1六个family/edge全部完成，各10对，原日志/receipt/check即时落盘。

启动 step18-b2-C1-C2-p0，unit=step27-step18-b2-C1-C2-p0，pairs=2；命令已保存。

结束 step18-b2-C1-C2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=394912，PID/cgroup结束=True。

启动 step18-b2-C1-C2-p1，unit=step27-step18-b2-C1-C2-p1，pairs=2；命令已保存。

结束 step18-b2-C1-C2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=398900，PID/cgroup结束=True。

启动 step18-b2-C1-C2-p2，unit=step27-step18-b2-C1-C2-p2，pairs=2；命令已保存。

结束 step18-b2-C1-C2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=387708，PID/cgroup结束=True。

启动 step18-b2-C1-C2-p3，unit=step27-step18-b2-C1-C2-p3，pairs=2；命令已保存。

结束 step18-b2-C1-C2-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=392868，PID/cgroup结束=True。

启动 step18-b2-C1-C2-p4，unit=step27-step18-b2-C1-C2-p4，pairs=2；命令已保存。

结束 step18-b2-C1-C2-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=385472，PID/cgroup结束=True。

启动 step18-b2-R1-C2-p0，unit=step27-step18-b2-R1-C2-p0，pairs=2；命令已保存。

结束 step18-b2-R1-C2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=384488，PID/cgroup结束=True。

启动 step18-b2-R1-C2-p1，unit=step27-step18-b2-R1-C2-p1，pairs=2；命令已保存。

结束 step18-b2-R1-C2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=393744，PID/cgroup结束=True。

启动 step18-b2-R1-C2-p2，unit=step27-step18-b2-R1-C2-p2，pairs=2；命令已保存。

结束 step18-b2-R1-C2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=396560，PID/cgroup结束=True。

启动 step18-b2-R1-C2-p3，unit=step27-step18-b2-R1-C2-p3，pairs=2；命令已保存。

结束 step18-b2-R1-C2-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=386980，PID/cgroup结束=True。

启动 step18-b2-R1-C2-p4，unit=step27-step18-b2-R1-C2-p4，pairs=2；命令已保存。

结束 step18-b2-R1-C2-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=406060，PID/cgroup结束=True。

启动 step18-b2-R1-C1-p0，unit=step27-step18-b2-R1-C1-p0，pairs=2；命令已保存。

结束 step18-b2-R1-C1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=373192，PID/cgroup结束=True。

启动 step18-b2-R1-C1-p1，unit=step27-step18-b2-R1-C1-p1，pairs=2；命令已保存。

结束 step18-b2-R1-C1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=389844，PID/cgroup结束=True。

启动 step18-b2-R1-C1-p2，unit=step27-step18-b2-R1-C1-p2，pairs=2；命令已保存。

结束 step18-b2-R1-C1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=395140，PID/cgroup结束=True。

启动 step18-b2-R1-C1-p3，unit=step27-step18-b2-R1-C1-p3，pairs=2；命令已保存。

结束 step18-b2-R1-C1-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=389828，PID/cgroup结束=True。

启动 step18-b2-R1-C1-p4，unit=step27-step18-b2-R1-C1-p4，pairs=2；命令已保存。

结束 step18-b2-R1-C1-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=396404，PID/cgroup结束=True。

启动 original-b2-R1-C1-p0，unit=step27-original-b2-R1-C1-p0，pairs=2；命令已保存。

结束 original-b2-R1-C1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=384768，PID/cgroup结束=True。

启动 original-b2-R1-C1-p1，unit=step27-original-b2-R1-C1-p1，pairs=2；命令已保存。

结束 original-b2-R1-C1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=385800，PID/cgroup结束=True。

启动 original-b2-R1-C1-p2，unit=step27-original-b2-R1-C1-p2，pairs=2；命令已保存。

结束 original-b2-R1-C1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=388100，PID/cgroup结束=True。

启动 original-b2-R1-C1-p3，unit=step27-original-b2-R1-C1-p3，pairs=2；命令已保存。

结束 original-b2-R1-C1-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=387924，PID/cgroup结束=True。

启动 original-b2-R1-C1-p4，unit=step27-original-b2-R1-C1-p4，pairs=2；命令已保存。

结束 original-b2-R1-C1-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=380772，PID/cgroup结束=True。

启动 step18-b2-R0-R1-p0，unit=step27-step18-b2-R0-R1-p0，pairs=2；命令已保存。

结束 step18-b2-R0-R1-p0：passed=True，reason=exited，peak_threads=57，RSS_KiB=306236，PID/cgroup结束=True。

启动 step18-b2-R0-R1-p1，unit=step27-step18-b2-R0-R1-p1，pairs=2；命令已保存。

结束 step18-b2-R0-R1-p1：passed=True，reason=exited，peak_threads=57，RSS_KiB=297400，PID/cgroup结束=True。

启动 step18-b2-R0-R1-p2，unit=step27-step18-b2-R0-R1-p2，pairs=2；命令已保存。

结束 step18-b2-R0-R1-p2：passed=True，reason=exited，peak_threads=57，RSS_KiB=308168，PID/cgroup结束=True。

启动 step18-b2-R0-R1-p3，unit=step27-step18-b2-R0-R1-p3，pairs=2；命令已保存。

结束 step18-b2-R0-R1-p3：passed=True，reason=exited，peak_threads=57，RSS_KiB=286972，PID/cgroup结束=True。

启动 step18-b2-R0-R1-p4，unit=step27-step18-b2-R0-R1-p4，pairs=2；命令已保存。

结束 step18-b2-R0-R1-p4：passed=True，reason=exited，peak_threads=57，RSS_KiB=304032，PID/cgroup结束=True。

启动 original-b2-R0-R1-p0，unit=step27-original-b2-R0-R1-p0，pairs=2；命令已保存。

结束 original-b2-R0-R1-p0：passed=True，reason=exited，peak_threads=57，RSS_KiB=306364，PID/cgroup结束=True。

启动 original-b2-R0-R1-p1，unit=step27-original-b2-R0-R1-p1，pairs=2；命令已保存。

结束 original-b2-R0-R1-p1：passed=True，reason=exited，peak_threads=57，RSS_KiB=300260，PID/cgroup结束=True。

启动 original-b2-R0-R1-p2，unit=step27-original-b2-R0-R1-p2，pairs=2；命令已保存。

结束 original-b2-R0-R1-p2：passed=True，reason=exited，peak_threads=57，RSS_KiB=291024，PID/cgroup结束=True。

启动 original-b2-R0-R1-p3，unit=step27-original-b2-R0-R1-p3，pairs=2；命令已保存。

结束 original-b2-R0-R1-p3：passed=True，reason=exited，peak_threads=57，RSS_KiB=304120，PID/cgroup结束=True。

启动 original-b2-R0-R1-p4，unit=step27-original-b2-R0-R1-p4，pairs=2；命令已保存。

结束 original-b2-R0-R1-p4：passed=True，reason=exited，peak_threads=57，RSS_KiB=295968，PID/cgroup结束=True。

正式批2六个family/edge全部完成，各10对，原日志/receipt/check即时落盘。

启动 original-b3-R0-R1-p0，unit=step27-original-b3-R0-R1-p0，pairs=2；命令已保存。

结束 original-b3-R0-R1-p0：passed=True，reason=exited，peak_threads=58，RSS_KiB=302428，PID/cgroup结束=True。

启动 original-b3-R0-R1-p1，unit=step27-original-b3-R0-R1-p1，pairs=2；命令已保存。

结束 original-b3-R0-R1-p1：passed=True，reason=exited，peak_threads=57，RSS_KiB=302488，PID/cgroup结束=True。

启动 original-b3-R0-R1-p2，unit=step27-original-b3-R0-R1-p2，pairs=2；命令已保存。

结束 original-b3-R0-R1-p2：passed=True，reason=exited，peak_threads=57，RSS_KiB=300420，PID/cgroup结束=True。

启动 original-b3-R0-R1-p3，unit=step27-original-b3-R0-R1-p3，pairs=2；命令已保存。

结束 original-b3-R0-R1-p3：passed=True，reason=exited，peak_threads=57，RSS_KiB=296412，PID/cgroup结束=True。

启动 original-b3-R0-R1-p4，unit=step27-original-b3-R0-R1-p4，pairs=2；命令已保存。

结束 original-b3-R0-R1-p4：passed=True，reason=exited，peak_threads=57，RSS_KiB=298812，PID/cgroup结束=True。

启动 step18-b3-R0-R1-p0，unit=step27-step18-b3-R0-R1-p0，pairs=2；命令已保存。

结束 step18-b3-R0-R1-p0：passed=True，reason=exited，peak_threads=57，RSS_KiB=308768，PID/cgroup结束=True。

启动 step18-b3-R0-R1-p1，unit=step27-step18-b3-R0-R1-p1，pairs=2；命令已保存。

结束 step18-b3-R0-R1-p1：passed=True，reason=exited，peak_threads=57，RSS_KiB=303188，PID/cgroup结束=True。

启动 step18-b3-R0-R1-p2，unit=step27-step18-b3-R0-R1-p2，pairs=2；命令已保存。

结束 step18-b3-R0-R1-p2：passed=True，reason=exited，peak_threads=57，RSS_KiB=302048，PID/cgroup结束=True。

启动 step18-b3-R0-R1-p3，unit=step27-step18-b3-R0-R1-p3，pairs=2；命令已保存。

结束 step18-b3-R0-R1-p3：passed=True，reason=exited，peak_threads=57，RSS_KiB=287988，PID/cgroup结束=True。

启动 step18-b3-R0-R1-p4，unit=step27-step18-b3-R0-R1-p4，pairs=2；命令已保存。

结束 step18-b3-R0-R1-p4：passed=True，reason=exited，peak_threads=57，RSS_KiB=304968，PID/cgroup结束=True。

启动 original-b3-R1-C1-p0，unit=step27-original-b3-R1-C1-p0，pairs=2；命令已保存。

结束 original-b3-R1-C1-p0：passed=True，reason=exited，peak_threads=109，RSS_KiB=398040，PID/cgroup结束=True。

启动 original-b3-R1-C1-p1，unit=step27-original-b3-R1-C1-p1，pairs=2；命令已保存。

结束 original-b3-R1-C1-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=384684，PID/cgroup结束=True。

启动 original-b3-R1-C1-p2，unit=step27-original-b3-R1-C1-p2，pairs=2；命令已保存。

结束 original-b3-R1-C1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=389764，PID/cgroup结束=True。

启动 original-b3-R1-C1-p3，unit=step27-original-b3-R1-C1-p3，pairs=2；命令已保存。

结束 original-b3-R1-C1-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=383040，PID/cgroup结束=True。

启动 original-b3-R1-C1-p4，unit=step27-original-b3-R1-C1-p4，pairs=2；命令已保存。

结束 original-b3-R1-C1-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=385540，PID/cgroup结束=True。

启动 step18-b3-R1-C1-p0，unit=step27-step18-b3-R1-C1-p0，pairs=2；命令已保存。

结束 step18-b3-R1-C1-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=392740，PID/cgroup结束=True。

启动 step18-b3-R1-C1-p1，unit=step27-step18-b3-R1-C1-p1，pairs=2；命令已保存。

结束 step18-b3-R1-C1-p1：passed=True，reason=exited，peak_threads=109，RSS_KiB=397256，PID/cgroup结束=True。

启动 step18-b3-R1-C1-p2，unit=step27-step18-b3-R1-C1-p2，pairs=2；命令已保存。

结束 step18-b3-R1-C1-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=390720，PID/cgroup结束=True。

启动 step18-b3-R1-C1-p3，unit=step27-step18-b3-R1-C1-p3，pairs=2；命令已保存。

结束 step18-b3-R1-C1-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=380448，PID/cgroup结束=True。

启动 step18-b3-R1-C1-p4，unit=step27-step18-b3-R1-C1-p4，pairs=2；命令已保存。

结束 step18-b3-R1-C1-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=396708，PID/cgroup结束=True。

启动 step18-b3-R1-C2-p0，unit=step27-step18-b3-R1-C2-p0，pairs=2；命令已保存。

结束 step18-b3-R1-C2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=393752，PID/cgroup结束=True。

启动 step18-b3-R1-C2-p1，unit=step27-step18-b3-R1-C2-p1，pairs=2；命令已保存。

结束 step18-b3-R1-C2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=394152，PID/cgroup结束=True。

启动 step18-b3-R1-C2-p2，unit=step27-step18-b3-R1-C2-p2，pairs=2；命令已保存。

结束 step18-b3-R1-C2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=400388，PID/cgroup结束=True。

启动 step18-b3-R1-C2-p3，unit=step27-step18-b3-R1-C2-p3，pairs=2；命令已保存。

结束 step18-b3-R1-C2-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=393920，PID/cgroup结束=True。

启动 step18-b3-R1-C2-p4，unit=step27-step18-b3-R1-C2-p4，pairs=2；命令已保存。

结束 step18-b3-R1-C2-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=401432，PID/cgroup结束=True。

启动 step18-b3-C1-C2-p0，unit=step27-step18-b3-C1-C2-p0，pairs=2；命令已保存。

结束 step18-b3-C1-C2-p0：passed=True，reason=exited，peak_threads=108，RSS_KiB=387116，PID/cgroup结束=True。

启动 step18-b3-C1-C2-p1，unit=step27-step18-b3-C1-C2-p1，pairs=2；命令已保存。

结束 step18-b3-C1-C2-p1：passed=True，reason=exited，peak_threads=108，RSS_KiB=393136，PID/cgroup结束=True。

启动 step18-b3-C1-C2-p2，unit=step27-step18-b3-C1-C2-p2，pairs=2；命令已保存。

结束 step18-b3-C1-C2-p2：passed=True，reason=exited，peak_threads=108，RSS_KiB=387420，PID/cgroup结束=True。

启动 step18-b3-C1-C2-p3，unit=step27-step18-b3-C1-C2-p3，pairs=2；命令已保存。

结束 step18-b3-C1-C2-p3：passed=True，reason=exited，peak_threads=108，RSS_KiB=384928，PID/cgroup结束=True。

启动 step18-b3-C1-C2-p4，unit=step27-step18-b3-C1-C2-p4，pairs=2；命令已保存。

结束 step18-b3-C1-C2-p4：passed=True，reason=exited，peak_threads=108，RSS_KiB=394472，PID/cgroup结束=True。

正式批3六个family/edge全部完成，各10对，原日志/receipt/check即时落盘。

启动 diag-original-b1-R0-R1，unit=step27-diag-original-b1-R0-R1，pairs=1；命令已保存。

结束 diag-original-b1-R0-R1：passed=True，reason=exited，peak_threads=40，RSS_KiB=305988，PID/cgroup结束=True。

启动 diag-step18-b1-C1-C2，unit=step27-diag-step18-b1-C1-C2，pairs=1；命令已保存。

结束 diag-step18-b1-C1-C2：passed=True，reason=exited，peak_threads=74，RSS_KiB=381032，PID/cgroup结束=True。

启动 diag-original-b2-R0-R1，unit=step27-diag-original-b2-R0-R1，pairs=1；命令已保存。

结束 diag-original-b2-R0-R1：passed=True，reason=exited，peak_threads=40，RSS_KiB=290840，PID/cgroup结束=True。

启动 diag-step18-b2-C1-C2，unit=step27-diag-step18-b2-C1-C2，pairs=1；命令已保存。

结束 diag-step18-b2-C1-C2：passed=True，reason=exited，peak_threads=74，RSS_KiB=376908，PID/cgroup结束=True。

启动 diag-original-b3-R0-R1，unit=step27-diag-original-b3-R0-R1，pairs=1；命令已保存。

结束 diag-original-b3-R0-R1：passed=True，reason=exited，peak_threads=40，RSS_KiB=282224，PID/cgroup结束=True。

启动 diag-step18-b3-C1-C2，unit=step27-diag-step18-b3-C1-C2，pairs=1；命令已保存。

结束 diag-step18-b3-C1-C2：passed=True，reason=exited，peak_threads=74，RSS_KiB=374440，PID/cgroup结束=True。

## 预检与正式实验已完成
build2成功，SHA a036d80886c8017de843d992d5c6a57aeee339fed015d24e5c620b2ea5131cf7。六项2对预检通过：原件R0/R1实际同一Store/Module，R1两次关闭后R0仍执行，native计数guard保持。
suite.py formal已真实执行6个family/edge各3批×5进程×2对=180对/90进程；每批每edge10对。suite.py diagnostic另6独立进程各1对，不并入主性能；原件R0业务预热1次有单列记录。全部102测试过程exit0/owner清零/PID与cgroup退出，无资源保护触发。峰RSS401.23MiB、host heap objects63.56MiB、线程109。
原件：R0−R1 export+1.293ms CI[-0.079,2.405]，Full−3.978ms CI[-4.959,-2.490]；Fresh略快的窗口倾向不等于8ms稳定复现，也不等于Full更快。首笔业务/第二笔分层保留；原件Copy Full+0.405ms CI跨零。Step18 R0/R1 export反向点估计CI也跨零；A+Copy对Fresh Full+3.540ms CI正，但对Copy直接−0.518ms CI跨零。没有合并两家族或旧样本。

## 复算与正确性
198对严格Gas/返回/根RWSet/事件/初始及最终账本均通过。原件Gas100000072，Step18 100000019，分开统计。首次离线分析曾误要求保留的R0 init也具有after-close计数、以及误要求跨家族Gas固定；已修正读数语义，不改任何原始样本/期望业务/Gas代码。原生关闭guard未改。build1unused import/未生成binary的准备失败与所有分析说明保留audit/preparation-issues。
主host GC77周期属于外层窗口，不能当export内或Guest GC。12条测量期diagnostic host GC为0，CPU/wall差仍变方向，机制尚未唯一定位。无Guest GC/栈/物理频率和Windows调度证据，不把猜测写成原因。
代码冻结ebbe636（采样后归档，逐Go文件与build2 manifest验证），每进程额外provenance明确事后添加，不篡改原command。历史600B5、两反序短批与新样本分开；26无新增normal样本。

## 交付/恢复
README、NORMALCAL_ANALYSIS、HISTORICAL_AUDIT、LIFECYCLE_AUDIT、CORRECTNESS、全部原CSV/日志/脚本完成，无PPT。原件C2仍blocked，Step18 C2不同WASM明确记录。关闭与模块准备单列；Table/异常/跨合约/长期回收/原池并发均not_tested。
下一条命令仅为python3 -B scripts/verify.py或analyze.py→report.py（离线），没有未完成的Guest任务。不要重跑已有label，不提高预算，不push。正在保存最终独立分支提交并同步IDE资料。
