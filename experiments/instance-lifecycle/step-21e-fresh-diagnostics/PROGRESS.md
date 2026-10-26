# Step21E 可恢复进度

**当前状态：四项诊断与12个有界独立进程验证已完成；下文保留历史检查点。最终结论见README和四份专项报告，未放行100次/并发。**

2026-10-26 Asia/Shanghai。分支experiment/step21e-fresh-diagnostics，独立worktree /home/frankie/mygitprojects/.worktrees/cvw-step21e，父87eb925（Step21D）；21B 620650d、21C 32d257b仅作为证据，不覆盖原件。

已完成：定位分支、读取21D所有权/性能/后续及进度、21A normal分析、旧Step21 CSV字段。当前尚未构建或执行新的guest测试。

阶段1进行中：先从既有原始数据定位Gas首次差异、normal导出窗口和Module成本。阶段2按串行/固定所有者设计少量补测；禁止新并发Fresh压测、100次、Copy/Arena/PB，不修改生产VM或Gas规则。

已运行命令：git worktree/status/log，创建独立worktree，rg/cat/head读取上述文件。
下一条安全操作：提取历史逐调用数据与21D根/子Gas、审计SDK Gas及序列化/Module源码；保存静态证据后决定补测。
阻塞：so精确构建来源、部分Gas差异归因、guest GC观测与normal重复性、长期资源边界尚未闭合。
恢复规则：先读本文件及raw_logs/outcome、检查unit；不重复已有失败/不完整进程，不更改代理/WSL/VSCode配置，不push。

即将执行 fact-probe-1；unit=step21e-fact-probe-1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 fact-probe-1：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 278684, "peak_sampled_threads": 23, "wall_s": 1.3574388190172613, "test": "Gas", "method": "fact", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 normal-gate；unit=step21e-normal-gate；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 normal-gate：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 431092, "peak_sampled_threads": 40, "wall_s": 1.3487346549809445, "test": "Normal", "method": "normalCal", "policy": "R0", "n": 1}；先分析再决定后续。

即将执行 fact-probe-off；unit=step21e-fact-probe-off；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 fact-probe-off：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 281508, "peak_sampled_threads": 23, "wall_s": 1.2970446329854894, "test": "Gas", "method": "fact", "policy": "R1", "n": 1}；先分析再决定后续。

## 静态证据与安全预检完成
- 旧ERC721冷/热Gas差4379、fact594；21D buyNow前5子调用Gas相同，第6transferFrom及根差4379，已定位首分歧层。
- 固定WASM反汇编提取5个GetGas指针槽（audit/gas-slots.json，逐件hash）；只读内存计数器与原有Getter返回核对。fact-probe-1通过真实init+1业务，Gas1585、回收正常，未改WASM/业务/Gas。
- normal-gate通过：预建两个独立Store、R0预热1次、AB各1次，输出/Gas正确、资源约421MiB/40线程，全部scope关闭。允许进入预登记4个bundle、3对的两个相反顺序短批；仍无并发。
- native实际符号只有module_new/serialize/deserialize，没有module_share/obtain。21D引用threads示例不能等于本库已提供API。已保存固定6.0.1源与库符号；准备一个可信本机序列化微型能力检查，不做优化研究。
- build01通过；追加Module能力入口后构建02。下一步读取probe-off结果核对无Gas/状态扰动，再运行预算内Gas短批和normal顺序对照。

即将执行 module-capability；unit=step21e-module-capability；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 module-capability：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 44120, "peak_sampled_threads": 5, "wall_s": 0.03780730298603885, "test": "Module", "method": "module", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 fact-r0；unit=step21e-fact-r0；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 fact-r0：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 269304, "peak_sampled_threads": 22, "wall_s": 0.701553774997592, "test": "Gas", "method": "fact", "policy": "R0", "n": 3}；先分析再决定后续。

即将执行 fact-r1；unit=step21e-fact-r1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 fact-r1：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 324200, "peak_sampled_threads": 25, "wall_s": 2.567775714007439, "test": "Gas", "method": "fact", "policy": "R1", "n": 3}；先分析再决定后续。

即将执行 erc721-r0；unit=step21e-erc721-r0；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 erc721-r0：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 281620, "peak_sampled_threads": 22, "wall_s": 0.7318670579988975, "test": "Gas", "method": "erc721", "policy": "R0", "n": 3}；先分析再决定后续。

即将执行 erc721-r1；unit=step21e-erc721-r1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 erc721-r1：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 370792, "peak_sampled_threads": 26, "wall_s": 2.750873765995493, "test": "Gas", "method": "erc721", "policy": "R1", "n": 3}；先分析再决定后续。

即将执行 buyNow-r0；unit=step21e-buyNow-r0；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 buyNow-r0：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 669228, "peak_sampled_threads": 56, "wall_s": 1.996932915004436, "test": "Gas", "method": "buyNow", "policy": "R0", "n": 1}；先分析再决定后续。

即将执行 buyNow-r1；unit=step21e-buyNow-r1；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 buyNow-r1：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 588744, "peak_sampled_threads": 47, "wall_s": 6.467480092018377, "test": "Gas", "method": "buyNow", "policy": "R1", "n": 1}；先分析再决定后续。

即将执行 normal-ab；unit=step21e-normal-ab；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 normal-ab：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 754700, "peak_sampled_threads": 74, "wall_s": 2.9557180349947885, "test": "Normal", "method": "normalCal", "policy": "R0", "n": 3}；先分析再决定后续。

即将执行 normal-ba；unit=step21e-normal-ba；binary/命令已落盘。恢复先查unit，不重复启动已有日志。

已结束 normal-ba：{"passed": true, "reason": "exited", "status_before_stop": {"MainPID": "0", "Result": "success", "ExecMainStatus": "0", "ControlGroup": "", "ActiveState": "active", "SubState": "exited"}, "post_stop": "MainPID=0\nActiveState=inactive\n", "peak_sampled_rss_kib": 768872, "peak_sampled_threads": 74, "wall_s": 2.982904009986669, "test": "Normal", "method": "normalCal", "policy": "R0", "n": 3}；先分析再决定后续。

## 阶段2/3完成（2026-10-26 15:38后）
- build02成功；已执行module-capability、fact两模式各3、ERC721两模式各3、真实buyNow两模式各1（每根6真实子调用），normal两种反向顺序各3对。加预检共12独立进程，全部原始退出0、scope登记0、单owner_tid、停止后MainPID0；资源限额未放宽，峰值采样750.85MiB/74线程。
- fact trace on/off的Gas、业务输入、前后状态、RWSet、结果与事件完全相同。fixed-hash只读计数器逐调用与原Getter一致。Gas差异首次边界已经保存audit/first-gas-divergence.json；fact业务入口至首EmitEvent，ERC721最后相同PutState至latestTxInfo日志，buyNow第6callee最后相同DeleteState至相同日志。没有改Gas/业务。
- 等状态fact R0=1585,991,991 / R1=1585x3；ERC R0=15449,11070,11070 / R1=15449x3；buyNow根12761395/12765774。read/write/event/结果等价。下游Gas是累计值，已保存GasIn与local_delta，不能六子Gas直接相加。
- normal AB批export均值R0/R1=77.398/75.912ms；BA批=78.270/75.251ms；原600条重算81.739/73.445ms。新小样本同方向但幅度不同，机制仍未解释；HostGC数据不等于guestGC。
- Module微型能力验证同Module串行2Instance +可信Serialize/独立目标Store Deserialize后实例化，真实结果42；未验证业务WASI反序列化缓存或并发。
- scripts/analyze.py已通过语义与历史600行一致性断言。生成processes/call_records/gas_timeline/normal_samples/normal_summary、verification.json，历史6原log已只读冻结audit/history-source。
下一条安全操作：完成四项报告、源码diff与证据索引；只做静态核对和重新分析，不再增加guest测试。没有允许100次/并行Fresh。
阻塞：native准确构建链；逐函数Gas冷缓存因果；normal guestGC/CPU频率及原负载可重复性；长期WASI资源与安全供给/业务Module缓存契约。

## 阶段4交付检查点：完成
- 已交付README、STORE_OWNERSHIP、GAS_ANALYSIS、NORMALCAL_ANALYSIS、MODULE_ANALYSIS、VALIDATION、NEXT_STEP、SOURCE_INDEX和source.patch；所有关键定量结论回链原日志/receipt/CSV。
- 已重新执行离线scripts/analyze.py，通过12进程/所有者/回收和语义检查，以及旧600行原B5匹配；Python源码静态编译、作者新增文件空白和报告本地链接核对通过；没有新增guest运行。
- git全量diff --check会报告继承源码的CRLF、原始日志和objdump空白；保持原字节避免改写审计证据。已单独检查新增诊断源码/脚本/文档，说明保存在audit/whitespace-review.json及authored-checks.json。
- systemctl --user list-units step21e-*显示0已加载unit。D和C worktree均clean；所有暂存文件限Step21E目录，未包含ELF/native库。
- 下一条安全操作：记录manifest并在独立E分支提交本目录；向主CVW新增同名IDE阅读镜像（仅Git交付文件，既有21B/C/D不覆盖）。无远程push。
- 恢复后没有待执行的动态实验。若要进入Step22，先读NEXT_STEP中的Gas冷态、业务Module绑定/缓存、长期回收/供给门槛，不自动扩大到100次或并行。
