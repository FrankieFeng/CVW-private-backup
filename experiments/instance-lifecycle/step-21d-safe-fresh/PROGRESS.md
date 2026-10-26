# Step21D 可恢复进度

2026-10-26 Asia/Shanghai。分支experiment/step21d-safe-fresh，worktree /home/frankie/mygitprojects/.worktrees/cvw-step21d；基于Step21B 620650d。Step21C 32d257b只读取/选择夹具，不合并全分支。

阶段1完成：读取21B README/所有权/并发约束/守卫与保存失败栈/NextStep/Progress；读取21C README/AUDIT/Progress、fixture、manifest和保护计划。21C历史文案“21B未执行”是其当时范围，当前以用户明确指定620650d结果为准。

尚未构建或执行本轮native场景。原始21B/21C及主工作区生产脏文件未改。

下一条安全操作：设计独立Store/目标Module/host/WASI绑定和显式所有者回收；保存设计后才实现。所有危险场景禁自动重跑；每个进程有独立log/outcome，恢复先查unit及已有outcome。

已执行：git status/worktree list/show；创建并移动Step21D独立worktree；rg/cat/sed只读源码及报告。
阻塞：native精确构建映射、Go Finalizer回收及WASI重复创建线程预算；不把未崩溃当安全证明。

## 阶段2完成
设计保存DESIGN.md。选B串行参考：每Fresh调用独立Store/同Store编译Module/host/WASI，单OS线程owner，全部自动native Finalizer替换为强引用确定清理scope，R0缓存bundle仅参考。不使用原池/后台goroutine，不允许native并发。旧guard变量仍开，但新scope/owner协议另行验证，不靠旧guard漏检。

## 阶段3进行中
实验复制模块位于source/vm，只此目录接管Finalizer及提供dManager/Runtime。复制21C的实际VmManager/内存账本/身份/receipt代码，保留旧Skip入口；新增独立有界入口。Gas maps/config逐字提取，Gas导出调用不改。创建失败回滚scope、关闭跟踪inFlight/created/closed。构建01因替换Finalizer后unused runtime imports失败已保存；修正只在实验复制模块，构建02进行中。
初次shell工作目录错配导致预备写入未生效、go test setup报相对replace缺失；没有guest运行，已将实验go.mod路径指向原缓存依赖。后续构建使用有界systemd并保存命令/退出。
下一条安全操作：读取build02结果；编译成功后静态确认Finalizer无遗漏、Gas配置一致，再运行OwnerFailure预检。

即将执行 owner-check；unit=step21d-owner-check；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 owner-check：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 48012, "peak_sampled_threads": 5, "wall_s": 0.039212641975609586, "test": "OwnerFailure", "method": "bigNumCal", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 big-fresh-1；unit=step21d-big-fresh-1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 big-fresh-1：{"passed": false, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "exit-code", "ExecMainStatus": "2", "ControlGroup": "", "ActiveState": "failed", "SubState": "failed"}, "post_stop": "MainPID=0\nActiveState=failed\n", "peak_sampled_rss_kib": 45180, "peak_sampled_threads": 5, "wall_s": 0.06383889899007045, "test": "Compute", "method": "bigNumCal", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 big-fresh-1-v2；unit=step21d-big-fresh-1-v2；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 big-fresh-1-v2：{"passed": false, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "exit-code", "ExecMainStatus": "1", "ControlGroup": "", "ActiveState": "failed", "SubState": "failed"}, "post_stop": "MainPID=0\nActiveState=failed\n", "peak_sampled_rss_kib": 253868, "peak_sampled_threads": 22, "wall_s": 0.623241405992303, "test": "Compute", "method": "bigNumCal", "policy": "R1", "n": 1}；先分析再决定后续。

## 阶段3完成，阶段4最小验证进行中
build03成功，静态Gas配置一致、自动native Finalizer零剩余。owner-check通过：无效字节码清理登记归零、关闭后拒绝新请求。
big-fresh-1在进入native前因简化Snapshot漏GetSnapshotSize发生Go panic；修复实验夹具后build04。big-fresh-1-v2遇标准Go WASI _start返回ExitCode::0，被新构造严格处理为失败；全部scope清理成功、native线程由22降至7，无业务返回。仅接受该固定ABI精确零退出字符串，其余start错误仍失败；不是禁用安全守卫。准备build05后同一个1次业务门槛，新标签保存旧失败不覆盖。

即将执行 big-fresh-1-v3；unit=step21d-big-fresh-1-v3；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 big-fresh-1-v3：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 241808, "peak_sampled_threads": 22, "wall_s": 0.6179535729752388, "test": "Compute", "method": "bigNumCal", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 normal-fresh-1；unit=step21d-normal-fresh-1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 normal-fresh-1：{"passed": false, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "exit-code", "ExecMainStatus": "1", "ControlGroup": "", "ActiveState": "failed", "SubState": "failed"}, "post_stop": "MainPID=0\nActiveState=failed\n", "peak_sampled_rss_kib": 263552, "peak_sampled_threads": 23, "wall_s": 0.7411191840074025, "test": "Compute", "method": "normalCal", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 normal-fresh-1-v2；unit=step21d-normal-fresh-1-v2；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 normal-fresh-1-v2：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 268868, "peak_sampled_threads": 23, "wall_s": 0.6867371010011993, "test": "Compute", "method": "normalCal", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 owner-errors-v2；unit=step21d-owner-errors-v2；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 owner-errors-v2：{"passed": false, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "exit-code", "ExecMainStatus": "1", "ControlGroup": "", "ActiveState": "failed", "SubState": "failed"}, "post_stop": "MainPID=0\nActiveState=failed\n", "peak_sampled_rss_kib": 46084, "peak_sampled_threads": 5, "wall_s": 0.06810797299840488, "test": "OwnerFailure", "method": "bigNumCal", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 owner-errors-v3；unit=step21d-owner-errors-v3；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 owner-errors-v3：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 57712, "peak_sampled_threads": 7, "wall_s": 0.06166128601762466, "test": "OwnerFailure", "method": "bigNumCal", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 big-fresh-3；unit=step21d-big-fresh-3；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 big-fresh-3：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 313076, "peak_sampled_threads": 25, "wall_s": 1.7179688809846994, "test": "Compute", "method": "bigNumCal", "policy": "R1", "n": 3}；先分析再决定后续。

即将执行 normal-fresh-3；unit=step21d-normal-fresh-3；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 normal-fresh-3：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 302544, "peak_sampled_threads": 25, "wall_s": 1.9925560579868034, "test": "Compute", "method": "normalCal", "policy": "R1", "n": 3}；先分析再决定后续。

即将执行 big-reuse-3；unit=step21d-big-reuse-3；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 big-reuse-3：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 252216, "peak_sampled_threads": 22, "wall_s": 0.6313608289929107, "test": "Compute", "method": "bigNumCal", "policy": "R0", "n": 3}；先分析再决定后续。

即将执行 normal-reuse-3；unit=step21d-normal-reuse-3；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 normal-reuse-3：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 269116, "peak_sampled_threads": 23, "wall_s": 0.892542194982525, "test": "Compute", "method": "normalCal", "policy": "R0", "n": 3}；先分析再决定后续。

## 阶段4 compute门槛通过，exchange运行前检查点
- build08为当前安全实现；build06修正normal返回空格并加入单调时间线；旧失败保留。bigNum/normal各R0/R1连续3次通过（四个独立进程），Gas分别105920/100000072，R1 3次不同bundle，R0同bundle复用，仅参考。
- 每个进程manager_closed created=closed、inFlight0，owner_closed registry0，均exit0。Fresh关闭后WASI线程下降约16，不证明长期RSS收敛；没有提高阈值。
- owner-errors-v3通过：跨OS线程访问在native前拒绝、malformed bytecode创建回滚、缺少deallocate的真实最小WASM关闭报错但全部资源scope继续清理、关闭后拒新请求。
- 回调审计见audit/reentry-decision.md及固定6.0.1源码快照。当前仅允许同一所有者同步GetGas/SetGas的限深重入，其他同Store重入禁止；子业务独立Store。仍禁止并发创建/执行。
- 下一条安全操作：独立进程exchange-fresh-1，真实3次init+最多1个buyNow，六callee不足则失败，不放宽保护。100次未准入。

即将执行 exchange-fresh-1；unit=step21d-exchange-fresh-1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 exchange-fresh-1：{"passed": false, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "exit-code", "ExecMainStatus": "1", "ControlGroup": "", "ActiveState": "failed", "SubState": "failed"}, "post_stop": "MainPID=0\nActiveState=failed\n", "peak_sampled_rss_kib": 273672, "peak_sampled_threads": 22, "wall_s": 0.7229127709870227, "test": "Exchange", "method": "buyNow", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 exchange-fresh-1-v2；unit=step21d-exchange-fresh-1-v2；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 exchange-fresh-1-v2：{"passed": false, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "exit-code", "ExecMainStatus": "1", "ControlGroup": "", "ActiveState": "failed", "SubState": "failed"}, "post_stop": "MainPID=0\nActiveState=failed\n", "peak_sampled_rss_kib": 329436, "peak_sampled_threads": 23, "wall_s": 1.36584198102355, "test": "Exchange", "method": "buyNow", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 exchange-fresh-1-v3；unit=step21d-exchange-fresh-1-v3；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 exchange-fresh-1-v3：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 617204, "peak_sampled_threads": 48, "wall_s": 6.287591943022562, "test": "Exchange", "method": "buyNow", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 exchange-reuse-1；unit=step21d-exchange-reuse-1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 exchange-reuse-1：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 675416, "peak_sampled_threads": 57, "wall_s": 1.9436810440092813, "test": "Exchange", "method": "buyNow", "policy": "R0", "n": 1}；先分析再决定后续。

## exchange真实Fresh验证通过
exchange-fresh-1-v3通过：3次真实init+1个buyNow（六个真实callee、depth1、全部code0），白名单/owner/授权/事件断言通过，创建=关闭10、inFlight0、registry0；rootGas12765774。原前两次失败是21C夹具配置：Block1不支持CHAINMAKER，ZXL改变SDK senderPk为PEM；最终选ETHEREUM保留UID模式，见audit/address-decision.md。
当前R0 exchange参考正在独立进程执行；无并发。

## 阶段5运行前登记
此前compute n3在每次调用后强制GC用于生命周期验证，不能当无间隔原池性能。最终统一版本仅可选D_FORCE_GC=1才逐调用强制GC，性能诊断默认不强制，结束后仍强制GC。对最终ETHEREUM上下文重新做bigNum/normal×R0/R1各3次（同binary）；原数据全保留不混合。每笔receipt保存有额外I/O，当前没有后台供给所以绝不称原Step21连续负载同机制。
100次禁止：Fresh每次含约0.55s编译，100次约55s量级，已超过45s Go timeout预算；exchange每根约4.4s更不满足。尚未验证长期RSS收敛，不能放宽原保护换取100次。

## 最终生命周期收尾补强
exchange-reuse-1也通过真实六callee和状态断言，rootGas12761395，与R1的12765774不相同，R0仅参考，不认证Gas等价。
最终复核发现ImportObject在Instance构造失败前没有独立清理登记；实验绑定增加scope登记/幂等nil关闭，并把WASI named extern vector的删除设为defer覆盖错误分支。构建12；这是错误路径修复，不修改业务Gas。build11仅将逐调用强制GC改为可选，结束强制GC保留。
下一步对最终binary12运行owner-errors及compute四个3次小批、exchange两模式各1根，确认清理新路径。原所有日志保留，主对比只用final-*标签，之前样本归为预检/开发验证，不混合版本。

即将执行 final-owner；unit=step21d-final-owner；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 final-owner：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 39964, "peak_sampled_threads": 5, "wall_s": 0.035982408007839695, "test": "OwnerFailure", "method": "bigNumCal", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 final-big-r0；unit=step21d-final-big-r0；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 final-big-r0：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 251580, "peak_sampled_threads": 22, "wall_s": 0.6719294250069652, "test": "Compute", "method": "bigNumCal", "policy": "R0", "n": 3}；先分析再决定后续。

即将执行 final-big-r1；unit=step21d-final-big-r1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 final-big-r1：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 298144, "peak_sampled_threads": 24, "wall_s": 1.773615542013431, "test": "Compute", "method": "bigNumCal", "policy": "R1", "n": 3}；先分析再决定后续。

即将执行 final-normal-r1；unit=step21d-final-normal-r1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 final-normal-r1：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 300228, "peak_sampled_threads": 25, "wall_s": 2.0262126779998653, "test": "Compute", "method": "normalCal", "policy": "R1", "n": 3}；先分析再决定后续。

即将执行 final-normal-r0；unit=step21d-final-normal-r0；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 final-normal-r0：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 271676, "peak_sampled_threads": 23, "wall_s": 0.8892940169898793, "test": "Compute", "method": "normalCal", "policy": "R0", "n": 3}；先分析再决定后续。

即将执行 final-exchange-r1；unit=step21d-final-exchange-r1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 final-exchange-r1：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 595076, "peak_sampled_threads": 48, "wall_s": 6.5008248160011135, "test": "Exchange", "method": "buyNow", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 final-exchange-r0；unit=step21d-final-exchange-r0；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 final-exchange-r0：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 679728, "peak_sampled_threads": 56, "wall_s": 1.971674450993305, "test": "Exchange", "method": "buyNow", "policy": "R0", "n": 1}；先分析再决定后续。

## 阶段4与阶段5完成
最终build12的7个进程全部通过：final-owner + compute 2方法×R0/R1各3次 + exchange两模式各1根。14个目标根调用、含init/callee共32个真实VM Invoke。全部创建/关闭相等、inFlight0、registry0，所有进程已停止。
主样本同一binary，默认不逐调用强制GC，结束后强制GC。分析已输出summary/samples/correctness/lifecycle_events/all_processes和verification；23个开发/最终测试进程全留档，17通过6失败。早期逐调用GC、旧夹具和不同binary不混入主表。
真实buyNow每模式6callee成功、状态/事件通过；R0/R1根Gas12761395/12765774，差异保留，未声称等价。最终资源峰值事件+采样约681.24MiB/57线程，无保护越限。没有运行100次或应用层C API并发。
已写README、DESIGN、OWNERSHIP、VALIDATION、PERFORMANCE、NEXT_STEP、REPRODUCE、SOURCE_INDEX及完整source.patch/fixture-adaptation.patch。
下一条安全操作：仅链接/hash/进程状态/源码差异检查和独立分支归档，不再执行native。
仍阻塞：精确native构建映射、长期资源收敛、45秒预算下100次、可控compiled-module跨Store绑定与并行所有者、exchange Gas差异。小样本功能边界已恢复，不等于原池/生产或Step22性能准入。

## 最终检查完成，等待归档
source hash一致、文档链接无缺失、Gas配置与原源码一致、最终所有CallMethod错误/关闭错误均nil、每进程单owner线程、所有receipt成功。实际查询23个unit全部MainPID0，状态保存audit/final-unit-states.json。
source.patch、fixture-adaptation.patch、关键依赖源码/Imports/继承报告与失败栈已保存。原生产VM工作树diff为空。
下一条安全操作：只在experiment/step21d-safe-fresh提交本新目录；如主目录需要可读镜像，仅复制本目录，不覆盖任何旧实验。不再运行测试，不push。

归档使用仅本次命令的Git作者标识Codex，不修改全局/仓库Git配置。native库和测试binary保持Git忽略；本目录源码和结果归档到独立分支，最终提交以git log为准。原B/C和主工作区脏文件保留。

## 独立分支归档完成
本目录已在experiment/step21d-safe-fresh归档（最终提交以git log为准），未推送。已排除测试binary、native库及不使用的packaged工具ELF，仅保存源码/报告/日志/输入元数据。独立worktree生产路径未改，旧B/C原件未改。
最后操作只做结果镜像和hash核对；下一次恢复只读本文件/README/NEXT_STEP，不重复已有测试。当前无待执行进程或压测任务。
